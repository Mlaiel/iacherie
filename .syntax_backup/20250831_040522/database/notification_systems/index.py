"""
Enterprise Notification Systems Index Module

Point d'entrée principal pour tous les gestionnaires de notifications industriels
de la plateforme IA Influencer Agent avec protection de contenu et monétisation.

Ce module orchestre l'ensemble des systèmes de notifications spécialisés:
- Protection de contenu et violations de droits d'auteur
- Revenus et monétisation multi-plateformes  
- Collaborations et partenariats d'artistes
- Analytics de performance et insights IA
- Distribution cross-platform automatisée

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
from dataclasses import dataclass
import aioredis
import asyncpg

# Import des gestionnaires spécialisés
from .email_manager import EmailNotificationManager
from .push_manager import PushNotificationManager  
from .realtime_manager import RealtimeNotificationManager
from .alert_manager import AlertManager
from .queue_manager import QueueManager
from .content_protection_alerts import ContentProtectionAlertManager
from .revenue_notifications import RevenueNotificationManager
from .collaboration_notifications import CollaborationNotificationManager
from .performance_analytics import PerformanceAnalyticsManager
from .distribution_notifications import MultiPlatformDistributionManager

# Import des nouveaux gestionnaires d'intégration
from .fingerprint_integration_notifications import FingerprintingIntegrationManager
from .crawler_surveillance_notifications import CrawlerSurveillanceManager
from .licensing_monetization_notifications import LicensingMonetizationManager
from .seo_optimization_notifications import SEOOptimizationManager
from .collaboration_matching_notifications import CollaborationMatchingManager
from .collaboration_notifications import CollaborationNotificationManager
from .performance_analytics import PerformanceAnalyticsManager
from .distribution_notifications import MultiPlatformDistributionManager

# Import des nouveaux gestionnaires intégrés selon cahier des charges
from .fingerprint_integration_notifications import FingerprintingIntegrationManager
from .crawler_surveillance_notifications import CrawlerSurveillanceManager
from .licensing_monetization_notifications import LicensingMonetizationManager

from .schema import create_notification_schema_sql

logger = logging.getLogger(__name__)


@dataclass
class NotificationSystemConfig:
    """Configuration globale du système de notifications enrichie selon cahier des charges"""
    db_pool: asyncpg.Pool
    redis_client: aioredis.Redis
    max_workers: int = 10
    batch_size: int = 100
    retry_attempts: int = 3
    timeout_seconds: int = 30
    enable_analytics: bool = True
    enable_real_time: bool = True
    debug_mode: bool = False
    
    # Configurations spécialisées selon logique métier
    fingerprinting_config: Dict[str, Any] = None
    surveillance_config: Dict[str, Any] = None
    licensing_config: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialise les configurations par défaut"""
        if self.fingerprinting_config is None:
            self.fingerprinting_config = {
                "quality_thresholds": {
                    "excellent": 0.95,
                    "good": 0.85,
                    "medium": 0.70,
                    "poor": 0.50
                },
                "similarity_thresholds": {
                    "exact_match": 0.98,
                    "near_duplicate": 0.90,
                    "similar": 0.75,
                    "related": 0.60
                },
                "enable_ai_detection": True,
                "enable_rights_protection": True
            }
        
        if self.surveillance_config is None:
            self.surveillance_config = {
                "platforms": ["youtube", "tiktok", "instagram", "twitter", "soundcloud"],
                "scan_frequency": 3600,  # 1 heure
                "enable_real_time": True,
                "enable_automated_takedown": True,
                "violation_thresholds": {
                    "critical": 0.95,
                    "high": 0.85,
                    "medium": 0.70,
                    "low": 0.50
                }
            }
        
        if self.licensing_config is None:
            self.licensing_config = {
                "supported_currencies": ["EUR", "USD", "GBP", "CAD", "AUD"],
                "auto_payment_threshold": 50.00,
                "revenue_milestones": [100, 500, 1000, 5000, 10000, 25000, 50000, 100000],
                "enable_tax_documents": True,
                "enable_contract_automation": True
            }


class EnterpriseNotificationOrchestrator:
    """
    Orchestrateur principal des systèmes de notifications industriels
    
    Responsabilités:
    - Coordination des gestionnaires spécialisés
    - Routing intelligent des notifications
    - Monitoring global et métriques
    - Optimisation des performances
    - Gestion des pannes et recovery
    """

    def __init__(self, config: NotificationSystemConfig):
        self.config = config
        self.managers = {}
        self.is_initialized = False
        self.metrics = {
            "total_sent": 0,
            "total_failed": 0,
            "average_delivery_time": 0.0,
            "last_reset": datetime.now()
        }
        
    async def initialize(self) -> Dict[str, Any]:
        """Initialise tous les gestionnaires de notifications"""
        try:
            # Initialisation des gestionnaires core
            self.managers["email"] = EmailNotificationManager(
                self.config.db_pool, self.config.redis_client
            )
            self.managers["push"] = PushNotificationManager(
                self.config.db_pool, self.config.redis_client
            )
            self.managers["realtime"] = RealtimeNotificationManager(
                self.config.db_pool, self.config.redis_client
            )
            self.managers["alert"] = AlertManager(
                self.config.db_pool, self.config.redis_client
            )
            self.managers["queue"] = QueueManager(
                self.config.db_pool, self.config.redis_client
            )
            
            # Initialisation des gestionnaires spécialisés
            self.managers["protection"] = ContentProtectionAlertManager(
                self.config.db_pool, self.config.redis_client
            )
            self.managers["revenue"] = RevenueNotificationManager(
                self.config.db_pool, self.config.redis_client
            )
            self.managers["collaboration"] = CollaborationNotificationManager(
                self.config.db_pool, self.config.redis_client
            )
            self.managers["analytics"] = PerformanceAnalyticsManager(
                self.config.db_pool, self.config.redis_client
            )
            self.managers["distribution"] = MultiPlatformDistributionManager(
                self.config.db_pool, self.config.redis_client
            )
            
            # Initialisation des nouveaux gestionnaires intégrés selon cahier des charges
            self.managers["fingerprinting"] = FingerprintingIntegrationManager(
                self.config.db_pool, self.config.redis_client, self.config.fingerprinting_config
            )
            self.managers["surveillance"] = CrawlerSurveillanceManager(
                self.config.db_pool, self.config.redis_client, self.config.surveillance_config
            )
            self.managers["licensing"] = LicensingMonetizationManager(
                self.config.db_pool, self.config.redis_client, self.config.licensing_config
            )
            self.managers["seo"] = SEOOptimizationManager(
                self.config.db_pool, self.config.redis_client, {}
            )
            self.managers["collab_matching"] = CollaborationMatchingManager(
                self.config.db_pool, self.config.redis_client, {}
            )
            
            # Vérification de l'état des gestionnaires
            health_checks = []
            for name, manager in self.managers.items():
                if hasattr(manager, 'health_check'):
                    health_checks.append(manager.health_check())
            
            if health_checks:
                health_results = await asyncio.gather(*health_checks, return_exceptions=True)
                logger.info(f"Health checks completed: {len(health_results)} managers")
            
            self.is_initialized = True
            logger.info("Enterprise Notification Orchestrator initialisé avec succès")
            
            return {
                "status": "initialized",
                "managers_count": len(self.managers),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur initialisation orchestrateur: {str(e)}")
            raise

    async def send_notification(
        self,
        notification_type: str,
        user_id: str,
        data: Dict[str, Any],
        channels: List[str] = None,
        priority: int = 3
    ) -> Dict[str, Any]:
        """
        Envoie une notification via le gestionnaire approprié
        
        Args:
            notification_type: Type de notification (protection, revenue, etc.)
            user_id: ID de l'utilisateur destinataire
            data: Données de la notification
            channels: Canaux de notification (email, push, etc.)
            priority: Priorité (1=urgent, 5=low)
            
        Returns:
            Résultats de l'envoi avec métriques
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            start_time = datetime.now()
            
            # Sélection du gestionnaire approprié
            manager = self._select_manager(notification_type)
            if not manager:
                raise ValueError(f"Gestionnaire non trouvé pour type: {notification_type}")
            
            # Préparation de la notification
            prepared_notification = await self._prepare_notification(
                notification_type, user_id, data, channels, priority
            )
            
            # Envoi via le gestionnaire approprié
            if notification_type == "protection":
                result = await manager.process_violation_detection(prepared_notification)
            elif notification_type == "revenue":
                result = await manager.process_revenue_transaction(prepared_notification)
            elif notification_type == "collaboration":
                result = await manager.process_collaboration_request(
                    user_id, prepared_notification.get("target_id"), prepared_notification
                )
            elif notification_type == "analytics":
                result = await manager.collect_performance_data(
                    user_id, prepared_notification.get("platforms"), 
                    prepared_notification.get("metrics")
                )
            elif notification_type == "distribution":
                result = await manager.create_distribution_job(
                    user_id, prepared_notification.get("content_data"),
                    prepared_notification.get("distribution_config")
                )
            else:
                # Gestionnaires core (email, push, etc.)
                result = await manager.send_notification(prepared_notification)
            
            # Métriques et logging
            delivery_time = (datetime.now() - start_time).total_seconds()
            await self._update_metrics(notification_type, "sent", delivery_time)
            
            logger.info(f"Notification {notification_type} envoyée avec succès pour {user_id}")
            
            return {
                "status": "success",
                "notification_type": notification_type,
                "user_id": user_id,
                "delivery_time": delivery_time,
                "result": result
            }
            
        except Exception as e:
            await self._update_metrics(notification_type, "failed", 0)
            logger.error(f"Erreur envoi notification {notification_type}: {str(e)}")
            raise

    async def batch_send_notifications(
        self,
        notifications: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Envoi en lot de notifications avec optimisation"""
        if not notifications:
            return {"status": "no_notifications", "processed": 0}
        
        try:
            # Groupement par type pour optimisation
            grouped_notifications = {}
            for notif in notifications:
                notif_type = notif.get("type", "unknown")
                if notif_type not in grouped_notifications:
                    grouped_notifications[notif_type] = []
                grouped_notifications[notif_type].append(notif)
            
            # Traitement parallèle par type
            batch_tasks = []
            for notif_type, notif_list in grouped_notifications.items():
                for notif in notif_list:
                    task = self.send_notification(
                        notif_type,
                        notif["user_id"],
                        notif.get("data", {}),
                        notif.get("channels", []),
                        notif.get("priority", 3)
                    )
                    batch_tasks.append(task)
            
            # Exécution avec limitation de concurrence
            semaphore = asyncio.Semaphore(self.config.max_workers)
            
            async def limited_send(task):
                async with semaphore:
                    return await task
            
            results = await asyncio.gather(
                *[limited_send(task) for task in batch_tasks],
                return_exceptions=True
            )
            
            # Analyse des résultats
            successful = sum(1 for r in results if not isinstance(r, Exception))
            failed = len(results) - successful
            
            return {
                "status": "completed",
                "total_processed": len(results),
                "successful": successful,
                "failed": failed,
                "success_rate": successful / len(results) if results else 0,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Erreur batch send: {str(e)}")
            raise

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques globales du système"""
        try:
            # Métriques globales
            global_metrics = dict(self.metrics)
            
            # Métriques par gestionnaire
            manager_metrics = {}
            for name, manager in self.managers.items():
                if hasattr(manager, 'get_metrics'):
                    manager_metrics[name] = await manager.get_metrics()
            
            # Métriques de la queue Redis
            queue_metrics = await self._get_queue_metrics()
            
            # Métriques de performance base de données
            db_metrics = await self._get_database_metrics()
            
            return {
                "global": global_metrics,
                "managers": manager_metrics,
                "queue": queue_metrics,
                "database": db_metrics,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération métriques: {str(e)}")
            return {"error": str(e)}

    def _select_manager(self, notification_type: str):
        """Sélectionne le gestionnaire approprié selon le type"""
        type_mapping = {
            "email": "email",
            "push": "push", 
            "realtime": "realtime",
            "alert": "alert",
            "protection": "protection",
            "revenue": "revenue",
            "collaboration": "collaboration",
            "analytics": "analytics",
            "distribution": "distribution"
        }
        
        manager_key = type_mapping.get(notification_type)
        return self.managers.get(manager_key)

    async def _prepare_notification(
        self,
        notification_type: str,
        user_id: str,
        data: Dict[str, Any],
        channels: List[str],
        priority: int
    ) -> Dict[str, Any]:
        """Prépare une notification pour envoi"""
        # Structure commune pour tous les types
        prepared = {
            "id": f"notif_{datetime.now().timestamp()}",
            "type": notification_type,
            "user_id": user_id,
            "priority": priority,
            "channels": channels or ["email"],
            "created_at": datetime.now(),
            "data": data
        }
        
        # Enrichissement spécifique par type
        if notification_type == "protection":
            from .content_protection_alerts import ProtectionViolation
            # Conversion en objet ProtectionViolation si nécessaire
            prepared = ProtectionViolation(**data)
            
        elif notification_type == "revenue":
            from .revenue_notifications import RevenueTransaction
            # Conversion en objet RevenueTransaction si nécessaire
            prepared = RevenueTransaction(**data)
        
        return prepared

    async def _update_metrics(self, notification_type: str, status: str, delivery_time: float):
        """Met à jour les métriques système"""
        if status == "sent":
            self.metrics["total_sent"] += 1
            # Mise à jour moyenne temps de livraison
            current_avg = self.metrics["average_delivery_time"]
            total_count = self.metrics["total_sent"]
            self.metrics["average_delivery_time"] = (
                (current_avg * (total_count - 1) + delivery_time) / total_count
            )
        elif status == "failed":
            self.metrics["total_failed"] += 1
        
        # Mise à jour dans Redis pour persistance
        await self.config.redis_client.hmset(
            "notification_metrics",
            self.metrics
        )

    async def _get_queue_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques de la queue Redis"""
        try:
            queue_size = await self.config.redis_client.llen("notification_queue")
            processing_count = await self.config.redis_client.llen("notification_processing")
            failed_count = await self.config.redis_client.llen("notification_failed")
            
            return {
                "queue_size": queue_size,
                "processing_count": processing_count,
                "failed_count": failed_count,
                "total_pending": queue_size + processing_count
            }
        except Exception as e:
            return {"error": str(e)}

    async def _get_database_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques de performance base de données"""
        try:
            async with self.config.db_pool.acquire() as conn:
                # Métriques notifications récentes
                recent_stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_notifications,
                        COUNT(*) FILTER (WHERE status = 'sent') as sent_count,
                        COUNT(*) FILTER (WHERE status = 'failed') as failed_count,
                        AVG(EXTRACT(EPOCH FROM (sent_at - created_at))) as avg_processing_time
                    FROM notification_queue 
                    WHERE created_at >= NOW() - INTERVAL '1 hour'
                """)
                
                return dict(recent_stats) if recent_stats else {}
        except Exception as e:
            return {"error": str(e)}


# Instance globale de l'orchestrateur (singleton pattern)
_orchestrator_instance = None

async def get_notification_orchestrator(config: NotificationSystemConfig = None) -> EnterpriseNotificationOrchestrator:
    """Récupère l'instance singleton de l'orchestrateur"""
    global _orchestrator_instance
    
    if _orchestrator_instance is None:
        if config is None:
            raise ValueError("Configuration requise pour la première initialisation")
        _orchestrator_instance = EnterpriseNotificationOrchestrator(config)
        await _orchestrator_instance.initialize()
    
    return _orchestrator_instance

# Fonctions utilitaires d'export
async def create_database_schema(db_pool: asyncpg.Pool) -> bool:
    """Crée le schéma complet de la base de données"""
    try:
        schema_sql = create_notification_schema_sql()
        async with db_pool.acquire() as conn:
            await conn.execute(schema_sql)
        logger.info("Schéma de base de données créé avec succès")
        return True
    except Exception as e:
        logger.error(f"Erreur création schéma: {str(e)}")
        return False

# Export des classes et fonctions principales
__all__ = [
    "EnterpriseNotificationOrchestrator",
    "NotificationSystemConfig",
    "get_notification_orchestrator",
    "create_database_schema"
]
    PushNotification,
    PushDevice,
    PushPlatform,
    PushPriority,
    NotificationType
)

from .realtime_manager import (
    RealtimeCommunicationManager,
    RealtimeMessage,
    MessageType,
    UserPresence,
    UserStatus,
    Room
)

from .alert_manager import (
    AlertManager,
    Alert,
    AlertRule,
    AlertSeverity,
    AlertStatus,
    EscalationPolicy
)

from .queue_manager import (
    NotificationQueueManager,
    QueueMessage,
    QueuePriority,
    ProcessingStatus
)

from .schema import initialize_notification_database
from . import NotificationStatus, NotificationPriority, NotificationMetrics

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class NotificationSystemConfig:
    """Configuration complète du système de notifications"""
    
    # Configuration base de données
    database_url: str = ""
    redis_url: str = ""
    
    # Configuration email
    email_config: Dict[str, Any] = field(default_factory=dict)
    
    # Configuration push
    push_config: Dict[str, Any] = field(default_factory=dict)
    
    # Configuration temps réel
    realtime_config: Dict[str, Any] = field(default_factory=dict)
    
    # Configuration alertes
    alert_config: Dict[str, Any] = field(default_factory=dict)
    
    # Configuration files d'attente
    queue_config: Dict[str, Any] = field(default_factory=dict)
    
    # Configuration monitoring
    monitoring_enabled: bool = True
    metrics_retention_days: int = 30
    health_check_interval: int = 60
    
    # Configuration sécurité
    encryption_key: Optional[str] = None
    audit_logging: bool = True
    
    # Configuration performance
    max_concurrent_workers: int = 10
    batch_processing_size: int = 100
    rate_limiting_enabled: bool = True

class NotificationSystemOrchestrator:
    """
    Orchestrateur principal du système de notifications.
    
    Cette classe centralise la gestion de tous les composants de notifications :
    - Gestionnaire d'emails transactionnels
    - Gestionnaire de notifications push
    - Gestionnaire de communications temps réel
    - Gestionnaire d'alertes et escalades
    - Gestionnaire de files d'attente
    """
    
    def __init__(self, config: NotificationSystemConfig):
        self.config = config
        self.db_pool: Optional[asyncpg.Pool] = None
        self.redis_client: Optional[aioredis.Redis] = None
        
        # Gestionnaires de notifications
        self.email_manager: Optional[EnterpriseEmailManager] = None
        self.push_manager: Optional[PushNotificationManager] = None
        self.realtime_manager: Optional[RealtimeCommunicationManager] = None
        self.alert_manager: Optional[AlertManager] = None
        self.queue_manager: Optional[NotificationQueueManager] = None
        
        # État du système
        self.is_initialized = False
        self.is_running = False
        self.last_health_check = None
        self.system_metrics = NotificationMetrics()
        
        # Tâches de background
        self._background_tasks: List[asyncio.Task] = []
        
        logger.info("Notification System Orchestrator initialized")

    async def initialize(self) -> bool:
        """
        Initialise tous les composants du système de notifications.
        
        Returns:
            bool: True si l'initialisation est réussie
        """
        try:
            logger.info("Initializing Notification System...")
            
            # Initialiser les connexions base de données
            await self._initialize_database_connections()
            
            # Initialiser la base de données
            await self._initialize_database_schema()
            
            # Initialiser les gestionnaires
            await self._initialize_managers()
            
            # Démarrer les services de background
            await self._start_background_services()
            
            self.is_initialized = True
            self.is_running = True
            
            logger.info("✅ Notification System successfully initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Notification System: {str(e)}")
            await self.shutdown()
            return False

    async def send_notification(
        self,
        notification_type: str,
        recipient: str,
        content: Dict[str, Any],
        channel: Union[str, List[str]] = "auto",
        priority: NotificationPriority = NotificationPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Interface unifiée pour envoyer des notifications.
        
        Args:
            notification_type: Type de notification (welcome, alert, etc.)
            recipient: Destinataire (email, user_id, etc.)
            content: Contenu de la notification
            channel: Canal(aux) de notification ('email', 'push', 'realtime', 'auto')
            priority: Priorité de la notification
            metadata: Métadonnées additionnelles
            
        Returns:
            Dict[str, Any]: Résultat de l'envoi avec IDs des messages
        """
        try:
            if not self.is_initialized:
                raise RuntimeError("Notification system not initialized")
            
            metadata = metadata or {}
            results = {}
            
            # Déterminer les canaux automatiquement si nécessaire
            if channel == "auto":
                channels = await self._determine_notification_channels(
                    notification_type, recipient, priority
                )
            elif isinstance(channel, str):
                channels = [channel]
            else:
                channels = channel
            
            # Envoyer sur chaque canal
            for ch in channels:
                try:
                    if ch == "email" and self.email_manager:
                        result = await self._send_email_notification(
                            notification_type, recipient, content, priority, metadata
                        )
                        results["email"] = result
                        
                    elif ch == "push" and self.push_manager:
                        result = await self._send_push_notification(
                            notification_type, recipient, content, priority, metadata
                        )
                        results["push"] = result
                        
                    elif ch == "realtime" and self.realtime_manager:
                        result = await self._send_realtime_notification(
                            notification_type, recipient, content, priority, metadata
                        )
                        results["realtime"] = result
                        
                    elif ch == "alert" and self.alert_manager:
                        result = await self._send_alert_notification(
                            notification_type, recipient, content, priority, metadata
                        )
                        results["alert"] = result
                        
                except Exception as e:
                    logger.error(f"Failed to send {ch} notification: {str(e)}")
                    results[ch] = {"success": False, "error": str(e)}
            
            # Enregistrer dans les métriques
            await self._update_notification_metrics(notification_type, channels, results)
            
            return {
                "success": any(r.get("success", False) for r in results.values()),
                "results": results,
                "channels": channels,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def get_system_status(self) -> Dict[str, Any]:
        """Retourne le statut complet du système"""
        return {
            "is_initialized": self.is_initialized,
            "is_running": self.is_running,
            "last_health_check": self.last_health_check,
            "system_metrics": {
                "total_sent": self.system_metrics.total_sent,
                "delivered_count": self.system_metrics.delivered_count,
                "failed_count": self.system_metrics.failed_count,
                "delivery_rate": self.system_metrics.delivery_rate,
                "last_updated": self.system_metrics.last_updated.isoformat() if self.system_metrics.last_updated else None
            },
            "active_background_tasks": len(self._background_tasks),
            "config": {
                "monitoring_enabled": self.config.monitoring_enabled,
                "max_concurrent_workers": self.config.max_concurrent_workers,
                "rate_limiting_enabled": self.config.rate_limiting_enabled
            }
        }

    async def shutdown(self) -> None:
        """Arrête proprement le système de notifications"""
        try:
            logger.info("Shutting down Notification System...")
            
            self.is_running = False
            
            # Arrêter les tâches de background
            for task in self._background_tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            # Fermer les connexions
            if self.redis_client:
                await self.redis_client.close()
            
            if self.db_pool:
                await self.db_pool.close()
            
            logger.info("✅ Notification System shut down successfully")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {str(e)}")

# Instance globale pour utilisation simplifiée
_global_orchestrator: Optional[NotificationSystemOrchestrator] = None

async def initialize_notification_system(config: NotificationSystemConfig) -> NotificationSystemOrchestrator:
    """
    Initialise le système global de notifications.
    
    Args:
        config: Configuration du système
        
    Returns:
        NotificationSystemOrchestrator: Instance initialisée
    """
    global _global_orchestrator
    
    _global_orchestrator = NotificationSystemOrchestrator(config)
    
    success = await _global_orchestrator.initialize()
    if not success:
        raise RuntimeError("Failed to initialize notification system")
    
    return _global_orchestrator

async def get_notification_system() -> Optional[NotificationSystemOrchestrator]:
    """Retourne l'instance globale du système de notifications"""
    return _global_orchestrator

async def send_notification(
    notification_type: str,
    recipient: str,
    content: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    """
    Interface simplifiée pour envoyer des notifications.
    
    Args:
        notification_type: Type de notification
        recipient: Destinataire
        content: Contenu de la notification
        **kwargs: Arguments additionnels
        
    Returns:
        Dict[str, Any]: Résultat de l'envoi
    """
    if _global_orchestrator is None:
        raise RuntimeError("Notification system not initialized")
    
    return await _global_orchestrator.send_notification(
        notification_type, recipient, content, **kwargs
    )

# Fonctions utilitaires pour les types de notifications courantes

async def send_welcome_notification(user_email: str, user_name: str, account_type: str = "creator") -> Dict[str, Any]:
    """Envoie une notification de bienvenue"""
    return await send_notification(
        "welcome",
        user_email,
        {
            "user_name": user_name,
            "account_type": account_type,
            "subject": f"Bienvenue {user_name} sur IA Influencer Agent !",
            "title": "Bienvenue !",
            "body": f"Bonjour {user_name}, votre compte {account_type} a été créé avec succès."
        },
        channel=["email", "push"],
        priority=NotificationPriority.HIGH
    )

async def send_content_protection_alert(
    user_email: str,
    content_title: str,
    platform: str,
    recommended_action: str
) -> Dict[str, Any]:
    """Envoie une alerte de protection de contenu"""
    return await send_notification(
        "protection_alert",
        user_email,
        {
            "content_title": content_title,
            "platform": platform,
            "recommended_action": recommended_action,
            "subject": "🚨 Alerte de Protection de Contenu",
            "title": "Violation Détectée",
            "body": f"Utilisation non autorisée de '{content_title}' détectée sur {platform}"
        },
        channel=["email", "push", "alert"],
        priority=NotificationPriority.CRITICAL
    )

# Export des composants principaux
__all__ = [
    # Configuration et orchestration
    "NotificationSystemConfig",
    "NotificationSystemOrchestrator",
    
    # Gestionnaires de notifications
    "EnterpriseEmailManager",
    "PushNotificationManager", 
    "RealtimeCommunicationManager",
    "AlertManager",
    "NotificationQueueManager",
    
    # Types de données
    "EmailMessage",
    "PushNotification",
    "RealtimeMessage",
    "Alert",
    "QueueMessage",
    
    # Fonctions utilitaires
    "initialize_notification_system",
    "get_notification_system",
    "send_notification",
    "send_welcome_notification",
    "send_content_protection_alert",
    
    # Initialisation base de données
    "initialize_notification_database"
]

logger.info("Notification Systems Index module loaded successfully")
logger.info("© 2025 Fahed Mlaiel - mlaiel@live.de - Tous droits réservés")
