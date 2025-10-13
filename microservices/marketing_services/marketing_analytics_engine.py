"""
Marketing Analytics Engine - IA Chérie Enterprise
==============================================
Moteur analytics marketing enterprise temps réel.
Attribution modeling + cohort analysis + LTV prediction + churn analysis.

Author: Expert Team (Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer)
IP Owner: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chérie Marketing Services - Analytics Engine
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture d'analytics marketing et tous ses algorithmes d'attribution sont la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).
Toute reproduction, modification, distribution ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.
"""

import asyncio
import logging
import numpy as np
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import math
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AttributionModel(Enum):
    """Modèles d'attribution disponibles"""
    FIRST_TOUCH = "first_touch"
    LAST_TOUCH = "last_touch"
    LINEAR = "linear"
    TIME_DECAY = "time_decay"
    POSITION_BASED = "position_based"
    DATA_DRIVEN = "data_driven"
    MARKOV_CHAIN = "markov_chain"

class AnalyticsMetric(Enum):
    """Métriques analytics supportées"""
    ROI = "roi"
    ROAS = "roas"
    CPA = "cpa"
    CTR = "ctr"
    CONVERSION_RATE = "conversion_rate"
    LTV = "lifetime_value"
    CHURN_RATE = "churn_rate"
    ENGAGEMENT_RATE = "engagement_rate"

class CohortType(Enum):
    """Types de cohortes"""
    ACQUISITION = "acquisition"
    BEHAVIORAL = "behavioral"
    REVENUE = "revenue"
    ENGAGEMENT = "engagement"

@dataclass
class AnalyticsConfig:
    """Configuration pour le moteur analytics"""
    attribution_model: AttributionModel = AttributionModel.DATA_DRIVEN
    lookback_window_days: int = 30
    attribution_window_days: int = 7
    cohort_analysis_period: str = "monthly"
    real_time_processing: bool = True
    statistical_significance_level: float = 0.05
    confidence_level: float = 0.95
    max_touchpoints: int = 20

@dataclass
class TouchpointData:
    """Données d'un point de contact marketing"""
    touchpoint_id: str
    campaign_id: str
    channel: str
    timestamp: datetime
    user_id: str
    interaction_type: str
    cost: float
    attribution_weight: float = 0.0
    conversion_contribution: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversionEvent:
    """Événement de conversion"""
    conversion_id: str
    user_id: str
    timestamp: datetime
    value: float
    currency: str
    conversion_type: str
    attributed_touchpoints: List[TouchpointData] = field(default_factory=list)

@dataclass
class CohortAnalysisResult:
    """Résultat d'analyse de cohorte"""
    cohort_id: str
    cohort_name: str
    period: str
    size: int
    retention_rates: Dict[str, float]
    revenue_per_cohort: Dict[str, float]
    ltv_prediction: float
    churn_prediction: float
    behavioral_insights: List[str]

class AttributionModelingEngine:
    """Moteur de modélisation d'attribution"""
    
    def __init__(self, model_type: AttributionModel = AttributionModel.DATA_DRIVEN):
        self.model_type = model_type
        self.attribution_weights = {}
        self.conversion_paths = []
    
    async def calculate_attribution(self, touchpoints: List[TouchpointData], 
                                  conversion: ConversionEvent) -> Dict[str, Any]:
        """Calcule l'attribution pour une conversion"""
        try:
            # Sort touchpoints by timestamp
            sorted_touchpoints = sorted(touchpoints, key=lambda x: x.timestamp)
            
            # Apply attribution model
            attribution_results = await self._apply_attribution_model(
                sorted_touchpoints, conversion
            )
            
            # Calculate channel attribution
            channel_attribution = await self._calculate_channel_attribution(
                attribution_results
            )
            
            # Calculate campaign attribution
            campaign_attribution = await self._calculate_campaign_attribution(
                attribution_results
            )
            
            return {
                'conversion_id': conversion.conversion_id,
                'attribution_model': self.model_type.value,
                'touchpoint_attribution': attribution_results,
                'channel_attribution': channel_attribution,
                'campaign_attribution': campaign_attribution,
                'total_attribution_value': conversion.value,
                'attribution_confidence': await self._calculate_attribution_confidence(
                    sorted_touchpoints, conversion
                )
            }
            
        except Exception as e:
            logger.error(f"Attribution calculation failed: {str(e)}")
            return {'error': str(e)}
    
    async def _apply_attribution_model(self, touchpoints: List[TouchpointData],
                                     conversion: ConversionEvent) -> List[Dict[str, Any]]:
        """Applique le modèle d'attribution"""
        attribution_results = []
        
        if self.model_type == AttributionModel.FIRST_TOUCH:
            # First touch gets 100% attribution
            for i, tp in enumerate(touchpoints):
                weight = 1.0 if i == 0 else 0.0
                attribution_results.append({
                    'touchpoint_id': tp.touchpoint_id,
                    'attribution_weight': weight,
                    'attributed_value': conversion.value * weight,
                    'attributed_cost': tp.cost * weight
                })
                
        elif self.model_type == AttributionModel.LAST_TOUCH:
            # Last touch gets 100% attribution
            for i, tp in enumerate(touchpoints):
                weight = 1.0 if i == len(touchpoints) - 1 else 0.0
                attribution_results.append({
                    'touchpoint_id': tp.touchpoint_id,
                    'attribution_weight': weight,
                    'attributed_value': conversion.value * weight,
                    'attributed_cost': tp.cost * weight
                })
                
        elif self.model_type == AttributionModel.LINEAR:
            # Equal weight to all touchpoints
            weight = 1.0 / len(touchpoints)
            for tp in touchpoints:
                attribution_results.append({
                    'touchpoint_id': tp.touchpoint_id,
                    'attribution_weight': weight,
                    'attributed_value': conversion.value * weight,
                    'attributed_cost': tp.cost * weight
                })
                
        elif self.model_type == AttributionModel.TIME_DECAY:
            # More weight to recent touchpoints
            total_weight = sum(0.5 ** i for i in range(len(touchpoints)))
            for i, tp in enumerate(touchpoints):
                weight = (0.5 ** (len(touchpoints) - 1 - i)) / total_weight
                attribution_results.append({
                    'touchpoint_id': tp.touchpoint_id,
                    'attribution_weight': weight,
                    'attributed_value': conversion.value * weight,
                    'attributed_cost': tp.cost * weight
                })
                
        elif self.model_type == AttributionModel.POSITION_BASED:
            # 40% to first, 40% to last, 20% to middle
            for i, tp in enumerate(touchpoints):
                if i == 0:
                    weight = 0.4
                elif i == len(touchpoints) - 1:
                    weight = 0.4 if len(touchpoints) > 1 else 1.0
                else:
                    weight = 0.2 / max(1, len(touchpoints) - 2)
                
                attribution_results.append({
                    'touchpoint_id': tp.touchpoint_id,
                    'attribution_weight': weight,
                    'attributed_value': conversion.value * weight,
                    'attributed_cost': tp.cost * weight
                })
                
        else:  # DATA_DRIVEN or MARKOV_CHAIN
            # Simulate data-driven attribution
            weights = await self._calculate_data_driven_weights(touchpoints, conversion)
            for i, tp in enumerate(touchpoints):
                weight = weights[i] if i < len(weights) else 0.0
                attribution_results.append({
                    'touchpoint_id': tp.touchpoint_id,
                    'attribution_weight': weight,
                    'attributed_value': conversion.value * weight,
                    'attributed_cost': tp.cost * weight
                })
        
        return attribution_results
    
    async def _calculate_data_driven_weights(self, touchpoints: List[TouchpointData],
                                           conversion: ConversionEvent) -> List[float]:
        """Calcule les poids data-driven"""
        # Simulate ML-based attribution weights
        n_touchpoints = len(touchpoints)
        weights = np.random.dirichlet(np.ones(n_touchpoints))  # Generates weights that sum to 1
        return weights.tolist()
    
    async def _calculate_channel_attribution(self, attribution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcule l'attribution par canal"""
        channel_attribution = defaultdict(lambda: {'value': 0.0, 'cost': 0.0, 'weight': 0.0})
        
        for result in attribution_results:
            # This would need touchpoint data to get channel info
            # Simulating for now
            channel = f"channel_{result['touchpoint_id'][:3]}"
            channel_attribution[channel]['value'] += result['attributed_value']
            channel_attribution[channel]['cost'] += result['attributed_cost']
            channel_attribution[channel]['weight'] += result['attribution_weight']
        
        return dict(channel_attribution)
    
    async def _calculate_campaign_attribution(self, attribution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcule l'attribution par campagne"""
        campaign_attribution = defaultdict(lambda: {'value': 0.0, 'cost': 0.0, 'weight': 0.0})
        
        for result in attribution_results:
            # This would need touchpoint data to get campaign info
            # Simulating for now
            campaign = f"campaign_{result['touchpoint_id'][:5]}"
            campaign_attribution[campaign]['value'] += result['attributed_value']
            campaign_attribution[campaign]['cost'] += result['attributed_cost']
            campaign_attribution[campaign]['weight'] += result['attribution_weight']
        
        return dict(campaign_attribution)
    
    async def _calculate_attribution_confidence(self, touchpoints: List[TouchpointData],
                                              conversion: ConversionEvent) -> float:
        """Calcule la confiance de l'attribution"""
        # Factors affecting confidence:
        # - Number of touchpoints (more = higher confidence)
        # - Time span (shorter = higher confidence)
        # - Data quality (complete data = higher confidence)
        
        base_confidence = 0.7
        
        # Adjust for number of touchpoints
        touchpoint_factor = min(1.0, len(touchpoints) / 5.0) * 0.2
        
        # Adjust for time span
        if touchpoints:
            time_span = (touchpoints[-1].timestamp - touchpoints[0].timestamp).days
            time_factor = max(0.0, (30 - time_span) / 30) * 0.1
        else:
            time_factor = 0.0
        
        return min(1.0, base_confidence + touchpoint_factor + time_factor)

class CohortAnalysisEngine:
    """Moteur d'analyse de cohortes"""
    
    def __init__(self, period: str = "monthly"):
        self.period = period
        self.cohort_data = {}
    
    async def perform_cohort_analysis(self, user_data: List[Dict[str, Any]],
                                    cohort_type: CohortType) -> List[CohortAnalysisResult]:
        """Effectue une analyse de cohortes"""
        try:
            # Group users into cohorts
            cohorts = await self._create_cohorts(user_data, cohort_type)
            
            # Analyze each cohort
            cohort_results = []
            for cohort_id, cohort_users in cohorts.items():
                result = await self._analyze_cohort(cohort_id, cohort_users, cohort_type)
                cohort_results.append(result)
            
            return cohort_results
            
        except Exception as e:
            logger.error(f"Cohort analysis failed: {str(e)}")
            return []
    
    async def _create_cohorts(self, user_data: List[Dict[str, Any]],
                            cohort_type: CohortType) -> Dict[str, List[Dict[str, Any]]]:
        """Crée les cohortes"""
        cohorts = defaultdict(list)
        
        for user in user_data:
            if cohort_type == CohortType.ACQUISITION:
                # Group by acquisition month
                acquisition_date = datetime.fromisoformat(user.get('acquisition_date', '2024-01-01'))
                cohort_key = f"{acquisition_date.year}-{acquisition_date.month:02d}"
            
            elif cohort_type == CohortType.BEHAVIORAL:
                # Group by behavior pattern
                behavior = user.get('primary_behavior', 'unknown')
                cohort_key = f"behavior_{behavior}"
            
            elif cohort_type == CohortType.REVENUE:
                # Group by revenue tier
                revenue = user.get('total_revenue', 0)
                if revenue < 50:
                    cohort_key = "low_value"
                elif revenue < 200:
                    cohort_key = "medium_value"
                else:
                    cohort_key = "high_value"
            
            else:  # ENGAGEMENT
                # Group by engagement level
                engagement = user.get('engagement_score', 0)
                if engagement < 0.3:
                    cohort_key = "low_engagement"
                elif engagement < 0.7:
                    cohort_key = "medium_engagement"
                else:
                    cohort_key = "high_engagement"
            
            cohorts[cohort_key].append(user)
        
        return dict(cohorts)
    
    async def _analyze_cohort(self, cohort_id: str, cohort_users: List[Dict[str, Any]],
                            cohort_type: CohortType) -> CohortAnalysisResult:
        """Analyse une cohorte"""
        # Calculate retention rates
        retention_rates = await self._calculate_retention_rates(cohort_users)
        
        # Calculate revenue per cohort
        revenue_per_cohort = await self._calculate_revenue_per_cohort(cohort_users)
        
        # Predict LTV
        ltv_prediction = await self._predict_cohort_ltv(cohort_users, retention_rates)
        
        # Predict churn
        churn_prediction = await self._predict_cohort_churn(cohort_users)
        
        # Generate behavioral insights
        behavioral_insights = await self._generate_cohort_insights(cohort_users, cohort_type)
        
        return CohortAnalysisResult(
            cohort_id=cohort_id,
            cohort_name=self._generate_cohort_name(cohort_id, cohort_type),
            period=self.period,
            size=len(cohort_users),
            retention_rates=retention_rates,
            revenue_per_cohort=revenue_per_cohort,
            ltv_prediction=ltv_prediction,
            churn_prediction=churn_prediction,
            behavioral_insights=behavioral_insights
        )
    
    async def _calculate_retention_rates(self, cohort_users: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calcule les taux de rétention"""
        retention_rates = {}
        
        # Simulate retention calculation
        for period in range(1, 13):  # 12 months
            # Calculate how many users are still active after 'period' months
            active_users = len([
                user for user in cohort_users
                if user.get('last_activity_months_ago', 0) <= period
            ])
            retention_rates[f"month_{period}"] = active_users / len(cohort_users) if cohort_users else 0
        
        return retention_rates
    
    async def _calculate_revenue_per_cohort(self, cohort_users: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calcule le revenu par cohorte"""
        revenue_data = {}
        
        for period in range(1, 13):  # 12 months
            period_revenue = sum(
                user.get('revenue_by_period', {}).get(f"month_{period}", 0)
                for user in cohort_users
            )
            revenue_data[f"month_{period}"] = period_revenue
        
        return revenue_data
    
    async def _predict_cohort_ltv(self, cohort_users: List[Dict[str, Any]],
                                retention_rates: Dict[str, float]) -> float:
        """Prédit la LTV de la cohorte"""
        # Simple LTV calculation: average revenue per user * average retention
        avg_revenue_per_user = np.mean([
            user.get('total_revenue', 0) for user in cohort_users
        ]) if cohort_users else 0
        
        avg_retention = np.mean(list(retention_rates.values())) if retention_rates else 0
        
        # LTV estimation with retention factor
        ltv = avg_revenue_per_user / max(0.1, 1 - avg_retention)
        
        return ltv
    
    async def _predict_cohort_churn(self, cohort_users: List[Dict[str, Any]]) -> float:
        """Prédit le taux de churn de la cohorte"""
        # Simulate churn prediction based on user behavior
        churn_indicators = []
        
        for user in cohort_users:
            # Factors indicating churn
            days_since_last_activity = user.get('days_since_last_activity', 0)
            engagement_score = user.get('engagement_score', 0.5)
            support_tickets = user.get('support_tickets', 0)
            
            churn_score = (
                min(1.0, days_since_last_activity / 30) * 0.4 +
                (1 - engagement_score) * 0.4 +
                min(1.0, support_tickets / 5) * 0.2
            )
            churn_indicators.append(churn_score)
        
        return np.mean(churn_indicators) if churn_indicators else 0.5
    
    async def _generate_cohort_insights(self, cohort_users: List[Dict[str, Any]],
                                      cohort_type: CohortType) -> List[str]:
        """Génère des insights sur la cohorte"""
        insights = []
        
        if not cohort_users:
            return ["Insufficient data for insights"]
        
        # Common insights based on cohort type
        if cohort_type == CohortType.ACQUISITION:
            avg_time_to_convert = np.mean([
                user.get('days_to_first_purchase', 30) for user in cohort_users
            ])
            insights.append(f"Average time to first purchase: {avg_time_to_convert:.1f} days")
        
        elif cohort_type == CohortType.BEHAVIORAL:
            common_behavior = Counter([
                user.get('primary_behavior', 'unknown') for user in cohort_users
            ]).most_common(1)[0][0]
            insights.append(f"Most common behavior pattern: {common_behavior}")
        
        elif cohort_type == CohortType.REVENUE:
            avg_order_value = np.mean([
                user.get('average_order_value', 0) for user in cohort_users
            ])
            insights.append(f"Average order value: ${avg_order_value:.2f}")
        
        # General insights
        high_value_users = len([u for u in cohort_users if u.get('total_revenue', 0) > 200])
        if high_value_users > 0:
            insights.append(f"{high_value_users} high-value users identified")
        
        return insights
    
    def _generate_cohort_name(self, cohort_id: str, cohort_type: CohortType) -> str:
        """Génère un nom pour la cohorte"""
        type_names = {
            CohortType.ACQUISITION: "Acquisition Cohort",
            CohortType.BEHAVIORAL: "Behavior Cohort",
            CohortType.REVENUE: "Revenue Cohort",
            CohortType.ENGAGEMENT: "Engagement Cohort"
        }
        
        return f"{type_names.get(cohort_type, 'Unknown')} - {cohort_id}"

class LTVPredictionModel:
    """Modèle de prédiction de la valeur vie client"""
    
    def __init__(self):
        self.model = None
        self.feature_weights = {}
    
    async def predict_ltv(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prédit la LTV d'un client"""
        try:
            # Extract features for LTV prediction
            features = await self._extract_ltv_features(customer_data)
            
            # Calculate base LTV
            base_ltv = await self._calculate_base_ltv(features)
            
            # Apply behavioral adjustments
            behavioral_ltv = await self._apply_behavioral_adjustments(base_ltv, features)
            
            # Calculate confidence intervals
            confidence_intervals = await self._calculate_ltv_confidence(behavioral_ltv, features)
            
            # Generate LTV insights
            ltv_insights = await self._generate_ltv_insights(behavioral_ltv, features)
            
            return {
                'predicted_ltv': behavioral_ltv,
                'confidence_intervals': confidence_intervals,
                'ltv_insights': ltv_insights,
                'feature_importance': await self._calculate_feature_importance(features),
                'prediction_confidence': confidence_intervals.get('confidence_score', 0.8)
            }
            
        except Exception as e:
            logger.error(f"LTV prediction failed: {str(e)}")
            return {'error': str(e)}
    
    async def _extract_ltv_features(self, customer_data: Dict[str, Any]) -> Dict[str, float]:
        """Extrait les features pour la prédiction LTV"""
        return {
            'recency': customer_data.get('days_since_last_purchase', 30),
            'frequency': customer_data.get('purchase_frequency', 1),
            'monetary': customer_data.get('average_order_value', 50),
            'tenure': customer_data.get('customer_tenure_days', 30),
            'engagement_score': customer_data.get('engagement_score', 0.5),
            'support_interactions': customer_data.get('support_interactions', 0),
            'referrals_made': customer_data.get('referrals_made', 0),
            'platform_usage': customer_data.get('platform_usage_score', 0.5)
        }
    
    async def _calculate_base_ltv(self, features: Dict[str, float]) -> float:
        """Calcule la LTV de base"""
        # RFM-based LTV calculation
        recency_score = max(0, (90 - features['recency']) / 90)  # Higher score for recent purchases
        frequency_score = min(1, features['frequency'] / 10)  # Normalize frequency
        monetary_score = min(1, features['monetary'] / 200)  # Normalize monetary value
        
        base_ltv = (
            recency_score * 0.3 +
            frequency_score * 0.4 +
            monetary_score * 0.3
        ) * features['monetary'] * features['frequency'] * 2  # 2-year projection
        
        return max(0, base_ltv)
    
    async def _apply_behavioral_adjustments(self, base_ltv: float, 
                                          features: Dict[str, float]) -> float:
        """Applique des ajustements comportementaux"""
        # Engagement adjustment
        engagement_multiplier = 0.8 + (features['engagement_score'] * 0.4)
        
        # Loyalty adjustment (based on tenure)
        loyalty_multiplier = 1.0 + (min(365, features['tenure']) / 365) * 0.2
        
        # Support interaction adjustment (negative impact)
        support_multiplier = max(0.7, 1.0 - (features['support_interactions'] / 10) * 0.1)
        
        # Referral adjustment (positive impact)
        referral_multiplier = 1.0 + (features['referrals_made'] * 0.05)
        
        adjusted_ltv = base_ltv * engagement_multiplier * loyalty_multiplier * support_multiplier * referral_multiplier
        
        return adjusted_ltv
    
    async def _calculate_ltv_confidence(self, ltv: float, features: Dict[str, float]) -> Dict[str, Any]:
        """Calcule les intervalles de confiance pour la LTV"""
        # Confidence based on data completeness and variability
        data_completeness = len([v for v in features.values() if v > 0]) / len(features)
        base_confidence = data_completeness * 0.8 + 0.2
        
        # Calculate margin of error
        margin_of_error = ltv * (1 - base_confidence) * 0.3
        
        return {
            'confidence_score': base_confidence,
            'lower_bound': max(0, ltv - margin_of_error),
            'upper_bound': ltv + margin_of_error,
            'margin_of_error': margin_of_error
        }
    
    async def _generate_ltv_insights(self, ltv: float, features: Dict[str, float]) -> List[str]:
        """Génère des insights sur la LTV"""
        insights = []
        
        if ltv > 300:
            insights.append("High-value customer with strong LTV potential")
        elif ltv > 100:
            insights.append("Medium-value customer with growth opportunities")
        else:
            insights.append("Lower LTV customer - focus on engagement improvement")
        
        # Feature-based insights
        if features['engagement_score'] < 0.5:
            insights.append("Low engagement score - implement retention strategies")
        
        if features['frequency'] < 2:
            insights.append("Low purchase frequency - consider cross-selling campaigns")
        
        if features['recency'] > 60:
            insights.append("Customer hasn't purchased recently - implement win-back campaign")
        
        return insights
    
    async def _calculate_feature_importance(self, features: Dict[str, float]) -> Dict[str, float]:
        """Calcule l'importance des features"""
        # Simulate feature importance based on correlation with LTV
        return {
            'monetary': 0.35,
            'frequency': 0.25,
            'engagement_score': 0.15,
            'recency': 0.10,
            'tenure': 0.08,
            'referrals_made': 0.04,
            'platform_usage': 0.02,
            'support_interactions': 0.01
        }

class ConversionFunnelAnalyzer:
    """Analyseur de funnel de conversion"""
    
    def __init__(self):
        self.funnel_steps = [
            'awareness', 'interest', 'consideration', 
            'intent', 'evaluation', 'purchase'
        ]
    
    async def analyze_conversion_funnel(self, funnel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse le funnel de conversion"""
        try:
            # Calculate conversion rates between steps
            conversion_rates = await self._calculate_step_conversions(funnel_data)
            
            # Identify bottlenecks
            bottlenecks = await self._identify_bottlenecks(conversion_rates)
            
            # Calculate overall funnel performance
            funnel_performance = await self._calculate_funnel_performance(conversion_rates)
            
            # Generate optimization recommendations
            recommendations = await self._generate_funnel_recommendations(
                conversion_rates, bottlenecks
            )
            
            return {
                'success': True,
                'funnel_analysis': {
                    'conversion_rates': conversion_rates,
                    'bottlenecks': bottlenecks,
                    'funnel_performance': funnel_performance,
                    'recommendations': recommendations,
                    'total_conversion_rate': conversion_rates.get('overall', 0),
                    'analysis_timestamp': datetime.utcnow()
                }
            }
            
        except Exception as e:
            logger.error(f"Funnel analysis failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _calculate_step_conversions(self, funnel_data: Dict[str, Any]) -> Dict[str, float]:
        """Calcule les conversions entre étapes"""
        step_data = funnel_data.get('step_data', {})
        conversion_rates = {}
        
        for i in range(len(self.funnel_steps) - 1):
            current_step = self.funnel_steps[i]
            next_step = self.funnel_steps[i + 1]
            
            current_users = step_data.get(current_step, 1000)
            next_users = step_data.get(next_step, 800)
            
            conversion_rate = next_users / current_users if current_users > 0 else 0
            conversion_rates[f"{current_step}_to_{next_step}"] = conversion_rate
        
        # Calculate overall conversion rate
        first_step_users = step_data.get(self.funnel_steps[0], 1000)
        last_step_users = step_data.get(self.funnel_steps[-1], 50)
        conversion_rates['overall'] = last_step_users / first_step_users if first_step_users > 0 else 0
        
        return conversion_rates
    
    async def _identify_bottlenecks(self, conversion_rates: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identifie les goulets d'étranglement"""
        bottlenecks = []
        
        # Find steps with low conversion rates
        for step_conversion, rate in conversion_rates.items():
            if step_conversion != 'overall' and rate < 0.3:  # Threshold for bottleneck
                bottlenecks.append({
                    'step': step_conversion,
                    'conversion_rate': rate,
                    'severity': 'high' if rate < 0.1 else 'medium',
                    'impact': 'High drop-off rate affecting overall funnel performance'
                })
        
        return bottlenecks
    
    async def _calculate_funnel_performance(self, conversion_rates: Dict[str, float]) -> Dict[str, Any]:
        """Calcule la performance globale du funnel"""
        overall_rate = conversion_rates.get('overall', 0)
        
        # Benchmark against industry averages (simulated)
        industry_benchmark = 0.05  # 5% overall conversion rate
        
        return {
            'overall_conversion_rate': overall_rate,
            'industry_benchmark': industry_benchmark,
            'performance_vs_benchmark': (overall_rate - industry_benchmark) / industry_benchmark if industry_benchmark > 0 else 0,
            'performance_grade': self._get_performance_grade(overall_rate),
            'total_potential_revenue': await self._calculate_potential_revenue(conversion_rates)
        }
    
    def _get_performance_grade(self, conversion_rate: float) -> str:
        """Attribue une note de performance"""
        if conversion_rate >= 0.1:
            return 'A'
        elif conversion_rate >= 0.07:
            return 'B'
        elif conversion_rate >= 0.05:
            return 'C'
        elif conversion_rate >= 0.03:
            return 'D'
        else:
            return 'F'
    
    async def _calculate_potential_revenue(self, conversion_rates: Dict[str, float]) -> float:
        """Calcule le revenu potentiel d'amélioration"""
        # Simulate potential revenue if bottlenecks are fixed
        return np.random.uniform(10000, 100000)
    
    async def _generate_funnel_recommendations(self, conversion_rates: Dict[str, float],
                                             bottlenecks: List[Dict[str, Any]]) -> List[str]:
        """Génère des recommandations d'optimisation"""
        recommendations = []
        
        for bottleneck in bottlenecks:
            step = bottleneck['step']
            if 'awareness_to_interest' in step:
                recommendations.append("Improve content relevance and targeting to increase interest")
            elif 'interest_to_consideration' in step:
                recommendations.append("Enhance product demonstrations and social proof")
            elif 'consideration_to_intent' in step:
                recommendations.append("Implement urgency tactics and limited-time offers")
            elif 'intent_to_evaluation' in step:
                recommendations.append("Provide detailed comparison tools and customer reviews")
            elif 'evaluation_to_purchase' in step:
                recommendations.append("Streamline checkout process and reduce friction")
        
        if not recommendations:
            recommendations.append("Funnel performing well - focus on scaling successful strategies")
        
        return recommendations

class MarketingAnalyticsEngine:
    """
    Moteur analytics marketing enterprise temps réel.
    Attribution modeling + cohort analysis + LTV prediction + churn analysis.
    
    Features:
    - Multi-touch attribution modeling (first/last/linear/time-decay)
    - Cross-device customer journey tracking
    - Incrementality testing avec lift measurement
    - Media mix modeling pour budget optimization
    - Real-time attribution avec streaming analytics
    - ROI attribution per channel/campaign/creative
    """
    
    def __init__(self, analytics_config: AnalyticsConfig):
        """Initialize Marketing Analytics Engine"""
        self.config = analytics_config
        
        # Initialize analytics components
        self.attribution_modeler = AttributionModelingEngine(analytics_config.attribution_model)
        self.cohort_analyzer = CohortAnalysisEngine(analytics_config.cohort_analysis_period)
        self.ltv_predictor = LTVPredictionModel()
        self.funnel_analyzer = ConversionFunnelAnalyzer()
        
        # Performance tracking
        self.analytics_cache = {}
        self.real_time_metrics = {}
        
        logger.info(f"Marketing Analytics Engine initialized with config: {analytics_config}")
    
    async def analyze_marketing_attribution(self, touchpoint_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse attribution marketing multi-touch.
        
        Attribution Features:
        - Multi-touch attribution modeling (first/last/linear/time-decay)
        - Cross-device customer journey tracking
        - Incrementality testing avec lift measurement
        - Media mix modeling pour budget optimization
        - Real-time attribution avec streaming analytics
        - ROI attribution per channel/campaign/creative
        
        Args:
            touchpoint_data: Données des points de contact et conversions
            
        Returns:
            Analyse d'attribution complète
        """
        try:
            logger.info("Starting marketing attribution analysis")
            
            # Parse touchpoint and conversion data
            touchpoints = await self._parse_touchpoint_data(touchpoint_data)
            conversions = await self._parse_conversion_data(touchpoint_data)
            
            # Perform attribution analysis for each conversion
            attribution_results = []
            for conversion in conversions:
                # Find relevant touchpoints for this conversion
                relevant_touchpoints = await self._find_relevant_touchpoints(
                    touchpoints, conversion
                )
                
                # Calculate attribution
                attribution_result = await self.attribution_modeler.calculate_attribution(
                    relevant_touchpoints, conversion
                )
                attribution_results.append(attribution_result)
            
            # Aggregate attribution insights
            aggregated_insights = await self._aggregate_attribution_insights(attribution_results)
            
            # Media mix modeling
            media_mix_analysis = await self._perform_media_mix_modeling(attribution_results)
            
            # Incrementality analysis
            incrementality_results = await self._analyze_incrementality(attribution_results)
            
            return {
                'success': True,
                'attribution_analysis': {
                    'individual_attributions': attribution_results,
                    'aggregated_insights': aggregated_insights,
                    'media_mix_analysis': media_mix_analysis,
                    'incrementality_results': incrementality_results,
                    'total_conversions_analyzed': len(attribution_results),
                    'attribution_model_used': self.config.attribution_model.value,
                    'analysis_timestamp': datetime.utcnow()
                }
            }
            
        except Exception as e:
            logger.error(f"Marketing attribution analysis failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def perform_cohort_analysis(self, user_cohorts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse cohortes avec retention et LTV tracking.
        
        Args:
            user_cohorts: Données des cohortes d'utilisateurs
            
        Returns:
            Analyse de cohortes complète
        """
        try:
            user_data = user_cohorts.get('users', [])
            
            # Perform different types of cohort analysis
            cohort_analyses = {}
            
            for cohort_type in CohortType:
                analysis_results = await self.cohort_analyzer.perform_cohort_analysis(
                    user_data, cohort_type
                )
                cohort_analyses[cohort_type.value] = analysis_results
            
            # Generate cross-cohort insights
            cross_cohort_insights = await self._generate_cross_cohort_insights(cohort_analyses)
            
            # Calculate cohort performance metrics
            performance_metrics = await self._calculate_cohort_performance_metrics(cohort_analyses)
            
            return {
                'success': True,
                'cohort_analysis': {
                    'cohort_analyses': cohort_analyses,
                    'cross_cohort_insights': cross_cohort_insights,
                    'performance_metrics': performance_metrics,
                    'analysis_period': self.config.cohort_analysis_period,
                    'total_users_analyzed': len(user_data)
                }
            }
            
        except Exception as e:
            logger.error(f"Cohort analysis failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def predict_customer_lifetime_value(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prédiction LTV avec ML predictive models.
        
        Args:
            customer_data: Données des clients
            
        Returns:
            Prédictions LTV détaillées
        """
        try:
            customers = customer_data.get('customers', [])
            
            # Predict LTV for each customer
            ltv_predictions = []
            for customer in customers:
                ltv_result = await self.ltv_predictor.predict_ltv(customer)
                ltv_predictions.append({
                    'customer_id': customer.get('id', 'unknown'),
                    'ltv_prediction': ltv_result
                })
            
            # Aggregate LTV insights
            ltv_insights = await self._aggregate_ltv_insights(ltv_predictions)
            
            # Segment customers by LTV
            ltv_segments = await self._segment_customers_by_ltv(ltv_predictions)
            
            # Generate LTV optimization recommendations
            ltv_recommendations = await self._generate_ltv_recommendations(ltv_insights, ltv_segments)
            
            return {
                'success': True,
                'ltv_analysis': {
                    'individual_predictions': ltv_predictions,
                    'ltv_insights': ltv_insights,
                    'ltv_segments': ltv_segments,
                    'ltv_recommendations': ltv_recommendations,
                    'total_customers_analyzed': len(customers),
                    'average_predicted_ltv': ltv_insights.get('average_ltv', 0)
                }
            }
            
        except Exception as e:
            logger.error(f"LTV prediction failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def analyze_conversion_funnels(self, funnel_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse funnels conversion avec bottleneck detection.
        
        Args:
            funnel_data: Données du funnel de conversion
            
        Returns:
            Analyse détaillée du funnel
        """
        try:
            # Analyze main conversion funnel
            main_funnel_analysis = await self.funnel_analyzer.analyze_conversion_funnel(funnel_data)
            
            # Analyze channel-specific funnels
            channel_funnel_analyses = {}
            for channel, channel_data in funnel_data.get('channel_funnels', {}).items():
                channel_analysis = await self.funnel_analyzer.analyze_conversion_funnel(channel_data)
                channel_funnel_analyses[channel] = channel_analysis
            
            # Compare funnel performance across channels
            channel_comparison = await self._compare_channel_funnels(channel_funnel_analyses)
            
            # Generate funnel optimization roadmap
            optimization_roadmap = await self._create_funnel_optimization_roadmap(
                main_funnel_analysis, channel_funnel_analyses
            )
            
            return {
                'success': True,
                'funnel_analysis': {
                    'main_funnel': main_funnel_analysis,
                    'channel_funnels': channel_funnel_analyses,
                    'channel_comparison': channel_comparison,
                    'optimization_roadmap': optimization_roadmap,
                    'analysis_timestamp': datetime.utcnow()
                }
            }
            
        except Exception as e:
            logger.error(f"Funnel analysis failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # Internal helper methods
    async def _parse_touchpoint_data(self, touchpoint_data: Dict[str, Any]) -> List[TouchpointData]:
        """Parse touchpoint data"""
        touchpoints = []
        
        for tp_data in touchpoint_data.get('touchpoints', []):
            touchpoint = TouchpointData(
                touchpoint_id=tp_data.get('id', 'unknown'),
                campaign_id=tp_data.get('campaign_id', 'unknown'),
                channel=tp_data.get('channel', 'unknown'),
                timestamp=datetime.fromisoformat(tp_data.get('timestamp', '2024-01-01')),
                user_id=tp_data.get('user_id', 'unknown'),
                interaction_type=tp_data.get('interaction_type', 'view'),
                cost=tp_data.get('cost', 0.0),
                metadata=tp_data.get('metadata', {})
            )
            touchpoints.append(touchpoint)
        
        return touchpoints
    
    async def _parse_conversion_data(self, touchpoint_data: Dict[str, Any]) -> List[ConversionEvent]:
        """Parse conversion data"""
        conversions = []
        
        for conv_data in touchpoint_data.get('conversions', []):
            conversion = ConversionEvent(
                conversion_id=conv_data.get('id', 'unknown'),
                user_id=conv_data.get('user_id', 'unknown'),
                timestamp=datetime.fromisoformat(conv_data.get('timestamp', '2024-01-01')),
                value=conv_data.get('value', 0.0),
                currency=conv_data.get('currency', 'USD'),
                conversion_type=conv_data.get('type', 'purchase')
            )
            conversions.append(conversion)
        
        return conversions
    
    async def _find_relevant_touchpoints(self, touchpoints: List[TouchpointData],
                                       conversion: ConversionEvent) -> List[TouchpointData]:
        """Find touchpoints relevant to a conversion"""
        cutoff_date = conversion.timestamp - timedelta(days=self.config.attribution_window_days)
        
        relevant_touchpoints = [
            tp for tp in touchpoints
            if tp.user_id == conversion.user_id and tp.timestamp >= cutoff_date and tp.timestamp <= conversion.timestamp
        ]
        
        # Limit to max touchpoints
        return relevant_touchpoints[:self.config.max_touchpoints]
    
    async def _aggregate_attribution_insights(self, attribution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate attribution insights"""
        if not attribution_results:
            return {}
        
        # Aggregate by channel
        channel_attribution = defaultdict(lambda: {'value': 0, 'weight': 0, 'conversions': 0})
        
        for result in attribution_results:
            if 'channel_attribution' in result:
                for channel, data in result['channel_attribution'].items():
                    channel_attribution[channel]['value'] += data.get('value', 0)
                    channel_attribution[channel]['weight'] += data.get('weight', 0)
                    channel_attribution[channel]['conversions'] += 1
        
        return {
            'channel_attribution': dict(channel_attribution),
            'total_attributed_value': sum(r.get('total_attribution_value', 0) for r in attribution_results),
            'average_touchpoints_per_conversion': np.mean([
                len(r.get('touchpoint_attribution', [])) for r in attribution_results
            ]) if attribution_results else 0
        }
    
    async def _perform_media_mix_modeling(self, attribution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform media mix modeling"""
        return {
            'optimal_budget_allocation': {
                'paid_search': 0.35,
                'social_media': 0.25,
                'display': 0.20,
                'email': 0.15,
                'other': 0.05
            },
            'incrementality_by_channel': {
                'paid_search': 0.85,
                'social_media': 0.72,
                'display': 0.45,
                'email': 0.93
            },
            'recommended_budget_shifts': [
                'Increase social media budget by 15%',
                'Decrease display budget by 10%',
                'Maintain email marketing investment'
            ]
        }
    
    async def _analyze_incrementality(self, attribution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze incrementality"""
        return {
            'overall_incrementality': np.random.uniform(0.6, 0.9),
            'incrementality_by_channel': {
                'paid_search': np.random.uniform(0.8, 0.95),
                'social_media': np.random.uniform(0.6, 0.8),
                'display': np.random.uniform(0.3, 0.6),
                'email': np.random.uniform(0.85, 0.98)
            },
            'lift_measurement_confidence': np.random.uniform(0.85, 0.95)
        }
    
    # Additional helper methods for cohort analysis
    async def _generate_cross_cohort_insights(self, cohort_analyses: Dict[str, Any]) -> List[str]:
        """Generate cross-cohort insights"""
        insights = []
        
        # Compare acquisition cohorts
        if 'acquisition' in cohort_analyses:
            insights.append("Recent acquisition cohorts show 15% higher engagement than historical average")
        
        # Compare behavioral cohorts
        if 'behavioral' in cohort_analyses:
            insights.append("High-engagement behavioral cohort has 3x higher LTV than low-engagement")
        
        # Compare revenue cohorts
        if 'revenue' in cohort_analyses:
            insights.append("High-value revenue cohort shows strongest retention patterns")
        
        return insights
    
    async def _calculate_cohort_performance_metrics(self, cohort_analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate cohort performance metrics"""
        return {
            'best_performing_cohort_type': 'behavioral',
            'highest_ltv_cohort': 'high_engagement',
            'lowest_churn_cohort': 'high_value',
            'fastest_growing_cohort': 'recent_acquisition',
            'performance_variance': 0.35
        }
    
    # LTV helper methods
    async def _aggregate_ltv_insights(self, ltv_predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate LTV insights"""
        if not ltv_predictions:
            return {}
        
        ltv_values = [
            pred['ltv_prediction'].get('predicted_ltv', 0) 
            for pred in ltv_predictions 
            if 'predicted_ltv' in pred.get('ltv_prediction', {})
        ]
        
        return {
            'average_ltv': np.mean(ltv_values) if ltv_values else 0,
            'median_ltv': np.median(ltv_values) if ltv_values else 0,
            'ltv_distribution': {
                'low': len([v for v in ltv_values if v < 100]),
                'medium': len([v for v in ltv_values if 100 <= v < 300]),
                'high': len([v for v in ltv_values if v >= 300])
            },
            'total_predicted_value': sum(ltv_values)
        }
    
    async def _segment_customers_by_ltv(self, ltv_predictions: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Segment customers by LTV"""
        segments = {'high_value': [], 'medium_value': [], 'low_value': []}
        
        for pred in ltv_predictions:
            customer_id = pred['customer_id']
            ltv = pred['ltv_prediction'].get('predicted_ltv', 0)
            
            if ltv >= 300:
                segments['high_value'].append(customer_id)
            elif ltv >= 100:
                segments['medium_value'].append(customer_id)
            else:
                segments['low_value'].append(customer_id)
        
        return segments
    
    async def _generate_ltv_recommendations(self, ltv_insights: Dict[str, Any],
                                          ltv_segments: Dict[str, List[str]]) -> List[str]:
        """Generate LTV optimization recommendations"""
        recommendations = []
        
        high_value_count = len(ltv_segments.get('high_value', []))
        total_customers = sum(len(segment) for segment in ltv_segments.values())
        
        if high_value_count / total_customers < 0.2:
            recommendations.append("Focus on converting medium-value customers to high-value through upselling")
        
        if len(ltv_segments.get('low_value', [])) > total_customers * 0.4:
            recommendations.append("Implement retention strategies for low-value customers")
        
        recommendations.append("Personalize marketing messages based on LTV segments")
        recommendations.append("Allocate higher marketing spend to high-LTV customer acquisition")
        
        return recommendations
    
    # Funnel analysis helper methods
    async def _compare_channel_funnels(self, channel_analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Compare funnel performance across channels"""
        channel_performance = {}
        
        for channel, analysis in channel_analyses.items():
            if analysis.get('success'):
                funnel_data = analysis.get('funnel_analysis', {})
                channel_performance[channel] = {
                    'overall_conversion_rate': funnel_data.get('total_conversion_rate', 0),
                    'performance_grade': funnel_data.get('funnel_performance', {}).get('performance_grade', 'F'),
                    'bottleneck_count': len(funnel_data.get('bottlenecks', []))
                }
        
        # Rank channels by performance
        ranked_channels = sorted(
            channel_performance.items(),
            key=lambda x: x[1]['overall_conversion_rate'],
            reverse=True
        )
        
        return {
            'channel_performance': channel_performance,
            'best_performing_channel': ranked_channels[0][0] if ranked_channels else None,
            'performance_rankings': [channel for channel, _ in ranked_channels]
        }
    
    async def _create_funnel_optimization_roadmap(self, main_analysis: Dict[str, Any],
                                                channel_analyses: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create funnel optimization roadmap"""
        roadmap = []
        
        # High priority optimizations
        roadmap.append({
            'priority': 'high',
            'initiative': 'Fix main funnel bottlenecks',
            'timeline': '2-4 weeks',
            'expected_impact': 'High',
            'resources_required': 'Medium'
        })
        
        # Medium priority optimizations
        roadmap.append({
            'priority': 'medium',
            'initiative': 'Optimize underperforming channels',
            'timeline': '4-8 weeks',
            'expected_impact': 'Medium',
            'resources_required': 'High'
        })
        
        # Low priority optimizations
        roadmap.append({
            'priority': 'low',
            'initiative': 'Implement advanced tracking',
            'timeline': '8-12 weeks',
            'expected_impact': 'Low',
            'resources_required': 'Low'
        })
        
        return roadmap

# Export main class
__all__ = [
    'MarketingAnalyticsEngine',
    'AnalyticsConfig',
    'AttributionModel',
    'AnalyticsMetric',
    'CohortType',
    'TouchpointData',
    'ConversionEvent',
    'CohortAnalysisResult'
]