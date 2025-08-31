"""IA Influencer Agent - Module d'Observabilité Index
=================================================

Point d'entrée principal et gestionnaire centralisé pour l'infrastructure d'observabilité
de niveau entreprise de la plateforme IA Influencer Agent.

Auteur: Fahed Mlaiel (mlaiel@live.de)
Copyright © 2025 Fahed Mlaiel. Tous droits réservés.

🚨 PROPRIÉTÉ INTELLECTUELLE PROTÉGÉE 🚨
Ce code est la propriété exclusive de Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from contextlib import asynccontextmanager

from .metrics import MetricsCollector, ContentMetricsCollector, AIMetricsCollector
from .tracing import TracingManager, DistributedTracer, RequestTracer
from .alerting import AlertManager, AlertRule, AlertSeverity, NotificationChannel
from .monitoring import SystemMonitor, PerformanceMonitor, ResourceMonitor
from .sla import SLAMonitor, ServiceLevelTracker, AvailabilityCalculator
from .logging import StructuredLogger, AuditLogger, SecurityLogger
from .dashboards import DashboardManager, MetricsDashboard, HealthDashboard, AlertDashboard
from .health import HealthChecker, ServiceHealthMonitor, DatabaseHealthChecker


@dataclass
class ObservabilityConfig:
    """Configuration centralisée pour le module d'observabilité."""    
    service_name: str = "ia-influencer-agent"
    environment: str = "production"
    
    # Configuration des métriques
    metrics_retention_hours: int = 24
    prometheus_port: int = 8090
    enable_business_metrics: bool = True
    
    # Configuration du tracing
    tracing_sample_rate: float = 0.1
    jaeger_endpoint: Optional[str] = None
    enable_request_tracing: bool = True
    
    # Configuration des alertes
    alert_evaluation_interval: int = 60  # secondes
    notification_channels: List[NotificationChannel] = field(
        default_factory=lambda: [NotificationChannel.EMAIL, NotificationChannel.SLACK]
    )
    
    # Configuration SLA
    default_sla_targets: Dict[str, float] = field(default_factory=lambda: {
        "content_upload_success_rate": 0.999,  # 99.9%
        "ai_processing_success_rate": 0.995,   # 99.5%
        "content_protection_accuracy": 0.98,   # 98%
        "api_response_time_p95": 2000,         # 2s
        "system_availability": 0.999           # 99.9%
    })
    
    # Configuration de surveillance
    monitoring_interval: int = 30  # secondes
    health_check_timeout: int = 10  # secondes
    
    # Configuration logging
    log_level: str = "INFO"
    enable_audit_logging: bool = True
    enable_security_logging: bool = True
    
    # Configuration dashboards
    dashboard_refresh_rate: int = 5  # secondes
    enable_realtime_dashboards: bool = True


class ObservabilityIndex:
    """    Gestionnaire centralisé de l'infrastructure d'observabilité.
    
    Coordonne tous les composants d'observabilité et fournit une interface
    unifiée pour la surveillance, les métriques, le tracing et les alertes.
    """    
    def __init__(self, config: Optional[ObservabilityConfig] = None):
        """Initialise l'index d'observabilité."""        self.config = config or ObservabilityConfig()
        self.logger = logging.getLogger(__name__)
        
        # État du système
        self._initialized = False
        self._running = False
        self._startup_time = None
        
        # Composants principaux
        self._metrics_collector: Optional[MetricsCollector] = None
        self._content_metrics: Optional[ContentMetricsCollector] = None
        self._ai_metrics: Optional[AIMetricsCollector] = None
        self._tracing_manager: Optional[TracingManager] = None
        self._distributed_tracer: Optional[DistributedTracer] = None
        self._request_tracer: Optional[RequestTracer] = None
        self._alert_manager: Optional[AlertManager] = None
        self._system_monitor: Optional[SystemMonitor] = None
        self._performance_monitor: Optional[PerformanceMonitor] = None
        self._resource_monitor: Optional[ResourceMonitor] = None
        self._sla_monitor: Optional[SLAMonitor] = None
        self._service_tracker: Optional[ServiceLevelTracker] = None
        self._availability_calculator: Optional[AvailabilityCalculator] = None
        self._structured_logger: Optional[StructuredLogger] = None
        self._audit_logger: Optional[AuditLogger] = None
        self._security_logger: Optional[SecurityLogger] = None
        self._dashboard_manager: Optional[DashboardManager] = None
        self._health_checker: Optional[HealthChecker] = None
        self._service_health_monitor: Optional[ServiceHealthMonitor] = None
        self._db_health_checker: Optional[DatabaseHealthChecker] = None
        
        # Tâches de surveillance
        self._monitoring_tasks: List[asyncio.Task] = []
        
    async def initialize(self) -> None:
        """Initialise tous les composants d'observabilité."""        if self._initialized:
            return
            
        self.logger.info(f"Initialisation du module d'observabilité pour {self.config.service_name}")
        self._startup_time = datetime.utcnow()
        
        try:
            # Initialiser les composants de métriques
            await self._initialize_metrics()
            
            # Initialiser le tracing
            await self._initialize_tracing()
            
            # Initialiser les alertes
            await self._initialize_alerting()
            
            # Initialiser la surveillance
            await self._initialize_monitoring()
            
            # Initialiser SLA
            await self._initialize_sla()
            
            # Initialiser le logging
            await self._initialize_logging()
            
            # Initialiser les dashboards
            await self._initialize_dashboards()
            
            # Initialiser les vérifications de santé
            await self._initialize_health_checks()
            
            self._initialized = True
            self.logger.info("Module d'observabilité initialisé avec succès")
            
            # Enregistrer l'événement de démarrage
            if self._audit_logger:
                await self._audit_logger.log_system_event(
                    "observability_initialized",
                    {"service_name": self.config.service_name, "startup_time": self._startup_time.isoformat()}
                )
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation de l'observabilité: {e}")
            raise
            
    async def _initialize_metrics(self) -> None:
        """Initialise les collecteurs de métriques."""        self._metrics_collector = MetricsCollector(
            service_name=self.config.service_name,
            retention_hours=self.config.metrics_retention_hours
        )
        
        if self.config.enable_business_metrics:
            self._content_metrics = ContentMetricsCollector(self._metrics_collector)
            self._ai_metrics = AIMetricsCollector(self._metrics_collector)
            
        # Démarrer l'export Prometheus si configuré
        if self.config.prometheus_port:
            await self._metrics_collector.start_prometheus_server(self.config.prometheus_port)
            
    async def _initialize_tracing(self) -> None:
        """Initialise les composants de tracing."""        self._tracing_manager = TracingManager(
            service_name=self.config.service_name,
            sample_rate=self.config.tracing_sample_rate
        )
        
        if self.config.jaeger_endpoint:
            self._tracing_manager.configure_jaeger_export(self.config.jaeger_endpoint)
            
        self._distributed_tracer = DistributedTracer(self._tracing_manager)
        
        if self.config.enable_request_tracing:
            self._request_tracer = RequestTracer(self._tracing_manager)
            
    async def _initialize_alerting(self) -> None:
        """Initialise le système d'alertes."""        self._alert_manager = AlertManager(
            evaluation_interval=self.config.alert_evaluation_interval,
            default_channels=self.config.notification_channels
        )
        
        # Configurer les règles d'alerte par défaut
        await self._configure_default_alerts()
        
    async def _initialize_monitoring(self) -> None:
        """Initialise les composants de surveillance."""        self._system_monitor = SystemMonitor(
            monitoring_interval=self.config.monitoring_interval
        )
        self._performance_monitor = PerformanceMonitor()
        self._resource_monitor = ResourceMonitor()
        
    async def _initialize_sla(self) -> None:
        """Initialise le monitoring SLA."""        self._sla_monitor = SLAMonitor(self.config.default_sla_targets)
        self._service_tracker = ServiceLevelTracker()
        self._availability_calculator = AvailabilityCalculator()
        
    async def _initialize_logging(self) -> None:
        """Initialise les systèmes de logging."""        self._structured_logger = StructuredLogger(
            service_name=self.config.service_name,
            log_level=self.config.log_level
        )
        
        if self.config.enable_audit_logging:
            self._audit_logger = AuditLogger(self._structured_logger)
            
        if self.config.enable_security_logging:
            self._security_logger = SecurityLogger(self._structured_logger)
            
    async def _initialize_dashboards(self) -> None:
        """Initialise les tableaux de bord."""        if not self.config.enable_realtime_dashboards:
            return
            
        self._dashboard_manager = DashboardManager(
            refresh_rate=self.config.dashboard_refresh_rate
        )
        
        # Créer les dashboards par défaut
        metrics_dashboard = MetricsDashboard(self._metrics_collector)
        health_dashboard = HealthDashboard(self._health_checker)
        alert_dashboard = AlertDashboard(self._alert_manager)
        
        await self._dashboard_manager.register_dashboard("metrics", metrics_dashboard)
        await self._dashboard_manager.register_dashboard("health", health_dashboard)
        await self._dashboard_manager.register_dashboard("alerts", alert_dashboard)
        
    async def _initialize_health_checks(self) -> None:
        """Initialise les vérifications de santé."""        self._health_checker = HealthChecker(timeout=self.config.health_check_timeout)
        self._service_health_monitor = ServiceHealthMonitor(self._health_checker)
        self._db_health_checker = DatabaseHealthChecker()
        
    async def _configure_default_alerts(self) -> None:
        """Configure les règles d'alerte par défaut."""        if not self._alert_manager:
            return
            
        # Alerte taux d'échec upload de contenu élevé
        await self._alert_manager.register_rule(AlertRule(
            name="content_upload_failure_rate_high",
            condition=lambda data: data.get("metrics", {}).get("content.upload.failure_rate", 0) > 0.05,
            severity=AlertSeverity.CRITICAL,
            description="Taux d'échec d'upload de contenu > 5%",
            notification_channels=self.config.notification_channels
        ))
        
        # Alerte performance IA dégradée
        await self._alert_manager.register_rule(AlertRule(
            name="ai_processing_performance_degraded",
            condition=lambda data: data.get("metrics", {}).get("ai.processing.avg_time_ms", 0) > 30000,
            severity=AlertSeverity.WARNING,
            description="Temps de traitement IA > 30s",
            notification_channels=[NotificationChannel.SLACK]
        ))
        
        # Alerte utilisation CPU élevée
        await self._alert_manager.register_rule(AlertRule(
            name="system_cpu_usage_high",
            condition=lambda data: data.get("system", {}).get("cpu_percent", 0) > 80,
            severity=AlertSeverity.WARNING,
            description="Utilisation CPU > 80%",
            notification_channels=[NotificationChannel.EMAIL]
        ))
        
        # Alerte utilisation mémoire critique
        await self._alert_manager.register_rule(AlertRule(
            name="system_memory_usage_critical",
            condition=lambda data: data.get("system", {}).get("memory_percent", 0) > 90,
            severity=AlertSeverity.CRITICAL,
            description="Utilisation mémoire > 90%",
            notification_channels=self.config.notification_channels
        ))
        
    async def start(self) -> None:
        """Démarre tous les composants d'observabilité."""        if not self._initialized:
            await self.initialize()
            
        if self._running:
            return
            
        self.logger.info("Démarrage du système d'observabilité")
        
        try:
            # Démarrer la surveillance système
            if self._system_monitor:
                monitoring_task = asyncio.create_task(self._system_monitor.start_monitoring())
                self._monitoring_tasks.append(monitoring_task)
                
            # Démarrer l'évaluation des alertes
            if self._alert_manager:
                alert_task = asyncio.create_task(self._alert_manager.start_evaluation())
                self._monitoring_tasks.append(alert_task)
                
            # Démarrer le monitoring SLA
            if self._sla_monitor:
                sla_task = asyncio.create_task(self._sla_monitor.start_monitoring())
                self._monitoring_tasks.append(sla_task)
                
            # Démarrer les dashboards
            if self._dashboard_manager:
                dashboard_task = asyncio.create_task(self._dashboard_manager.start())
                self._monitoring_tasks.append(dashboard_task)
                
            # Démarrer la surveillance de santé
            if self._service_health_monitor:
                health_task = asyncio.create_task(self._service_health_monitor.start_monitoring())
                self._monitoring_tasks.append(health_task)
                
            self._running = True
            self.logger.info("Système d'observabilité démarré avec succès")
            
            # Enregistrer l'événement de démarrage
            if self._audit_logger:
                await self._audit_logger.log_system_event(
                    "observability_started",
                    {"active_tasks": len(self._monitoring_tasks)}
                )
                
        except Exception as e:
            self.logger.error(f"Erreur lors du démarrage de l'observabilité: {e}")
            await self.stop()
            raise
            
    async def stop(self) -> None:
        """Arrête tous les composants d'observabilité."""        if not self._running:
            return
            
        self.logger.info("Arrêt du système d'observabilité")
        
        # Arrêter toutes les tâches de surveillance
        for task in self._monitoring_tasks:
            if not task.done():
                task.cancel()
                
        # Attendre l'arrêt des tâches
        if self._monitoring_tasks:
            await asyncio.gather(*self._monitoring_tasks, return_exceptions=True)
            
        self._monitoring_tasks.clear()
        self._running = False
        
        # Enregistrer l'événement d'arrêt
        if self._audit_logger:
            await self._audit_logger.log_system_event("observability_stopped", {})
            
        self.logger.info("Système d'observabilité arrêté")
        
    async def get_status(self) -> Dict[str, Any]:
        """Retourne l'état complet du système d'observabilité."""        return {
            "initialized": self._initialized,
            "running": self._running,
            "startup_time": self._startup_time.isoformat() if self._startup_time else None,
            "uptime_seconds": (datetime.utcnow() - self._startup_time).total_seconds() if self._startup_time else 0,
            "config": {
                "service_name": self.config.service_name,
                "environment": self.config.environment,
                "metrics_enabled": self._metrics_collector is not None,
                "tracing_enabled": self._tracing_manager is not None,
                "alerting_enabled": self._alert_manager is not None,
                "monitoring_enabled": self._system_monitor is not None,
                "sla_enabled": self._sla_monitor is not None,
                "dashboards_enabled": self._dashboard_manager is not None,
                "health_checks_enabled": self._health_checker is not None
            },
            "active_tasks": len(self._monitoring_tasks),
            "components": {
                "metrics_collector": "active" if self._metrics_collector else "inactive",
                "tracing_manager": "active" if self._tracing_manager else "inactive",
                "alert_manager": "active" if self._alert_manager else "inactive",
                "system_monitor": "active" if self._system_monitor else "inactive",
                "sla_monitor": "active" if self._sla_monitor else "inactive",
                "dashboard_manager": "active" if self._dashboard_manager else "inactive",
                "health_checker": "active" if self._health_checker else "inactive"
            }
        }
        
    # Propriétés d'accès aux composants
    @property
    def metrics(self) -> Optional[MetricsCollector]:
        """Accès au collecteur de métriques."""        return self._metrics_collector
        
    @property
    def content_metrics(self) -> Optional[ContentMetricsCollector]:
        """Accès aux métriques de contenu."""        return self._content_metrics
        
    @property
    def ai_metrics(self) -> Optional[AIMetricsCollector]:
        """Accès aux métriques IA."""        return self._ai_metrics
        
    @property
    def tracing(self) -> Optional[TracingManager]:
        """Accès au gestionnaire de tracing."""        return self._tracing_manager
        
    @property
    def distributed_tracer(self) -> Optional[DistributedTracer]:
        """Accès au traceur distribué."""        return self._distributed_tracer
        
    @property
    def request_tracer(self) -> Optional[RequestTracer]:
        """Accès au traceur de requêtes."""        return self._request_tracer
        
    @property
    def alerts(self) -> Optional[AlertManager]:
        """Accès au gestionnaire d'alertes."""        return self._alert_manager
        
    @property
    def monitoring(self) -> Optional[SystemMonitor]:
        """Accès au surveillant système."""        return self._system_monitor
        
    @property
    def sla(self) -> Optional[SLAMonitor]:
        """Accès au moniteur SLA."""        return self._sla_monitor
        
    @property
    def logger(self) -> Optional[StructuredLogger]:
        """Accès au logger structuré."""        return self._structured_logger
        
    @property
    def audit_logger(self) -> Optional[AuditLogger]:
        """Accès au logger d'audit."""        return self._audit_logger
        
    @property
    def security_logger(self) -> Optional[SecurityLogger]:
        """Accès au logger de sécurité."""        return self._security_logger
        
    @property
    def dashboards(self) -> Optional[DashboardManager]:
        """Accès au gestionnaire de dashboards."""        return self._dashboard_manager
        
    @property
    def health(self) -> Optional[HealthChecker]:
        """Accès au vérificateur de santé."""        return self._health_checker


# Instance globale par défaut
_default_observability_index: Optional[ObservabilityIndex] = None


def get_observability() -> ObservabilityIndex:
    """    Retourne l'instance globale du gestionnaire d'observabilité.
    
    Returns:
        ObservabilityIndex: Instance du gestionnaire d'observabilité
    """    global _default_observability_index
    
    if _default_observability_index is None:
        _default_observability_index = ObservabilityIndex()
        
    return _default_observability_index


def initialize_observability(config: Optional[ObservabilityConfig] = None) -> ObservabilityIndex:
    """    Initialise l'instance globale d'observabilité avec une configuration.
    
    Args:
        config: Configuration d'observabilité optionnelle
        
    Returns:
        ObservabilityIndex: Instance configurée du gestionnaire d'observabilité
    """    global _default_observability_index
    
    _default_observability_index = ObservabilityIndex(config)
    return _default_observability_index


@asynccontextmanager
async def observability_context(config: Optional[ObservabilityConfig] = None):
    """    Gestionnaire de contexte pour l'observabilité.
    
    Usage:
        async with observability_context() as obs:
            # Utiliser l'observabilité
            await obs.metrics.record_event("test", 1)
    """    obs = initialize_observability(config)
    
    try:
        await obs.start()
        yield obs
    finally:
        await obs.stop()


# Fonctions utilitaires d'accès rapide
async def record_metric(name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
    """Enregistre une métrique rapidement."""    obs = get_observability()
    if obs.metrics:
        obs.metrics.record_gauge(name, value, tags or {})


async def record_content_event(event_type: str, content_type: str, user_id: str, 
                             metadata: Optional[Dict[str, Any]] = None) -> None:
    """Enregistre un événement de contenu rapidement."""    obs = get_observability()
    if obs.content_metrics:
        await obs.content_metrics.record_content_event(event_type, content_type, user_id, metadata or {})


async def log_security_event(event_type: str, user_id: Optional[str] = None, 
                           details: Optional[Dict[str, Any]] = None) -> None:
    """Enregistre un événement de sécurité rapidement."""    obs = get_observability()
    if obs.security_logger:
        await obs.security_logger.log_security_event(event_type, user_id, details or {})


# Export des principales classes pour utilisation directe
__all__ = [
    'ObservabilityIndex',
    'ObservabilityConfig',
    'get_observability',
    'initialize_observability',
    'observability_context',
    'record_metric',
    'record_content_event',
    'log_security_event'
]
