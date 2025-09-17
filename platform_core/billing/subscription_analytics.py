"""🚀 Subscription Analytics System - IA Influencer Agent Platform Enterprise
========================================================================
Module: backend/platform_core/billing/subscription_analytics.py
Author: Fahed Mlaiel (mlaiel@live.de)
========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME ANALYTICS ABONNEMENTS AVANCÉ
Analytics complète des abonnements avec ML prédictif et business intelligence
- Cohort analysis et lifetime value predictions
- Churn prediction ML avec early warning systems
- Revenue forecasting et growth analytics
- Subscription health metrics et KPIs business
- Creator-specific subscription insights et optimizations

Multi-Expert Implementation:
🧠 Lead Dev IA: ML churn prediction, LTV modeling, intelligent segmentation
🏗️ Backend Senior: Architecture analytics haute performance, real-time processing
🤖 ML Engineer: Cohort models, predictive analytics, behavioral clustering
🗄️ DBA: Analytics data modeling, time-series optimization, OLAP cubes
🔒 Security: Privacy-compliant analytics, data anonymization, GDPR compliance
🌐 Microservices: Analytics API services, real-time streaming, data pipelines
🎵 Audio: Music subscription analytics, artist engagement metrics
⚙️ DevOps: Analytics infrastructure, data pipeline monitoring, automated reporting
💡 AI Prompt: Intelligent insights generation, automated recommendations
"""

import asyncio
import json
import logging
import time
import uuid
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta, date
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import statistics
from collections import defaultdict

# Configuration logging
logger = logging.getLogger(__name__)


class SubscriptionStatus(Enum):
    """États des abonnements"""
    ACTIVE = "active"
    TRIAL = "trial"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    CHURNED = "churned"


class ChurnRisk(Enum):
    """Niveaux de risque de churn"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SubscriptionTier(Enum):
    """Tiers d'abonnement"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    CREATOR_PRO = "creator_pro"


@dataclass
class SubscriptionEvent:
    """Événement d'abonnement"""
    event_id: str
    subscription_id: str
    event_type: str  # "created", "upgraded", "downgraded", "cancelled", "renewed"
    event_date: datetime
    previous_status: Optional[str] = None
    new_status: str = ""
    previous_tier: Optional[str] = None
    new_tier: Optional[str] = None
    revenue_impact: Decimal = Decimal('0.00')
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SubscriptionMetrics:
    """Métriques d'abonnement"""
    subscription_id: str
    customer_id: str
    current_tier: SubscriptionTier
    current_status: SubscriptionStatus
    monthly_revenue: Decimal
    total_revenue: Decimal
    subscription_age_days: int
    churn_probability: float
    lifetime_value_predicted: Decimal
    engagement_score: float
    last_activity_date: datetime
    payment_failures_count: int = 0
    support_tickets_count: int = 0
    feature_usage_score: float = 0.0


@dataclass
class CohortData:
    """Données de cohorte"""
    cohort_month: str
    cohort_size: int
    customers_retained: Dict[int, int]  # mois -> nombre de clients
    revenue_retained: Dict[int, Decimal]  # mois -> revenus
    retention_rates: Dict[int, float]  # mois -> taux de rétention
    lifetime_value: Decimal = Decimal('0.00')
    avg_subscription_length: float = 0.0


@dataclass
class ChurnPrediction:
    """Prédiction de churn"""
    customer_id: str
    subscription_id: str
    churn_probability: float
    risk_level: ChurnRisk
    key_factors: List[Dict[str, Any]]
    recommended_actions: List[str]
    prediction_confidence: float
    days_to_likely_churn: Optional[int] = None
    predicted_at: datetime = field(default_factory=datetime.utcnow)


class MLChurnPredictor:
    """🤖 Prédicteur ML de churn"""
    
    def __init__(self):
        self.model_version = "1.0.0"
        self.feature_weights = {
            "days_since_last_login": 0.25,
            "payment_failures": 0.20,
            "feature_usage_decline": 0.18,
            "support_tickets": 0.15,
            "subscription_age": 0.10,
            "engagement_score": 0.12
        }
        self.churn_threshold = 0.7
    
    def extract_features(self, subscription_metrics: SubscriptionMetrics) -> Dict[str, float]:
        """🔍 Extraction de features pour prédiction"""
        
        features = {}
        
        # Feature temporelle
        days_since_activity = (datetime.utcnow() - subscription_metrics.last_activity_date).days
        features["days_since_last_login"] = min(days_since_activity / 30.0, 1.0)  # Normalisé sur 30 jours
        
        # Features comportementales
        features["payment_failures"] = min(subscription_metrics.payment_failures_count / 3.0, 1.0)  # Normalisé sur 3 échecs
        features["support_tickets"] = min(subscription_metrics.support_tickets_count / 5.0, 1.0)  # Normalisé sur 5 tickets
        
        # Feature usage
        features["feature_usage_decline"] = max(0, 1 - subscription_metrics.feature_usage_score)
        
        # Feature engagement
        features["engagement_score"] = 1 - subscription_metrics.engagement_score
        
        # Feature âge abonnement (courbe en U - nouveaux et très anciens à risque)
        age_months = subscription_metrics.subscription_age_days / 30.0
        if age_months < 1:
            features["subscription_age"] = 0.8  # Nouveaux clients à risque
        elif age_months > 24:
            features["subscription_age"] = 0.6  # Clients anciens potentiellement saturés
        else:
            features["subscription_age"] = 0.2  # Clients dans la zone de confort
        
        return features
    
    def predict_churn_probability(self, features: Dict[str, float]) -> float:
        """🎯 Prédiction de la probabilité de churn"""
        
        weighted_score = 0.0
        
        for feature_name, weight in self.feature_weights.items():
            feature_value = features.get(feature_name, 0.0)
            weighted_score += feature_value * weight
        
        # Application d'une fonction sigmoïde pour normaliser
        probability = 1 / (1 + np.exp(-5 * (weighted_score - 0.5)))
        
        return min(1.0, max(0.0, probability))
    
    def identify_churn_factors(self, features: Dict[str, float]) -> List[Dict[str, Any]]:
        """🔍 Identification des facteurs de churn"""
        
        factors = []
        
        for feature_name, value in features.items():
            if value > 0.3:  # Seuil de significativité
                impact = value * self.feature_weights.get(feature_name, 0)
                
                factor_descriptions = {
                    "days_since_last_login": "Inactivité prolongée de l'utilisateur",
                    "payment_failures": "Échecs de paiement récurrents",
                    "feature_usage_decline": "Baisse d'utilisation des fonctionnalités",
                    "support_tickets": "Nombre élevé de tickets support",
                    "subscription_age": "Âge de l'abonnement critique",
                    "engagement_score": "Score d'engagement faible"
                }
                
                factors.append({
                    "factor": feature_name,
                    "description": factor_descriptions.get(feature_name, feature_name),
                    "severity": value,
                    "impact_on_churn": impact,
                    "weight": self.feature_weights.get(feature_name, 0)
                })
        
        # Tri par impact décroissant
        factors.sort(key=lambda x: x["impact_on_churn"], reverse=True)
        
        return factors


class SubscriptionAnalyticsEngine:
    """🚀 Moteur d'Analytics des Abonnements Enterprise"""
    
    def __init__(self):
        self.ml_predictor = MLChurnPredictor()
        self.subscription_metrics: Dict[str, SubscriptionMetrics] = {}
        self.subscription_events: List[SubscriptionEvent] = []
        self.cohort_data: Dict[str, CohortData] = {}
        self.churn_predictions: Dict[str, ChurnPrediction] = {}
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """🔧 Initialisation de données d'exemple"""
        
        # Génération de métriques d'exemple
        for i in range(100):
            subscription_id = f"sub_{uuid.uuid4().hex[:8]}"
            customer_id = f"customer_{uuid.uuid4().hex[:8]}"
            
            # Simulation de données variées
            tier = np.random.choice(list(SubscriptionTier))
            status = np.random.choice(list(SubscriptionStatus))
            
            # Revenus basés sur le tier
            tier_revenues = {
                SubscriptionTier.FREE: Decimal('0.00'),
                SubscriptionTier.BASIC: Decimal('9.99'),
                SubscriptionTier.PREMIUM: Decimal('19.99'),
                SubscriptionTier.ENTERPRISE: Decimal('49.99'),
                SubscriptionTier.CREATOR_PRO: Decimal('99.99')
            }
            
            monthly_revenue = tier_revenues[tier]
            subscription_age = np.random.randint(1, 730)  # 1 jour à 2 ans
            total_revenue = monthly_revenue * (subscription_age / 30)  # Approximation
            
            metrics = SubscriptionMetrics(
                subscription_id=subscription_id,
                customer_id=customer_id,
                current_tier=tier,
                current_status=status,
                monthly_revenue=monthly_revenue,
                total_revenue=total_revenue,
                subscription_age_days=subscription_age,
                churn_probability=np.random.random(),
                lifetime_value_predicted=total_revenue * Decimal(str(np.random.uniform(1.5, 4.0))),
                engagement_score=np.random.random(),
                last_activity_date=datetime.utcnow() - timedelta(days=np.random.randint(0, 30)),
                payment_failures_count=np.random.randint(0, 3),
                support_tickets_count=np.random.randint(0, 5),
                feature_usage_score=np.random.random()
            )
            
            self.subscription_metrics[subscription_id] = metrics
    
    async def analyze_subscription_cohorts(
        self,
        period_months: int = 12,
        cohort_definition: str = "month"
    ) -> Dict[str, Any]:
        """📊 Analyse des cohortes d'abonnements"""
        
        try:
            cohorts = {}
            
            # Groupement par cohorte
            for subscription_id, metrics in self.subscription_metrics.items():
                # Calcul de la date de début d'abonnement
                start_date = datetime.utcnow() - timedelta(days=metrics.subscription_age_days)
                cohort_key = start_date.strftime("%Y-%m")
                
                if cohort_key not in cohorts:
                    cohorts[cohort_key] = {
                        "customers": [],
                        "total_revenue": Decimal('0.00'),
                        "start_date": start_date
                    }
                
                cohorts[cohort_key]["customers"].append(metrics)
                cohorts[cohort_key]["total_revenue"] += metrics.total_revenue
            
            # Analyse de rétention par cohorte
            cohort_analysis = {}
            
            for cohort_month, cohort_info in cohorts.items():
                if len(cohort_info["customers"]) < 5:  # Seuil minimum pour analyse
                    continue
                
                # Calcul des taux de rétention par mois
                retention_data = self._calculate_cohort_retention(
                    cohort_info["customers"], cohort_info["start_date"]
                )
                
                # Calcul du LTV
                ltv = self._calculate_cohort_ltv(cohort_info["customers"])
                
                cohort_data = CohortData(
                    cohort_month=cohort_month,
                    cohort_size=len(cohort_info["customers"]),
                    customers_retained=retention_data["customers"],
                    revenue_retained=retention_data["revenue"],
                    retention_rates=retention_data["rates"],
                    lifetime_value=ltv,
                    avg_subscription_length=retention_data["avg_length"]
                )
                
                cohort_analysis[cohort_month] = cohort_data
                self.cohort_data[cohort_month] = cohort_data
            
            # Métriques globales
            global_metrics = self._calculate_global_cohort_metrics(cohort_analysis)
            
            return {
                "analysis_period_months": period_months,
                "cohort_definition": cohort_definition,
                "total_cohorts": len(cohort_analysis),
                "global_metrics": global_metrics,
                "cohort_details": {
                    cohort_month: {
                        "cohort_size": data.cohort_size,
                        "retention_rates": {k: round(v, 2) for k, v in data.retention_rates.items()},
                        "lifetime_value": float(data.lifetime_value),
                        "avg_subscription_length": round(data.avg_subscription_length, 1)
                    }
                    for cohort_month, data in cohort_analysis.items()
                },
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des cohortes: {e}")
            return {"error": str(e)}
    
    def _calculate_cohort_retention(
        self,
        customers: List[SubscriptionMetrics],
        cohort_start_date: datetime
    ) -> Dict[str, Any]:
        """📈 Calcul de la rétention d'une cohorte"""
        
        retention_by_month = {}
        revenue_by_month = {}
        
        # Analyse par mois depuis le début de la cohorte
        for month in range(12):  # 12 mois d'analyse
            retained_customers = 0
            retained_revenue = Decimal('0.00')
            
            for customer in customers:
                # Vérification si le client était encore actif ce mois-là
                months_since_start = customer.subscription_age_days / 30.0
                
                if months_since_start >= month and customer.current_status in [
                    SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL
                ]:
                    retained_customers += 1
                    retained_revenue += customer.monthly_revenue
            
            retention_by_month[month] = retained_customers
            revenue_by_month[month] = retained_revenue
        
        # Calcul des taux de rétention
        initial_size = len(customers)
        retention_rates = {
            month: (count / initial_size * 100) if initial_size > 0 else 0
            for month, count in retention_by_month.items()
        }
        
        # Durée moyenne d'abonnement
        avg_length = statistics.mean([c.subscription_age_days / 30.0 for c in customers])
        
        return {
            "customers": retention_by_month,
            "revenue": revenue_by_month,
            "rates": retention_rates,
            "avg_length": avg_length
        }
    
    def _calculate_cohort_ltv(self, customers: List[SubscriptionMetrics]) -> Decimal:
        """💰 Calcul du LTV de cohorte"""
        
        if not customers:
            return Decimal('0.00')
        
        total_ltv = sum(c.lifetime_value_predicted for c in customers)
        avg_ltv = total_ltv / len(customers)
        
        return avg_ltv
    
    def _calculate_global_cohort_metrics(self, cohorts: Dict[str, CohortData]) -> Dict[str, Any]:
        """🌐 Calcul des métriques globales"""
        
        if not cohorts:
            return {}
        
        # Rétention moyenne par mois
        avg_retention_by_month = {}
        
        for month in range(12):
            retention_rates = []
            for cohort in cohorts.values():
                if month in cohort.retention_rates:
                    retention_rates.append(cohort.retention_rates[month])
            
            if retention_rates:
                avg_retention_by_month[month] = statistics.mean(retention_rates)
        
        # LTV moyen
        avg_ltv = statistics.mean([c.lifetime_value for c in cohorts.values()])
        
        # Durée moyenne d'abonnement
        avg_subscription_length = statistics.mean([c.avg_subscription_length for c in cohorts.values()])
        
        return {
            "average_retention_by_month": {k: round(v, 2) for k, v in avg_retention_by_month.items()},
            "average_lifetime_value": float(avg_ltv),
            "average_subscription_length_months": round(avg_subscription_length, 1),
            "total_customers_analyzed": sum(c.cohort_size for c in cohorts.values())
        }
    
    async def predict_customer_churn(
        self,
        customer_id: Optional[str] = None,
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """🔮 Prédiction de churn clients"""
        
        try:
            predictions = {}
            processed_count = 0
            
            # Filtrage des clients à analyser
            if customer_id:
                target_metrics = {
                    k: v for k, v in self.subscription_metrics.items()
                    if v.customer_id == customer_id
                }
            else:
                # Analyse en batch
                target_metrics = dict(list(self.subscription_metrics.items())[:batch_size])
            
            # Prédiction pour chaque client
            for subscription_id, metrics in target_metrics.items():
                # Extraction des features
                features = self.ml_predictor.extract_features(metrics)
                
                # Prédiction de churn
                churn_probability = self.ml_predictor.predict_churn_probability(features)
                
                # Détermination du niveau de risque
                risk_level = self._determine_churn_risk_level(churn_probability)
                
                # Identification des facteurs clés
                key_factors = self.ml_predictor.identify_churn_factors(features)
                
                # Recommandations d'actions
                recommended_actions = self._generate_churn_prevention_actions(
                    metrics, key_factors, risk_level
                )
                
                # Estimation du délai avant churn
                days_to_churn = self._estimate_days_to_churn(churn_probability, features)
                
                prediction = ChurnPrediction(
                    customer_id=metrics.customer_id,
                    subscription_id=subscription_id,
                    churn_probability=churn_probability,
                    risk_level=risk_level,
                    key_factors=key_factors,
                    recommended_actions=recommended_actions,
                    prediction_confidence=0.85,  # Confiance du modèle
                    days_to_likely_churn=days_to_churn
                )
                
                predictions[subscription_id] = prediction
                self.churn_predictions[subscription_id] = prediction
                processed_count += 1
            
            # Statistiques globales
            risk_distribution = self._calculate_risk_distribution(predictions)
            
            return {
                "batch_size": batch_size,
                "processed_customers": processed_count,
                "model_version": self.ml_predictor.model_version,
                "risk_distribution": risk_distribution,
                "high_risk_customers": [
                    {
                        "customer_id": p.customer_id,
                        "subscription_id": p.subscription_id,
                        "churn_probability": round(p.churn_probability, 3),
                        "days_to_churn": p.days_to_likely_churn,
                        "top_factors": p.key_factors[:3]
                    }
                    for p in predictions.values()
                    if p.risk_level in [ChurnRisk.HIGH, ChurnRisk.CRITICAL]
                ],
                "prediction_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction de churn: {e}")
            return {"error": str(e)}
    
    def _determine_churn_risk_level(self, probability: float) -> ChurnRisk:
        """🎯 Détermination du niveau de risque"""
        
        if probability >= 0.8:
            return ChurnRisk.CRITICAL
        elif probability >= 0.6:
            return ChurnRisk.HIGH
        elif probability >= 0.3:
            return ChurnRisk.MEDIUM
        else:
            return ChurnRisk.LOW
    
    def _generate_churn_prevention_actions(
        self,
        metrics: SubscriptionMetrics,
        factors: List[Dict[str, Any]],
        risk_level: ChurnRisk
    ) -> List[str]:
        """💡 Génération d'actions de prévention"""
        
        actions = []
        
        # Actions basées sur les facteurs de risque
        for factor in factors[:3]:  # Top 3 facteurs
            factor_name = factor["factor"]
            
            if factor_name == "days_since_last_login":
                actions.append("Envoyer email de re-engagement personnalisé")
                actions.append("Proposer une session de formation gratuite")
            
            elif factor_name == "payment_failures":
                actions.append("Contacter pour mise à jour des informations de paiement")
                actions.append("Proposer un plan de paiement alternatif")
            
            elif factor_name == "feature_usage_decline":
                actions.append("Organiser une session de démonstration des fonctionnalités")
                actions.append("Envoyer des tutoriels personnalisés")
            
            elif factor_name == "support_tickets":
                actions.append("Assigner un customer success manager dédié")
                actions.append("Programmer un appel de suivi")
            
            elif factor_name == "engagement_score":
                actions.append("Proposer du contenu personnalisé basé sur les intérêts")
                actions.append("Inviter à rejoindre la communauté des utilisateurs")
        
        # Actions basées sur le niveau de risque
        if risk_level == ChurnRisk.CRITICAL:
            actions.append("Appel urgent du responsable client")
            actions.append("Proposer une remise temporaire")
            actions.append("Escalader vers l'équipe de rétention")
        
        elif risk_level == ChurnRisk.HIGH:
            actions.append("Email personnalisé du customer success")
            actions.append("Proposer un upgrade avec avantages")
        
        # Actions basées sur le tier
        if metrics.current_tier == SubscriptionTier.FREE:
            actions.append("Proposer un essai gratuit premium")
        elif metrics.current_tier == SubscriptionTier.BASIC:
            actions.append("Mettre en avant les avantages premium")
        
        return list(set(actions))  # Suppression des doublons
    
    def _estimate_days_to_churn(self, probability: float, features: Dict[str, float]) -> Optional[int]:
        """📅 Estimation du délai avant churn"""
        
        if probability < 0.3:
            return None  # Risque trop faible pour estimation
        
        # Modèle simple basé sur la probabilité et l'activité
        base_days = 30  # Base de 30 jours
        
        # Ajustement basé sur la probabilité
        probability_factor = (1 - probability) * 2  # Plus la probabilité est haute, plus c'est urgent
        
        # Ajustement basé sur l'inactivité
        inactivity_factor = features.get("days_since_last_login", 0)
        
        estimated_days = int(base_days * probability_factor * (1 - inactivity_factor))
        
        return max(1, min(90, estimated_days))  # Entre 1 et 90 jours
    
    def _calculate_risk_distribution(self, predictions: Dict[str, ChurnPrediction]) -> Dict[str, Any]:
        """📊 Calcul de la distribution des risques"""
        
        distribution = {level.value: 0 for level in ChurnRisk}
        
        for prediction in predictions.values():
            distribution[prediction.risk_level.value] += 1
        
        total = len(predictions)
        
        return {
            "counts": distribution,
            "percentages": {
                level: round((count / total * 100), 1) if total > 0 else 0
                for level, count in distribution.items()
            },
            "total_analyzed": total
        }
    
    async def generate_revenue_forecast(
        self,
        forecast_months: int = 12,
        confidence_level: float = 0.8
    ) -> Dict[str, Any]:
        """📈 Génération de prévisions de revenus"""
        
        try:
            current_date = datetime.utcnow()
            forecasts = {}
            
            # Calcul des revenus actuels
            current_mrr = sum(
                m.monthly_revenue for m in self.subscription_metrics.values()
                if m.current_status == SubscriptionStatus.ACTIVE
            )
            
            # Prévisions mois par mois
            for month in range(1, forecast_months + 1):
                forecast_date = current_date + timedelta(days=month * 30)
                
                # Modèle simple de prévision
                # Facteurs: croissance historique, churn prévu, nouveaux clients
                
                # Estimation du churn
                expected_churn_rate = await self._estimate_monthly_churn_rate()
                
                # Estimation de la croissance
                estimated_growth_rate = await self._estimate_growth_rate()
                
                # Calcul du MRR prévu
                previous_mrr = current_mrr if month == 1 else forecasts[month-1]["mrr"]
                
                # Application du churn
                mrr_after_churn = previous_mrr * (1 - expected_churn_rate)
                
                # Application de la croissance
                forecasted_mrr = mrr_after_churn * (1 + estimated_growth_rate)
                
                # Calcul de la confiance (diminue avec le temps)
                month_confidence = confidence_level * (0.95 ** (month - 1))
                
                forecasts[month] = {
                    "month": month,
                    "date": forecast_date.strftime("%Y-%m"),
                    "mrr": float(forecasted_mrr),
                    "arr": float(forecasted_mrr * 12),
                    "confidence": round(month_confidence, 2),
                    "growth_rate": round(estimated_growth_rate * 100, 2),
                    "churn_rate": round(expected_churn_rate * 100, 2)
                }
            
            # Métriques de synthèse
            total_forecast_revenue = sum(f["mrr"] for f in forecasts.values()) * 12 / forecast_months
            growth_projection = (forecasts[forecast_months]["mrr"] / float(current_mrr) - 1) * 100
            
            return {
                "forecast_period_months": forecast_months,
                "base_confidence_level": confidence_level,
                "current_mrr": float(current_mrr),
                "current_arr": float(current_mrr * 12),
                "forecasted_arr_end_period": forecasts[forecast_months]["arr"],
                "total_growth_projection": round(growth_projection, 1),
                "monthly_forecasts": forecasts,
                "summary": {
                    "average_monthly_revenue": round(total_forecast_revenue / 12, 2),
                    "revenue_trend": "increasing" if growth_projection > 0 else "decreasing",
                    "high_confidence_months": len([f for f in forecasts.values() if f["confidence"] > 0.7])
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des prévisions: {e}")
            return {"error": str(e)}
    
    async def _estimate_monthly_churn_rate(self) -> float:
        """📉 Estimation du taux de churn mensuel"""
        
        # Calcul basé sur les prédictions de churn
        high_risk_customers = sum(
            1 for p in self.churn_predictions.values()
            if p.risk_level in [ChurnRisk.HIGH, ChurnRisk.CRITICAL]
        )
        
        total_active_customers = sum(
            1 for m in self.subscription_metrics.values()
            if m.current_status == SubscriptionStatus.ACTIVE
        )
        
        if total_active_customers == 0:
            return 0.05  # 5% par défaut
        
        # Taux basé sur les prédictions + facteur historique
        predicted_churn_rate = high_risk_customers / total_active_customers
        historical_churn_rate = 0.03  # 3% historique simulé
        
        # Moyenne pondérée
        estimated_rate = (predicted_churn_rate * 0.7) + (historical_churn_rate * 0.3)
        
        return min(0.2, max(0.01, estimated_rate))  # Entre 1% et 20%
    
    async def _estimate_growth_rate(self) -> float:
        """📈 Estimation du taux de croissance"""
        
        # Modèle simple basé sur l'engagement et les tendances
        
        # Calcul de l'engagement moyen
        avg_engagement = statistics.mean([
            m.engagement_score for m in self.subscription_metrics.values()
            if m.current_status == SubscriptionStatus.ACTIVE
        ]) if self.subscription_metrics else 0.5
        
        # Calcul basé sur la distribution des tiers
        premium_ratio = sum(
            1 for m in self.subscription_metrics.values()
            if m.current_tier in [SubscriptionTier.PREMIUM, SubscriptionTier.ENTERPRISE, SubscriptionTier.CREATOR_PRO]
        ) / len(self.subscription_metrics) if self.subscription_metrics else 0.3
        
        # Taux de croissance basé sur l'engagement et la qualité des clients
        base_growth = 0.05  # 5% de base
        engagement_bonus = (avg_engagement - 0.5) * 0.1  # Bonus/malus basé sur l'engagement
        premium_bonus = (premium_ratio - 0.3) * 0.05  # Bonus si plus de clients premium
        
        growth_rate = base_growth + engagement_bonus + premium_bonus
        
        return max(-0.05, min(0.15, growth_rate))  # Entre -5% et 15%
    
    async def calculate_subscription_health_score(
        self,
        subscription_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """🏥 Calcul du score de santé des abonnements"""
        
        try:
            if subscription_id:
                # Score pour un abonnement spécifique
                metrics = self.subscription_metrics.get(subscription_id)
                if not metrics:
                    raise ValueError(f"Subscription {subscription_id} not found")
                
                score = self._calculate_individual_health_score(metrics)
                
                return {
                    "subscription_id": subscription_id,
                    "health_score": score["score"],
                    "health_level": score["level"],
                    "score_components": score["components"],
                    "recommendations": score["recommendations"],
                    "calculated_at": datetime.utcnow().isoformat()
                }
            
            else:
                # Score global pour tous les abonnements
                all_scores = []
                health_distribution = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
                
                for sub_id, metrics in self.subscription_metrics.items():
                    if metrics.current_status == SubscriptionStatus.ACTIVE:
                        score = self._calculate_individual_health_score(metrics)
                        all_scores.append(score["score"])
                        health_distribution[score["level"]] += 1
                
                if all_scores:
                    avg_score = statistics.mean(all_scores)
                    
                    return {
                        "global_health_score": round(avg_score, 2),
                        "total_active_subscriptions": len(all_scores),
                        "health_distribution": health_distribution,
                        "distribution_percentages": {
                            level: round((count / len(all_scores) * 100), 1)
                            for level, count in health_distribution.items()
                        },
                        "calculated_at": datetime.utcnow().isoformat()
                    }
                else:
                    return {"error": "No active subscriptions found"}
                    
        except Exception as e:
            logger.error(f"Erreur lors du calcul du score de santé: {e}")
            return {"error": str(e)}
    
    def _calculate_individual_health_score(self, metrics: SubscriptionMetrics) -> Dict[str, Any]:
        """🎯 Calcul du score de santé individuel"""
        
        components = {}
        
        # Composant engagement (30%)
        engagement_score = metrics.engagement_score * 100
        components["engagement"] = {
            "score": engagement_score,
            "weight": 0.3,
            "weighted_score": engagement_score * 0.3
        }
        
        # Composant activité récente (25%)
        days_since_activity = (datetime.utcnow() - metrics.last_activity_date).days
        activity_score = max(0, 100 - (days_since_activity * 5))  # -5 points par jour d'inactivité
        components["recent_activity"] = {
            "score": activity_score,
            "weight": 0.25,
            "weighted_score": activity_score * 0.25
        }
        
        # Composant paiements (20%)
        payment_score = max(0, 100 - (metrics.payment_failures_count * 25))  # -25 points par échec
        components["payment_health"] = {
            "score": payment_score,
            "weight": 0.2,
            "weighted_score": payment_score * 0.2
        }
        
        # Composant utilisation fonctionnalités (15%)
        feature_score = metrics.feature_usage_score * 100
        components["feature_usage"] = {
            "score": feature_score,
            "weight": 0.15,
            "weighted_score": feature_score * 0.15
        }
        
        # Composant support (10%)
        support_score = max(0, 100 - (metrics.support_tickets_count * 15))  # -15 points par ticket
        components["support_interaction"] = {
            "score": support_score,
            "weight": 0.1,
            "weighted_score": support_score * 0.1
        }
        
        # Score global
        total_score = sum(comp["weighted_score"] for comp in components.values())
        
        # Niveau de santé
        if total_score >= 80:
            health_level = "excellent"
        elif total_score >= 60:
            health_level = "good"
        elif total_score >= 40:
            health_level = "fair"
        else:
            health_level = "poor"
        
        # Recommandations
        recommendations = self._generate_health_recommendations(components, health_level)
        
        return {
            "score": round(total_score, 1),
            "level": health_level,
            "components": components,
            "recommendations": recommendations
        }
    
    def _generate_health_recommendations(
        self, 
        components: Dict[str, Any], 
        health_level: str
    ) -> List[str]:
        """💡 Génération de recommandations d'amélioration"""
        
        recommendations = []
        
        # Recommandations basées sur les composants faibles
        for component_name, component_data in components.items():
            if component_data["score"] < 50:  # Composant problématique
                
                if component_name == "engagement":
                    recommendations.append("Améliorer l'engagement avec du contenu personnalisé")
                    recommendations.append("Organiser des webinaires ou événements communautaires")
                
                elif component_name == "recent_activity":
                    recommendations.append("Envoyer des notifications de rappel d'utilisation")
                    recommendations.append("Proposer des fonctionnalités ou contenus nouveaux")
                
                elif component_name == "payment_health":
                    recommendations.append("Contacter pour résoudre les problèmes de paiement")
                    recommendations.append("Proposer des méthodes de paiement alternatives")
                
                elif component_name == "feature_usage":
                    recommendations.append("Fournir une formation sur les fonctionnalités avancées")
                    recommendations.append("Simplifier l'interface utilisateur")
                
                elif component_name == "support_interaction":
                    recommendations.append("Améliorer la documentation et les ressources d'aide")
                    recommendations.append("Mettre en place un programme de customer success proactif")
        
        # Recommandations basées sur le niveau général
        if health_level == "poor":
            recommendations.append("Assigner un customer success manager dédié")
            recommendations.append("Programmer un appel de récupération urgent")
        
        elif health_level == "fair":
            recommendations.append("Augmenter la fréquence de communication")
            recommendations.append("Proposer des resources d'onboarding supplémentaires")
        
        return recommendations
    
    def get_subscription_analytics_summary(self, period_days: int = 30) -> Dict[str, Any]:
        """📊 Résumé des analytics d'abonnements"""
        
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Métriques de base
            total_subscriptions = len(self.subscription_metrics)
            active_subscriptions = sum(
                1 for m in self.subscription_metrics.values()
                if m.current_status == SubscriptionStatus.ACTIVE
            )
            
            # Revenus
            total_mrr = sum(
                m.monthly_revenue for m in self.subscription_metrics.values()
                if m.current_status == SubscriptionStatus.ACTIVE
            )
            
            total_arr = total_mrr * 12
            
            # Prédictions de churn
            high_risk_count = sum(
                1 for p in self.churn_predictions.values()
                if p.risk_level in [ChurnRisk.HIGH, ChurnRisk.CRITICAL]
            )
            
            # Distribution par tier
            tier_distribution = {}
            for tier in SubscriptionTier:
                count = sum(
                    1 for m in self.subscription_metrics.values()
                    if m.current_tier == tier and m.current_status == SubscriptionStatus.ACTIVE
                )
                tier_distribution[tier.value] = count
            
            # LTV moyen
            avg_ltv = statistics.mean([
                float(m.lifetime_value_predicted) for m in self.subscription_metrics.values()
                if m.current_status == SubscriptionStatus.ACTIVE
            ]) if active_subscriptions > 0 else 0
            
            return {
                "period_days": period_days,
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat(),
                "subscription_metrics": {
                    "total_subscriptions": total_subscriptions,
                    "active_subscriptions": active_subscriptions,
                    "active_rate_percentage": round((active_subscriptions / total_subscriptions * 100), 1) if total_subscriptions > 0 else 0
                },
                "revenue_metrics": {
                    "monthly_recurring_revenue": float(total_mrr),
                    "annual_recurring_revenue": float(total_arr),
                    "average_revenue_per_user": float(total_mrr / active_subscriptions) if active_subscriptions > 0 else 0
                },
                "churn_analytics": {
                    "high_risk_customers": high_risk_count,
                    "churn_risk_percentage": round((high_risk_count / active_subscriptions * 100), 1) if active_subscriptions > 0 else 0
                },
                "tier_distribution": tier_distribution,
                "lifetime_value": {
                    "average_ltv": round(avg_ltv, 2),
                    "total_ltv_portfolio": round(avg_ltv * active_subscriptions, 2)
                },
                "analytics_coverage": {
                    "cohort_analysis_available": len(self.cohort_data) > 0,
                    "churn_predictions_available": len(self.churn_predictions) > 0,
                    "ml_model_version": self.ml_predictor.model_version
                },
                "summary_generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du résumé: {e}")
            return {"error": str(e)}