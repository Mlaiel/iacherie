"""Alert Management System

Système de gestion avancée des alertes et notifications critiques.
Gestion des escalades, seuils, règles métier et notifications multi-canaux.

Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead AI Developer, Backend Senior, ML Engineer, Security Expert
Copyright © 2025 Fahed Mlaiel. Tous droits réservés.

AVERTISSEMENT LÉGAL:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée
est strictement interdite et constitue une violation des droits d'auteur.
Les contrevenants s'exposent à des poursuites judiciaires.
"""from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import json
import uuid
from abc import ABC, abstractmethod
import aioredis
import asyncpg
from croniter import croniter

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Niveaux de sévérité des alertes"""    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertStatus(Enum):
    """Statuts des alertes"""    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    EXPIRED = "expired"


class AlertType(Enum):
    """Types d'alertes"""    SYSTEM_ERROR = "system_error"
    SECURITY_BREACH = "security_breach"
    CONTENT_VIOLATION = "content_violation"
    PAYMENT_FAILURE = "payment_failure"
    API_RATE_LIMIT = "api_rate_limit"
    STORAGE_FULL = "storage_full"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    USER_SUSPICIOUS_ACTIVITY = "user_suspicious_activity"
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    REVENUE_ANOMALY = "revenue_anomaly"
    COLLABORATION_ISSUE = "collaboration_issue"
    PLATFORM_INTEGRATION_ERROR = "platform_integration_error"


class EscalationAction(Enum):
    """Actions d'escalade"""    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    SLACK = "slack"
    TEAMS = "teams"
    PHONE_CALL = "phone_call"
    TICKET_CREATION = "ticket_creation"


@dataclass
class AlertRule:
    """Règle d'alerte"""    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    alert_type: AlertType = AlertType.SYSTEM_ERROR
    severity: AlertSeverity = AlertSeverity.MEDIUM
    conditions: Dict[str, Any] = field(default_factory=dict)
    threshold_value: Optional[float] = None
    threshold_operator: str = ">"  # >, <, >=, <=, ==, !=
    time_window: int = 300  # 5 minutes
    occurrence_count: int = 1
    suppression_time: int = 3600  # 1 heure
    auto_resolve_time: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """Alerte système"""    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str = ""
    alert_type: AlertType = AlertType.SYSTEM_ERROR
    severity: AlertSeverity = AlertSeverity.MEDIUM
    status: AlertStatus = AlertStatus.ACTIVE
    title: str = ""
    description: str = ""
    source: str = ""
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    current_value: Optional[float] = None
    threshold_value: Optional[float] = None
    occurrence_count: int = 1
    first_occurrence: datetime = field(default_factory=datetime.utcnow)
    last_occurrence: datetime = field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    suppressed_until: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    escalation_level: int = 0
    next_escalation_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EscalationPolicy:
    """Politique d'escalade"""    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    alert_types: List[AlertType] = field(default_factory=list)
    severity_levels: List[AlertSeverity] = field(default_factory=list)
    steps: List[Dict[str, Any]] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AlertNotification:
    """Notification d'alerte"""    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alert_id: str = ""
    escalation_step: int = 0
    action: EscalationAction = EscalationAction.EMAIL
    recipient: str = ""
    recipient_type: str = "user"  # user, group, external
    message: str = ""
    status: str = "pending"  # pending, sent, failed, delivered
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    next_retry_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class AlertConditionEvaluator(ABC):
    """Évaluateur de conditions d'alerte abstrait"""    
    @abstractmethod
    async def evaluate(self, rule: AlertRule, context: Dict[str, Any]) -> bool:
        """Évaluer une condition"""        pass


class ThresholdConditionEvaluator(AlertConditionEvaluator):
    """Évaluateur de conditions de seuil"""    
    async def evaluate(self, rule: AlertRule, context: Dict[str, Any]) -> bool:
        """Évaluer une condition de seuil"""        try:
            current_value = context.get("value")
            threshold_value = rule.threshold_value
            operator = rule.threshold_operator
            
            if current_value is None or threshold_value is None:
                return False
            
            if operator == ">":
                return current_value > threshold_value
            elif operator == "<":
                return current_value < threshold_value
            elif operator == ">=":
                return current_value >= threshold_value
            elif operator == "<=":
                return current_value <= threshold_value
            elif operator == "==":
                return current_value == threshold_value
            elif operator == "!=":
                return current_value != threshold_value
            else:
                logger.warning(f"Opérateur inconnu: {operator}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur évaluation condition seuil: {e}")
            return False


class PatternConditionEvaluator(AlertConditionEvaluator):
    """Évaluateur de conditions de motif"""    
    async def evaluate(self, rule: AlertRule, context: Dict[str, Any]) -> bool:
        """Évaluer une condition de motif"""        try:
            conditions = rule.conditions
            pattern_type = conditions.get("pattern_type")
            
            if pattern_type == "frequency":
                return await self._evaluate_frequency_pattern(conditions, context)
            elif pattern_type == "trend":
                return await self._evaluate_trend_pattern(conditions, context)
            elif pattern_type == "anomaly":
                return await self._evaluate_anomaly_pattern(conditions, context)
            else:
                return False
                
        except Exception as e:
            logger.error(f"Erreur évaluation condition motif: {e}")
            return False
    
    async def _evaluate_frequency_pattern(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Évaluer un motif de fréquence"""        expected_count = conditions.get("expected_count", 0)
        time_window = conditions.get("time_window", 300)
        actual_count = context.get("event_count", 0)
        
        return actual_count >= expected_count
    
    async def _evaluate_trend_pattern(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Évaluer un motif de tendance"""        trend_type = conditions.get("trend_type", "increasing")
        trend_threshold = conditions.get("trend_threshold", 0.1)
        values = context.get("values", [])
        
        if len(values) < 2:
            return False
        
        # Calculer la tendance
        first_value = values[0]
        last_value = values[-1]
        change_rate = (last_value - first_value) / first_value if first_value != 0 else 0
        
        if trend_type == "increasing":
            return change_rate > trend_threshold
        elif trend_type == "decreasing":
            return change_rate < -trend_threshold
        else:
            return False
    
    async def _evaluate_anomaly_pattern(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Évaluer un motif d'anomalie"""        anomaly_score = context.get("anomaly_score", 0)
        threshold = conditions.get("anomaly_threshold", 0.8)
        
        return anomaly_score > threshold


class AlertEngine:
    """Moteur de gestion des alertes"""    
    def __init__(self, db_pool: asyncpg.Pool, redis_client: aioredis.Redis):
        self.db_pool = db_pool
        self.redis = redis_client
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.escalation_policies: Dict[str, EscalationPolicy] = {}
        self.condition_evaluators = {
            "threshold": ThresholdConditionEvaluator(),
            "pattern": PatternConditionEvaluator()
        }
        
    async def initialize(self):
        """Initialiser le moteur d'alertes"""        try:
            await self._load_rules()
            await self._load_escalation_policies()
            await self._load_active_alerts()
            
            # Démarrer les tâches de fond
            asyncio.create_task(self._escalation_processor())
            asyncio.create_task(self._auto_resolver())
            asyncio.create_task(self._suppression_cleaner())
            
            logger.info("Moteur d'alertes initialisé")
            
        except Exception as e:
            logger.error(f"Erreur initialisation moteur d'alertes: {e}")
            raise
    
    async def create_rule(self, rule: AlertRule) -> str:
        """Créer une règle d'alerte"""        try:
            # Sauvegarder en base
            rule_id = await self._save_rule(rule)
            
            # Ajouter au cache
            self.rules[rule_id] = rule
            
            logger.info(f"Règle d'alerte créée: {rule_id}")
            return rule_id
            
        except Exception as e:
            logger.error(f"Erreur création règle d'alerte: {e}")
            raise
    
    async def evaluate_conditions(self, rule_id: str, context: Dict[str, Any]) -> Optional[Alert]:
        """Évaluer les conditions d'une règle"""        try:
            rule = self.rules.get(rule_id)
            if not rule or not rule.is_active:
                return None
            
            # Déterminer le type d'évaluateur
            evaluator_type = rule.conditions.get("type", "threshold")
            evaluator = self.condition_evaluators.get(evaluator_type)
            
            if not evaluator:
                logger.warning(f"Évaluateur non trouvé: {evaluator_type}")
                return None
            
            # Évaluer les conditions
            condition_met = await evaluator.evaluate(rule, context)
            
            if not condition_met:
                return None
            
            # Vérifier la suppression
            if await self._is_suppressed(rule_id):
                logger.debug(f"Règle {rule_id} supprimée")
                return None
            
            # Créer ou mettre à jour l'alerte
            alert = await self._create_or_update_alert(rule, context)
            
            return alert
            
        except Exception as e:
            logger.error(f"Erreur évaluation conditions {rule_id}: {e}")
            return None
    
    async def acknowledge_alert(self, alert_id: str, user_id: str, notes: Optional[str] = None) -> bool:
        """Acquitter une alerte"""        try:
            alert = self.active_alerts.get(alert_id)
            if not alert or alert.status != AlertStatus.ACTIVE:
                return False
            
            # Mettre à jour l'alerte
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.utcnow()
            alert.acknowledged_by = user_id
            alert.updated_at = datetime.utcnow()
            
            if notes:
                alert.context["acknowledgment_notes"] = notes
            
            # Sauvegarder
            await self._update_alert(alert)
            
            # Arrêter l'escalade
            alert.next_escalation_at = None
            
            logger.info(f"Alerte acquittée: {alert_id} par {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur acquittement alerte {alert_id}: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str, user_id: str, notes: Optional[str] = None) -> bool:
        """Résoudre une alerte"""        try:
            alert = self.active_alerts.get(alert_id)
            if not alert:
                return False
            
            # Mettre à jour l'alerte
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.utcnow()
            alert.resolved_by = user_id
            alert.resolution_notes = notes
            alert.updated_at = datetime.utcnow()
            
            # Sauvegarder
            await self._update_alert(alert)
            
            # Supprimer du cache des alertes actives
            del self.active_alerts[alert_id]
            
            logger.info(f"Alerte résolue: {alert_id} par {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur résolution alerte {alert_id}: {e}")
            return False
    
    async def suppress_alert(self, alert_id: str, duration: int, user_id: str) -> bool:
        """Supprimer temporairement une alerte"""        try:
            alert = self.active_alerts.get(alert_id)
            if not alert:
                return False
            
            # Mettre à jour l'alerte
            alert.status = AlertStatus.SUPPRESSED
            alert.suppressed_until = datetime.utcnow() + timedelta(seconds=duration)
            alert.updated_at = datetime.utcnow()
            alert.context["suppressed_by"] = user_id
            
            # Sauvegarder
            await self._update_alert(alert)
            
            # Ajouter à la liste de suppression Redis
            await self.redis.setex(
                f"alert:suppressed:{alert_id}",
                duration,
                json.dumps({"user_id": user_id, "until": alert.suppressed_until.isoformat()})
            )
            
            logger.info(f"Alerte supprimée: {alert_id} pour {duration}s par {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur suppression alerte {alert_id}: {e}")
            return False
    
    async def _create_or_update_alert(self, rule: AlertRule, context: Dict[str, Any]) -> Alert:
        """Créer ou mettre à jour une alerte"""        try:
            # Chercher une alerte existante pour cette règle
            existing_alert = None
            for alert in self.active_alerts.values():
                if (alert.rule_id == rule.id and 
                    alert.status == AlertStatus.ACTIVE and
                    alert.entity_id == context.get("entity_id")):
                    existing_alert = alert
                    break
            
            if existing_alert:
                # Mettre à jour l'alerte existante
                existing_alert.occurrence_count += 1
                existing_alert.last_occurrence = datetime.utcnow()
                existing_alert.current_value = context.get("value")
                existing_alert.context.update(context)
                existing_alert.updated_at = datetime.utcnow()
                
                await self._update_alert(existing_alert)
                return existing_alert
            else:
                # Créer une nouvelle alerte
                alert = Alert(
                    rule_id=rule.id,
                    alert_type=rule.alert_type,
                    severity=rule.severity,
                    title=context.get("title", f"Alert for rule {rule.name}"),
                    description=context.get("description", rule.description),
                    source=context.get("source", "system"),
                    entity_id=context.get("entity_id"),
                    entity_type=context.get("entity_type"),
                    current_value=context.get("value"),
                    threshold_value=rule.threshold_value,
                    tags=rule.tags.copy(),
                    context=context.copy()
                )
                
                # Définir l'expiration automatique
                if rule.auto_resolve_time:
                    alert.expires_at = datetime.utcnow() + timedelta(seconds=rule.auto_resolve_time)
                
                # Programmer la première escalade
                await self._schedule_escalation(alert)
                
                # Sauvegarder
                await self._save_alert(alert)
                
                # Ajouter au cache
                self.active_alerts[alert.id] = alert
                
                logger.info(f"Nouvelle alerte créée: {alert.id}")
                return alert
                
        except Exception as e:
            logger.error(f"Erreur création/mise à jour alerte: {e}")
            raise
    
    async def _schedule_escalation(self, alert: Alert):
        """Programmer l'escalade d'une alerte"""        try:
            # Trouver la politique d'escalade appropriée
            policy = await self._find_escalation_policy(alert)
            if not policy or not policy.steps:
                return
            
            # Programmer la première escalade
            first_step = policy.steps[0]
            delay = first_step.get("delay", 300)  # 5 minutes par défaut
            
            alert.next_escalation_at = datetime.utcnow() + timedelta(seconds=delay)
            
        except Exception as e:
            logger.error(f"Erreur programmation escalade: {e}")
    
    async def _find_escalation_policy(self, alert: Alert) -> Optional[EscalationPolicy]:
        """Trouver la politique d'escalade pour une alerte"""        for policy in self.escalation_policies.values():
            if not policy.is_active:
                continue
            
            # Vérifier les types d'alerte
            if policy.alert_types and alert.alert_type not in policy.alert_types:
                continue
            
            # Vérifier les niveaux de sévérité
            if policy.severity_levels and alert.severity not in policy.severity_levels:
                continue
            
            return policy
        
        return None
    
    async def _escalation_processor(self):
        """Processeur d'escalades"""        while True:
            try:
                now = datetime.utcnow()
                
                for alert in list(self.active_alerts.values()):
                    if (alert.next_escalation_at and 
                        alert.next_escalation_at <= now and
                        alert.status == AlertStatus.ACTIVE):
                        
                        await self._process_escalation(alert)
                
                # Attendre 30 secondes avant la prochaine vérification
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Erreur processeur escalades: {e}")
                await asyncio.sleep(60)
    
    async def _process_escalation(self, alert: Alert):
        """Traiter l'escalade d'une alerte"""        try:
            policy = await self._find_escalation_policy(alert)
            if not policy:
                return
            
            # Vérifier s'il y a encore des étapes d'escalade
            if alert.escalation_level >= len(policy.steps):
                logger.warning(f"Aucune étape d'escalade restante pour {alert.id}")
                return
            
            step = policy.steps[alert.escalation_level]
            
            # Exécuter les actions de l'étape
            for action_config in step.get("actions", []):
                await self._execute_escalation_action(alert, action_config, alert.escalation_level)
            
            # Programmer la prochaine escalade
            alert.escalation_level += 1
            if alert.escalation_level < len(policy.steps):
                next_step = policy.steps[alert.escalation_level]
                delay = next_step.get("delay", 300)
                alert.next_escalation_at = datetime.utcnow() + timedelta(seconds=delay)
            else:
                alert.next_escalation_at = None
            
            # Sauvegarder
            await self._update_alert(alert)
            
        except Exception as e:
            logger.error(f"Erreur traitement escalade {alert.id}: {e}")
    
    async def _execute_escalation_action(self, alert: Alert, action_config: Dict[str, Any], escalation_step: int):
        """Exécuter une action d'escalade"""        try:
            action_type = EscalationAction(action_config["type"])
            recipients = action_config.get("recipients", [])
            
            for recipient in recipients:
                notification = AlertNotification(
                    alert_id=alert.id,
                    escalation_step=escalation_step,
                    action=action_type,
                    recipient=recipient,
                    message=self._build_alert_message(alert, action_config)
                )
                
                await self._send_alert_notification(notification)
                
        except Exception as e:
            logger.error(f"Erreur exécution action escalade: {e}")
    
    def _build_alert_message(self, alert: Alert, action_config: Dict[str, Any]) -> str:
        """Construire le message d'alerte"""        template = action_config.get("message_template", 
                                   "Alert: {title}\nSeverity: {severity}\nDescription: {description}")
        
        return template.format(
            title=alert.title,
            severity=alert.severity.value,
            description=alert.description,
            current_value=alert.current_value,
            threshold_value=alert.threshold_value,
            occurrence_count=alert.occurrence_count,
            first_occurrence=alert.first_occurrence.isoformat(),
            last_occurrence=alert.last_occurrence.isoformat()
        )
    
    async def _send_alert_notification(self, notification: AlertNotification):
        """Envoyer une notification d'alerte"""        try:
            # Sauvegarder la notification
            await self._save_notification(notification)
            
            # Ajouter à la queue de traitement
            await self.redis.lpush(
                "alert:notifications:queue",
                json.dumps({
                    "id": notification.id,
                    "action": notification.action.value,
                    "recipient": notification.recipient,
                    "message": notification.message
                })
            )
            
        except Exception as e:
            logger.error(f"Erreur envoi notification alerte: {e}")
    
    async def _auto_resolver(self):
        """Résolveur automatique d'alertes"""        while True:
            try:
                now = datetime.utcnow()
                
                for alert in list(self.active_alerts.values()):
                    if alert.expires_at and alert.expires_at <= now:
                        alert.status = AlertStatus.RESOLVED
                        alert.resolved_at = now
                        alert.resolved_by = "system"
                        alert.resolution_notes = "Auto-resolved by expiration"
                        
                        await self._update_alert(alert)
                        del self.active_alerts[alert.id]
                        
                        logger.info(f"Alerte auto-résolue: {alert.id}")
                
                # Attendre 1 minute
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Erreur résolveur automatique: {e}")
                await asyncio.sleep(300)
    
    async def _suppression_cleaner(self):
        """Nettoyeur de suppressions expirées"""        while True:
            try:
                now = datetime.utcnow()
                
                for alert in list(self.active_alerts.values()):
                    if (alert.status == AlertStatus.SUPPRESSED and
                        alert.suppressed_until and
                        alert.suppressed_until <= now):
                        
                        alert.status = AlertStatus.ACTIVE
                        alert.suppressed_until = None
                        
                        await self._update_alert(alert)
                        
                        # Reprendre l'escalade
                        await self._schedule_escalation(alert)
                        
                        logger.info(f"Suppression expirée pour alerte: {alert.id}")
                
                # Attendre 1 minute
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Erreur nettoyeur suppressions: {e}")
                await asyncio.sleep(300)
    
    async def _is_suppressed(self, rule_id: str) -> bool:
        """Vérifier si une règle est supprimée"""        try:
            key = f"alert:suppressed:rule:{rule_id}"
            return await self.redis.exists(key)
        except Exception as e:
            logger.error(f"Erreur vérification suppression: {e}")
            return False
    
    async def _load_rules(self):
        """Charger les règles d'alerte"""        async with self.db_pool.acquire() as conn:
            query = "SELECT * FROM alert_rules WHERE is_active = true"
            rows = await conn.fetch(query)
            
            for row in rows:
                rule = AlertRule(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"],
                    alert_type=AlertType(row["alert_type"]),
                    severity=AlertSeverity(row["severity"]),
                    conditions=json.loads(row["conditions"]),
                    threshold_value=row["threshold_value"],
                    threshold_operator=row["threshold_operator"],
                    time_window=row["time_window"],
                    occurrence_count=row["occurrence_count"],
                    suppression_time=row["suppression_time"],
                    auto_resolve_time=row["auto_resolve_time"],
                    tags=json.loads(row["tags"] or "[]"),
                    is_active=row["is_active"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    metadata=json.loads(row["metadata"] or "{}")
                )
                
                self.rules[rule.id] = rule
    
    async def _load_escalation_policies(self):
        """Charger les politiques d'escalade"""        async with self.db_pool.acquire() as conn:
            query = "SELECT * FROM escalation_policies WHERE is_active = true"
            rows = await conn.fetch(query)
            
            for row in rows:
                policy = EscalationPolicy(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"],
                    alert_types=[AlertType(t) for t in json.loads(row["alert_types"] or "[]")],
                    severity_levels=[AlertSeverity(s) for s in json.loads(row["severity_levels"] or "[]")],
                    steps=json.loads(row["steps"] or "[]"),
                    is_active=row["is_active"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
                
                self.escalation_policies[policy.id] = policy
    
    async def _load_active_alerts(self):
        """Charger les alertes actives"""        async with self.db_pool.acquire() as conn:
            query = """                SELECT * FROM alerts 
                WHERE status IN ('active', 'acknowledged', 'suppressed')
                AND (expires_at IS NULL OR expires_at > $1)
            """            rows = await conn.fetch(query, datetime.utcnow())
            
            for row in rows:
                alert = Alert(
                    id=row["id"],
                    rule_id=row["rule_id"],
                    alert_type=AlertType(row["alert_type"]),
                    severity=AlertSeverity(row["severity"]),
                    status=AlertStatus(row["status"]),
                    title=row["title"],
                    description=row["description"],
                    source=row["source"],
                    entity_id=row["entity_id"],
                    entity_type=row["entity_type"],
                    current_value=row["current_value"],
                    threshold_value=row["threshold_value"],
                    occurrence_count=row["occurrence_count"],
                    first_occurrence=row["first_occurrence"],
                    last_occurrence=row["last_occurrence"],
                    acknowledged_at=row["acknowledged_at"],
                    acknowledged_by=row["acknowledged_by"],
                    resolved_at=row["resolved_at"],
                    resolved_by=row["resolved_by"],
                    resolution_notes=row["resolution_notes"],
                    suppressed_until=row["suppressed_until"],
                    expires_at=row["expires_at"],
                    tags=json.loads(row["tags"] or "[]"),
                    context=json.loads(row["context"] or "{}"),
                    escalation_level=row["escalation_level"],
                    next_escalation_at=row["next_escalation_at"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
                
                self.active_alerts[alert.id] = alert
    
    async def _save_rule(self, rule: AlertRule) -> str:
        """Sauvegarder une règle"""        async with self.db_pool.acquire() as conn:
            query = """                INSERT INTO alert_rules (
                    id, name, description, alert_type, severity, conditions,
                    threshold_value, threshold_operator, time_window,
                    occurrence_count, suppression_time, auto_resolve_time,
                    tags, is_active, created_at, updated_at, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
                RETURNING id
            """            
            result = await conn.fetchval(
                query,
                rule.id, rule.name, rule.description, rule.alert_type.value,
                rule.severity.value, json.dumps(rule.conditions), rule.threshold_value,
                rule.threshold_operator, rule.time_window, rule.occurrence_count,
                rule.suppression_time, rule.auto_resolve_time, json.dumps(rule.tags),
                rule.is_active, rule.created_at, rule.updated_at, json.dumps(rule.metadata)
            )
            
            return result
    
    async def _save_alert(self, alert: Alert):
        """Sauvegarder une alerte"""        async with self.db_pool.acquire() as conn:
            query = """                INSERT INTO alerts (
                    id, rule_id, alert_type, severity, status, title, description,
                    source, entity_id, entity_type, current_value, threshold_value,
                    occurrence_count, first_occurrence, last_occurrence,
                    acknowledged_at, acknowledged_by, resolved_at, resolved_by,
                    resolution_notes, suppressed_until, expires_at, tags, context,
                    escalation_level, next_escalation_at, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24, $25, $26, $27, $28)
            """            
            await conn.execute(
                query,
                alert.id, alert.rule_id, alert.alert_type.value, alert.severity.value,
                alert.status.value, alert.title, alert.description, alert.source,
                alert.entity_id, alert.entity_type, alert.current_value, alert.threshold_value,
                alert.occurrence_count, alert.first_occurrence, alert.last_occurrence,
                alert.acknowledged_at, alert.acknowledged_by, alert.resolved_at,
                alert.resolved_by, alert.resolution_notes, alert.suppressed_until,
                alert.expires_at, json.dumps(alert.tags), json.dumps(alert.context),
                alert.escalation_level, alert.next_escalation_at, alert.created_at, alert.updated_at
            )
    
    async def _update_alert(self, alert: Alert):
        """Mettre à jour une alerte"""        async with self.db_pool.acquire() as conn:
            query = """                UPDATE alerts SET
                    status = $2, current_value = $3, occurrence_count = $4,
                    last_occurrence = $5, acknowledged_at = $6, acknowledged_by = $7,
                    resolved_at = $8, resolved_by = $9, resolution_notes = $10,
                    suppressed_until = $11, context = $12, escalation_level = $13,
                    next_escalation_at = $14, updated_at = $15
                WHERE id = $1
            """            
            await conn.execute(
                query,
                alert.id, alert.status.value, alert.current_value, alert.occurrence_count,
                alert.last_occurrence, alert.acknowledged_at, alert.acknowledged_by,
                alert.resolved_at, alert.resolved_by, alert.resolution_notes,
                alert.suppressed_until, json.dumps(alert.context), alert.escalation_level,
                alert.next_escalation_at, alert.updated_at
            )
    
    async def _save_notification(self, notification: AlertNotification):
        """Sauvegarder une notification"""        async with self.db_pool.acquire() as conn:
            query = """                INSERT INTO alert_notifications (
                    id, alert_id, escalation_step, action, recipient,
                    recipient_type, message, status, sent_at, delivered_at,
                    failed_at, failure_reason, retry_count, max_retries,
                    next_retry_at, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
            """            
            await conn.execute(
                query,
                notification.id, notification.alert_id, notification.escalation_step,
                notification.action.value, notification.recipient, notification.recipient_type,
                notification.message, notification.status, notification.sent_at,
                notification.delivered_at, notification.failed_at, notification.failure_reason,
                notification.retry_count, notification.max_retries, notification.next_retry_at,
                notification.created_at
            )
    
    async def get_active_alerts(self, filters: Optional[Dict[str, Any]] = None) -> List[Alert]:
        """Récupérer les alertes actives avec filtres"""        alerts = list(self.active_alerts.values())
        
        if not filters:
            return alerts
        
        filtered_alerts = []
        for alert in alerts:
            if self._match_alert_filters(alert, filters):
                filtered_alerts.append(alert)
        
        return filtered_alerts
    
    def _match_alert_filters(self, alert: Alert, filters: Dict[str, Any]) -> bool:
        """Vérifier si une alerte correspond aux filtres"""        if "severity" in filters and alert.severity not in filters["severity"]:
            return False
        
        if "status" in filters and alert.status not in filters["status"]:
            return False
        
        if "alert_type" in filters and alert.alert_type not in filters["alert_type"]:
            return False
        
        if "tags" in filters:
            required_tags = set(filters["tags"])
            alert_tags = set(alert.tags)
            if not required_tags.issubset(alert_tags):
                return False
        
        return True
    
    async def get_alert_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Récupérer les statistiques d'alertes"""        async with self.db_pool.acquire() as conn:
            # Statistiques générales
            stats_query = """                SELECT 
                    COUNT(*) as total_alerts,
                    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_alerts,
                    COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_alerts,
                    COUNT(CASE WHEN acknowledged_at IS NOT NULL THEN 1 END) as acknowledged_alerts,
                    AVG(EXTRACT(EPOCH FROM (COALESCE(resolved_at, NOW()) - first_occurrence))) as avg_resolution_time
                FROM alerts
                WHERE created_at BETWEEN $1 AND $2
            """            
            stats = await conn.fetchrow(stats_query, start_date, end_date)
            
            # Statistiques par sévérité
            severity_query = """                SELECT severity, COUNT(*) as count
                FROM alerts
                WHERE created_at BETWEEN $1 AND $2
                GROUP BY severity
            """            
            severity_stats = await conn.fetch(severity_query, start_date, end_date)
            
            # Statistiques par type
            type_query = """                SELECT alert_type, COUNT(*) as count
                FROM alerts
                WHERE created_at BETWEEN $1 AND $2
                GROUP BY alert_type
            """            
            type_stats = await conn.fetch(type_query, start_date, end_date)
            
            return {
                "period": {"start": start_date, "end": end_date},
                "totals": dict(stats),
                "by_severity": [dict(row) for row in severity_stats],
                "by_type": [dict(row) for row in type_stats]
            }
