"""
Performance Intelligence Engine - Intelligence IA pour optimisation de performance
Auteur: Fahed Mlaiel (mlaiel@live.de)
Version: 1.0 Production

Moteur d'IA pour prédiction et optimisation des performances de distribution.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
from datetime import datetime, timedelta
import statistics
from collections import defaultdict, deque
import time

class PerformanceMetric(Enum):
    """Métriques de performance trackées."""
    ENGAGEMENT_RATE = "engagement_rate"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    CTR = "click_through_rate"
    CONVERSION_RATE = "conversion_rate"
    ROI = "return_on_investment"
    COST_PER_ENGAGEMENT = "cost_per_engagement"
    LIFETIME_VALUE = "lifetime_value"

@dataclass
class PerformancePrediction:
    """Prédiction de performance complète."""
    content_id: str
    predicted_metrics: Dict[str, float]
    confidence_scores: Dict[str, float]
    performance_benchmarks: Dict[str, float]
    optimization_opportunities: List[str]
    risk_factors: List[str]
    expected_timeline: Dict[str, Any]
    roi_forecast: Dict[str, float]

class ROIOptimizer:
    """Optimiseur ROI pour distribution multi-plateforme."""
    
    def __init__(self):
        self.roi_models = {}
        self.cost_structures = {}
        self.performance_baselines = {}
        self.optimization_strategies = {}
        self.logger = logging.getLogger("ROIOptimizer")
        
        self._initialize_roi_models()
    
    def _initialize_roi_models(self):
        """Initialise les modèles ROI par plateforme."""
        self.roi_models = {
            'instagram': {
                'avg_cpe': 0.02,  # Cost per engagement
                'avg_cpm': 8.50,  # Cost per mille
                'avg_conversion_rate': 0.024,
                'avg_customer_value': 45.0,
                'engagement_to_revenue_ratio': 0.018
            },
            'tiktok': {
                'avg_cpe': 0.015,
                'avg_cpm': 6.20,
                'avg_conversion_rate': 0.019,
                'avg_customer_value': 32.0,
                'engagement_to_revenue_ratio': 0.014
            },
            'youtube': {
                'avg_cpe': 0.035,
                'avg_cpm': 12.30,
                'avg_conversion_rate': 0.031,
                'avg_customer_value': 78.0,
                'engagement_to_revenue_ratio': 0.025
            },
            'facebook': {
                'avg_cpe': 0.025,
                'avg_cpm': 9.80,
                'avg_conversion_rate': 0.027,
                'avg_customer_value': 52.0,
                'engagement_to_revenue_ratio': 0.021
            },
            'linkedin': {
                'avg_cpe': 0.045,
                'avg_cpm': 18.50,
                'avg_conversion_rate': 0.048,
                'avg_customer_value': 185.0,
                'engagement_to_revenue_ratio': 0.042
            },
            'spotify': {
                'avg_cpe': 0.008,
                'avg_cpm': 4.20,
                'avg_conversion_rate': 0.012,
                'avg_customer_value': 25.0,
                'engagement_to_revenue_ratio': 0.008
            },
            'patreon': {
                'avg_cpe': 0.12,
                'avg_cpm': 35.0,
                'avg_conversion_rate': 0.085,
                'avg_customer_value': 280.0,
                'engagement_to_revenue_ratio': 0.125
            }
        }
        
        self.logger.info(f"Initialized ROI models for {len(self.roi_models)} platforms")
    
    async def calculate_roi_forecast(self, platform: str, content_data: Dict[str, Any],
                                   budget: float, campaign_duration_days: int) -> Dict[str, Any]:
        """Calcule la prévision ROI pour une plateforme."""
        try:
            if platform not in self.roi_models:
                return {'error': f'Platform {platform} not supported'}
            
            model = self.roi_models[platform]
            
            # Prédictions de base
            predicted_reach = await self._predict_reach(content_data, budget, model)
            predicted_engagement = await self._predict_engagement(predicted_reach, content_data, model)
            predicted_conversions = await self._predict_conversions(predicted_engagement, model)
            predicted_revenue = await self._predict_revenue(predicted_conversions, model)
            
            # Calcul ROI
            roi = (predicted_revenue - budget) / budget if budget > 0 else 0
            
            # Métriques détaillées
            cost_per_engagement = budget / predicted_engagement if predicted_engagement > 0 else 0
            cost_per_conversion = budget / predicted_conversions if predicted_conversions > 0 else 0
            
            # Timeline de performance
            timeline = await self._generate_performance_timeline(
                campaign_duration_days, predicted_reach, predicted_engagement, predicted_revenue
            )
            
            return {
                'platform': platform,
                'investment': budget,
                'predicted_metrics': {
                    'reach': predicted_reach,
                    'engagement': predicted_engagement,
                    'conversions': predicted_conversions,
                    'revenue': predicted_revenue
                },
                'roi_metrics': {
                    'roi_percentage': roi * 100,
                    'cost_per_engagement': cost_per_engagement,
                    'cost_per_conversion': cost_per_conversion,
                    'revenue_per_engagement': predicted_revenue / predicted_engagement if predicted_engagement > 0 else 0
                },
                'performance_timeline': timeline,
                'break_even_point_days': await self._calculate_break_even_point(budget, predicted_revenue, campaign_duration_days)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating ROI forecast: {str(e)}")
            return {'error': str(e)}
    
    async def _predict_reach(self, content_data: Dict[str, Any], budget: float, model: Dict[str, Any]) -> int:
        """Prédit la portée basée sur le budget et la qualité du contenu."""
        # Portée organique de base
        organic_reach = content_data.get('predicted_organic_reach', 1000)
        
        # Portée payante basée sur le budget
        cpm = model['avg_cpm']
        paid_impressions = (budget / cpm) * 1000
        
        # Facteur de qualité du contenu
        content_quality = content_data.get('content_quality_score', 0.7)
        quality_multiplier = 0.5 + content_quality
        
        # Facteur de ciblage
        targeting_precision = content_data.get('targeting_precision', 0.7)
        targeting_multiplier = 0.7 + (targeting_precision * 0.6)
        
        # Portée totale prédite
        total_reach = int((organic_reach + paid_impressions) * quality_multiplier * targeting_multiplier)
        
        return max(total_reach, organic_reach)  # Minimum = portée organique
    
    async def _predict_engagement(self, predicted_reach: int, content_data: Dict[str, Any], 
                                model: Dict[str, Any]) -> int:
        """Prédit l'engagement basé sur la portée et la qualité du contenu."""
        # Taux d'engagement de base pour la plateforme
        base_engagement_rate = model.get('avg_engagement_rate', 0.03)
        
        # Ajustements basés sur le contenu
        content_quality = content_data.get('content_quality_score', 0.7)
        engagement_rate = base_engagement_rate * (0.5 + content_quality)
        
        # Facteurs d'engagement spécifiques
        has_call_to_action = content_data.get('has_call_to_action', False)
        if has_call_to_action:
            engagement_rate *= 1.2
        
        emotional_intensity = abs(content_data.get('sentiment_score', 0))
        engagement_rate *= (1 + emotional_intensity * 0.3)
        
        # Engagement total prédit
        predicted_engagement = int(predicted_reach * engagement_rate)
        
        return predicted_engagement
    
    async def _predict_conversions(self, predicted_engagement: int, model: Dict[str, Any]) -> int:
        """Prédit les conversions basées sur l'engagement."""
        conversion_rate = model['avg_conversion_rate']
        predicted_conversions = int(predicted_engagement * conversion_rate)
        
        return predicted_conversions
    
    async def _predict_revenue(self, predicted_conversions: int, model: Dict[str, Any]) -> float:
        """Prédit les revenus basés sur les conversions."""
        avg_customer_value = model['avg_customer_value']
        predicted_revenue = predicted_conversions * avg_customer_value
        
        return predicted_revenue
    
    async def _generate_performance_timeline(self, duration_days: int, total_reach: int,
                                           total_engagement: int, total_revenue: float) -> Dict[str, List]:
        """Génère une timeline de performance sur la durée de la campagne."""
        timeline = {
            'days': list(range(1, duration_days + 1)),
            'cumulative_reach': [],
            'cumulative_engagement': [],
            'cumulative_revenue': []
        }
        
        # Distribution logarithmique pour simuler l'adoption réelle
        for day in range(1, duration_days + 1):
            # Facteur de progression (courbe logarithmique)
            progress_factor = np.log(day + 1) / np.log(duration_days + 1)
            
            # Métriques cumulatives
            cumul_reach = int(total_reach * progress_factor)
            cumul_engagement = int(total_engagement * progress_factor)
            cumul_revenue = total_revenue * progress_factor
            
            timeline['cumulative_reach'].append(cumul_reach)
            timeline['cumulative_engagement'].append(cumul_engagement)
            timeline['cumulative_revenue'].append(round(cumul_revenue, 2))
        
        return timeline
    
    async def _calculate_break_even_point(self, budget: float, total_revenue: float, 
                                        duration_days: int) -> Optional[int]:
        """Calcule le point d'équilibre en jours."""
        if total_revenue <= budget:
            return None  # Pas de break-even dans la période
        
        # Estimation du jour de break-even (simplifiée)
        break_even_ratio = budget / total_revenue
        break_even_day = int(duration_days * break_even_ratio)
        
        return max(1, break_even_day)
    
    async def optimize_budget_allocation(self, total_budget: float, 
                                       platforms: List[str],
                                       content_data: Dict[str, Any],
                                       campaign_duration: int) -> Dict[str, Any]:
        """Optimise l'allocation de budget entre plateformes."""
        try:
            platform_forecasts = {}
            
            # Calcul des prévisions pour chaque plateforme avec budget égal
            equal_budget = total_budget / len(platforms)
            
            for platform in platforms:
                forecast = await self.calculate_roi_forecast(
                    platform, content_data, equal_budget, campaign_duration
                )
                if 'error' not in forecast:
                    platform_forecasts[platform] = forecast
            
            if not platform_forecasts:
                return {'error': 'No valid platform forecasts'}
            
            # Calcul des scores de performance relatifs
            performance_scores = {}
            for platform, forecast in platform_forecasts.items():
                roi = forecast['roi_metrics']['roi_percentage']
                engagement_efficiency = forecast['predicted_metrics']['engagement'] / equal_budget
                
                # Score composite (ROI + efficacité engagement)
                performance_scores[platform] = roi * 0.7 + engagement_efficiency * 0.3
            
            # Normalisation des scores
            total_score = sum(performance_scores.values())
            if total_score > 0:
                normalized_scores = {p: score/total_score for p, score in performance_scores.items()}
            else:
                normalized_scores = {p: 1/len(platforms) for p in platforms}
            
            # Allocation optimisée du budget
            optimized_allocation = {}
            total_optimized_roi = 0
            
            for platform, weight in normalized_scores.items():
                allocated_budget = total_budget * weight
                optimized_allocation[platform] = {
                    'allocated_budget': round(allocated_budget, 2),
                    'weight': round(weight, 3),
                    'performance_score': round(performance_scores[platform], 3)
                }
                
                # Recalcul du ROI avec budget optimisé
                optimized_forecast = await self.calculate_roi_forecast(
                    platform, content_data, allocated_budget, campaign_duration
                )
                
                if 'error' not in optimized_forecast:
                    optimized_allocation[platform]['optimized_roi'] = optimized_forecast['roi_metrics']['roi_percentage']
                    total_optimized_roi += optimized_forecast['predicted_metrics']['revenue']
            
            # Comparaison avec allocation égale
            equal_allocation_roi = sum(f['predicted_metrics']['revenue'] for f in platform_forecasts.values())
            improvement = ((total_optimized_roi - equal_allocation_roi) / equal_allocation_roi * 100 
                          if equal_allocation_roi > 0 else 0)
            
            return {
                'total_budget': total_budget,
                'optimized_allocation': optimized_allocation,
                'optimization_summary': {
                    'total_optimized_revenue': round(total_optimized_roi, 2),
                    'equal_allocation_revenue': round(equal_allocation_roi, 2),
                    'improvement_percentage': round(improvement, 2),
                    'recommended_strategy': await self._recommend_allocation_strategy(optimized_allocation)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing budget allocation: {str(e)}")
            return {'error': str(e)}
    
    async def _recommend_allocation_strategy(self, allocation: Dict[str, Any]) -> str:
        """Recommande une stratégie d'allocation basée sur les résultats."""
        sorted_platforms = sorted(allocation.items(), 
                                key=lambda x: x[1].get('optimized_roi', 0), 
                                reverse=True)
        
        if not sorted_platforms:
            return "Redistribuer le budget équitablement"
        
        best_platform = sorted_platforms[0][0]
        best_roi = sorted_platforms[0][1].get('optimized_roi', 0)
        
        if best_roi > 200:  # ROI > 200%
            return f"Concentrer majoritairement sur {best_platform} (performance exceptionnelle)"
        elif len([p for p, data in sorted_platforms if data.get('optimized_roi', 0) > 50]) >= 3:
            return "Diversifier sur les 3 meilleures plateformes"
        elif best_roi > 50:
            return f"Prioriser {best_platform} avec support sur autres plateformes"
        else:
            return "Optimiser le contenu avant d'allouer le budget"

class PerformanceIntelligenceEngine:
    """Moteur d'intelligence de performance pour optimisation globale."""
    
    def __init__(self):
        self.roi_optimizer = ROIOptimizer()
        self.performance_history = defaultdict(deque)
        self.benchmarks = {}
        self.predictive_models = {}
        self.optimization_strategies = {}
        self.logger = logging.getLogger("PerformanceIntelligenceEngine")
        
        self._initialize_benchmarks()
        self._initialize_predictive_models()
    
    def _initialize_benchmarks(self):
        """Initialise les benchmarks de performance par industrie et plateforme."""
        self.benchmarks = {
            'entertainment': {
                'engagement_rate': {'instagram': 0.045, 'tiktok': 0.062, 'youtube': 0.038},
                'click_through_rate': {'instagram': 0.015, 'tiktok': 0.012, 'youtube': 0.028},
                'conversion_rate': {'instagram': 0.024, 'tiktok': 0.019, 'youtube': 0.031}
            },
            'technology': {
                'engagement_rate': {'instagram': 0.032, 'tiktok': 0.048, 'youtube': 0.042},
                'click_through_rate': {'instagram': 0.022, 'tiktok': 0.018, 'youtube': 0.035},
                'conversion_rate': {'instagram': 0.031, 'tiktok': 0.025, 'youtube': 0.042}
            },
            'music': {
                'engagement_rate': {'spotify': 0.085, 'youtube': 0.052, 'instagram': 0.038},
                'click_through_rate': {'spotify': 0.045, 'youtube': 0.032, 'instagram': 0.018},
                'conversion_rate': {'spotify': 0.015, 'youtube': 0.025, 'instagram': 0.012}
            },
            'education': {
                'engagement_rate': {'linkedin': 0.048, 'youtube': 0.055, 'instagram': 0.025},
                'click_through_rate': {'linkedin': 0.032, 'youtube': 0.038, 'instagram': 0.015},
                'conversion_rate': {'linkedin': 0.052, 'youtube': 0.048, 'instagram': 0.018}
            }
        }
        
        self.logger.info(f"Initialized benchmarks for {len(self.benchmarks)} industries")
    
    def _initialize_predictive_models(self):
        """Initialise les modèles prédictifs de performance."""
        self.predictive_models = {
            'engagement_predictor': {
                'features': ['content_quality', 'timing_score', 'audience_match', 'trend_alignment'],
                'weights': [0.35, 0.25, 0.25, 0.15],
                'base_rates': {'instagram': 0.03, 'tiktok': 0.055, 'youtube': 0.025}
            },
            'reach_predictor': {
                'features': ['follower_count', 'content_quality', 'hashtag_optimization', 'algorithm_factors'],
                'weights': [0.4, 0.3, 0.15, 0.15],
                'amplification_factors': {'high_quality': 2.5, 'trending': 3.0, 'algorithm_boost': 4.0}
            },
            'conversion_predictor': {
                'features': ['call_to_action', 'landing_page_quality', 'audience_intent', 'offer_strength'],
                'weights': [0.25, 0.3, 0.25, 0.2],
                'platform_modifiers': {'linkedin': 1.5, 'youtube': 1.2, 'instagram': 0.8}
            }
        }
        
        self.logger.info(f"Initialized {len(self.predictive_models)} predictive models")
    
    async def predict_performance(self, content_id: str, content_data: Dict[str, Any],
                                target_platforms: List[str],
                                campaign_config: Optional[Dict[str, Any]] = None) -> PerformancePrediction:
        """Prédit la performance complète pour un contenu."""
        try:
            self.logger.info(f"Predicting performance for content {content_id}")
            
            predicted_metrics = {}
            confidence_scores = {}
            benchmarks = {}
            
            # Prédictions par plateforme
            for platform in target_platforms:
                platform_metrics = await self._predict_platform_performance(
                    platform, content_data, campaign_config
                )
                predicted_metrics[platform] = platform_metrics
                
                # Calcul de confiance
                confidence_scores[platform] = await self._calculate_prediction_confidence(
                    platform, content_data
                )
                
                # Benchmarks
                benchmarks[platform] = await self._get_platform_benchmarks(
                    platform, content_data.get('industry', 'general')
                )
            
            # Opportunités d'optimisation
            optimization_opportunities = await self._identify_optimization_opportunities(
                predicted_metrics, benchmarks, content_data
            )
            
            # Facteurs de risque
            risk_factors = await self._identify_performance_risks(
                predicted_metrics, content_data
            )
            
            # Timeline prédite
            expected_timeline = await self._predict_performance_timeline(
                predicted_metrics, target_platforms
            )
            
            # Prévision ROI
            roi_forecast = await self._calculate_roi_forecast(
                predicted_metrics, campaign_config or {}
            )
            
            return PerformancePrediction(
                content_id=content_id,
                predicted_metrics=predicted_metrics,
                confidence_scores=confidence_scores,
                performance_benchmarks=benchmarks,
                optimization_opportunities=optimization_opportunities,
                risk_factors=risk_factors,
                expected_timeline=expected_timeline,
                roi_forecast=roi_forecast
            )
            
        except Exception as e:
            self.logger.error(f"Error predicting performance: {str(e)}")
            raise
    
    async def _predict_platform_performance(self, platform: str, content_data: Dict[str, Any],
                                          campaign_config: Optional[Dict[str, Any]]) -> Dict[str, float]:
        """Prédit la performance pour une plateforme spécifique."""
        metrics = {}
        
        # Prédiction d'engagement
        engagement_rate = await self._predict_engagement_rate(platform, content_data)
        metrics['engagement_rate'] = engagement_rate
        
        # Prédiction de portée
        reach = await self._predict_reach(platform, content_data, campaign_config)
        metrics['reach'] = reach
        
        # Calcul des métriques dérivées
        metrics['total_engagement'] = reach * engagement_rate
        
        # Prédiction CTR
        ctr = await self._predict_click_through_rate(platform, content_data)
        metrics['click_through_rate'] = ctr
        
        # Prédiction de conversion
        conversion_rate = await self._predict_conversion_rate(platform, content_data)
        metrics['conversion_rate'] = conversion_rate
        
        # Métriques de coût (si budget spécifié)
        if campaign_config and 'budget' in campaign_config:
            budget = campaign_config['budget']
            metrics['cost_per_engagement'] = budget / metrics['total_engagement'] if metrics['total_engagement'] > 0 else 0
            metrics['cost_per_click'] = budget / (reach * ctr) if reach * ctr > 0 else 0
        
        return metrics
    
    async def _predict_engagement_rate(self, platform: str, content_data: Dict[str, Any]) -> float:
        """Prédit le taux d'engagement pour une plateforme."""
        model = self.predictive_models['engagement_predictor']
        
        # Taux de base pour la plateforme
        base_rate = model['base_rates'].get(platform, 0.03)
        
        # Calcul du score basé sur les features
        feature_score = 0
        for i, feature in enumerate(model['features']):
            weight = model['weights'][i]
            
            if feature == 'content_quality':
                value = content_data.get('content_quality_score', 0.7)
            elif feature == 'timing_score':
                value = content_data.get('timing_optimization_score', 0.7)
            elif feature == 'audience_match':
                value = content_data.get('audience_match_score', 0.6)
            elif feature == 'trend_alignment':
                value = content_data.get('trend_alignment_score', 0.5)
            else:
                value = 0.5
            
            feature_score += value * weight
        
        # Application du score aux taux de base
        predicted_rate = base_rate * (0.5 + feature_score)
        
        # Limites réalistes
        return min(max(predicted_rate, 0.005), 0.15)
    
    async def _predict_reach(self, platform: str, content_data: Dict[str, Any],
                           campaign_config: Optional[Dict[str, Any]]) -> int:
        """Prédit la portée pour une plateforme."""
        model = self.predictive_models['reach_predictor']
        
        # Portée organique de base
        follower_count = content_data.get('follower_count', 1000)
        organic_reach_rate = 0.1  # 10% des followers en moyenne
        organic_reach = int(follower_count * organic_reach_rate)
        
        # Facteurs d'amplification
        amplification = 1.0
        
        # Qualité du contenu
        content_quality = content_data.get('content_quality_score', 0.7)
        if content_quality > 0.8:
            amplification *= model['amplification_factors']['high_quality']
        
        # Contenu trending
        is_trending = content_data.get('is_trending_topic', False)
        if is_trending:
            amplification *= model['amplification_factors']['trending']
        
        # Boost algorithmique
        algorithm_score = content_data.get('algorithm_optimization_score', 0.5)
        if algorithm_score > 0.8:
            amplification *= model['amplification_factors']['algorithm_boost']
        
        # Portée payante (si budget)
        paid_reach = 0
        if campaign_config and 'budget' in campaign_config:
            budget = campaign_config['budget']
            # Estimation simple: $10 CPM
            paid_reach = int((budget / 10) * 1000)
        
        total_reach = int((organic_reach * amplification) + paid_reach)
        
        return max(total_reach, organic_reach)
    
    async def _predict_click_through_rate(self, platform: str, content_data: Dict[str, Any]) -> float:
        """Prédit le taux de clic pour une plateforme."""
        # Taux de base par plateforme
        base_rates = {
            'instagram': 0.015,
            'tiktok': 0.012,
            'youtube': 0.028,
            'facebook': 0.018,
            'linkedin': 0.032,
            'twitter': 0.022
        }
        
        base_ctr = base_rates.get(platform, 0.02)
        
        # Facteurs d'influence
        has_cta = content_data.get('has_call_to_action', False)
        cta_multiplier = 1.5 if has_cta else 1.0
        
        content_type = content_data.get('content_type', 'text')
        type_multipliers = {'video': 1.3, 'image': 1.1, 'carousel': 1.2, 'text': 1.0}
        type_multiplier = type_multipliers.get(content_type, 1.0)
        
        engagement_quality = content_data.get('engagement_quality_score', 0.7)
        
        predicted_ctr = base_ctr * cta_multiplier * type_multiplier * (0.5 + engagement_quality)
        
        return min(predicted_ctr, 0.08)  # Cap réaliste
    
    async def _predict_conversion_rate(self, platform: str, content_data: Dict[str, Any]) -> float:
        """Prédit le taux de conversion pour une plateforme."""
        model = self.predictive_models['conversion_predictor']
        
        # Taux de base
        base_conversion_rates = {
            'instagram': 0.024,
            'youtube': 0.031,
            'linkedin': 0.048,
            'facebook': 0.027,
            'tiktok': 0.019
        }
        
        base_rate = base_conversion_rates.get(platform, 0.025)
        
        # Modificateur de plateforme
        platform_modifier = model['platform_modifiers'].get(platform, 1.0)
        
        # Facteurs de conversion
        has_strong_cta = content_data.get('has_strong_call_to_action', False)
        landing_quality = content_data.get('landing_page_quality', 0.7)
        audience_intent = content_data.get('audience_purchase_intent', 0.5)
        offer_strength = content_data.get('offer_attractiveness', 0.6)
        
        # Score composite
        conversion_score = (
            (1.5 if has_strong_cta else 1.0) *
            landing_quality *
            (0.5 + audience_intent) *
            (0.5 + offer_strength)
        )
        
        predicted_rate = base_rate * platform_modifier * conversion_score
        
        return min(predicted_rate, 0.1)  # Cap réaliste
    
    async def _calculate_prediction_confidence(self, platform: str, content_data: Dict[str, Any]) -> float:
        """Calcule la confiance dans la prédiction."""
        confidence_factors = []
        
        # Facteur de données historiques
        historical_data_points = content_data.get('historical_performance_points', 0)
        data_confidence = min(historical_data_points / 50, 1.0)
        confidence_factors.append(data_confidence)
        
        # Facteur de complétude des données
        required_fields = ['content_quality_score', 'audience_match_score', 'follower_count']
        completeness = sum(1 for field in required_fields if field in content_data) / len(required_fields)
        confidence_factors.append(completeness)
        
        # Facteur de connaissance de la plateforme
        platform_knowledge = 1.0 if platform in self.roi_optimizer.roi_models else 0.6
        confidence_factors.append(platform_knowledge)
        
        # Facteur de récence des benchmarks
        confidence_factors.append(0.8)  # Suppose des benchmarks récents
        
        return np.mean(confidence_factors)
    
    async def _get_platform_benchmarks(self, platform: str, industry: str) -> Dict[str, float]:
        """Récupère les benchmarks pour une plateforme et industrie."""
        if industry in self.benchmarks:
            platform_benchmarks = {}
            for metric, platforms in self.benchmarks[industry].items():
                if platform in platforms:
                    platform_benchmarks[metric] = platforms[platform]
            return platform_benchmarks
        
        # Benchmarks par défaut
        return {
            'engagement_rate': 0.03,
            'click_through_rate': 0.02,
            'conversion_rate': 0.025
        }
    
    async def _identify_optimization_opportunities(self, predicted_metrics: Dict[str, Any],
                                                 benchmarks: Dict[str, Any],
                                                 content_data: Dict[str, Any]) -> List[str]:
        """Identifie les opportunités d'optimisation."""
        opportunities = []
        
        for platform, metrics in predicted_metrics.items():
            platform_benchmarks = benchmarks.get(platform, {})
            
            # Opportunités basées sur les benchmarks
            for metric, predicted_value in metrics.items():
                if metric in platform_benchmarks:
                    benchmark_value = platform_benchmarks[metric]
                    
                    if predicted_value < benchmark_value * 0.8:
                        if metric == 'engagement_rate':
                            opportunities.append(f"Améliorer l'engagement sur {platform} (sous benchmark)")
                        elif metric == 'click_through_rate':
                            opportunities.append(f"Optimiser CTR sur {platform} avec meilleurs CTA")
                        elif metric == 'conversion_rate':
                            opportunities.append(f"Améliorer conversion sur {platform} avec landing page")
        
        # Opportunités générales
        content_quality = content_data.get('content_quality_score', 0.7)
        if content_quality < 0.8:
            opportunities.append("Améliorer la qualité générale du contenu")
        
        has_cta = content_data.get('has_call_to_action', False)
        if not has_cta:
            opportunities.append("Ajouter des appels à l'action clairs")
        
        timing_score = content_data.get('timing_optimization_score', 0.7)
        if timing_score < 0.8:
            opportunities.append("Optimiser le timing de publication")
        
        return opportunities[:8]  # Limite aux 8 principales
    
    async def _identify_performance_risks(self, predicted_metrics: Dict[str, Any],
                                        content_data: Dict[str, Any]) -> List[str]:
        """Identifie les risques de performance."""
        risks = []
        
        # Risques basés sur les prédictions
        avg_engagement = np.mean([
            metrics.get('engagement_rate', 0) 
            for metrics in predicted_metrics.values()
        ])
        
        if avg_engagement < 0.02:
            risks.append("Engagement prédit très faible sur toutes plateformes")
        
        # Risques de contenu
        content_safety = content_data.get('content_safety_score', 0.8)
        if content_safety < 0.7:
            risks.append("Risque de restriction algorithmique")
        
        # Risques de timing
        is_peak_time = content_data.get('is_peak_time', True)
        if not is_peak_time:
            risks.append("Publication hors heures optimales")
        
        # Risques de concurrence
        competition_level = content_data.get('competition_intensity', 0.5)
        if competition_level > 0.8:
            risks.append("Concurrence très élevée sur le sujet")
        
        # Risques budgétaires
        estimated_cpm = content_data.get('estimated_cpm', 10)
        if estimated_cpm > 20:
            risks.append("Coûts de distribution élevés prédits")
        
        return risks
    
    async def _predict_performance_timeline(self, predicted_metrics: Dict[str, Any],
                                          platforms: List[str]) -> Dict[str, Any]:
        """Prédit la timeline de performance."""
        timeline = {
            'phases': {},
            'key_milestones': [],
            'optimization_windows': []
        }
        
        current_time = datetime.now()
        
        # Phase initiale (0-2h)
        timeline['phases']['initial'] = {
            'start': current_time.isoformat(),
            'end': (current_time + timedelta(hours=2)).isoformat(),
            'expected_reach_percentage': 15,
            'key_actions': ['Monitoring initial', 'Ajustements rapides']
        }
        
        # Phase de croissance (2-24h)
        timeline['phases']['growth'] = {
            'start': (current_time + timedelta(hours=2)).isoformat(),
            'end': (current_time + timedelta(hours=24)).isoformat(),
            'expected_reach_percentage': 70,
            'key_actions': ['Amplification', 'Optimisation continue']
        }
        
        # Phase de maturité (24-72h)
        timeline['phases']['maturity'] = {
            'start': (current_time + timedelta(hours=24)).isoformat(),
            'end': (current_time + timedelta(hours=72)).isoformat(),
            'expected_reach_percentage': 100,
            'key_actions': ['Maintien performance', 'Analyse ROI']
        }
        
        # Jalons clés
        timeline['key_milestones'] = [
            {'time': (current_time + timedelta(hours=6)).isoformat(), 'event': 'Premier rapport performance'},
            {'time': (current_time + timedelta(hours=24)).isoformat(), 'event': 'Évaluation ROI intermédiaire'},
            {'time': (current_time + timedelta(hours=72)).isoformat(), 'event': 'Rapport final performance'}
        ]
        
        # Fenêtres d'optimisation
        timeline['optimization_windows'] = [
            {'start_hour': 1, 'end_hour': 3, 'focus': 'Ajustements créatifs'},
            {'start_hour': 8, 'end_hour': 10, 'focus': 'Optimisation budget'},
            {'start_hour': 24, 'end_hour': 48, 'focus': 'Scaling stratégique'}
        ]
        
        return timeline
    
    async def _calculate_roi_forecast(self, predicted_metrics: Dict[str, Any],
                                    campaign_config: Dict[str, Any]) -> Dict[str, float]:
        """Calcule la prévision ROI basée sur les métriques prédites."""
        roi_forecast = {}
        
        total_budget = campaign_config.get('total_budget', 0)
        if total_budget <= 0:
            return {'total_roi': 0.0, 'revenue_prediction': 0.0}
        
        total_revenue = 0
        platform_revenues = {}
        
        for platform, metrics in predicted_metrics.items():
            reach = metrics.get('reach', 0)
            conversion_rate = metrics.get('conversion_rate', 0.025)
            
            # Revenus estimés
            conversions = reach * conversion_rate
            avg_customer_value = campaign_config.get('avg_customer_value', 50)
            platform_revenue = conversions * avg_customer_value
            
            platform_revenues[platform] = platform_revenue
            total_revenue += platform_revenue
        
        # ROI global
        total_roi = ((total_revenue - total_budget) / total_budget * 100) if total_budget > 0 else 0
        
        roi_forecast = {
            'total_roi': round(total_roi, 2),
            'total_revenue_prediction': round(total_revenue, 2),
            'total_investment': total_budget,
            'platform_revenues': {k: round(v, 2) for k, v in platform_revenues.items()},
            'break_even_point': 'Immédiat' if total_roi > 0 else 'Non atteint',
            'profit_margin': round((total_revenue - total_budget) / total_revenue * 100, 2) if total_revenue > 0 else 0
        }
        
        return roi_forecast
    
    async def analyze_performance_gap(self, predicted_performance: PerformancePrediction,
                                    actual_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse l'écart entre performance prédite et réelle."""
        try:
            gap_analysis = {}
            
            for platform in predicted_performance.predicted_metrics.keys():
                if platform in actual_metrics:
                    platform_gaps = {}
                    predicted = predicted_performance.predicted_metrics[platform]
                    actual = actual_metrics[platform]
                    
                    for metric in predicted.keys():
                        if metric in actual:
                            predicted_value = predicted[metric]
                            actual_value = actual[metric]
                            
                            if predicted_value > 0:
                                gap_percentage = ((actual_value - predicted_value) / predicted_value) * 100
                                platform_gaps[metric] = {
                                    'predicted': predicted_value,
                                    'actual': actual_value,
                                    'gap_percentage': round(gap_percentage, 2),
                                    'performance': 'above' if gap_percentage > 0 else 'below'
                                }
                    
                    gap_analysis[platform] = platform_gaps
            
            # Analyse globale
            overall_accuracy = await self._calculate_overall_prediction_accuracy(gap_analysis)
            
            # Insights et recommandations
            insights = await self._generate_gap_insights(gap_analysis)
            
            return {
                'content_id': predicted_performance.content_id,
                'gap_analysis': gap_analysis,
                'overall_accuracy': overall_accuracy,
                'insights': insights,
                'model_improvement_suggestions': await self._suggest_model_improvements(gap_analysis)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing performance gap: {str(e)}")
            return {'error': str(e)}
    
    async def _calculate_overall_prediction_accuracy(self, gap_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calcule la précision globale des prédictions."""
        all_gaps = []
        
        for platform_gaps in gap_analysis.values():
            for metric_gap in platform_gaps.values():
                all_gaps.append(abs(metric_gap['gap_percentage']))
        
        if not all_gaps:
            return {'accuracy': 0.0, 'avg_error': 0.0}
        
        avg_error = np.mean(all_gaps)
        accuracy = max(0, 100 - avg_error)
        
        return {
            'accuracy_percentage': round(accuracy, 2),
            'average_error_percentage': round(avg_error, 2),
            'prediction_quality': 'excellent' if accuracy > 80 else 'good' if accuracy > 60 else 'needs_improvement'
        }
    
    async def _generate_gap_insights(self, gap_analysis: Dict[str, Any]) -> List[str]:
        """Génère des insights basés sur l'analyse des écarts."""
        insights = []
        
        # Analyse des patterns d'écart
        over_performers = []
        under_performers = []
        
        for platform, metrics in gap_analysis.items():
            platform_performance = np.mean([m['gap_percentage'] for m in metrics.values()])
            
            if platform_performance > 20:
                over_performers.append(platform)
            elif platform_performance < -20:
                under_performers.append(platform)
        
        if over_performers:
            insights.append(f"Plateformes surperformantes: {', '.join(over_performers)}")
        
        if under_performers:
            insights.append(f"Plateformes sous-performantes: {', '.join(under_performers)}")
        
        # Métriques les plus difficiles à prédire
        metric_errors = defaultdict(list)
        for platform_metrics in gap_analysis.values():
            for metric, data in platform_metrics.items():
                metric_errors[metric].append(abs(data['gap_percentage']))
        
        most_variable_metric = max(metric_errors.items(), key=lambda x: np.mean(x[1]))[0]
        insights.append(f"Métrique la plus variable: {most_variable_metric}")
        
        return insights
    
    async def _suggest_model_improvements(self, gap_analysis: Dict[str, Any]) -> List[str]:
        """Suggère des améliorations pour les modèles prédictifs."""
        suggestions = []
        
        # Analyse des biais systématiques
        overall_bias = np.mean([
            np.mean([m['gap_percentage'] for m in platform_metrics.values()])
            for platform_metrics in gap_analysis.values()
        ])
        
        if overall_bias > 15:
            suggestions.append("Ajuster les modèles - biais optimiste détecté")
        elif overall_bias < -15:
            suggestions.append("Ajuster les modèles - biais pessimiste détecté")
        
        # Suggestions spécifiques
        suggestions.extend([
            "Intégrer plus de données temps réel",
            "Améliorer la pondération des facteurs saisonniers",
            "Affiner les benchmarks par industry",
            "Développer des modèles spécifiques par type de créateur"
        ])
        
        return suggestions[:5]
    
    def get_engine_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du moteur de performance."""
        return {
            'predictions_made': sum(len(history) for history in self.performance_history.values()),
            'platforms_supported': len(self.roi_optimizer.roi_models),
            'industries_benchmarked': len(self.benchmarks),
            'predictive_models': len(self.predictive_models),
            'engine_status': 'operational'
        }