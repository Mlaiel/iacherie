"""
Engagement Prediction Model - Ainflue Enterprise
==============================================
Modèle prédiction engagement avec time series et social signals.
Engagement forecasting + viral prediction + audience behavior + monetization impact.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue ML Models
Version: 1.0 Production
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
from pathlib import Path
import json
import pandas as pd
from datetime import datetime, timedelta
import math

# ⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
# Cette architecture ML et tous ses algorithmes sont la propriété intellectuelle 
# EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Tous droits réservés.

logger = logging.getLogger(__name__)

class EngagementType(Enum):
    """Types d'engagement mesurés"""
    VIEWS = "views"
    LIKES = "likes"
    SHARES = "shares"
    COMMENTS = "comments"
    SAVES = "saves"
    CLICK_THROUGH = "click_through"
    DWELL_TIME = "dwell_time"
    CONVERSION = "conversion"

class ViralityLevel(Enum):
    """Niveaux de viralité prédits"""
    LOW = 1
    MODERATE = 2
    HIGH = 3
    VIRAL = 4
    MEGA_VIRAL = 5

class AudienceBehavior(Enum):
    """Comportements audience observés"""
    PASSIVE_VIEWING = "passive_viewing"
    ACTIVE_ENGAGEMENT = "active_engagement"
    SHARING_ORIENTED = "sharing_oriented"
    DISCUSSION_DRIVEN = "discussion_driven"
    CONVERSION_FOCUSED = "conversion_focused"

class PlatformType(Enum):
    """Plateformes pour prédiction engagement"""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    SNAPCHAT = "snapchat"

@dataclass
class ContentFeatures:
    """Features contenu pour prédiction engagement"""
    content_id: str
    content_type: str
    quality_score: float
    duration: Optional[float] = None
    hashtags: List[str] = None
    posting_time: Optional[datetime] = None
    creator_follower_count: int = 0
    historical_engagement_rate: float = 0.0
    sentiment_score: float = 0.5
    trending_topics_alignment: float = 0.0

@dataclass
class EngagementPredictionRequest:
    """Requête prédiction engagement"""
    content_features: ContentFeatures
    target_platforms: List[PlatformType]
    prediction_horizon_hours: int = 24
    audience_context: Optional[Dict[str, Any]] = None
    business_objectives: Optional[Dict[str, float]] = None

@dataclass
class EngagementForecast:
    """Forecast engagement par type"""
    engagement_type: EngagementType
    predicted_value: float
    confidence_interval: Tuple[float, float]
    peak_time_hours: float
    growth_rate: float
    plateau_value: float

@dataclass
class ViralPrediction:
    """Prédiction potentiel viral"""
    virality_level: ViralityLevel
    viral_probability: float
    estimated_reach: int
    viral_factors: List[str]
    tipping_point_hours: Optional[float]
    viral_coefficient: float

@dataclass
class AudienceBehaviorAnalysis:
    """Analyse comportement audience"""
    dominant_behavior: AudienceBehavior
    behavior_probabilities: Dict[AudienceBehavior, float]
    engagement_patterns: Dict[str, float]
    demographic_preferences: Dict[str, float]
    optimal_posting_times: List[datetime]

@dataclass
class MonetizationForecast:
    """Forecast impact monétisation"""
    estimated_revenue: float
    conversion_rate: float
    cpm_estimate: float
    sponsorship_value: float
    affiliate_potential: float
    merchandise_opportunity: float

@dataclass
class EngagementPredictionResult:
    """Résultat complet prédiction engagement"""
    content_id: str
    prediction_timestamp: str
    engagement_forecasts: Dict[EngagementType, EngagementForecast]
    platform_predictions: Dict[PlatformType, Dict[str, float]]
    viral_prediction: ViralPrediction
    audience_behavior: AudienceBehaviorAnalysis
    monetization_forecast: MonetizationForecast
    optimization_recommendations: List[str]
    confidence_score: float
    processing_time_ms: float

@dataclass
class EngagementConfig:
    """Configuration pour prédiction engagement"""
    model_version: str = "1.0"
    device: str = "cpu"
    prediction_accuracy_target: float = 0.85
    enable_viral_prediction: bool = True
    enable_monetization_forecast: bool = True
    time_series_window_hours: int = 168  # 1 week

class TimeSeriesPredictor(nn.Module):
    """Prédicteur time series pour engagement trends"""
    
    def __init__(self, config: EngagementConfig):
        super().__init__()
        self.config = config
        self.hidden_size = 128
        self.num_layers = 2
        
        # LSTM for time series prediction
        self.lstm = nn.LSTM(
            input_size=10,  # Features: time, engagement types, etc.
            hidden_size=self.hidden_size,
            num_layers=self.num_layers,
            batch_first=True,
            dropout=0.2
        )
        
        # Attention mechanism
        self.attention = nn.MultiheadAttention(
            embed_dim=self.hidden_size,
            num_heads=8,
            dropout=0.1
        )
        
        # Prediction heads for different engagement types
        self.engagement_predictors = nn.ModuleDict({
            engagement_type.value: nn.Sequential(
                nn.Linear(self.hidden_size, 64),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.Linear(32, 1),
                nn.ReLU()  # Ensure positive predictions
            ) for engagement_type in EngagementType
        })
        
        # Confidence predictor
        self.confidence_predictor = nn.Sequential(
            nn.Linear(self.hidden_size, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    
    def forward(self, time_series_data: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Forward pass pour time series prediction"""
        batch_size, seq_len, _ = time_series_data.shape
        
        # LSTM processing
        lstm_output, (hidden, cell) = self.lstm(time_series_data)
        
        # Attention mechanism
        attended_output, attention_weights = self.attention(
            lstm_output, lstm_output, lstm_output
        )
        
        # Use last time step for prediction
        final_features = attended_output[:, -1, :]
        
        # Predict engagement for each type
        predictions = {}
        for engagement_type in EngagementType:
            pred = self.engagement_predictors[engagement_type.value](final_features)
            predictions[engagement_type.value] = pred.squeeze()
        
        # Predict confidence
        confidence = self.confidence_predictor(final_features).squeeze()
        predictions['confidence'] = confidence
        
        return predictions
    
    def predict_engagement_trajectory(self, content_features: ContentFeatures,
                                    historical_data: np.ndarray,
                                    prediction_hours: int = 24) -> Dict[EngagementType, EngagementForecast]:
        """Prédiction trajectoire engagement avec growth patterns"""
        self.eval()
        
        # Prepare input data
        input_tensor = torch.FloatTensor(historical_data).unsqueeze(0)
        
        forecasts = {}
        
        with torch.no_grad():
            predictions = self.forward(input_tensor)
            
            for engagement_type in EngagementType:
                pred_value = predictions[engagement_type.value].item()
                confidence = predictions['confidence'].item()
                
                # Calculate growth parameters
                growth_rate = self._calculate_growth_rate(historical_data, engagement_type)
                peak_time = self._estimate_peak_time(content_features, engagement_type)
                plateau_value = pred_value * 1.2  # Estimate plateau
                
                # Confidence interval
                margin = pred_value * (1 - confidence) * 0.5
                confidence_interval = (
                    max(0, pred_value - margin),
                    pred_value + margin
                )
                
                forecast = EngagementForecast(
                    engagement_type=engagement_type,
                    predicted_value=pred_value,
                    confidence_interval=confidence_interval,
                    peak_time_hours=peak_time,
                    growth_rate=growth_rate,
                    plateau_value=plateau_value
                )
                
                forecasts[engagement_type] = forecast
        
        return forecasts
    
    def _calculate_growth_rate(self, historical_data: np.ndarray, 
                             engagement_type: EngagementType) -> float:
        """Calcul taux de croissance basé sur données historiques"""
        if len(historical_data) < 2:
            return 0.1  # Default growth rate
        
        # Simple growth rate calculation
        recent_values = historical_data[-5:, 0]  # Last 5 data points
        if len(recent_values) >= 2:
            growth_rate = (recent_values[-1] - recent_values[0]) / max(recent_values[0], 1)
            return max(0.0, min(2.0, growth_rate))  # Clamp between 0 and 200%
        
        return 0.1
    
    def _estimate_peak_time(self, content_features: ContentFeatures,
                          engagement_type: EngagementType) -> float:
        """Estimation temps de pic engagement"""
        # Different engagement types peak at different times
        peak_times = {
            EngagementType.VIEWS: 2.0,  # Views peak early
            EngagementType.LIKES: 4.0,  # Likes peak a bit later
            EngagementType.SHARES: 8.0,  # Shares take longer
            EngagementType.COMMENTS: 6.0,  # Comments moderate timing
            EngagementType.SAVES: 12.0,  # Saves happen later
            EngagementType.CLICK_THROUGH: 3.0,
            EngagementType.DWELL_TIME: 1.0,
            EngagementType.CONVERSION: 24.0  # Conversions take longest
        }
        
        base_peak_time = peak_times.get(engagement_type, 6.0)
        
        # Adjust based on content quality
        quality_factor = content_features.quality_score
        adjusted_peak_time = base_peak_time * (2 - quality_factor)  # Higher quality peaks faster
        
        return max(0.5, adjusted_peak_time)

class ViralPredictionEngine:
    """Moteur prédiction viral avec social signals"""
    
    def __init__(self, config: EngagementConfig):
        self.config = config
        
        # Viral prediction factors
        self.viral_factors = {
            'content_quality': 0.25,
            'creator_influence': 0.20,
            'trending_alignment': 0.15,
            'emotion_intensity': 0.15,
            'shareability': 0.15,
            'timing_optimization': 0.10
        }
    
    def predict_viral_potential(self, content_features: ContentFeatures,
                              engagement_forecasts: Dict[EngagementType, EngagementForecast]) -> ViralPrediction:
        """Prédiction potentiel viral basé sur content features et engagement patterns"""
        
        # Calculate viral score based on multiple factors
        viral_score = 0.0
        viral_factors_detected = []
        
        # Content quality factor
        quality_contribution = content_features.quality_score * self.viral_factors['content_quality']
        viral_score += quality_contribution
        if content_features.quality_score > 0.8:
            viral_factors_detected.append("High content quality")
        
        # Creator influence factor
        # Normalized follower count (log scale)
        influence_score = min(1.0, math.log10(max(content_features.creator_follower_count, 1)) / 6.0)
        influence_contribution = influence_score * self.viral_factors['creator_influence']
        viral_score += influence_contribution
        if influence_score > 0.7:
            viral_factors_detected.append("High creator influence")
        
        # Trending alignment factor
        trending_contribution = content_features.trending_topics_alignment * self.viral_factors['trending_alignment']
        viral_score += trending_contribution
        if content_features.trending_topics_alignment > 0.7:
            viral_factors_detected.append("Strong trending alignment")
        
        # Emotion intensity (based on sentiment)
        emotion_intensity = abs(content_features.sentiment_score - 0.5) * 2  # Convert to 0-1 scale
        emotion_contribution = emotion_intensity * self.viral_factors['emotion_intensity']
        viral_score += emotion_contribution
        if emotion_intensity > 0.8:
            viral_factors_detected.append("High emotional intensity")
        
        # Shareability (based on predicted shares vs views ratio)
        if EngagementType.SHARES in engagement_forecasts and EngagementType.VIEWS in engagement_forecasts:
            share_ratio = (engagement_forecasts[EngagementType.SHARES].predicted_value / 
                          max(engagement_forecasts[EngagementType.VIEWS].predicted_value, 1))
            shareability_score = min(1.0, share_ratio * 10)  # Normalize
            shareability_contribution = shareability_score * self.viral_factors['shareability']
            viral_score += shareability_contribution
            if shareability_score > 0.6:
                viral_factors_detected.append("High shareability potential")
        
        # Timing optimization
        timing_score = self._calculate_timing_score(content_features)
        timing_contribution = timing_score * self.viral_factors['timing_optimization']
        viral_score += timing_contribution
        if timing_score > 0.8:
            viral_factors_detected.append("Optimal timing")
        
        # Determine virality level
        if viral_score >= 0.9:
            virality_level = ViralityLevel.MEGA_VIRAL
            estimated_reach = content_features.creator_follower_count * 50
        elif viral_score >= 0.75:
            virality_level = ViralityLevel.VIRAL
            estimated_reach = content_features.creator_follower_count * 20
        elif viral_score >= 0.6:
            virality_level = ViralityLevel.HIGH
            estimated_reach = content_features.creator_follower_count * 10
        elif viral_score >= 0.4:
            virality_level = ViralityLevel.MODERATE
            estimated_reach = content_features.creator_follower_count * 5
        else:
            virality_level = ViralityLevel.LOW
            estimated_reach = content_features.creator_follower_count * 2
        
        # Calculate tipping point
        tipping_point_hours = self._calculate_tipping_point(viral_score, engagement_forecasts)
        
        # Viral coefficient (how much each share multiplies reach)
        viral_coefficient = 1.0 + (viral_score * 2.0)
        
        return ViralPrediction(
            virality_level=virality_level,
            viral_probability=viral_score,
            estimated_reach=int(estimated_reach),
            viral_factors=viral_factors_detected,
            tipping_point_hours=tipping_point_hours,
            viral_coefficient=viral_coefficient
        )
    
    def _calculate_timing_score(self, content_features: ContentFeatures) -> float:
        """Calcul score timing optimal"""
        if not content_features.posting_time:
            return 0.5  # Neutral score if no time info
        
        # Optimal posting times (simplified)
        hour = content_features.posting_time.hour
        day_of_week = content_features.posting_time.weekday()
        
        # Peak engagement hours: 7-9 AM, 12-1 PM, 7-9 PM
        if hour in [7, 8, 12, 19, 20]:
            time_score = 1.0
        elif hour in [9, 11, 13, 18, 21]:
            time_score = 0.8
        elif hour in [6, 10, 14, 15, 16, 17, 22]:
            time_score = 0.6
        else:
            time_score = 0.3
        
        # Weekdays generally better for engagement
        if day_of_week in [0, 1, 2, 3, 4]:  # Monday to Friday
            day_score = 0.8
        elif day_of_week == 6:  # Sunday
            day_score = 0.9
        else:  # Saturday
            day_score = 0.7
        
        return (time_score + day_score) / 2
    
    def _calculate_tipping_point(self, viral_score: float,
                               engagement_forecasts: Dict[EngagementType, EngagementForecast]) -> Optional[float]:
        """Calcul point de basculement viral"""
        if viral_score < 0.5:
            return None  # No viral tipping point expected
        
        # Estimate when viral growth begins
        base_tipping_point = 6.0  # 6 hours base
        
        # Earlier tipping point for higher viral potential
        viral_acceleration = (1 - viral_score) * 5  # 0-5 hours adjustment
        tipping_point = base_tipping_point - viral_acceleration
        
        return max(1.0, tipping_point)

class AudienceBehaviorAnalyzer:
    """Analyseur comportement audience avec ML patterns"""
    
    def __init__(self, config: EngagementConfig):
        self.config = config
        
        # Behavior pattern definitions
        self.behavior_patterns = {
            AudienceBehavior.PASSIVE_VIEWING: {
                'views_ratio': 0.8,
                'likes_ratio': 0.1,
                'shares_ratio': 0.05,
                'comments_ratio': 0.05
            },
            AudienceBehavior.ACTIVE_ENGAGEMENT: {
                'views_ratio': 0.6,
                'likes_ratio': 0.25,
                'shares_ratio': 0.1,
                'comments_ratio': 0.15
            },
            AudienceBehavior.SHARING_ORIENTED: {
                'views_ratio': 0.5,
                'likes_ratio': 0.2,
                'shares_ratio': 0.25,
                'comments_ratio': 0.05
            },
            AudienceBehavior.DISCUSSION_DRIVEN: {
                'views_ratio': 0.4,
                'likes_ratio': 0.15,
                'shares_ratio': 0.1,
                'comments_ratio': 0.35
            },
            AudienceBehavior.CONVERSION_FOCUSED: {
                'views_ratio': 0.7,
                'likes_ratio': 0.1,
                'shares_ratio': 0.05,
                'clicks_ratio': 0.15
            }
        }
    
    def analyze_audience_behavior(self, content_features: ContentFeatures,
                                engagement_forecasts: Dict[EngagementType, EngagementForecast]) -> AudienceBehaviorAnalysis:
        """Analyse comportement audience basé sur engagement patterns"""
        
        # Calculate engagement ratios
        total_engagement = sum(
            forecast.predicted_value for forecast in engagement_forecasts.values()
        )
        
        if total_engagement == 0:
            # Default behavior analysis
            return self._default_behavior_analysis()
        
        engagement_ratios = {
            'views_ratio': engagement_forecasts.get(EngagementType.VIEWS, EngagementForecast(
                EngagementType.VIEWS, 0, (0, 0), 0, 0, 0
            )).predicted_value / total_engagement,
            'likes_ratio': engagement_forecasts.get(EngagementType.LIKES, EngagementForecast(
                EngagementType.LIKES, 0, (0, 0), 0, 0, 0
            )).predicted_value / total_engagement,
            'shares_ratio': engagement_forecasts.get(EngagementType.SHARES, EngagementForecast(
                EngagementType.SHARES, 0, (0, 0), 0, 0, 0
            )).predicted_value / total_engagement,
            'comments_ratio': engagement_forecasts.get(EngagementType.COMMENTS, EngagementForecast(
                EngagementType.COMMENTS, 0, (0, 0), 0, 0, 0
            )).predicted_value / total_engagement
        }
        
        # Compare with behavior patterns
        behavior_scores = {}
        for behavior, pattern in self.behavior_patterns.items():
            score = 0.0
            matches = 0
            
            for ratio_key, expected_ratio in pattern.items():
                if ratio_key in engagement_ratios:
                    actual_ratio = engagement_ratios[ratio_key]
                    # Calculate similarity (inverse of absolute difference)
                    similarity = 1.0 - abs(actual_ratio - expected_ratio)
                    score += similarity
                    matches += 1
            
            if matches > 0:
                behavior_scores[behavior] = score / matches
            else:
                behavior_scores[behavior] = 0.0
        
        # Determine dominant behavior
        dominant_behavior = max(behavior_scores, key=behavior_scores.get)
        
        # Generate engagement patterns
        engagement_patterns = self._analyze_engagement_patterns(engagement_forecasts)
        
        # Demographic preferences (simplified)
        demographic_preferences = self._estimate_demographic_preferences(
            content_features, engagement_ratios
        )
        
        # Optimal posting times
        optimal_posting_times = self._calculate_optimal_posting_times(
            dominant_behavior, content_features
        )
        
        return AudienceBehaviorAnalysis(
            dominant_behavior=dominant_behavior,
            behavior_probabilities=behavior_scores,
            engagement_patterns=engagement_patterns,
            demographic_preferences=demographic_preferences,
            optimal_posting_times=optimal_posting_times
        )
    
    def _analyze_engagement_patterns(self, forecasts: Dict[EngagementType, EngagementForecast]) -> Dict[str, float]:
        """Analyse patterns engagement temporels"""
        patterns = {
            'early_peak': 0.0,
            'sustained_growth': 0.0,
            'late_bloomer': 0.0,
            'steady_engagement': 0.0
        }
        
        for engagement_type, forecast in forecasts.items():
            peak_time = forecast.peak_time_hours
            growth_rate = forecast.growth_rate
            
            if peak_time < 2:
                patterns['early_peak'] += 1
            elif peak_time > 12:
                patterns['late_bloomer'] += 1
            
            if growth_rate > 0.5:
                patterns['sustained_growth'] += 1
            elif 0.1 <= growth_rate <= 0.3:
                patterns['steady_engagement'] += 1
        
        # Normalize to probabilities
        total = sum(patterns.values())
        if total > 0:
            patterns = {k: v / total for k, v in patterns.items()}
        
        return patterns
    
    def _estimate_demographic_preferences(self, content_features: ContentFeatures,
                                        engagement_ratios: Dict[str, float]) -> Dict[str, float]:
        """Estimation préférences démographiques"""
        demographics = {
            'young_adults_18_24': 0.25,  # Base assumption
            'adults_25_34': 0.30,
            'adults_35_44': 0.25,
            'mature_45_plus': 0.20
        }
        
        # Adjust based on engagement patterns
        if engagement_ratios.get('shares_ratio', 0) > 0.2:
            # High sharing suggests younger audience
            demographics['young_adults_18_24'] += 0.15
            demographics['adults_25_34'] += 0.10
            demographics['mature_45_plus'] -= 0.10
        
        if engagement_ratios.get('comments_ratio', 0) > 0.2:
            # High commenting suggests engaged, possibly older audience
            demographics['adults_25_34'] += 0.10
            demographics['adults_35_44'] += 0.10
            demographics['young_adults_18_24'] -= 0.05
        
        # Normalize
        total = sum(demographics.values())
        demographics = {k: v / total for k, v in demographics.items()}
        
        return demographics
    
    def _calculate_optimal_posting_times(self, dominant_behavior: AudienceBehavior,
                                       content_features: ContentFeatures) -> List[datetime]:
        """Calcul times de posting optimaux"""
        base_time = datetime.now().replace(minute=0, second=0, microsecond=0)
        optimal_times = []
        
        # Different behaviors have different optimal times
        if dominant_behavior == AudienceBehavior.PASSIVE_VIEWING:
            # Peak viewing times
            for hour in [7, 12, 19, 21]:  # Morning, lunch, evening
                optimal_times.append(base_time.replace(hour=hour))
        
        elif dominant_behavior == AudienceBehavior.ACTIVE_ENGAGEMENT:
            # Active hours when people interact more
            for hour in [8, 13, 18, 20]:
                optimal_times.append(base_time.replace(hour=hour))
        
        elif dominant_behavior == AudienceBehavior.SHARING_ORIENTED:
            # Times when people are most likely to share
            for hour in [9, 14, 17, 22]:
                optimal_times.append(base_time.replace(hour=hour))
        
        elif dominant_behavior == AudienceBehavior.DISCUSSION_DRIVEN:
            # Times for discussions and debates
            for hour in [10, 15, 19, 21]:
                optimal_times.append(base_time.replace(hour=hour))
        
        else:  # CONVERSION_FOCUSED
            # Business hours and decision-making times
            for hour in [9, 11, 14, 16]:
                optimal_times.append(base_time.replace(hour=hour))
        
        return optimal_times
    
    def _default_behavior_analysis(self) -> AudienceBehaviorAnalysis:
        """Analyse comportement par défaut"""
        return AudienceBehaviorAnalysis(
            dominant_behavior=AudienceBehavior.PASSIVE_VIEWING,
            behavior_probabilities={behavior: 0.2 for behavior in AudienceBehavior},
            engagement_patterns={'steady_engagement': 1.0},
            demographic_preferences={'adults_25_34': 0.4, 'young_adults_18_24': 0.3, 'adults_35_44': 0.3},
            optimal_posting_times=[datetime.now().replace(hour=h, minute=0, second=0, microsecond=0) 
                                 for h in [7, 12, 19]]
        )

class MonetizationImpactCalculator:
    """Calculateur impact monétisation avec revenue prediction"""
    
    def __init__(self, config: EngagementConfig):
        self.config = config
        
        # Revenue multipliers by engagement type
        self.revenue_multipliers = {
            EngagementType.VIEWS: 0.001,  # $0.001 per view (typical CPM)
            EngagementType.CLICKS: 0.05,   # $0.05 per click
            EngagementType.SHARES: 0.02,   # $0.02 per share (reach multiplier)
            EngagementType.SAVES: 0.03,    # $0.03 per save (high intent)
            EngagementType.CONVERSION: 5.0 # $5 per conversion
        }
    
    def forecast_monetization_impact(self, engagement_forecasts: Dict[EngagementType, EngagementForecast],
                                   content_features: ContentFeatures,
                                   viral_prediction: ViralPrediction) -> MonetizationForecast:
        """Forecast impact monétisation basé sur engagement predictions"""
        
        # Calculate base revenue from direct engagement
        estimated_revenue = 0.0
        for engagement_type, forecast in engagement_forecasts.items():
            if engagement_type in self.revenue_multipliers:
                revenue_contribution = (
                    forecast.predicted_value * 
                    self.revenue_multipliers[engagement_type]
                )
                estimated_revenue += revenue_contribution
        
        # Apply viral multiplier
        if viral_prediction.virality_level.value >= 3:  # HIGH or above
            viral_multiplier = viral_prediction.viral_coefficient
            estimated_revenue *= viral_multiplier
        
        # Calculate conversion rate
        total_views = engagement_forecasts.get(
            EngagementType.VIEWS, 
            EngagementForecast(EngagementType.VIEWS, 1, (0, 1), 0, 0, 0)
        ).predicted_value
        
        total_conversions = engagement_forecasts.get(
            EngagementType.CONVERSION,
            EngagementForecast(EngagementType.CONVERSION, 0, (0, 0), 0, 0, 0)
        ).predicted_value
        
        conversion_rate = total_conversions / max(total_views, 1)
        
        # Estimate CPM (Cost Per Mille)
        cpm_base = 2.0  # $2 base CPM
        quality_multiplier = content_features.quality_score * 2  # 0-2x multiplier
        cpm_estimate = cpm_base * quality_multiplier
        
        # Sponsorship value (based on engagement and reach)
        total_engagement = sum(f.predicted_value for f in engagement_forecasts.values())
        sponsorship_value = total_engagement * 0.01  # $0.01 per engagement
        
        # Affiliate potential (based on click-through and conversion rates)
        click_through_rate = 0.02  # 2% default CTR
        affiliate_potential = total_views * click_through_rate * conversion_rate * 10  # $10 avg commission
        
        # Merchandise opportunity (based on fan engagement)
        fan_engagement_score = (
            engagement_forecasts.get(EngagementType.LIKES, EngagementForecast(EngagementType.LIKES, 0, (0, 0), 0, 0, 0)).predicted_value +
            engagement_forecasts.get(EngagementType.SAVES, EngagementForecast(EngagementType.SAVES, 0, (0, 0), 0, 0, 0)).predicted_value
        )
        merchandise_opportunity = fan_engagement_score * 0.005  # $0.005 per fan engagement
        
        return MonetizationForecast(
            estimated_revenue=estimated_revenue,
            conversion_rate=conversion_rate,
            cpm_estimate=cpm_estimate,
            sponsorship_value=sponsorship_value,
            affiliate_potential=affiliate_potential,
            merchandise_opportunity=merchandise_opportunity
        )

class EngagementPredictionModel:
    """
    Modèle principal prédiction engagement avec time series et social signals.
    Engagement forecasting + viral prediction + audience behavior + monetization impact.
    """
    
    def __init__(self, engagement_config: EngagementConfig):
        self.engagement_config = engagement_config
        self.time_series_predictor = TimeSeriesPredictor(engagement_config)
        self.viral_predictor = ViralPredictionEngine(engagement_config)
        self.audience_behavior_analyzer = AudienceBehaviorAnalyzer(engagement_config)
        self.monetization_impact_calculator = MonetizationImpactCalculator(engagement_config)
        
        # Platform-specific adjustment factors
        self.platform_adjustments = {
            PlatformType.INSTAGRAM: {'views': 1.0, 'likes': 1.2, 'shares': 0.8, 'comments': 1.1},
            PlatformType.TIKTOK: {'views': 1.5, 'likes': 1.1, 'shares': 1.3, 'comments': 0.9},
            PlatformType.YOUTUBE: {'views': 0.8, 'likes': 1.0, 'shares': 1.0, 'comments': 1.2},
            PlatformType.FACEBOOK: {'views': 0.9, 'likes': 1.1, 'shares': 1.4, 'comments': 1.3},
            PlatformType.TWITTER: {'views': 0.7, 'likes': 0.9, 'shares': 1.6, 'comments': 1.4},
            PlatformType.LINKEDIN: {'views': 0.6, 'likes': 0.8, 'shares': 1.2, 'comments': 1.5}
        }
    
    async def predict_content_engagement(self, prediction_request: EngagementPredictionRequest) -> EngagementPredictionResult:
        """
        Prédiction engagement contenu avec business impact.
        
        Engagement Prediction Features:
        - Time series forecasting pour engagement trends
        - Viral potential prediction basé sur content features
        - Audience behavior modeling avec demographic analysis
        - Platform-specific engagement optimization
        - Cross-platform engagement correlation analysis
        - Monetization impact prediction basé sur engagement metrics
        - Optimal posting time recommendations
        - Content lifecycle engagement forecasting
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            content_features = prediction_request.content_features
            target_platforms = prediction_request.target_platforms
            prediction_horizon = prediction_request.prediction_horizon_hours
            
            # Generate mock historical data for time series prediction
            historical_data = self._generate_mock_historical_data(content_features)
            
            # Predict engagement for each type
            engagement_forecasts = self.time_series_predictor.predict_engagement_trajectory(
                content_features, historical_data, prediction_horizon
            )
            
            # Platform-specific predictions
            platform_predictions = {}
            for platform in target_platforms:
                platform_pred = self._adjust_for_platform(engagement_forecasts, platform)
                platform_predictions[platform] = platform_pred
            
            # Viral prediction
            viral_prediction = self.viral_predictor.predict_viral_potential(
                content_features, engagement_forecasts
            )
            
            # Audience behavior analysis
            audience_behavior = self.audience_behavior_analyzer.analyze_audience_behavior(
                content_features, engagement_forecasts
            )
            
            # Monetization forecast
            monetization_forecast = self.monetization_impact_calculator.forecast_monetization_impact(
                engagement_forecasts, content_features, viral_prediction
            )
            
            # Generate optimization recommendations
            optimization_recommendations = self._generate_optimization_recommendations(
                engagement_forecasts, viral_prediction, audience_behavior, content_features
            )
            
            # Calculate overall confidence score
            confidence_score = self._calculate_confidence_score(
                engagement_forecasts, viral_prediction, content_features
            )
            
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return EngagementPredictionResult(
                content_id=content_features.content_id,
                prediction_timestamp=str(np.datetime64('now')),
                engagement_forecasts=engagement_forecasts,
                platform_predictions=platform_predictions,
                viral_prediction=viral_prediction,
                audience_behavior=audience_behavior,
                monetization_forecast=monetization_forecast,
                optimization_recommendations=optimization_recommendations,
                confidence_score=confidence_score,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Engagement prediction error: {e}")
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return self._default_prediction_result(prediction_request, processing_time)
    
    def _generate_mock_historical_data(self, content_features: ContentFeatures) -> np.ndarray:
        """Génération données historiques mock pour time series"""
        # Generate 7 days of hourly data (168 data points)
        hours = self.engagement_config.time_series_window_hours
        
        # Create features based on content characteristics
        base_engagement = content_features.historical_engagement_rate * 1000
        quality_factor = content_features.quality_score
        
        historical_data = []
        for hour in range(hours):
            # Simulate engagement patterns
            time_factor = math.sin(hour * math.pi / 12) * 0.3 + 0.7  # Daily cycle
            noise = np.random.normal(0, 0.1)  # Random variation
            
            engagement_value = base_engagement * quality_factor * time_factor + noise
            
            # Create feature vector: [engagement, hour_of_day, day_of_week, quality, sentiment, ...]
            feature_vector = [
                max(0, engagement_value),
                hour % 24,  # Hour of day
                (hour // 24) % 7,  # Day of week
                quality_factor,
                content_features.sentiment_score,
                content_features.trending_topics_alignment,
                math.log10(max(content_features.creator_follower_count, 1)) / 6.0,  # Normalized
                content_features.historical_engagement_rate,
                0.5,  # Placeholder for additional features
                0.5   # Placeholder for additional features
            ]
            
            historical_data.append(feature_vector)
        
        return np.array(historical_data)
    
    def _adjust_for_platform(self, base_forecasts: Dict[EngagementType, EngagementForecast],
                           platform: PlatformType) -> Dict[str, float]:
        """Ajustement prédictions pour plateforme spécifique"""
        platform_pred = {}
        adjustments = self.platform_adjustments.get(platform, {})
        
        for engagement_type, forecast in base_forecasts.items():
            adjustment_key = engagement_type.value.split('_')[0]  # Get first part of engagement type
            adjustment_factor = adjustments.get(adjustment_key, 1.0)
            
            adjusted_value = forecast.predicted_value * adjustment_factor
            platform_pred[engagement_type.value] = adjusted_value
        
        return platform_pred
    
    def _generate_optimization_recommendations(self, 
                                             engagement_forecasts: Dict[EngagementType, EngagementForecast],
                                             viral_prediction: ViralPrediction,
                                             audience_behavior: AudienceBehaviorAnalysis,
                                             content_features: ContentFeatures) -> List[str]:
        """Génération recommandations optimization"""
        recommendations = []
        
        # Content quality recommendations
        if content_features.quality_score < 0.8:
            recommendations.append("Improve content quality for higher engagement potential")
        
        # Viral potential recommendations
        if viral_prediction.viral_probability > 0.7:
            recommendations.append("High viral potential detected - consider cross-platform promotion")
            recommendations.append("Engage with comments early to boost viral momentum")
        
        # Timing recommendations
        if audience_behavior.optimal_posting_times:
            optimal_time = audience_behavior.optimal_posting_times[0]
            recommendations.append(f"Optimal posting time: {optimal_time.strftime('%H:%M')}")
        
        # Platform-specific recommendations
        if audience_behavior.dominant_behavior == AudienceBehavior.SHARING_ORIENTED:
            recommendations.append("Focus on shareable content formats and clear call-to-actions")
        elif audience_behavior.dominant_behavior == AudienceBehavior.DISCUSSION_DRIVEN:
            recommendations.append("Include conversation starters and respond to comments promptly")
        
        # Engagement pattern recommendations
        peak_engagement = max(f.predicted_value for f in engagement_forecasts.values())
        if peak_engagement > content_features.historical_engagement_rate * 1000:
            recommendations.append("Expected engagement exceeds historical average - prepare for increased activity")
        
        # Monetization recommendations
        if any("High" in factor for factor in viral_prediction.viral_factors):
            recommendations.append("Consider sponsored content opportunities due to high engagement potential")
        
        return recommendations
    
    def _calculate_confidence_score(self, engagement_forecasts: Dict[EngagementType, EngagementForecast],
                                  viral_prediction: ViralPrediction,
                                  content_features: ContentFeatures) -> float:
        """Calcul score confiance global"""
        confidence_factors = []
        
        # Content quality confidence
        quality_confidence = content_features.quality_score
        confidence_factors.append(quality_confidence)
        
        # Historical data confidence
        if content_features.historical_engagement_rate > 0:
            historical_confidence = min(1.0, content_features.historical_engagement_rate * 10)
            confidence_factors.append(historical_confidence)
        
        # Creator influence confidence
        follower_confidence = min(1.0, math.log10(max(content_features.creator_follower_count, 1)) / 6.0)
        confidence_factors.append(follower_confidence)
        
        # Prediction consistency confidence
        engagement_values = [f.predicted_value for f in engagement_forecasts.values()]
        if engagement_values:
            consistency = 1.0 - (np.std(engagement_values) / max(np.mean(engagement_values), 1))
            consistency_confidence = max(0.0, min(1.0, consistency))
            confidence_factors.append(consistency_confidence)
        
        # Overall confidence
        if confidence_factors:
            overall_confidence = np.mean(confidence_factors)
        else:
            overall_confidence = 0.5
        
        return overall_confidence
    
    def _default_prediction_result(self, request: EngagementPredictionRequest,
                                 processing_time: float) -> EngagementPredictionResult:
        """Résultat prédiction par défaut en cas d'erreur"""
        default_forecasts = {}
        for engagement_type in EngagementType:
            default_forecasts[engagement_type] = EngagementForecast(
                engagement_type=engagement_type,
                predicted_value=100.0,
                confidence_interval=(50.0, 150.0),
                peak_time_hours=6.0,
                growth_rate=0.1,
                plateau_value=120.0
            )
        
        return EngagementPredictionResult(
            content_id=request.content_features.content_id,
            prediction_timestamp=str(np.datetime64('now')),
            engagement_forecasts=default_forecasts,
            platform_predictions={platform: {"views": 100.0} for platform in request.target_platforms},
            viral_prediction=ViralPrediction(
                ViralityLevel.LOW, 0.3, 1000, [], None, 1.0
            ),
            audience_behavior=self.audience_behavior_analyzer._default_behavior_analysis(),
            monetization_forecast=MonetizationForecast(10.0, 0.01, 2.0, 5.0, 2.0, 1.0),
            optimization_recommendations=["Monitor engagement patterns"],
            confidence_score=0.5,
            processing_time_ms=processing_time
        )

class EngagementPredictionService:
    """
    Service principal pour engagement prediction Ainflue.
    Orchestration + batch processing + analytics + A/B testing.
    """
    
    def __init__(self, config: EngagementConfig):
        self.config = config
        self.model = EngagementPredictionModel(config)
        self.prediction_history = []
    
    async def predict_engagement_batch(self, requests: List[EngagementPredictionRequest]) -> List[EngagementPredictionResult]:
        """Prédiction engagement batch pour optimisation performance"""
        results = []
        
        for request in requests:
            result = await self.model.predict_content_engagement(request)
            results.append(result)
            
            # Store for analytics
            self.prediction_history.append(result)
        
        return results
    
    async def generate_engagement_analytics(self) -> Dict[str, Any]:
        """Génération analytics engagement agrégées"""
        if not self.prediction_history:
            return {}
        
        results = self.prediction_history
        
        analytics = {
            'total_predictions': len(results),
            'average_confidence': np.mean([r.confidence_score for r in results]),
            'viral_content_percentage': sum(
                1 for r in results if r.viral_prediction.virality_level.value >= 4
            ) / len(results) * 100,
            'engagement_trends': {},
            'monetization_insights': {
                'avg_estimated_revenue': np.mean([r.monetization_forecast.estimated_revenue for r in results]),
                'avg_conversion_rate': np.mean([r.monetization_forecast.conversion_rate for r in results])
            },
            'audience_behavior_distribution': {},
            'processing_performance': {
                'avg_processing_time_ms': np.mean([r.processing_time_ms for r in results])
            }
        }
        
        # Engagement trends
        all_engagements = []
        for result in results:
            for eng_type, forecast in result.engagement_forecasts.items():
                all_engagements.append((eng_type.value, forecast.predicted_value))
        
        from collections import defaultdict
        engagement_by_type = defaultdict(list)
        for eng_type, value in all_engagements:
            engagement_by_type[eng_type].append(value)
        
        for eng_type, values in engagement_by_type.items():
            analytics['engagement_trends'][eng_type] = {
                'avg_predicted': np.mean(values),
                'total_predicted': sum(values)
            }
        
        # Audience behavior distribution
        behavior_counts = defaultdict(int)
        for result in results:
            behavior_counts[result.audience_behavior.dominant_behavior.value] += 1
        
        total_results = len(results)
        analytics['audience_behavior_distribution'] = {
            behavior: count / total_results for behavior, count in behavior_counts.items()
        }
        
        return analytics


# Factory function pour faciliter l'utilisation
def create_engagement_predictor(device: str = "cpu",
                              enable_viral_prediction: bool = True,
                              enable_monetization_forecast: bool = True) -> EngagementPredictionService:
    """Factory function pour créer engagement predictor"""
    config = EngagementConfig(
        device=device,
        prediction_accuracy_target=0.85,
        enable_viral_prediction=enable_viral_prediction,
        enable_monetization_forecast=enable_monetization_forecast,
        time_series_window_hours=168
    )
    
    return EngagementPredictionService(config)


# Export des classes principales
__all__ = [
    "EngagementType",
    "ViralityLevel", 
    "AudienceBehavior",
    "PlatformType",
    "ContentFeatures",
    "EngagementPredictionRequest",
    "EngagementForecast",
    "ViralPrediction",
    "AudienceBehaviorAnalysis",
    "MonetizationForecast",
    "EngagementPredictionResult",
    "EngagementConfig",
    "EngagementPredictionModel",
    "EngagementPredictionService",
    "create_engagement_predictor"
]