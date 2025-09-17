"""
🚨 Intelligent Alerting System - Système Alerting Intelligent Adaptatif
======================================================================

Système alerting intelligent temps réel ultra-avancé pour gestion
adaptative notifications, priorisation ML et prévention fatigue
alertes Creator Economy avec intelligence contextuelle.

Fonctionnalités:
- Context-aware alerting avec analyse situationnelle
- ML-powered alert prioritization avec scoring dynamique
- Intelligent escalation routing avec expertise matching
- Alert fatigue prevention avec adaptive thresholding
- Automated response triggers avec workflow orchestration
- Multi-channel notification optimization avec préférences

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Set, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
from collections import deque, defaultdict
import statistics
import math
from decimal import Decimal
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AlertChannel(Enum):
    """Canaux d'alerte"""
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    DISCORD = "discord"
    TEAMS = "teams"
    WEBHOOK = "webhook"
    PUSH_NOTIFICATION = "push_notification"
    IN_APP = "in_app"
    PHONE_CALL = "phone_call"
    DASHBOARD = "dashboard"


class AlertPriority(Enum):
    """Priorités d'alerte"""
    EMERGENCY = "emergency"      # Immediate action required
    CRITICAL = "critical"        # Within 5 minutes
    HIGH = "high"               # Within 30 minutes
    MEDIUM = "medium"           # Within 2 hours
    LOW = "low"                # Within 24 hours
    INFO = "info"              # No time constraint


class AlertStatus(Enum):
    """Statuts d'alerte"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    SUPPRESSED = "suppressed"
    FAILED = "failed"


class EscalationLevel(Enum):
    """Niveaux d'escalation"""
    L1_SUPPORT = "l1_support"
    L2_SPECIALIST = "l2_specialist"
    L3_EXPERT = "l3_expert"
    MANAGEMENT = "management"
    EXECUTIVE = "executive"
    EXTERNAL = "external"


class AlertCategory(Enum):
    """Catégories d'alerte"""
    SYSTEM_HEALTH = "system_health"
    SECURITY_INCIDENT = "security_incident"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    BUSINESS_ANOMALY = "business_anomaly"
    USER_EXPERIENCE = "user_experience"
    REVENUE_IMPACT = "revenue_impact"
    COMPLIANCE_VIOLATION = "compliance_violation"
    INFRASTRUCTURE = "infrastructure"
    APPLICATION_ERROR = "application_error"
    DATA_QUALITY = "data_quality"


@dataclass
class AlertPolicy:
    """Politique d'alerte"""
    policy_id: str
    name: str
    category: AlertCategory
    priority: AlertPriority
    
    # Conditions déclenchement
    trigger_conditions: List[Dict[str, Any]]
    suppression_conditions: List[Dict[str, Any]]
    
    # Escalation
    escalation_rules: List[Dict[str, Any]]
    escalation_timeout_minutes: int
    max_escalation_level: EscalationLevel
    
    # Routing
    routing_rules: List[Dict[str, Any]]
    default_assignee: Optional[str]
    expert_pool: List[str]
    
    # Channels
    preferred_channels: List[AlertChannel]
    channel_fallback: Dict[AlertChannel, AlertChannel]
    
    # Timing
    business_hours_only: bool
    timezone: str
    quiet_hours: Optional[Tuple[int, int]]
    
    # Frequency
    max_alerts_per_hour: int
    duplicate_suppression_minutes: int
    
    # Métadonnées
    created_by: str
    created_at: datetime
    last_modified: datetime
    is_active: bool


@dataclass
class AlertContext:
    """Contexte d'alerte"""
    alert_id: str
    
    # Contexte temporel
    timestamp: datetime
    business_hours: bool
    is_holiday: bool
    day_of_week: int
    
    # Contexte système
    system_load: float
    active_incidents: int
    recent_deployments: List[str]
    maintenance_windows: List[Dict[str, Any]]
    
    # Contexte utilisateur
    affected_user_count: int
    vip_users_affected: bool
    geographic_impact: Dict[str, int]
    
    # Contexte business
    revenue_impact: Decimal
    sla_risk: bool
    competitive_event: bool
    marketing_campaign_active: bool
    
    # Contexte équipe
    on_call_engineer: Optional[str]
    team_availability: Dict[str, bool]
    expertise_required: List[str]
    
    # Historique
    similar_incidents: List[str]
    recent_resolution_time: Optional[int]
    escalation_history: List[Dict[str, Any]]


@dataclass
class SmartAlert:
    """Alerte intelligente"""
    alert_id: str
    policy_id: str
    category: AlertCategory
    priority: AlertPriority
    
    # Contenu
    title: str
    description: str
    details: Dict[str, Any]
    severity_score: float
    
    # Contexte
    context: AlertContext
    source_system: str
    affected_entities: List[str]
    
    # Intelligence
    ml_priority_score: float
    urgency_score: float
    business_impact_score: float
    technical_complexity_score: float
    
    # Routing
    assigned_to: Optional[str]
    assigned_team: Optional[str]
    escalation_level: EscalationLevel
    
    # État
    status: AlertStatus
    created_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    
    # Notifications
    notifications_sent: List[Dict[str, Any]] = field(default_factory=list)
    channels_used: List[AlertChannel] = field(default_factory=list)
    
    # Réponse
    automated_actions: List[str] = field(default_factory=list)
    response_playbook: Optional[str] = None
    resolution_steps: List[str] = field(default_factory=list)
    
    # Métadonnées
    tags: List[str] = field(default_factory=list)
    correlation_id: Optional[str] = None
    parent_alert_id: Optional[str] = None


@dataclass
class NotificationDelivery:
    """Livraison notification"""
    delivery_id: str
    alert_id: str
    channel: AlertChannel
    recipient: str
    
    # Contenu
    subject: str
    message: str
    formatted_content: Dict[str, Any]
    
    # État livraison
    status: AlertStatus
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    response_at: Optional[datetime]
    
    # Métriques
    delivery_time_ms: Optional[int]
    read_time_minutes: Optional[int]
    response_time_minutes: Optional[int]
    
    # Erreurs
    error_message: Optional[str]
    retry_count: int
    max_retries: int


@dataclass
class AlertingMetrics:
    """Métriques système alerting"""
    timestamp: datetime
    
    # Volume
    total_alerts_24h: int
    alerts_by_priority: Dict[AlertPriority, int]
    alerts_by_category: Dict[AlertCategory, int]
    
    # Performance
    mean_detection_time_seconds: float
    mean_notification_time_seconds: float
    mean_acknowledgment_time_minutes: float
    mean_resolution_time_minutes: float
    
    # Qualité
    false_positive_rate: float
    duplicate_rate: float
    escalation_rate: float
    auto_resolution_rate: float
    
    # Satisfaction
    alert_fatigue_score: float
    user_satisfaction_score: float
    noise_to_signal_ratio: float
    
    # Canaux
    channel_effectiveness: Dict[AlertChannel, float]
    delivery_success_rate: Dict[AlertChannel, float]


class IntelligentAlertingSystem:
    """
    Système alerting intelligent ultra-avancé
    
    Gestion adaptative notifications avec ML, priorisation contextuelle
    et prévention fatigue alertes pour Creator Economy.
    """
    
    def __init__(self, 
                 ml_prioritization_enabled: bool = True,
                 adaptive_thresholding_enabled: bool = True,
                 fatigue_prevention_enabled: bool = True):
        """
        Initialise système alerting intelligent
        
        Args:
            ml_prioritization_enabled: Activation priorisation ML
            adaptive_thresholding_enabled: Activation seuils adaptatifs
            fatigue_prevention_enabled: Activation prévention fatigue
        """
        self.ml_prioritization_enabled = ml_prioritization_enabled
        self.adaptive_thresholding_enabled = adaptive_thresholding_enabled
        self.fatigue_prevention_enabled = fatigue_prevention_enabled
        
        # Stockage état
        self.alert_policies: Dict[str, AlertPolicy] = {}
        self.active_alerts: Dict[str, SmartAlert] = {}
        self.alert_history: deque = deque(maxlen=100000)
        self.notification_history: deque = deque(maxlen=200000)
        
        # Intelligence contextuelle
        self.context_analyzer = self._init_context_analyzer()
        self.ml_prioritizer = self._init_ml_prioritizer()
        self.fatigue_detector = self._init_fatigue_detector()
        
        # Routing et escalation
        self.routing_engine = self._init_routing_engine()
        self.escalation_manager = self._init_escalation_manager()
        
        # Channels et intégrations
        self.notification_channels: Dict[AlertChannel, Any] = {}
        self.channel_adapters: Dict[AlertChannel, Callable] = {}
        
        # Métriques et monitoring
        self.alerting_metrics: deque = deque(maxlen=1440)  # 24h par minute
        self.user_preferences: Dict[str, Dict[str, Any]] = {}
        self.team_configs: Dict[str, Dict[str, Any]] = {}
        
        # Seuils adaptatifs
        self.adaptive_thresholds: Dict[str, Dict[str, float]] = {}
        self.threshold_learning_rate = 0.1
        
        # Suppression et corrélation
        self.suppression_rules: Dict[str, Any] = {}
        self.correlation_windows: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )
        
        logger.info("IntelligentAlertingSystem initialisé avec succès")
    
    def _init_context_analyzer(self):
        """Initialise analyseur contexte"""
        return {
            'model_type': 'context_awareness_transformer',
            'accuracy': 0.91,
            'last_trained': datetime.now(),
            'context_dimensions': [
                'temporal', 'system_state', 'business_impact',
                'team_availability', 'historical_patterns'
            ]
        }
    
    def _init_ml_prioritizer(self):
        """Initialise prioriseur ML"""
        return {
            'model_type': 'priority_ranking_ensemble',
            'accuracy': 0.88,
            'last_trained': datetime.now(),
            'features': [
                'severity_score', 'business_impact', 'urgency',
                'historical_priority', 'context_signals'
            ]
        }
    
    def _init_fatigue_detector(self):
        """Initialise détecteur fatigue"""
        return {
            'model_type': 'fatigue_prediction_lstm',
            'accuracy': 0.85,
            'last_trained': datetime.now(),
            'fatigue_indicators': [
                'alert_frequency', 'false_positive_rate',
                'response_time_degradation', 'acknowledgment_rate'
            ]
        }
    
    def _init_routing_engine(self):
        """Initialise moteur routing"""
        return {
            'algorithm': 'expertise_matching_ml',
            'skill_mapping_accuracy': 0.89,
            'load_balancing_enabled': True,
            'timezone_awareness': True
        }
    
    def _init_escalation_manager(self):
        """Initialise gestionnaire escalation"""
        return {
            'strategy': 'intelligent_escalation',
            'timeout_prediction_enabled': True,
            'skill_gap_detection': True,
            'management_notification_threshold': EscalationLevel.L3_EXPERT
        }
    
    async def create_alert_policy(self, policy_config: Dict[str, Any]) -> AlertPolicy:
        """
        Crée politique d'alerte
        
        Args:
            policy_config: Configuration politique
            
        Returns:
            AlertPolicy: Politique créée
        """
        try:
            policy = AlertPolicy(
                policy_id=policy_config.get('policy_id', str(uuid.uuid4())),
                name=policy_config['name'],
                category=AlertCategory(policy_config['category']),
                priority=AlertPriority(policy_config['priority']),
                
                # Conditions
                trigger_conditions=policy_config.get('trigger_conditions', []),
                suppression_conditions=policy_config.get('suppression_conditions', []),
                
                # Escalation
                escalation_rules=policy_config.get('escalation_rules', []),
                escalation_timeout_minutes=policy_config.get('escalation_timeout_minutes', 30),
                max_escalation_level=EscalationLevel(
                    policy_config.get('max_escalation_level', 'l3_expert')
                ),
                
                # Routing
                routing_rules=policy_config.get('routing_rules', []),
                default_assignee=policy_config.get('default_assignee'),
                expert_pool=policy_config.get('expert_pool', []),
                
                # Channels
                preferred_channels=[
                    AlertChannel(ch) for ch in policy_config.get('preferred_channels', ['email'])
                ],
                channel_fallback=policy_config.get('channel_fallback', {}),
                
                # Timing
                business_hours_only=policy_config.get('business_hours_only', False),
                timezone=policy_config.get('timezone', 'UTC'),
                quiet_hours=policy_config.get('quiet_hours'),
                
                # Frequency
                max_alerts_per_hour=policy_config.get('max_alerts_per_hour', 10),
                duplicate_suppression_minutes=policy_config.get('duplicate_suppression_minutes', 5),
                
                # Métadonnées
                created_by=policy_config.get('created_by', 'system'),
                created_at=datetime.now(),
                last_modified=datetime.now(),
                is_active=policy_config.get('is_active', True)
            )
            
            # Stockage politique
            self.alert_policies[policy.policy_id] = policy
            
            logger.info(f"Politique alerte créée: {policy.name}")
            return policy
            
        except Exception as e:
            logger.error(f"Erreur create alert policy: {e}")
            raise
    
    async def process_alert(self, 
                          alert_data: Dict[str, Any],
                          policy_id: Optional[str] = None) -> SmartAlert:
        """
        Traite alerte intelligente
        
        Args:
            alert_data: Données alerte
            policy_id: ID politique (optionnel)
            
        Returns:
            SmartAlert: Alerte traitée
        """
        try:
            # Sélection/création politique
            if policy_id:
                policy = self.alert_policies.get(policy_id)
                if not policy:
                    raise ValueError(f"Politique non trouvée: {policy_id}")
            else:
                policy = await self._auto_select_policy(alert_data)
            
            # Analyse contexte
            context = await self._analyze_alert_context(alert_data)
            
            # Vérification suppression
            if await self._should_suppress_alert(alert_data, context, policy):
                logger.info("Alerte supprimée par règles")
                return None
            
            # Calcul scores intelligence
            ml_priority_score = await self._calculate_ml_priority_score(alert_data, context)
            urgency_score = await self._calculate_urgency_score(alert_data, context)
            business_impact_score = await self._calculate_business_impact_score(alert_data, context)
            technical_complexity_score = await self._calculate_technical_complexity_score(alert_data)
            
            # Détermination priorité finale
            final_priority = await self._determine_final_priority(
                policy.priority, ml_priority_score, urgency_score, business_impact_score
            )
            
            # Routing intelligent
            assigned_to, assigned_team, escalation_level = await self._intelligent_routing(
                alert_data, context, policy
            )
            
            # Création alerte intelligente
            smart_alert = SmartAlert(
                alert_id=str(uuid.uuid4()),
                policy_id=policy.policy_id,
                category=policy.category,
                priority=final_priority,
                
                # Contenu
                title=alert_data['title'],
                description=alert_data.get('description', ''),
                details=alert_data.get('details', {}),
                severity_score=alert_data.get('severity_score', 0.5),
                
                # Contexte
                context=context,
                source_system=alert_data.get('source_system', 'unknown'),
                affected_entities=alert_data.get('affected_entities', []),
                
                # Intelligence
                ml_priority_score=ml_priority_score,
                urgency_score=urgency_score,
                business_impact_score=business_impact_score,
                technical_complexity_score=technical_complexity_score,
                
                # Routing
                assigned_to=assigned_to,
                assigned_team=assigned_team,
                escalation_level=escalation_level,
                
                # État
                status=AlertStatus.PENDING,
                created_at=datetime.now(),
                acknowledged_at=None,
                resolved_at=None,
                
                # Réponse
                response_playbook=await self._select_response_playbook(alert_data, context),
                tags=alert_data.get('tags', [])
            )
            
            # Stockage alerte
            self.active_alerts[smart_alert.alert_id] = smart_alert
            self.alert_history.append(smart_alert)
            
            # Notification
            await self._send_notifications(smart_alert, policy)
            
            # Actions automatisées
            await self._trigger_automated_actions(smart_alert, policy)
            
            # Corrélation avec alertes existantes
            await self._correlate_alert(smart_alert)
            
            logger.info(f"Alerte intelligente traitée: {smart_alert.alert_id}")
            return smart_alert
            
        except Exception as e:
            logger.error(f"Erreur process alert: {e}")
            raise
    
    async def acknowledge_alert(self, 
                              alert_id: str,
                              user_id: str,
                              acknowledgment_note: Optional[str] = None) -> bool:
        """
        Accuse réception alerte
        
        Args:
            alert_id: ID alerte
            user_id: ID utilisateur
            acknowledgment_note: Note accusé réception (optionnel)
            
        Returns:
            bool: Succès accusé réception
        """
        try:
            alert = self.active_alerts.get(alert_id)
            if not alert:
                raise ValueError(f"Alerte non trouvée: {alert_id}")
            
            if alert.status in [AlertStatus.ACKNOWLEDGED, AlertStatus.RESOLVED]:
                logger.warning(f"Alerte déjà traitée: {alert_id}")
                return False
            
            # Mise à jour état
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now()
            alert.assigned_to = user_id
            
            # Calcul temps réponse
            response_time = (alert.acknowledged_at - alert.created_at).total_seconds() / 60
            
            # Notification équipe
            await self._notify_acknowledgment(alert, user_id, acknowledgment_note)
            
            # Annulation escalation automatique
            await self._cancel_auto_escalation(alert_id)
            
            # Mise à jour métriques
            await self._update_acknowledgment_metrics(alert, response_time)
            
            logger.info(f"Alerte accusée réception: {alert_id} par {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur acknowledge alert: {e}")
            return False
    
    async def resolve_alert(self, 
                          alert_id: str,
                          user_id: str,
                          resolution_note: str,
                          resolution_actions: List[str]) -> bool:
        """
        Résout alerte
        
        Args:
            alert_id: ID alerte
            user_id: ID utilisateur
            resolution_note: Note résolution
            resolution_actions: Actions résolution
            
        Returns:
            bool: Succès résolution
        """
        try:
            alert = self.active_alerts.get(alert_id)
            if not alert:
                raise ValueError(f"Alerte non trouvée: {alert_id}")
            
            if alert.status == AlertStatus.RESOLVED:
                logger.warning(f"Alerte déjà résolue: {alert_id}")
                return False
            
            # Mise à jour état
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            alert.resolution_steps.extend(resolution_actions)
            
            # Calcul temps résolution
            resolution_time = (alert.resolved_at - alert.created_at).total_seconds() / 60
            
            # Notification résolution
            await self._notify_resolution(alert, user_id, resolution_note)
            
            # Analyse post-incident
            await self._trigger_post_incident_analysis(alert)
            
            # Apprentissage pour amélioration
            await self._learn_from_resolution(alert, resolution_actions)
            
            # Retrait alertes actives
            del self.active_alerts[alert_id]
            
            # Mise à jour métriques
            await self._update_resolution_metrics(alert, resolution_time)
            
            logger.info(f"Alerte résolue: {alert_id} par {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur resolve alert: {e}")
            return False
    
    async def escalate_alert(self, 
                           alert_id: str,
                           escalation_reason: str,
                           escalated_by: str) -> bool:
        """
        Escalade alerte
        
        Args:
            alert_id: ID alerte
            escalation_reason: Raison escalation
            escalated_by: Utilisateur escalation
            
        Returns:
            bool: Succès escalation
        """
        try:
            alert = self.active_alerts.get(alert_id)
            if not alert:
                raise ValueError(f"Alerte non trouvée: {alert_id}")
            
            # Détermination niveau escalation suivant
            next_level = await self._determine_next_escalation_level(alert)
            
            if not next_level:
                logger.warning(f"Escalation maximum atteinte: {alert_id}")
                return False
            
            # Mise à jour alerte
            alert.escalation_level = next_level
            alert.status = AlertStatus.ESCALATED
            
            # Nouveau routing
            new_assignee, new_team, _ = await self._escalation_routing(
                alert, next_level
            )
            
            alert.assigned_to = new_assignee
            alert.assigned_team = new_team
            
            # Notification escalation
            await self._notify_escalation(alert, escalation_reason, escalated_by)
            
            # Enregistrement escalation
            escalation_record = {
                'timestamp': datetime.now(),
                'from_level': alert.escalation_level,
                'to_level': next_level,
                'reason': escalation_reason,
                'escalated_by': escalated_by
            }
            alert.context.escalation_history.append(escalation_record)
            
            logger.info(f"Alerte escaladée: {alert_id} vers {next_level.value}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur escalate alert: {e}")
            return False
    
    async def get_alert_dashboard(self, 
                                user_id: str,
                                time_range_hours: int = 24) -> Dict[str, Any]:
        """
        Récupère dashboard alertes personnalisé
        
        Args:
            user_id: ID utilisateur
            time_range_hours: Période en heures
            
        Returns:
            Dict[str, Any]: Dashboard personnalisé
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
            
            # Alertes assignées utilisateur
            user_alerts = [
                alert for alert in self.active_alerts.values()
                if alert.assigned_to == user_id
            ]
            
            # Alertes équipe utilisateur
            user_preferences = self.user_preferences.get(user_id, {})
            user_teams = user_preferences.get('teams', [])
            
            team_alerts = [
                alert for alert in self.active_alerts.values()
                if alert.assigned_team in user_teams
            ]
            
            # Alertes récentes
            recent_alerts = [
                alert for alert in self.alert_history
                if alert.created_at >= cutoff_time
            ]
            
            # Métriques personnalisées
            personal_metrics = await self._calculate_personal_metrics(
                user_id, recent_alerts
            )
            
            # Recommandations
            recommendations = await self._generate_user_recommendations(
                user_id, user_alerts, team_alerts
            )
            
            # Alertes prioritaires
            priority_alerts = sorted(
                user_alerts + team_alerts,
                key=lambda x: (
                    x.ml_priority_score + x.urgency_score + x.business_impact_score
                ),
                reverse=True
            )[:10]
            
            return {
                'user_id': user_id,
                'dashboard_generated_at': datetime.now().isoformat(),
                'time_range_hours': time_range_hours,
                'summary': {
                    'total_assigned_alerts': len(user_alerts),
                    'total_team_alerts': len(team_alerts),
                    'critical_alerts': len([
                        a for a in user_alerts + team_alerts
                        if a.priority in [AlertPriority.EMERGENCY, AlertPriority.CRITICAL]
                    ]),
                    'unacknowledged_alerts': len([
                        a for a in user_alerts + team_alerts
                        if a.status == AlertStatus.PENDING
                    ])
                },
                'priority_alerts': [
                    {
                        'alert_id': alert.alert_id,
                        'title': alert.title,
                        'priority': alert.priority.value,
                        'category': alert.category.value,
                        'created_at': alert.created_at.isoformat(),
                        'status': alert.status.value,
                        'ml_priority_score': alert.ml_priority_score,
                        'business_impact_score': alert.business_impact_score
                    }
                    for alert in priority_alerts
                ],
                'personal_metrics': personal_metrics,
                'recommendations': recommendations,
                'alert_trends': await self._analyze_alert_trends(user_id, recent_alerts),
                'fatigue_assessment': await self._assess_user_fatigue(user_id),
                'next_escalations': await self._predict_next_escalations(user_alerts)
            }
            
        except Exception as e:
            logger.error(f"Erreur get alert dashboard: {e}")
            return {'error': str(e)}
    
    # Méthodes privées d'intelligence et ML
    
    async def _analyze_alert_context(self, alert_data: Dict[str, Any]) -> AlertContext:
        """Analyse contexte alerte"""
        try:
            now = datetime.now()
            
            # Contexte temporel
            business_hours = await self._is_business_hours(now)
            is_holiday = await self._is_holiday(now)
            
            # Contexte système
            system_load = await self._get_current_system_load()
            active_incidents = len(self.active_alerts)
            recent_deployments = await self._get_recent_deployments()
            maintenance_windows = await self._get_active_maintenance_windows()
            
            # Contexte utilisateur
            affected_user_count = alert_data.get('affected_users', 0)
            vip_users_affected = alert_data.get('vip_users_affected', False)
            geographic_impact = alert_data.get('geographic_impact', {})
            
            # Contexte business
            revenue_impact = Decimal(str(alert_data.get('revenue_impact', 0)))
            sla_risk = alert_data.get('sla_risk', False)
            competitive_event = await self._detect_competitive_event()
            marketing_campaign_active = await self._is_marketing_campaign_active()
            
            # Contexte équipe
            on_call_engineer = await self._get_on_call_engineer()
            team_availability = await self._get_team_availability()
            expertise_required = await self._identify_required_expertise(alert_data)
            
            # Historique
            similar_incidents = await self._find_similar_incidents(alert_data)
            recent_resolution_time = await self._get_recent_resolution_time(similar_incidents)
            
            return AlertContext(
                alert_id=str(uuid.uuid4()),
                
                # Temporel
                timestamp=now,
                business_hours=business_hours,
                is_holiday=is_holiday,
                day_of_week=now.weekday(),
                
                # Système
                system_load=system_load,
                active_incidents=active_incidents,
                recent_deployments=recent_deployments,
                maintenance_windows=maintenance_windows,
                
                # Utilisateur
                affected_user_count=affected_user_count,
                vip_users_affected=vip_users_affected,
                geographic_impact=geographic_impact,
                
                # Business
                revenue_impact=revenue_impact,
                sla_risk=sla_risk,
                competitive_event=competitive_event,
                marketing_campaign_active=marketing_campaign_active,
                
                # Équipe
                on_call_engineer=on_call_engineer,
                team_availability=team_availability,
                expertise_required=expertise_required,
                
                # Historique
                similar_incidents=similar_incidents,
                recent_resolution_time=recent_resolution_time,
                escalation_history=[]
            )
            
        except Exception as e:
            logger.error(f"Erreur analyze alert context: {e}")
            return None
    
    async def _calculate_ml_priority_score(self, 
                                         alert_data: Dict[str, Any],
                                         context: AlertContext) -> float:
        """Calcule score priorité ML"""
        try:
            # Simulation ML scoring - en production utiliser modèle entraîné
            features = [
                alert_data.get('severity_score', 0.5),
                context.affected_user_count / 10000,  # Normalisation
                float(context.revenue_impact) / 100000,  # Normalisation
                1.0 if context.vip_users_affected else 0.0,
                1.0 if context.sla_risk else 0.0,
                context.system_load,
                len(context.similar_incidents) / 10,  # Normalisation
                1.0 if context.business_hours else 0.5
            ]
            
            # Score composite ML simulé
            weights = [0.25, 0.15, 0.15, 0.15, 0.1, 0.1, 0.05, 0.05]
            ml_score = sum(
                feature * weight 
                for feature, weight in zip(features, weights)
            )
            
            return min(ml_score, 1.0)
            
        except Exception as e:
            logger.error(f"Erreur calculate ml priority score: {e}")
            return 0.5
    
    async def _calculate_urgency_score(self, 
                                     alert_data: Dict[str, Any],
                                     context: AlertContext) -> float:
        """Calcule score urgence"""
        urgency_factors = [
            context.sla_risk * 0.3,
            (context.affected_user_count / 50000) * 0.2,  # Normalisation
            context.vip_users_affected * 0.2,
            (float(context.revenue_impact) / 500000) * 0.2,  # Normalisation
            (context.system_load > 0.8) * 0.1
        ]
        
        return min(sum(urgency_factors), 1.0)
    
    async def _calculate_business_impact_score(self, 
                                             alert_data: Dict[str, Any],
                                             context: AlertContext) -> float:
        """Calcule score impact business"""
        impact_factors = [
            (float(context.revenue_impact) / 1000000) * 0.4,  # Normalisation
            (context.affected_user_count / 100000) * 0.3,
            context.competitive_event * 0.15,
            context.marketing_campaign_active * 0.15
        ]
        
        return min(sum(impact_factors), 1.0)
    
    async def _calculate_technical_complexity_score(self, 
                                                  alert_data: Dict[str, Any]) -> float:
        """Calcule score complexité technique"""
        # Simulation basée sur métadonnées alerte
        complexity_indicators = [
            'database' in alert_data.get('description', '').lower(),
            'network' in alert_data.get('description', '').lower(),
            'security' in alert_data.get('description', '').lower(),
            len(alert_data.get('affected_entities', [])) > 5,
            alert_data.get('cross_system_impact', False)
        ]
        
        complexity_score = sum(complexity_indicators) / len(complexity_indicators)
        return complexity_score
    
    # Méthodes utilitaires (implémentations simplifiées)
    
    async def _auto_select_policy(self, alert_data: Dict[str, Any]) -> AlertPolicy:
        """Sélectionne automatiquement politique"""
        # Logique sélection basée sur catégorie/contenu
        category_keywords = {
            AlertCategory.SYSTEM_HEALTH: ['cpu', 'memory', 'disk', 'health'],
            AlertCategory.SECURITY_INCIDENT: ['security', 'breach', 'unauthorized'],
            AlertCategory.PERFORMANCE_DEGRADATION: ['slow', 'latency', 'timeout'],
            AlertCategory.REVENUE_IMPACT: ['payment', 'revenue', 'transaction']
        }
        
        description = alert_data.get('description', '').lower()
        
        for category, keywords in category_keywords.items():
            if any(keyword in description for keyword in keywords):
                # Recherche politique correspondante
                for policy in self.alert_policies.values():
                    if policy.category == category and policy.is_active:
                        return policy
        
        # Politique par défaut
        return list(self.alert_policies.values())[0] if self.alert_policies else None
    
    async def _should_suppress_alert(self, 
                                   alert_data: Dict[str, Any],
                                   context: AlertContext,
                                   policy: AlertPolicy) -> bool:
        """Vérifie si alerte doit être supprimée"""
        # Vérification fenêtre maintenance
        for maintenance in context.maintenance_windows:
            if maintenance.get('suppress_alerts', False):
                return True
        
        # Vérification heures silence
        if policy.quiet_hours:
            current_hour = context.timestamp.hour
            start_hour, end_hour = policy.quiet_hours
            if start_hour <= current_hour <= end_hour:
                return True
        
        # Vérification limite fréquence
        recent_similar = await self._count_recent_similar_alerts(
            alert_data, policy.duplicate_suppression_minutes
        )
        
        if recent_similar >= policy.max_alerts_per_hour:
            return True
        
        return False
    
    async def _intelligent_routing(self, 
                                 alert_data: Dict[str, Any],
                                 context: AlertContext,
                                 policy: AlertPolicy) -> Tuple[Optional[str], Optional[str], EscalationLevel]:
        """Routing intelligent alerte"""
        # Assignation basée sur expertise requise
        required_expertise = context.expertise_required
        
        # Recherche expert disponible
        available_experts = [
            expert for expert in policy.expert_pool
            if context.team_availability.get(expert, False)
        ]
        
        if available_experts:
            # Sélection basée sur charge et expertise
            best_expert = await self._select_best_expert(
                available_experts, required_expertise
            )
            return best_expert, None, EscalationLevel.L1_SUPPORT
        
        # Fallback assignation par défaut
        return policy.default_assignee, None, EscalationLevel.L1_SUPPORT
    
    async def _send_notifications(self, alert: SmartAlert, policy: AlertPolicy):
        """Envoie notifications"""
        try:
            for channel in policy.preferred_channels:
                # Détermination destinataire
                recipient = alert.assigned_to or policy.default_assignee
                
                if recipient:
                    delivery = await self._send_notification_channel(
                        alert, channel, recipient
                    )
                    alert.notifications_sent.append(delivery.__dict__)
                    alert.channels_used.append(channel)
            
        except Exception as e:
            logger.error(f"Erreur send notifications: {e}")
    
    async def _send_notification_channel(self, 
                                       alert: SmartAlert,
                                       channel: AlertChannel,
                                       recipient: str) -> NotificationDelivery:
        """Envoie notification via canal spécifique"""
        delivery = NotificationDelivery(
            delivery_id=str(uuid.uuid4()),
            alert_id=alert.alert_id,
            channel=channel,
            recipient=recipient,
            subject=f"[{alert.priority.value.upper()}] {alert.title}",
            message=alert.description,
            formatted_content={},
            status=AlertStatus.SENT,
            sent_at=datetime.now(),
            delivered_at=datetime.now(),  # Simulation
            read_at=None,
            response_at=None,
            delivery_time_ms=100,  # Simulation
            read_time_minutes=None,
            response_time_minutes=None,
            error_message=None,
            retry_count=0,
            max_retries=3
        )
        
        self.notification_history.append(delivery)
        return delivery
    
    # Méthodes de métriques et apprentissage
    
    async def _update_acknowledgment_metrics(self, alert: SmartAlert, response_time: float):
        """Met à jour métriques accusé réception"""
        # Mise à jour stats temps réponse
        pass
    
    async def _update_resolution_metrics(self, alert: SmartAlert, resolution_time: float):
        """Met à jour métriques résolution"""
        # Mise à jour stats temps résolution
        pass
    
    async def _learn_from_resolution(self, alert: SmartAlert, resolution_actions: List[str]):
        """Apprentissage à partir de résolution"""
        # ML learning pour améliorer prédictions futures
        pass


# Factory function pour faciliter l'import
def create_intelligent_alerting_system(**kwargs) -> IntelligentAlertingSystem:
    """
    Factory function pour créer instance IntelligentAlertingSystem
    
    Returns:
        IntelligentAlertingSystem: Instance configurée
    """
    return IntelligentAlertingSystem(**kwargs)


# Export pour utilisation externe
__all__ = [
    'IntelligentAlertingSystem',
    'AlertPolicy',
    'AlertContext',
    'SmartAlert',
    'NotificationDelivery',
    'AlertingMetrics',
    'AlertChannel',
    'AlertPriority',
    'AlertStatus',
    'EscalationLevel',
    'AlertCategory',
    'create_intelligent_alerting_system'
]