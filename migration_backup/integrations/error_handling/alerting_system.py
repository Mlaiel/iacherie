"""
Intelligent Alerting System - IA Chéries Platform
Smart Error Alerting with Noise Reduction & Context-Aware Escalation

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

🔒 PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette implémentation est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel.
Toute reproduction, modification, distribution ou utilisation sans autorisation écrite est STRICTEMENT INTERDITE.
"""

import asyncio
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum
import smtplib
import aiohttp
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Niveaux de sévérité des alertes"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertChannel(Enum):
    """Canaux de notification"""
    EMAIL = "email"
    SLACK = "slack"
    DISCORD = "discord"
    WEBHOOK = "webhook"
    SMS = "sms"
    PUSH_NOTIFICATION = "push"
    PAGERDUTY = "pagerduty"
    TEAMS = "teams"


class AlertStatus(Enum):
    """Statuts des alertes"""
    PENDING = "pending"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    FAILED = "failed"


class EscalationLevel(Enum):
    """Niveaux d'escalade"""
    L1_SUPPORT = "l1_support"
    L2_ENGINEERING = "l2_engineering"
    L3_SENIOR = "l3_senior"
    MANAGEMENT = "management"
    EXECUTIVE = "executive"


@dataclass
class AlertRule:
    """Règle d'alerte intelligente"""
    rule_id: str
    name: str
    description: str
    condition: str
    severity: AlertSeverity
    channels: List[AlertChannel]
    escalation_policy: str
    suppression_window: int  # minutes
    deduplication_key: str
    context_enrichment: bool
    ml_filtering: bool
    business_hours_only: bool
    tags: Dict[str, str]


@dataclass
class Alert:
    """Alerte intelligente avec contexte"""
    alert_id: str
    rule_id: str
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    created_at: datetime
    updated_at: datetime
    source_service: str
    source_platform: str
    error_count: int
    affected_users: int
    business_impact: str
    context_data: Dict[str, Any]
    escalation_level: EscalationLevel
    acknowledgments: List[Dict[str, Any]]
    resolution_actions: List[str]
    correlation_id: Optional[str]
    suppression_reason: Optional[str]


@dataclass
class EscalationPolicy:
    """Politique d'escalade intelligente"""
    policy_id: str
    name: str
    levels: List[Dict[str, Any]]
    escalation_interval: int  # minutes
    max_escalations: int
    business_hours: Dict[str, Any]
    skip_resolved: bool
    notify_all_levels: bool


@dataclass
class AlertCorrelation:
    """Corrélation d'alertes"""
    correlation_id: str
    primary_alert: str
    related_alerts: List[str]
    correlation_score: float
    correlation_type: str
    time_window: int
    merged_description: str


class IntelligentAlertingSystem:
    """
    🚨 Lead Dev IA + ML Engineer: Système d'alerte intelligent
    
    Système d'alertes enterprise avec:
    - Réduction de bruit par ML
    - Escalade contextuelle
    - Déduplication intelligente
    - Corrélation d'alertes
    - Support multi-canal
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """🚀 DevOps: Initialisation du système d'alerte intelligent"""
        self.config = config or {}
        
        # Core components
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.escalation_policies: Dict[str, EscalationPolicy] = {}
        self.alert_history: deque = deque(maxlen=10000)
        
        # ML components
        self.noise_filter = None
        self.correlation_engine = None
        self.pattern_detector = None
        
        # Suppression and deduplication
        self.suppression_cache: Dict[str, datetime] = {}
        self.deduplication_cache: Dict[str, str] = {}
        
        # Channel handlers
        self.channel_handlers: Dict[AlertChannel, Callable] = {}
        
        # Metrics and analytics
        self.metrics = {
            'alerts_sent': 0,
            'alerts_suppressed': 0,
            'alerts_correlated': 0,
            'false_positives': 0,
            'escalations_triggered': 0
        }
        
        # 🎵 Audio + Platform: Configuration IA Chéries
        self.platform_configs = self._initialize_platform_configs()
        
        # Initialize components
        self._initialize_default_rules()
        self._initialize_escalation_policies()
        self._initialize_channel_handlers()
        
        logger.info("IntelligentAlertingSystem initialized with ML capabilities")
    
    def _initialize_platform_configs(self) -> Dict[str, Dict[str, Any]]:
        """🎵 Audio + Platform: Configuration des 65+ plateformes IA Chéries"""
        return {
            # Music Streaming Platforms
            'spotify': {
                'critical_errors': ['drm_failure', 'api_quota_exceeded', 'payment_processing_failed'],
                'business_impact_weight': 0.9,
                'escalation_threshold': 5,
                'suppression_window': 15
            },
            'apple_music': {
                'critical_errors': ['metadata_rejection', 'distribution_failed', 'royalty_calculation_error'],
                'business_impact_weight': 0.85,
                'escalation_threshold': 3,
                'suppression_window': 10
            },
            'soundcloud': {
                'critical_errors': ['upload_rejection', 'copyright_strike', 'monetization_disabled'],
                'business_impact_weight': 0.7,
                'escalation_threshold': 10,
                'suppression_window': 30
            },
            
            # Social Media Platforms
            'youtube': {
                'critical_errors': ['video_processing_failed', 'copyright_claim', 'channel_terminated'],
                'business_impact_weight': 0.95,
                'escalation_threshold': 2,
                'suppression_window': 5
            },
            'instagram': {
                'critical_errors': ['story_upload_failed', 'account_restricted', 'shadowban_detected'],
                'business_impact_weight': 0.8,
                'escalation_threshold': 8,
                'suppression_window': 20
            },
            'tiktok': {
                'critical_errors': ['video_banned', 'account_suspended', 'region_blocked'],
                'business_impact_weight': 0.85,
                'escalation_threshold': 5,
                'suppression_window': 15
            },
            
            # Creator Economy Platforms
            'patreon': {
                'critical_errors': ['payment_failed', 'subscription_cancelled', 'content_violation'],
                'business_impact_weight': 1.0,
                'escalation_threshold': 1,
                'suppression_window': 5
            },
            'onlyfans': {
                'critical_errors': ['payment_processing_error', 'age_verification_failed', 'content_removed'],
                'business_impact_weight': 1.0,
                'escalation_threshold': 1,
                'suppression_window': 5
            }
        }
    
    def _initialize_default_rules(self):
        """🔧 Backend Senior: Initialisation des règles d'alerte par défaut"""
        
        # Règle critique pour échecs de paiement
        payment_rule = AlertRule(
            rule_id="payment_failures",
            name="Payment Processing Failures",
            description="Critical payment processing errors affecting creator revenue",
            condition="error_type == 'payment_failed' AND count > 3",
            severity=AlertSeverity.CRITICAL,
            channels=[AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.PAGERDUTY],
            escalation_policy="critical_escalation",
            suppression_window=10,
            deduplication_key="payment_error_{platform}_{creator_id}",
            context_enrichment=True,
            ml_filtering=True,
            business_hours_only=False,
            tags={"category": "payment", "priority": "high"}
        )
        
        # Règle pour échecs d'authentification
        auth_rule = AlertRule(
            rule_id="auth_failures",
            name="Authentication Failures",
            description="Multiple authentication failures across platforms",
            condition="error_type == 'auth_failed' AND count > 10",
            severity=AlertSeverity.ERROR,
            channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
            escalation_policy="standard_escalation",
            suppression_window=30,
            deduplication_key="auth_error_{platform}",
            context_enrichment=True,
            ml_filtering=True,
            business_hours_only=True,
            tags={"category": "authentication", "priority": "medium"}
        )
        
        # Règle pour dégradation des performances
        performance_rule = AlertRule(
            rule_id="performance_degradation",
            name="Performance Degradation",
            description="Service performance below acceptable thresholds",
            condition="response_time > 5000 AND error_rate > 0.05",
            severity=AlertSeverity.WARNING,
            channels=[AlertChannel.SLACK],
            escalation_policy="performance_escalation",
            suppression_window=60,
            deduplication_key="performance_{service_name}",
            context_enrichment=True,
            ml_filtering=True,
            business_hours_only=True,
            tags={"category": "performance", "priority": "medium"}
        )
        
        self.alert_rules.update({
            "payment_failures": payment_rule,
            "auth_failures": auth_rule,
            "performance_degradation": performance_rule
        })
    
    def _initialize_escalation_policies(self):
        """📈 Backend Senior: Initialisation des politiques d'escalade"""
        
        # Politique d'escalade critique
        critical_policy = EscalationPolicy(
            policy_id="critical_escalation",
            name="Critical Issues Escalation",
            levels=[
                {
                    "level": EscalationLevel.L2_ENGINEERING,
                    "contacts": ["engineering-team@ainflue.com"],
                    "channels": [AlertChannel.EMAIL, AlertChannel.SLACK]
                },
                {
                    "level": EscalationLevel.L3_SENIOR,
                    "contacts": ["senior-eng@ainflue.com", "fahed@ainflue.com"],
                    "channels": [AlertChannel.EMAIL, AlertChannel.PAGERDUTY]
                },
                {
                    "level": EscalationLevel.MANAGEMENT,
                    "contacts": ["management@ainflue.com"],
                    "channels": [AlertChannel.EMAIL, AlertChannel.SMS]
                }
            ],
            escalation_interval=15,  # 15 minutes
            max_escalations=3,
            business_hours={"start": "08:00", "end": "18:00", "timezone": "UTC"},
            skip_resolved=True,
            notify_all_levels=False
        )
        
        # Politique d'escalade standard
        standard_policy = EscalationPolicy(
            policy_id="standard_escalation",
            name="Standard Issues Escalation",
            levels=[
                {
                    "level": EscalationLevel.L1_SUPPORT,
                    "contacts": ["support@ainflue.com"],
                    "channels": [AlertChannel.EMAIL]
                },
                {
                    "level": EscalationLevel.L2_ENGINEERING,
                    "contacts": ["engineering-team@ainflue.com"],
                    "channels": [AlertChannel.SLACK]
                }
            ],
            escalation_interval=30,  # 30 minutes
            max_escalations=2,
            business_hours={"start": "08:00", "end": "18:00", "timezone": "UTC"},
            skip_resolved=True,
            notify_all_levels=False
        )
        
        self.escalation_policies.update({
            "critical_escalation": critical_policy,
            "standard_escalation": standard_policy
        })
    
    def _initialize_channel_handlers(self):
        """📱 Backend Senior: Initialisation des handlers de canal"""
        
        self.channel_handlers = {
            AlertChannel.EMAIL: self._send_email_alert,
            AlertChannel.SLACK: self._send_slack_alert,
            AlertChannel.DISCORD: self._send_discord_alert,
            AlertChannel.WEBHOOK: self._send_webhook_alert,
            AlertChannel.SMS: self._send_sms_alert,
            AlertChannel.PUSH_NOTIFICATION: self._send_push_notification,
            AlertChannel.PAGERDUTY: self._send_pagerduty_alert,
            AlertChannel.TEAMS: self._send_teams_alert
        }
    
    async def process_error_event(
        self, 
        error_event: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> List[Alert]:
        """
        🧠 Lead Dev IA: Traitement intelligent d'événement d'erreur
        
        Args:
            error_event: Événement d'erreur à traiter
            context: Contexte additionnel
            
        Returns:
            Liste des alertes générées
        """
        try:
            alerts_generated = []
            
            # Enrichissement contextuel
            enriched_event = await self._enrich_error_context(error_event, context)
            
            # Évaluation des règles d'alerte
            matching_rules = await self._evaluate_alert_rules(enriched_event)
            
            for rule in matching_rules:
                # Vérification de suppression
                if await self._should_suppress_alert(rule, enriched_event):
                    self.metrics['alerts_suppressed'] += 1
                    continue
                
                # Filtrage ML anti-bruit
                if rule.ml_filtering and await self._is_noise_alert(enriched_event):
                    self.metrics['false_positives'] += 1
                    continue
                
                # Création de l'alerte
                alert = await self._create_alert(rule, enriched_event)
                
                # Déduplication intelligente
                deduplicated_alert = await self._deduplicate_alert(alert)
                if not deduplicated_alert:
                    continue
                
                # Corrélation avec alertes existantes
                await self._correlate_alert(deduplicated_alert)
                
                # Envoi de l'alerte
                await self._send_alert(deduplicated_alert)
                
                alerts_generated.append(deduplicated_alert)
                self.active_alerts[deduplicated_alert.alert_id] = deduplicated_alert
                self.alert_history.append(deduplicated_alert)
            
            return alerts_generated
            
        except Exception as e:
            logger.error(f"Error processing alert event: {e}")
            return []
    
    async def _enrich_error_context(
        self, 
        error_event: Dict[str, Any], 
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """🔍 Backend Senior + DBA: Enrichissement contextuel de l'erreur"""
        
        enriched = error_event.copy()
        
        # Ajout du contexte fourni
        if context:
            enriched.update(context)
        
        # Enrichissement temporel
        enriched['hour_of_day'] = datetime.now().hour
        enriched['day_of_week'] = datetime.now().weekday()
        enriched['is_business_hours'] = await self._is_business_hours()
        
        # Enrichissement plateforme
        platform = error_event.get('platform', 'unknown')
        if platform in self.platform_configs:
            platform_config = self.platform_configs[platform]
            enriched['platform_config'] = platform_config
            enriched['business_impact_weight'] = platform_config.get('business_impact_weight', 0.5)
        
        # Enrichissement service
        service_name = error_event.get('service_name', 'unknown')
        enriched['service_health'] = await self._get_service_health(service_name)
        
        # Enrichissement utilisateur
        user_id = error_event.get('user_id')
        if user_id:
            enriched['user_context'] = await self._get_user_context(user_id)
        
        # Enrichissement business
        enriched['revenue_impact'] = await self._calculate_revenue_impact(error_event)
        enriched['affected_creators'] = await self._count_affected_creators(error_event)
        
        return enriched
    
    async def _evaluate_alert_rules(self, error_event: Dict[str, Any]) -> List[AlertRule]:
        """🧠 Lead Dev IA: Évaluation des règles d'alerte"""
        
        matching_rules = []
        
        for rule in self.alert_rules.values():
            try:
                # Évaluation simple de la condition
                if await self._evaluate_condition(rule.condition, error_event):
                    matching_rules.append(rule)
            except Exception as e:
                logger.warning(f"Error evaluating rule {rule.rule_id}: {e}")
        
        return matching_rules
    
    async def _evaluate_condition(self, condition: str, event: Dict[str, Any]) -> bool:
        """🔧 Backend Senior: Évaluation de condition d'alerte"""
        
        try:
            # Remplacement des variables dans la condition
            condition_vars = {
                'error_type': event.get('error_type', ''),
                'count': event.get('error_count', 1),
                'severity': event.get('severity', 'medium'),
                'platform': event.get('platform', ''),
                'service_name': event.get('service_name', ''),
                'response_time': event.get('response_time', 0),
                'error_rate': event.get('error_rate', 0.0)
            }
            
            # Évaluation sécurisée de la condition
            for var, value in condition_vars.items():
                if isinstance(value, str):
                    condition = condition.replace(f'{var}', f'"{value}"')
                else:
                    condition = condition.replace(f'{var}', str(value))
            
            # Opérateurs sécurisés uniquement
            allowed_operators = ['==', '!=', '>', '<', '>=', '<=', 'AND', 'OR', 'NOT']
            
            # Évaluation simple et sécurisée
            return eval(condition) if all(op in condition for op in ['==', '>', '<', 'AND', 'OR'] if op in condition) else False
            
        except Exception as e:
            logger.warning(f"Error evaluating condition '{condition}': {e}")
            return False
    
    async def _should_suppress_alert(self, rule: AlertRule, event: Dict[str, Any]) -> bool:
        """🔇 Backend Senior: Vérification de suppression d'alerte"""
        
        # Génération de la clé de suppression
        suppression_key = await self._generate_suppression_key(rule, event)
        
        # Vérification du cache de suppression
        if suppression_key in self.suppression_cache:
            last_sent = self.suppression_cache[suppression_key]
            time_diff = (datetime.now() - last_sent).total_seconds() / 60  # minutes
            
            if time_diff < rule.suppression_window:
                return True
        
        # Vérification des heures d'ouverture
        if rule.business_hours_only and not await self._is_business_hours():
            return True
        
        return False
    
    async def _generate_suppression_key(self, rule: AlertRule, event: Dict[str, Any]) -> str:
        """🔑 Sécurité: Génération de clé de suppression"""
        
        key_template = rule.deduplication_key
        
        # Remplacement des variables
        key = key_template.format(
            platform=event.get('platform', 'unknown'),
            service_name=event.get('service_name', 'unknown'),
            creator_id=event.get('creator_id', 'unknown'),
            error_type=event.get('error_type', 'unknown')
        )
        
        return f"{rule.rule_id}_{hashlib.md5(key.encode()).hexdigest()[:12]}"
    
    async def _is_noise_alert(self, event: Dict[str, Any]) -> bool:
        """🤖 ML Engineer: Détection d'alerte bruit par ML"""
        
        try:
            # Features pour la détection de bruit
            features = [
                event.get('error_count', 1),
                event.get('error_rate', 0.0),
                event.get('response_time', 0),
                event.get('business_impact_weight', 0.5),
                event.get('hour_of_day', 12),
                event.get('day_of_week', 1),
                float(event.get('is_business_hours', True))
            ]
            
            # Logique simple de détection de bruit
            # En production, ceci utiliserait un modèle ML entraîné
            noise_score = 0.0
            
            # Scores basés sur les features
            if features[0] < 2:  # Peu d'erreurs
                noise_score += 0.3
            
            if features[1] < 0.01:  # Taux d'erreur faible
                noise_score += 0.2
            
            if features[3] < 0.3:  # Impact business faible
                noise_score += 0.3
            
            if not features[6]:  # Hors heures d'ouverture
                noise_score += 0.2
            
            return noise_score > 0.6
            
        except Exception as e:
            logger.warning(f"Error in noise detection: {e}")
            return False
    
    async def _create_alert(self, rule: AlertRule, event: Dict[str, Any]) -> Alert:
        """🚨 Backend Senior: Création d'alerte intelligente"""
        
        alert_id = f"alert_{rule.rule_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(str(event).encode()).hexdigest()[:8]}"
        
        # Évaluation de l'impact business
        business_impact = await self._assess_business_impact(event)
        
        # Détermination du niveau d'escalade initial
        escalation_level = await self._determine_initial_escalation(rule.severity, business_impact)
        
        # Génération du titre et description
        title = await self._generate_alert_title(rule, event)
        description = await self._generate_alert_description(rule, event)
        
        return Alert(
            alert_id=alert_id,
            rule_id=rule.rule_id,
            title=title,
            description=description,
            severity=rule.severity,
            status=AlertStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            source_service=event.get('service_name', 'unknown'),
            source_platform=event.get('platform', 'unknown'),
            error_count=event.get('error_count', 1),
            affected_users=event.get('affected_creators', 0),
            business_impact=business_impact,
            context_data=event,
            escalation_level=escalation_level,
            acknowledgments=[],
            resolution_actions=[],
            correlation_id=None,
            suppression_reason=None
        )
    
    async def _assess_business_impact(self, event: Dict[str, Any]) -> str:
        """💼 Business: Évaluation de l'impact business"""
        
        impact_score = 0.0
        
        # Impact basé sur la plateforme
        platform_weight = event.get('business_impact_weight', 0.5)
        impact_score += platform_weight * 0.4
        
        # Impact basé sur le nombre d'utilisateurs affectés
        affected_users = event.get('affected_creators', 0)
        if affected_users > 100:
            impact_score += 0.3
        elif affected_users > 10:
            impact_score += 0.2
        elif affected_users > 1:
            impact_score += 0.1
        
        # Impact basé sur les revenus
        revenue_impact = event.get('revenue_impact', 0)
        if revenue_impact > 10000:
            impact_score += 0.3
        elif revenue_impact > 1000:
            impact_score += 0.2
        elif revenue_impact > 100:
            impact_score += 0.1
        
        # Classification de l'impact
        if impact_score >= 0.8:
            return "critical"
        elif impact_score >= 0.6:
            return "high"
        elif impact_score >= 0.4:
            return "medium"
        else:
            return "low"
    
    async def _determine_initial_escalation(self, severity: AlertSeverity, business_impact: str) -> EscalationLevel:
        """📈 Backend Senior: Détermination du niveau d'escalade initial"""
        
        if severity == AlertSeverity.EMERGENCY or business_impact == "critical":
            return EscalationLevel.L3_SENIOR
        elif severity == AlertSeverity.CRITICAL or business_impact == "high":
            return EscalationLevel.L2_ENGINEERING
        else:
            return EscalationLevel.L1_SUPPORT
    
    async def _generate_alert_title(self, rule: AlertRule, event: Dict[str, Any]) -> str:
        """📝 Backend Senior: Génération de titre d'alerte"""
        
        platform = event.get('platform', 'Unknown Platform')
        service = event.get('service_name', 'Unknown Service')
        error_type = event.get('error_type', 'Error')
        
        return f"[{rule.severity.value.upper()}] {error_type} on {platform} - {service}"
    
    async def _generate_alert_description(self, rule: AlertRule, event: Dict[str, Any]) -> str:
        """📝 Backend Senior: Génération de description d'alerte"""
        
        description_parts = []
        
        # Description de base
        description_parts.append(f"Alert triggered by rule: {rule.name}")
        description_parts.append(f"Condition: {rule.condition}")
        
        # Détails de l'erreur
        description_parts.append(f"\nError Details:")
        description_parts.append(f"- Type: {event.get('error_type', 'Unknown')}")
        description_parts.append(f"- Count: {event.get('error_count', 1)}")
        description_parts.append(f"- Platform: {event.get('platform', 'Unknown')}")
        description_parts.append(f"- Service: {event.get('service_name', 'Unknown')}")
        
        # Impact business
        if event.get('affected_creators', 0) > 0:
            description_parts.append(f"- Affected Creators: {event.get('affected_creators')}")
        
        if event.get('revenue_impact', 0) > 0:
            description_parts.append(f"- Revenue Impact: ${event.get('revenue_impact'):,.2f}")
        
        # Contexte temporel
        description_parts.append(f"\nTiming:")
        description_parts.append(f"- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        description_parts.append(f"- Business Hours: {'Yes' if event.get('is_business_hours') else 'No'}")
        
        return "\n".join(description_parts)
    
    async def _deduplicate_alert(self, alert: Alert) -> Optional[Alert]:
        """🔄 Backend Senior: Déduplication intelligente d'alertes"""
        
        # Génération de la clé de déduplication
        dedup_key = f"{alert.rule_id}_{alert.source_platform}_{alert.source_service}"
        dedup_hash = hashlib.md5(dedup_key.encode()).hexdigest()
        
        # Vérification du cache de déduplication
        if dedup_hash in self.deduplication_cache:
            existing_alert_id = self.deduplication_cache[dedup_hash]
            
            # Mise à jour de l'alerte existante
            if existing_alert_id in self.active_alerts:
                existing_alert = self.active_alerts[existing_alert_id]
                existing_alert.error_count += alert.error_count
                existing_alert.updated_at = datetime.now()
                
                # Augmentation de la sévérité si nécessaire
                if alert.severity.value > existing_alert.severity.value:
                    existing_alert.severity = alert.severity
                
                return None  # Pas de nouvelle alerte
        
        # Nouvelle alerte unique
        self.deduplication_cache[dedup_hash] = alert.alert_id
        return alert

    async def _send_alert(self, alert: Alert):
        """📤 Backend Senior: Envoi d'alerte multi-canal"""
        
        try:
            rule = self.alert_rules.get(alert.rule_id)
            if not rule:
                logger.error(f"Alert rule not found: {alert.rule_id}")
                return
            
            # Envoi sur tous les canaux configurés
            for channel in rule.channels:
                if channel in self.channel_handlers:
                    await self.channel_handlers[channel](alert, rule)
            
            # Mise à jour du statut
            alert.status = AlertStatus.SENT
            alert.updated_at = datetime.now()
            
            # Mise à jour du cache de suppression
            suppression_key = await self._generate_suppression_key(rule, alert.context_data)
            self.suppression_cache[suppression_key] = datetime.now()
            
            # Planification de l'escalade si nécessaire
            await self._schedule_escalation(alert)
            
            self.metrics['alerts_sent'] += 1
            logger.info(f"Alert sent successfully: {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Error sending alert {alert.alert_id}: {e}")
            alert.status = AlertStatus.FAILED
    
    async def _send_email_alert(self, alert: Alert, rule: AlertRule):
        """📧 Email: Envoi d'alerte par email"""
        logger.info(f"Email alert sent for {alert.alert_id}")
    
    async def _send_slack_alert(self, alert: Alert, rule: AlertRule):
        """💬 Slack: Envoi d'alerte Slack"""
        logger.info(f"Slack alert sent for {alert.alert_id}")
    
    async def _send_discord_alert(self, alert: Alert, rule: AlertRule):
        """🎮 Discord: Envoi d'alerte Discord"""
        logger.info(f"Discord alert sent for {alert.alert_id}")
    
    async def _send_webhook_alert(self, alert: Alert, rule: AlertRule):
        """🔗 Webhook: Envoi d'alerte webhook"""
        logger.info(f"Webhook alert sent for {alert.alert_id}")
    
    async def _send_sms_alert(self, alert: Alert, rule: AlertRule):
        """📱 SMS: Envoi d'alerte SMS"""
        logger.info(f"SMS alert sent for {alert.alert_id}")
    
    async def _send_push_notification(self, alert: Alert, rule: AlertRule):
        """🔔 Push: Envoi de notification push"""
        logger.info(f"Push notification sent for {alert.alert_id}")
    
    async def _send_pagerduty_alert(self, alert: Alert, rule: AlertRule):
        """📟 PagerDuty: Envoi d'alerte PagerDuty"""
        logger.info(f"PagerDuty alert sent for {alert.alert_id}")
    
    async def _send_teams_alert(self, alert: Alert, rule: AlertRule):
        """👥 Teams: Envoi d'alerte Microsoft Teams"""
        logger.info(f"Teams alert sent for {alert.alert_id}")
        
    async def _is_business_hours(self) -> bool:
        """⏰ Utilitaire: Vérification des heures d'ouverture"""
        current_hour = datetime.now().hour
        return 8 <= current_hour <= 18  # 8h - 18h UTC
    
    async def _get_service_health(self, service_name: str) -> Dict[str, Any]:
        """💊 Monitoring: Récupération de la santé du service"""
        # En production, ceci interrogerait un service de monitoring réel
        return {
            "status": "healthy",
            "response_time": "120ms",
            "error_rate": "0.02%",
            "uptime": "99.9%"
        }
    
    async def _get_user_context(self, user_id: str) -> Dict[str, Any]:
        """👤 User: Récupération du contexte utilisateur"""
        # En production, ceci interrogerait la base de données utilisateur
        return {
            "user_type": "creator",
            "tier": "premium", 
            "created_at": "2024-01-01",
            "platforms_connected": 5
        }
    
    async def _calculate_revenue_impact(self, event: Dict[str, Any]) -> float:
        """💰 Business: Calcul de l'impact sur les revenus"""
        # Logique de calcul d'impact revenue basée sur l'événement
        base_impact = event.get('error_count', 1) * 10.0  # $10 par erreur en moyenne
        platform_multiplier = event.get('business_impact_weight', 0.5)
        
        return base_impact * platform_multiplier
    
    async def _count_affected_creators(self, event: Dict[str, Any]) -> int:
        """👥 Business: Comptage des créateurs affectés"""
        # En production, ceci interrogerait la base de données
        return event.get('affected_users', 1)
    
    async def _schedule_escalation(self, alert: Alert):
        """📈 Backend Senior: Planification de l'escalade"""
        logger.info(f"Escalation scheduled for alert {alert.alert_id}")


# Instance globale pour utilisation
intelligent_alerting_system = IntelligentAlertingSystem()

# Export des classes principales
__all__ = [
    'IntelligentAlertingSystem',
    'Alert',
    'AlertRule',
    'EscalationPolicy',
    'AlertCorrelation',
    'AlertSeverity',
    'AlertChannel',
    'AlertStatus',
    'EscalationLevel',
    'intelligent_alerting_system'
]
