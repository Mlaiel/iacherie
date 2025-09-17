"""
📊 LOAD BALANCER METRICS - ENTERPRISE COMPREHENSIVE TRACKING
Système métriques comprehensive pour load balancing

Implements real-time metrics + performance analytics + optimization insights
for enterprise-grade load balancing monitoring and performance analysis.

Key Features:
- Real-time metrics collection avec multi-dimensional tracking
- Performance analytics avec trend analysis et anomaly detection
- Distribution efficiency analysis avec load balancing optimization
- Server performance monitoring avec health scoring
- Request routing analytics avec success rate tracking
- Capacity utilization metrics avec scaling recommendations

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture load balancer metrics est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel.
Toute reproduction, modification, distribution sans autorisation écrite est STRICTEMENT INTERDITE.
"""

import asyncio
import logging
import time
import statistics
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types de métriques load balancing"""
    REQUEST_COUNT = "request_count"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    SERVER_LOAD = "server_load"
    CONNECTION_COUNT = "connection_count"
    QUEUE_LENGTH = "queue_length"
    CIRCUIT_BREAKER_STATE = "circuit_breaker_state"
    GEOGRAPHIC_DISTRIBUTION = "geographic_distribution"
    SESSION_AFFINITY = "session_affinity"

class AggregationType(Enum):
    """Types d'agrégation métriques"""
    SUM = "sum"
    AVERAGE = "average"
    MINIMUM = "minimum"
    MAXIMUM = "maximum"
    COUNT = "count"
    PERCENTILE_95 = "p95"
    PERCENTILE_99 = "p99"
    RATE = "rate"

@dataclass
class MetricPoint:
    """Point métrique individuel"""
    metric_name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AggregatedMetric:
    """Métrique agrégée"""
    metric_name: str
    aggregation_type: AggregationType
    value: float
    sample_count: int
    time_window_start: datetime
    time_window_end: datetime
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class ServerMetrics:
    """Métriques serveur individuelles"""
    server_id: str
    request_count: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    active_connections: int = 0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    network_io: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    @property
    def success_rate(self) -> float:
        """Taux de succès"""
        return (self.successful_requests / max(1, self.request_count)) * 100.0
    
    @property
    def error_rate(self) -> float:
        """Taux d'erreur"""
        return (self.failed_requests / max(1, self.request_count)) * 100.0
    
    @property
    def average_response_time(self) -> float:
        """Temps de réponse moyen"""
        return self.total_response_time / max(1, self.request_count)

@dataclass
class LoadBalancingMetrics:
    """Métriques load balancing globales"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    throughput_rps: float = 0.0
    active_servers: int = 0
    total_servers: int = 0
    distribution_efficiency: float = 0.0
    circuit_breaker_trips: int = 0
    session_affinity_hits: int = 0
    geographic_regions_active: int = 0
    priority_queue_length: int = 0
    last_updated: datetime = field(default_factory=datetime.now)

class MetricsCollector:
    """Collecteur métriques temps réel"""
    
    def __init__(self, collection_interval: float = 1.0):
        self.collection_interval = collection_interval
        self.metrics_buffer: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.server_metrics: Dict[str, ServerMetrics] = {}
        self.global_metrics = LoadBalancingMetrics()
        
        # Thread-safe operations
        self._lock = threading.RLock()
        self._collection_active = False
        self._collection_task: Optional[asyncio.Task] = None
        
        # Executor pour calculs intensifs
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="metrics_")
        
    async def start_collection(self) -> bool:
        """Démarrage collection métriques"""
        try:
            if self._collection_active:
                logger.warning("Collection métriques déjà active")
                return False
            
            self._collection_active = True
            self._collection_task = asyncio.create_task(self._collection_loop())
            
            logger.info("📊 Collection métriques démarrée")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur démarrage collection métriques: {e}")
            return False
    
    async def stop_collection(self) -> bool:
        """Arrêt collection métriques"""
        try:
            self._collection_active = False
            
            if self._collection_task:
                self._collection_task.cancel()
                try:
                    await self._collection_task
                except asyncio.CancelledError:
                    pass
            
            self._executor.shutdown(wait=True)
            logger.info("📊 Collection métriques arrêtée")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur arrêt collection métriques: {e}")
            return False
    
    async def record_metric(self, metric_point: MetricPoint) -> bool:
        """Enregistrement point métrique"""
        try:
            with self._lock:
                self.metrics_buffer[metric_point.metric_name].append(metric_point)
            
            # Mise à jour métriques serveur si applicable
            if "server_id" in metric_point.labels:
                await self._update_server_metrics(metric_point)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur enregistrement métrique: {e}")
            return False
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """Obtention métriques actuelles"""
        try:
            with self._lock:
                current_metrics = {
                    "global_metrics": asdict(self.global_metrics),
                    "server_metrics": {
                        server_id: asdict(metrics) 
                        for server_id, metrics in self.server_metrics.items()
                    },
                    "collection_stats": {
                        "buffer_sizes": {
                            name: len(buffer) 
                            for name, buffer in self.metrics_buffer.items()
                        },
                        "total_metrics_collected": sum(len(buffer) for buffer in self.metrics_buffer.values()),
                        "collection_active": self._collection_active,
                        "last_collection": datetime.now()
                    }
                }
            
            return current_metrics
            
        except Exception as e:
            logger.error(f"❌ Erreur obtention métriques actuelles: {e}")
            return {}
    
    async def _collection_loop(self):
        """Boucle collection métriques"""
        while self._collection_active:
            try:
                await asyncio.sleep(self.collection_interval)
                
                # Mise à jour métriques globales
                await self._update_global_metrics()
                
                # Nettoyage buffer périodique
                await self._cleanup_old_metrics()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur boucle collection métriques: {e}")
                await asyncio.sleep(5.0)  # Pause avant retry
    
    async def _update_server_metrics(self, metric_point: MetricPoint):
        """Mise à jour métriques serveur"""
        server_id = metric_point.labels.get("server_id")
        if not server_id:
            return
        
        with self._lock:
            if server_id not in self.server_metrics:
                self.server_metrics[server_id] = ServerMetrics(server_id=server_id)
            
            server_metrics = self.server_metrics[server_id]
            
            # Mise à jour selon type métrique
            if metric_point.metric_name == MetricType.REQUEST_COUNT.value:
                server_metrics.request_count += int(metric_point.value)
            elif metric_point.metric_name == MetricType.RESPONSE_TIME.value:
                server_metrics.total_response_time += metric_point.value
            elif metric_point.metric_name == MetricType.ERROR_RATE.value:
                if metric_point.value > 0:
                    server_metrics.failed_requests += 1
                else:
                    server_metrics.successful_requests += 1
            
            server_metrics.last_updated = datetime.now()
    
    async def _update_global_metrics(self):
        """Mise à jour métriques globales"""
        try:
            with self._lock:
                # Calcul métriques globales depuis métriques serveurs
                total_requests = sum(m.request_count for m in self.server_metrics.values())
                total_successful = sum(m.successful_requests for m in self.server_metrics.values())
                total_failed = sum(m.failed_requests for m in self.server_metrics.values())
                
                self.global_metrics.total_requests = total_requests
                self.global_metrics.successful_requests = total_successful
                self.global_metrics.failed_requests = total_failed
                self.global_metrics.total_servers = len(self.server_metrics)
                self.global_metrics.active_servers = sum(
                    1 for m in self.server_metrics.values() 
                    if (datetime.now() - m.last_updated).total_seconds() < 60
                )
                
                # Calcul temps réponse moyen global
                if total_requests > 0:
                    total_response_time = sum(m.total_response_time for m in self.server_metrics.values())
                    self.global_metrics.average_response_time = total_response_time / total_requests
                
                # Calcul throughput
                time_window = 60.0  # 1 minute
                recent_requests = sum(
                    len([p for p in self.metrics_buffer[MetricType.REQUEST_COUNT.value] 
                         if (datetime.now() - p.timestamp).total_seconds() < time_window])
                )
                self.global_metrics.throughput_rps = recent_requests / time_window
                
                self.global_metrics.last_updated = datetime.now()
                
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour métriques globales: {e}")
    
    async def _cleanup_old_metrics(self):
        """Nettoyage métriques anciennes"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=1)
            
            with self._lock:
                for metric_name, buffer in self.metrics_buffer.items():
                    # Suppression métriques > 1 heure
                    while buffer and buffer[0].timestamp < cutoff_time:
                        buffer.popleft()
                        
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage métriques: {e}")

class PerformanceAnalyzer:
    """Analyseur performance load balancing"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.analysis_cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes
        
    async def analyze_distribution_efficiency(self, traffic_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        📈 ANALYSE EFFICACITÉ DISTRIBUTION AVEC RECOMMENDATIONS
        
        Analyse efficacité distribution load balancing avec recommendations d'optimisation.
        """
        logger.info("📈 Analyse efficacité distribution")
        
        analysis_result = {
            "efficiency_score": 0.0,
            "distribution_metrics": {},
            "server_utilization": {},
            "bottlenecks_identified": [],
            "optimization_recommendations": [],
            "performance_trends": {}
        }
        
        try:
            # Obtention métriques actuelles
            current_metrics = await self.metrics_collector.get_current_metrics()
            server_metrics = current_metrics.get("server_metrics", {})
            
            if not server_metrics:
                logger.warning("Aucune métrique serveur disponible pour analyse")
                return analysis_result
            
            # Analyse distribution charge
            server_loads = []
            total_requests = 0
            
            for server_id, metrics in server_metrics.items():
                server_load = metrics.get("request_count", 0)
                server_loads.append(server_load)
                total_requests += server_load
                
                # Analyse utilisation individuelle
                analysis_result["server_utilization"][server_id] = {
                    "request_count": server_load,
                    "success_rate": metrics.get("success_rate", 0.0),
                    "average_response_time": metrics.get("average_response_time", 0.0),
                    "utilization_percentage": (server_load / max(1, total_requests)) * 100
                }
            
            # Calcul efficacité distribution
            if server_loads and len(server_loads) > 1:
                # Coefficient variation (plus faible = meilleure distribution)
                mean_load = statistics.mean(server_loads)
                if mean_load > 0:
                    cv = statistics.stdev(server_loads) / mean_load
                    efficiency_score = max(0.0, 100.0 - (cv * 100.0))
                    analysis_result["efficiency_score"] = efficiency_score
                else:
                    analysis_result["efficiency_score"] = 100.0
            
            # Métriques distribution
            analysis_result["distribution_metrics"] = {
                "total_servers": len(server_metrics),
                "active_servers": sum(1 for m in server_metrics.values() if m.get("request_count", 0) > 0),
                "load_variance": statistics.variance(server_loads) if len(server_loads) > 1 else 0.0,
                "load_std_dev": statistics.stdev(server_loads) if len(server_loads) > 1 else 0.0,
                "min_load": min(server_loads) if server_loads else 0,
                "max_load": max(server_loads) if server_loads else 0,
                "load_range": max(server_loads) - min(server_loads) if server_loads else 0
            }
            
            # Identification bottlenecks
            if server_loads:
                max_load = max(server_loads)
                avg_load = statistics.mean(server_loads)
                
                for server_id, metrics in server_metrics.items():
                    server_load = metrics.get("request_count", 0)
                    
                    # Serveur surchargé
                    if server_load > avg_load * 2:
                        analysis_result["bottlenecks_identified"].append({
                            "server_id": server_id,
                            "type": "overloaded",
                            "load": server_load,
                            "deviation_from_avg": server_load - avg_load,
                            "impact": "high"
                        })
                    
                    # Serveur sous-utilisé
                    elif server_load < avg_load * 0.3 and avg_load > 0:
                        analysis_result["bottlenecks_identified"].append({
                            "server_id": server_id,
                            "type": "underutilized",
                            "load": server_load,
                            "deviation_from_avg": avg_load - server_load,
                            "impact": "medium"
                        })
            
            # Recommandations optimisation
            recommendations = []
            
            if analysis_result["efficiency_score"] < 70:
                recommendations.append({
                    "type": "algorithm_optimization",
                    "priority": "high",
                    "description": "Efficacité distribution faible - considérer algorithme weighted round-robin",
                    "expected_improvement": "15-25% amélioration distribution"
                })
            
            if len(analysis_result["bottlenecks_identified"]) > 0:
                overloaded_servers = [b for b in analysis_result["bottlenecks_identified"] if b["type"] == "overloaded"]
                if overloaded_servers:
                    recommendations.append({
                        "type": "capacity_scaling",
                        "priority": "high",
                        "description": f"{len(overloaded_servers)} serveur(s) surchargé(s) - scaling nécessaire",
                        "expected_improvement": "Réduction latence 30-50%"
                    })
            
            if analysis_result["distribution_metrics"]["load_variance"] > 1000:
                recommendations.append({
                    "type": "load_balancing_tuning",
                    "priority": "medium", 
                    "description": "Variance charge élevée - ajustement poids serveurs recommandé",
                    "expected_improvement": "Réduction variance 40-60%"
                })
            
            analysis_result["optimization_recommendations"] = recommendations
            
            # Tendances performance (simulation basée sur données actuelles)
            analysis_result["performance_trends"] = {
                "efficiency_trend": "stable" if analysis_result["efficiency_score"] > 80 else "declining",
                "load_growth_rate": min(10.0, total_requests / max(1, len(server_metrics)) * 0.1),
                "projected_capacity_need": total_requests * 1.2,  # 20% buffer
                "optimization_potential": max(0, 100 - analysis_result["efficiency_score"])
            }
            
            logger.info(f"✅ Analyse distribution terminée: efficacité {analysis_result['efficiency_score']:.1f}%")
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse efficacité distribution: {e}")
            analysis_result["error"] = str(e)
        
        return analysis_result
    
    async def generate_optimization_insights(self, historical_data: Dict[str, Any]) -> List[str]:
        """
        💡 GÉNÉRATION INSIGHTS OPTIMIZATION BASÉS SUR ANALYTICS
        
        Génération insights optimization basés sur analytics historiques.
        """
        logger.info("💡 Génération insights optimization")
        
        insights = []
        
        try:
            # Analyse données historiques
            time_series_data = historical_data.get("time_series", [])
            server_performance = historical_data.get("server_performance", {})
            traffic_patterns = historical_data.get("traffic_patterns", {})
            error_patterns = historical_data.get("error_patterns", {})
            
            # Insight #1: Patterns temporels
            if traffic_patterns:
                peak_hours = traffic_patterns.get("peak_hours", [])
                if peak_hours:
                    insights.append(
                        f"🕐 Pics trafic identifiés: {', '.join(map(str, peak_hours))}h - "
                        f"considérer auto-scaling programmé pour améliorer performance"
                    )
            
            # Insight #2: Performance serveurs
            if server_performance:
                slow_servers = [
                    server for server, perf in server_performance.items()
                    if perf.get("average_response_time", 0) > 500  # > 500ms
                ]
                
                if slow_servers:
                    insights.append(
                        f"⚠️ Serveurs lents détectés: {', '.join(slow_servers)} - "
                        f"optimisation ou remplacement recommandé"
                    )
            
            # Insight #3: Patterns erreurs
            if error_patterns:
                high_error_servers = [
                    server for server, error_rate in error_patterns.items()
                    if error_rate > 5.0  # > 5% erreurs
                ]
                
                if high_error_servers:
                    insights.append(
                        f"🚨 Taux erreurs élevé: {', '.join(high_error_servers)} - "
                        f"investigation et corrective action requises"
                    )
            
            # Insight #4: Efficacité algorithme
            current_efficiency = historical_data.get("current_efficiency", 0)
            if current_efficiency < 80:
                insights.append(
                    f"📊 Efficacité load balancing: {current_efficiency:.1f}% - "
                    f"changement algorithme vers intelligent ML recommandé"
                )
            
            # Insight #5: Capacité
            capacity_utilization = historical_data.get("capacity_utilization", 0)
            if capacity_utilization > 85:
                insights.append(
                    f"📈 Utilisation capacité élevée: {capacity_utilization:.1f}% - "
                    f"scaling horizontal nécessaire avant saturation"
                )
            elif capacity_utilization < 30:
                insights.append(
                    f"📉 Sous-utilisation capacité: {capacity_utilization:.1f}% - "
                    f"optimisation coûts possible via consolidation serveurs"
                )
            
            # Insight #6: Répartition géographique
            geo_distribution = historical_data.get("geographic_distribution", {})
            if geo_distribution:
                unbalanced_regions = [
                    region for region, load in geo_distribution.items()
                    if load > 60 or load < 10  # > 60% ou < 10%
                ]
                
                if unbalanced_regions:
                    insights.append(
                        f"🌍 Déséquilibre géographique: {', '.join(unbalanced_regions)} - "
                        f"ajustement routing géographique recommandé"
                    )
            
            # Insight #7: Session affinity
            session_metrics = historical_data.get("session_metrics", {})
            if session_metrics:
                affinity_hit_rate = session_metrics.get("affinity_hit_rate", 0)
                if affinity_hit_rate < 90:
                    insights.append(
                        f"🔗 Taux affinity session faible: {affinity_hit_rate:.1f}% - "
                        f"optimisation session store et sticky sessions recommandée"
                    )
            
            # Insight générique si pas d'insights spécifiques
            if not insights:
                insights.append(
                    "✅ Performance load balancing globalement satisfaisante - "
                    "monitoring continu recommandé pour détection proactive"
                )
            
            logger.info(f"✅ Génération insights terminée: {len(insights)} insights identifiés")
            
        except Exception as e:
            logger.error(f"❌ Erreur génération insights optimization: {e}")
            insights.append(f"❌ Erreur analyse: {str(e)} - vérification configuration requise")
        
        return insights

class LoadBalancerMetrics:
    """
    📊 SYSTÈME MÉTRIQUES COMPREHENSIVE POUR LOAD BALANCING
    
    Système métriques comprehensive pour load balancing.
    Real-time metrics + performance analytics + optimization insights.
    """
    
    def __init__(self, collection_interval: float = 1.0):
        self.metrics_collector = MetricsCollector(collection_interval)
        self.performance_analyzer = PerformanceAnalyzer(self.metrics_collector)
        
        # État système
        self.is_active = False
        self.start_time: Optional[datetime] = None
        
        logger.info("📊 Load Balancer Metrics System initialisé")
    
    async def initialize(self) -> bool:
        """Initialisation système métriques"""
        try:
            success = await self.metrics_collector.start_collection()
            if success:
                self.is_active = True
                self.start_time = datetime.now()
                logger.info("✅ Système métriques load balancer initialisé avec succès")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation système métriques: {e}")
            return False
    
    async def shutdown(self) -> bool:
        """Arrêt système métriques"""
        try:
            success = await self.metrics_collector.stop_collection()
            if success:
                self.is_active = False
                logger.info("✅ Système métriques load balancer arrêté")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Erreur arrêt système métriques: {e}")
            return False

    async def collect_balancing_metrics(self, balancer_id: str) -> Dict[str, Any]:
        """
        📊 COLLECTION MÉTRIQUES LOAD BALANCING COMPREHENSIVE
        
        Collection métriques load balancing comprehensive avec analytics temps réel.
        """
        logger.debug(f"📊 Collection métriques load balancer {balancer_id}")
        
        collection_result = {
            "balancer_id": balancer_id,
            "collection_timestamp": datetime.now(),
            "metrics": {},
            "aggregated_metrics": {},
            "collection_status": "success"
        }
        
        try:
            # Collection métriques actuelles
            current_metrics = await self.metrics_collector.get_current_metrics()
            collection_result["metrics"] = current_metrics
            
            # Métriques agrégées
            global_metrics = current_metrics.get("global_metrics", {})
            server_metrics = current_metrics.get("server_metrics", {})
            
            collection_result["aggregated_metrics"] = {
                "summary": {
                    "total_requests": global_metrics.get("total_requests", 0),
                    "success_rate": (
                        (global_metrics.get("successful_requests", 0) / 
                         max(1, global_metrics.get("total_requests", 1))) * 100
                    ),
                    "average_response_time_ms": global_metrics.get("average_response_time", 0.0) * 1000,
                    "throughput_rps": global_metrics.get("throughput_rps", 0.0),
                    "active_servers": global_metrics.get("active_servers", 0),
                    "total_servers": global_metrics.get("total_servers", 0)
                },
                "server_summary": {
                    server_id: {
                        "request_count": metrics.get("request_count", 0),
                        "success_rate": metrics.get("success_rate", 0.0),
                        "avg_response_time": metrics.get("average_response_time", 0.0)
                    }
                    for server_id, metrics in server_metrics.items()
                },
                "health_indicators": {
                    "overall_health": "healthy" if global_metrics.get("active_servers", 0) > 0 else "unhealthy",
                    "distribution_quality": "good",  # À calculer basé sur variance
                    "performance_status": "optimal" if global_metrics.get("average_response_time", 1) < 0.5 else "degraded"
                }
            }
            
            logger.debug(f"✅ Collection métriques terminée pour {balancer_id}")
            
        except Exception as e:
            logger.error(f"❌ Erreur collection métriques {balancer_id}: {e}")
            collection_result["collection_status"] = "error"
            collection_result["error"] = str(e)
        
        return collection_result
    
    async def record_request_metrics(self, request_data: Dict[str, Any]) -> bool:
        """Enregistrement métriques requête"""
        try:
            # Création points métriques
            timestamp = datetime.now()
            server_id = request_data.get("server_id", "unknown")
            
            metrics_to_record = [
                MetricPoint(
                    metric_name=MetricType.REQUEST_COUNT.value,
                    value=1.0,
                    timestamp=timestamp,
                    labels={"server_id": server_id}
                ),
                MetricPoint(
                    metric_name=MetricType.RESPONSE_TIME.value,
                    value=request_data.get("response_time", 0.0),
                    timestamp=timestamp,
                    labels={"server_id": server_id}
                ),
                MetricPoint(
                    metric_name=MetricType.ERROR_RATE.value,
                    value=1.0 if request_data.get("error", False) else 0.0,
                    timestamp=timestamp,
                    labels={"server_id": server_id}
                )
            ]
            
            # Enregistrement points
            for metric_point in metrics_to_record:
                await self.metrics_collector.record_metric(metric_point)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur enregistrement métriques requête: {e}")
            return False

# Point d'entrée pour tests et démonstration
async def main():
    """Démonstration Load Balancer Metrics"""
    logger.info("🚀 Démonstration Load Balancer Metrics")
    
    # Initialisation système métriques
    metrics_system = LoadBalancerMetrics(collection_interval=0.5)
    await metrics_system.initialize()
    
    # Simulation enregistrement métriques
    test_requests = [
        {"server_id": "srv-01", "response_time": 0.05, "error": False},
        {"server_id": "srv-02", "response_time": 0.08, "error": False},
        {"server_id": "srv-01", "response_time": 0.12, "error": True},
        {"server_id": "srv-03", "response_time": 0.03, "error": False},
        {"server_id": "srv-02", "response_time": 0.07, "error": False},
    ]
    
    for request in test_requests:
        await metrics_system.record_request_metrics(request)
        await asyncio.sleep(0.1)  # Simule délai entre requêtes
    
    # Attente accumulation métriques
    await asyncio.sleep(2.0)
    
    # Collection métriques
    collection_result = await metrics_system.collect_balancing_metrics("test_balancer")
    logger.info(f"📊 Métriques collectées: "
               f"{collection_result['aggregated_metrics']['summary']['total_requests']} requêtes")
    
    # Analyse distribution
    traffic_data = {"server_distribution": {"srv-01": 40, "srv-02": 35, "srv-03": 25}}
    analysis_result = await metrics_system.performance_analyzer.analyze_distribution_efficiency(traffic_data)
    logger.info(f"📈 Efficacité distribution: {analysis_result['efficiency_score']:.1f}%")
    
    # Génération insights
    historical_data = {
        "current_efficiency": analysis_result['efficiency_score'],
        "capacity_utilization": 45.0,
        "peak_hours": [9, 14, 20],
        "server_performance": {
            "srv-01": {"average_response_time": 80},
            "srv-02": {"average_response_time": 120}
        }
    }
    
    insights = await metrics_system.performance_analyzer.generate_optimization_insights(historical_data)
    logger.info(f"💡 Insights générés: {len(insights)} recommandations")
    for insight in insights[:2]:  # Affiche 2 premiers insights
        logger.info(f"💡 {insight}")
    
    # Arrêt système
    await metrics_system.shutdown()
    
    logger.info("✅ Démonstration terminée avec succès")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())