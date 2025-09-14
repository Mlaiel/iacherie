"""
📊 Content Analytics Service - Analytics de Contenu Enterprise
© Fahed Mlaiel 2024-2025 - Ainflue Microservices Enterprise

Service spécialisé d'analytics avancée pour performance et engagement du contenu.
Analytics temps réel avec IA prédictive et insights automatiques.
"""

import asyncio
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import logging
import json
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


@dataclass
class ContentMetrics:
    """Métriques de performance du contenu"""
    content_id: str
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    downloads: int = 0
    engagement_rate: float = 0.0
    watch_time: float = 0.0
    completion_rate: float = 0.0
    click_through_rate: float = 0.0
    conversion_rate: float = 0.0


@dataclass
class AudienceInsights:
    """Insights sur l'audience"""
    demographics: Dict[str, Any]
    geographic_distribution: Dict[str, float]
    platform_preferences: Dict[str, float]
    engagement_patterns: Dict[str, Any]
    peak_activity_hours: List[int]


class ContentAnalyticsService:
    """Service d'analytics avancée pour contenu"""
    
    def __init__(self):
        self.metrics_cache = {}
        self.insights_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Seuils pour les alertes
        self.performance_thresholds = {
            'engagement_rate': {'low': 0.02, 'high': 0.08},
            'completion_rate': {'low': 0.3, 'high': 0.7},
            'ctr': {'low': 0.01, 'high': 0.05}
        }
    
    async def get_content_analytics(
        self,
        content_id: str,
        time_range: str = "7d",
        include_predictions: bool = True
    ) -> Dict[str, Any]:
        """Obtient les analytics complètes pour un contenu"""
        try:
            # Vérifier le cache
            cache_key = f"{content_id}_{time_range}"
            if self._is_cache_valid(cache_key):
                return self.metrics_cache[cache_key]['data']
            
            # Récupérer les métriques de base
            base_metrics = await self._fetch_base_metrics(content_id, time_range)
            
            # Calculer les métriques dérivées
            derived_metrics = await self._calculate_derived_metrics(base_metrics)
            
            # Analytics comparative
            comparative_analytics = await self._get_comparative_analytics(
                content_id, base_metrics
            )
            
            # Analyse de tendances
            trend_analysis = await self._analyze_trends(content_id, time_range)
            
            # Insights automatiques
            auto_insights = await self._generate_insights(
                base_metrics, derived_metrics, trend_analysis
            )
            
            # Prédictions si demandées
            predictions = {}
            if include_predictions:
                predictions = await self._generate_predictions(content_id, base_metrics)
            
            result = {
                'content_id': content_id,
                'time_range': time_range,
                'generated_at': datetime.utcnow().isoformat(),
                'base_metrics': base_metrics,
                'derived_metrics': derived_metrics,
                'comparative_analytics': comparative_analytics,
                'trend_analysis': trend_analysis,
                'insights': auto_insights,
                'predictions': predictions,
                'performance_alerts': await self._check_performance_alerts(derived_metrics)
            }
            
            # Mettre en cache
            self._cache_result(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur analytics contenu {content_id}: {e}")
            return {
                'content_id': content_id,
                'error': str(e),
                'generated_at': datetime.utcnow().isoformat()
            }
    
    async def _fetch_base_metrics(
        self,
        content_id: str,
        time_range: str
    ) -> ContentMetrics:
        """Récupère les métriques de base depuis les sources de données"""
        # Simuler récupération depuis base de données/APIs
        # En production, ceci ferait des appels réels aux DBs
        
        base_metrics = ContentMetrics(
            content_id=content_id,
            views=np.random.randint(100, 10000),
            likes=np.random.randint(10, 1000),
            shares=np.random.randint(5, 500),
            comments=np.random.randint(2, 200),
            downloads=np.random.randint(0, 100),
            watch_time=np.random.uniform(30, 300),
            engagement_rate=np.random.uniform(0.01, 0.1),
            completion_rate=np.random.uniform(0.2, 0.9),
            click_through_rate=np.random.uniform(0.005, 0.08),
            conversion_rate=np.random.uniform(0.001, 0.05)
        )
        
        return base_metrics
    
    async def _calculate_derived_metrics(
        self,
        base_metrics: ContentMetrics
    ) -> Dict[str, Any]:
        """Calcule des métriques dérivées avancées"""
        
        derived = {}
        
        # Score d'engagement global
        derived['engagement_score'] = (
            (base_metrics.likes + base_metrics.shares * 2 + base_metrics.comments * 3) /
            max(base_metrics.views, 1) * 100
        )
        
        # Indice de qualité du contenu
        derived['content_quality_index'] = (
            base_metrics.completion_rate * 0.4 +
            base_metrics.engagement_rate * 0.3 +
            (base_metrics.likes / max(base_metrics.views, 1)) * 0.3
        ) * 100
        
        # Score de viralité
        derived['virality_score'] = (
            base_metrics.shares / max(base_metrics.views, 1) * 1000
        )
        
        # Taux de rétention
        derived['retention_rate'] = (
            base_metrics.completion_rate * base_metrics.watch_time / 100
        )
        
        # Performance relative
        derived['performance_percentile'] = await self._calculate_performance_percentile(
            base_metrics
        )
        
        return derived
    
    async def _get_comparative_analytics(
        self,
        content_id: str,
        metrics: ContentMetrics
    ) -> Dict[str, Any]:
        """Analytics comparative avec d'autres contenus similaires"""
        
        # Simuler comparaison avec contenus similaires
        similar_content_avg = {
            'views': np.random.randint(500, 5000),
            'engagement_rate': np.random.uniform(0.02, 0.06),
            'completion_rate': np.random.uniform(0.3, 0.6)
        }
        
        comparison = {}
        
        # Comparaison des vues
        comparison['views_vs_average'] = (
            (metrics.views - similar_content_avg['views']) / 
            similar_content_avg['views'] * 100
        )
        
        # Comparaison engagement
        comparison['engagement_vs_average'] = (
            (metrics.engagement_rate - similar_content_avg['engagement_rate']) /
            similar_content_avg['engagement_rate'] * 100
        )
        
        # Comparaison completion
        comparison['completion_vs_average'] = (
            (metrics.completion_rate - similar_content_avg['completion_rate']) /
            similar_content_avg['completion_rate'] * 100
        )
        
        # Ranking estimé
        comparison['estimated_ranking'] = np.random.randint(1, 100)
        comparison['category'] = await self._determine_performance_category(metrics)
        
        return comparison
    
    async def _analyze_trends(
        self,
        content_id: str,
        time_range: str
    ) -> Dict[str, Any]:
        """Analyse les tendances de performance"""
        
        # Simuler données de tendance
        days = int(time_range.replace('d', ''))
        time_series = []
        
        for i in range(days):
            day_metrics = {
                'date': (datetime.utcnow() - timedelta(days=days-i)).isoformat()[:10],
                'views': np.random.randint(50, 500),
                'engagement_rate': np.random.uniform(0.01, 0.08)
            }
            time_series.append(day_metrics)
        
        # Calculer tendances
        views_trend = np.polyfit(range(len(time_series)), 
                               [d['views'] for d in time_series], 1)[0]
        engagement_trend = np.polyfit(range(len(time_series)),
                                    [d['engagement_rate'] for d in time_series], 1)[0]
        
        return {
            'time_series': time_series,
            'views_trend': 'increasing' if views_trend > 0 else 'decreasing',
            'views_trend_strength': abs(views_trend),
            'engagement_trend': 'increasing' if engagement_trend > 0 else 'decreasing',
            'engagement_trend_strength': abs(engagement_trend),
            'peak_performance_day': max(time_series, key=lambda x: x['views'])['date']
        }
    
    async def _generate_insights(
        self,
        base_metrics: ContentMetrics,
        derived_metrics: Dict[str, Any],
        trend_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Génère des insights automatiques"""
        
        insights = []
        
        # Insight sur la performance
        if derived_metrics['engagement_score'] > 5:
            insights.append({
                'type': 'positive',
                'category': 'engagement',
                'message': 'Excellent taux d\'engagement détecté',
                'recommendation': 'Considérer ce contenu comme modèle pour futurs créations'
            })
        elif derived_metrics['engagement_score'] < 1:
            insights.append({
                'type': 'warning',
                'category': 'engagement',
                'message': 'Taux d\'engagement faible',
                'recommendation': 'Analyser les éléments qui peuvent être améliorés'
            })
        
        # Insight sur la viralité
        if derived_metrics['virality_score'] > 10:
            insights.append({
                'type': 'positive',
                'category': 'viral',
                'message': 'Potentiel viral élevé détecté',
                'recommendation': 'Amplifier la promotion sur les plateformes sociales'
            })
        
        # Insight sur les tendances
        if trend_analysis['views_trend'] == 'increasing':
            insights.append({
                'type': 'positive',
                'category': 'growth',
                'message': 'Croissance positive des vues observée',
                'recommendation': 'Maintenir la stratégie actuelle de promotion'
            })
        
        # Insight sur la rétention
        if base_metrics.completion_rate > 0.7:
            insights.append({
                'type': 'positive',
                'category': 'retention',
                'message': 'Excellent taux de rétention',
                'recommendation': 'Format et durée optimaux pour l\'audience'
            })
        
        return insights
    
    async def _generate_predictions(
        self,
        content_id: str,
        metrics: ContentMetrics
    ) -> Dict[str, Any]:
        """Génère des prédictions basées sur l'IA"""
        
        # Prédictions simplifiées (à remplacer par modèles ML réels)
        predictions = {}
        
        # Prédiction vues 7 prochains jours
        current_daily_views = metrics.views / 7  # Approximation
        growth_factor = np.random.uniform(0.8, 1.3)
        predictions['views_next_7_days'] = int(current_daily_views * 7 * growth_factor)
        
        # Prédiction engagement
        predictions['engagement_prediction'] = {
            'next_week': metrics.engagement_rate * np.random.uniform(0.9, 1.2),
            'confidence': np.random.uniform(0.6, 0.9)
        }
        
        # Prédiction peak performance
        predictions['peak_performance_estimate'] = {
            'estimated_peak_views': int(metrics.views * np.random.uniform(1.5, 3.0)),
            'time_to_peak': f"{np.random.randint(1, 14)} jours"
        }
        
        # Score de potentiel global
        predictions['potential_score'] = min(
            (metrics.engagement_rate * 50 + 
             metrics.completion_rate * 30 + 
             (metrics.shares / max(metrics.views, 1)) * 1000), 100
        )
        
        return predictions
    
    async def _check_performance_alerts(
        self,
        derived_metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Vérifie et génère des alertes de performance"""
        
        alerts = []
        
        # Alerte engagement faible
        if derived_metrics['engagement_score'] < 1:
            alerts.append({
                'type': 'warning',
                'severity': 'medium',
                'metric': 'engagement_score',
                'value': derived_metrics['engagement_score'],
                'threshold': 1,
                'message': 'Engagement en dessous du seuil critique'
            })
        
        # Alerte performance exceptionnelle
        if derived_metrics['content_quality_index'] > 80:
            alerts.append({
                'type': 'success',
                'severity': 'info',
                'metric': 'content_quality_index',
                'value': derived_metrics['content_quality_index'],
                'threshold': 80,
                'message': 'Performance exceptionnelle détectée'
            })
        
        return alerts
    
    async def _calculate_performance_percentile(
        self,
        metrics: ContentMetrics
    ) -> float:
        """Calcule le percentile de performance"""
        # Simulation - en production, comparer avec distribution réelle
        score = (
            metrics.engagement_rate * 100 +
            metrics.completion_rate * 50 +
            (metrics.likes / max(metrics.views, 1)) * 200
        )
        
        # Normaliser en percentile
        return min(max(score * 5, 0), 100)
    
    async def _determine_performance_category(
        self,
        metrics: ContentMetrics
    ) -> str:
        """Détermine la catégorie de performance"""
        
        engagement_score = (
            (metrics.likes + metrics.shares * 2 + metrics.comments * 3) /
            max(metrics.views, 1) * 100
        )
        
        if engagement_score > 5:
            return 'top_performer'
        elif engagement_score > 2:
            return 'good_performer'
        elif engagement_score > 0.5:
            return 'average_performer'
        else:
            return 'underperformer'
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Vérifie si le cache est encore valide"""
        if cache_key not in self.metrics_cache:
            return False
        
        cached_time = self.metrics_cache[cache_key]['timestamp']
        return (datetime.utcnow() - cached_time).seconds < self.cache_ttl
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Met en cache le résultat"""
        self.metrics_cache[cache_key] = {
            'data': result,
            'timestamp': datetime.utcnow()
        }
    
    async def get_audience_insights(
        self,
        content_id: str,
        time_range: str = "30d"
    ) -> AudienceInsights:
        """Obtient les insights sur l'audience"""
        
        # Simuler données d'audience
        return AudienceInsights(
            demographics={
                'age_groups': {
                    '18-24': 0.25,
                    '25-34': 0.35,
                    '35-44': 0.25,
                    '45+': 0.15
                },
                'gender': {
                    'male': 0.52,
                    'female': 0.48
                }
            },
            geographic_distribution={
                'US': 0.35,
                'UK': 0.15,
                'CA': 0.12,
                'AU': 0.08,
                'DE': 0.10,
                'FR': 0.08,
                'Other': 0.12
            },
            platform_preferences={
                'youtube': 0.40,
                'instagram': 0.25,
                'tiktok': 0.20,
                'facebook': 0.15
            },
            engagement_patterns={
                'peak_engagement_time': '20:00-22:00',
                'avg_session_duration': 245,
                'return_viewer_rate': 0.34
            },
            peak_activity_hours=[19, 20, 21, 22]
        )
    
    async def generate_performance_report(
        self,
        content_ids: List[str],
        time_range: str = "30d"
    ) -> Dict[str, Any]:
        """Génère un rapport de performance pour multiple contenus"""
        
        reports = []
        
        for content_id in content_ids:
            analytics = await self.get_content_analytics(
                content_id, time_range, include_predictions=False
            )
            reports.append(analytics)
        
        # Agrégations globales
        total_views = sum(r.get('base_metrics', {}).get('views', 0) for r in reports)
        avg_engagement = np.mean([
            r.get('base_metrics', {}).get('engagement_rate', 0) for r in reports
        ])
        
        return {
            'report_generated_at': datetime.utcnow().isoformat(),
            'time_range': time_range,
            'content_count': len(content_ids),
            'global_metrics': {
                'total_views': total_views,
                'average_engagement_rate': avg_engagement,
                'top_performer': max(reports, key=lambda x: x.get('derived_metrics', {}).get('engagement_score', 0))['content_id'],
                'improvement_opportunities': len([r for r in reports if r.get('derived_metrics', {}).get('engagement_score', 0) < 2])
            },
            'individual_reports': reports
        }


# Instance globale du service
content_analytics_service = ContentAnalyticsService()