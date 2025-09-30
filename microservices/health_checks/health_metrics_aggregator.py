"""
Health Metrics Aggregator - IA Chérie Health Checks Module
Agrégateur métriques santé avec time-series aggregation, statistical analysis,
business intelligence et real-time metrics processing.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture health checks et tous ses patterns sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel. Toute reproduction, modification, distribution ou vol 
d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor
import time

logger = logging.getLogger(__name__)

class AggregationType(Enum):
    """Types d'agrégation métriques"""
    AVERAGE = "average"
    SUM = "sum"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE = "percentile"
    MEDIAN = "median"
    STANDARD_DEVIATION = "std_dev"
    RATE = "rate"
    DELTA = "delta"

class TimeWindow(Enum):
    """Fenêtres temporelles agrégation"""
    MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    HOUR = "1h"
    DAY = "1d"
    WEEK = "1w"
    MONTH = "1M"

class MetricType(Enum):
    """Types de métriques health"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    RATE = "rate"
    BUSINESS = "business"

@dataclass
class HealthMetric:
    """Métrique santé individuelle"""
    name: str
    value: Union[float, int]
    timestamp: datetime
    service_name: str
    metric_type: MetricType
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AggregatedMetric:
    """Métrique agrégée"""
    name: str
    aggregation_type: AggregationType
    value: float
    time_window: TimeWindow
    window_start: datetime
    window_end: datetime
    service_name: str
    sample_count: int
    confidence: float = 1.0
    percentile: Optional[int] = None

@dataclass
class AggregatorConfig:
    """Configuration agrégateur métriques"""
    max_metrics_in_memory: int = 100000
    aggregation_interval_seconds: int = 60
    retention_hours: int = 168  # 7 days
    enable_real_time_aggregation: bool = True
    batch_size: int = 1000
    parallel_processing: bool = True
    max_workers: int = 4
    percentiles: List[int] = field(default_factory=lambda: [50, 75, 90, 95, 99])

@dataclass
class BusinessMetric:
    """Métrique business intelligence"""
    metric_name: str
    business_value: float
    impact_score: float
    trend_direction: str
    anomaly_score: float
    recommendations: List[str]
    business_context: Dict[str, Any]

class MetricsStorage:
    """Stockage optimisé métriques time-series"""
    
    def __init__(self, max_metrics: int):
        self.max_metrics = max_metrics
        
        # Stockage par service et métrique
        self.raw_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.aggregated_metrics: Dict[str, Dict[TimeWindow, deque]] = defaultdict(
            lambda: {window: deque(maxlen=1000) for window in TimeWindow}
        )
        
        # Index temporel pour recherche rapide
        self.time_index: Dict[str, List[Tuple[datetime, int]]] = defaultdict(list)
        
        # Cache agrégations fréquentes
        self.aggregation_cache: Dict[str, Tuple[datetime, Any]] = {}
        self.cache_ttl_seconds = 60
        
    def store_metric(self, metric: HealthMetric):
        """Stocker métrique raw"""
        metric_key = f"{metric.service_name}:{metric.name}"
        self.raw_metrics[metric_key].append(metric)
        
        # Maintenir index temporel
        if len(self.time_index[metric_key]) > 1000:
            self.time_index[metric_key] = self.time_index[metric_key][-500:]  # Keep last 500
            
        self.time_index[metric_key].append((metric.timestamp, len(self.raw_metrics[metric_key]) - 1))
        
    def store_aggregated_metric(self, metric: AggregatedMetric):
        """Stocker métrique agrégée"""
        metric_key = f"{metric.service_name}:{metric.name}"
        self.aggregated_metrics[metric_key][metric.time_window].append(metric)
        
    def get_metrics_in_range(self, service_name: str, metric_name: str, 
                           start_time: datetime, end_time: datetime) -> List[HealthMetric]:
        """Récupérer métriques dans plage temporelle"""
        metric_key = f"{service_name}:{metric_name}"
        
        if metric_key not in self.raw_metrics:
            return []
            
        # Utiliser index temporel pour recherche efficace
        result_metrics = []
        for timestamp, index in self.time_index[metric_key]:
            if start_time <= timestamp <= end_time:
                if index < len(self.raw_metrics[metric_key]):
                    result_metrics.append(self.raw_metrics[metric_key][index])
                    
        return result_metrics
        
    def get_aggregated_metrics(self, service_name: str, metric_name: str, 
                             time_window: TimeWindow, 
                             start_time: datetime, end_time: datetime) -> List[AggregatedMetric]:
        """Récupérer métriques agrégées"""
        metric_key = f"{service_name}:{metric_name}"
        
        if metric_key not in self.aggregated_metrics:
            return []
            
        result_metrics = []
        for aggregated_metric in self.aggregated_metrics[metric_key][time_window]:
            if (start_time <= aggregated_metric.window_start <= end_time or
                start_time <= aggregated_metric.window_end <= end_time):
                result_metrics.append(aggregated_metric)
                
        return result_metrics
        
    def cleanup_old_metrics(self, retention_hours: int):
        """Nettoyer anciennes métriques"""
        cutoff_time = datetime.now() - timedelta(hours=retention_hours)
        
        # Nettoyer métriques raw
        for metric_key in self.raw_metrics:
            while (self.raw_metrics[metric_key] and 
                   self.raw_metrics[metric_key][0].timestamp < cutoff_time):
                self.raw_metrics[metric_key].popleft()
                
        # Nettoyer index temporel
        for metric_key in self.time_index:
            self.time_index[metric_key] = [
                (ts, idx) for ts, idx in self.time_index[metric_key] 
                if ts >= cutoff_time
            ]

class StatisticalProcessor:
    """Processeur statistiques avancées"""
    
    @staticmethod
    def calculate_percentile(values: List[float], percentile: int) -> float:
        """Calculer percentile"""
        if not values:
            return 0.0
        return np.percentile(values, percentile)
        
    @staticmethod
    def calculate_moving_average(values: List[float], window_size: int) -> List[float]:
        """Calculer moyenne mobile"""
        if len(values) < window_size:
            return values
            
        moving_averages = []
        for i in range(window_size - 1, len(values)):
            window_avg = sum(values[i - window_size + 1:i + 1]) / window_size
            moving_averages.append(window_avg)
            
        return moving_averages
        
    @staticmethod
    def detect_outliers(values: List[float], method: str = 'iqr') -> List[int]:
        """Détecter outliers"""
        if len(values) < 4:
            return []
            
        if method == 'iqr':
            q1 = np.percentile(values, 25)
            q3 = np.percentile(values, 75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = []
            for i, value in enumerate(values):
                if value < lower_bound or value > upper_bound:
                    outliers.append(i)
                    
            return outliers
            
        elif method == 'zscore':
            mean_val = np.mean(values)
            std_val = np.std(values)
            
            outliers = []
            for i, value in enumerate(values):
                zscore = abs((value - mean_val) / std_val) if std_val > 0 else 0
                if zscore > 3:  # 3-sigma rule
                    outliers.append(i)
                    
            return outliers
            
        return []
        
    @staticmethod
    def calculate_correlation(series1: List[float], series2: List[float]) -> float:
        """Calculer corrélation entre deux séries"""
        if len(series1) != len(series2) or len(series1) < 2:
            return 0.0
            
        return float(np.corrcoef(series1, series2)[0, 1]) if not np.isnan(np.corrcoef(series1, series2)[0, 1]) else 0.0
        
    @staticmethod
    def calculate_seasonality_strength(values: List[float], period: int = 24) -> float:
        """Calculer force saisonnalité"""
        if len(values) < period * 2:
            return 0.0
            
        # Décomposition simple trend vs seasonal
        seasonal_values = []
        for i in range(period, len(values)):
            seasonal_component = values[i] - values[i - period]
            seasonal_values.append(abs(seasonal_component))
            
        if not seasonal_values:
            return 0.0
            
        seasonality_strength = np.mean(seasonal_values) / (np.std(values) + 1e-6)
        return min(1.0, seasonality_strength)

class HealthMetricsAggregator:
    """
    Agrégateur métriques santé enterprise.
    Time-series aggregation + statistical analysis + business intelligence + real-time processing.
    
    Features:
    - Multi-level time-series aggregation
    - Statistical analysis avancée (percentiles, outliers, correlation)
    - Business intelligence metrics
    - Real-time aggregation en streaming
    - Parallel processing pour performance
    - Caching intelligent pour queries fréquentes
    """
    
    def __init__(self, aggregator_config: AggregatorConfig):
        self.aggregator_config = aggregator_config
        self.storage = MetricsStorage(aggregator_config.max_metrics_in_memory)
        self.statistical_processor = StatisticalProcessor()
        
        # Thread pool pour parallel processing
        self.executor = ThreadPoolExecutor(max_workers=aggregator_config.max_workers) if aggregator_config.parallel_processing else None
        
        # Real-time aggregation
        self.real_time_enabled = aggregator_config.enable_real_time_aggregation
        self.aggregation_thread = None
        self.stop_aggregation = threading.Event()
        
        # Métriques business
        self.business_metrics: Dict[str, BusinessMetric] = {}
        
        # Stats agrégateur
        self.aggregator_stats = {
            'total_metrics_processed': 0,
            'aggregations_computed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'processing_time_ms': 0.0,
            'errors': 0
        }
        
        # Démarrer agrégation temps réel
        if self.real_time_enabled:
            self.start_real_time_aggregation()
            
    def start_real_time_aggregation(self):
        """Démarrer agrégation temps réel"""
        if self.aggregation_thread and self.aggregation_thread.is_alive():
            return
            
        self.stop_aggregation.clear()
        self.aggregation_thread = threading.Thread(target=self._real_time_aggregation_loop)
        self.aggregation_thread.daemon = True
        self.aggregation_thread.start()
        
        logger.info("Started real-time metrics aggregation")
        
    def stop_real_time_aggregation(self):
        """Arrêter agrégation temps réel"""
        if self.aggregation_thread:
            self.stop_aggregation.set()
            self.aggregation_thread.join(timeout=5)
            
        logger.info("Stopped real-time metrics aggregation")
        
    async def ingest_metric(self, metric: HealthMetric):
        """Ingérer nouvelle métrique health"""
        try:
            self.storage.store_metric(metric)
            self.aggregator_stats['total_metrics_processed'] += 1
            
            # Déclencher agrégation immédiate pour métriques critiques
            if 'critical' in metric.labels.values():
                await self._trigger_immediate_aggregation(metric)
                
        except Exception as e:
            logger.error(f"Failed to ingest metric {metric.name}: {e}")
            self.aggregator_stats['errors'] += 1
            
    async def ingest_metrics_batch(self, metrics: List[HealthMetric]):
        """Ingérer batch de métriques"""
        try:
            for metric in metrics:
                self.storage.store_metric(metric)
                
            self.aggregator_stats['total_metrics_processed'] += len(metrics)
            
        except Exception as e:
            logger.error(f"Failed to ingest metrics batch: {e}")
            self.aggregator_stats['errors'] += 1
            
    async def aggregate_metrics(self, service_name: str, metric_name: str,
                              aggregation_type: AggregationType,
                              time_window: TimeWindow,
                              start_time: datetime = None,
                              end_time: datetime = None) -> List[AggregatedMetric]:
        """
        Agréger métriques selon paramètres.
        
        Args:
            service_name: Nom du service
            metric_name: Nom de la métrique
            aggregation_type: Type d'agrégation
            time_window: Fenêtre temporelle
            start_time: Début période (défaut: dernière heure)
            end_time: Fin période (défaut: maintenant)
            
        Returns:
            Liste métriques agrégées
        """
        aggregation_start = time.time()
        
        try:
            # Paramètres par défaut
            if end_time is None:
                end_time = datetime.now()
            if start_time is None:
                start_time = end_time - timedelta(hours=1)
                
            # Vérifier cache
            cache_key = f"{service_name}:{metric_name}:{aggregation_type.value}:{time_window.value}:{start_time}:{end_time}"
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                self.aggregator_stats['cache_hits'] += 1
                return cached_result
                
            self.aggregator_stats['cache_misses'] += 1
            
            # Récupérer métriques raw
            raw_metrics = self.storage.get_metrics_in_range(service_name, metric_name, start_time, end_time)
            
            if not raw_metrics:
                return []
                
            # Calculer fenêtres temporelles
            window_duration = self._get_window_duration(time_window)
            aggregated_metrics = []
            
            current_window_start = start_time
            while current_window_start < end_time:
                current_window_end = min(current_window_start + window_duration, end_time)
                
                # Filtrer métriques pour cette fenêtre
                window_metrics = [
                    m for m in raw_metrics 
                    if current_window_start <= m.timestamp < current_window_end
                ]
                
                if window_metrics:
                    # Calculer agrégation
                    aggregated_value = await self._calculate_aggregation(
                        window_metrics, aggregation_type
                    )
                    
                    aggregated_metric = AggregatedMetric(
                        name=metric_name,
                        aggregation_type=aggregation_type,
                        value=aggregated_value,
                        time_window=time_window,
                        window_start=current_window_start,
                        window_end=current_window_end,
                        service_name=service_name,
                        sample_count=len(window_metrics),
                        confidence=min(1.0, len(window_metrics) / 10.0)  # Confidence basée sur échantillon
                    )
                    
                    aggregated_metrics.append(aggregated_metric)
                    
                current_window_start = current_window_end
                
            # Stocker en cache
            self._store_in_cache(cache_key, aggregated_metrics)
            
            # Stocker métriques agrégées
            for agg_metric in aggregated_metrics:
                self.storage.store_aggregated_metric(agg_metric)
                
            self.aggregator_stats['aggregations_computed'] += len(aggregated_metrics)
            
            return aggregated_metrics
            
        except Exception as e:
            logger.error(f"Metrics aggregation failed: {e}")
            self.aggregator_stats['errors'] += 1
            return []
            
        finally:
            processing_time = (time.time() - aggregation_start) * 1000
            self.aggregator_stats['processing_time_ms'] += processing_time
            
    async def compute_statistical_summary(self, service_name: str, metric_name: str,
                                        time_range_hours: int = 24) -> Dict[str, Any]:
        """Calculer synthèse statistique complète"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=time_range_hours)
        
        raw_metrics = self.storage.get_metrics_in_range(service_name, metric_name, start_time, end_time)
        
        if not raw_metrics:
            return {'error': 'No metrics found for specified range'}
            
        values = [m.value for m in raw_metrics]
        
        # Statistiques de base
        basic_stats = {
            'count': len(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'min': min(values),
            'max': max(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0,
            'variance': statistics.variance(values) if len(values) > 1 else 0.0
        }
        
        # Percentiles
        percentiles = {}
        for p in self.aggregator_config.percentiles:
            percentiles[f'p{p}'] = self.statistical_processor.calculate_percentile(values, p)
            
        # Détection outliers
        outliers_iqr = self.statistical_processor.detect_outliers(values, 'iqr')
        outliers_zscore = self.statistical_processor.detect_outliers(values, 'zscore')
        
        # Moyenne mobile
        moving_avg = self.statistical_processor.calculate_moving_average(values, min(10, len(values) // 4))
        
        # Saisonnalité
        seasonality_strength = self.statistical_processor.calculate_seasonality_strength(values)
        
        return {
            'metric_name': metric_name,
            'service_name': service_name,
            'time_range_hours': time_range_hours,
            'basic_statistics': basic_stats,
            'percentiles': percentiles,
            'outliers': {
                'iqr_method': len(outliers_iqr),
                'zscore_method': len(outliers_zscore),
                'outlier_ratio': len(outliers_iqr) / len(values) if values else 0
            },
            'trend_analysis': {
                'moving_average_last_points': moving_avg[-5:] if len(moving_avg) >= 5 else moving_avg,
                'seasonality_strength': seasonality_strength,
                'trend_direction': self._determine_trend_direction(values)
            }
        }
        
    async def generate_business_intelligence(self, services: List[str] = None) -> Dict[str, Any]:
        """Générer business intelligence métriques"""
        if services is None:
            # Extraire tous les services des métriques
            services = list(set(
                key.split(':')[0] for key in self.storage.raw_metrics.keys()
            ))
            
        business_insights = {
            'analysis_timestamp': datetime.now().isoformat(),
            'services_analyzed': len(services),
            'service_insights': {},
            'cross_service_analysis': {},
            'recommendations': []
        }
        
        for service_name in services:
            service_insights = await self._analyze_service_business_metrics(service_name)
            business_insights['service_insights'][service_name] = service_insights
            
        # Analyse cross-service
        if len(services) > 1:
            cross_analysis = await self._analyze_cross_service_correlations(services)
            business_insights['cross_service_analysis'] = cross_analysis
            
        # Recommandations globales
        recommendations = await self._generate_business_recommendations(business_insights)
        business_insights['recommendations'] = recommendations
        
        return business_insights
        
    async def get_real_time_metrics_summary(self) -> Dict[str, Any]:
        """Obtenir synthèse métriques temps réel"""
        return {
            'aggregator_stats': self.aggregator_stats.copy(),
            'storage_stats': {
                'raw_metrics_count': sum(len(deque_) for deque_ in self.storage.raw_metrics.values()),
                'aggregated_metrics_count': sum(
                    sum(len(window_deque) for window_deque in time_windows.values())
                    for time_windows in self.storage.aggregated_metrics.values()
                ),
                'cache_size': len(self.storage.aggregation_cache)
            },
            'business_metrics_count': len(self.business_metrics),
            'real_time_aggregation_active': self.real_time_enabled and (
                self.aggregation_thread and self.aggregation_thread.is_alive()
            )
        }
        
    # Méthodes utilitaires
    
    def _real_time_aggregation_loop(self):
        """Boucle agrégation temps réel"""
        while not self.stop_aggregation.is_set():
            try:
                # Exécuter agrégations automatiques
                asyncio.run(self._perform_automated_aggregations())
                
                # Nettoyer ancien cache
                self._cleanup_cache()
                
                # Nettoyer anciennes métriques
                self.storage.cleanup_old_metrics(self.aggregator_config.retention_hours)
                
                # Attendre avant prochaine itération
                self.stop_aggregation.wait(self.aggregator_config.aggregation_interval_seconds)
                
            except Exception as e:
                logger.error(f"Real-time aggregation error: {e}")
                self.stop_aggregation.wait(10)  # Wait 10s on error
                
    async def _perform_automated_aggregations(self):
        """Effectuer agrégations automatiques"""
        # Identifier métriques nécessitant agrégation
        current_time = datetime.now()
        
        for metric_key in list(self.storage.raw_metrics.keys()):
            if not self.storage.raw_metrics[metric_key]:
                continue
                
            service_name, metric_name = metric_key.split(':', 1)
            
            # Latest metric timestamp
            latest_metric = self.storage.raw_metrics[metric_key][-1]
            
            # Si métrique récente, agréger fenêtres courtes
            if (current_time - latest_metric.timestamp).total_seconds() < 300:  # 5 minutes
                try:
                    # Agrégation 1 minute
                    await self.aggregate_metrics(
                        service_name, metric_name, 
                        AggregationType.AVERAGE, TimeWindow.MINUTE,
                        current_time - timedelta(minutes=5), current_time
                    )
                except Exception as e:
                    logger.error(f"Automated aggregation failed for {metric_key}: {e}")
                    
    async def _trigger_immediate_aggregation(self, metric: HealthMetric):
        """Déclencher agrégation immédiate pour métrique critique"""
        try:
            current_time = datetime.now()
            await self.aggregate_metrics(
                metric.service_name, metric.name,
                AggregationType.AVERAGE, TimeWindow.MINUTE,
                current_time - timedelta(minutes=1), current_time
            )
        except Exception as e:
            logger.error(f"Immediate aggregation failed: {e}")
            
    async def _calculate_aggregation(self, metrics: List[HealthMetric], 
                                   aggregation_type: AggregationType) -> float:
        """Calculer valeur agrégée"""
        values = [m.value for m in metrics]
        
        if aggregation_type == AggregationType.AVERAGE:
            return statistics.mean(values)
        elif aggregation_type == AggregationType.SUM:
            return sum(values)
        elif aggregation_type == AggregationType.MIN:
            return min(values)
        elif aggregation_type == AggregationType.MAX:
            return max(values)
        elif aggregation_type == AggregationType.COUNT:
            return len(values)
        elif aggregation_type == AggregationType.MEDIAN:
            return statistics.median(values)
        elif aggregation_type == AggregationType.STANDARD_DEVIATION:
            return statistics.stdev(values) if len(values) > 1 else 0.0
        elif aggregation_type == AggregationType.RATE:
            # Calculer taux (changement par seconde)
            if len(metrics) < 2:
                return 0.0
            time_diff = (metrics[-1].timestamp - metrics[0].timestamp).total_seconds()
            value_diff = metrics[-1].value - metrics[0].value
            return value_diff / time_diff if time_diff > 0 else 0.0
        elif aggregation_type == AggregationType.DELTA:
            # Changement entre première et dernière valeur
            return metrics[-1].value - metrics[0].value if len(metrics) >= 2 else 0.0
        else:
            return statistics.mean(values)  # Default to average
            
    def _get_window_duration(self, time_window: TimeWindow) -> timedelta:
        """Obtenir durée fenêtre temporelle"""
        durations = {
            TimeWindow.MINUTE: timedelta(minutes=1),
            TimeWindow.FIVE_MINUTES: timedelta(minutes=5),
            TimeWindow.FIFTEEN_MINUTES: timedelta(minutes=15),
            TimeWindow.HOUR: timedelta(hours=1),
            TimeWindow.DAY: timedelta(days=1),
            TimeWindow.WEEK: timedelta(weeks=1),
            TimeWindow.MONTH: timedelta(days=30)
        }
        return durations.get(time_window, timedelta(minutes=5))
        
    def _get_from_cache(self, cache_key: str) -> Optional[List[AggregatedMetric]]:
        """Récupérer du cache"""
        if cache_key in self.storage.aggregation_cache:
            cached_time, cached_data = self.storage.aggregation_cache[cache_key]
            if (datetime.now() - cached_time).total_seconds() < self.storage.cache_ttl_seconds:
                return cached_data
        return None
        
    def _store_in_cache(self, cache_key: str, data: List[AggregatedMetric]):
        """Stocker en cache"""
        self.storage.aggregation_cache[cache_key] = (datetime.now(), data)
        
    def _cleanup_cache(self):
        """Nettoyer ancien cache"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, (cached_time, _) in self.storage.aggregation_cache.items():
            if (current_time - cached_time).total_seconds() > self.storage.cache_ttl_seconds:
                expired_keys.append(key)
                
        for key in expired_keys:
            del self.storage.aggregation_cache[key]
            
    def _determine_trend_direction(self, values: List[float]) -> str:
        """Déterminer direction tendance"""
        if len(values) < 5:
            return "insufficient_data"
            
        # Comparer première moitié vs seconde moitié
        mid_point = len(values) // 2
        first_half_avg = statistics.mean(values[:mid_point])
        second_half_avg = statistics.mean(values[mid_point:])
        
        change_ratio = (second_half_avg - first_half_avg) / first_half_avg if first_half_avg != 0 else 0
        
        if abs(change_ratio) < 0.05:  # Less than 5% change
            return "stable"
        elif change_ratio > 0:
            return "increasing"
        else:
            return "decreasing"
            
    async def _analyze_service_business_metrics(self, service_name: str) -> Dict[str, Any]:
        """Analyser métriques business d'un service"""
        insights = {
            'service_name': service_name,
            'health_score': 0.0,
            'performance_rating': 'unknown',
            'availability_percentage': 0.0,
            'key_metrics': {},
            'issues': [],
            'strengths': []
        }
        
        # Analyser métriques clés du service
        key_metrics = ['response_time_ms', 'error_rate_percent', 'cpu_utilization', 'memory_utilization']
        
        metric_scores = []
        for metric_name in key_metrics:
            try:
                stats = await self.compute_statistical_summary(service_name, metric_name, 24)
                if 'basic_statistics' in stats:
                    basic_stats = stats['basic_statistics']
                    insights['key_metrics'][metric_name] = basic_stats
                    
                    # Scorer selon type métrique
                    if metric_name == 'response_time_ms':
                        score = max(0, 1 - (basic_stats['mean'] / 1000))  # Lower is better
                    elif metric_name == 'error_rate_percent':
                        score = max(0, 1 - (basic_stats['mean'] / 10))  # Lower is better
                    else:  # Utilization metrics
                        score = 1 - abs(basic_stats['mean'] - 50) / 50  # 50% is optimal
                    
                    metric_scores.append(score)
                    
            except Exception as e:
                logger.error(f"Failed to analyze {metric_name} for {service_name}: {e}")
                
        # Calculer health score global
        if metric_scores:
            insights['health_score'] = statistics.mean(metric_scores)
            
            if insights['health_score'] >= 0.8:
                insights['performance_rating'] = 'excellent'
            elif insights['health_score'] >= 0.6:
                insights['performance_rating'] = 'good'
            elif insights['health_score'] >= 0.4:
                insights['performance_rating'] = 'fair'
            else:
                insights['performance_rating'] = 'poor'
                
        return insights
        
    async def _analyze_cross_service_correlations(self, services: List[str]) -> Dict[str, Any]:
        """Analyser corrélations cross-service"""
        correlations = {}
        
        # Comparer services par paires
        for i, service1 in enumerate(services):
            for service2 in services[i+1:]:
                try:
                    correlation = await self._calculate_service_correlation(service1, service2)
                    if abs(correlation) > 0.5:  # Significant correlation
                        correlations[f"{service1}_vs_{service2}"] = correlation
                except Exception as e:
                    logger.error(f"Cross-service correlation failed: {e}")
                    
        return {
            'significant_correlations': correlations,
            'total_pairs_analyzed': len(services) * (len(services) - 1) // 2,
            'correlation_insights': self._interpret_correlations(correlations)
        }
        
    async def _calculate_service_correlation(self, service1: str, service2: str) -> float:
        """Calculer corrélation entre deux services"""
        # Utiliser métrique response_time comme proxy
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        metrics1 = self.storage.get_metrics_in_range(service1, 'response_time_ms', start_time, end_time)
        metrics2 = self.storage.get_metrics_in_range(service2, 'response_time_ms', start_time, end_time)
        
        if len(metrics1) < 10 or len(metrics2) < 10:
            return 0.0
            
        # Aligner temporellement
        values1 = [m.value for m in metrics1[:min(len(metrics1), len(metrics2))]]
        values2 = [m.value for m in metrics2[:min(len(metrics1), len(metrics2))]]
        
        return self.statistical_processor.calculate_correlation(values1, values2)
        
    def _interpret_correlations(self, correlations: Dict[str, float]) -> List[str]:
        """Interpréter corrélations"""
        insights = []
        
        high_positive = [(k, v) for k, v in correlations.items() if v > 0.7]
        high_negative = [(k, v) for k, v in correlations.items() if v < -0.7]
        
        if high_positive:
            insights.append(f"Found {len(high_positive)} strong positive correlations")
        if high_negative:
            insights.append(f"Found {len(high_negative)} strong negative correlations")
            
        return insights
        
    async def _generate_business_recommendations(self, business_insights: Dict[str, Any]) -> List[str]:
        """Générer recommandations business"""
        recommendations = []
        
        # Analyser services avec poor performance
        poor_services = [
            service for service, insights in business_insights['service_insights'].items()
            if insights.get('performance_rating') == 'poor'
        ]
        
        if poor_services:
            recommendations.append(f"Priority: Investigate {len(poor_services)} underperforming services")
            
        # Recommandations basées sur corrélations
        cross_analysis = business_insights.get('cross_service_analysis', {})
        if cross_analysis.get('significant_correlations'):
            recommendations.append("Consider service dependencies in capacity planning")
            
        return recommendations

# Example usage et testing
if __name__ == "__main__":
    async def test_metrics_aggregator():
        """Test agrégateur métriques"""
        config = AggregatorConfig(
            aggregation_interval_seconds=10,  # Plus fréquent pour test
            enable_real_time_aggregation=True,
            parallel_processing=True
        )
        
        aggregator = HealthMetricsAggregator(config)
        
        # Simuler ingestion métriques
        base_time = datetime.now()
        for i in range(100):
            timestamp = base_time + timedelta(minutes=i)
            
            # Métrique response time avec trend
            response_time = 100 + i * 2 + np.random.normal(0, 20)
            metric = HealthMetric(
                name='response_time_ms',
                value=max(0, response_time),
                timestamp=timestamp,
                service_name='api_service',
                metric_type=MetricType.GAUGE,
                labels={'environment': 'production'}
            )
            await aggregator.ingest_metric(metric)
            
            # Métrique CPU utilization
            cpu_value = 30 + 20 * np.sin(i * 0.1) + np.random.normal(0, 5)
            cpu_metric = HealthMetric(
                name='cpu_utilization',
                value=max(0, min(100, cpu_value)),
                timestamp=timestamp,
                service_name='api_service',
                metric_type=MetricType.GAUGE
            )
            await aggregator.ingest_metric(cpu_metric)
            
        # Test agrégations
        print("📊 Health Metrics Aggregator Results:")
        
        # Agrégation moyenne par fenêtre 15 minutes
        aggregated = await aggregator.aggregate_metrics(
            'api_service', 'response_time_ms', 
            AggregationType.AVERAGE, TimeWindow.FIFTEEN_MINUTES
        )
        print(f"15-minute averages: {len(aggregated)} windows")
        
        # Statistiques complètes
        stats = await aggregator.compute_statistical_summary('api_service', 'response_time_ms')
        print(f"Mean response time: {stats['basic_statistics']['mean']:.2f}ms")
        print(f"P95 response time: {stats['percentiles']['p95']:.2f}ms")
        
        # Business intelligence
        bi_results = await aggregator.generate_business_intelligence(['api_service'])
        print(f"Health Score: {bi_results['service_insights']['api_service']['health_score']:.2f}")
        print(f"Performance Rating: {bi_results['service_insights']['api_service']['performance_rating']}")
        
        # Stats temps réel
        rt_stats = await aggregator.get_real_time_metrics_summary()
        print(f"Total Metrics Processed: {rt_stats['aggregator_stats']['total_metrics_processed']}")
        print(f"Aggregations Computed: {rt_stats['aggregator_stats']['aggregations_computed']}")
        
        # Arrêter agrégation temps réel
        aggregator.stop_real_time_aggregation()
        
        return aggregated, stats, bi_results
        
    # Run test
    asyncio.run(test_metrics_aggregator())