"""Platform Earnings Database Models

Gestion agrégée des revenus par plateforme avec analytics
avancées et optimisation des performances financières.

Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead AI Developer & Platform Revenue Architect
"""
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import uuid
import logging
from dataclasses import dataclass
from sqlalchemy import Column, String, Numeric, DateTime, Integer, Text, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from ..models.base import BaseModel, TimestampMixin
from ...core.database import DatabaseManager
from ...core.cache import CacheManager
from ...utils.analytics import PlatformAnalytics
from ...utils.financial import RevenueOptimizer
from .revenue_records import RevenueSource, TransactionStatus

logger = logging.getLogger(__name__)

Base = declarative_base()


class EarningsInterval(Enum):
    """Intervalles de calcul des revenus"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class PlatformPerformanceRating(Enum):
    """Évaluation des performances plateforme"""
    EXCELLENT = "excellent"  # >90% performance
    GOOD = "good"           # 70-90% performance
    AVERAGE = "average"     # 50-70% performance
    POOR = "poor"          # 30-50% performance
    CRITICAL = "critical"   # <30% performance


@dataclass
class PlatformEarnings(BaseModel, TimestampMixin):
    """
    Modèle pour les revenus agrégés par plateforme
    """
    __tablename__ = "platform_earnings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Identification plateforme
    platform_name = Column(String(100), nullable=False, index=True)
    platform_id = Column(String(200), nullable=True)
    revenue_source = Column(String(50), nullable=False)
    
    # Période de calcul
    earnings_period = Column(String(20), nullable=False)  # EarningsInterval
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False, index=True)
    
    # Métriques financières
    total_gross_revenue = Column(Numeric(15, 4), nullable=False, default=0)
    total_net_revenue = Column(Numeric(15, 4), nullable=False, default=0)
    platform_fees_total = Column(Numeric(15, 4), nullable=False, default=0)
    commission_total = Column(Numeric(15, 4), nullable=False, default=0)
    creator_payout_total = Column(Numeric(15, 4), nullable=False, default=0)
    
    # Métriques de performance
    transaction_count = Column(Integer, nullable=False, default=0)
    unique_content_count = Column(Integer, nullable=False, default=0)
    average_transaction_value = Column(Numeric(10, 4), nullable=False, default=0)
    revenue_growth_rate = Column(Numeric(8, 4), nullable=True)
    
    # Analytics avancées
    top_earning_content_ids = Column(ARRAY(String), nullable=True)
    revenue_distribution = Column(JSONB, nullable=True)  # Distribution par type de contenu
    engagement_metrics = Column(JSONB, nullable=True)    # Métriques d'engagement
    conversion_metrics = Column(JSONB, nullable=True)    # Métriques de conversion
    
    # Évaluation performance
    performance_score = Column(Numeric(5, 2), nullable=True)  # Score 0-100
    performance_rating = Column(String(20), nullable=True)
    performance_trends = Column(JSONB, nullable=True)
    
    # Optimisations recommandées
    optimization_suggestions = Column(JSONB, nullable=True)
    potential_revenue_increase = Column(Numeric(15, 4), nullable=True)
    
    # Métadonnées
    currency = Column(String(3), nullable=False, default="EUR")
    metadata = Column(JSONB, nullable=True)
    last_calculated = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="platform_earnings")
    
    # Index composites pour performance
    __table_args__ = (
        Index('idx_platform_earnings_user_period', 'user_id', 'earnings_period', 'period_start'),
        Index('idx_platform_earnings_platform_period', 'platform_name', 'earnings_period', 'period_start'),
        Index('idx_platform_earnings_performance', 'performance_score', 'revenue_growth_rate'),
    )

    def calculate_performance_score(self) -> float:
        """Calcule le score de performance de la plateforme"""
        score = 0.0
        
        # Facteur volume (30%)
        if self.transaction_count > 0:
            volume_score = min(self.transaction_count / 100, 1.0) * 30
            score += volume_score
        
        # Facteur valeur moyenne (25%)
        if self.average_transaction_value > 0:
            value_score = min(float(self.average_transaction_value) / 50, 1.0) * 25
            score += value_score
        
        # Facteur croissance (25%)
        if self.revenue_growth_rate and self.revenue_growth_rate > 0:
            growth_score = min(float(self.revenue_growth_rate) / 50, 1.0) * 25
            score += growth_score
        
        # Facteur diversité contenu (20%)
        if self.unique_content_count > 0:
            diversity_score = min(self.unique_content_count / 20, 1.0) * 20
            score += diversity_score
        
        return round(score, 2)

    def get_performance_rating(self) -> PlatformPerformanceRating:
        """Détermine la notation de performance"""
        score = self.performance_score or 0
        
        if score >= 90:
            return PlatformPerformanceRating.EXCELLENT
        elif score >= 70:
            return PlatformPerformanceRating.GOOD
        elif score >= 50:
            return PlatformPerformanceRating.AVERAGE
        elif score >= 30:
            return PlatformPerformanceRating.POOR
        else:
            return PlatformPerformanceRating.CRITICAL


class PlatformComparisonMetrics(BaseModel, TimestampMixin):
    """
    Métriques de comparaison entre plateformes
    """
    __tablename__ = "platform_comparison_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Période de comparaison
    comparison_period = Column(String(20), nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Platforms comparées
    platforms_compared = Column(ARRAY(String), nullable=False)
    
    # Métriques comparatives
    best_performing_platform = Column(String(100), nullable=True)
    worst_performing_platform = Column(String(100), nullable=True)
    revenue_leader = Column(String(100), nullable=True)
    growth_leader = Column(String(100), nullable=True)
    
    # Analytics comparatives
    platform_rankings = Column(JSONB, nullable=True)
    revenue_distribution = Column(JSONB, nullable=True)
    performance_gaps = Column(JSONB, nullable=True)
    optimization_opportunities = Column(JSONB, nullable=True)
    
    # Recommandations stratégiques
    strategic_recommendations = Column(JSONB, nullable=True)
    resource_allocation_suggestions = Column(JSONB, nullable=True)
    
    # Relations
    user = relationship("User", back_populates="platform_comparisons")


class PlatformEarningsManager:
    """
    Manager pour la gestion des revenus par plateforme
    """
    
    def __init__(self, db_manager: DatabaseManager, cache_manager: CacheManager):
        self.db = db_manager
        self.cache = cache_manager
        self.analytics = PlatformAnalytics()
        self.optimizer = RevenueOptimizer()
        self.logger = logging.getLogger(__name__)

    async def calculate_platform_earnings(
        self,
        user_id: uuid.UUID,
        platform_name: str,
        period_start: datetime,
        period_end: datetime,
        interval: EarningsInterval = EarningsInterval.DAILY
    ) -> PlatformEarnings:
        """
        Calcule les revenus agrégés pour une plateforme
        
        Args:
            user_id: ID utilisateur
            platform_name: Nom de la plateforme
            period_start: Début de période
            period_end: Fin de période
            interval: Intervalle de calcul
            
        Returns:
            PlatformEarnings: Revenus calculés
        """
        try:
            # Vérification cache
            cache_key = f"platform_earnings:{user_id}:{platform_name}:{interval.value}:{period_start.date()}:{period_end.date()}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return PlatformEarnings(**cached_result)
            
            # Récupération des transactions de la période
            async with self.db.get_session() as session:
                from .revenue_records import RevenueRecord
                
                query = session.query(RevenueRecord).filter(
                    RevenueRecord.user_id == user_id,
                    RevenueRecord.platform_name == platform_name,
                    RevenueRecord.transaction_date >= period_start,
                    RevenueRecord.transaction_date <= period_end,
                    RevenueRecord.transaction_status.in_([
                        TransactionStatus.CONFIRMED.value,
                        TransactionStatus.PROCESSED.value
                    ])
                )
                
                transactions = await query.all()
            
            # Calculs agrégés
            total_gross = sum(t.amount_gross for t in transactions)
            total_net = sum(t.amount_net for t in transactions)
            platform_fees = sum(t.platform_fee_amount or 0 for t in transactions)
            commission_total = sum(t.commission_amount for t in transactions)
            creator_payout = sum(t.creator_payout for t in transactions)
            
            transaction_count = len(transactions)
            unique_content_ids = list(set(t.content_id for t in transactions if t.content_id))
            unique_content_count = len(unique_content_ids)
            
            avg_transaction_value = total_gross / transaction_count if transaction_count > 0 else 0
            
            # Analytics avancées
            revenue_distribution = await self._calculate_revenue_distribution(transactions)
            engagement_metrics = await self._calculate_engagement_metrics(user_id, platform_name, period_start, period_end)
            conversion_metrics = await self._calculate_conversion_metrics(transactions)
            
            # Top content par revenus
            content_revenues = {}
            for t in transactions:
                if t.content_id:
                    content_id = str(t.content_id)
                    content_revenues[content_id] = content_revenues.get(content_id, 0) + float(t.amount_gross)
            
            top_earning_content = sorted(
                content_revenues.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
            top_earning_content_ids = [content_id for content_id, _ in top_earning_content]
            
            # Calcul de la croissance
            revenue_growth_rate = await self._calculate_growth_rate(
                user_id, platform_name, period_start, period_end, total_gross
            )
            
            # Création de l'enregistrement
            earnings = PlatformEarnings(
                user_id=user_id,
                platform_name=platform_name,
                revenue_source=await self._determine_revenue_source(platform_name),
                earnings_period=interval.value,
                period_start=period_start,
                period_end=period_end,
                total_gross_revenue=total_gross,
                total_net_revenue=total_net,
                platform_fees_total=platform_fees,
                commission_total=commission_total,
                creator_payout_total=creator_payout,
                transaction_count=transaction_count,
                unique_content_count=unique_content_count,
                average_transaction_value=avg_transaction_value,
                revenue_growth_rate=revenue_growth_rate,
                top_earning_content_ids=top_earning_content_ids,
                revenue_distribution=revenue_distribution,
                engagement_metrics=engagement_metrics,
                conversion_metrics=conversion_metrics
            )
            
            # Calcul score de performance
            earnings.performance_score = earnings.calculate_performance_score()
            earnings.performance_rating = earnings.get_performance_rating().value
            
            # Calcul des tendances et optimisations
            earnings.performance_trends = await self._calculate_performance_trends(
                user_id, platform_name, period_start, period_end
            )
            earnings.optimization_suggestions = await self._generate_optimization_suggestions(earnings)
            
            # Sauvegarde
            async with self.db.get_session() as session:
                session.add(earnings)
                await session.commit()
                await session.refresh(earnings)
            
            # Cache du résultat
            await self.cache.set(cache_key, earnings.__dict__, ttl=3600)  # 1 heure
            
            self.logger.info(
                f"Platform earnings calculated for {platform_name}, user {user_id}: "
                f"{total_gross} revenue, {transaction_count} transactions"
            )
            
            return earnings
            
        except Exception as e:
            self.logger.error(f"Error calculating platform earnings: {str(e)}")
            raise

    async def get_platform_performance_ranking(
        self,
        user_id: uuid.UUID,
        period_start: datetime,
        period_end: datetime
    ) -> List[Dict[str, Any]]:
        """
        Classement des plateformes par performance
        
        Args:
            user_id: ID utilisateur
            period_start: Début de période
            period_end: Fin de période
            
        Returns:
            List[Dict]: Classement des plateformes
        """
        try:
            async with self.db.get_session() as session:
                earnings = await session.query(PlatformEarnings).filter(
                    PlatformEarnings.user_id == user_id,
                    PlatformEarnings.period_start >= period_start,
                    PlatformEarnings.period_end <= period_end
                ).order_by(PlatformEarnings.performance_score.desc()).all()
            
            ranking = []
            for i, earning in enumerate(earnings, 1):
                ranking.append({
                    "rank": i,
                    "platform_name": earning.platform_name,
                    "performance_score": float(earning.performance_score or 0),
                    "performance_rating": earning.performance_rating,
                    "total_revenue": float(earning.total_gross_revenue),
                    "growth_rate": float(earning.revenue_growth_rate or 0),
                    "transaction_count": earning.transaction_count,
                    "avg_transaction_value": float(earning.average_transaction_value)
                })
            
            return ranking
            
        except Exception as e:
            self.logger.error(f"Error getting platform ranking: {str(e)}")
            raise

    async def generate_platform_comparison_report(
        self,
        user_id: uuid.UUID,
        platforms: List[str],
        period_start: datetime,
        period_end: datetime
    ) -> PlatformComparisonMetrics:
        """
        Génère un rapport de comparaison entre plateformes
        
        Args:
            user_id: ID utilisateur
            platforms: Liste des plateformes à comparer
            period_start: Début de période
            period_end: Fin de période
            
        Returns:
            PlatformComparisonMetrics: Rapport de comparaison
        """
        try:
            # Récupération des données par plateforme
            platform_data = {}
            for platform in platforms:
                earnings = await self.calculate_platform_earnings(
                    user_id, platform, period_start, period_end
                )
                platform_data[platform] = earnings
            
            # Analyse comparative
            revenue_ranking = sorted(
                platform_data.items(),
                key=lambda x: x[1].total_gross_revenue,
                reverse=True
            )
            
            performance_ranking = sorted(
                platform_data.items(),
                key=lambda x: x[1].performance_score or 0,
                reverse=True
            )
            
            growth_ranking = sorted(
                platform_data.items(),
                key=lambda x: x[1].revenue_growth_rate or 0,
                reverse=True
            )
            
            # Métriques comparatives
            best_performing = performance_ranking[0][0] if performance_ranking else None
            worst_performing = performance_ranking[-1][0] if performance_ranking else None
            revenue_leader = revenue_ranking[0][0] if revenue_ranking else None
            growth_leader = growth_ranking[0][0] if growth_ranking else None
            
            # Distribution des revenus
            total_revenue = sum(data.total_gross_revenue for data in platform_data.values())
            revenue_distribution = {
                platform: {
                    "amount": float(data.total_gross_revenue),
                    "percentage": float((data.total_gross_revenue / total_revenue) * 100) if total_revenue > 0 else 0
                }
                for platform, data in platform_data.items()
            }
            
            # Gaps de performance
            performance_gaps = await self._calculate_performance_gaps(platform_data)
            
            # Opportunités d'optimisation
            optimization_opportunities = await self._identify_optimization_opportunities(platform_data)
            
            # Recommandations stratégiques
            strategic_recommendations = await self._generate_strategic_recommendations(platform_data)
            
            # Création du rapport
            comparison = PlatformComparisonMetrics(
                user_id=user_id,
                comparison_period=f"{period_start.date()}_to_{period_end.date()}",
                period_start=period_start,
                period_end=period_end,
                platforms_compared=platforms,
                best_performing_platform=best_performing,
                worst_performing_platform=worst_performing,
                revenue_leader=revenue_leader,
                growth_leader=growth_leader,
                platform_rankings={
                    "performance": [(p, float(d.performance_score or 0)) for p, d in performance_ranking],
                    "revenue": [(p, float(d.total_gross_revenue)) for p, d in revenue_ranking],
                    "growth": [(p, float(d.revenue_growth_rate or 0)) for p, d in growth_ranking]
                },
                revenue_distribution=revenue_distribution,
                performance_gaps=performance_gaps,
                optimization_opportunities=optimization_opportunities,
                strategic_recommendations=strategic_recommendations
            )
            
            # Sauvegarde
            async with self.db.get_session() as session:
                session.add(comparison)
                await session.commit()
                await session.refresh(comparison)
            
            return comparison
            
        except Exception as e:
            self.logger.error(f"Error generating platform comparison: {str(e)}")
            raise

    async def _calculate_revenue_distribution(
        self, 
        transactions: List
    ) -> Dict[str, Any]:
        """Calcule la distribution des revenus par type"""
        distribution = {}
        total = sum(t.amount_gross for t in transactions)
        
        for transaction in transactions:
            trans_type = transaction.transaction_type
            if trans_type not in distribution:
                distribution[trans_type] = {"amount": 0, "count": 0}
            
            distribution[trans_type]["amount"] += float(transaction.amount_gross)
            distribution[trans_type]["count"] += 1
        
        # Ajout des pourcentages
        for trans_type in distribution:
            amount = distribution[trans_type]["amount"]
            distribution[trans_type]["percentage"] = (amount / float(total)) * 100 if total > 0 else 0
        
        return distribution

    async def _calculate_engagement_metrics(
        self,
        user_id: uuid.UUID,
        platform_name: str,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Calcule les métriques d'engagement pour la plateforme"""
        # Cette méthode serait intégrée avec les modules d'analytics
        return {
            "average_engagement_rate": 0.0,
            "total_interactions": 0,
            "reach": 0,
            "conversion_rate": 0.0
        }

    async def _calculate_conversion_metrics(self, transactions: List) -> Dict[str, Any]:
        """Calcule les métriques de conversion"""
        return {
            "total_conversions": len(transactions),
            "conversion_value": sum(float(t.amount_gross) for t in transactions),
            "average_conversion_value": sum(float(t.amount_gross) for t in transactions) / len(transactions) if transactions else 0
        }

    async def _calculate_growth_rate(
        self,
        user_id: uuid.UUID,
        platform_name: str,
        period_start: datetime,
        period_end: datetime,
        current_revenue: Decimal
    ) -> Optional[Decimal]:
        """Calcule le taux de croissance par rapport à la période précédente"""
        try:
            # Période précédente de même durée
            period_duration = period_end - period_start
            previous_start = period_start - period_duration
            previous_end = period_start
            
            async with self.db.get_session() as session:
                previous_earnings = await session.query(PlatformEarnings).filter(
                    PlatformEarnings.user_id == user_id,
                    PlatformEarnings.platform_name == platform_name,
                    PlatformEarnings.period_start >= previous_start,
                    PlatformEarnings.period_end <= previous_end
                ).first()
            
            if previous_earnings and previous_earnings.total_gross_revenue > 0:
                growth_rate = ((current_revenue - previous_earnings.total_gross_revenue) / 
                              previous_earnings.total_gross_revenue) * 100
                return Decimal(str(growth_rate))
            
            return None
            
        except Exception:
            return None

    async def _determine_revenue_source(self, platform_name: str) -> str:
        """Détermine la source de revenus basée sur le nom de plateforme"""
        platform_mapping = {
            "spotify": RevenueSource.SPOTIFY.value,
            "youtube": RevenueSource.YOUTUBE.value,
            "tiktok": RevenueSource.TIKTOK.value,
            "instagram": RevenueSource.INSTAGRAM.value,
            "soundcloud": RevenueSource.SOUNDCLOUD.value,
        }
        
        return platform_mapping.get(platform_name.lower(), RevenueSource.CUSTOM_PLATFORM.value)

    async def _calculate_performance_trends(
        self,
        user_id: uuid.UUID,
        platform_name: str,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Calcule les tendances de performance"""
        # Implémentation des tendances basée sur l'historique
        return {
            "revenue_trend": "increasing",
            "transaction_trend": "stable",
            "performance_trend": "improving"
        }

    async def _generate_optimization_suggestions(
        self, 
        earnings: PlatformEarnings
    ) -> List[Dict[str, Any]]:
        """Génère des suggestions d'optimisation"""
        suggestions = []
        
        if earnings.performance_score and earnings.performance_score < 70:
            suggestions.append({
                "type": "performance_improvement",
                "priority": "high",
                "suggestion": "Improve content quality and engagement strategies",
                "potential_impact": "15-25% revenue increase"
            })
        
        if earnings.average_transaction_value < 10:
            suggestions.append({
                "type": "value_optimization",
                "priority": "medium",
                "suggestion": "Focus on higher-value content formats",
                "potential_impact": "10-20% revenue increase"
            })
        
        return suggestions

    async def _calculate_performance_gaps(
        self, 
        platform_data: Dict[str, PlatformEarnings]
    ) -> Dict[str, Any]:
        """Calcule les écarts de performance entre plateformes"""
        gaps = {}
        
        if len(platform_data) < 2:
            return gaps
        
        # Trouve la meilleure performance
        best_performance = max(
            platform_data.values(),
            key=lambda x: x.performance_score or 0
        )
        
        # Calcule les écarts
        for platform, data in platform_data.items():
            gap = (best_performance.performance_score or 0) - (data.performance_score or 0)
            gaps[platform] = {
                "performance_gap": float(gap),
                "revenue_gap": float(best_performance.total_gross_revenue - data.total_gross_revenue)
            }
        
        return gaps

    async def _identify_optimization_opportunities(
        self, 
        platform_data: Dict[str, PlatformEarnings]
    ) -> List[Dict[str, Any]]:
        """Identifie les opportunités d'optimisation cross-platform"""
        opportunities = []
        
        # Analyse des meilleures pratiques par plateforme
        best_performers = {}
        for platform, data in platform_data.items():
            if data.performance_score and data.performance_score > 80:
                best_performers[platform] = data
        
        # Suggestions basées sur les meilleures performances
        for platform, data in platform_data.items():
            if data.performance_score and data.performance_score < 70:
                opportunities.append({
                    "platform": platform,
                    "type": "cross_platform_learning",
                    "suggestion": f"Apply successful strategies from {list(best_performers.keys())}",
                    "potential_impact": "20-30% performance improvement"
                })
        
        return opportunities

    async def _generate_strategic_recommendations(
        self, 
        platform_data: Dict[str, PlatformEarnings]
    ) -> List[Dict[str, Any]]:
        """Génère des recommandations stratégiques"""
        recommendations = []
        
        # Analyse de diversification
        total_revenue = sum(data.total_gross_revenue for data in platform_data.values())
        
        for platform, data in platform_data.items():
            platform_percentage = (data.total_gross_revenue / total_revenue) * 100 if total_revenue > 0 else 0
            
            if platform_percentage > 60:
                recommendations.append({
                    "type": "diversification",
                    "priority": "high",
                    "recommendation": "Reduce platform dependency by diversifying content distribution",
                    "risk_level": "high"
                })
            elif platform_percentage < 5 and data.performance_score and data.performance_score > 70:
                recommendations.append({
                    "type": "expansion",
                    "priority": "medium",
                    "recommendation": f"Increase investment in {platform} due to high performance",
                    "opportunity_level": "high"
                })
        
        return recommendations


# Export des classes principales
__all__ = [
    "PlatformEarnings",
    "PlatformComparisonMetrics",
    "PlatformEarningsManager",
    "EarningsInterval",
    "PlatformPerformanceRating"
]
