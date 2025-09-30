"""🚀 Platform Core Subscription - Usage Analytics System
=========================================================
Module: backend/platform_core/subscription/usage_analytics.py
Author: Fahed Mlaiel (mlaiel@live.de)
=========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME D'ANALYTICS D'USAGE
Analytics avancées et prédictives pour optimiser les abonnements
- Analyse des patterns d'usage
- Prédictions de consommation
- Insights business intelligence
- Recommandations automatiques
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
import logging
from decimal import Decimal
import statistics

# Configure logging
logger = logging.getLogger(__name__)


class AnalyticsTimeframe(Enum):
    """Périodes d'analyse"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class TrendDirection(Enum):
    """Directions de tendance"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


class UsagePattern(Enum):
    """Patterns d'usage"""
    CONSISTENT = "consistent"
    SEASONAL = "seasonal"
    BURST = "burst"
    DECLINING = "declining"
    GROWING = "growing"


@dataclass
class UsageReport:
    """Rapport d'usage"""
    id: str
    customer_id: str
    timeframe: AnalyticsTimeframe
    start_date: datetime
    end_date: datetime
    total_usage: int
    average_daily_usage: float
    peak_usage: int
    trend_direction: TrendDirection
    usage_pattern: UsagePattern
    efficiency_score: float  # 0.0 to 1.0
    recommendations: List[str]
    generated_at: datetime
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le rapport en dictionnaire"""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "timeframe": self.timeframe.value,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "total_usage": self.total_usage,
            "average_daily_usage": self.average_daily_usage,
            "peak_usage": self.peak_usage,
            "trend_direction": self.trend_direction.value,
            "usage_pattern": self.usage_pattern.value,
            "efficiency_score": self.efficiency_score,
            "recommendations": self.recommendations,
            "generated_at": self.generated_at.isoformat(),
            "metadata": self.metadata or {}
        }


@dataclass
class PredictiveAnalytics:
    """Analytics prédictives"""
    customer_id: str
    predicted_usage: int
    confidence_level: float  # 0.0 to 1.0
    prediction_timeframe: AnalyticsTimeframe
    factors_analyzed: List[str]
    risk_factors: List[str]
    opportunities: List[str]
    recommended_actions: List[str]
    generated_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convertit les analytics en dictionnaire"""
        return {
            "customer_id": self.customer_id,
            "predicted_usage": self.predicted_usage,
            "confidence_level": self.confidence_level,
            "prediction_timeframe": self.prediction_timeframe.value,
            "factors_analyzed": self.factors_analyzed,
            "risk_factors": self.risk_factors,
            "opportunities": self.opportunities,
            "recommended_actions": self.recommended_actions,
            "generated_at": self.generated_at.isoformat()
        }


class UsageAnalytics:
    """Gestionnaire principal des analytics d'usage"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialise le gestionnaire d'analytics
        
        Args:
            config: Configuration du gestionnaire
        """
        self.config = config or {}
        self.usage_data: List[Dict[str, Any]] = []
        self.reports: Dict[str, UsageReport] = {}
        self.predictions: Dict[str, PredictiveAnalytics] = {}
        self.benchmark_data: Dict[str, Any] = {}
        
        logger.info("UsageAnalytics initialized")

    async def record_usage(
        self,
        customer_id: str,
        resource_type: str,
        amount: int,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Enregistre un événement d'usage
        
        Args:
            customer_id: ID du client
            resource_type: Type de ressource
            amount: Quantité utilisée
            timestamp: Timestamp de l'usage
            metadata: Métadonnées additionnelles
            
        Returns:
            bool: True si enregistré avec succès
        """
        try:
            usage_event = {
                "customer_id": customer_id,
                "resource_type": resource_type,
                "amount": amount,
                "timestamp": timestamp or datetime.now(),
                "metadata": metadata or {}
            }
            
            self.usage_data.append(usage_event)
            
            # Maintenance automatique des données anciennes
            await self._cleanup_old_data()
            
            logger.debug(f"Usage recorded: {customer_id} - {resource_type} - {amount}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording usage: {e}")
            return False

    async def generate_usage_report(
        self,
        customer_id: str,
        timeframe: AnalyticsTimeframe,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Optional[UsageReport]:
        """Génère un rapport d'usage pour un client
        
        Args:
            customer_id: ID du client
            timeframe: Période d'analyse
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Optional[UsageReport]: Le rapport généré
        """
        try:
            # Définition des dates si non fournies
            if not end_date:
                end_date = datetime.now()
            
            if not start_date:
                start_date = self._calculate_start_date(end_date, timeframe)
            
            # Filtrage des données d'usage
            filtered_data = self._filter_usage_data(customer_id, start_date, end_date)
            
            if not filtered_data:
                logger.warning(f"No usage data found for customer: {customer_id}")
                return None
            
            # Calcul des métriques
            total_usage = sum(event["amount"] for event in filtered_data)
            days_in_period = (end_date - start_date).days or 1
            average_daily_usage = total_usage / days_in_period
            peak_usage = max(event["amount"] for event in filtered_data)
            
            # Analyse des tendances
            trend_direction = await self._analyze_trend(filtered_data)
            usage_pattern = await self._analyze_pattern(filtered_data)
            efficiency_score = await self._calculate_efficiency_score(customer_id, filtered_data)
            
            # Génération de recommandations
            recommendations = await self._generate_recommendations(
                customer_id, filtered_data, efficiency_score
            )
            
            # Création du rapport
            report_id = f"report_{customer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            report = UsageReport(
                id=report_id,
                customer_id=customer_id,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date,
                total_usage=total_usage,
                average_daily_usage=average_daily_usage,
                peak_usage=peak_usage,
                trend_direction=trend_direction,
                usage_pattern=usage_pattern,
                efficiency_score=efficiency_score,
                recommendations=recommendations,
                generated_at=datetime.now()
            )
            
            # Stockage du rapport
            self.reports[report_id] = report
            
            logger.info(f"Usage report generated: {report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating usage report: {e}")
            return None

    async def generate_predictive_analytics(
        self,
        customer_id: str,
        prediction_timeframe: AnalyticsTimeframe
    ) -> Optional[PredictiveAnalytics]:
        """Génère des analytics prédictives
        
        Args:
            customer_id: ID du client
            prediction_timeframe: Période de prédiction
            
        Returns:
            Optional[PredictiveAnalytics]: Les analytics prédictives
        """
        try:
            # Récupération des données historiques
            historical_data = self._get_historical_data(customer_id, days=90)
            
            if len(historical_data) < 10:  # Pas assez de données
                logger.warning(f"Insufficient data for prediction: {customer_id}")
                return None
            
            # Prédiction d'usage
            predicted_usage, confidence = await self._predict_usage(
                historical_data, prediction_timeframe
            )
            
            # Analyse des facteurs
            factors_analyzed = await self._analyze_factors(historical_data)
            risk_factors = await self._identify_risk_factors(historical_data)
            opportunities = await self._identify_opportunities(historical_data)
            recommended_actions = await self._generate_action_recommendations(
                historical_data, predicted_usage, risk_factors, opportunities
            )
            
            # Création des analytics prédictives
            analytics = PredictiveAnalytics(
                customer_id=customer_id,
                predicted_usage=predicted_usage,
                confidence_level=confidence,
                prediction_timeframe=prediction_timeframe,
                factors_analyzed=factors_analyzed,
                risk_factors=risk_factors,
                opportunities=opportunities,
                recommended_actions=recommended_actions,
                generated_at=datetime.now()
            )
            
            # Stockage des analytics
            self.predictions[customer_id] = analytics
            
            logger.info(f"Predictive analytics generated: {customer_id}")
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating predictive analytics: {e}")
            return None

    def _calculate_start_date(
        self,
        end_date: datetime,
        timeframe: AnalyticsTimeframe
    ) -> datetime:
        """Calcule la date de début basée sur la période"""
        if timeframe == AnalyticsTimeframe.DAILY:
            return end_date - timedelta(days=1)
        elif timeframe == AnalyticsTimeframe.WEEKLY:
            return end_date - timedelta(weeks=1)
        elif timeframe == AnalyticsTimeframe.MONTHLY:
            return end_date - timedelta(days=30)
        elif timeframe == AnalyticsTimeframe.QUARTERLY:
            return end_date - timedelta(days=90)
        elif timeframe == AnalyticsTimeframe.YEARLY:
            return end_date - timedelta(days=365)
        else:
            return end_date - timedelta(days=30)  # Default to monthly

    def _filter_usage_data(
        self,
        customer_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Filtre les données d'usage pour une période"""
        return [
            event for event in self.usage_data
            if (event["customer_id"] == customer_id and
                start_date <= event["timestamp"] <= end_date)
        ]

    def _get_historical_data(self, customer_id: str, days: int) -> List[Dict[str, Any]]:
        """Récupère les données historiques"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [
            event for event in self.usage_data
            if (event["customer_id"] == customer_id and
                event["timestamp"] >= cutoff_date)
        ]

    async def _analyze_trend(self, data: List[Dict[str, Any]]) -> TrendDirection:
        """Analyse la tendance d'usage"""
        try:
            if len(data) < 3:
                return TrendDirection.STABLE
            
            # Groupement par jour
            daily_usage = {}
            for event in data:
                day = event["timestamp"].date()
                daily_usage[day] = daily_usage.get(day, 0) + event["amount"]
            
            if len(daily_usage) < 3:
                return TrendDirection.STABLE
            
            # Calcul de la tendance
            values = list(daily_usage.values())
            first_half = sum(values[:len(values)//2])
            second_half = sum(values[len(values)//2:])
            
            change_ratio = (second_half - first_half) / max(first_half, 1)
            
            if change_ratio > 0.2:
                return TrendDirection.INCREASING
            elif change_ratio < -0.2:
                return TrendDirection.DECREASING
            elif statistics.stdev(values) / statistics.mean(values) > 0.5:
                return TrendDirection.VOLATILE
            else:
                return TrendDirection.STABLE
                
        except Exception as e:
            logger.error(f"Error analyzing trend: {e}")
            return TrendDirection.STABLE

    async def _analyze_pattern(self, data: List[Dict[str, Any]]) -> UsagePattern:
        """Analyse le pattern d'usage"""
        try:
            if len(data) < 10:
                return UsagePattern.CONSISTENT
            
            # Groupement par jour
            daily_usage = {}
            for event in data:
                day = event["timestamp"].date()
                daily_usage[day] = daily_usage.get(day, 0) + event["amount"]
            
            values = list(daily_usage.values())
            
            if not values:
                return UsagePattern.CONSISTENT
            
            # Calcul des métriques
            mean_usage = statistics.mean(values)
            std_usage = statistics.stdev(values) if len(values) > 1 else 0
            cv = std_usage / mean_usage if mean_usage > 0 else 0
            
            # Classification du pattern
            if cv < 0.3:
                return UsagePattern.CONSISTENT
            elif cv > 0.8:
                # Vérification si c'est burst ou volatilité
                max_usage = max(values)
                if max_usage > mean_usage * 3:
                    return UsagePattern.BURST
                else:
                    return UsagePattern.SEASONAL
            else:
                # Analyse de la tendance pour growing/declining
                first_half = sum(values[:len(values)//2])
                second_half = sum(values[len(values)//2:])
                
                if second_half > first_half * 1.2:
                    return UsagePattern.GROWING
                elif second_half < first_half * 0.8:
                    return UsagePattern.DECLINING
                else:
                    return UsagePattern.CONSISTENT
                    
        except Exception as e:
            logger.error(f"Error analyzing pattern: {e}")
            return UsagePattern.CONSISTENT

    async def _calculate_efficiency_score(
        self,
        customer_id: str,
        data: List[Dict[str, Any]]
    ) -> float:
        """Calcule le score d'efficacité"""
        try:
            if not data:
                return 0.0
            
            # Métriques d'efficacité
            total_usage = sum(event["amount"] for event in data)
            unique_days = len(set(event["timestamp"].date() for event in data))
            
            # Score basé sur la régularité d'usage
            regularity_score = min(unique_days / 30, 1.0) * 0.4
            
            # Score basé sur l'optimisation (pas de pics excessifs)
            values = [event["amount"] for event in data]
            if len(values) > 1:
                mean_usage = statistics.mean(values)
                max_usage = max(values)
                optimization_score = min(mean_usage / max_usage, 1.0) * 0.3
            else:
                optimization_score = 0.5
            
            # Score basé sur l'utilisation par rapport aux benchmarks
            benchmark_score = 0.3  # Score par défaut
            
            total_score = regularity_score + optimization_score + benchmark_score
            return min(total_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating efficiency score: {e}")
            return 0.5

    async def _generate_recommendations(
        self,
        customer_id: str,
        data: List[Dict[str, Any]],
        efficiency_score: float
    ) -> List[str]:
        """Génère des recommandations d'usage"""
        recommendations = []
        
        try:
            # Recommandations basées sur l'efficacité
            if efficiency_score < 0.6:
                recommendations.append("Optimiser la distribution d'usage pour réduire les pics")
            
            # Recommandations basées sur l'usage
            total_usage = sum(event["amount"] for event in data)
            days = len(set(event["timestamp"].date() for event in data))
            
            if days > 0:
                avg_daily = total_usage / days
                if avg_daily > 1000:  # Seuil arbitraire
                    recommendations.append("Considérer un plan avec plus de quotas")
                elif avg_daily < 100:
                    recommendations.append("Optimiser l'usage pour maximiser la valeur du plan")
            
            # Recommandations par défaut
            if not recommendations:
                recommendations.append("Usage optimal - continuer les pratiques actuelles")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Analyser l'usage pour des recommandations personnalisées"]

    async def _predict_usage(
        self,
        historical_data: List[Dict[str, Any]],
        timeframe: AnalyticsTimeframe
    ) -> Tuple[int, float]:
        """Prédit l'usage futur"""
        try:
            # Groupement par jour
            daily_usage = {}
            for event in historical_data:
                day = event["timestamp"].date()
                daily_usage[day] = daily_usage.get(day, 0) + event["amount"]
            
            if not daily_usage:
                return 0, 0.0
            
            # Calcul de la moyenne mobile
            values = list(daily_usage.values())
            recent_avg = statistics.mean(values[-7:]) if len(values) >= 7 else statistics.mean(values)
            
            # Facteur de croissance
            if len(values) >= 14:
                older_avg = statistics.mean(values[:7])
                growth_factor = recent_avg / max(older_avg, 1)
            else:
                growth_factor = 1.0
            
            # Prédiction basée sur la période
            days_to_predict = self._get_days_for_timeframe(timeframe)
            predicted_usage = int(recent_avg * days_to_predict * growth_factor)
            
            # Confiance basée sur la consistance des données
            confidence = min(len(values) / 30, 1.0) * 0.8
            
            return predicted_usage, confidence
            
        except Exception as e:
            logger.error(f"Error predicting usage: {e}")
            return 0, 0.0

    def _get_days_for_timeframe(self, timeframe: AnalyticsTimeframe) -> int:
        """Retourne le nombre de jours pour une période"""
        if timeframe == AnalyticsTimeframe.WEEKLY:
            return 7
        elif timeframe == AnalyticsTimeframe.MONTHLY:
            return 30
        elif timeframe == AnalyticsTimeframe.QUARTERLY:
            return 90
        else:
            return 30  # Default

    async def _analyze_factors(self, data: List[Dict[str, Any]]) -> List[str]:
        """Analyse les facteurs d'influence"""
        factors = ["Usage historique", "Tendance temporelle"]
        
        # Analyse des métadonnées pour identifier d'autres facteurs
        metadata_keys = set()
        for event in data:
            if event.get("metadata"):
                metadata_keys.update(event["metadata"].keys())
        
        if "user_type" in metadata_keys:
            factors.append("Type d'utilisateur")
        if "campaign_id" in metadata_keys:
            factors.append("Campagnes marketing")
        
        return factors

    async def _identify_risk_factors(self, data: List[Dict[str, Any]]) -> List[str]:
        """Identifie les facteurs de risque"""
        risks = []
        
        # Risque de volatilité
        values = [event["amount"] for event in data]
        if len(values) > 1:
            cv = statistics.stdev(values) / statistics.mean(values)
            if cv > 0.8:
                risks.append("Usage volatil pouvant dépasser les quotas")
        
        # Risque de croissance rapide
        if len(values) >= 14:
            recent_avg = statistics.mean(values[-7:])
            older_avg = statistics.mean(values[:7])
            if recent_avg > older_avg * 1.5:
                risks.append("Croissance rapide d'usage")
        
        return risks

    async def _identify_opportunities(self, data: List[Dict[str, Any]]) -> List[str]:
        """Identifie les opportunités"""
        opportunities = []
        
        # Opportunité d'optimisation
        values = [event["amount"] for event in data]
        if len(values) > 1:
            mean_usage = statistics.mean(values)
            max_usage = max(values)
            if max_usage > mean_usage * 2:
                opportunities.append("Optimisation possible de la distribution d'usage")
        
        # Opportunité de plan adapté
        avg_daily = sum(values) / max(len(set(event["timestamp"].date() for event in data)), 1)
        if avg_daily < 500:  # Seuil arbitraire
            opportunities.append("Plan moins cher pourrait être adapté")
        
        return opportunities

    async def _generate_action_recommendations(
        self,
        data: List[Dict[str, Any]],
        predicted_usage: int,
        risk_factors: List[str],
        opportunities: List[str]
    ) -> List[str]:
        """Génère des recommandations d'actions"""
        actions = []
        
        if "Usage volatil pouvant dépasser les quotas" in risk_factors:
            actions.append("Mettre en place des alertes de quota")
        
        if "Croissance rapide d'usage" in risk_factors:
            actions.append("Considérer un upgrade préventif")
        
        if "Plan moins cher pourrait être adapté" in opportunities:
            actions.append("Évaluer un downgrade pour optimiser les coûts")
        
        if not actions:
            actions.append("Maintenir la surveillance de l'usage")
        
        return actions

    async def _cleanup_old_data(self, days_to_keep: int = 365):
        """Nettoie les anciennes données"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            initial_count = len(self.usage_data)
            
            self.usage_data = [
                event for event in self.usage_data
                if event["timestamp"] >= cutoff_date
            ]
            
            cleaned_count = initial_count - len(self.usage_data)
            if cleaned_count > 0:
                logger.info(f"Cleaned {cleaned_count} old usage records")
                
        except Exception as e:
            logger.error(f"Error cleaning old data: {e}")

    def get_customer_analytics_summary(self, customer_id: str) -> Dict[str, Any]:
        """Récupère un résumé des analytics pour un client"""
        try:
            # Données d'usage récentes
            recent_data = self._get_historical_data(customer_id, days=30)
            
            if not recent_data:
                return {"error": "No usage data found"}
            
            total_usage = sum(event["amount"] for event in recent_data)
            unique_days = len(set(event["timestamp"].date() for event in recent_data))
            avg_daily = total_usage / max(unique_days, 1)
            
            # Dernière prédiction
            prediction = self.predictions.get(customer_id)
            
            return {
                "customer_id": customer_id,
                "total_usage_30_days": total_usage,
                "average_daily_usage": avg_daily,
                "active_days": unique_days,
                "last_prediction": prediction.to_dict() if prediction else None,
                "reports_generated": len([r for r in self.reports.values() if r.customer_id == customer_id])
            }
            
        except Exception as e:
            logger.error(f"Error generating analytics summary: {e}")
            return {"error": str(e)}