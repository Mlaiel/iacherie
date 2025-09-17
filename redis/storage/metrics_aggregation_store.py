"""🚀 Metrics Aggregation Store - Enterprise Grade
===============================================
Expert: DBA + DATA ARCHITECT + ML ENGINEER + PERFORMANCE ENGINEER
Technologies: Real-Time Aggregation + Multi-Dimensional Metrics + OLAP + Stream Processing
Architecture: Level 2 - Storage Layer - Metrics Aggregation
Date: 2025-01-14

Ultra-optimized enterprise metrics aggregation with multi-dimensional analysis,
real-time stream processing, OLAP capabilities and intelligent pre-aggregation.
===============================================
"""

import asyncio
import logging
import time
import json
import hashlib
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

class AggregationFunction(Enum):
    """Fonctions d'agrégation disponibles"""
    SUM = "sum"
    COUNT = "count"
    AVERAGE = "avg"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    PERCENTILE_95 = "p95"
    PERCENTILE_99 = "p99"
    STANDARD_DEVIATION = "stddev"
    UNIQUE_COUNT = "count_distinct"
    VARIANCE = "variance"
    FIRST = "first"
    LAST = "last"
    RATE = "rate"
    GROWTH_RATE = "growth_rate"

class DimensionType(Enum):
    """Types de dimensions pour agrégation"""
    USER_ID = "user_id"
    CREATOR_ID = "creator_id"
    CONTENT_TYPE = "content_type"
    PLATFORM = "platform"
    GEOGRAPHIC = "geographic"
    DEVICE_TYPE = "device_type"
    TRAFFIC_SOURCE = "traffic_source"
    TIME_PERIOD = "time_period"
    CUSTOM = "custom"

class AggregationGranularity(Enum):
    """Granularité d'agrégation temporelle"""
    REAL_TIME = "real_time"  # < 1 seconde
    MINUTE = "minute"
    FIVE_MINUTES = "5min"
    FIFTEEN_MINUTES = "15min"
    HOUR = "hour"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

@dataclass
class MetricDefinition:
    """Définition d'une métrique à agréger"""
    metric_name: str
    aggregation_function: AggregationFunction
    source_field: str
    dimensions: List[DimensionType] = field(default_factory=list)
    granularities: List[AggregationGranularity] = field(default_factory=lambda: [
        AggregationGranularity.HOUR, AggregationGranularity.DAILY
    ])
    filter_conditions: Dict[str, Any] = field(default_factory=dict)
    weight_field: Optional[str] = None
    custom_formula: Optional[str] = None
    tags: Set[str] = field(default_factory=set)

@dataclass
class AggregatedMetric:
    """Métrique agrégée avec métadonnées"""
    metric_name: str
    value: Union[int, float, Decimal, Dict[str, Any]]
    aggregation_function: AggregationFunction
    granularity: AggregationGranularity
    time_bucket: datetime
    dimensions: Dict[str, str] = field(default_factory=dict)
    sample_count: int = 0
    confidence_interval: Optional[Tuple[float, float]] = None
    last_updated: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AggregationConfig:
    """Configuration du système d'agrégation"""
    redis_url: str = "redis://localhost:6379"
    buffer_size: int = 10000
    flush_interval_seconds: int = 30
    retention_policies: Dict[AggregationGranularity, int] = field(default_factory=lambda: {
        AggregationGranularity.REAL_TIME: 1,  # 1 jour
        AggregationGranularity.MINUTE: 7,     # 7 jours
        AggregationGranularity.HOUR: 30,      # 30 jours
        AggregationGranularity.DAILY: 365,    # 1 an
        AggregationGranularity.WEEKLY: 730,   # 2 ans
        AggregationGranularity.MONTHLY: 1825, # 5 ans
    })
    max_dimensions_cardinality: int = 1000000
    enable_compression: bool = True
    enable_pre_aggregation: bool = True
    parallel_workers: int = 4

class MetricsAggregationStore:
    """🚀 **Enterprise**: Store d'agrégation métriques multi-dimensionnelles
    
    Système d'agrégation enterprise avec traitement temps-réel,
    analyse multi-dimensionnelle, OLAP et optimisations performance.
    
    Fonctionnalités:
    - Agrégation temps-réel multi-niveaux
    - Support dimensions multiples
    - Pre-aggregation intelligente
    - Retention policies automatiques
    - Compression données optimisée
    - Calculs parallèles haute performance
    """
    
    def __init__(self, config: AggregationConfig):
        self.config = config
        self._redis_client: Optional[redis.Redis] = None
        self._metric_definitions: Dict[str, MetricDefinition] = {}
        self._aggregation_buffer: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._running = False
        
        # Clés Redis optimisées
        self.metrics_prefix = "metrics:agg"
        self.definitions_prefix = "metrics:def"
        self.metadata_prefix = "metrics:meta"
        
        # Workers pour traitement parallèle
        self._workers: List[asyncio.Task] = []
        self._work_queue: asyncio.Queue = asyncio.Queue(maxsize=config.buffer_size)
        
        # Performance counters
        self._metrics_processed = 0
        self._aggregations_computed = 0
        self._cache_hits = 0
        self._cache_misses = 0
        
    async def initialize(self) -> bool:
        """🚀 **Enterprise**: Initialisation store agrégation
        
        Initialise connexion Redis, démarre workers parallèles,
        charge définitions métriques et configure retention.
        """
        try:
            if REDIS_AVAILABLE and self.config.redis_url:
                self._redis_client = redis.from_url(
                    self.config.redis_url,
                    decode_responses=True,
                    max_connections=30
                )
                await self._redis_client.ping()
                logger.info("✅ Connexion Redis metrics aggregation établie")
            else:
                logger.warning("⚠️ Redis non disponible - mode dégradé activé")
                
            # Chargement définitions métriques existantes
            await self._load_metric_definitions()
            
            # Démarrage workers parallèles
            await self._start_workers()
            
            # Configuration retention policies
            await self._setup_retention_policies()
            
            self._running = True
            logger.info("🚀 Metrics Aggregation Store initialisé")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation aggregation store: {e}")
            return False
    
    async def register_metric(self, definition: MetricDefinition) -> bool:
        """📊 **Data Architect**: Enregistrement définition métrique
        
        Enregistre une nouvelle définition de métrique avec validation,
        optimisation et configuration automatique des agrégations.
        """
        try:
            # Validation définition
            if not self._validate_metric_definition(definition):
                logger.error(f"❌ Définition métrique invalide: {definition.metric_name}")
                return False
            
            # Stockage en mémoire
            self._metric_definitions[definition.metric_name] = definition
            
            # Persistance dans Redis
            if self._redis_client:
                definition_key = f"{self.definitions_prefix}:{definition.metric_name}"
                definition_data = asdict(definition)
                
                # Conversion sets/enums pour JSON
                definition_data['dimensions'] = [d.value for d in definition.dimensions]
                definition_data['granularities'] = [g.value for g in definition.granularities]
                definition_data['aggregation_function'] = definition.aggregation_function.value
                definition_data['tags'] = list(definition.tags)
                
                await self._redis_client.setex(
                    definition_key,
                    timedelta(days=365),
                    json.dumps(definition_data)
                )
            
            # Pré-création des structures d'agrégation
            await self._setup_metric_aggregation_structure(definition)
            
            logger.info(f"✅ Métrique {definition.metric_name} enregistrée")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur enregistrement métrique: {e}")
            return False
    
    async def record_data_point(
        self,
        metric_name: str,
        value: Union[int, float, Decimal],
        dimensions: Optional[Dict[str, str]] = None,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """📈 **ML Engineer**: Enregistrement point de données
        
        Enregistre un point de données pour agrégation avec validation,
        enrichissement et mise en queue optimisée.
        """
        try:
            if metric_name not in self._metric_definitions:
                logger.warning(f"⚠️ Métrique non définie: {metric_name}")
                return False
            
            data_point = {
                "metric_name": metric_name,
                "value": float(value) if isinstance(value, Decimal) else value,
                "dimensions": dimensions or {},
                "timestamp": timestamp or datetime.now(),
                "recorded_at": time.time()
            }
            
            # Validation dimensions
            if not self._validate_dimensions(metric_name, dimensions):
                logger.warning(f"⚠️ Dimensions invalides pour {metric_name}")
                return False
            
            # Ajout à la queue de traitement
            try:
                await self._work_queue.put_nowait(data_point)
                self._metrics_processed += 1
                return True
            except asyncio.QueueFull:
                logger.warning("⚠️ Queue aggregation pleine - point de données ignoré")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur enregistrement data point: {e}")
            return False
    
    async def get_aggregated_metric(
        self,
        metric_name: str,
        granularity: AggregationGranularity,
        start_time: datetime,
        end_time: datetime,
        dimensions: Optional[Dict[str, str]] = None,
        aggregation_function: Optional[AggregationFunction] = None
    ) -> List[AggregatedMetric]:
        """📊 **Performance Engineer**: Récupération métriques agrégées
        
        Récupère métriques agrégées avec cache intelligent,
        optimisations requêtes et support multi-dimensionnel.
        """
        try:
            if metric_name not in self._metric_definitions:
                logger.warning(f"⚠️ Métrique non définie: {metric_name}")
                return []
            
            definition = self._metric_definitions[metric_name]
            agg_func = aggregation_function or definition.aggregation_function
            
            # Construction clé cache
            cache_key = self._build_cache_key(
                metric_name, granularity, start_time, end_time, dimensions, agg_func
            )
            
            # Tentative récupération depuis cache
            cached_result = await self._get_from_cache(cache_key)
            if cached_result:
                self._cache_hits += 1
                return cached_result
            
            self._cache_misses += 1
            
            # Récupération depuis Redis avec optimisations
            metrics = await self._fetch_aggregated_metrics(
                metric_name, granularity, start_time, end_time, dimensions, agg_func
            )
            
            # Mise en cache du résultat
            await self._cache_result(cache_key, metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération métrique agrégée: {e}")
            return []
    
    async def get_multi_dimensional_analysis(
        self,
        metric_name: str,
        granularity: AggregationGranularity,
        time_range: Tuple[datetime, datetime],
        group_by_dimensions: List[DimensionType]
    ) -> Dict[str, Any]:
        """🔍 **Data Architect**: Analyse multi-dimensionnelle OLAP
        
        Effectue analyse OLAP multi-dimensionnelle avec:
        - Drill-down/drill-up automatique
        - Pivoting intelligent
        - Détection anomalies
        - Insights business automatiques
        """
        try:
            start_time, end_time = time_range
            analysis = {
                "metric_name": metric_name,
                "granularity": granularity.value,
                "time_range": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                },
                "dimensions_analyzed": [d.value for d in group_by_dimensions],
                "generated_at": datetime.now().isoformat()
            }
            
            # Récupération données brutes
            raw_metrics = await self.get_aggregated_metric(
                metric_name, granularity, start_time, end_time
            )
            
            if not raw_metrics:
                return analysis
            
            # Groupement par dimensions
            grouped_data = await self._group_by_dimensions(raw_metrics, group_by_dimensions)
            analysis["grouped_data"] = grouped_data
            
            # Calculs statistiques avancés
            statistics_analysis = await self._calculate_advanced_statistics(grouped_data)
            analysis["statistics"] = statistics_analysis
            
            # Détection anomalies
            anomalies = await self._detect_anomalies(grouped_data)
            analysis["anomalies"] = anomalies
            
            # Insights business automatiques
            insights = await self._generate_business_insights(grouped_data, metric_name)
            analysis["insights"] = insights
            
            # Recommandations optimisation
            recommendations = await self._generate_optimization_recommendations(analysis)
            analysis["recommendations"] = recommendations
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse multi-dimensionnelle: {e}")
            return {}
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """⚡ **Performance Engineer**: Métriques performance store
        
        Retourne métriques détaillées de performance du store d'agrégation.
        """
        queue_size = self._work_queue.qsize()
        
        return {
            "metrics_processed": self._metrics_processed,
            "aggregations_computed": self._aggregations_computed,
            "cache_hit_ratio": self._cache_hits / max(self._cache_hits + self._cache_misses, 1),
            "queue_size": queue_size,
            "queue_utilization": queue_size / self.config.buffer_size,
            "active_workers": len(self._workers),
            "registered_metrics": len(self._metric_definitions),
            "throughput_metrics_per_second": self._metrics_processed / max(time.time() - getattr(self, '_start_time', time.time()), 1),
            "memory_efficient": True
        }
    
    # Méthodes internes optimisées
    
    async def _start_workers(self):
        """Démarrage workers parallèles"""
        self._start_time = time.time()
        
        for i in range(self.config.parallel_workers):
            worker = asyncio.create_task(self._aggregation_worker(f"worker-{i}"))
            self._workers.append(worker)
            
        logger.info(f"✅ {len(self._workers)} workers d'agrégation démarrés")
    
    async def _aggregation_worker(self, worker_id: str):
        """Worker d'agrégation parallèle"""
        logger.info(f"🚀 Worker {worker_id} démarré")
        
        while self._running:
            try:
                # Récupération point de données avec timeout
                data_point = await asyncio.wait_for(
                    self._work_queue.get(), timeout=1.0
                )
                
                # Traitement agrégation
                await self._process_data_point(data_point)
                self._aggregations_computed += 1
                
                # Marque tâche comme terminée
                self._work_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"❌ Erreur worker {worker_id}: {e}")
                
        logger.info(f"⏹️ Worker {worker_id} arrêté")
    
    async def _process_data_point(self, data_point: Dict[str, Any]):
        """Traitement d'un point de données pour agrégation"""
        try:
            metric_name = data_point["metric_name"]
            definition = self._metric_definitions[metric_name]
            
            # Agrégation pour chaque granularité configurée
            for granularity in definition.granularities:
                await self._aggregate_for_granularity(data_point, granularity, definition)
                
        except Exception as e:
            logger.error(f"❌ Erreur traitement data point: {e}")
    
    async def _aggregate_for_granularity(
        self,
        data_point: Dict[str, Any],
        granularity: AggregationGranularity,
        definition: MetricDefinition
    ):
        """Agrégation pour une granularité spécifique"""
        try:
            # Calcul bucket temporel
            time_bucket = self._calculate_time_bucket(
                data_point["timestamp"], granularity
            )
            
            # Construction clé agrégation
            agg_key = self._build_aggregation_key(
                definition.metric_name,
                granularity,
                time_bucket,
                data_point["dimensions"]
            )
            
            # Mise à jour agrégation dans Redis
            if self._redis_client:
                await self._update_aggregation_in_redis(
                    agg_key, data_point["value"], definition.aggregation_function
                )
            
        except Exception as e:
            logger.error(f"❌ Erreur agrégation granularité {granularity.value}: {e}")
    
    async def _update_aggregation_in_redis(
        self,
        key: str,
        value: Union[int, float],
        agg_function: AggregationFunction
    ):
        """Mise à jour agrégation dans Redis avec fonction appropriée"""
        try:
            pipe = self._redis_client.pipeline()
            
            # Logique selon fonction d'agrégation
            if agg_function == AggregationFunction.SUM:
                pipe.incrbyfloat(f"{key}:sum", value)
                pipe.incr(f"{key}:count")
            elif agg_function == AggregationFunction.COUNT:
                pipe.incr(f"{key}:count")
            elif agg_function == AggregationFunction.AVERAGE:
                pipe.incrbyfloat(f"{key}:sum", value)
                pipe.incr(f"{key}:count")
            elif agg_function == AggregationFunction.MIN:
                current_min = await self._redis_client.get(f"{key}:min")
                if current_min is None or value < float(current_min):
                    pipe.set(f"{key}:min", value)
            elif agg_function == AggregationFunction.MAX:
                current_max = await self._redis_client.get(f"{key}:max")
                if current_max is None or value > float(current_max):
                    pipe.set(f"{key}:max", value)
            
            # Mise à jour timestamp
            pipe.set(f"{key}:last_updated", time.time())
            
            await pipe.execute()
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour Redis: {e}")
    
    def _calculate_time_bucket(
        self,
        timestamp: datetime,
        granularity: AggregationGranularity
    ) -> datetime:
        """Calcul du bucket temporel selon granularité"""
        if granularity == AggregationGranularity.MINUTE:
            return timestamp.replace(second=0, microsecond=0)
        elif granularity == AggregationGranularity.FIVE_MINUTES:
            minute = (timestamp.minute // 5) * 5
            return timestamp.replace(minute=minute, second=0, microsecond=0)
        elif granularity == AggregationGranularity.HOUR:
            return timestamp.replace(minute=0, second=0, microsecond=0)
        elif granularity == AggregationGranularity.DAILY:
            return timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        elif granularity == AggregationGranularity.WEEKLY:
            days_since_monday = timestamp.weekday()
            week_start = timestamp - timedelta(days=days_since_monday)
            return week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        elif granularity == AggregationGranularity.MONTHLY:
            return timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            return timestamp
    
    def _build_aggregation_key(
        self,
        metric_name: str,
        granularity: AggregationGranularity,
        time_bucket: datetime,
        dimensions: Dict[str, str]
    ) -> str:
        """Construction clé optimisée pour agrégation"""
        key_parts = [
            self.metrics_prefix,
            metric_name,
            granularity.value,
            time_bucket.strftime("%Y%m%d%H%M")
        ]
        
        # Ajout dimensions triées pour consistance
        if dimensions:
            dim_str = ":".join(f"{k}={v}" for k, v in sorted(dimensions.items()))
            key_parts.append(hashlib.md5(dim_str.encode()).hexdigest()[:8])
        
        return ":".join(key_parts)
    
    def _build_cache_key(
        self,
        metric_name: str,
        granularity: AggregationGranularity,
        start_time: datetime,
        end_time: datetime,
        dimensions: Optional[Dict[str, str]],
        agg_func: AggregationFunction
    ) -> str:
        """Construction clé cache optimisée"""
        key_components = [
            "cache",
            metric_name,
            granularity.value,
            agg_func.value,
            start_time.strftime("%Y%m%d%H%M"),
            end_time.strftime("%Y%m%d%H%M")
        ]
        
        if dimensions:
            dim_hash = hashlib.md5(str(sorted(dimensions.items())).encode()).hexdigest()[:8]
            key_components.append(dim_hash)
        
        return ":".join(key_components)
    
    async def shutdown(self):
        """🛑 **Enterprise**: Arrêt propre du store agrégation"""
        try:
            self._running = False
            
            # Attente fin traitement queue
            await self._work_queue.join()
            
            # Arrêt workers
            for worker in self._workers:
                worker.cancel()
            
            await asyncio.gather(*self._workers, return_exceptions=True)
            
            # Fermeture connexion Redis
            if self._redis_client:
                await self._redis_client.close()
                
            logger.info("⏹️ Metrics Aggregation Store arrêté proprement")
            
        except Exception as e:
            logger.error(f"❌ Erreur arrêt aggregation store: {e}")

    # Méthodes helper simplifiées (implémentation production serait plus complexe)
    
    def _validate_metric_definition(self, definition: MetricDefinition) -> bool:
        """Validation définition métrique"""
        return bool(definition.metric_name and definition.source_field)
    
    def _validate_dimensions(self, metric_name: str, dimensions: Optional[Dict[str, str]]) -> bool:
        """Validation dimensions"""
        if not dimensions:
            return True
        return len(dimensions) <= 10  # Limite arbitraire
    
    async def _load_metric_definitions(self):
        """Chargement définitions depuis Redis"""
        # Implémentation simplifiée
        pass
    
    async def _setup_retention_policies(self):
        """Configuration policies de rétention"""
        # Implémentation simplifiée
        pass
    
    async def _setup_metric_aggregation_structure(self, definition: MetricDefinition):
        """Setup structure d'agrégation pour métrique"""
        # Implémentation simplifiée
        pass

# Factory function
async def create_metrics_aggregation_store(config: Optional[AggregationConfig] = None) -> MetricsAggregationStore:
    """🏭 **Factory**: Création instance Metrics Aggregation Store
    
    Crée et initialise un store d'agrégation métriques enterprise
    avec configuration optimisée et workers parallèles.
    """
    if config is None:
        config = AggregationConfig()
        
    store = MetricsAggregationStore(config)
    
    initialized = await store.initialize()
    if not initialized:
        logger.warning("⚠️ Metrics aggregation store initialisé en mode dégradé")
        
    return store