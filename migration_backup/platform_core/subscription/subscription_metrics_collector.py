"""🚀 Platform Core Subscription - Subscription Metrics Collector
================================================================
Module: backend/platform_core/subscription/subscription_metrics_collector.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🚨 AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

🎯 COLLECTEUR MÉTRIQUES BUSINESS ENTERPRISE
Collecte et analyse de métriques business avancées
- KPIs subscription en temps réel
- Métriques financières et opérationnelles
- Analytics comportementales créateurs
- Dashboards business intelligence
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import logging
import asyncio
import json
from decimal import Decimal
import numpy as np
import pandas as pd
from collections import defaultdict

# Configure logging
logger = logging.getLogger(__name__)


class MetricCategory(Enum):
    """Catégories de métriques"""
    REVENUE = "revenue"
    GROWTH = "growth"
    RETENTION = "retention"
    ENGAGEMENT = "engagement"
    OPERATIONAL = "operational"
    CUSTOMER_SUCCESS = "customer_success"


class MetricFrequency(Enum):
    """Fréquences de collecte"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class MetricDefinition:
    """Définition d'une métrique"""
    metric_id: str
    name: str
    description: str
    category: MetricCategory
    frequency: MetricFrequency
    calculation_method: str
    target_value: Optional[float]
    warning_threshold: Optional[float]
    critical_threshold: Optional[float]


@dataclass
class MetricValue:
    """Valeur d'une métrique"""
    metric_id: str
    timestamp: datetime
    value: float
    dimensions: Dict[str, Any]
    context: Dict[str, Any]


@dataclass
class BusinessDashboard:
    """Dashboard business avec métriques"""
    dashboard_id: str
    name: str
    metrics: List[MetricValue]
    kpis: Dict[str, float]
    trends: Dict[str, float]
    alerts: List[str]
    last_update: datetime


class SubscriptionMetricsCollector:
    """🚀 Collecteur Métriques Business Enterprise
    
    Système avancé de collecte et analyse de métriques business
    pour optimisation des performances subscription.
    """
    
    def __init__(self):
        """Initialise le collecteur de métriques"""
        self.metric_definitions = {}
        self.metric_cache = {}
        self.real_time_metrics = {}
        self.aggregated_metrics = {}
        
        # Configuration des métriques principales
        self._initialize_core_metrics()
        
        # Cache pour optimisation des performances
        self.calculation_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        logger.info("🚀 Subscription Metrics Collector initialized")
    
    def _initialize_core_metrics(self):
        """Initialise les métriques principales"""
        
        # Métriques de revenus
        self.metric_definitions.update({
            'mrr': MetricDefinition(
                metric_id='mrr',
                name='Monthly Recurring Revenue',
                description='Revenus récurrents mensuels',
                category=MetricCategory.REVENUE,
                frequency=MetricFrequency.DAILY,
                calculation_method='sum_active_subscriptions',
                target_value=100000.0,
                warning_threshold=80000.0,
                critical_threshold=60000.0
            ),
            'arr': MetricDefinition(
                metric_id='arr',
                name='Annual Recurring Revenue',
                description='Revenus récurrents annuels',
                category=MetricCategory.REVENUE,
                frequency=MetricFrequency.MONTHLY,
                calculation_method='mrr_x_12',
                target_value=1200000.0,
                warning_threshold=960000.0,
                critical_threshold=720000.0
            ),
            'arpu': MetricDefinition(
                metric_id='arpu',
                name='Average Revenue Per User',
                description='Revenu moyen par utilisateur',
                category=MetricCategory.REVENUE,
                frequency=MetricFrequency.DAILY,
                calculation_method='total_revenue_div_active_users',
                target_value=50.0,
                warning_threshold=40.0,
                critical_threshold=30.0
            )
        })
        
        # Métriques de croissance
        self.metric_definitions.update({
            'new_subscriptions': MetricDefinition(
                metric_id='new_subscriptions',
                name='New Subscriptions',
                description='Nouveaux abonnements',
                category=MetricCategory.GROWTH,
                frequency=MetricFrequency.DAILY,
                calculation_method='count_new_subscriptions',
                target_value=100.0,
                warning_threshold=50.0,
                critical_threshold=25.0
            ),
            'subscription_growth_rate': MetricDefinition(
                metric_id='subscription_growth_rate',
                name='Subscription Growth Rate',
                description='Taux de croissance des abonnements',
                category=MetricCategory.GROWTH,
                frequency=MetricFrequency.MONTHLY,
                calculation_method='calculate_growth_rate',
                target_value=10.0,
                warning_threshold=5.0,
                critical_threshold=0.0
            ),
            'ltv': MetricDefinition(
                metric_id='ltv',
                name='Customer Lifetime Value',
                description='Valeur vie client',
                category=MetricCategory.REVENUE,
                frequency=MetricFrequency.MONTHLY,
                calculation_method='calculate_ltv',
                target_value=500.0,
                warning_threshold=300.0,
                critical_threshold=200.0
            )
        })
        
        # Métriques de rétention
        self.metric_definitions.update({
            'churn_rate': MetricDefinition(
                metric_id='churn_rate',
                name='Churn Rate',
                description='Taux de désabonnement',
                category=MetricCategory.RETENTION,
                frequency=MetricFrequency.DAILY,
                calculation_method='calculate_churn_rate',
                target_value=2.0,
                warning_threshold=5.0,
                critical_threshold=10.0
            ),
            'retention_rate': MetricDefinition(
                metric_id='retention_rate',
                name='Retention Rate',
                description='Taux de rétention',
                category=MetricCategory.RETENTION,
                frequency=MetricFrequency.MONTHLY,
                calculation_method='calculate_retention_rate',
                target_value=95.0,
                warning_threshold=90.0,
                critical_threshold=85.0
            )
        })
        
        # Métriques d'engagement
        self.metric_definitions.update({
            'daily_active_creators': MetricDefinition(
                metric_id='daily_active_creators',
                name='Daily Active Creators',
                description='Créateurs actifs quotidiens',
                category=MetricCategory.ENGAGEMENT,
                frequency=MetricFrequency.DAILY,
                calculation_method='count_active_creators',
                target_value=1000.0,
                warning_threshold=800.0,
                critical_threshold=600.0
            ),
            'content_creation_rate': MetricDefinition(
                metric_id='content_creation_rate',
                name='Content Creation Rate',
                description='Taux de création de contenu',
                category=MetricCategory.ENGAGEMENT,
                frequency=MetricFrequency.DAILY,
                calculation_method='calculate_content_rate',
                target_value=2.5,
                warning_threshold=2.0,
                critical_threshold=1.5
            )
        })
    
    async def collect_metric(self, metric_id: str, timestamp: Optional[datetime] = None) -> MetricValue:
        """Collecte une métrique spécifique"""
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            # Vérification du cache
            cache_key = f"{metric_id}_{timestamp.strftime('%Y%m%d%H%M')}"
            if cache_key in self.calculation_cache:
                cached_value, cache_time = self.calculation_cache[cache_key]
                if (datetime.now() - cache_time).seconds < self.cache_ttl:
                    return cached_value
            
            metric_def = self.metric_definitions.get(metric_id)
            if not metric_def:
                raise ValueError(f"Metric definition not found: {metric_id}")
            
            # Calcul de la métrique
            value = await self._calculate_metric_value(metric_def, timestamp)
            
            # Contexte additionnel
            context = await self._gather_metric_context(metric_def, timestamp)
            
            # Dimensions pour segmentation
            dimensions = await self._gather_metric_dimensions(metric_def, timestamp)
            
            metric_value = MetricValue(
                metric_id=metric_id,
                timestamp=timestamp,
                value=value,
                dimensions=dimensions,
                context=context
            )
            
            # Mise en cache
            self.calculation_cache[cache_key] = (metric_value, datetime.now())
            
            # Stockage pour aggregation
            self._store_metric_value(metric_value)
            
            logger.debug(f"✅ Metric collected: {metric_id} = {value}")
            return metric_value
            
        except Exception as e:
            logger.error(f"❌ Error collecting metric {metric_id}: {e}")
            return None
    
    async def _calculate_metric_value(self, metric_def: MetricDefinition, timestamp: datetime) -> float:
        """Calcule la valeur d'une métrique"""
        method = metric_def.calculation_method
        
        # Simulation des calculs (à remplacer par vraies requêtes DB)
        if method == 'sum_active_subscriptions':
            return await self._calculate_mrr(timestamp)
        elif method == 'mrr_x_12':
            mrr = await self._calculate_mrr(timestamp)
            return mrr * 12
        elif method == 'total_revenue_div_active_users':
            return await self._calculate_arpu(timestamp)
        elif method == 'count_new_subscriptions':
            return await self._count_new_subscriptions(timestamp)
        elif method == 'calculate_growth_rate':
            return await self._calculate_growth_rate(timestamp)
        elif method == 'calculate_ltv':
            return await self._calculate_ltv(timestamp)
        elif method == 'calculate_churn_rate':
            return await self._calculate_churn_rate(timestamp)
        elif method == 'calculate_retention_rate':
            return await self._calculate_retention_rate(timestamp)
        elif method == 'count_active_creators':
            return await self._count_active_creators(timestamp)
        elif method == 'calculate_content_rate':
            return await self._calculate_content_rate(timestamp)
        else:
            logger.warning(f"Unknown calculation method: {method}")
            return 0.0
    
    async def _calculate_mrr(self, timestamp: datetime) -> float:
        """Calcule le MRR (Monthly Recurring Revenue)"""
        # Simulation - à remplacer par vraie logique
        base_mrr = 50000.0
        growth_factor = 1 + (timestamp.month - 1) * 0.05  # Croissance simulée
        variance = np.random.normal(0, 0.1)  # Variance réaliste
        return base_mrr * growth_factor * (1 + variance)
    
    async def _calculate_arpu(self, timestamp: datetime) -> float:
        """Calcule l'ARPU (Average Revenue Per User)"""
        mrr = await self._calculate_mrr(timestamp)
        active_users = await self._count_active_users(timestamp)
        return mrr / active_users if active_users > 0 else 0.0
    
    async def _count_active_users(self, timestamp: datetime) -> float:
        """Compte les utilisateurs actifs"""
        # Simulation - croissance avec saisonnalité
        base_users = 1000.0
        seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * timestamp.month / 12)
        growth = 1 + (timestamp.month - 1) * 0.08
        return base_users * seasonal_factor * growth
    
    async def _count_new_subscriptions(self, timestamp: datetime) -> float:
        """Compte les nouveaux abonnements"""
        # Simulation avec tendance et saisonnalité
        base_new = 50.0
        day_factor = 1.2 if timestamp.weekday() < 5 else 0.8  # Plus élevé en semaine
        seasonal = 1 + 0.2 * np.sin(2 * np.pi * timestamp.month / 12)
        variance = np.random.normal(0, 0.15)
        return max(0, base_new * day_factor * seasonal * (1 + variance))
    
    async def _calculate_growth_rate(self, timestamp: datetime) -> float:
        """Calcule le taux de croissance"""
        current_month_subs = await self._count_active_users(timestamp)
        last_month = timestamp - timedelta(days=30)
        last_month_subs = await self._count_active_users(last_month)
        
        if last_month_subs > 0:
            growth_rate = ((current_month_subs - last_month_subs) / last_month_subs) * 100
            return growth_rate
        return 0.0
    
    async def _calculate_ltv(self, timestamp: datetime) -> float:
        """Calcule la Customer Lifetime Value"""
        arpu = await self._calculate_arpu(timestamp)
        churn_rate = await self._calculate_churn_rate(timestamp)
        
        if churn_rate > 0:
            avg_lifespan_months = 1 / (churn_rate / 100)  # Conversion en mois
            ltv = arpu * avg_lifespan_months
            return ltv
        return arpu * 12  # Fallback: 1 an
    
    async def _calculate_churn_rate(self, timestamp: datetime) -> float:
        """Calcule le taux de churn"""
        # Simulation réaliste
        base_churn = 3.0  # 3% de base
        seasonal_impact = 0.5 * np.sin(2 * np.pi * timestamp.month / 12)  # Saisonnalité
        trend_impact = -0.1 * (timestamp.month - 1)  # Amélioration dans le temps
        variance = np.random.normal(0, 0.3)
        
        churn = base_churn + seasonal_impact + trend_impact + variance
        return max(0.5, min(churn, 15.0))  # Entre 0.5% et 15%
    
    async def _calculate_retention_rate(self, timestamp: datetime) -> float:
        """Calcule le taux de rétention"""
        churn_rate = await self._calculate_churn_rate(timestamp)
        return 100 - churn_rate
    
    async def _count_active_creators(self, timestamp: datetime) -> float:
        """Compte les créateurs actifs"""
        active_users = await self._count_active_users(timestamp)
        # ~80% des utilisateurs sont des créateurs actifs
        creator_ratio = 0.8 + np.random.normal(0, 0.05)
        return active_users * creator_ratio
    
    async def _calculate_content_rate(self, timestamp: datetime) -> float:
        """Calcule le taux de création de contenu"""
        # Contenu par créateur par jour
        base_rate = 2.0
        weekend_factor = 0.7 if timestamp.weekday() >= 5 else 1.0
        seasonal = 1 + 0.1 * np.sin(2 * np.pi * timestamp.month / 12)
        variance = np.random.normal(0, 0.1)
        
        return max(0.5, base_rate * weekend_factor * seasonal * (1 + variance))
    
    async def _gather_metric_context(self, metric_def: MetricDefinition, timestamp: datetime) -> Dict[str, Any]:
        """Rassemble le contexte d'une métrique"""
        return {
            'collection_time': timestamp.isoformat(),
            'frequency': metric_def.frequency.value,
            'category': metric_def.category.value,
            'target_value': metric_def.target_value,
            'thresholds': {
                'warning': metric_def.warning_threshold,
                'critical': metric_def.critical_threshold
            }
        }
    
    async def _gather_metric_dimensions(self, metric_def: MetricDefinition, timestamp: datetime) -> Dict[str, Any]:
        """Rassemble les dimensions pour segmentation"""
        return {
            'date': timestamp.date().isoformat(),
            'hour': timestamp.hour,
            'day_of_week': timestamp.weekday(),
            'month': timestamp.month,
            'quarter': (timestamp.month - 1) // 3 + 1,
            'is_weekend': timestamp.weekday() >= 5,
            'season': self._get_season(timestamp.month)
        }
    
    def _get_season(self, month: int) -> str:
        """Détermine la saison"""
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'autumn'
    
    def _store_metric_value(self, metric_value: MetricValue):
        """Stocke une valeur de métrique pour aggregation"""
        metric_id = metric_value.metric_id
        
        if metric_id not in self.aggregated_metrics:
            self.aggregated_metrics[metric_id] = []
        
        self.aggregated_metrics[metric_id].append(metric_value)
        
        # Garde seulement les 1000 dernières valeurs
        if len(self.aggregated_metrics[metric_id]) > 1000:
            self.aggregated_metrics[metric_id] = self.aggregated_metrics[metric_id][-1000:]
    
    async def collect_all_metrics(self, timestamp: Optional[datetime] = None) -> Dict[str, MetricValue]:
        """Collecte toutes les métriques définies"""
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            results = {}
            
            # Collecte parallèle des métriques
            tasks = []
            for metric_id in self.metric_definitions.keys():
                task = self.collect_metric(metric_id, timestamp)
                tasks.append((metric_id, task))
            
            # Attente des résultats
            for metric_id, task in tasks:
                try:
                    result = await task
                    if result:
                        results[metric_id] = result
                except Exception as e:
                    logger.error(f"❌ Error collecting metric {metric_id}: {e}")
            
            logger.info(f"✅ Collected {len(results)} metrics at {timestamp}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error collecting all metrics: {e}")
            return {}
    
    async def generate_business_dashboard(
        self,
        dashboard_id: str = "main_dashboard",
        timeframe_hours: int = 24
    ) -> BusinessDashboard:
        """Génère un dashboard business complet"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=timeframe_hours)
            
            # Collecte des métriques récentes
            current_metrics = await self.collect_all_metrics(end_time)
            
            # Calcul des KPIs principaux
            kpis = {}
            if 'mrr' in current_metrics:
                kpis['MRR'] = current_metrics['mrr'].value
            if 'arpu' in current_metrics:
                kpis['ARPU'] = current_metrics['arpu'].value
            if 'churn_rate' in current_metrics:
                kpis['Churn Rate'] = current_metrics['churn_rate'].value
            if 'new_subscriptions' in current_metrics:
                kpis['New Subscriptions (24h)'] = current_metrics['new_subscriptions'].value
            
            # Calcul des tendances
            trends = await self._calculate_trends(timeframe_hours)
            
            # Génération des alertes
            alerts = await self._generate_metric_alerts(current_metrics)
            
            dashboard = BusinessDashboard(
                dashboard_id=dashboard_id,
                name="IA Chéries Subscription Metrics Dashboard",
                metrics=list(current_metrics.values()),
                kpis=kpis,
                trends=trends,
                alerts=alerts,
                last_update=end_time
            )
            
            logger.info(f"✅ Business dashboard generated: {len(current_metrics)} metrics, {len(alerts)} alerts")
            return dashboard
            
        except Exception as e:
            logger.error(f"❌ Error generating business dashboard: {e}")
            return None
    
    async def _calculate_trends(self, timeframe_hours: int) -> Dict[str, float]:
        """Calcule les tendances des métriques"""
        trends = {}
        
        try:
            # Calcul des tendances pour les métriques principales
            key_metrics = ['mrr', 'arpu', 'churn_rate', 'new_subscriptions']
            
            for metric_id in key_metrics:
                if metric_id in self.aggregated_metrics:
                    values = self.aggregated_metrics[metric_id]
                    if len(values) >= 2:
                        # Comparaison avec la période précédente
                        recent_values = [v.value for v in values[-timeframe_hours:]]
                        older_values = [v.value for v in values[-2*timeframe_hours:-timeframe_hours]]
                        
                        if recent_values and older_values:
                            recent_avg = np.mean(recent_values)
                            older_avg = np.mean(older_values)
                            
                            if older_avg > 0:
                                trend = ((recent_avg - older_avg) / older_avg) * 100
                                trends[metric_id] = trend
            
            return trends
            
        except Exception as e:
            logger.error(f"❌ Error calculating trends: {e}")
            return {}
    
    async def _generate_metric_alerts(self, current_metrics: Dict[str, MetricValue]) -> List[str]:
        """Génère des alertes basées sur les seuils"""
        alerts = []
        
        try:
            for metric_id, metric_value in current_metrics.items():
                metric_def = self.metric_definitions.get(metric_id)
                if not metric_def:
                    continue
                
                value = metric_value.value
                
                # Alertes critiques
                if metric_def.critical_threshold is not None:
                    if (metric_id == 'churn_rate' and value > metric_def.critical_threshold) or \
                       (metric_id != 'churn_rate' and value < metric_def.critical_threshold):
                        alerts.append(f"🚨 CRITIQUE: {metric_def.name} = {value:.1f} (seuil: {metric_def.critical_threshold})")
                
                # Alertes d'avertissement
                elif metric_def.warning_threshold is not None:
                    if (metric_id == 'churn_rate' and value > metric_def.warning_threshold) or \
                       (metric_id != 'churn_rate' and value < metric_def.warning_threshold):
                        alerts.append(f"⚠️ ATTENTION: {metric_def.name} = {value:.1f} (seuil: {metric_def.warning_threshold})")
            
            # Alertes sur les tendances
            trends = await self._calculate_trends(24)
            for metric_id, trend in trends.items():
                if abs(trend) > 20:  # Changement > 20%
                    direction = "hausse" if trend > 0 else "baisse"
                    alerts.append(f"📈 TENDANCE: {metric_id} en {direction} de {abs(trend):.1f}%")
            
            return alerts[:10]  # Maximum 10 alertes
            
        except Exception as e:
            logger.error(f"❌ Error generating alerts: {e}")
            return []
    
    async def export_metrics_report(
        self,
        start_date: datetime,
        end_date: datetime,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Exporte un rapport de métriques"""
        try:
            report = {
                'report_id': f"metrics_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}",
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'duration_days': (end_date - start_date).days
                },
                'metrics': {},
                'summary': {},
                'generated_at': datetime.now().isoformat()
            }
            
            # Collecte des métriques pour la période
            for metric_id in self.metric_definitions.keys():
                if metric_id in self.aggregated_metrics:
                    period_values = [
                        v for v in self.aggregated_metrics[metric_id]
                        if start_date <= v.timestamp <= end_date
                    ]
                    
                    if period_values:
                        values = [v.value for v in period_values]
                        report['metrics'][metric_id] = {
                            'count': len(values),
                            'min': min(values),
                            'max': max(values),
                            'avg': np.mean(values),
                            'std': np.std(values),
                            'trend': self._calculate_simple_trend(values)
                        }
            
            # Résumé exécutif
            if 'mrr' in report['metrics']:
                report['summary']['avg_mrr'] = report['metrics']['mrr']['avg']
            if 'churn_rate' in report['metrics']:
                report['summary']['avg_churn'] = report['metrics']['churn_rate']['avg']
            if 'new_subscriptions' in report['metrics']:
                report['summary']['total_new_subs'] = report['metrics']['new_subscriptions']['count']
            
            logger.info(f"✅ Metrics report exported for period {start_date} to {end_date}")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error exporting metrics report: {e}")
            return {}
    
    def _calculate_simple_trend(self, values: List[float]) -> str:
        """Calcule une tendance simple"""
        if len(values) < 2:
            return "stable"
        
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = np.mean(first_half)
        second_avg = np.mean(second_half)
        
        if second_avg > first_avg * 1.05:
            return "increasing"
        elif second_avg < first_avg * 0.95:
            return "decreasing"
        else:
            return "stable"
    
    async def get_metric_history(
        self,
        metric_id: str,
        hours: int = 24
    ) -> List[MetricValue]:
        """Récupère l'historique d'une métrique"""
        try:
            if metric_id not in self.aggregated_metrics:
                return []
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            history = [
                v for v in self.aggregated_metrics[metric_id]
                if v.timestamp >= cutoff_time
            ]
            
            return sorted(history, key=lambda x: x.timestamp)
            
        except Exception as e:
            logger.error(f"❌ Error getting metric history for {metric_id}: {e}")
            return []
    
    async def setup_real_time_monitoring(self, metric_ids: List[str], interval_seconds: int = 60):
        """Configure le monitoring en temps réel"""
        try:
            logger.info(f"🚀 Setting up real-time monitoring for {len(metric_ids)} metrics")
            
            while True:
                timestamp = datetime.now()
                
                for metric_id in metric_ids:
                    try:
                        metric_value = await self.collect_metric(metric_id, timestamp)
                        if metric_value:
                            self.real_time_metrics[metric_id] = metric_value
                    except Exception as e:
                        logger.error(f"❌ Error in real-time collection for {metric_id}: {e}")
                
                await asyncio.sleep(interval_seconds)
                
        except Exception as e:
            logger.error(f"❌ Error in real-time monitoring: {e}")


# Instance globale
subscription_metrics_collector = SubscriptionMetricsCollector()

# Export des classes principales
__all__ = [
    'SubscriptionMetricsCollector',
    'MetricDefinition',
    'MetricValue',
    'BusinessDashboard',
    'MetricCategory',
    'MetricFrequency',
    'subscription_metrics_collector'
]