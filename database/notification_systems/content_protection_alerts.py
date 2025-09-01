"""Content Protection Alert Notification Manager

Gestionnaire spécialisé pour les alertes de protection de contenu dans l'écosystème
IA Influencer Agent. Détection en temps réel, notifications d'urgence et escalation automatique.

Fonctionnalités:
- Alertes violations de droits d'auteur temps réel
- Notifications fingerprinting et matching
- Escalation automatique selon gravité
- Intégration juridique pour DMCA takedowns
- Dashboard monitoring protection contenu

Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

Copyright (c) 2025 Fahed Mlaiel. Tous droits réservés.
AVERTISSEMENT LÉGAL STRICT:
Ce code constitue la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification, distribution ou tentative de reverse engineering
non autorisée par écrit est formellement interdite et passible de poursuites judiciaires
selon le droit allemand et international. Contact: mlaiel@live.de
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, IntEnum
import asyncio
import logging
import json
import uuid
from decimal import Decimal
import aioredis
import asyncpg
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, DECIMAL, JSON
from sqlalchemy.dialects.postgresql import UUID
from pydantic import BaseModel, validator
import httpx
from jinja2 import Template

logger = logging.getLogger(__name__)


class ViolationType(Enum):
    """
Types de violations de protection de contenu"""

    DIRECT_COPY = "direct_copy"
    PARTIAL_USE = "partial_use"
    REMIX_UNAUTHORIZED = "remix_unauthorized"
    REUPLOAD = "reupload"
    COMMERCIAL_USE = "commercial_use"
    BACKGROUND_MUSIC = "background_music"
    DERIVATIVE_WORK = "derivative_work"
    AI_GENERATED_COPY = "ai_generated_copy"


class ViolationSeverity(IntEnum):
    """Niveaux de gravité des violations"""

    LOW = 1          # Utilisation partielle, non commerciale
    MEDIUM = 2       # Utilisation significative sans attribution
    HIGH = 3         # Utilisation commerciale non autorisée
    CRITICAL = 4     # Violation massive ou récidive


class Platform(Enum):
    """
Plateformes surveillées pour la protection de contenu"""

    YOUTUBE = "youtube"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    TWITCH = "twitch"
    DISCORD = "discord"
    BANDCAMP = "bandcamp"
    DEEZER = "deezer"
    APPLE_MUSIC = "apple_music"
    AMAZON_MUSIC = "amazon_music"


@dataclass
class ProtectionViolation:
    """Modèle de données pour une violation détectée"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = None
    content_id: str = None
    fingerprint_id: str = None
    violation_type: ViolationType = ViolationType.DIRECT_COPY
    severity: ViolationSeverity = ViolationSeverity.MEDIUM
    platform: Platform = Platform.YOUTUBE
    detected_url: str = None
    violator_info: Dict[str, Any] = field(default_factory=dict)
    similarity_score: float = 0.0
    content_segment: Dict[str, Any] = field(default_factory=dict)
    evidence_data: Dict[str, Any] = field(default_factory=dict)
    legal_action_required: bool = False
    revenue_impact: Decimal = field(default_factory=lambda: Decimal('0.00'))
    detected_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EscalationRule:
    """Règles d'escalation automatique selon le type et la gravité"""
    violation_type: ViolationType
    min_severity: ViolationSeverity
    escalation_delay: timedelta
    notification_channels: List[str]
    actions: List[str]
    legal_threshold: bool = False


class ContentProtectionAlertManager:
    """
    Gestionnaire avancé des alertes de protection de contenu
    
    Responsabilités:
    - Détection et classification des violations
    - Notifications multi-canal en temps réel
    - Escalation automatique selon gravité
    - Coordination avec équipes juridiques
    - Analytics et reporting protection
    """
    def __init__(self, db_pool: asyncpg.Pool, redis_client: aioredis.Redis):
        self.db_pool = db_pool
        self.redis = redis_client
        self.escalation_rules = self._load_escalation_rules()
        self.notification_templates = self._load_notification_templates()
        self.legal_contacts = self._load_legal_contacts()
        
    def _load_escalation_rules(self) -> List[EscalationRule]:
        """
Charge les règles d'escalation depuis la configuration"""
        return [
            EscalationRule(
                violation_type=ViolationType.COMMERCIAL_USE,
                min_severity=ViolationSeverity.HIGH,
                escalation_delay=timedelta(minutes=15),
                notification_channels=["email", "sms", "slack"],
                actions=["dmca_notice", "legal_review"],
                legal_threshold=True
            ),
            EscalationRule(
                violation_type=ViolationType.DIRECT_COPY,
                min_severity=ViolationSeverity.MEDIUM,
                escalation_delay=timedelta(hours=1),
                notification_channels=["email", "push"],
                actions=["platform_report", "user_notify"],
                legal_threshold=False
            ),
            EscalationRule(
                violation_type=ViolationType.AI_GENERATED_COPY,
                min_severity=ViolationSeverity.HIGH,
                escalation_delay=timedelta(minutes=30),
                notification_channels=["email", "slack", "webhook"],
                actions=["urgent_review", "ai_analysis"],
                legal_threshold=True
            )
        ]

    def _load_notification_templates(self) -> Dict[str, Template]:
        """Charge les templates de notification personnalisés"""
        templates = {
            "violation_detected": Template("""
                🚨 VIOLATION DE DROITS D'AUTEUR DÉTECTÉE

                Artiste: {{ artist_name }}
                Contenu: {{ content_title }}
                Plateforme: {{ platform }}
                URL: {{ violation_url }}
                
                Similarité: {{ similarity_score }}%
                Gravité: {{ severity }}
                Revenus estimés perdus: {{ revenue_impact }}€
                
                Action requise: {{ recommended_action }}
                
                🔗 Voir détails: {{ dashboard_url }}
                ⚡ Action rapide: {{ quick_action_url }}
            """),
            
            "critical_violation": Template("""
                🔴 ALERTE CRITIQUE - VIOLATION MAJEURE

                ⚠️ VIOLATION COMMERCIALE DÉTECTÉE
                
                Contenu protégé: {{ content_title }}
                Violateur: {{ violator_name }}
                Plateforme: {{ platform }}
                Impact financier: {{ revenue_impact }}€/jour
                
                🚨 ACTION IMMÉDIATE REQUISE
                - Envoi notice DMCA automatique activé
                - Équipe juridique notifiée
                - Surveillance renforcée activée
                
                📞 Contact urgence: +49 xxx xxx xxxx
            """),
            
            "escalation_legal": Template("""
                ⚖️ ESCALATION JURIDIQUE AUTOMATIQUE
                
                Violation: {{ violation_id }}
                Récidive: {{ is_repeat_offender }}
                Dommages estimés: {{ total_damages }}€
                
                Actions recommandées:
                {{ legal_actions | join('\n- ') }}
                
                Dossier complet: {{ legal_folder_url }}
            """)
        }
        
        return templates

    def _load_legal_contacts(self) -> Dict[str, Any]:
        """
Charge les contacts juridiques pour escalation"""
        return {
            "primary_lawyer": {
                "name": "Dr. Maria Schmidt",
                "email": "legal@ia-influencer.de",
                "phone": "+49 30 xxx xxxx",
                "specialties": ["copyright", "digital_rights", "dmca"]
            },
            "dmca_agent": {
                "name": "DMCA Protection Services",
                "email": "dmca@ia-influencer.de",
                "api_key": "dmca_api_key_here"
            },
            "platform_contacts": {
                "youtube": "copyright@youtube.com",
                "spotify": "legal@spotify.com",
                "soundcloud": "copyright@soundcloud.com"
            }
        }

    async def process_violation_detection(
        self,
        violation: ProtectionViolation
    ) -> Dict[str, Any]:
        """
        Traite une violation détectée avec classification et notification automatique
        
        Args:
            violation: Données de la violation détectée
            
        Returns:
            Dict contenant les actions prises et les notifications envoyées
        """
        try:
            # Enrichissement des données de violation
            enriched_violation = await self._enrich_violation_data(violation)
            
            # Classification automatique de la gravité
            classified_violation = await self._classify_violation_severity(enriched_violation)
            
            # Sauvegarde en base de données
            violation_id = await self._save_violation_to_db(classified_violation)
            
            # Vérification récidive
            is_repeat = await self._check_repeat_offender(classified_violation.violator_info)
            
            # Calcul impact financier
            revenue_impact = await self._calculate_revenue_impact(classified_violation)
            
            # Notifications immédiates selon gravité
            notifications_sent = await self._send_immediate_notifications(
                classified_violation, is_repeat, revenue_impact
            )
            
            # Configuration escalation automatique
            escalation_job = await self._schedule_escalation(classified_violation)
            
            # Déclenchement actions automatiques
            automated_actions = await self._trigger_automated_actions(classified_violation)
            
            # Métriques et logging
            await self._update_protection_metrics(classified_violation)
            
            logger.info(f"Violation {violation_id} traitée avec succès")
            
            return {
                "violation_id": violation_id,
                "severity": classified_violation.severity.name,
                "notifications_sent": notifications_sent,
                "escalation_scheduled": escalation_job,
                "automated_actions": automated_actions,
                "revenue_impact": float(revenue_impact),
                "is_repeat_offender": is_repeat
            }
            
        except Exception as e:
            logger.error(f"Erreur traitement violation: {str(e)}")
            await self._send_error_alert(violation, str(e))
            raise

    async def _enrich_violation_data(self, violation: ProtectionViolation) -> ProtectionViolation:
        """Enrichit les données de violation avec informations complémentaires"""
        # Récupération métadonnées contenu original
        original_content = await self._get_original_content_metadata(violation.content_id)
        
        # Analyse de la plateforme violatrice
        platform_analysis = await self._analyze_violating_platform(
            violation.platform, violation.detected_url
        )
        
        # Extraction données violateur
        violator_info = await self._extract_violator_information(
            violation.detected_url, violation.platform
        )
        
        # Géolocalisation et juridiction
        jurisdiction_info = await self._determine_jurisdiction(violator_info)
        
        violation.violator_info.update(violator_info)
        violation.metadata.update({
            "original_content": original_content,
            "platform_analysis": platform_analysis,
            "jurisdiction": jurisdiction_info,
            "enriched_at": datetime.now().isoformat()
        })
        
        return violation

    async def _classify_violation_severity(self, violation: ProtectionViolation) -> ProtectionViolation:
        """Classification automatique de la gravité basée sur ML et règles métier"""
        severity_factors = {
            "similarity_score": violation.similarity_score,
            "commercial_use": self._detect_commercial_use(violation),
            "duration_used": self._calculate_duration_used(violation),
            "platform_reach": await self._estimate_platform_reach(violation),
            "violator_history": await self._get_violator_history(violation.violator_info),
            "content_value": await self._assess_content_commercial_value(violation.content_id)
        }
        
        # Calcul score de gravité pondéré
        severity_score = self._calculate_severity_score(severity_factors)
        
        # Attribution niveau de gravité
        if severity_score >= 80:
            violation.severity = ViolationSeverity.CRITICAL
            violation.legal_action_required = True
        elif severity_score >= 60:
            violation.severity = ViolationSeverity.HIGH
            violation.legal_action_required = severity_factors["commercial_use"]
        elif severity_score >= 40:
            violation.severity = ViolationSeverity.MEDIUM
        else:
            violation.severity = ViolationSeverity.LOW
            
        violation.metadata["severity_factors"] = severity_factors
        violation.metadata["severity_score"] = severity_score
        
        return violation

    async def _send_immediate_notifications(
        self,
        violation: ProtectionViolation,
        is_repeat: bool,
        revenue_impact: Decimal
    ) -> List[Dict[str, Any]]:
        """Envoi notifications immédiates selon la gravité et le type"""
        notifications_sent = []
        
        # Template selection basé sur gravité
        if violation.severity == ViolationSeverity.CRITICAL:
            template_key = "critical_violation"
            channels = ["email", "sms", "slack", "webhook"]
        elif violation.legal_action_required:
            template_key = "escalation_legal"
            channels = ["email", "slack"]
        else:
            template_key = "violation_detected"
            channels = ["email", "push"]
        
        # Données template
        template_data = {
            "artist_name": await self._get_artist_name(violation.user_id),
            "content_title": await self._get_content_title(violation.content_id),
            "platform": violation.platform.value,
            "violation_url": violation.detected_url,
            "similarity_score": int(violation.similarity_score),
            "severity": violation.severity.name,
            "revenue_impact": float(revenue_impact),
            "violator_name": violation.violator_info.get("name", "Inconnu"),
            "is_repeat_offender": is_repeat,
            "violation_id": violation.id,
            "dashboard_url": f"https://dashboard.ia-influencer.de/protection/{violation.id}",
            "quick_action_url": f"https://api.ia-influencer.de/protection/quick-action/{violation.id}"
        }
        
        # Envoi sur chaque canal
        for channel in channels:
            try:
                notification_result = await self._send_channel_notification(
                    channel, template_key, template_data, violation
                )
                notifications_sent.append(notification_result)
            except Exception as e:
                logger.error(f"Erreur envoi notification {channel}: {str(e)}")
        
        return notifications_sent

    async def _trigger_automated_actions(self, violation: ProtectionViolation) -> List[str]:
        """Déclenche les actions automatiques selon le type et la gravité"""
        actions_triggered = []
        
        # Actions basées sur la gravité
        if violation.severity == ViolationSeverity.CRITICAL:
            # DMCA automatique
            dmca_result = await self._send_automated_dmca_notice(violation)
            if dmca_result:
                actions_triggered.append("dmca_notice_sent")
            
            # Notification équipe juridique
            await self._notify_legal_team(violation)
            actions_triggered.append("legal_team_notified")
            
            # Surveillance renforcée
            await self._enable_enhanced_monitoring(violation)
            actions_triggered.append("enhanced_monitoring_enabled")
        
        # Actions pour utilisation commerciale
        if violation.violation_type == ViolationType.COMMERCIAL_USE:
            # Calcul dommages
            damages = await self._calculate_damages(violation)
            actions_triggered.append(f"damages_calculated_{damages}")
            
            # Préparation dossier juridique
            await self._prepare_legal_case(violation, damages)
            actions_triggered.append("legal_case_prepared")
        
        # Actions plateforme spécifiques
        platform_actions = await self._trigger_platform_specific_actions(violation)
        actions_triggered.extend(platform_actions)
        
        return actions_triggered

    async def _schedule_escalation(self, violation: ProtectionViolation) -> Dict[str, Any]:
        """Programme l'escalation automatique selon les règles définies"""
        applicable_rules = [
            rule for rule in self.escalation_rules
            if (rule.violation_type == violation.violation_type and
                rule.min_severity <= violation.severity)
        ]
        
        if not applicable_rules:
            return {"status": "no_escalation_rules"}
        
        # Sélection règle la plus stricte
        primary_rule = min(applicable_rules, key=lambda r: r.escalation_delay)
        
        # Programmation tâche escalation
        escalation_time = datetime.now() + primary_rule.escalation_delay
        
        escalation_job = {
            "violation_id": violation.id,
            "rule_id": f"{primary_rule.violation_type.value}_{primary_rule.min_severity.value}",
            "scheduled_time": escalation_time.isoformat(),
            "actions": primary_rule.actions,
            "channels": primary_rule.notification_channels
        }
        
        # Sauvegarde job escalation
        await self.redis.setex(
            f"escalation:{violation.id}",
            int(primary_rule.escalation_delay.total_seconds()),
            json.dumps(escalation_job)
        )
        
        logger.info(f"Escalation programmée pour {escalation_time} - Violation {violation.id}")
        
        return escalation_job

    async def get_protection_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """Récupère les données du dashboard de protection pour un utilisateur"""
        async with self.db_pool.acquire() as conn:
            # Violations récentes
            recent_violations = await conn.fetch("""
                SELECT * FROM content_protection_violations 
                WHERE user_id = $1 
                ORDER BY detected_at DESC 
                LIMIT 50
            """, user_id)
            
            # Statistiques protection
            stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_violations,
                    COUNT(*) FILTER (WHERE severity = 'CRITICAL') as critical_count,
                    COUNT(*) FILTER (WHERE status = 'resolved') as resolved_count,
                    AVG(similarity_score) as avg_similarity,
                    SUM(revenue_impact) as total_revenue_impact
                FROM content_protection_violations 
                WHERE user_id = $1 
                AND detected_at >= NOW() - INTERVAL '30 days'
            """, user_id)
            
            # Plateformes les plus problématiques
            platform_stats = await conn.fetch("""
                SELECT 
                    platform, 
                    COUNT(*) as violation_count,
                    AVG(severity_score) as avg_severity
                FROM content_protection_violations 
                WHERE user_id = $1 
                GROUP BY platform 
                ORDER BY violation_count DESC
            """, user_id)
            
            return {
                "recent_violations": [dict(v) for v in recent_violations],
                "statistics": dict(stats) if stats else {},
                "platform_breakdown": [dict(p) for p in platform_stats],
                "protection_score": await self._calculate_protection_score(user_id),
                "recommendations": await self._get_protection_recommendations(user_id)
            }

    # Méthodes utilitaires (implementation details)
    async def _save_violation_to_db(self, violation: ProtectionViolation) -> str:
        """Sauvegarde violation en base de données avec toutes les métadonnées"""
        async with self.db_pool.acquire() as conn:
            violation_id = await conn.fetchval("""
                INSERT INTO content_protection_violations (
                    id, user_id, content_id, fingerprint_id, violation_type, 
                    severity, platform, detected_url, violator_info, 
                    similarity_score, content_segment, evidence_data,
                    legal_action_required, revenue_impact, detected_at, 
                    status, metadata
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, 
                    $11, $12, $13, $14, $15, $16, $17
                ) RETURNING id
            """,
                violation.id, violation.user_id, violation.content_id,
                violation.fingerprint_id, violation.violation_type.value,
                violation.severity.value, violation.platform.value,
                violation.detected_url, json.dumps(violation.violator_info),
                violation.similarity_score, json.dumps(violation.content_segment),
                json.dumps(violation.evidence_data), violation.legal_action_required,
                violation.revenue_impact, violation.detected_at,
                violation.status, json.dumps(violation.metadata)
            )
        return violation_id

    async def _detect_commercial_use(self, violation: ProtectionViolation) -> bool:
        """
Détecte si l'usage est commercial (publicités, monétisation)"""
        # Implementation de détection usage commercial via ML et analyse metadata
        return False  # Placeholder

    async def _calculate_revenue_impact(self, violation: ProtectionViolation) -> Decimal:
        """
Calcule l'impact sur les revenus estimé"""
        # Implementation calcul impact revenus basé sur analytics et données marché
        return Decimal('0.00')  # Placeholder

    async def _send_automated_dmca_notice(self, violation: ProtectionViolation) -> bool:
        """
Envoi automatique notice DMCA via API dédiée"""
        # Implementation envoi DMCA automatique
        return True  # Placeholder


# Export des classes principales
__all__ = [
    "ContentProtectionAlertManager",
    "ProtectionViolation", 
    "ViolationType",
    "ViolationSeverity",
    "Platform",
    "EscalationRule"
]
