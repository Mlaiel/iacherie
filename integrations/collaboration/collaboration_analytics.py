"""
Collaboration Analytics - Collaboration Module
==============================================
Analytics avancés pour collaborations créateurs.
Métriques performance, ROI et insights business.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import statistics

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types de métriques analytics."""
    COLLABORATION_SUCCESS = "collaboration_success"
    REVENUE_IMPACT = "revenue_impact"
    AUDIENCE_GROWTH = "audience_growth"
    ENGAGEMENT_BOOST = "engagement_boost"
    CREATOR_SATISFACTION = "creator_satisfaction"
    PROJECT_COMPLETION = "project_completion"

@dataclass
class CollaborationMetric:
    """Métrique de collaboration."""
    metric_id: str
    collaboration_id: str
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class PerformanceReport:
    """Rapport de performance collaboration."""
    collaboration_id: str
    creators: List[str]
    start_date: datetime
    end_date: Optional[datetime]
    metrics: Dict[MetricType, float]
    insights: List[str]
    recommendations: List[str]
    roi_score: float

class CollaborationAnalytics:
    """
    Système d'analytics pour collaborations.
    Analyse performance et génère insights business.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialise le système d'analytics."""
        self.config = config or {}
        self.metrics_store: Dict[str, List[CollaborationMetric]] = {}
        self.performance_cache: Dict[str, PerformanceReport] = {}
        self.benchmark_data: Dict[str, float] = {}
        self._load_benchmarks()
        logger.info("Collaboration Analytics initialisé")
    
    def _load_benchmarks(self):
        """Charge les données de benchmark."""
        self.benchmark_data = {
            'average_collaboration_success': 0.75,
            'average_revenue_increase': 0.45,
            'average_audience_growth': 0.25,
            'average_engagement_boost': 0.35,
            'completion_rate': 0.82,
            'creator_satisfaction': 0.88
        }
    
    async def track_metric(
        self,
        collaboration_id: str,
        metric_type: MetricType,
        value: float,
        unit: str = "",
        metadata: Dict[str, Any] = None
    ) -> str:
        """Enregistre une métrique de collaboration."""
        metric_id = f"{collaboration_id}_{metric_type.value}_{datetime.now().timestamp()}"
        
        metric = CollaborationMetric(
            metric_id=metric_id,
            collaboration_id=collaboration_id,
            metric_type=metric_type,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        if collaboration_id not in self.metrics_store:
            self.metrics_store[collaboration_id] = []
        
        self.metrics_store[collaboration_id].append(metric)
        
        # Invalider cache si existe
        if collaboration_id in self.performance_cache:
            del self.performance_cache[collaboration_id]
        
        logger.info(f"Métrique trackée: {metric_type.value} = {value} pour {collaboration_id}")
        return metric_id
    
    async def get_collaboration_performance(
        self,
        collaboration_id: str,
        force_refresh: bool = False
    ) -> Optional[PerformanceReport]:
        """Retourne le rapport de performance d'une collaboration."""
        if collaboration_id in self.performance_cache and not force_refresh:
            return self.performance_cache[collaboration_id]
        
        if collaboration_id not in self.metrics_store:
            logger.warning(f"Aucune métrique pour collaboration {collaboration_id}")
            return None
        
        metrics = self.metrics_store[collaboration_id]
        
        # Calculer métriques agrégées
        aggregated_metrics = {}
        for metric_type in MetricType:
            values = [m.value for m in metrics if m.metric_type == metric_type]
            if values:
                aggregated_metrics[metric_type] = statistics.mean(values)
        
        # Générer insights et recommendations
        insights = self._generate_insights(collaboration_id, aggregated_metrics)
        recommendations = self._generate_recommendations(aggregated_metrics)
        
        # Calculer ROI score
        roi_score = self._calculate_roi_score(aggregated_metrics)
        
        # Déterminer dates
        start_date = min(m.timestamp for m in metrics)
        end_date = max(m.timestamp for m in metrics) if len(metrics) > 1 else None
        
        # Extraire créateurs des métadonnées
        creators = self._extract_creators_from_metrics(metrics)
        
        report = PerformanceReport(
            collaboration_id=collaboration_id,
            creators=creators,
            start_date=start_date,
            end_date=end_date,
            metrics=aggregated_metrics,
            insights=insights,
            recommendations=recommendations,
            roi_score=roi_score
        )
        
        # Cache report
        self.performance_cache[collaboration_id] = report
        
        return report
    
    async def get_creator_analytics(
        self,
        creator_id: str,
        time_period: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """Retourne analytics pour un créateur spécifique."""
        end_date = datetime.now()
        start_date = end_date - time_period
        
        # Trouver toutes collaborations du créateur
        creator_collaborations = []
        for collab_id, metrics in self.metrics_store.items():
            creators = self._extract_creators_from_metrics(metrics)
            if creator_id in creators:
                collab_metrics = [m for m in metrics if start_date <= m.timestamp <= end_date]
                if collab_metrics:
                    creator_collaborations.append((collab_id, collab_metrics))
        
        if not creator_collaborations:
            return {
                'creator_id': creator_id,
                'total_collaborations': 0,
                'period_days': time_period.days,
                'metrics': {}
            }
        
        # Agréger métriques
        all_metrics = []
        for _, metrics in creator_collaborations:
            all_metrics.extend(metrics)
        
        aggregated = {}
        for metric_type in MetricType:
            values = [m.value for m in all_metrics if m.metric_type == metric_type]
            if values:
                aggregated[metric_type.value] = {
                    'average': statistics.mean(values),
                    'median': statistics.median(values),
                    'count': len(values),
                    'trend': self._calculate_trend(values)
                }
        
        # Performance vs benchmarks
        performance_vs_benchmark = {}
        for metric_name, data in aggregated.items():
            if metric_name in self.benchmark_data:
                benchmark = self.benchmark_data[metric_name]
                performance_vs_benchmark[metric_name] = {
                    'value': data['average'],
                    'benchmark': benchmark,
                    'performance': (data['average'] / benchmark) - 1 if benchmark > 0 else 0
                }
        
        return {
            'creator_id': creator_id,
            'total_collaborations': len(creator_collaborations),
            'period_days': time_period.days,
            'metrics': aggregated,
            'performance_vs_benchmark': performance_vs_benchmark,
            'overall_score': self._calculate_creator_score(aggregated)
        }
    
    async def get_platform_analytics(
        self,
        time_period: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """Retourne analytics globales de la plateforme."""
        end_date = datetime.now()
        start_date = end_date - time_period
        
        # Collecter toutes métriques de la période
        all_metrics = []
        active_collaborations = set()
        
        for collab_id, metrics in self.metrics_store.items():
            period_metrics = [m for m in metrics if start_date <= m.timestamp <= end_date]
            if period_metrics:
                all_metrics.extend(period_metrics)
                active_collaborations.add(collab_id)
        
        if not all_metrics:
            return {
                'period_days': time_period.days,
                'total_collaborations': 0,
                'metrics': {}
            }
        
        # Agréger par type de métrique
        platform_metrics = {}
        for metric_type in MetricType:
            values = [m.value for m in all_metrics if m.metric_type == metric_type]
            if values:
                platform_metrics[metric_type.value] = {
                    'total_measurements': len(values),
                    'average': statistics.mean(values),
                    'median': statistics.median(values),
                    'min': min(values),
                    'max': max(values),
                    'std_dev': statistics.stdev(values) if len(values) > 1 else 0
                }
        
        # Top performers
        top_collaborations = await self._get_top_collaborations(
            list(active_collaborations), limit=10
        )
        
        # Tendances
        trends = await self._calculate_platform_trends(all_metrics, time_period)
        
        return {
            'period_days': time_period.days,
            'total_collaborations': len(active_collaborations),
            'total_metrics': len(all_metrics),
            'metrics': platform_metrics,
            'top_collaborations': top_collaborations,
            'trends': trends,
            'health_score': self._calculate_platform_health_score(platform_metrics)
        }
    
    def _generate_insights(
        self,
        collaboration_id: str,
        metrics: Dict[MetricType, float]
    ) -> List[str]:
        """Génère des insights basés sur les métriques."""
        insights = []
        
        # Insights basés sur performance
        success_rate = metrics.get(MetricType.COLLABORATION_SUCCESS, 0)
        if success_rate > 0.8:
            insights.append("Collaboration très réussie - excellent matching créateurs")
        elif success_rate < 0.5:
            insights.append("Performance faible - revoir compatibilité créateurs")
        
        # Insights revenue
        revenue_impact = metrics.get(MetricType.REVENUE_IMPACT, 0)
        if revenue_impact > 0.5:
            insights.append(f"Impact revenue positif (+{revenue_impact:.1%})")
        
        # Insights audience
        audience_growth = metrics.get(MetricType.AUDIENCE_GROWTH, 0)
        if audience_growth > 0.3:
            insights.append("Excellent growth audience grâce à synergie")
        
        # Insights engagement
        engagement_boost = metrics.get(MetricType.ENGAGEMENT_BOOST, 0)
        if engagement_boost > 0.4:
            insights.append("Boost engagement significatif observé")
        
        return insights
    
    def _generate_recommendations(
        self,
        metrics: Dict[MetricType, float]
    ) -> List[str]:
        """Génère des recommandations d'amélioration."""
        recommendations = []
        
        success_rate = metrics.get(MetricType.COLLABORATION_SUCCESS, 0)
        if success_rate < 0.7:
            recommendations.append("Améliorer le matching IA pour meilleure compatibilité")
        
        revenue_impact = metrics.get(MetricType.REVENUE_IMPACT, 0)
        if revenue_impact < 0.2:
            recommendations.append("Optimiser stratégie monétisation collaborative")
        
        engagement_boost = metrics.get(MetricType.ENGAGEMENT_BOOST, 0)
        if engagement_boost < 0.2:
            recommendations.append("Travailler sur synergie audience et contenu")
        
        completion_rate = metrics.get(MetricType.PROJECT_COMPLETION, 0)
        if completion_rate < 0.8:
            recommendations.append("Améliorer project management et communication")
        
        return recommendations
    
    def _calculate_roi_score(self, metrics: Dict[MetricType, float]) -> float:
        """Calcule un score ROI global."""
        weights = {
            MetricType.REVENUE_IMPACT: 0.4,
            MetricType.AUDIENCE_GROWTH: 0.25,
            MetricType.ENGAGEMENT_BOOST: 0.2,
            MetricType.COLLABORATION_SUCCESS: 0.15
        }
        
        roi_score = 0
        total_weight = 0
        
        for metric_type, weight in weights.items():
            if metric_type in metrics:
                roi_score += metrics[metric_type] * weight
                total_weight += weight
        
        return roi_score / total_weight if total_weight > 0 else 0
    
    def _extract_creators_from_metrics(self, metrics: List[CollaborationMetric]) -> List[str]:
        """Extrait la liste des créateurs des métadonnées."""
        creators = set()
        for metric in metrics:
            if 'creators' in metric.metadata:
                creators.update(metric.metadata['creators'])
            elif 'creator_id' in metric.metadata:
                creators.add(metric.metadata['creator_id'])
        return list(creators)
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calcule la tendance d'une série de valeurs."""
        if len(values) < 2:
            return "stable"
        
        # Simple calcul de tendance
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        avg_first = statistics.mean(first_half)
        avg_second = statistics.mean(second_half)
        
        change = (avg_second - avg_first) / avg_first if avg_first > 0 else 0
        
        if change > 0.1:
            return "increasing"
        elif change < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_creator_score(self, metrics: Dict[str, Any]) -> float:
        """Calcule un score global pour un créateur."""
        # Score basé sur performance moyenne vs benchmarks
        scores = []
        
        for metric_name, data in metrics.items():
            if metric_name in self.benchmark_data:
                benchmark = self.benchmark_data[metric_name]
                if benchmark > 0:
                    score = min(1.0, data['average'] / benchmark)
                    scores.append(score)
        
        return statistics.mean(scores) if scores else 0.5
    
    async def _get_top_collaborations(
        self,
        collaboration_ids: List[str],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retourne les meilleures collaborations."""
        collaboration_scores = []
        
        for collab_id in collaboration_ids:
            report = await self.get_collaboration_performance(collab_id)
            if report:
                collaboration_scores.append({
                    'collaboration_id': collab_id,
                    'roi_score': report.roi_score,
                    'creators': report.creators,
                    'key_metrics': {
                        k.value: v for k, v in report.metrics.items()
                    }
                })
        
        # Trier par ROI score
        collaboration_scores.sort(key=lambda x: x['roi_score'], reverse=True)
        return collaboration_scores[:limit]
    
    async def _calculate_platform_trends(
        self,
        metrics: List[CollaborationMetric],
        time_period: timedelta
    ) -> Dict[str, Any]:
        """Calcule les tendances plateforme."""
        # Grouper métriques par semaine
        weekly_data = {}
        
        for metric in metrics:
            week_start = metric.timestamp - timedelta(days=metric.timestamp.weekday())
            week_key = week_start.strftime('%Y-W%U')
            
            if week_key not in weekly_data:
                weekly_data[week_key] = {mt: [] for mt in MetricType}
            
            weekly_data[week_key][metric.metric_type].append(metric.value)
        
        # Calculer tendances par type
        trends = {}
        for metric_type in MetricType:
            weekly_averages = []
            for week_data in weekly_data.values():
                if weekly_data[metric_type]:
                    weekly_averages.append(statistics.mean(weekly_data[metric_type]))
            
            if len(weekly_averages) >= 2:
                trends[metric_type.value] = self._calculate_trend(weekly_averages)
            else:
                trends[metric_type.value] = "insufficient_data"
        
        return trends
    
    def _calculate_platform_health_score(
        self,
        platform_metrics: Dict[str, Any]
    ) -> float:
        """Calcule un score de santé global de la plateforme."""
        health_factors = []
        
        # Facteurs de santé basés sur benchmarks
        for metric_name, data in platform_metrics.items():
            if metric_name in self.benchmark_data:
                benchmark = self.benchmark_data[metric_name]
                if benchmark > 0:
                    health_score = min(1.0, data['average'] / benchmark)
                    health_factors.append(health_score)
        
        return statistics.mean(health_factors) if health_factors else 0.5