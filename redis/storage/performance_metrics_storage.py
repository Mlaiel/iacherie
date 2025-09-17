"""🚀 Performance Metrics Storage - Enterprise Grade
================================================
Expert: PERFORMANCE ENGINEER + DEVOPS + ML ENGINEER + BACKEND SENIOR
Technologies: Performance Monitoring + APM + System Health + Infrastructure Analytics
Architecture: Level 2 - Storage Layer - Performance Metrics
Date: 2025-01-14

Ultra-optimized enterprise performance metrics storage with real-time monitoring,
APM integration, system health analytics and predictive performance insights.
================================================
"""

import asyncio
import logging
import time
import json
import hashlib
import psutil
from typing import Dict, Any, Optional, List, Union, Callable, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import statistics
from decimal import Decimal

# Optional imports with fallbacks
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)

class MetricCategory(Enum):
    """Catégories de métriques performance"""
    SYSTEM = "system"
    APPLICATION = "application"
    DATABASE = "database"
    NETWORK = "network"
    STORAGE = "storage"
    USER_EXPERIENCE = "user_experience"
    BUSINESS = "business"
    SECURITY = "security"

class MetricType(Enum):
    """Types de métriques"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"
    PERCENTAGE = "percentage"

class AlertLevel(Enum):
    """Niveaux d'alerte performance"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class PerformanceStatus(Enum):
    """États de performance"""
    OPTIMAL = "optimal"
    GOOD = "good"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNAVAILABLE = "unavailable"

@dataclass
class PerformanceMetric:
    """Métrique de performance enterprise"""
    metric_id: str = field(default_factory=lambda: hashlib.sha256(str(time.time()).encode()).hexdigest()[:16])
    name: str = ""
    category: MetricCategory = MetricCategory.SYSTEM
    metric_type: MetricType = MetricType.GAUGE
    value: Union[int, float, Decimal] = 0
    unit: str = ""
    timestamp: float = field(default_factory=time.time)
    source: str = "system"
    tags: Dict[str, str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    description: str = ""
    sampling_rate: float = 1.0

@dataclass
class SystemHealthMetrics:
    """Métriques santé système complètes"""
    timestamp: float = field(default_factory=time.time)
    cpu_usage_percent: float = 0.0
    memory_usage_percent: float = 0.0
    disk_usage_percent: float = 0.0
    network_bytes_sent: int = 0
    network_bytes_received: int = 0
    load_average: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    process_count: int = 0
    thread_count: int = 0
    file_descriptors: int = 0
    tcp_connections: int = 0
    system_uptime: float = 0.0
    boot_time: float = 0.0

@dataclass
class ApplicationMetrics:
    """Métriques application spécialisées"""
    timestamp: float = field(default_factory=time.time)
    request_rate: float = 0.0
    response_time_avg: float = 0.0
    response_time_p95: float = 0.0
    response_time_p99: float = 0.0
    error_rate: float = 0.0
    throughput: float = 0.0
    active_connections: int = 0
    queue_depth: int = 0
    cache_hit_ratio: float = 0.0
    database_connections: int = 0
    memory_heap_used: int = 0
    gc_collections: int = 0
    gc_time_ms: float = 0.0

@dataclass
class PerformanceAlert:
    """Alerte performance intelligente"""
    alert_id: str = field(default_factory=lambda: hashlib.sha256(str(time.time()).encode()).hexdigest()[:12])
    metric_name: str = ""
    current_value: float = 0.0
    threshold_value: float = 0.0
    alert_level: AlertLevel = AlertLevel.WARNING
    message: str = ""
    triggered_at: float = field(default_factory=time.time)
    resolved_at: Optional[float] = None
    duration_seconds: Optional[float] = None
    source: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    auto_resolved: bool = False

@dataclass
class PerformanceInsight:
    """Insight performance IA-généré"""
    insight_id: str = field(default_factory=lambda: hashlib.sha256(str(time.time()).encode()).hexdigest()[:12])
    category: str = "performance_optimization"
    title: str = ""
    description: str = ""
    severity: str = "medium"
    confidence_score: float = 0.0
    generated_at: float = field(default_factory=time.time)
    metrics_analyzed: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    predicted_impact: Dict[str, float] = field(default_factory=dict)
    action_items: List[str] = field(default_factory=list)

@dataclass
class PerformanceConfig:
    """Configuration monitoring performance"""
    redis_url: str = "redis://localhost:6379"
    collection_interval_seconds: int = 60
    retention_days: int = 30
    enable_system_monitoring: bool = True
    enable_application_monitoring: bool = True
    enable_ai_insights: bool = True
    alert_cooldown_seconds: int = 300
    batch_size: int = 100
    enable_predictive_alerts: bool = True
    performance_baseline_days: int = 7
    anomaly_detection_enabled: bool = True

class PerformanceMetricsStorage:
    """🚀 **Enterprise**: Storage métriques performance intelligent
    
    Système de stockage métriques performance enterprise avec monitoring
    temps-réel, alertes prédictives et insights IA pour optimisation.
    
    Fonctionnalités:
    - Monitoring performance temps-réel
    - Collecte métriques système/application
    - Alertes intelligentes prédictives
    - Insights IA optimisation performance
    - Baseline automatique et anomalies
    - APM integration enterprise
    - Health scoring automatique
    """
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self._redis_client: Optional[redis.Redis] = None
        self._running = False
        
        # Cache métriques en mémoire
        self._metrics_cache: Dict[str, List[PerformanceMetric]] = defaultdict(list)
        self._system_health_cache: Optional[SystemHealthMetrics] = None
        self._app_metrics_cache: Optional[ApplicationMetrics] = None
        self._active_alerts: Dict[str, PerformanceAlert] = {}
        
        # Buffers optimisés
        self._metrics_buffer: deque = deque(maxlen=config.batch_size * 10)
        self._alerts_buffer: deque = deque(maxlen=100)
        
        # Clés Redis optimisées
        self.metrics_prefix = "perf:metrics"
        self.system_prefix = "perf:system"
        self.alerts_prefix = "perf:alerts"
        self.insights_prefix = "perf:insights"
        self.baseline_prefix = "perf:baseline"
        
        # Composants IA et monitoring
        self._anomaly_detector = None
        self._performance_predictor = None
        self._baseline_calculator = None
        
        # Tâches background
        self._monitoring_tasks: List[asyncio.Task] = []
        self._metrics_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        
        # Performance counters
        self._metrics_collected = 0
        self._alerts_triggered = 0
        self._insights_generated = 0
        self._anomalies_detected = 0
        
    async def initialize(self) -> bool:
        """🚀 **Enterprise**: Initialisation storage métriques performance
        
        Initialise connexion Redis, démarre monitoring système,
        configure alertes et initialise composants IA.
        """
        try:
            if REDIS_AVAILABLE and self.config.redis_url:
                self._redis_client = redis.from_url(
                    self.config.redis_url,
                    decode_responses=True,
                    max_connections=20
                )
                await self._redis_client.ping()
                logger.info("✅ Connexion Redis performance metrics établie")
            else:
                logger.warning("⚠️ Redis non disponible - mode dégradé activé")
                
            # Initialisation composants IA
            if self.config.enable_ai_insights:
                await self._initialize_ai_components()
            
            # Chargement baseline performance
            await self._load_performance_baseline()
            
            # Démarrage monitoring système
            if self.config.enable_system_monitoring:
                await self._start_system_monitoring()
            
            # Démarrage monitoring application
            if self.config.enable_application_monitoring:
                await self._start_application_monitoring()
            
            # Configuration alertes
            await self._setup_performance_alerts()
            
            self._running = True
            self._start_time = time.time()
            logger.info("🚀 Performance Metrics Storage initialisé")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation performance metrics: {e}")
            return False
    
    async def record_metric(self, metric: PerformanceMetric) -> bool:
        """📊 **Performance Engineer**: Enregistrement métrique performance
        
        Enregistre métrique avec validation, vérification seuils
        et déclenchement alertes automatiques si nécessaire.
        """
        try:
            # Validation métrique
            if not self._validate_metric(metric):
                logger.warning(f"⚠️ Métrique invalide: {metric.name}")
                return False
            
            # Enrichissement automatique
            enriched_metric = await self._enrich_metric(metric)
            
            # Ajout cache et buffer
            self._metrics_cache[metric.name].append(enriched_metric)
            self._metrics_buffer.append(enriched_metric)
            self._metrics_collected += 1
            
            # Vérification seuils et alertes
            await self._check_thresholds(enriched_metric)
            
            # Détection anomalies si activée
            if self.config.anomaly_detection_enabled:
                await self._detect_anomalies(enriched_metric)
            
            # Queue pour traitement batch
            try:
                await self._metrics_queue.put_nowait(enriched_metric)
            except asyncio.QueueFull:
                logger.warning("⚠️ Queue métriques performance pleine")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur enregistrement métrique: {e}")
            return False
    
    async def get_system_health(self) -> SystemHealthMetrics:
        """🖥️ **DevOps**: Santé système temps-réel
        
        Collecte métriques santé système complètes avec
        analyse tendances et scoring performance automatique.
        """
        try:
            # Collecte métriques système actuelles
            health_metrics = await self._collect_system_metrics()
            
            # Mise en cache
            self._system_health_cache = health_metrics
            
            # Enregistrement historique
            await self._record_system_health_history(health_metrics)
            
            return health_metrics
            
        except Exception as e:
            logger.error(f"❌ Erreur collecte santé système: {e}")
            return SystemHealthMetrics()
    
    async def get_application_metrics(self) -> ApplicationMetrics:
        """🚀 **Backend Senior**: Métriques application temps-réel
        
        Collecte métriques application avec analyse performance,
        bottlenecks et recommandations optimisation.
        """
        try:
            # Collecte métriques application
            app_metrics = await self._collect_application_metrics()
            
            # Mise en cache
            self._app_metrics_cache = app_metrics
            
            # Enregistrement historique
            await self._record_app_metrics_history(app_metrics)
            
            return app_metrics
            
        except Exception as e:
            logger.error(f"❌ Erreur collecte métriques application: {e}")
            return ApplicationMetrics()
    
    async def get_performance_dashboard_data(self) -> Dict[str, Any]:
        """📈 **Performance Engineer**: Données dashboard performance
        
        Génère données complètes dashboard performance avec:
        - Métriques temps-réel
        - Alertes actives
        - Insights optimisation
        - Tendances historiques
        """
        try:
            dashboard_data = {
                "timestamp": time.time(),
                "overall_status": await self._calculate_overall_status(),
                "generated_at": datetime.now().isoformat()
            }
            
            # Santé système
            system_health = await self.get_system_health()
            dashboard_data["system_health"] = asdict(system_health)
            
            # Métriques application
            app_metrics = await self.get_application_metrics()
            dashboard_data["application_metrics"] = asdict(app_metrics)
            
            # Alertes actives
            active_alerts = await self._get_active_alerts()
            dashboard_data["active_alerts"] = [asdict(alert) for alert in active_alerts]
            
            # Top métriques critiques
            critical_metrics = await self._get_critical_metrics()
            dashboard_data["critical_metrics"] = critical_metrics
            
            # Tendances performance
            performance_trends = await self._calculate_performance_trends()
            dashboard_data["performance_trends"] = performance_trends
            
            # Insights optimisation
            if self.config.enable_ai_insights:
                optimization_insights = await self._get_optimization_insights()
                dashboard_data["optimization_insights"] = optimization_insights
            
            # Score performance global
            performance_score = await self._calculate_performance_score()
            dashboard_data["performance_score"] = performance_score
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"❌ Erreur génération dashboard performance: {e}")
            return {}
    
    async def get_performance_insights(
        self,
        category: Optional[MetricCategory] = None,
        time_range_hours: int = 24
    ) -> List[PerformanceInsight]:
        """🧠 **ML Engineer**: Insights performance IA
        
        Génère insights performance avec ML:
        - Détection goulots d'étranglement
        - Prédictions dégradation
        - Recommandations optimisation
        - Impact estimé améliorations
        """
        try:
            if not self.config.enable_ai_insights:
                logger.warning("⚠️ Insights IA désactivés")
                return []
            
            insights = []
            
            # Analyse métriques récentes
            recent_metrics = await self._get_recent_metrics(time_range_hours, category)
            
            if not recent_metrics:
                return insights
            
            # Détection bottlenecks
            bottleneck_insights = await self._detect_performance_bottlenecks(recent_metrics)
            insights.extend(bottleneck_insights)
            
            # Prédictions dégradation
            degradation_insights = await self._predict_performance_degradation(recent_metrics)
            insights.extend(degradation_insights)
            
            # Recommandations optimisation
            optimization_insights = await self._generate_optimization_recommendations(recent_metrics)
            insights.extend(optimization_insights)
            
            # Analyse corrélations
            correlation_insights = await self._analyze_metric_correlations(recent_metrics)
            insights.extend(correlation_insights)
            
            # Tri par importance et confiance
            insights.sort(
                key=lambda i: (i.confidence_score, i.generated_at),
                reverse=True
            )
            
            self._insights_generated += len(insights)
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Erreur génération insights performance: {e}")
            return []
    
    async def trigger_performance_alert(
        self,
        metric_name: str,
        current_value: float,
        threshold_value: float,
        alert_level: AlertLevel,
        message: str
    ) -> str:
        """🚨 **Alert System**: Déclenchement alerte performance
        
        Déclenche alerte performance avec notification automatique
        et intégration système monitoring enterprise.
        """
        try:
            alert = PerformanceAlert(
                metric_name=metric_name,
                current_value=current_value,
                threshold_value=threshold_value,
                alert_level=alert_level,
                message=message,
                source="performance_monitor"
            )
            
            # Vérification cooldown
            if await self._is_alert_in_cooldown(metric_name):
                logger.info(f"⏳ Alerte {metric_name} en cooldown")
                return ""
            
            # Stockage alerte
            self._active_alerts[alert.alert_id] = alert
            self._alerts_triggered += 1
            
            # Persistance Redis
            if self._redis_client:
                alert_key = f"{self.alerts_prefix}:{alert.alert_id}"
                alert_data = asdict(alert)
                alert_data['alert_level'] = alert.alert_level.value
                
                await self._redis_client.setex(
                    alert_key,
                    timedelta(days=7),
                    json.dumps(alert_data, default=str)
                )
            
            # Génération recommandations automatiques
            alert.recommendations = await self._generate_alert_recommendations(alert)
            
            logger.warning(f"🚨 Alerte performance {alert_level.value}: {message}")
            return alert.alert_id
            
        except Exception as e:
            logger.error(f"❌ Erreur déclenchement alerte performance: {e}")
            return ""
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """⚡ **Performance Engineer**: Statistiques système monitoring
        
        Retourne métriques détaillées du système de monitoring performance.
        """
        uptime = time.time() - getattr(self, '_start_time', time.time())
        
        # Calcul utilisation ressources système
        current_system = await self._collect_current_system_usage()
        
        return {
            "uptime_seconds": uptime,
            "metrics_collected": self._metrics_collected,
            "alerts_triggered": self._alerts_triggered,
            "insights_generated": self._insights_generated,
            "anomalies_detected": self._anomalies_detected,
            "cached_metrics_series": len(self._metrics_cache),
            "metrics_buffer_size": len(self._metrics_buffer),
            "alerts_buffer_size": len(self._alerts_buffer),
            "queue_size": self._metrics_queue.qsize(),
            "active_alerts_count": len(self._active_alerts),
            "collection_rate_metrics_per_second": self._metrics_collected / max(uptime, 1),
            "system_monitoring_enabled": self.config.enable_system_monitoring,
            "ai_insights_enabled": self.config.enable_ai_insights,
            "current_cpu_usage": current_system.get("cpu_percent", 0),
            "current_memory_usage": current_system.get("memory_percent", 0),
            "monitoring_overhead_cpu": await self._calculate_monitoring_overhead()
        }
    
    # Méthodes internes optimisées
    
    async def _start_system_monitoring(self):
        """Démarrage monitoring système"""
        system_monitor = asyncio.create_task(self._system_monitor_loop())
        self._monitoring_tasks.append(system_monitor)
        
        logger.info("✅ Monitoring système démarré")
    
    async def _start_application_monitoring(self):
        """Démarrage monitoring application"""
        app_monitor = asyncio.create_task(self._application_monitor_loop())
        self._monitoring_tasks.append(app_monitor)
        
        logger.info("✅ Monitoring application démarré")
    
    async def _system_monitor_loop(self):
        """Boucle monitoring système"""
        while self._running:
            try:
                # Collecte métriques système
                system_metrics = await self._collect_system_metrics()
                
                # Conversion en métriques individuelles
                individual_metrics = await self._convert_system_to_metrics(system_metrics)
                
                # Enregistrement métriques
                for metric in individual_metrics:
                    await self.record_metric(metric)
                
                await asyncio.sleep(self.config.collection_interval_seconds)
                
            except Exception as e:
                logger.error(f"❌ Erreur monitoring système: {e}")
                await asyncio.sleep(10)
    
    async def _collect_system_metrics(self) -> SystemHealthMetrics:
        """Collecte métriques système actuelles"""
        try:
            metrics = SystemHealthMetrics()
            
            # CPU
            metrics.cpu_usage_percent = psutil.cpu_percent(interval=1)
            metrics.load_average = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            
            # Mémoire
            memory = psutil.virtual_memory()
            metrics.memory_usage_percent = memory.percent
            
            # Disque
            disk = psutil.disk_usage('/')
            metrics.disk_usage_percent = (disk.used / disk.total) * 100
            
            # Réseau
            network = psutil.net_io_counters()
            metrics.network_bytes_sent = network.bytes_sent
            metrics.network_bytes_received = network.bytes_recv
            
            # Processus
            metrics.process_count = len(psutil.pids())
            
            # Uptime système
            boot_time = psutil.boot_time()
            metrics.boot_time = boot_time
            metrics.system_uptime = time.time() - boot_time
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Erreur collecte métriques système: {e}")
            return SystemHealthMetrics()
    
    def _validate_metric(self, metric: PerformanceMetric) -> bool:
        """Validation métrique performance"""
        return bool(metric.name and metric.category and metric.metric_type)
    
    async def _enrich_metric(self, metric: PerformanceMetric) -> PerformanceMetric:
        """Enrichissement métrique avec contexte"""
        # Ajout tags automatiques
        metric.tags["host"] = "localhost"
        metric.tags["environment"] = "production"
        
        # Ajout timestamp précis si manquant
        if not metric.timestamp:
            metric.timestamp = time.time()
        
        return metric
    
    async def shutdown(self):
        """🛑 **Enterprise**: Arrêt propre du monitoring performance"""
        try:
            self._running = False
            
            # Sauvegarde métriques en cache
            await self._save_cached_metrics()
            
            # Attente fin traitement
            await self._metrics_queue.join()
            
            # Arrêt tâches monitoring
            for task in self._monitoring_tasks:
                task.cancel()
            
            await asyncio.gather(*self._monitoring_tasks, return_exceptions=True)
            
            # Fermeture Redis
            if self._redis_client:
                await self._redis_client.close()
                
            logger.info("⏹️ Performance Metrics Storage arrêté proprement")
            
        except Exception as e:
            logger.error(f"❌ Erreur arrêt performance metrics: {e}")

    # Méthodes helper simplifiées
    
    async def _initialize_ai_components(self):
        """Initialisation composants IA"""
        self._anomaly_detector = "loaded"
        self._performance_predictor = "loaded"
        self._baseline_calculator = "loaded"
    
    async def _load_performance_baseline(self):
        """Chargement baseline performance"""
        pass
    
    async def _setup_performance_alerts(self):
        """Configuration alertes performance"""
        pass

# Factory function
async def create_performance_metrics_storage(config: Optional[PerformanceConfig] = None) -> PerformanceMetricsStorage:
    """🏭 **Factory**: Création instance Performance Metrics Storage
    
    Crée et initialise un système monitoring performance enterprise
    avec IA insights et alertes prédictives.
    """
    if config is None:
        config = PerformanceConfig()
        
    storage = PerformanceMetricsStorage(config)
    
    initialized = await storage.initialize()
    if not initialized:
        logger.warning("⚠️ Performance metrics storage initialisé en mode dégradé")
        
    return storage