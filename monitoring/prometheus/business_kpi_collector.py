"""
Business KPI Collector Module
Collecteur KPIs business temps réel - IA Chérie Platform

⚠️ CONFIDENTIEL - IA Chérie Creator Platform ⚠️
🔒 PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - Fahed Mlaiel (mlaiel@live.de)

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from decimal import Decimal
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram
import logging

logger = logging.getLogger(__name__)

@dataclass
class CreatorKPI:
    """KPI d'un créateur"""
    creator_id: str
    revenue_total: Decimal
    revenue_month: Decimal
    content_count: int
    engagement_rate: float
    collaboration_count: int
    follower_growth: float

@dataclass
class BusinessMetrics:
    """Métriques business globales"""
    total_revenue: Decimal
    active_creators: int
    total_collaborations: int
    platform_growth_rate: float
    churn_rate: float

class BusinessKPICollector:
    """
    Collecteur KPIs business temps réel
    
    Fonctionnalités:
    - Revenue per creator tracking
    - Collaboration success rates
    - Content monetization metrics
    - Creator engagement KPIs
    - Platform growth indicators
    """
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        self.registry = registry or CollectorRegistry()
        self.collection_active = False
        self.collection_interval = 60  # secondes
        self.kpi_cache = {}
        self._initialize_metrics()
        
    def _initialize_metrics(self):
        """Initialise les métriques Prometheus pour les KPIs business"""
        
        # Métriques de revenus
        self.revenue_per_creator = Gauge(
            'ainflue_business_revenue_per_creator_euros',
            'Revenue generated per creator in euros',
            labelnames=['creator_id', 'creator_tier', 'revenue_stream'],
            registry=self.registry
        )
        
        self.total_platform_revenue = Gauge(
            'ainflue_business_total_revenue_euros',
            'Total platform revenue in euros',
            labelnames=['time_period', 'revenue_type'],
            registry=self.registry
        )
        
        self.revenue_growth_rate = Gauge(
            'ainflue_business_revenue_growth_rate',
            'Revenue growth rate percentage',
            labelnames=['creator_tier', 'time_period'],
            registry=self.registry
        )
        
        # Métriques de collaboration
        self.collaboration_success_rate = Gauge(
            'ainflue_business_collaboration_success_rate',
            'Collaboration success rate percentage',
            labelnames=['creator_category', 'brand_category', 'collaboration_type'],
            registry=self.registry
        )
        
        self.collaboration_revenue = Gauge(
            'ainflue_business_collaboration_revenue_euros',
            'Revenue from collaborations in euros',
            labelnames=['creator_id', 'brand_id', 'collaboration_type'],
            registry=self.registry
        )
        
        self.collaboration_count = Counter(
            'ainflue_business_collaboration_total',
            'Total number of collaborations',
            labelnames=['creator_tier', 'brand_tier', 'status'],
            registry=self.registry
        )
        
        # Métriques de monétisation de contenu
        self.content_monetization_rate = Gauge(
            'ainflue_business_content_monetization_rate',
            'Content monetization success rate',
            labelnames=['content_type', 'monetization_method'],
            registry=self.registry
        )
        
        self.average_content_value = Gauge(
            'ainflue_business_average_content_value_euros',
            'Average monetary value per content piece',
            labelnames=['content_type', 'creator_tier'],
            registry=self.registry
        )
        
        self.content_roi = Gauge(
            'ainflue_business_content_roi_ratio',
            'Return on investment for content creation',
            labelnames=['creator_id', 'content_type'],
            registry=self.registry
        )
        
        # Métriques d'engagement créateur
        self.creator_engagement_score = Gauge(
            'ainflue_business_creator_engagement_score',
            'Creator engagement score (0-100)',
            labelnames=['creator_id', 'engagement_type'],
            registry=self.registry
        )
        
        self.creator_retention_rate = Gauge(
            'ainflue_business_creator_retention_rate',
            'Creator retention rate percentage',
            labelnames=['cohort_month', 'creator_tier'],
            registry=self.registry
        )
        
        self.creator_satisfaction_score = Gauge(
            'ainflue_business_creator_satisfaction_score',
            'Creator satisfaction score (1-10)',
            labelnames=['creator_id', 'survey_type'],
            registry=self.registry
        )
        
        # Métriques de croissance plateforme
        self.platform_growth_indicators = Gauge(
            'ainflue_business_platform_growth_rate',
            'Platform growth indicators',
            labelnames=['metric_type', 'time_period'],
            registry=self.registry
        )
        
        self.active_creators = Gauge(
            'ainflue_business_active_creators_count',
            'Number of active creators',
            labelnames=['activity_level', 'creator_tier'],
            registry=self.registry
        )
        
        self.new_creator_acquisition = Counter(
            'ainflue_business_new_creator_acquisitions_total',
            'Total new creator acquisitions',
            labelnames=['acquisition_channel', 'creator_tier'],
            registry=self.registry
        )
        
        # Métriques de performance business spécifiques
        self.ltv_per_creator = Gauge(
            'ainflue_business_ltv_per_creator_euros',
            'Lifetime value per creator in euros',
            labelnames=['creator_tier', 'cohort'],
            registry=self.registry
        )
        
        self.churn_rate = Gauge(
            'ainflue_business_churn_rate',
            'Creator churn rate percentage',
            labelnames=['creator_tier', 'churn_reason'],
            registry=self.registry
        )
        
        self.marketplace_transaction_volume = Gauge(
            'ainflue_business_marketplace_volume_euros',
            'Marketplace transaction volume in euros',
            labelnames=['transaction_type', 'creator_tier'],
            registry=self.registry
        )
        
        logger.info("Business KPI metrics initialized")
    
    async def start_collection(self, interval: int = 60):
        """Démarre la collecte automatique des KPIs"""
        if self.collection_active:
            logger.warning("KPI collection already active")
            return
            
        self.collection_active = True
        self.collection_interval = interval
        
        # Démarre la tâche de collecte
        asyncio.create_task(self._collection_loop())
        logger.info(f"Started business KPI collection with {interval}s interval")
    
    async def stop_collection(self):
        """Arrête la collecte automatique"""
        self.collection_active = False
        logger.info("Stopped business KPI collection")
    
    async def _collection_loop(self):
        """Boucle principale de collecte des KPIs"""
        while self.collection_active:
            try:
                await self._collect_all_kpis()
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                logger.error(f"Error in KPI collection loop: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _collect_all_kpis(self):
        """Collecte tous les KPIs business"""
        await asyncio.gather(
            self._collect_revenue_kpis(),
            self._collect_collaboration_kpis(),
            self._collect_content_kpis(),
            self._collect_engagement_kpis(),
            self._collect_growth_kpis(),
            return_exceptions=True
        )
    
    async def _collect_revenue_kpis(self):
        """Collecte les KPIs de revenus"""
        try:
            # Simulation de collecte de données depuis la DB
            # Dans un environnement réel, cela ferait des requêtes à la base de données
            
            # Revenue par créateur (simulation)
            creators_revenue = await self._fetch_creators_revenue()
            for creator_data in creators_revenue:
                self.revenue_per_creator.labels(
                    creator_id=creator_data['creator_id'],
                    creator_tier=creator_data['tier'],
                    revenue_stream=creator_data['stream']
                ).set(float(creator_data['revenue']))
            
            # Revenue total plateforme
            total_revenue = await self._calculate_total_revenue()
            self.total_platform_revenue.labels(
                time_period='monthly',
                revenue_type='gross'
            ).set(float(total_revenue))
            
            # Taux de croissance
            growth_rates = await self._calculate_revenue_growth()
            for tier, rate in growth_rates.items():
                self.revenue_growth_rate.labels(
                    creator_tier=tier,
                    time_period='monthly'
                ).set(rate)
                
            logger.debug("Revenue KPIs collected successfully")
            
        except Exception as e:
            logger.error(f"Error collecting revenue KPIs: {e}")
    
    async def _collect_collaboration_kpis(self):
        """Collecte les KPIs de collaboration"""
        try:
            # Taux de succès des collaborations
            success_rates = await self._calculate_collaboration_success_rates()
            for (creator_cat, brand_cat, collab_type), rate in success_rates.items():
                self.collaboration_success_rate.labels(
                    creator_category=creator_cat,
                    brand_category=brand_cat,
                    collaboration_type=collab_type
                ).set(rate)
            
            # Revenue des collaborations
            collaboration_revenues = await self._fetch_collaboration_revenues()
            for collab_data in collaboration_revenues:
                self.collaboration_revenue.labels(
                    creator_id=collab_data['creator_id'],
                    brand_id=collab_data['brand_id'],
                    collaboration_type=collab_data['type']
                ).set(float(collab_data['revenue']))
            
            logger.debug("Collaboration KPIs collected successfully")
            
        except Exception as e:
            logger.error(f"Error collecting collaboration KPIs: {e}")
    
    async def _collect_content_kpis(self):
        """Collecte les KPIs de contenu"""
        try:
            # Taux de monétisation de contenu
            monetization_rates = await self._calculate_content_monetization_rates()
            for (content_type, method), rate in monetization_rates.items():
                self.content_monetization_rate.labels(
                    content_type=content_type,
                    monetization_method=method
                ).set(rate)
            
            # Valeur moyenne du contenu
            content_values = await self._calculate_average_content_values()
            for (content_type, creator_tier), value in content_values.items():
                self.average_content_value.labels(
                    content_type=content_type,
                    creator_tier=creator_tier
                ).set(float(value))
            
            # ROI du contenu
            content_rois = await self._calculate_content_roi()
            for (creator_id, content_type), roi in content_rois.items():
                self.content_roi.labels(
                    creator_id=creator_id,
                    content_type=content_type
                ).set(roi)
                
            logger.debug("Content KPIs collected successfully")
            
        except Exception as e:
            logger.error(f"Error collecting content KPIs: {e}")
    
    async def _collect_engagement_kpis(self):
        """Collecte les KPIs d'engagement"""
        try:
            # Scores d'engagement créateur
            engagement_scores = await self._calculate_creator_engagement_scores()
            for (creator_id, engagement_type), score in engagement_scores.items():
                self.creator_engagement_score.labels(
                    creator_id=creator_id,
                    engagement_type=engagement_type
                ).set(score)
            
            # Taux de rétention
            retention_rates = await self._calculate_retention_rates()
            for (cohort, tier), rate in retention_rates.items():
                self.creator_retention_rate.labels(
                    cohort_month=cohort,
                    creator_tier=tier
                ).set(rate)
            
            # Scores de satisfaction
            satisfaction_scores = await self._fetch_satisfaction_scores()
            for (creator_id, survey_type), score in satisfaction_scores.items():
                self.creator_satisfaction_score.labels(
                    creator_id=creator_id,
                    survey_type=survey_type
                ).set(score)
                
            logger.debug("Engagement KPIs collected successfully")
            
        except Exception as e:
            logger.error(f"Error collecting engagement KPIs: {e}")
    
    async def _collect_growth_kpis(self):
        """Collecte les KPIs de croissance"""
        try:
            # Indicateurs de croissance plateforme
            growth_indicators = await self._calculate_platform_growth()
            for (metric_type, time_period), value in growth_indicators.items():
                self.platform_growth_indicators.labels(
                    metric_type=metric_type,
                    time_period=time_period
                ).set(value)
            
            # Créateurs actifs
            active_creator_counts = await self._count_active_creators()
            for (activity_level, tier), count in active_creator_counts.items():
                self.active_creators.labels(
                    activity_level=activity_level,
                    creator_tier=tier
                ).set(count)
            
            # LTV par créateur
            ltv_values = await self._calculate_creator_ltv()
            for (tier, cohort), ltv in ltv_values.items():
                self.ltv_per_creator.labels(
                    creator_tier=tier,
                    cohort=cohort
                ).set(float(ltv))
            
            # Taux de churn
            churn_rates = await self._calculate_churn_rates()
            for (tier, reason), rate in churn_rates.items():
                self.churn_rate.labels(
                    creator_tier=tier,
                    churn_reason=reason
                ).set(rate)
                
            logger.debug("Growth KPIs collected successfully")
            
        except Exception as e:
            logger.error(f"Error collecting growth KPIs: {e}")
    
    # Méthodes de simulation de données (à remplacer par de vraies requêtes DB)
    
    async def _fetch_creators_revenue(self) -> List[Dict[str, Any]]:
        """Simule la récupération des revenus créateurs"""
        # Simulation - remplacer par vraie requête DB
        import random
        creators = []
        for i in range(10):
            creators.append({
                'creator_id': f'creator_{i}',
                'tier': random.choice(['bronze', 'silver', 'gold', 'platinum']),
                'stream': random.choice(['sponsorship', 'subscription', 'merchandise', 'tips']),
                'revenue': Decimal(str(random.uniform(100, 10000)))
            })
        return creators
    
    async def _calculate_total_revenue(self) -> Decimal:
        """Calcule le revenue total"""
        # Simulation
        import random
        return Decimal(str(random.uniform(50000, 500000)))
    
    async def _calculate_revenue_growth(self) -> Dict[str, float]:
        """Calcule les taux de croissance des revenus"""
        import random
        return {
            'bronze': random.uniform(0.05, 0.15),
            'silver': random.uniform(0.10, 0.25),
            'gold': random.uniform(0.15, 0.35),
            'platinum': random.uniform(0.20, 0.50)
        }
    
    async def _calculate_collaboration_success_rates(self) -> Dict[Tuple[str, str, str], float]:
        """Calcule les taux de succès des collaborations"""
        import random
        rates = {}
        categories = ['tech', 'fashion', 'gaming', 'lifestyle']
        collab_types = ['sponsored_post', 'product_review', 'brand_partnership']
        
        for creator_cat in categories:
            for brand_cat in categories:
                for collab_type in collab_types:
                    rates[(creator_cat, brand_cat, collab_type)] = random.uniform(0.3, 0.8)
        
        return rates
    
    async def _fetch_collaboration_revenues(self) -> List[Dict[str, Any]]:
        """Récupère les revenus des collaborations"""
        import random
        collaborations = []
        for i in range(20):
            collaborations.append({
                'creator_id': f'creator_{i % 10}',
                'brand_id': f'brand_{i % 5}',
                'type': random.choice(['sponsored_post', 'product_review', 'brand_partnership']),
                'revenue': Decimal(str(random.uniform(500, 5000)))
            })
        return collaborations
    
    async def _calculate_content_monetization_rates(self) -> Dict[Tuple[str, str], float]:
        """Calcule les taux de monétisation de contenu"""
        import random
        rates = {}
        content_types = ['video', 'image', 'audio', 'text']
        methods = ['subscription', 'pay_per_view', 'merchandise', 'tips']
        
        for content_type in content_types:
            for method in methods:
                rates[(content_type, method)] = random.uniform(0.1, 0.6)
        
        return rates
    
    async def _calculate_average_content_values(self) -> Dict[Tuple[str, str], Decimal]:
        """Calcule les valeurs moyennes du contenu"""
        import random
        values = {}
        content_types = ['video', 'image', 'audio', 'text']
        tiers = ['bronze', 'silver', 'gold', 'platinum']
        
        for content_type in content_types:
            for tier in tiers:
                base_value = {'bronze': 10, 'silver': 25, 'gold': 50, 'platinum': 100}[tier]
                values[(content_type, tier)] = Decimal(str(random.uniform(base_value, base_value * 3)))
        
        return values
    
    async def _calculate_content_roi(self) -> Dict[Tuple[str, str], float]:
        """Calcule le ROI du contenu"""
        import random
        rois = {}
        for i in range(10):
            for content_type in ['video', 'image', 'audio']:
                rois[(f'creator_{i}', content_type)] = random.uniform(1.2, 5.0)
        return rois
    
    async def _calculate_creator_engagement_scores(self) -> Dict[Tuple[str, str], float]:
        """Calcule les scores d'engagement créateur"""
        import random
        scores = {}
        engagement_types = ['platform_activity', 'community_interaction', 'content_quality']
        
        for i in range(10):
            for engagement_type in engagement_types:
                scores[(f'creator_{i}', engagement_type)] = random.uniform(60, 100)
        
        return scores
    
    async def _calculate_retention_rates(self) -> Dict[Tuple[str, str], float]:
        """Calcule les taux de rétention"""
        import random
        rates = {}
        cohorts = ['2024-01', '2024-02', '2024-03', '2024-04']
        tiers = ['bronze', 'silver', 'gold', 'platinum']
        
        for cohort in cohorts:
            for tier in tiers:
                base_rate = {'bronze': 0.7, 'silver': 0.8, 'gold': 0.9, 'platinum': 0.95}[tier]
                rates[(cohort, tier)] = random.uniform(base_rate - 0.1, base_rate + 0.05)
        
        return rates
    
    async def _fetch_satisfaction_scores(self) -> Dict[Tuple[str, str], float]:
        """Récupère les scores de satisfaction"""
        import random
        scores = {}
        survey_types = ['platform_usability', 'support_quality', 'monetization_satisfaction']
        
        for i in range(10):
            for survey_type in survey_types:
                scores[(f'creator_{i}', survey_type)] = random.uniform(6, 10)
        
        return scores
    
    async def _calculate_platform_growth(self) -> Dict[Tuple[str, str], float]:
        """Calcule la croissance de la plateforme"""
        import random
        growth = {}
        metrics = ['user_acquisition', 'revenue_growth', 'engagement_growth']
        periods = ['monthly', 'quarterly', 'yearly']
        
        for metric in metrics:
            for period in periods:
                multiplier = {'monthly': 0.1, 'quarterly': 0.3, 'yearly': 1.0}[period]
                growth[(metric, period)] = random.uniform(0.05, 0.4) * multiplier
        
        return growth
    
    async def _count_active_creators(self) -> Dict[Tuple[str, str], int]:
        """Compte les créateurs actifs"""
        import random
        counts = {}
        activity_levels = ['daily', 'weekly', 'monthly']
        tiers = ['bronze', 'silver', 'gold', 'platinum']
        
        for activity in activity_levels:
            for tier in tiers:
                base_count = {'bronze': 1000, 'silver': 500, 'gold': 200, 'platinum': 50}[tier]
                multiplier = {'daily': 0.3, 'weekly': 0.6, 'monthly': 1.0}[activity]
                counts[(activity, tier)] = int(base_count * multiplier * random.uniform(0.8, 1.2))
        
        return counts
    
    async def _calculate_creator_ltv(self) -> Dict[Tuple[str, str], Decimal]:
        """Calcule la LTV des créateurs"""
        import random
        ltv_values = {}
        tiers = ['bronze', 'silver', 'gold', 'platinum']
        cohorts = ['Q1_2023', 'Q2_2023', 'Q3_2023', 'Q4_2023']
        
        for tier in tiers:
            for cohort in cohorts:
                base_ltv = {'bronze': 500, 'silver': 2000, 'gold': 8000, 'platinum': 25000}[tier]
                ltv_values[(tier, cohort)] = Decimal(str(base_ltv * random.uniform(0.8, 1.5)))
        
        return ltv_values
    
    async def _calculate_churn_rates(self) -> Dict[Tuple[str, str], float]:
        """Calcule les taux de churn"""
        import random
        churn_rates = {}
        tiers = ['bronze', 'silver', 'gold', 'platinum']
        reasons = ['low_earnings', 'platform_issues', 'competition', 'other']
        
        for tier in tiers:
            for reason in reasons:
                base_churn = {'bronze': 0.15, 'silver': 0.10, 'gold': 0.05, 'platinum': 0.02}[tier]
                churn_rates[(tier, reason)] = base_churn * random.uniform(0.2, 0.4)
        
        return churn_rates
    
    def get_current_kpis(self) -> Dict[str, Any]:
        """Récupère les KPIs actuels depuis le cache"""
        return self.kpi_cache.copy()
    
    def export_registry(self) -> CollectorRegistry:
        """Exporte le registry Prometheus"""
        return self.registry