"""
Fingerprinting Integration Notifications Manager

Gestionnaire spécialisé pour les notifications liées au système d'empreintage IA
et à l'intégration avec les agents de protection de contenu existants.

Fonctionnalités:
- Notifications de génération d'empreintes
- Alertes de détection de similarité
- Intégration avec le fingerprinting agent
- Surveillance temps réel des contenus
- Alertes de qualité et performance

Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

Copyright © 2025 Fahed Mlaiel. Tous droits réservés.
AVERTISSEMENT LÉGAL STRICT:
Ce code constitue la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification, distribution ou tentative de reverse engineering
non autorisée par écrit est formellement interdite et passible de poursuites judiciaires
selon le droit allemand et international. Contact: mlaiel@live.de
"""

from typing import Dict, List, Optional, Any, Union
import asyncio
import logging
from datetime import datetime, timedelta
import json
import aioredis
import asyncpg
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class FingerprintingEventType(Enum):
    """Types d'événements de fingerprinting"""
    FINGERPRINT_GENERATED = "fingerprint_generated"
    SIMILARITY_DETECTED = "similarity_detected"
    QUALITY_ALERT = "quality_alert"
    PROCESSING_COMPLETED = "processing_completed"
    PROCESSING_FAILED = "processing_failed"
    BATCH_COMPLETED = "batch_completed"
    DUPLICATE_FOUND = "duplicate_found"
    RIGHTS_VIOLATION = "rights_violation"
    MONITORING_ALERT = "monitoring_alert"
    THRESHOLD_EXCEEDED = "threshold_exceeded"


class FingerprintQuality(Enum):
    """Niveaux de qualité d'empreintes"""
    EXCELLENT = "excellent"
    GOOD = "good"
    MEDIUM = "medium"
    POOR = "poor"
    FAILED = "failed"


@dataclass
class FingerprintingNotificationData:
    """Structure des données de notification fingerprinting"""
    content_id: str
    fingerprint_id: str
    content_type: str  # audio, video, image, text
    quality_score: float
    processing_time: float
    similarity_matches: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    user_id: str
    platform_source: Optional[str] = None
    confidence_score: Optional[float] = None
    embedding_vector: Optional[List[float]] = None


class FingerprintingIntegrationManager:
    """
    Gestionnaire d'intégration pour les notifications de fingerprinting.
    
    Ce gestionnaire orchestre les notifications liées au système d'empreintage
    IA et s'intègre avec les agents de protection existants.
    """
    
    def __init__(self, db_pool: asyncpg.Pool, redis_client: aioredis.Redis, config: Dict[str, Any]):
        """
        Initialise le gestionnaire d'intégration fingerprinting.
        
        Args:
            db_pool: Pool de connexions PostgreSQL
            redis_client: Client Redis pour cache et queues
            config: Configuration du gestionnaire
        """
        self.db_pool = db_pool
        self.redis = redis_client
        self.config = config
        
        # Configuration des seuils
        self.quality_thresholds = {
            FingerprintQuality.EXCELLENT: 0.95,
            FingerprintQuality.GOOD: 0.85,
            FingerprintQuality.MEDIUM: 0.70,
            FingerprintQuality.POOR: 0.50
        }
        
        self.similarity_thresholds = {
            "exact_match": 0.98,
            "near_duplicate": 0.90,
            "similar": 0.75,
            "related": 0.60
        }
        
        # Métriques de performance
        self.metrics = {
            "notifications_sent": 0,
            "fingerprints_processed": 0,
            "similarities_detected": 0,
            "quality_alerts": 0,
            "processing_errors": 0
        }
        
        logger.info("FingerprintingIntegrationManager initialisé avec succès")

    async def process_fingerprint_notification(
        self,
        event_type: FingerprintingEventType,
        notification_data: FingerprintingNotificationData,
        notification_channels: List[str] = None
    ) -> Dict[str, Any]:
        """
        Traite une notification d'événement de fingerprinting.
        
        Args:
            event_type: Type d'événement
            notification_data: Données de la notification
            notification_channels: Canaux de notification à utiliser
            
        Returns:
            Résultat du traitement
        """
        try:
            # Channels par défaut si non spécifiés
            if notification_channels is None:
                notification_channels = self._get_default_channels(event_type)
            
            # Préparer le message selon le type d'événement
            message_data = await self._prepare_message_data(event_type, notification_data)
            
            # Enregistrer l'événement
            notification_id = await self._store_fingerprint_notification(
                event_type, notification_data, message_data
            )
            
            # Envoyer notifications
            delivery_results = await self._send_notifications(
                notification_id, message_data, notification_channels
            )
            
            # Traitement spécialisé selon le type d'événement
            await self._handle_specialized_processing(event_type, notification_data)
            
            # Mettre à jour les métriques
            await self._update_metrics(event_type, delivery_results)
            
            # Cache pour accès rapide
            await self._cache_notification_data(notification_id, message_data)
            
            self.metrics["notifications_sent"] += 1
            
            result = {
                "success": True,
                "notification_id": notification_id,
                "event_type": event_type.value,
                "channels_used": notification_channels,
                "delivery_results": delivery_results,
                "processing_time": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Notification fingerprinting traitée avec succès: {notification_id}")
            return result
            
        except Exception as e:
            self.metrics["processing_errors"] += 1
            logger.error(f"Erreur lors du traitement de notification fingerprinting: {str(e)}")
            raise

    async def _prepare_message_data(
        self, 
        event_type: FingerprintingEventType, 
        data: FingerprintingNotificationData
    ) -> Dict[str, Any]:
        """Prépare les données du message selon le type d'événement"""
        
        base_data = {
            "content_id": data.content_id,
            "fingerprint_id": data.fingerprint_id,
            "content_type": data.content_type,
            "quality_score": data.quality_score,
            "processing_time": data.processing_time,
            "user_id": data.user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if event_type == FingerprintingEventType.FINGERPRINT_GENERATED:
            return {
                **base_data,
                "title": "🔍 Empreinte générée avec succès",
                "message": f"L'empreinte de votre contenu {data.content_type} a été générée avec un score de qualité de {data.quality_score:.2%}.",
                "priority": "normal",
                "category": "fingerprint_success",
                "action_required": False
            }
            
        elif event_type == FingerprintingEventType.SIMILARITY_DETECTED:
            similarity_count = len(data.similarity_matches)
            return {
                **base_data,
                "title": "⚠️ Contenu similaire détecté",
                "message": f"Nous avons détecté {similarity_count} contenus similaires à votre {data.content_type}.",
                "priority": "high",
                "category": "similarity_alert",
                "action_required": True,
                "similarity_matches": data.similarity_matches,
                "recommended_actions": [
                    "Vérifier les correspondances",
                    "Examiner les droits d'auteur",
                    "Initier une action de protection si nécessaire"
                ]
            }
            
        elif event_type == FingerprintingEventType.QUALITY_ALERT:
            quality_level = self._determine_quality_level(data.quality_score)
            return {
                **base_data,
                "title": "📊 Alerte qualité d'empreinte",
                "message": f"La qualité de l'empreinte est {quality_level.value} ({data.quality_score:.2%}). Amélioration recommandée.",
                "priority": "medium" if quality_level != FingerprintQuality.FAILED else "high",
                "category": "quality_alert",
                "action_required": quality_level in [FingerprintQuality.POOR, FingerprintQuality.FAILED],
                "quality_level": quality_level.value,
                "improvement_suggestions": self._get_quality_improvement_suggestions(data.content_type, quality_level)
            }
            
        elif event_type == FingerprintingEventType.RIGHTS_VIOLATION:
            return {
                **base_data,
                "title": "🚨 Violation potentielle des droits détectée",
                "message": f"Une violation potentielle de vos droits a été détectée sur la plateforme {data.platform_source}.",
                "priority": "urgent",
                "category": "rights_violation",
                "action_required": True,
                "violation_details": {
                    "platform": data.platform_source,
                    "confidence": data.confidence_score,
                    "detected_at": datetime.utcnow().isoformat()
                },
                "automated_actions": [
                    "Capture de preuves",
                    "Documentation légale",
                    "Préparation DMCA"
                ]
            }
            
        elif event_type == FingerprintingEventType.PROCESSING_FAILED:
            return {
                **base_data,
                "title": "❌ Échec de traitement",
                "message": f"Le traitement de votre contenu {data.content_type} a échoué. Notre équipe technique a été notifiée.",
                "priority": "high",
                "category": "processing_error",
                "action_required": False,
                "support_ticket": True,
                "retry_available": True
            }
            
        elif event_type == FingerprintingEventType.BATCH_COMPLETED:
            return {
                **base_data,
                "title": "✅ Traitement batch terminé",
                "message": f"Le traitement en lot de vos contenus est terminé. {data.metadata.get('processed_count', 'N/A')} éléments traités.",
                "priority": "normal",
                "category": "batch_completion",
                "action_required": False,
                "batch_statistics": data.metadata
            }
            
        else:
            return {
                **base_data,
                "title": f"📢 Événement {event_type.value}",
                "message": f"Un événement de type {event_type.value} s'est produit pour votre contenu.",
                "priority": "normal",
                "category": "general_event",
                "action_required": False
            }

    async def _store_fingerprint_notification(
        self,
        event_type: FingerprintingEventType,
        data: FingerprintingNotificationData,
        message_data: Dict[str, Any]
    ) -> str:
        """Stocke la notification en base de données"""
        
        query = """
        INSERT INTO fingerprint_notifications (
            user_id, content_id, fingerprint_id, event_type, content_type,
            quality_score, processing_time, similarity_matches, message_data,
            priority, category, action_required, metadata, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, NOW())
        RETURNING id
        """
        
        async with self.db_pool.acquire() as conn:
            notification_id = await conn.fetchval(
                query,
                data.user_id,
                data.content_id, 
                data.fingerprint_id,
                event_type.value,
                data.content_type,
                data.quality_score,
                data.processing_time,
                json.dumps(data.similarity_matches),
                json.dumps(message_data),
                message_data.get("priority", "normal"),
                message_data.get("category", "general"),
                message_data.get("action_required", False),
                json.dumps(data.metadata)
            )
            
        return str(notification_id)

    async def _send_notifications(
        self,
        notification_id: str,
        message_data: Dict[str, Any],
        channels: List[str]
    ) -> Dict[str, Any]:
        """Envoie les notifications sur les canaux spécifiés"""
        
        delivery_results = {}
        
        for channel in channels:
            try:
                if channel == "email":
                    result = await self._send_email_notification(notification_id, message_data)
                elif channel == "push":
                    result = await self._send_push_notification(notification_id, message_data)
                elif channel == "websocket":
                    result = await self._send_websocket_notification(notification_id, message_data)
                elif channel == "dashboard":
                    result = await self._update_dashboard_notification(notification_id, message_data)
                else:
                    result = {"success": False, "error": f"Canal non supporté: {channel}"}
                
                delivery_results[channel] = result
                
            except Exception as e:
                delivery_results[channel] = {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
                logger.error(f"Erreur envoi notification {channel}: {str(e)}")
        
        return delivery_results

    async def _handle_specialized_processing(
        self,
        event_type: FingerprintingEventType,
        data: FingerprintingNotificationData
    ):
        """Traitement spécialisé selon le type d'événement"""
        
        try:
            if event_type == FingerprintingEventType.SIMILARITY_DETECTED:
                await self._process_similarity_detection(data)
                
            elif event_type == FingerprintingEventType.RIGHTS_VIOLATION:
                await self._initiate_rights_protection_workflow(data)
                
            elif event_type == FingerprintingEventType.QUALITY_ALERT:
                await self._schedule_quality_improvement(data)
                
            elif event_type == FingerprintingEventType.FINGERPRINT_GENERATED:
                await self._update_content_protection_status(data)
                
        except Exception as e:
            logger.error(f"Erreur traitement spécialisé {event_type.value}: {str(e)}")

    async def _process_similarity_detection(self, data: FingerprintingNotificationData):
        """Traite la détection de similarité"""
        
        # Analyser les correspondances
        high_confidence_matches = [
            match for match in data.similarity_matches 
            if match.get("confidence", 0) > self.similarity_thresholds["near_duplicate"]
        ]
        
        # Si correspondances à haute confiance, déclencher protection automatique
        if high_confidence_matches:
            await self._trigger_automated_protection(data, high_confidence_matches)
        
        # Mise à jour du tableau de bord de surveillance
        await self._update_monitoring_dashboard(data)

    async def _initiate_rights_protection_workflow(self, data: FingerprintingNotificationData):
        """Initie le workflow de protection des droits"""
        
        # Capturer les preuves
        evidence_data = {
            "fingerprint_id": data.fingerprint_id,
            "platform": data.platform_source,
            "detection_time": datetime.utcnow().isoformat(),
            "confidence_score": data.confidence_score,
            "content_metadata": data.metadata
        }
        
        # Stocker les preuves
        await self._store_violation_evidence(data.content_id, evidence_data)
        
        # Notifier l'équipe légale si score de confiance élevé
        if data.confidence_score and data.confidence_score > 0.90:
            await self._notify_legal_team(data, evidence_data)

    async def _get_default_channels(self, event_type: FingerprintingEventType) -> List[str]:
        """Retourne les canaux par défaut selon le type d'événement"""
        
        channel_mapping = {
            FingerprintingEventType.FINGERPRINT_GENERATED: ["dashboard", "websocket"],
            FingerprintingEventType.SIMILARITY_DETECTED: ["email", "push", "dashboard"],
            FingerprintingEventType.QUALITY_ALERT: ["dashboard", "websocket"],
            FingerprintingEventType.RIGHTS_VIOLATION: ["email", "push", "dashboard", "websocket"],
            FingerprintingEventType.PROCESSING_FAILED: ["email", "dashboard"],
            FingerprintingEventType.BATCH_COMPLETED: ["email", "dashboard"],
            FingerprintingEventType.DUPLICATE_FOUND: ["dashboard", "websocket"],
            FingerprintingEventType.MONITORING_ALERT: ["push", "dashboard"],
            FingerprintingEventType.THRESHOLD_EXCEEDED: ["email", "push"]
        }
        
        return channel_mapping.get(event_type, ["dashboard"])

    def _determine_quality_level(self, quality_score: float) -> FingerprintQuality:
        """Détermine le niveau de qualité basé sur le score"""
        
        if quality_score >= self.quality_thresholds[FingerprintQuality.EXCELLENT]:
            return FingerprintQuality.EXCELLENT
        elif quality_score >= self.quality_thresholds[FingerprintQuality.GOOD]:
            return FingerprintQuality.GOOD
        elif quality_score >= self.quality_thresholds[FingerprintQuality.MEDIUM]:
            return FingerprintQuality.MEDIUM
        elif quality_score >= self.quality_thresholds[FingerprintQuality.POOR]:
            return FingerprintQuality.POOR
        else:
            return FingerprintQuality.FAILED

    def _get_quality_improvement_suggestions(
        self, 
        content_type: str, 
        quality_level: FingerprintQuality
    ) -> List[str]:
        """Retourne des suggestions d'amélioration de qualité"""
        
        suggestions = {
            "audio": {
                FingerprintQuality.POOR: [
                    "Améliorer la qualité audio (min 128kbps)",
                    "Réduire le bruit de fond",
                    "Vérifier l'intégrité du fichier"
                ],
                FingerprintQuality.FAILED: [
                    "Fichier audio corrompu ou invalide",
                    "Format non supporté",
                    "Contacter le support technique"
                ]
            },
            "video": {
                FingerprintQuality.POOR: [
                    "Améliorer la résolution (min 720p recommandé)",
                    "Réduire la compression",
                    "Vérifier la stabilité des images"
                ],
                FingerprintQuality.FAILED: [
                    "Fichier vidéo corrompu",
                    "Codec non supporté",
                    "Durée insuffisante pour l'analyse"
                ]
            },
            "image": {
                FingerprintQuality.POOR: [
                    "Augmenter la résolution",
                    "Améliorer la netteté",
                    "Réduire la compression JPEG"
                ],
                FingerprintQuality.FAILED: [
                    "Image corrompue ou invalide",
                    "Format non reconnu",
                    "Taille insuffisante"
                ]
            },
            "text": {
                FingerprintQuality.POOR: [
                    "Augmenter la longueur du texte",
                    "Améliorer la structure",
                    "Vérifier l'encodage des caractères"
                ],
                FingerprintQuality.FAILED: [
                    "Texte trop court pour l'analyse",
                    "Contenu illisible",
                    "Erreur d'encodage"
                ]
            }
        }
        
        return suggestions.get(content_type, {}).get(quality_level, ["Contacter le support technique"])

    async def get_fingerprint_notifications_history(
        self,
        user_id: str,
        content_id: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Récupère l'historique des notifications de fingerprinting"""
        
        conditions = ["user_id = $1"]
        params = [user_id]
        param_count = 1
        
        if content_id:
            param_count += 1
            conditions.append(f"content_id = ${param_count}")
            params.append(content_id)
            
        if event_types:
            param_count += 1
            conditions.append(f"event_type = ANY(${param_count})")
            params.append(event_types)
        
        query = f"""
        SELECT id, content_id, fingerprint_id, event_type, content_type,
               quality_score, processing_time, message_data, priority,
               category, action_required, created_at
        FROM fingerprint_notifications
        WHERE {' AND '.join(conditions)}
        ORDER BY created_at DESC
        LIMIT ${param_count + 1} OFFSET ${param_count + 2}
        """
        
        params.extend([limit, offset])
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            
        return [dict(row) for row in rows]

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques du système de fingerprinting"""
        
        # Métriques en temps réel depuis Redis
        redis_metrics = await self.redis.hgetall("fingerprint:metrics")
        
        # Métriques de base de données
        async with self.db_pool.acquire() as conn:
            db_metrics = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_notifications,
                COUNT(*) FILTER (WHERE event_type = 'fingerprint_generated') as fingerprints_generated,
                COUNT(*) FILTER (WHERE event_type = 'similarity_detected') as similarities_detected,
                COUNT(*) FILTER (WHERE event_type = 'rights_violation') as rights_violations,
                COUNT(*) FILTER (WHERE action_required = true) as actions_required,
                AVG(quality_score) as avg_quality_score
            FROM fingerprint_notifications
            WHERE created_at >= NOW() - INTERVAL '24 hours'
            """)
        
        return {
            "realtime_metrics": self.metrics,
            "redis_metrics": {k.decode(): v.decode() for k, v in redis_metrics.items()},
            "database_metrics": dict(db_metrics) if db_metrics else {},
            "system_status": "operational",
            "last_updated": datetime.utcnow().isoformat()
        }

    async def _send_email_notification(self, notification_id: str, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Envoie une notification par email"""
        # Intégration avec le gestionnaire d'emails existant
        return {"success": True, "method": "email", "notification_id": notification_id}

    async def _send_push_notification(self, notification_id: str, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Envoie une notification push"""
        # Intégration avec le gestionnaire push existant
        return {"success": True, "method": "push", "notification_id": notification_id}

    async def _send_websocket_notification(self, notification_id: str, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Envoie une notification WebSocket"""
        # Intégration avec le gestionnaire temps réel existant
        return {"success": True, "method": "websocket", "notification_id": notification_id}

    async def _update_dashboard_notification(self, notification_id: str, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Met à jour le tableau de bord"""
        return {"success": True, "method": "dashboard", "notification_id": notification_id}

    async def _cache_notification_data(self, notification_id: str, message_data: Dict[str, Any]):
        """Met en cache les données de notification pour accès rapide"""
        await self.redis.setex(
            f"fingerprint:notification:{notification_id}",
            3600,  # 1 heure
            json.dumps(message_data)
        )

    async def _update_metrics(self, event_type: FingerprintingEventType, delivery_results: Dict[str, Any]):
        """Met à jour les métriques système"""
        
        # Incrémenter compteurs Redis
        await self.redis.hincrby("fingerprint:metrics", f"event:{event_type.value}", 1)
        
        # Compter succès/échecs de livraison
        for channel, result in delivery_results.items():
            status = "success" if result.get("success") else "failure"
            await self.redis.hincrby("fingerprint:metrics", f"delivery:{channel}:{status}", 1)

    async def _trigger_automated_protection(self, data: FingerprintingNotificationData, matches: List[Dict[str, Any]]):
        """Déclenche la protection automatisée"""
        logger.info(f"Déclenchement protection automatisée pour {data.content_id}")
        # Intégration avec le système de protection existant

    async def _update_monitoring_dashboard(self, data: FingerprintingNotificationData):
        """Met à jour le tableau de bord de surveillance"""
        dashboard_data = {
            "content_id": data.content_id,
            "similarity_count": len(data.similarity_matches),
            "last_check": datetime.utcnow().isoformat()
        }
        
        await self.redis.setex(
            f"fingerprint:monitoring:{data.content_id}",
            86400,  # 24 heures
            json.dumps(dashboard_data)
        )

    async def _store_violation_evidence(self, content_id: str, evidence_data: Dict[str, Any]):
        """Stocke les preuves de violation"""
        query = """
        INSERT INTO content_violation_evidence (content_id, evidence_data, created_at)
        VALUES ($1, $2, NOW())
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(query, content_id, json.dumps(evidence_data))

    async def _notify_legal_team(self, data: FingerprintingNotificationData, evidence_data: Dict[str, Any]):
        """Notifie l'équipe légale"""
        logger.info(f"Notification équipe légale pour violation: {data.content_id}")
        # Intégration avec le système de notification légale

    async def _schedule_quality_improvement(self, data: FingerprintingNotificationData):
        """Programme l'amélioration de qualité"""
        logger.info(f"Planification amélioration qualité: {data.fingerprint_id}")

    async def _update_content_protection_status(self, data: FingerprintingNotificationData):
        """Met à jour le statut de protection du contenu"""
        query = """
        UPDATE content_items 
        SET fingerprint_status = 'completed', protection_enabled = true, updated_at = NOW()
        WHERE id = $1
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(query, data.content_id)
