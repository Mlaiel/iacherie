#!/usr/bin/env python3
"""⚡ Real-Time Analytics Manager - Advanced Analytics Intelligence
================================================================
Expert: DATA ENGINEER + BACKEND SENIOR + ML ENGINEER + DEVOPS
Technologies: Real-Time Analytics + Stream Processing + Event Analytics + Performance Monitoring
Architecture: Level 3 - Analytics Intelligence Layer
Date: 2025-01-14

Ultra-advanced real-time analytics system for Redis orchestration with stream processing,
event analytics, performance monitoring and intelligent insights generation.
================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
Utilisation commerciale INTERDITE sans autorisation écrite explicite
================================================================
"""

import asyncio
import logging
import json
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import redis
from collections import deque, defaultdict
import statistics
import math
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class AnalyticsType(Enum):
    """Types d'analytics supportés"""
    PERFORMANCE = "performance"
    BUSINESS = "business"
    TECHNICAL = "technical"
    USER_BEHAVIOR = "user_behavior"
    SYSTEM_HEALTH = "system_health"
    CREATOR_ECONOMY = "creator_economy"
    SECURITY = "security"
    OPERATIONAL = "operational"

class MetricType(Enum):
    """Types de métriques"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    RATE = "rate"
    PERCENTAGE = "percentage"
    RATIO = "ratio"
    DURATION = "duration"

class AggregationType(Enum):
    """Types d'agrégation"""
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    MEDIAN = "median"
    PERCENTILE = "percentile"
    STDDEV = "stddev"

class AlertSeverity(Enum):
    """Niveaux de sévérité des alertes"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    FATAL = "fatal"

@dataclass
class AnalyticsEvent:
    """Événement analytique"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    analytics_type: AnalyticsType = AnalyticsType.PERFORMANCE
    source: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metrics: Dict[str, Any] = field(default_factory=dict)
    dimensions: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class MetricDefinition:
    """Définition d'une métrique"""
    metric_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    metric_type: MetricType = MetricType.GAUGE
    unit: str = ""
    dimensions: List[str] = field(default_factory=list)
    aggregations: List[AggregationType] = field(default_factory=list)
    retention_period: timedelta = timedelta(days=30)
    is_business_critical: bool = False
    alert_thresholds: Dict[str, float] = field(default_factory=dict)

@dataclass
class AnalyticsResult:
    """Résultat d'analyse"""
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metric_name: str = ""
    aggregation_type: AggregationType = AggregationType.AVERAGE
    value: float = 0.0
    time_range: Tuple[datetime, datetime] = field(default_factory=lambda: (datetime.now(), datetime.now()))
    dimensions: Dict[str, str] = field(default_factory=dict)
    confidence: float = 1.0
    sample_size: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalyticsAlert:
    """Alerte analytique"""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metric_name: str = ""
    severity: AlertSeverity = AlertSeverity.WARNING
    message: str = ""
    current_value: float = 0.0
    threshold_value: float = 0.0
    condition: str = ""
    triggered_at: datetime = field(default_factory=datetime.now)
    dimensions: Dict[str, str] = field(default_factory=dict)
    is_acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None

@dataclass
class DashboardWidget:
    """Widget de dashboard"""
    widget_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    widget_type: str = "chart"  # chart, table, metric, gauge
    metric_name: str = ""
    aggregation: AggregationType = AggregationType.AVERAGE
    time_range: timedelta = timedelta(hours=24)
    refresh_interval: timedelta = timedelta(minutes=5)
    dimensions: Dict[str, str] = field(default_factory=dict)
    visualization_config: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, int] = field(default_factory=dict)

@dataclass
class RealTimeAnalyticsConfig:
    """Configuration du gestionnaire d'analytics en temps réel"""
    stream_buffer_size: int = 10000
    batch_processing_interval: timedelta = timedelta(seconds=10)
    metric_retention_days: int = 30
    enable_real_time_alerts: bool = True
    enable_anomaly_detection: bool = True
    anomaly_threshold: float = 2.0  # Standard deviations
    alert_cooldown_period: timedelta = timedelta(minutes=5)
    max_concurrent_processors: int = 5
    enable_predictive_analytics: bool = True
    compression_enabled: bool = True
    sampling_rate: float = 1.0  # 1.0 = 100% sampling

class RedisRealTimeAnalyticsManager:
    """Gestionnaire d'analytics en temps réel Redis enterprise"""
    
    def __init__(self, config: RealTimeAnalyticsConfig, redis_client: Optional[redis.Redis] = None):
        self.config = config
        self.redis_client = redis_client or redis.Redis()
        self.is_running = False
        
        # Composants internes
        self.event_stream = deque(maxlen=config.stream_buffer_size)
        self.metric_definitions = {}
        self.active_alerts = {}
        self.dashboard_widgets = {}
        self.metric_cache = defaultdict(dict)
        
        # Processeurs de métriques
        self.metric_processors = {}
        self.aggregation_processors = {}
        
        # Détection d'anomalies
        self.metric_history = defaultdict(lambda: deque(maxlen=1000))
        self.anomaly_models = {}
        
        # Métriques du gestionnaire
        self.manager_metrics = {
            'events_processed': 0,
            'alerts_triggered': 0,
            'anomalies_detected': 0,
            'processing_latency': deque(maxlen=1000),
            'last_batch_time': None,
            'active_streams': 0
        }
        
        # Tâches asynchrones
        self.processing_tasks = {}
        
    async def initialize(self) -> bool:
        """Initialise le gestionnaire d'analytics"""
        try:
            logger.info("⚡ Initializing Real-Time Analytics Manager...")
            
            # Charger les définitions de métriques
            await self._load_metric_definitions()
            
            # Charger les widgets de dashboard
            await self._load_dashboard_widgets()
            
            # Initialiser les processeurs
            await self._initialize_processors()
            
            # Démarrer les tâches de traitement
            await self._start_processing_tasks()
            
            self.is_running = True
            logger.info("✅ Real-Time Analytics Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Real-Time Analytics Manager: {e}")
            return False
    
    async def _load_metric_definitions(self):
        """Charge les définitions de métriques depuis Redis"""
        try:
            keys = [key.decode() for key in self.redis_client.keys("analytics:metrics:*")]
            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    metric_data = json.loads(data)
                    metric = MetricDefinition(**metric_data)
                    self.metric_definitions[metric.name] = metric
            
            # Ajouter des métriques par défaut si aucune n'existe
            if not self.metric_definitions:
                await self._create_default_metrics()
            
            logger.info(f"✅ Loaded {len(self.metric_definitions)} metric definitions")
            
        except Exception as e:
            logger.error(f"❌ Failed to load metric definitions: {e}")
    
    async def _create_default_metrics(self):
        """Crée les métriques par défaut"""
        default_metrics = [
            MetricDefinition(
                name="redis_operations_per_second",
                description="Number of Redis operations per second",
                metric_type=MetricType.RATE,
                unit="ops/sec",
                aggregations=[AggregationType.SUM, AggregationType.AVERAGE],
                alert_thresholds={'high': 10000, 'critical': 20000}
            ),
            MetricDefinition(
                name="memory_usage_percentage",
                description="Memory usage percentage",
                metric_type=MetricType.PERCENTAGE,
                unit="%",
                aggregations=[AggregationType.AVERAGE, AggregationType.MAX],
                alert_thresholds={'warning': 80, 'critical': 95}
            ),
            MetricDefinition(
                name="response_time_ms",
                description="Average response time in milliseconds",
                metric_type=MetricType.DURATION,
                unit="ms",
                aggregations=[AggregationType.AVERAGE, AggregationType.PERCENTILE],
                alert_thresholds={'warning': 100, 'critical': 500}
            ),
            MetricDefinition(
                name="active_connections",
                description="Number of active Redis connections",
                metric_type=MetricType.GAUGE,
                unit="connections",
                aggregations=[AggregationType.AVERAGE, AggregationType.MAX],
                alert_thresholds={'high': 1000, 'critical': 2000}
            ),
            MetricDefinition(
                name="creator_content_uploads",
                description="Number of creator content uploads",
                metric_type=MetricType.COUNTER,
                unit="uploads",
                aggregations=[AggregationType.SUM, AggregationType.RATE],
                is_business_critical=True
            )
        ]
        
        for metric in default_metrics:
            self.metric_definitions[metric.name] = metric
            await self._store_metric_definition(metric)
    
    async def _store_metric_definition(self, metric: MetricDefinition):
        """Stocke une définition de métrique dans Redis"""
        try:
            key = f"analytics:metrics:{metric.name}"
            data = {
                'metric_id': metric.metric_id,
                'name': metric.name,
                'description': metric.description,
                'metric_type': metric.metric_type.value,
                'unit': metric.unit,
                'dimensions': metric.dimensions,
                'aggregations': [agg.value for agg in metric.aggregations],
                'retention_period': metric.retention_period.total_seconds(),
                'is_business_critical': metric.is_business_critical,
                'alert_thresholds': metric.alert_thresholds
            }
            
            self.redis_client.setex(key, 30 * 24 * 3600, json.dumps(data))  # 30 jours
            
        except Exception as e:
            logger.error(f"❌ Failed to store metric definition: {e}")
    
    async def _load_dashboard_widgets(self):
        """Charge les widgets de dashboard"""
        try:
            keys = [key.decode() for key in self.redis_client.keys("analytics:widgets:*")]
            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    widget_data = json.loads(data)
                    widget = DashboardWidget(**widget_data)
                    self.dashboard_widgets[widget.widget_id] = widget
            
            logger.info(f"✅ Loaded {len(self.dashboard_widgets)} dashboard widgets")
            
        except Exception as e:
            logger.error(f"❌ Failed to load dashboard widgets: {e}")
    
    async def _initialize_processors(self):
        """Initialise les processeurs de métriques"""
        try:
            # Processeurs par type de métrique
            self.metric_processors[MetricType.COUNTER] = self._process_counter_metric
            self.metric_processors[MetricType.GAUGE] = self._process_gauge_metric
            self.metric_processors[MetricType.RATE] = self._process_rate_metric
            self.metric_processors[MetricType.DURATION] = self._process_duration_metric
            self.metric_processors[MetricType.PERCENTAGE] = self._process_percentage_metric
            
            # Processeurs d'agrégation
            self.aggregation_processors[AggregationType.SUM] = lambda values: sum(values)
            self.aggregation_processors[AggregationType.AVERAGE] = lambda values: statistics.mean(values)
            self.aggregation_processors[AggregationType.MIN] = lambda values: min(values)
            self.aggregation_processors[AggregationType.MAX] = lambda values: max(values)
            self.aggregation_processors[AggregationType.COUNT] = lambda values: len(values)
            self.aggregation_processors[AggregationType.MEDIAN] = lambda values: statistics.median(values)
            self.aggregation_processors[AggregationType.STDDEV] = lambda values: statistics.stdev(values) if len(values) > 1 else 0
            
            logger.info("✅ Metric processors initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize processors: {e}")
    
    async def _start_processing_tasks(self):
        """Démarre les tâches de traitement"""
        self.processing_tasks['batch'] = asyncio.create_task(self._batch_processing_loop())
        self.processing_tasks['alerts'] = asyncio.create_task(self._alert_processing_loop())
        
        if self.config.enable_anomaly_detection:
            self.processing_tasks['anomaly'] = asyncio.create_task(self._anomaly_detection_loop())
        
        self.processing_tasks['cleanup'] = asyncio.create_task(self._cleanup_loop())
    
    async def ingest_event(self, event: AnalyticsEvent) -> bool:
        """Ingère un événement analytique"""
        try:
            # Échantillonnage si configuré
            if self.config.sampling_rate < 1.0:
                if np.random.random() > self.config.sampling_rate:
                    return True  # Événement ignoré mais pas d'erreur
            
            # Ajouter au stream
            self.event_stream.append(event)
            
            # Traitement temps réel si requis
            if event.analytics_type in [AnalyticsType.SECURITY, AnalyticsType.SYSTEM_HEALTH]:
                await self._process_event_real_time(event)
            
            # Mettre à jour les métriques du gestionnaire
            self.manager_metrics['events_processed'] += 1
            self.manager_metrics['active_streams'] = len(self.event_stream)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to ingest event: {e}")
            return False
    
    async def _process_event_real_time(self, event: AnalyticsEvent):
        """Traite un événement en temps réel"""
        try:
            start_time = time.time()
            
            # Traiter chaque métrique dans l'événement
            for metric_name, value in event.metrics.items():
                if metric_name in self.metric_definitions:
                    metric_def = self.metric_definitions[metric_name]
                    
                    # Traiter la métrique selon son type
                    processor = self.metric_processors.get(metric_def.metric_type)
                    if processor:
                        await processor(metric_name, value, event, metric_def)
                    
                    # Vérifier les seuils d'alerte
                    if self.config.enable_real_time_alerts:
                        await self._check_alert_thresholds(metric_name, value, metric_def, event)
                    
                    # Ajouter à l'historique pour détection d'anomalies
                    if self.config.enable_anomaly_detection:
                        self.metric_history[metric_name].append({
                            'value': value,
                            'timestamp': event.timestamp,
                            'dimensions': event.dimensions
                        })
            
            # Mettre à jour la latence de traitement
            processing_time = time.time() - start_time
            self.manager_metrics['processing_latency'].append(processing_time)
            
        except Exception as e:
            logger.error(f"❌ Failed to process event in real-time: {e}")
    
    async def _process_counter_metric(self, metric_name: str, value: float, 
                                    event: AnalyticsEvent, metric_def: MetricDefinition):
        """Traite une métrique de type compteur"""
        key = f"analytics:counter:{metric_name}"
        dimension_key = self._create_dimension_key(event.dimensions)
        
        # Incrémenter le compteur
        self.redis_client.hincrby(key, dimension_key, int(value))
        
        # Définir TTL pour la rétention
        ttl = int(metric_def.retention_period.total_seconds())
        self.redis_client.expire(key, ttl)
    
    async def _process_gauge_metric(self, metric_name: str, value: float,
                                  event: AnalyticsEvent, metric_def: MetricDefinition):
        """Traite une métrique de type jauge"""
        key = f"analytics:gauge:{metric_name}"
        dimension_key = self._create_dimension_key(event.dimensions)
        
        # Stocker la valeur avec timestamp
        data = {
            'value': value,
            'timestamp': event.timestamp.isoformat(),
            'dimensions': event.dimensions
        }
        
        self.redis_client.hset(key, dimension_key, json.dumps(data))
        
        # Définir TTL pour la rétention
        ttl = int(metric_def.retention_period.total_seconds())
        self.redis_client.expire(key, ttl)
    
    async def _process_rate_metric(self, metric_name: str, value: float,
                                 event: AnalyticsEvent, metric_def: MetricDefinition):
        """Traite une métrique de type taux"""
        # Utiliser une fenêtre glissante pour calculer le taux
        key = f"analytics:rate:{metric_name}"
        
        # Ajouter la valeur avec timestamp
        score = event.timestamp.timestamp()
        self.redis_client.zadd(key, {str(value): score})
        
        # Nettoyer les anciennes valeurs (plus de 1 heure)
        cutoff = (event.timestamp - timedelta(hours=1)).timestamp()
        self.redis_client.zremrangebyscore(key, 0, cutoff)
        
        # Définir TTL
        ttl = int(metric_def.retention_period.total_seconds())
        self.redis_client.expire(key, ttl)
    
    async def _process_duration_metric(self, metric_name: str, value: float,
                                     event: AnalyticsEvent, metric_def: MetricDefinition):
        """Traite une métrique de type durée"""
        key = f"analytics:duration:{metric_name}"
        dimension_key = self._create_dimension_key(event.dimensions)
        
        # Stocker dans une liste pour calculs statistiques
        data = {
            'value': value,
            'timestamp': event.timestamp.isoformat(),
            'dimensions': event.dimensions
        }
        
        self.redis_client.lpush(f"{key}:{dimension_key}", json.dumps(data))
        
        # Limiter la taille de la liste
        self.redis_client.ltrim(f"{key}:{dimension_key}", 0, 999)  # Garder 1000 valeurs
        
        # Définir TTL
        ttl = int(metric_def.retention_period.total_seconds())
        self.redis_client.expire(f"{key}:{dimension_key}", ttl)
    
    async def _process_percentage_metric(self, metric_name: str, value: float,
                                       event: AnalyticsEvent, metric_def: MetricDefinition):
        """Traite une métrique de type pourcentage"""
        # Traiter comme une jauge avec validation de plage
        if 0 <= value <= 100:
            await self._process_gauge_metric(metric_name, value, event, metric_def)
        else:
            logger.warning(f"⚠️ Invalid percentage value for {metric_name}: {value}")
    
    def _create_dimension_key(self, dimensions: Dict[str, str]) -> str:
        """Crée une clé pour les dimensions"""
        if not dimensions:
            return "default"
        
        # Trier les clés pour assurer la cohérence
        sorted_dims = sorted(dimensions.items())
        return ":".join([f"{k}={v}" for k, v in sorted_dims])
    
    async def _check_alert_thresholds(self, metric_name: str, value: float,
                                    metric_def: MetricDefinition, event: AnalyticsEvent):
        """Vérifie les seuils d'alerte"""
        try:
            for threshold_name, threshold_value in metric_def.alert_thresholds.items():
                should_alert = False
                severity = AlertSeverity.WARNING
                condition = ""
                
                # Déterminer la condition d'alerte
                if threshold_name in ['high', 'max']:
                    should_alert = value > threshold_value
                    condition = f"{metric_name} > {threshold_value}"
                    severity = AlertSeverity.WARNING if threshold_name == 'high' else AlertSeverity.ERROR
                elif threshold_name in ['low', 'min']:
                    should_alert = value < threshold_value
                    condition = f"{metric_name} < {threshold_value}"
                    severity = AlertSeverity.WARNING
                elif threshold_name == 'critical':
                    should_alert = value > threshold_value
                    condition = f"{metric_name} > {threshold_value}"
                    severity = AlertSeverity.CRITICAL
                elif threshold_name == 'warning':
                    should_alert = value > threshold_value
                    condition = f"{metric_name} > {threshold_value}"
                    severity = AlertSeverity.WARNING
                
                if should_alert:
                    # Vérifier la période de cooldown
                    alert_key = f"{metric_name}:{threshold_name}:{self._create_dimension_key(event.dimensions)}"
                    
                    if not await self._is_in_cooldown(alert_key):
                        alert = AnalyticsAlert(
                            metric_name=metric_name,
                            severity=severity,
                            message=f"Metric {metric_name} exceeded {threshold_name} threshold",
                            current_value=value,
                            threshold_value=threshold_value,
                            condition=condition,
                            dimensions=event.dimensions
                        )
                        
                        await self._trigger_alert(alert, alert_key)
                        self.manager_metrics['alerts_triggered'] += 1
        
        except Exception as e:
            logger.error(f"❌ Failed to check alert thresholds: {e}")
    
    async def _is_in_cooldown(self, alert_key: str) -> bool:
        """Vérifie si une alerte est en période de cooldown"""
        cooldown_key = f"analytics:cooldown:{alert_key}"
        return self.redis_client.exists(cooldown_key)
    
    async def _trigger_alert(self, alert: AnalyticsAlert, alert_key: str):
        """Déclenche une alerte"""
        try:
            # Stocker l'alerte
            self.active_alerts[alert.alert_id] = alert
            await self._store_alert(alert)
            
            # Définir la période de cooldown
            cooldown_key = f"analytics:cooldown:{alert_key}"
            cooldown_seconds = int(self.config.alert_cooldown_period.total_seconds())
            self.redis_client.setex(cooldown_key, cooldown_seconds, "1")
            
            # Log de l'alerte
            logger.warning(f"🚨 ALERT [{alert.severity.value.upper()}]: {alert.message} "
                         f"(Value: {alert.current_value}, Threshold: {alert.threshold_value})")
            
            # Publier l'alerte sur un canal Redis pour notification
            alert_data = {
                'alert_id': alert.alert_id,
                'metric_name': alert.metric_name,
                'severity': alert.severity.value,
                'message': alert.message,
                'current_value': alert.current_value,
                'threshold_value': alert.threshold_value,
                'triggered_at': alert.triggered_at.isoformat(),
                'dimensions': alert.dimensions
            }
            
            self.redis_client.publish("analytics:alerts", json.dumps(alert_data))
            
        except Exception as e:
            logger.error(f"❌ Failed to trigger alert: {e}")
    
    async def _store_alert(self, alert: AnalyticsAlert):
        """Stocke une alerte dans Redis"""
        try:
            key = f"analytics:alerts:{alert.alert_id}"
            data = {
                'alert_id': alert.alert_id,
                'metric_name': alert.metric_name,
                'severity': alert.severity.value,
                'message': alert.message,
                'current_value': alert.current_value,
                'threshold_value': alert.threshold_value,
                'condition': alert.condition,
                'triggered_at': alert.triggered_at.isoformat(),
                'dimensions': alert.dimensions,
                'is_acknowledged': alert.is_acknowledged,
                'acknowledged_by': alert.acknowledged_by,
                'acknowledged_at': alert.acknowledged_at.isoformat() if alert.acknowledged_at else None
            }
            
            self.redis_client.setex(key, 7 * 24 * 3600, json.dumps(data))  # 7 jours
            
        except Exception as e:
            logger.error(f"❌ Failed to store alert: {e}")
    
    async def _batch_processing_loop(self):
        """Boucle de traitement par batch"""
        while self.is_running:
            try:
                batch_start = time.time()
                
                # Traiter les événements en attente
                if self.event_stream:
                    events_to_process = []
                    
                    # Extraire un batch d'événements
                    batch_size = min(1000, len(self.event_stream))
                    for _ in range(batch_size):
                        if self.event_stream:
                            events_to_process.append(self.event_stream.popleft())
                    
                    # Traiter le batch
                    if events_to_process:
                        await self._process_event_batch(events_to_process)
                
                # Calculer les agrégations
                await self._calculate_aggregations()
                
                # Mettre à jour les métriques du gestionnaire
                batch_time = time.time() - batch_start
                self.manager_metrics['last_batch_time'] = datetime.now()
                
                # Attendre avant le prochain batch
                await asyncio.sleep(self.config.batch_processing_interval.total_seconds())
                
            except Exception as e:
                logger.error(f"❌ Error in batch processing loop: {e}")
                await asyncio.sleep(10)
    
    async def _process_event_batch(self, events: List[AnalyticsEvent]):
        """Traite un batch d'événements"""
        try:
            # Grouper les événements par type de métrique
            metric_groups = defaultdict(list)
            
            for event in events:
                for metric_name, value in event.metrics.items():
                    if metric_name in self.metric_definitions:
                        metric_groups[metric_name].append((value, event))
            
            # Traiter chaque groupe de métriques
            for metric_name, metric_data in metric_groups.items():
                metric_def = self.metric_definitions[metric_name]
                processor = self.metric_processors.get(metric_def.metric_type)
                
                if processor:
                    for value, event in metric_data:
                        await processor(metric_name, value, event, metric_def)
            
            logger.debug(f"✅ Processed batch of {len(events)} events")
            
        except Exception as e:
            logger.error(f"❌ Failed to process event batch: {e}")
    
    async def _calculate_aggregations(self):
        """Calcule les agrégations pour toutes les métriques"""
        try:
            for metric_name, metric_def in self.metric_definitions.items():
                for aggregation in metric_def.aggregations:
                    await self._calculate_metric_aggregation(metric_name, aggregation, metric_def)
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate aggregations: {e}")
    
    async def _calculate_metric_aggregation(self, metric_name: str, 
                                          aggregation: AggregationType,
                                          metric_def: MetricDefinition):
        """Calcule l'agrégation pour une métrique spécifique"""
        try:
            # Récupérer les données selon le type de métrique
            values = await self._get_metric_values(metric_name, metric_def.metric_type)
            
            if not values:
                return
            
            # Calculer l'agrégation
            processor = self.aggregation_processors.get(aggregation)
            if processor:
                result_value = processor(values)
                
                # Stocker le résultat
                result = AnalyticsResult(
                    metric_name=metric_name,
                    aggregation_type=aggregation,
                    value=result_value,
                    time_range=(datetime.now() - timedelta(hours=1), datetime.now()),
                    sample_size=len(values)
                )
                
                await self._store_aggregation_result(result)
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate aggregation for {metric_name}: {e}")
    
    async def _get_metric_values(self, metric_name: str, metric_type: MetricType) -> List[float]:
        """Récupère les valeurs d'une métrique"""
        try:
            values = []
            
            if metric_type == MetricType.GAUGE:
                key = f"analytics:gauge:{metric_name}"
                data = self.redis_client.hgetall(key)
                
                for dimension_data in data.values():
                    if isinstance(dimension_data, bytes):
                        dimension_data = dimension_data.decode()
                    
                    try:
                        parsed_data = json.loads(dimension_data)
                        values.append(float(parsed_data['value']))
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue
            
            elif metric_type == MetricType.DURATION:
                key = f"analytics:duration:{metric_name}"
                keys = [key.decode() for key in self.redis_client.keys(f"{key}:*")]
                
                for sub_key in keys:
                    duration_data = self.redis_client.lrange(sub_key, 0, -1)
                    for data in duration_data:
                        if isinstance(data, bytes):
                            data = data.decode()
                        
                        try:
                            parsed_data = json.loads(data)
                            values.append(float(parsed_data['value']))
                        except (json.JSONDecodeError, KeyError, ValueError):
                            continue
            
            elif metric_type == MetricType.RATE:
                key = f"analytics:rate:{metric_name}"
                # Récupérer les valeurs de la dernière heure
                cutoff = (datetime.now() - timedelta(hours=1)).timestamp()
                data = self.redis_client.zrangebyscore(key, cutoff, '+inf')
                
                values = [float(value) for value in data if value]
            
            return values
            
        except Exception as e:
            logger.error(f"❌ Failed to get metric values for {metric_name}: {e}")
            return []
    
    async def _store_aggregation_result(self, result: AnalyticsResult):
        """Stocke un résultat d'agrégation"""
        try:
            key = f"analytics:aggregations:{result.metric_name}:{result.aggregation_type.value}"
            data = {
                'result_id': result.result_id,
                'metric_name': result.metric_name,
                'aggregation_type': result.aggregation_type.value,
                'value': result.value,
                'time_range': [result.time_range[0].isoformat(), result.time_range[1].isoformat()],
                'dimensions': result.dimensions,
                'confidence': result.confidence,
                'sample_size': result.sample_size,
                'metadata': result.metadata
            }
            
            # Stocker avec timestamp pour série temporelle
            timestamp = int(result.time_range[1].timestamp())
            self.redis_client.zadd(key, {json.dumps(data): timestamp})
            
            # Nettoyer les anciennes données
            cutoff = (datetime.now() - timedelta(days=self.config.metric_retention_days)).timestamp()
            self.redis_client.zremrangebyscore(key, 0, cutoff)
            
        except Exception as e:
            logger.error(f"❌ Failed to store aggregation result: {e}")
    
    async def _alert_processing_loop(self):
        """Boucle de traitement des alertes"""
        while self.is_running:
            try:
                # Vérifier les alertes actives
                for alert_id, alert in list(self.active_alerts.items()):
                    # Auto-résoudre les alertes anciennes si la métrique est revenue normale
                    if not alert.is_acknowledged:
                        is_resolved = await self._check_alert_resolution(alert)
                        if is_resolved:
                            await self._resolve_alert(alert)
                            del self.active_alerts[alert_id]
                
                await asyncio.sleep(60)  # Vérifier toutes les minutes
                
            except Exception as e:
                logger.error(f"❌ Error in alert processing loop: {e}")
                await asyncio.sleep(300)
    
    async def _check_alert_resolution(self, alert: AnalyticsAlert) -> bool:
        """Vérifie si une alerte peut être résolue automatiquement"""
        try:
            # Récupérer la valeur actuelle de la métrique
            current_values = await self._get_metric_values(
                alert.metric_name,
                self.metric_definitions[alert.metric_name].metric_type
            )
            
            if not current_values:
                return False
            
            current_value = statistics.mean(current_values)
            
            # Vérifier si la valeur est revenue sous le seuil
            if ">" in alert.condition and current_value <= alert.threshold_value * 0.9:
                return True
            elif "<" in alert.condition and current_value >= alert.threshold_value * 1.1:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to check alert resolution: {e}")
            return False
    
    async def _resolve_alert(self, alert: AnalyticsAlert):
        """Résout une alerte automatiquement"""
        try:
            logger.info(f"✅ Auto-resolving alert {alert.alert_id}: {alert.message}")
            
            # Publier la résolution sur le canal Redis
            resolution_data = {
                'alert_id': alert.alert_id,
                'metric_name': alert.metric_name,
                'message': f"Alert {alert.alert_id} auto-resolved",
                'resolved_at': datetime.now().isoformat()
            }
            
            self.redis_client.publish("analytics:alert_resolutions", json.dumps(resolution_data))
            
        except Exception as e:
            logger.error(f"❌ Failed to resolve alert: {e}")
    
    async def _anomaly_detection_loop(self):
        """Boucle de détection d'anomalies"""
        while self.is_running:
            try:
                for metric_name, history in self.metric_history.items():
                    if len(history) >= 30:  # Minimum 30 points pour détection
                        anomalies = await self._detect_anomalies(metric_name, history)
                        
                        for anomaly in anomalies:
                            await self._handle_anomaly(anomaly, metric_name)
                            self.manager_metrics['anomalies_detected'] += 1
                
                await asyncio.sleep(300)  # Vérifier toutes les 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in anomaly detection loop: {e}")
                await asyncio.sleep(600)
    
    async def _detect_anomalies(self, metric_name: str, history: deque) -> List[Dict[str, Any]]:
        """Détecte les anomalies dans l'historique d'une métrique"""
        try:
            values = [point['value'] for point in history]
            
            if len(values) < 30:
                return []
            
            # Calcul statistique simple pour détection d'anomalies
            mean_val = statistics.mean(values)
            std_val = statistics.stdev(values)
            
            anomalies = []
            threshold = self.config.anomaly_threshold * std_val
            
            # Vérifier les dernières valeurs
            for i, point in enumerate(list(history)[-10:]):  # 10 dernières valeurs
                value = point['value']
                
                if abs(value - mean_val) > threshold:
                    anomaly = {
                        'metric_name': metric_name,
                        'value': value,
                        'expected_range': (mean_val - threshold, mean_val + threshold),
                        'deviation': abs(value - mean_val) / std_val if std_val > 0 else 0,
                        'timestamp': point['timestamp'],
                        'dimensions': point['dimensions']
                    }
                    anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"❌ Failed to detect anomalies for {metric_name}: {e}")
            return []
    
    async def _handle_anomaly(self, anomaly: Dict[str, Any], metric_name: str):
        """Traite une anomalie détectée"""
        try:
            # Créer une alerte d'anomalie
            alert = AnalyticsAlert(
                metric_name=metric_name,
                severity=AlertSeverity.WARNING,
                message=f"Anomaly detected in {metric_name}: value {anomaly['value']:.2f} deviates significantly from expected range",
                current_value=anomaly['value'],
                threshold_value=anomaly['expected_range'][1],
                condition=f"Statistical anomaly detected (deviation: {anomaly['deviation']:.2f}σ)",
                dimensions=anomaly['dimensions']
            )
            
            # Stocker et publier l'alerte
            await self._trigger_alert(alert, f"anomaly:{metric_name}")
            
            logger.warning(f"🔍 ANOMALY DETECTED in {metric_name}: "
                         f"Value {anomaly['value']:.2f} outside expected range "
                         f"{anomaly['expected_range'][0]:.2f}-{anomaly['expected_range'][1]:.2f}")
            
        except Exception as e:
            logger.error(f"❌ Failed to handle anomaly: {e}")
    
    async def _cleanup_loop(self):
        """Boucle de nettoyage des données anciennes"""
        while self.is_running:
            try:
                # Nettoyer les données expirées
                cutoff_time = datetime.now() - timedelta(days=self.config.metric_retention_days)
                
                # Nettoyer les agrégations anciennes
                await self._cleanup_old_aggregations(cutoff_time)
                
                # Nettoyer l'historique des métriques en mémoire
                self._cleanup_metric_history(cutoff_time)
                
                # Nettoyer les alertes résolues anciennes
                await self._cleanup_old_alerts(cutoff_time)
                
                logger.info("✅ Cleanup completed")
                
                # Nettoyer une fois par jour
                await asyncio.sleep(24 * 3600)
                
            except Exception as e:
                logger.error(f"❌ Error in cleanup loop: {e}")
                await asyncio.sleep(3600)
    
    async def _cleanup_old_aggregations(self, cutoff_time: datetime):
        """Nettoie les anciennes agrégations"""
        try:
            cutoff_timestamp = cutoff_time.timestamp()
            keys = [key.decode() for key in self.redis_client.keys("analytics:aggregations:*")]
            
            for key in keys:
                # Supprimer les anciennes entrées
                self.redis_client.zremrangebyscore(key, 0, cutoff_timestamp)
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old aggregations: {e}")
    
    def _cleanup_metric_history(self, cutoff_time: datetime):
        """Nettoie l'historique des métriques en mémoire"""
        try:
            for metric_name, history in self.metric_history.items():
                # Filtrer les points trop anciens
                filtered_history = deque(maxlen=1000)
                
                for point in history:
                    point_time = datetime.fromisoformat(point['timestamp'])
                    if point_time > cutoff_time:
                        filtered_history.append(point)
                
                self.metric_history[metric_name] = filtered_history
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup metric history: {e}")
    
    async def _cleanup_old_alerts(self, cutoff_time: datetime):
        """Nettoie les anciennes alertes"""
        try:
            keys = [key.decode() for key in self.redis_client.keys("analytics:alerts:*")]
            
            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    alert_data = json.loads(data)
                    triggered_at = datetime.fromisoformat(alert_data['triggered_at'])
                    
                    # Supprimer les alertes résolues anciennes
                    if (alert_data.get('is_acknowledged', False) and 
                        triggered_at < cutoff_time):
                        self.redis_client.delete(key)
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old alerts: {e}")
    
    async def get_metric_data(self, metric_name: str, 
                            aggregation: AggregationType = AggregationType.AVERAGE,
                            time_range: Optional[Tuple[datetime, datetime]] = None,
                            dimensions: Optional[Dict[str, str]] = None) -> List[AnalyticsResult]:
        """Récupère les données d'une métrique"""
        try:
            if time_range is None:
                end_time = datetime.now()
                start_time = end_time - timedelta(hours=24)
                time_range = (start_time, end_time)
            
            key = f"analytics:aggregations:{metric_name}:{aggregation.value}"
            
            start_timestamp = time_range[0].timestamp()
            end_timestamp = time_range[1].timestamp()
            
            # Récupérer les données dans la plage temporelle
            data = self.redis_client.zrangebyscore(key, start_timestamp, end_timestamp)
            
            results = []
            for item in data:
                if isinstance(item, bytes):
                    item = item.decode()
                
                try:
                    result_data = json.loads(item)
                    
                    # Filtrer par dimensions si spécifiées
                    if dimensions:
                        result_dimensions = result_data.get('dimensions', {})
                        if not all(result_dimensions.get(k) == v for k, v in dimensions.items()):
                            continue
                    
                    result = AnalyticsResult(**result_data)
                    results.append(result)
                    
                except (json.JSONDecodeError, TypeError):
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to get metric data for {metric_name}: {e}")
            return []
    
    async def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[AnalyticsAlert]:
        """Récupère les alertes actives"""
        try:
            alerts = list(self.active_alerts.values())
            
            if severity:
                alerts = [alert for alert in alerts if alert.severity == severity]
            
            # Trier par sévérité et date
            severity_order = {
                AlertSeverity.CRITICAL: 0,
                AlertSeverity.ERROR: 1,
                AlertSeverity.WARNING: 2,
                AlertSeverity.INFO: 3
            }
            
            alerts.sort(key=lambda x: (severity_order.get(x.severity, 3), x.triggered_at), reverse=True)
            
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Failed to get active alerts: {e}")
            return []
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acquitte une alerte"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.is_acknowledged = True
                alert.acknowledged_by = acknowledged_by
                alert.acknowledged_at = datetime.now()
                
                # Mettre à jour dans Redis
                await self._store_alert(alert)
                
                logger.info(f"✅ Alert {alert_id} acknowledged by {acknowledged_by}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to acknowledge alert {alert_id}: {e}")
            return False
    
    async def get_manager_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques du gestionnaire"""
        try:
            avg_latency = (statistics.mean(self.manager_metrics['processing_latency']) 
                          if self.manager_metrics['processing_latency'] else 0)
            
            return {
                'events_processed': self.manager_metrics['events_processed'],
                'alerts_triggered': self.manager_metrics['alerts_triggered'],
                'anomalies_detected': self.manager_metrics['anomalies_detected'],
                'avg_processing_latency_ms': avg_latency * 1000,
                'active_streams': self.manager_metrics['active_streams'],
                'last_batch_time': (self.manager_metrics['last_batch_time'].isoformat() 
                                  if self.manager_metrics['last_batch_time'] else None),
                'active_alerts_count': len(self.active_alerts),
                'metric_definitions_count': len(self.metric_definitions),
                'dashboard_widgets_count': len(self.dashboard_widgets),
                'is_running': self.is_running
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get manager metrics: {e}")
            return {}
    
    async def shutdown(self):
        """Arrête le gestionnaire d'analytics"""
        try:
            logger.info("🛑 Shutting down Real-Time Analytics Manager...")
            
            self.is_running = False
            
            # Arrêter toutes les tâches
            for task_name, task in self.processing_tasks.items():
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                    logger.info(f"✅ {task_name} task stopped")
            
            # Traiter les événements restants
            if self.event_stream:
                remaining_events = list(self.event_stream)
                if remaining_events:
                    await self._process_event_batch(remaining_events)
                    logger.info(f"✅ Processed {len(remaining_events)} remaining events")
            
            logger.info("✅ Real-Time Analytics Manager shut down successfully")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

# Factory function pour créer le gestionnaire
async def create_real_time_analytics_manager(
    config: Optional[RealTimeAnalyticsConfig] = None,
    redis_client: Optional[redis.Redis] = None
) -> RedisRealTimeAnalyticsManager:
    """Crée et initialise un gestionnaire d'analytics en temps réel"""
    
    if config is None:
        config = RealTimeAnalyticsConfig()
    
    manager = RedisRealTimeAnalyticsManager(config, redis_client)
    
    if await manager.initialize():
        return manager
    else:
        raise RuntimeError("Failed to initialize Real-Time Analytics Manager")

__all__ = [
    'RedisRealTimeAnalyticsManager',
    'RealTimeAnalyticsConfig',
    'AnalyticsEvent',
    'MetricDefinition',
    'AnalyticsResult',
    'AnalyticsAlert',
    'DashboardWidget',
    'AnalyticsType',
    'MetricType',
    'AggregationType',
    'AlertSeverity',
    'create_real_time_analytics_manager'
]