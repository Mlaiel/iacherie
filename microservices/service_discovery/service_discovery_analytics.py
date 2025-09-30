"""
📊 SERVICE DISCOVERY ANALYTICS - Module Analytics Service Discovery IA Chérie
========================================================================

**Expert Team**: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
**IP Owner**: Fahed Mlaiel (mlaiel@live.de)
**Copyright**: ©2025 IA Chérie Platform - Tous droits réservés

⚠️  PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
====================================================
Ce code constitue la propriété intellectuelle exclusive de Fahed Mlaiel.
- Email: mlaiel@live.de  
- Projet: IA Chérie Platform
- Licence: Propriétaire - Usage commercial interdit sans autorisation
- Protection: Code source confidentiel

📊 SERVICE DISCOVERY ANALYTICS ENGINE
==================================
Analytics avancés pour service discovery avec ML insights:
- Usage patterns analysis & optimization recommendations
- Capacity planning avec predictive modeling
- Performance trends & anomaly detection
- Service mesh topology analysis
- Cost optimization & resource efficiency
"""

import asyncio
import logging
import time
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
from collections import defaultdict, deque
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

logger = logging.getLogger(__name__)

class AnalyticsType(Enum):
    """Types d'analytics."""
    USAGE_PATTERNS = "usage_patterns"
    PERFORMANCE_TRENDS = "performance_trends"
    CAPACITY_PLANNING = "capacity_planning"
    COST_OPTIMIZATION = "cost_optimization"
    ANOMALY_DETECTION = "anomaly_detection"
    TOPOLOGY_ANALYSIS = "topology_analysis"
    RESOURCE_EFFICIENCY = "resource_efficiency"

class TimeWindow(Enum):
    """Fenêtres temporelles d'analyse."""
    HOUR = "1h"
    DAY = "1d"
    WEEK = "1w"
    MONTH = "1m"
    QUARTER = "3m"

@dataclass
class AnalyticsConfig:
    """Configuration analytics."""
    analytics_type: AnalyticsType
    time_window: TimeWindow
    services_filter: Optional[Set[str]] = None
    regions_filter: Optional[Set[str]] = None
    include_predictions: bool = True
    generate_visualizations: bool = True
    ml_insights: bool = True

@dataclass
class ServiceDiscoveryMetrics:
    """Métriques service discovery."""
    timestamp: datetime
    service_name: str
    region: str
    requests_count: int
    response_time_avg: float
    error_rate: float
    cpu_usage: float
    memory_usage: float
    network_io: float
    cache_hit_rate: float

@dataclass
class AnalyticsResult:
    """Résultat d'analyse."""
    analytics_type: AnalyticsType
    time_window: TimeWindow
    generated_at: datetime
    insights: Dict[str, Any]
    recommendations: List[str]
    visualizations: Dict[str, str] = field(default_factory=dict)  # base64 encoded
    predictions: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0

class ServiceDiscoveryAnalytics:
    """Analytics service discovery avec ML insights."""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis_client = redis_client
        
        # ML Models
        self.usage_clustering_model = KMeans(n_clusters=5, random_state=42)
        self.performance_regression = LinearRegression()
        self.scaler = StandardScaler()
        
        # Cache et données
        self.metrics_cache: Dict[str, List[ServiceDiscoveryMetrics]] = defaultdict(list)
        self.model_cache: Dict[str, Any] = {}
        
        # Configuration
        self.data_retention_days = 90
        self.min_data_points = 100
        self.anomaly_threshold = 2.0  # écarts-types
        
        logger.info("📊 ServiceDiscoveryAnalytics initialisé")
    
    async def analyze_service_discovery_patterns(self, config: AnalyticsConfig) -> AnalyticsResult:
        """Analyse patterns service discovery."""
        try:
            start_time = time.time()
            
            # Collecter données
            metrics_data = await self._collect_metrics_data(config)
            if len(metrics_data) < self.min_data_points:
                return self._create_insufficient_data_result(config)
            
            # Analyser selon type
            if config.analytics_type == AnalyticsType.USAGE_PATTERNS:
                result = await self._analyze_usage_patterns(config, metrics_data)
            elif config.analytics_type == AnalyticsType.PERFORMANCE_TRENDS:
                result = await self._analyze_performance_trends(config, metrics_data)
            elif config.analytics_type == AnalyticsType.CAPACITY_PLANNING:
                result = await self._analyze_capacity_planning(config, metrics_data)
            elif config.analytics_type == AnalyticsType.COST_OPTIMIZATION:
                result = await self._analyze_cost_optimization(config, metrics_data)
            elif config.analytics_type == AnalyticsType.ANOMALY_DETECTION:
                result = await self._analyze_anomalies(config, metrics_data)
            elif config.analytics_type == AnalyticsType.TOPOLOGY_ANALYSIS:
                result = await self._analyze_topology(config, metrics_data)
            elif config.analytics_type == AnalyticsType.RESOURCE_EFFICIENCY:
                result = await self._analyze_resource_efficiency(config, metrics_data)
            else:
                raise ValueError(f"Type analytics non supporté: {config.analytics_type}")
            
            # Calculer confidence score
            result.confidence_score = self._calculate_confidence_score(metrics_data, result)
            
            # Cache résultat
            await self._cache_analytics_result(config, result)
            
            processing_time = time.time() - start_time
            logger.info(f"Analytics {config.analytics_type.value} complétées en {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur analyse patterns discovery: {e}")
            raise
    
    async def _collect_metrics_data(self, config: AnalyticsConfig) -> List[ServiceDiscoveryMetrics]:
        """Collecte données métriques."""
        try:
            # Calculer période
            end_time = datetime.now()
            time_deltas = {
                TimeWindow.HOUR: timedelta(hours=1),
                TimeWindow.DAY: timedelta(days=1),
                TimeWindow.WEEK: timedelta(weeks=1),
                TimeWindow.MONTH: timedelta(days=30),
                TimeWindow.QUARTER: timedelta(days=90)
            }
            start_time = end_time - time_deltas[config.time_window]
            
            # Récupérer métriques Redis
            metrics = []
            current_time = start_time
            
            while current_time <= end_time:
                time_key = current_time.strftime('%Y%m%d_%H%M')
                metrics_keys = await self.redis_client.keys(f"discovery_metrics:{time_key}:*")
                
                for key in metrics_keys:
                    metrics_data = await self.redis_client.get(key)
                    if metrics_data:
                        data = json.loads(metrics_data)
                        
                        # Filtrer selon configuration
                        if config.services_filter and data['service_name'] not in config.services_filter:
                            continue
                        if config.regions_filter and data['region'] not in config.regions_filter:
                            continue
                        
                        metric = ServiceDiscoveryMetrics(
                            timestamp=datetime.fromisoformat(data['timestamp']),
                            service_name=data['service_name'],
                            region=data['region'],
                            requests_count=data['requests_count'],
                            response_time_avg=data['response_time_avg'],
                            error_rate=data['error_rate'],
                            cpu_usage=data['cpu_usage'],
                            memory_usage=data['memory_usage'],
                            network_io=data['network_io'],
                            cache_hit_rate=data['cache_hit_rate']
                        )
                        metrics.append(metric)
                
                current_time += timedelta(minutes=1)
            
            return sorted(metrics, key=lambda m: m.timestamp)
            
        except Exception as e:
            logger.error(f"Erreur collecte données métriques: {e}")
            return []
    
    async def _analyze_usage_patterns(self, config: AnalyticsConfig, 
                                    metrics: List[ServiceDiscoveryMetrics]) -> AnalyticsResult:
        """Analyse patterns d'usage."""
        try:
            # Préparer données pour clustering
            feature_data = []
            for metric in metrics:
                features = [
                    metric.requests_count,
                    metric.response_time_avg,
                    metric.cpu_usage,
                    metric.memory_usage,
                    metric.network_io,
                    metric.cache_hit_rate
                ]
                feature_data.append(features)
            
            # Normaliser données
            X = self.scaler.fit_transform(feature_data)
            
            # Clustering usage patterns
            clusters = self.usage_clustering_model.fit_predict(X)
            
            # Analyser clusters
            cluster_analysis = self._analyze_usage_clusters(metrics, clusters)
            
            # Patterns temporels
            temporal_patterns = self._analyze_temporal_patterns(metrics)
            
            # Recommandations
            recommendations = self._generate_usage_recommendations(cluster_analysis, temporal_patterns)
            
            insights = {
                'cluster_analysis': cluster_analysis,
                'temporal_patterns': temporal_patterns,
                'peak_hours': temporal_patterns['peak_hours'],
                'usage_distribution': temporal_patterns['usage_distribution'],
                'service_popularity': self._calculate_service_popularity(metrics)
            }
            
            # Visualisations si demandées
            visualizations = {}
            if config.generate_visualizations:
                visualizations = await self._generate_usage_visualizations(insights, metrics)
            
            return AnalyticsResult(
                analytics_type=config.analytics_type,
                time_window=config.time_window,
                generated_at=datetime.now(),
                insights=insights,
                recommendations=recommendations,
                visualizations=visualizations
            )
            
        except Exception as e:
            logger.error(f"Erreur analyse usage patterns: {e}")
            raise
    
    async def _analyze_performance_trends(self, config: AnalyticsConfig,
                                        metrics: List[ServiceDiscoveryMetrics]) -> AnalyticsResult:
        """Analyse tendances performance."""
        try:
            # Grouper par service
            service_metrics = defaultdict(list)
            for metric in metrics:
                service_metrics[metric.service_name].append(metric)
            
            # Analyser tendances par service
            trend_analysis = {}
            for service_name, service_data in service_metrics.items():
                trends = self._calculate_performance_trends(service_data)
                trend_analysis[service_name] = trends
            
            # Détecter dégradations
            degradations = self._detect_performance_degradations(trend_analysis)
            
            # Prédictions si ML activé
            predictions = {}
            if config.include_predictions and config.ml_insights:
                predictions = await self._predict_performance_trends(service_metrics)
            
            insights = {
                'trend_analysis': trend_analysis,
                'performance_degradations': degradations,
                'overall_health_score': self._calculate_overall_health_score(trend_analysis),
                'bottleneck_services': self._identify_bottleneck_services(trend_analysis)
            }
            
            recommendations = self._generate_performance_recommendations(
                degradations, trend_analysis
            )
            
            # Visualisations
            visualizations = {}
            if config.generate_visualizations:
                visualizations = await self._generate_performance_visualizations(
                    insights, service_metrics
                )
            
            return AnalyticsResult(
                analytics_type=config.analytics_type,
                time_window=config.time_window,
                generated_at=datetime.now(),
                insights=insights,
                recommendations=recommendations,
                visualizations=visualizations,
                predictions=predictions
            )
            
        except Exception as e:
            logger.error(f"Erreur analyse performance trends: {e}")
            raise
    
    async def _analyze_capacity_planning(self, config: AnalyticsConfig,
                                       metrics: List[ServiceDiscoveryMetrics]) -> AnalyticsResult:
        """Analyse capacity planning."""
        try:
            # Analyser croissance usage
            growth_analysis = self._analyze_usage_growth(metrics)
            
            # Prédire besoins futurs
            capacity_predictions = await self._predict_capacity_needs(metrics, config.time_window)
            
            # Identifier services à risque
            at_risk_services = self._identify_capacity_risks(metrics, capacity_predictions)
            
            # Recommandations scaling
            scaling_recommendations = self._generate_scaling_recommendations(
                capacity_predictions, at_risk_services
            )
            
            insights = {
                'growth_analysis': growth_analysis,
                'capacity_predictions': capacity_predictions,
                'at_risk_services': at_risk_services,
                'resource_utilization': self._analyze_resource_utilization(metrics),
                'scaling_opportunities': self._identify_scaling_opportunities(metrics)
            }
            
            recommendations = scaling_recommendations
            
            # Visualisations capacity planning
            visualizations = {}
            if config.generate_visualizations:
                visualizations = await self._generate_capacity_visualizations(insights, metrics)
            
            return AnalyticsResult(
                analytics_type=config.analytics_type,
                time_window=config.time_window,
                generated_at=datetime.now(),
                insights=insights,
                recommendations=recommendations,
                visualizations=visualizations,
                predictions=capacity_predictions
            )
            
        except Exception as e:
            logger.error(f"Erreur analyse capacity planning: {e}")
            raise
    
    async def _analyze_cost_optimization(self, config: AnalyticsConfig,
                                       metrics: List[ServiceDiscoveryMetrics]) -> AnalyticsResult:
        """Analyse optimization coûts."""
        try:
            # Analyser utilisation ressources
            resource_analysis = self._analyze_resource_costs(metrics)
            
            # Identifier gaspillages
            waste_analysis = self._identify_resource_waste(metrics)
            
            # Opportunités optimization
            optimization_opportunities = self._identify_cost_optimizations(
                resource_analysis, waste_analysis
            )
            
            # Estimation économies
            savings_estimate = self._estimate_cost_savings(optimization_opportunities)
            
            insights = {
                'resource_costs': resource_analysis,
                'waste_analysis': waste_analysis,
                'optimization_opportunities': optimization_opportunities,
                'savings_estimate': savings_estimate,
                'efficiency_scores': self._calculate_efficiency_scores(metrics)
            }
            
            recommendations = self._generate_cost_recommendations(optimization_opportunities)
            
            visualizations = {}
            if config.generate_visualizations:
                visualizations = await self._generate_cost_visualizations(insights)
            
            return AnalyticsResult(
                analytics_type=config.analytics_type,
                time_window=config.time_window,
                generated_at=datetime.now(),
                insights=insights,
                recommendations=recommendations,
                visualizations=visualizations
            )
            
        except Exception as e:
            logger.error(f"Erreur analyse cost optimization: {e}")
            raise
    
    async def _analyze_anomalies(self, config: AnalyticsConfig,
                               metrics: List[ServiceDiscoveryMetrics]) -> AnalyticsResult:
        """Détection anomalies."""
        try:
            # Détecter anomalies par métrique
            anomalies = {}
            
            # Anomalies temps de réponse
            response_time_anomalies = self._detect_response_time_anomalies(metrics)
            anomalies['response_time'] = response_time_anomalies
            
            # Anomalies taux d'erreur
            error_rate_anomalies = self._detect_error_rate_anomalies(metrics)
            anomalies['error_rate'] = error_rate_anomalies
            
            # Anomalies utilisation ressources
            resource_anomalies = self._detect_resource_anomalies(metrics)
            anomalies['resources'] = resource_anomalies
            
            # Scorer sévérité anomalies
            severity_scores = self._score_anomaly_severity(anomalies)
            
            # Prédire anomalies futures
            future_anomalies = {}
            if config.ml_insights:
                future_anomalies = await self._predict_future_anomalies(metrics)
            
            insights = {
                'detected_anomalies': anomalies,
                'severity_scores': severity_scores,
                'anomaly_patterns': self._analyze_anomaly_patterns(anomalies),
                'affected_services': self._identify_affected_services(anomalies)
            }
            
            recommendations = self._generate_anomaly_recommendations(anomalies, severity_scores)
            
            visualizations = {}
            if config.generate_visualizations:
                visualizations = await self._generate_anomaly_visualizations(insights, metrics)
            
            return AnalyticsResult(
                analytics_type=config.analytics_type,
                time_window=config.time_window,
                generated_at=datetime.now(),
                insights=insights,
                recommendations=recommendations,
                visualizations=visualizations,
                predictions=future_anomalies
            )
            
        except Exception as e:
            logger.error(f"Erreur détection anomalies: {e}")
            raise
    
    async def _analyze_topology(self, config: AnalyticsConfig,
                              metrics: List[ServiceDiscoveryMetrics]) -> AnalyticsResult:
        """Analyse topologie service mesh."""
        try:
            # Analyser distribution services
            topology_analysis = self._analyze_service_distribution(metrics)
            
            # Identifier goulots d'étranglement
            bottlenecks = self._identify_topology_bottlenecks(metrics)
            
            # Analyser patterns communication
            communication_patterns = self._analyze_communication_patterns(metrics)
            
            # Recommandations topologie
            topology_recommendations = self._generate_topology_recommendations(
                topology_analysis, bottlenecks, communication_patterns
            )
            
            insights = {
                'service_distribution': topology_analysis,
                'bottlenecks': bottlenecks,
                'communication_patterns': communication_patterns,
                'topology_health': self._assess_topology_health(topology_analysis),
                'optimization_opportunities': self._identify_topology_optimizations(
                    topology_analysis, communication_patterns
                )
            }
            
            recommendations = topology_recommendations
            
            visualizations = {}
            if config.generate_visualizations:
                visualizations = await self._generate_topology_visualizations(insights)
            
            return AnalyticsResult(
                analytics_type=config.analytics_type,
                time_window=config.time_window,
                generated_at=datetime.now(),
                insights=insights,
                recommendations=recommendations,
                visualizations=visualizations
            )
            
        except Exception as e:
            logger.error(f"Erreur analyse topologie: {e}")
            raise
    
    async def _analyze_resource_efficiency(self, config: AnalyticsConfig,
                                         metrics: List[ServiceDiscoveryMetrics]) -> AnalyticsResult:
        """Analyse efficacité ressources."""
        try:
            # Calculer scores efficacité
            efficiency_scores = self._calculate_resource_efficiency_scores(metrics)
            
            # Identifier services inefficaces
            inefficient_services = self._identify_inefficient_services(efficiency_scores)
            
            # Analyser patterns utilisation
            utilization_patterns = self._analyze_utilization_patterns(metrics)
            
            # Recommandations efficacité
            efficiency_recommendations = self._generate_efficiency_recommendations(
                efficiency_scores, inefficient_services, utilization_patterns
            )
            
            insights = {
                'efficiency_scores': efficiency_scores,
                'inefficient_services': inefficient_services,
                'utilization_patterns': utilization_patterns,
                'resource_waste': self._calculate_resource_waste(metrics),
                'optimization_potential': self._calculate_optimization_potential(efficiency_scores)
            }
            
            recommendations = efficiency_recommendations
            
            visualizations = {}
            if config.generate_visualizations:
                visualizations = await self._generate_efficiency_visualizations(insights, metrics)
            
            return AnalyticsResult(
                analytics_type=config.analytics_type,
                time_window=config.time_window,
                generated_at=datetime.now(),
                insights=insights,
                recommendations=recommendations,
                visualizations=visualizations
            )
            
        except Exception as e:
            logger.error(f"Erreur analyse resource efficiency: {e}")
            raise
    
    # Helper methods for analysis
    def _analyze_usage_clusters(self, metrics: List[ServiceDiscoveryMetrics], 
                              clusters: np.ndarray) -> Dict[str, Any]:
        """Analyse clusters d'usage."""
        cluster_stats = defaultdict(list)
        
        for i, metric in enumerate(metrics):
            cluster_id = clusters[i]
            cluster_stats[f"cluster_{cluster_id}"].append({
                'service': metric.service_name,
                'requests': metric.requests_count,
                'response_time': metric.response_time_avg,
                'cpu': metric.cpu_usage,
                'memory': metric.memory_usage
            })
        
        # Calculer statistiques par cluster
        cluster_analysis = {}
        for cluster_id, data in cluster_stats.items():
            cluster_analysis[cluster_id] = {
                'size': len(data),
                'avg_requests': np.mean([d['requests'] for d in data]),
                'avg_response_time': np.mean([d['response_time'] for d in data]),
                'avg_cpu': np.mean([d['cpu'] for d in data]),
                'avg_memory': np.mean([d['memory'] for d in data]),
                'dominant_services': list(set([d['service'] for d in data[:10]]))
            }
        
        return cluster_analysis
    
    def _analyze_temporal_patterns(self, metrics: List[ServiceDiscoveryMetrics]) -> Dict[str, Any]:
        """Analyse patterns temporels."""
        hourly_requests = defaultdict(int)
        daily_requests = defaultdict(int)
        
        for metric in metrics:
            hour = metric.timestamp.hour
            day = metric.timestamp.strftime('%A')
            
            hourly_requests[hour] += metric.requests_count
            daily_requests[day] += metric.requests_count
        
        # Identifier heures de pointe
        max_hour_requests = max(hourly_requests.values()) if hourly_requests else 0
        peak_hours = [hour for hour, requests in hourly_requests.items() 
                     if requests > max_hour_requests * 0.8]
        
        return {
            'hourly_distribution': dict(hourly_requests),
            'daily_distribution': dict(daily_requests),
            'peak_hours': peak_hours,
            'usage_distribution': {
                'peak_ratio': len(peak_hours) / 24 if peak_hours else 0,
                'concentration_score': max_hour_requests / sum(hourly_requests.values()) if sum(hourly_requests.values()) > 0 else 0
            }
        }
    
    def _calculate_service_popularity(self, metrics: List[ServiceDiscoveryMetrics]) -> Dict[str, int]:
        """Calcule popularité services."""
        service_requests = defaultdict(int)
        
        for metric in metrics:
            service_requests[metric.service_name] += metric.requests_count
        
        return dict(sorted(service_requests.items(), key=lambda x: x[1], reverse=True))
    
    def _generate_usage_recommendations(self, cluster_analysis: Dict[str, Any],
                                      temporal_patterns: Dict[str, Any]) -> List[str]:
        """Génère recommandations usage."""
        recommendations = []
        
        # Recommandations basées clusters
        high_load_clusters = [cid for cid, stats in cluster_analysis.items() 
                            if stats['avg_cpu'] > 0.8 or stats['avg_memory'] > 0.8]
        
        if high_load_clusters:
            recommendations.append(
                f"Surveiller clusters haute charge: {', '.join(high_load_clusters)}. "
                "Considérer scaling horizontal."
            )
        
        # Recommandations temporelles
        peak_hours = temporal_patterns.get('peak_hours', [])
        if len(peak_hours) <= 4:  # Concentration sur peu d'heures
            recommendations.append(
                f"Pic d'usage concentré sur {len(peak_hours)} heures. "
                "Considérer auto-scaling basé sur horaires."
            )
        
        # Recommandations efficacité
        concentration = temporal_patterns.get('usage_distribution', {}).get('concentration_score', 0)
        if concentration > 0.3:
            recommendations.append(
                "Usage très concentré temporellement. "
                "Optimiser pour pics de charge et réduire ressources en dehors des pics."
            )
        
        return recommendations
    
    def _create_insufficient_data_result(self, config: AnalyticsConfig) -> AnalyticsResult:
        """Crée résultat pour données insuffisantes."""
        return AnalyticsResult(
            analytics_type=config.analytics_type,
            time_window=config.time_window,
            generated_at=datetime.now(),
            insights={'error': 'Données insuffisantes pour analyse'},
            recommendations=[
                f"Collecter plus de données avant analyse {config.analytics_type.value}",
                f"Minimum {self.min_data_points} points de données requis"
            ],
            confidence_score=0.0
        )
    
    def _calculate_confidence_score(self, metrics: List[ServiceDiscoveryMetrics],
                                  result: AnalyticsResult) -> float:
        """Calcule score de confiance."""
        # Score basé sur quantité de données
        data_score = min(1.0, len(metrics) / (self.min_data_points * 2))
        
        # Score basé sur variété des services
        unique_services = len(set(m.service_name for m in metrics))
        variety_score = min(1.0, unique_services / 10)
        
        # Score basé sur période couverte
        if metrics:
            time_span = (metrics[-1].timestamp - metrics[0].timestamp).total_seconds()
            time_score = min(1.0, time_span / (24 * 3600))  # Normaliser sur 24h
        else:
            time_score = 0.0
        
        return (data_score + variety_score + time_score) / 3
    
    async def _cache_analytics_result(self, config: AnalyticsConfig, result: AnalyticsResult):
        """Cache résultat analytics."""
        try:
            cache_key = f"analytics_result:{config.analytics_type.value}:{config.time_window.value}:{result.generated_at.strftime('%Y%m%d_%H')}"
            
            # Sérialiser résultat (sans visualisations pour économiser espace)
            result_data = {
                'analytics_type': result.analytics_type.value,
                'time_window': result.time_window.value,
                'generated_at': result.generated_at.isoformat(),
                'insights': result.insights,
                'recommendations': result.recommendations,
                'confidence_score': result.confidence_score
            }
            
            # Cache pour 6 heures
            await self.redis_client.setex(
                cache_key,
                6 * 3600,
                json.dumps(result_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Erreur cache analytics result: {e}")
    
    # Placeholder methods pour analyses spécialisées
    def _calculate_performance_trends(self, service_data: List[ServiceDiscoveryMetrics]) -> Dict[str, Any]:
        """Calcule tendances performance."""
        if len(service_data) < 2:
            return {'trend': 'insufficient_data'}
        
        # Tendance temps de réponse
        response_times = [m.response_time_avg for m in service_data]
        response_trend = np.polyfit(range(len(response_times)), response_times, 1)[0]
        
        # Tendance taux d'erreur
        error_rates = [m.error_rate for m in service_data]
        error_trend = np.polyfit(range(len(error_rates)), error_rates, 1)[0]
        
        return {
            'response_time_trend': 'improving' if response_trend < 0 else 'degrading',
            'error_rate_trend': 'improving' if error_trend < 0 else 'degrading',
            'response_time_slope': response_trend,
            'error_rate_slope': error_trend
        }
    
    def _detect_performance_degradations(self, trend_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Détecte dégradations performance."""
        degradations = []
        
        for service, trends in trend_analysis.items():
            if trends.get('response_time_trend') == 'degrading':
                degradations.append({
                    'service': service,
                    'type': 'response_time_degradation',
                    'severity': 'high' if trends.get('response_time_slope', 0) > 0.1 else 'medium'
                })
            
            if trends.get('error_rate_trend') == 'degrading':
                degradations.append({
                    'service': service,
                    'type': 'error_rate_increase',
                    'severity': 'critical' if trends.get('error_rate_slope', 0) > 0.05 else 'high'
                })
        
        return degradations
    
    async def _generate_usage_visualizations(self, insights: Dict[str, Any],
                                           metrics: List[ServiceDiscoveryMetrics]) -> Dict[str, str]:
        """Génère visualisations usage (placeholder)."""
        # Implémentation complète nécessiterait matplotlib/seaborn
        return {
            'usage_clusters': 'base64_encoded_cluster_plot',
            'temporal_patterns': 'base64_encoded_temporal_plot'
        }
    
    # Méthodes supplémentaires (implémentations simplifiées)
    async def _predict_performance_trends(self, service_metrics: Dict[str, List[ServiceDiscoveryMetrics]]) -> Dict[str, Any]:
        """Prédictions tendances performance."""
        return {'placeholder': 'ml_predictions_would_go_here'}
    
    def _calculate_overall_health_score(self, trend_analysis: Dict[str, Any]) -> float:
        """Calcule score santé global."""
        if not trend_analysis:
            return 0.0
        
        improving_count = sum(1 for trends in trend_analysis.values() 
                            if trends.get('response_time_trend') == 'improving')
        total_services = len(trend_analysis)
        
        return improving_count / total_services if total_services > 0 else 0.0
    
    def _identify_bottleneck_services(self, trend_analysis: Dict[str, Any]) -> List[str]:
        """Identifie services goulots d'étranglement."""
        bottlenecks = []
        
        for service, trends in trend_analysis.items():
            if (trends.get('response_time_trend') == 'degrading' and 
                trends.get('response_time_slope', 0) > 0.1):
                bottlenecks.append(service)
        
        return bottlenecks
    
    def _generate_performance_recommendations(self, degradations: List[Dict[str, Any]],
                                            trend_analysis: Dict[str, Any]) -> List[str]:
        """Génère recommandations performance."""
        recommendations = []
        
        critical_degradations = [d for d in degradations if d.get('severity') == 'critical']
        if critical_degradations:
            services = [d['service'] for d in critical_degradations]
            recommendations.append(f"URGENT: Intervention requise sur services: {', '.join(services)}")
        
        high_degradations = [d for d in degradations if d.get('severity') == 'high']
        if high_degradations:
            recommendations.append(f"Surveiller étroitement {len(high_degradations)} services en dégradation")
        
        return recommendations

# Export classes principales
__all__ = [
    'ServiceDiscoveryAnalytics',
    'AnalyticsType',
    'TimeWindow',
    'AnalyticsConfig',
    'AnalyticsResult',
    'ServiceDiscoveryMetrics'
]