"""
IA-Influencer-Agent - Events Module Index
Module: backend/core/events/index.py
Architecture: Central Access Point for Event Management System
Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT STRICT ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
INTERDIT : Copie, reproduction, modification, ou usage sans autorisation écrite explicite.
Toute violation sera poursuivie selon la loi allemande et française.
Contact autorisations : mlaiel@live.de

Description:
    Point d'accès central pour le système de gestion d'événements de la plateforme
    IA-Influencer-Agent. Facilite l'initialisation et la configuration de tous
    les composants d'événements.
"""

from typing import Any, Dict, List, Optional, Union
import asyncio
import logging
from datetime import timedelta

# Import de tous les composants
from . import (
    # Core components
    EventBus, EventStore, EventPublisher, EventDispatcher, EventAggregator,
    EventScheduler, notification_service,
    
    # Event types
    EventType, ContentEvent, ProtectionEvent, MonetizationEvent,
    CollaborationEvent, SystemEvent,
    
    # Advanced features
    EventMetricsManager, event_metrics_manager,
    WorkflowEngine, initialize_workflow_engine,
    EventReplicationManager, initialize_replication_manager,
    EventResilienceManager, initialize_resilience_manager,
    
    # Configuration classes
    CircuitBreakerConfig, BulkheadConfig, RetryConfig, TimeoutConfig,
    ReplicationTarget, ReplicationStrategy
)

logger = logging.getLogger(__name__)


class EventSystemManager:
    """
    Gestionnaire centralisé du système d'événements IA-Influencer-Agent
    """
    
    def __init__(self):
        self._initialized = False
        self._config: Dict[str, Any] = {}
        
        # Composants principaux
        self.event_bus: Optional[EventBus] = None
        self.event_store: Optional[EventStore] = None
        self.event_publisher: Optional[EventPublisher] = None
        self.event_dispatcher: Optional[EventDispatcher] = None
        self.event_aggregator: Optional[EventAggregator] = None
        self.event_scheduler: Optional[EventScheduler] = None
        
        # Composants avancés
        self.metrics_manager: Optional[EventMetricsManager] = None
        self.workflow_engine: Optional[WorkflowEngine] = None
        self.replication_manager: Optional[EventReplicationManager] = None
        self.resilience_manager: Optional[EventResilienceManager] = None
        
        logger.info("EventSystemManager created")
    
    async def initialize(self, config: Dict[str, Any]):
        """
        Initialise complètement le système d'événements
        
        Args:
            config: Configuration complète du système
        """
        if self._initialized:
            logger.warning("EventSystemManager already initialized")
            return
        
        self._config = config
        logger.info("Initializing EventSystemManager with configuration")
        
        try:
            # 1. Initialisation du bus d'événements central
            await self._initialize_event_bus(config.get("event_bus", {}))
            
            # 2. Initialisation du stockage d'événements
            await self._initialize_event_store(config.get("event_store", {}))
            
            # 3. Initialisation du système de publication
            await self._initialize_event_publisher(config.get("event_publisher", {}))
            
            # 4. Initialisation du dispatcher
            await self._initialize_event_dispatcher(config.get("event_dispatcher", {}))
            
            # 5. Initialisation de l'agrégateur
            await self._initialize_event_aggregator(config.get("event_aggregator", {}))
            
            # 6. Initialisation du scheduler
            await self._initialize_event_scheduler(config.get("event_scheduler", {}))
            
            # 7. Initialisation des métriques
            await self._initialize_metrics_manager(config.get("metrics", {}))
            
            # 8. Initialisation des workflows
            await self._initialize_workflow_engine(config.get("workflows", {}))
            
            # 9. Initialisation de la réplication
            await self._initialize_replication_manager(config.get("replication", {}))
            
            # 10. Initialisation de la résilience
            await self._initialize_resilience_manager(config.get("resilience", {}))
            
            # 11. Initialisation des notifications
            await self._initialize_notification_service(config.get("notifications", {}))
            
            # 12. Configuration des workflows prédéfinis
            await self._setup_predefined_workflows()
            
            # 13. Configuration des métriques et alertes par défaut
            await self._setup_default_monitoring()
            
            self._initialized = True
            logger.info("EventSystemManager successfully initialized")
            
        except Exception as e:
            logger.error("Failed to initialize EventSystemManager: %s", e)
            raise
    
    async def _initialize_event_bus(self, config: Dict[str, Any]):
        """Initialise le bus d'événements"""
        self.event_bus = EventBus(
            name=config.get("name", "main"),
            max_workers=config.get("max_workers", 20),
            enable_persistence=config.get("enable_persistence", True),
            enable_metrics=config.get("enable_metrics", True)
        )
        await self.event_bus.start()
        logger.info("EventBus initialized")
    
    async def _initialize_event_store(self, config: Dict[str, Any]):
        """Initialise le stockage d'événements"""
        if config.get("enabled", True):
            self.event_store = EventStore(
                storage_backend=config.get("backend", "postgresql"),
                connection_config=config.get("connection", {}),
                retention_days=config.get("retention_days", 365),
                enable_compression=config.get("enable_compression", True)
            )
            await self.event_store.initialize()
            logger.info("EventStore initialized")
    
    async def _initialize_event_publisher(self, config: Dict[str, Any]):
        """Initialise le système de publication"""
        self.event_publisher = EventPublisher(
            redis_client=config.get("redis_client"),
            enable_persistence=config.get("enable_persistence", True)
        )
        await self.event_publisher.start()
        logger.info("EventPublisher initialized")
    
    async def _initialize_event_dispatcher(self, config: Dict[str, Any]):
        """Initialise le dispatcher"""
        self.event_dispatcher = EventDispatcher(
            event_bus=self.event_bus,
            max_workers=config.get("max_workers", 10),
            enable_metrics=config.get("enable_metrics", True)
        )
        await self.event_dispatcher.start()
        logger.info("EventDispatcher initialized")
    
    async def _initialize_event_aggregator(self, config: Dict[str, Any]):
        """Initialise l'agrégateur"""
        self.event_aggregator = EventAggregator(
            event_bus=self.event_bus,
            aggregation_window=timedelta(seconds=config.get("window_seconds", 60)),
            max_batch_size=config.get("max_batch_size", 100)
        )
        await self.event_aggregator.start()
        logger.info("EventAggregator initialized")
    
    async def _initialize_event_scheduler(self, config: Dict[str, Any]):
        """Initialise le scheduler"""
        self.event_scheduler = EventScheduler(
            event_bus=self.event_bus,
            persistence_backend=config.get("persistence_backend", "redis"),
            check_interval=config.get("check_interval", 30)
        )
        await self.event_scheduler.start()
        logger.info("EventScheduler initialized")
    
    async def _initialize_metrics_manager(self, config: Dict[str, Any]):
        """Initialise le gestionnaire de métriques"""
        if config.get("enabled", True):
            self.metrics_manager = event_metrics_manager
            await self.metrics_manager.start()
            logger.info("EventMetricsManager initialized")
    
    async def _initialize_workflow_engine(self, config: Dict[str, Any]):
        """Initialise le moteur de workflows"""
        if config.get("enabled", True):
            self.workflow_engine = initialize_workflow_engine(self.event_bus)
            logger.info("WorkflowEngine initialized")
    
    async def _initialize_replication_manager(self, config: Dict[str, Any]):
        """Initialise le gestionnaire de réplication"""
        if config.get("enabled", False):
            self.replication_manager = initialize_replication_manager(
                self.event_bus,
                self.event_store,
                config.get("redis_client")
            )
            
            # Configuration des cibles de réplication
            for target_config in config.get("targets", []):
                target = ReplicationTarget(
                    target_id=target_config["target_id"],
                    name=target_config["name"],
                    type=target_config["type"],
                    connection_config=target_config["connection_config"],
                    replication_strategy=ReplicationStrategy(target_config.get("strategy", "asynchronous")),
                    enabled=target_config.get("enabled", True),
                    filters=target_config.get("filters", {})
                )
                self.replication_manager.add_target(target)
            
            await self.replication_manager.start()
            logger.info("EventReplicationManager initialized with %d targets", 
                       len(config.get("targets", [])))
    
    async def _initialize_resilience_manager(self, config: Dict[str, Any]):
        """Initialise le gestionnaire de résilience"""
        if config.get("enabled", True):
            self.resilience_manager = initialize_resilience_manager(self.event_bus)
            
            # Configuration personnalisée si fournie
            for cb_config in config.get("circuit_breakers", []):
                self.resilience_manager.create_circuit_breaker(
                    cb_config["name"],
                    CircuitBreakerConfig(**cb_config.get("config", {}))
                )
            
            for bh_config in config.get("bulkheads", []):
                self.resilience_manager.create_bulkhead(
                    bh_config["name"],
                    BulkheadConfig(**bh_config.get("config", {}))
                )
            
            logger.info("EventResilienceManager initialized")
    
    async def _initialize_notification_service(self, config: Dict[str, Any]):
        """Initialise le service de notifications"""
        if config.get("enabled", True):
            await notification_service.initialize(config)
            logger.info("NotificationService initialized")
    
    async def _setup_predefined_workflows(self):
        """Configure les workflows prédéfinis pour IA-Influencer-Agent"""
        if not self.workflow_engine:
            return
        
        # Les workflows sont déjà enregistrés lors de l'initialisation
        # Ici on peut ajouter des configurations supplémentaires
        
        logger.info("Predefined workflows configured")
    
    async def _setup_default_monitoring(self):
        """Configure le monitoring par défaut"""
        if not self.metrics_manager:
            return
        
        # Les alertes par défaut sont déjà configurées
        # Ici on peut ajouter des callbacks personnalisés
        
        def alert_callback(alert):
            logger.critical("ALERT: %s - %s", alert.severity.value, alert.message)
            # Ici on pourrait envoyer vers d'autres systèmes (PagerDuty, Slack, etc.)
        
        self.metrics_manager.add_alert_callback(alert_callback)
        logger.info("Default monitoring configured")
    
    async def start_all(self):
        """Démarre tous les composants"""
        if not self._initialized:
            raise RuntimeError("EventSystemManager not initialized")
        
        # Les composants sont déjà démarrés lors de l'initialisation
        logger.info("All event system components started")
    
    async def stop_all(self):
        """Arrête tous les composants"""
        logger.info("Stopping all event system components")
        
        # Arrêt dans l'ordre inverse de l'initialisation
        if self.replication_manager:
            await self.replication_manager.stop()
        
        if self.metrics_manager:
            await self.metrics_manager.stop()
        
        if self.event_scheduler:
            await self.event_scheduler.stop()
        
        if self.event_aggregator:
            await self.event_aggregator.stop()
        
        if self.event_dispatcher:
            await self.event_dispatcher.stop()
        
        if self.event_publisher:
            await self.event_publisher.stop()
        
        if self.event_bus:
            await self.event_bus.stop()
        
        logger.info("All event system components stopped")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Retourne le statut de santé global"""
        status = {
            "initialized": self._initialized,
            "components": {}
        }
        
        if self.event_bus:
            status["components"]["event_bus"] = self.event_bus.get_stats()
        
        if self.metrics_manager:
            status["components"]["metrics"] = self.metrics_manager.get_current_metrics()
        
        if self.workflow_engine:
            status["components"]["workflows"] = self.workflow_engine.get_stats()
        
        if self.replication_manager:
            status["components"]["replication"] = self.replication_manager.get_replication_status()
        
        if self.resilience_manager:
            status["components"]["resilience"] = self.resilience_manager.get_health_status()
        
        return status
    
    def get_configuration(self) -> Dict[str, Any]:
        """Retourne la configuration actuelle"""
        return self._config.copy()


# Instance globale du gestionnaire
event_system_manager = EventSystemManager()


# Configuration par défaut pour IA-Influencer-Agent
DEFAULT_EVENT_SYSTEM_CONFIG = {
    "event_bus": {
        "name": "ia_influencer_main",
        "max_workers": 20,
        "enable_persistence": True,
        "enable_metrics": True
    },
    "event_store": {
        "enabled": True,
        "backend": "postgresql",
        "retention_days": 365,
        "enable_compression": True
    },
    "event_publisher": {
        "enable_persistence": True
    },
    "event_dispatcher": {
        "max_workers": 15,
        "enable_metrics": True
    },
    "event_aggregator": {
        "window_seconds": 60,
        "max_batch_size": 100
    },
    "event_scheduler": {
        "persistence_backend": "redis",
        "check_interval": 30
    },
    "metrics": {
        "enabled": True,
        "collection_interval": 60,
        "retention_days": 30
    },
    "workflows": {
        "enabled": True
    },
    "replication": {
        "enabled": False,  # À activer selon les besoins
        "targets": []
    },
    "resilience": {
        "enabled": True,
        "circuit_breakers": [
            {
                "name": "content_processing_advanced",
                "config": {
                    "failure_threshold": 5,
                    "timeout": 30
                }
            }
        ],
        "bulkheads": [
            {
                "name": "fingerprinting_advanced", 
                "config": {
                    "max_concurrent_calls": 100,
                    "queue_capacity": 1000
                }
            }
        ]
    },
    "notifications": {
        "enabled": True,
        "email": {
            "smtp_host": "localhost",
            "smtp_port": 587,
            "from_email": "noreply@ia-influencer-agent.com"
        },
        "websocket": {
            "port": 8765,
            "host": "0.0.0.0"
        }
    }
}


async def initialize_event_system(config: Optional[Dict[str, Any]] = None) -> EventSystemManager:
    """
    Fonction d'initialisation rapide du système d'événements
    
    Args:
        config: Configuration personnalisée (utilise la config par défaut si None)
        
    Returns:
        Instance configurée du gestionnaire
    """
    config = config or DEFAULT_EVENT_SYSTEM_CONFIG
    await event_system_manager.initialize(config)
    return event_system_manager


# Helper functions pour usage courant
async def publish_content_event(
    content_id: str,
    content_type: str,
    action: str,
    user_id: str,
    tenant_id: str,
    **kwargs
) -> bool:
    """Publie un événement de contenu"""
    if not event_system_manager.event_bus:
        raise RuntimeError("Event system not initialized")
    
    event = ContentEvent.create_uploaded(
        content_id=content_id,
        content_type=content_type,
        file_size=kwargs.get("file_size", 0),
        format=kwargs.get("format", ""),
        user_id=user_id,
        tenant_id=tenant_id,
        **kwargs
    )
    
    return await event_system_manager.event_bus.publish(event)


async def publish_protection_event(
    content_id: str,
    violation_url: str,
    similarity_score: float,
    platform: str,
    user_id: str,
    tenant_id: str
) -> bool:
    """Publie un événement de protection"""
    if not event_system_manager.event_bus:
        raise RuntimeError("Event system not initialized")
    
    event = ProtectionEvent.create_violation_detected(
        content_id=content_id,
        violation_url=violation_url,
        similarity_score=similarity_score,
        platform=platform,
        user_id=user_id,
        tenant_id=tenant_id
    )
    
    return await event_system_manager.event_bus.publish(event)


async def publish_monetization_event(
    content_id: str,
    revenue_amount: float,
    currency: str,
    platform: str,
    user_id: str,
    tenant_id: str
) -> bool:
    """Publie un événement de monétisation"""
    if not event_system_manager.event_bus:
        raise RuntimeError("Event system not initialized")
    
    event = MonetizationEvent.create_revenue_detected(
        content_id=content_id,
        revenue_amount=revenue_amount,
        currency=currency,
        platform=platform,
        user_id=user_id,
        tenant_id=tenant_id
    )
    
    return await event_system_manager.event_bus.publish(event)


# Export des fonctions utilitaires
__all__ = [
    "EventSystemManager",
    "event_system_manager",
    "DEFAULT_EVENT_SYSTEM_CONFIG",
    "initialize_event_system",
    "publish_content_event",
    "publish_protection_event", 
    "publish_monetization_event"
]
