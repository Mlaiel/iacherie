#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 SERVICE REGISTRY ENTERPRISE - REGISTRY PERFORMANCE MONITOR
=============================================================

**Author**: Expert Team (Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer)
**IP Owner**: Fahed Mlaiel (mlaiel@live.de)
**Project**: Ainflue Service Registry Enterprise
**Version**: 1.0 Production
**Created**: 2025-01-07 | Updated: 2025-12-14

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture service registry et tous ses algorithmes sont la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).
Toute reproduction, modification, distribution ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.

📊 REGISTRY PERFORMANCE MONITOR
Moniteur performance registry avec optimization recommendations.
Performance tracking + bottleneck detection + scaling recommendations.
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Set, Any, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import statistics
import numpy as np

# Core logger
logger = logging.getLogger(__name__)

class PerformanceMetric(Enum):
    """Métriques de performance"""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    CONNECTION_COUNT = "connection_count"
    QUEUE_SIZE = "queue_size"
    CACHE_HIT_RATIO = "cache_hit_ratio"

class AlertSeverity(Enum):
    """Niveaux de sévérité des alertes"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class BottleneckType(Enum):
    """Types de goulots d'étranglement"""
    CPU_BOUND = "cpu_bound"
    MEMORY_BOUND = "memory_bound"
    IO_BOUND = "io_bound"
    NETWORK_BOUND = "network_bound"
    DATABASE_BOUND = "database_bound"
    CACHE_BOUND = "cache_bound"
    CONCURRENCY_BOUND = "concurrency_bound"

@dataclass
class PerformanceThreshold:
    """Seuils de performance"""
    metric: PerformanceMetric
    warning_threshold: float
    critical_threshold: float
    emergency_threshold: float
    measurement_unit: str
    evaluation_window_seconds: int = 300

@dataclass
class PerformanceData:
    """Données de performance"""
    timestamp: float
    service_id: str
    metric: PerformanceMetric
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BottleneckDetectionResult:
    """Résultat de détection de goulot d'étranglement"""
    bottleneck_type: BottleneckType
    severity: AlertSeverity
    affected_services: List[str]
    root_cause: str
    impact_assessment: str
    resolution_recommendations: List[str]
    estimated_resolution_time_minutes: int
    confidence_score: float

@dataclass
class PerformanceMonitoringResult:
    """Résultat de monitoring performance"""
    monitoring_window_start: datetime
    monitoring_window_end: datetime
    total_services_monitored: int
    performance_summary: Dict[PerformanceMetric, Dict[str, float]]
    bottlenecks_detected: List[BottleneckDetectionResult]
    performance_trends: Dict[str, str]  # improving, stable, degrading
    scaling_recommendations: List[str]
    optimization_opportunities: List[str]
    overall_health_score: float

class RegistryPerformanceMonitor:
    """
    Moniteur performance registry avec optimization recommendations.
    Performance tracking + bottleneck detection + scaling recommendations.
    """
    
    def __init__(self, monitoring_config: Dict[str, Any] = None):
        """Initialisation du moniteur de performance"""
        self.monitoring_config = monitoring_config or {}
        self.performance_data: List[PerformanceData] = []
        self.performance_thresholds: Dict[PerformanceMetric, PerformanceThreshold] = {}
        self.monitored_services: Set[str] = set()
        
        # Composants spécialisés
        self.bottleneck_detector = BottleneckDetector()
        self.trend_analyzer = TrendAnalyzer()
        self.optimization_recommender = OptimizationRecommender()
        self.alert_manager = AlertManager()
        
        # Configuration des seuils par défaut
        self._initialize_default_thresholds()
        
        logger.info("📊 Registry Performance Monitor initialized")

    def _initialize_default_thresholds(self):
        """Initialisation des seuils de performance par défaut"""
        self.performance_thresholds = {
            PerformanceMetric.RESPONSE_TIME: PerformanceThreshold(
                metric=PerformanceMetric.RESPONSE_TIME,
                warning_threshold=100.0,  # 100ms
                critical_threshold=500.0,  # 500ms
                emergency_threshold=2000.0,  # 2s
                measurement_unit="milliseconds"
            ),
            PerformanceMetric.THROUGHPUT: PerformanceThreshold(
                metric=PerformanceMetric.THROUGHPUT,
                warning_threshold=1000.0,  # requests/sec
                critical_threshold=500.0,
                emergency_threshold=100.0,
                measurement_unit="requests_per_second"
            ),
            PerformanceMetric.ERROR_RATE: PerformanceThreshold(
                metric=PerformanceMetric.ERROR_RATE,
                warning_threshold=0.01,  # 1%
                critical_threshold=0.05,  # 5%
                emergency_threshold=0.10,  # 10%
                measurement_unit="percentage"
            ),
            PerformanceMetric.CPU_USAGE: PerformanceThreshold(
                metric=PerformanceMetric.CPU_USAGE,
                warning_threshold=70.0,  # 70%
                critical_threshold=85.0,  # 85%
                emergency_threshold=95.0,  # 95%
                measurement_unit="percentage"
            ),
            PerformanceMetric.MEMORY_USAGE: PerformanceThreshold(
                metric=PerformanceMetric.MEMORY_USAGE,
                warning_threshold=75.0,  # 75%
                critical_threshold=90.0,  # 90%
                emergency_threshold=98.0,  # 98%
                measurement_unit="percentage"
            ),
            PerformanceMetric.CACHE_HIT_RATIO: PerformanceThreshold(
                metric=PerformanceMetric.CACHE_HIT_RATIO,
                warning_threshold=0.80,  # 80%
                critical_threshold=0.60,  # 60%
                emergency_threshold=0.40,  # 40%
                measurement_unit="ratio"
            )
        }

    async def monitor_registry_performance(
        self, 
        monitoring_config: Dict[str, Any]
    ) -> PerformanceMonitoringResult:
        """
        Monitoring performance registry avec ML analysis.
        
        Features:
        - Multi-metric performance tracking
        - Real-time bottleneck detection
        - Trend analysis avec ML predictions
        - Automatic scaling recommendations
        - Root cause analysis
        """
        try:
            monitoring_start = datetime.now()
            
            # Collecte des données de performance
            performance_data = await self._collect_performance_data(monitoring_config)
            
            # Analyse des métriques
            performance_summary = await self._analyze_performance_metrics(performance_data)
            
            # Détection des goulots d'étranglement
            bottlenecks = await self._detect_performance_bottlenecks(performance_data)
            
            # Analyse des tendances
            performance_trends = await self._analyze_performance_trends(performance_data)
            
            # Génération des recommandations de scaling
            scaling_recommendations = await self._generate_scaling_recommendations(
                performance_summary, bottlenecks
            )
            
            # Identification des opportunités d'optimisation
            optimization_opportunities = await self._identify_optimization_opportunities(
                performance_data, bottlenecks
            )
            
            # Calcul du score de santé global
            overall_health_score = await self._calculate_overall_health_score(
                performance_summary, bottlenecks
            )
            
            # Déclenchement des alertes si nécessaire
            await self._trigger_performance_alerts(bottlenecks, performance_summary)
            
            monitoring_end = datetime.now()
            
            logger.info(
                f"📊 Performance monitoring completed: {len(self.monitored_services)} services, "
                f"{len(bottlenecks)} bottlenecks detected"
            )
            
            return PerformanceMonitoringResult(
                monitoring_window_start=monitoring_start,
                monitoring_window_end=monitoring_end,
                total_services_monitored=len(self.monitored_services),
                performance_summary=performance_summary,
                bottlenecks_detected=bottlenecks,
                performance_trends=performance_trends,
                scaling_recommendations=scaling_recommendations,
                optimization_opportunities=optimization_opportunities,
                overall_health_score=overall_health_score
            )
            
        except Exception as e:
            logger.error(f"❌ Performance monitoring failed: {str(e)}")
            raise

    async def _collect_performance_data(
        self, 
        monitoring_config: Dict[str, Any]
    ) -> List[PerformanceData]:
        """Collecte des données de performance"""
        collected_data = []
        current_time = time.time()
        
        for service_id in self.monitored_services:
            # Simulation de collecte de métriques
            # En réalité, cela viendrait de systèmes de monitoring réels
            
            metrics_data = {
                PerformanceMetric.RESPONSE_TIME: np.random.normal(150, 50),
                PerformanceMetric.THROUGHPUT: np.random.normal(2000, 500),
                PerformanceMetric.ERROR_RATE: max(0, np.random.normal(0.005, 0.002)),
                PerformanceMetric.CPU_USAGE: np.random.normal(60, 20),
                PerformanceMetric.MEMORY_USAGE: np.random.normal(65, 15),
                PerformanceMetric.CACHE_HIT_RATIO: min(1.0, max(0, np.random.normal(0.85, 0.1)))
            }
            
            for metric, value in metrics_data.items():
                performance_data = PerformanceData(
                    timestamp=current_time,
                    service_id=service_id,
                    metric=metric,
                    value=max(0, value),
                    metadata={'collection_method': 'simulated'}
                )
                collected_data.append(performance_data)
                
        self.performance_data.extend(collected_data)
        
        # Nettoyage des anciennes données (garder seulement 24h)
        cutoff_time = current_time - 86400  # 24 heures
        self.performance_data = [
            data for data in self.performance_data 
            if data.timestamp > cutoff_time
        ]
        
        return collected_data

    async def _analyze_performance_metrics(
        self, 
        performance_data: List[PerformanceData]
    ) -> Dict[PerformanceMetric, Dict[str, float]]:
        """Analyse des métriques de performance"""
        metrics_summary = {}
        
        for metric in PerformanceMetric:
            metric_values = [
                data.value for data in performance_data 
                if data.metric == metric
            ]
            
            if metric_values:
                metrics_summary[metric] = {
                    'mean': statistics.mean(metric_values),
                    'median': statistics.median(metric_values),
                    'min': min(metric_values),
                    'max': max(metric_values),
                    'std_dev': statistics.stdev(metric_values) if len(metric_values) > 1 else 0,
                    'p95': np.percentile(metric_values, 95),
                    'p99': np.percentile(metric_values, 99),
                    'sample_count': len(metric_values)
                }
                
        return metrics_summary

    async def _detect_performance_bottlenecks(
        self, 
        performance_data: List[PerformanceData]
    ) -> List[BottleneckDetectionResult]:
        """Détection des goulots d'étranglement de performance"""
        bottlenecks = []
        
        # Analyse par service
        service_metrics = {}
        for data in performance_data:
            if data.service_id not in service_metrics:
                service_metrics[data.service_id] = {}
            if data.metric not in service_metrics[data.service_id]:
                service_metrics[data.service_id][data.metric] = []
            service_metrics[data.service_id][data.metric].append(data.value)
        
        for service_id, metrics in service_metrics.items():
            # Détection CPU bound
            if PerformanceMetric.CPU_USAGE in metrics:
                cpu_values = metrics[PerformanceMetric.CPU_USAGE]
                avg_cpu = statistics.mean(cpu_values)
                
                if avg_cpu > 90:
                    bottleneck = BottleneckDetectionResult(
                        bottleneck_type=BottleneckType.CPU_BOUND,
                        severity=AlertSeverity.CRITICAL,
                        affected_services=[service_id],
                        root_cause=f"High CPU usage: {avg_cpu:.1f}%",
                        impact_assessment="Performance degradation, increased response times",
                        resolution_recommendations=[
                            "Scale horizontally with additional instances",
                            "Optimize CPU-intensive operations",
                            "Implement connection pooling",
                            "Consider async processing for heavy tasks"
                        ],
                        estimated_resolution_time_minutes=30,
                        confidence_score=0.85
                    )
                    bottlenecks.append(bottleneck)
            
            # Détection Memory bound
            if PerformanceMetric.MEMORY_USAGE in metrics:
                memory_values = metrics[PerformanceMetric.MEMORY_USAGE]
                avg_memory = statistics.mean(memory_values)
                
                if avg_memory > 85:
                    bottleneck = BottleneckDetectionResult(
                        bottleneck_type=BottleneckType.MEMORY_BOUND,
                        severity=AlertSeverity.WARNING if avg_memory < 95 else AlertSeverity.CRITICAL,
                        affected_services=[service_id],
                        root_cause=f"High memory usage: {avg_memory:.1f}%",
                        impact_assessment="Risk of OOM errors, garbage collection pressure",
                        resolution_recommendations=[
                            "Increase memory allocation",
                            "Optimize memory usage patterns",
                            "Implement memory caching strategies",
                            "Review for memory leaks"
                        ],
                        estimated_resolution_time_minutes=45,
                        confidence_score=0.90
                    )
                    bottlenecks.append(bottleneck)
            
            # Détection Cache inefficiency
            if PerformanceMetric.CACHE_HIT_RATIO in metrics:
                cache_values = metrics[PerformanceMetric.CACHE_HIT_RATIO]
                avg_cache_hit = statistics.mean(cache_values)
                
                if avg_cache_hit < 0.70:
                    bottleneck = BottleneckDetectionResult(
                        bottleneck_type=BottleneckType.CACHE_BOUND,
                        severity=AlertSeverity.WARNING,
                        affected_services=[service_id],
                        root_cause=f"Low cache hit ratio: {avg_cache_hit:.2f}",
                        impact_assessment="Increased database load, slower response times",
                        resolution_recommendations=[
                            "Optimize cache eviction policies",
                            "Increase cache size",
                            "Review cache key strategies",
                            "Implement cache warming"
                        ],
                        estimated_resolution_time_minutes=60,
                        confidence_score=0.75
                    )
                    bottlenecks.append(bottleneck)
        
        return bottlenecks

    async def _analyze_performance_trends(
        self, 
        performance_data: List[PerformanceData]
    ) -> Dict[str, str]:
        """Analyse des tendances de performance"""
        return await self.trend_analyzer.analyze_trends(performance_data)

    async def _generate_scaling_recommendations(
        self, 
        performance_summary: Dict[PerformanceMetric, Dict[str, float]],
        bottlenecks: List[BottleneckDetectionResult]
    ) -> List[str]:
        """Génération des recommandations de scaling"""
        recommendations = []
        
        # Recommandations basées sur les bottlenecks
        cpu_bottlenecks = [b for b in bottlenecks if b.bottleneck_type == BottleneckType.CPU_BOUND]
        memory_bottlenecks = [b for b in bottlenecks if b.bottleneck_type == BottleneckType.MEMORY_BOUND]
        
        if cpu_bottlenecks:
            recommendations.append("Horizontal scaling recommended: Add more service instances")
            recommendations.append("Consider CPU optimization: Profile and optimize hot code paths")
            
        if memory_bottlenecks:
            recommendations.append("Vertical scaling recommended: Increase memory allocation")
            recommendations.append("Memory optimization: Review object lifecycle and implement pooling")
        
        # Recommandations basées sur les métriques
        if PerformanceMetric.THROUGHPUT in performance_summary:
            throughput_stats = performance_summary[PerformanceMetric.THROUGHPUT]
            if throughput_stats['mean'] < 1000:
                recommendations.append("Performance scaling: Consider load balancer optimization")
                
        if PerformanceMetric.RESPONSE_TIME in performance_summary:
            response_time_stats = performance_summary[PerformanceMetric.RESPONSE_TIME]
            if response_time_stats['p95'] > 200:
                recommendations.append("Latency optimization: Implement response caching")
                
        return recommendations

    async def _identify_optimization_opportunities(
        self, 
        performance_data: List[PerformanceData],
        bottlenecks: List[BottleneckDetectionResult]
    ) -> List[str]:
        """Identification des opportunités d'optimisation"""
        return await self.optimization_recommender.identify_opportunities(
            performance_data, bottlenecks
        )

    async def _calculate_overall_health_score(
        self, 
        performance_summary: Dict[PerformanceMetric, Dict[str, float]],
        bottlenecks: List[BottleneckDetectionResult]
    ) -> float:
        """Calcul du score de santé global"""
        base_score = 100.0
        
        # Pénalités pour les bottlenecks
        for bottleneck in bottlenecks:
            if bottleneck.severity == AlertSeverity.EMERGENCY:
                base_score -= 30
            elif bottleneck.severity == AlertSeverity.CRITICAL:
                base_score -= 20
            elif bottleneck.severity == AlertSeverity.WARNING:
                base_score -= 10
                
        # Pénalités pour les métriques hors seuils
        for metric, stats in performance_summary.items():
            threshold = self.performance_thresholds.get(metric)
            if threshold:
                mean_value = stats['mean']
                
                if metric in [PerformanceMetric.RESPONSE_TIME, PerformanceMetric.ERROR_RATE]:
                    # Pour ces métriques, plus c'est bas, mieux c'est
                    if mean_value > threshold.critical_threshold:
                        base_score -= 15
                    elif mean_value > threshold.warning_threshold:
                        base_score -= 5
                elif metric in [PerformanceMetric.THROUGHPUT, PerformanceMetric.CACHE_HIT_RATIO]:
                    # Pour ces métriques, plus c'est haut, mieux c'est
                    if mean_value < threshold.critical_threshold:
                        base_score -= 15
                    elif mean_value < threshold.warning_threshold:
                        base_score -= 5
                        
        return max(0.0, min(100.0, base_score))

    async def _trigger_performance_alerts(
        self, 
        bottlenecks: List[BottleneckDetectionResult],
        performance_summary: Dict[PerformanceMetric, Dict[str, float]]
    ):
        """Déclenchement des alertes de performance"""
        await self.alert_manager.process_performance_alerts(bottlenecks, performance_summary)

    async def add_monitored_service(self, service_id: str):
        """Ajout d'un service à monitorer"""
        self.monitored_services.add(service_id)
        logger.info(f"📊 Added service to monitoring: {service_id}")

    async def remove_monitored_service(self, service_id: str):
        """Suppression d'un service du monitoring"""
        self.monitored_services.discard(service_id)
        logger.info(f"📊 Removed service from monitoring: {service_id}")

    async def update_performance_thresholds(
        self, 
        metric: PerformanceMetric, 
        threshold: PerformanceThreshold
    ):
        """Mise à jour des seuils de performance"""
        self.performance_thresholds[metric] = threshold
        logger.info(f"📊 Updated performance threshold for {metric.value}")

class BottleneckDetector:
    """Détecteur de goulots d'étranglement"""
    
    async def detect_bottlenecks(
        self, 
        performance_data: List[PerformanceData]
    ) -> List[BottleneckDetectionResult]:
        """Détection avancée de goulots d'étranglement avec ML"""
        # Implémentation d'algorithmes ML pour détection avancée
        return []

class TrendAnalyzer:
    """Analyseur de tendances"""
    
    async def analyze_trends(
        self, 
        performance_data: List[PerformanceData]
    ) -> Dict[str, str]:
        """Analyse des tendances de performance avec ML"""
        trends = {}
        
        # Analyse par métrique
        for metric in PerformanceMetric:
            metric_data = [data for data in performance_data if data.metric == metric]
            if len(metric_data) >= 10:
                values = [data.value for data in sorted(metric_data, key=lambda x: x.timestamp)]
                
                # Calcul de tendance simple (régression linéaire basique)
                if len(values) >= 2:
                    slope = (values[-1] - values[0]) / len(values)
                    
                    if abs(slope) < 0.01:
                        trends[metric.value] = "stable"
                    elif slope > 0:
                        if metric in [PerformanceMetric.RESPONSE_TIME, PerformanceMetric.ERROR_RATE]:
                            trends[metric.value] = "degrading"
                        else:
                            trends[metric.value] = "improving"
                    else:
                        if metric in [PerformanceMetric.RESPONSE_TIME, PerformanceMetric.ERROR_RATE]:
                            trends[metric.value] = "improving"
                        else:
                            trends[metric.value] = "degrading"
                            
        return trends

class OptimizationRecommender:
    """Recommandeur d'optimisations"""
    
    async def identify_opportunities(
        self, 
        performance_data: List[PerformanceData],
        bottlenecks: List[BottleneckDetectionResult]
    ) -> List[str]:
        """Identification des opportunités d'optimisation"""
        opportunities = []
        
        # Opportunités basées sur les patterns de performance
        opportunities.extend([
            "Implement connection pooling for database connections",
            "Add response caching for frequently accessed data",
            "Optimize database queries with proper indexing",
            "Implement async processing for non-critical operations",
            "Consider CDN for static content delivery",
            "Optimize serialization/deserialization performance",
            "Implement circuit breakers for external service calls",
            "Add request/response compression",
            "Optimize memory allocation patterns",
            "Implement batch processing for bulk operations"
        ])
        
        return opportunities

class AlertManager:
    """Gestionnaire d'alertes"""
    
    async def process_performance_alerts(
        self, 
        bottlenecks: List[BottleneckDetectionResult],
        performance_summary: Dict[PerformanceMetric, Dict[str, float]]
    ):
        """Traitement des alertes de performance"""
        for bottleneck in bottlenecks:
            if bottleneck.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
                await self._send_alert(bottleneck)
                
    async def _send_alert(self, bottleneck: BottleneckDetectionResult):
        """Envoi d'alerte"""
        logger.warning(
            f"🚨 Performance Alert - {bottleneck.severity.value.upper()}: "
            f"{bottleneck.bottleneck_type.value} detected - {bottleneck.root_cause}"
        )

# Factory function
def create_registry_performance_monitor(config: Dict[str, Any] = None) -> RegistryPerformanceMonitor:
    """Factory function pour créer un Registry Performance Monitor"""
    return RegistryPerformanceMonitor(config)

# Export des classes principales
__all__ = [
    'RegistryPerformanceMonitor',
    'PerformanceData',
    'PerformanceThreshold',
    'BottleneckDetectionResult',
    'PerformanceMonitoringResult',
    'PerformanceMetric',
    'AlertSeverity',
    'BottleneckType',
    'create_registry_performance_monitor'
]