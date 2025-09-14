"""
Advanced Engagement Prediction Engine for Ainflue Distribution Platform

This module provides sophisticated ML-powered engagement prediction capabilities
for optimizing content distribution and maximizing audience engagement across platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import json
import hashlib

logger = logging.getLogger(__name__)


class EngagementType(Enum):
    """Types of engagement metrics"""
    VIEWS = "views"
    LIKES = "likes"
    COMMENTS = "comments"
    SHARES = "shares"
    SAVES = "saves"
    CLICKS = "clicks"
    WATCH_TIME = "watch_time"
    COMPLETION_RATE = "completion_rate"
    VIRAL_SCORE = "viral_score"


class PredictionTimeframe(Enum):
    """Timeframes for engagement predictions"""
    FIRST_HOUR = "first_hour"
    FIRST_DAY = "first_day"
    FIRST_WEEK = "first_week"
    FIRST_MONTH = "first_month"
    LIFETIME = "lifetime"


class ConfidenceLevel(Enum):
    """Confidence levels for predictions"""
    VERY_HIGH = 0.9
    HIGH = 0.8
    MEDIUM = 0.6
    LOW = 0.4
    VERY_LOW = 0.2


@dataclass
class EngagementPrediction:
    """Individual engagement prediction"""
    prediction_id: str
    content_id: str
    user_id: str
    platform: str
    engagement_type: EngagementType
    predicted_value: float
    confidence_score: float
    timeframe: PredictionTimeframe
    prediction_factors: Dict[str, float]
    uncertainty_range: Tuple[float, float]
    created_at: datetime
    model_version: str


@dataclass
class ComprehensiveEngagementForecast:
    """Complete engagement forecast for content"""
    content_id: str
    platform: str
    predictions: Dict[EngagementType, EngagementPrediction]
    overall_engagement_score: float
    viral_potential: float
    audience_match_score: float
    optimal_posting_time: datetime
    expected_reach: int
    peak_engagement_window: Tuple[datetime, datetime]
    risk_factors: List[str]
    optimization_recommendations: List[str]
    created_at: datetime


@dataclass
class EngagementFactor:
    """Factor influencing engagement predictions"""
    factor_name: str
    factor_type: str
    impact_score: float
    confidence: float
    description: str
    optimization_potential: float


class AdvancedEngagementPredictor:
    """
    AI-powered engagement prediction engine with ML models
    
    Features:
    - Multi-platform engagement prediction
    - Real-time model adaptation
    - Comprehensive factor analysis
    - Uncertainty quantification
    - Optimization recommendations
    - A/B testing integration
    """

    def __init__(self) -> None:
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_importance = {}
        self.model_performance = {}
        self.prediction_cache = {}
        self.training_data = []
        
        # Initialize models for different engagement types
        self._initialize_models()
        
    def _initialize_models(self) -> None:
        """Initialize ML models for different engagement types"""
        
        for engagement_type in EngagementType:
            # Use different models for different engagement types
            if engagement_type in [EngagementType.VIEWS, EngagementType.WATCH_TIME]:
                self.models[engagement_type] = GradientBoostingRegressor(
                    n_estimators=200, learning_rate=0.1, max_depth=6, random_state=42
                )
            else:
                self.models[engagement_type] = RandomForestRegressor(
                    n_estimators=100, max_depth=10, random_state=42
                )
            
            self.scalers[engagement_type] = StandardScaler()
            self.encoders[engagement_type] = {}

    async def predict_engagement(
        self,
        content_metadata: Dict[str, Any],
        user_profile: Dict[str, Any],
        platform: str,
        posting_context: Dict[str, Any],
        timeframe: PredictionTimeframe = PredictionTimeframe.FIRST_DAY
    ) -> ComprehensiveEngagementForecast:
        """
        Predict comprehensive engagement metrics for content
        
        Args:
            content_metadata: Content characteristics
            user_profile: User/creator profile
            platform: Target platform
            posting_context: Posting time and context
            timeframe: Prediction timeframe
            
        Returns:
            Complete engagement forecast
        """
        try:
            # Extract features for prediction
            features = await self._extract_prediction_features(
                content_metadata, user_profile, platform, posting_context
            )
            
            # Generate predictions for all engagement types
            predictions = {}
            for engagement_type in EngagementType:
                prediction = await self._predict_single_engagement(
                    engagement_type, features, timeframe, content_metadata.get('content_id', '')
                )
                predictions[engagement_type] = prediction
            
            # Calculate overall scores
            overall_score = await self._calculate_overall_engagement_score(predictions)
            viral_potential = await self._calculate_viral_potential(predictions, features)
            audience_match = await self._calculate_audience_match_score(features)
            
            # Find optimal posting time
            optimal_time = await self._find_optimal_posting_time(features, platform)
            
            # Calculate expected reach
            expected_reach = await self._calculate_expected_reach(predictions, features)
            
            # Identify peak engagement window
            peak_window = await self._identify_peak_engagement_window(optimal_time, features)
            
            # Identify risk factors
            risk_factors = await self._identify_risk_factors(features, predictions)
            
            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(
                predictions, features, risk_factors
            )
            
            return ComprehensiveEngagementForecast(
                content_id=content_metadata.get('content_id', ''),
                platform=platform,
                predictions=predictions,
                overall_engagement_score=overall_score,
                viral_potential=viral_potential,
                audience_match_score=audience_match,
                optimal_posting_time=optimal_time,
                expected_reach=expected_reach,
                peak_engagement_window=peak_window,
                risk_factors=risk_factors,
                optimization_recommendations=recommendations,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error predicting engagement: {e}")
            raise

    async def _extract_prediction_features(
        self,
        content_metadata: Dict[str, Any],
        user_profile: Dict[str, Any],
        platform: str,
        posting_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract comprehensive features for engagement prediction"""
        
        features = {}
        
        # Content features
        features.update(await self._extract_content_features(content_metadata))
        
        # Creator features
        features.update(await self._extract_creator_features(user_profile))
        
        # Platform features
        features.update(await self._extract_platform_features(platform))
        
        # Temporal features
        features.update(await self._extract_temporal_features(posting_context))
        
        # Contextual features
        features.update(await self._extract_contextual_features(posting_context))
        
        # Historical performance features
        features.update(await self._extract_historical_features(user_profile, platform))
        
        return features

    async def _extract_content_features(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract content-specific features"""
        
        features = {}
        
        # Content type and format
        features['content_type'] = metadata.get('type', 'unknown')
        features['content_format'] = metadata.get('format', 'unknown')
        features['duration'] = metadata.get('duration', 0)
        features['file_size'] = metadata.get('file_size', 0)
        features['resolution'] = metadata.get('resolution', 0)
        features['quality_score'] = metadata.get('quality_score', 0.5)
        
        # Content characteristics
        features['has_audio'] = 1 if metadata.get('has_audio') else 0
        features['has_text_overlay'] = 1 if metadata.get('has_text_overlay') else 0
        features['has_captions'] = 1 if metadata.get('has_captions') else 0
        features['has_music'] = 1 if metadata.get('has_music') else 0
        features['is_original'] = 1 if metadata.get('is_original') else 0
        
        # Visual features
        features['brightness_level'] = metadata.get('brightness', 0.5)
        features['contrast_level'] = metadata.get('contrast', 0.5)
        features['color_saturation'] = metadata.get('saturation', 0.5)
        features['face_count'] = metadata.get('face_count', 0)
        features['scene_complexity'] = metadata.get('scene_complexity', 0.5)
        
        # Content category and topics
        categories = metadata.get('categories', [])
        features['category_count'] = len(categories)
        features['primary_category'] = categories[0] if categories else 'unknown'
        
        topics = metadata.get('topics', [])
        features['topic_count'] = len(topics)
        features['topic_diversity'] = len(set(topics)) / max(len(topics), 1)
        
        # Hashtags and keywords
        hashtags = metadata.get('hashtags', [])
        features['hashtag_count'] = len(hashtags)
        features['trending_hashtag_count'] = sum(
            1 for tag in hashtags if metadata.get('trending_hashtags', {}).get(tag, 0) > 100
        )
        
        # Text analysis
        title = metadata.get('title', '')
        description = metadata.get('description', '')
        
        features['title_length'] = len(title)
        features['description_length'] = len(description)
        features['title_word_count'] = len(title.split())
        features['description_word_count'] = len(description.split())
        features['has_question_mark'] = 1 if '?' in title else 0
        features['has_exclamation'] = 1 if '!' in title else 0
        features['title_sentiment'] = self._analyze_text_sentiment(title)
        features['description_sentiment'] = self._analyze_text_sentiment(description)
        
        return features

    async def _extract_creator_features(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Extract creator-specific features"""
        
        features = {}
        
        # Creator profile metrics
        features['follower_count'] = user_profile.get('follower_count', 0)
        features['following_count'] = user_profile.get('following_count', 0)
        features['total_posts'] = user_profile.get('total_posts', 0)
        features['account_age_days'] = user_profile.get('account_age_days', 0)
        features['verification_status'] = 1 if user_profile.get('is_verified') else 0
        
        # Creator engagement history
        features['avg_likes_per_post'] = user_profile.get('avg_likes', 0)
        features['avg_comments_per_post'] = user_profile.get('avg_comments', 0)
        features['avg_shares_per_post'] = user_profile.get('avg_shares', 0)
        features['avg_engagement_rate'] = user_profile.get('avg_engagement_rate', 0)
        
        # Creator activity patterns
        features['posting_frequency'] = user_profile.get('posts_per_week', 0)
        features['consistent_posting'] = 1 if user_profile.get('consistent_schedule') else 0
        features['peak_posting_hour'] = user_profile.get('peak_posting_hour', 12)
        
        # Creator content patterns
        features['content_diversity'] = user_profile.get('content_type_diversity', 0.5)
        features['niche_focus'] = user_profile.get('niche_consistency', 0.5)
        features['collaboration_frequency'] = user_profile.get('collaboration_rate', 0)
        
        # Creator audience metrics
        features['audience_growth_rate'] = user_profile.get('follower_growth_rate', 0)
        features['audience_engagement_quality'] = user_profile.get('engagement_quality', 0.5)
        features['audience_loyalty_score'] = user_profile.get('loyalty_score', 0.5)
        
        return features

    async def _extract_platform_features(self, platform: str) -> Dict[str, Any]:
        """Extract platform-specific features"""
        
        features = {}
        
        # Platform characteristics
        platform_lower = platform.lower()
        features['platform'] = platform_lower
        
        # Platform-specific weights
        platform_weights = {
            'tiktok': {'video_weight': 1.0, 'short_form_weight': 1.0, 'trending_weight': 1.0},
            'instagram': {'image_weight': 0.8, 'story_weight': 0.9, 'reel_weight': 1.0},
            'youtube': {'video_weight': 1.0, 'long_form_weight': 1.0, 'quality_weight': 1.0},
            'facebook': {'image_weight': 0.7, 'video_weight': 0.8, 'text_weight': 0.6},
            'twitter': {'text_weight': 1.0, 'trending_weight': 1.0, 'real_time_weight': 1.0},
            'linkedin': {'professional_weight': 1.0, 'text_weight': 0.8, 'network_weight': 1.0}
        }
        
        weights = platform_weights.get(platform_lower, {})
        for weight_name, weight_value in weights.items():
            features[f'platform_{weight_name}'] = weight_value
        
        # Platform algorithm factors
        features['algorithm_favor_score'] = self._get_platform_algorithm_score(platform_lower)
        features['competition_level'] = self._get_platform_competition_level(platform_lower)
        features['discovery_potential'] = self._get_platform_discovery_potential(platform_lower)
        
        return features

    async def _extract_temporal_features(self, posting_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract temporal features for prediction"""
        
        features = {}
        
        posting_time = posting_context.get('posting_time', datetime.utcnow())
        if isinstance(posting_time, str):
            posting_time = datetime.fromisoformat(posting_time)
        
        # Time-based features
        features['hour_of_day'] = posting_time.hour
        features['day_of_week'] = posting_time.weekday()
        features['day_of_month'] = posting_time.day
        features['month'] = posting_time.month
        features['is_weekend'] = 1 if posting_time.weekday() >= 5 else 0
        features['is_holiday'] = 1 if self._is_holiday(posting_time) else 0
        
        # Peak time indicators
        features['is_prime_time'] = 1 if 19 <= posting_time.hour <= 22 else 0
        features['is_lunch_time'] = 1 if 11 <= posting_time.hour <= 14 else 0
        features['is_morning_commute'] = 1 if 7 <= posting_time.hour <= 9 else 0
        features['is_evening_commute'] = 1 if 17 <= posting_time.hour <= 19 else 0
        
        # Seasonal features
        features['season'] = self._get_season(posting_time)
        features['is_summer'] = 1 if features['season'] == 'summer' else 0
        features['is_winter'] = 1 if features['season'] == 'winter' else 0
        
        # Time since last post
        last_post_time = posting_context.get('last_post_time')
        if last_post_time:
            if isinstance(last_post_time, str):
                last_post_time = datetime.fromisoformat(last_post_time)
            time_diff = (posting_time - last_post_time).total_seconds() / 3600  # hours
            features['hours_since_last_post'] = time_diff
        else:
            features['hours_since_last_post'] = 24  # default
        
        return features

    async def _extract_contextual_features(self, posting_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract contextual features"""
        
        features = {}
        
        # Trending context
        features['trending_topic_relevance'] = posting_context.get('trending_relevance', 0)
        features['current_event_relevance'] = posting_context.get('event_relevance', 0)
        features['seasonal_relevance'] = posting_context.get('seasonal_relevance', 0)
        
        # Competition context
        features['competitor_activity_level'] = posting_context.get('competition_level', 0.5)
        features['market_saturation'] = posting_context.get('market_saturation', 0.5)
        
        # Audience context
        features['audience_online_ratio'] = posting_context.get('audience_online', 0.5)
        features['target_audience_activity'] = posting_context.get('target_activity', 0.5)
        
        # Campaign context
        features['is_part_of_campaign'] = 1 if posting_context.get('campaign_id') else 0
        features['campaign_momentum'] = posting_context.get('campaign_momentum', 0)
        
        return features

    async def _extract_historical_features(self, user_profile: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Extract historical performance features"""
        
        features = {}
        
        # Recent performance
        recent_posts = user_profile.get('recent_posts', [])
        if recent_posts:
            recent_engagement = [post.get('engagement_rate', 0) for post in recent_posts[-10:]]
            features['recent_avg_engagement'] = np.mean(recent_engagement)
            features['recent_engagement_trend'] = self._calculate_trend(recent_engagement)
            features['recent_performance_consistency'] = 1 - np.std(recent_engagement)
        else:
            features['recent_avg_engagement'] = 0
            features['recent_engagement_trend'] = 0
            features['recent_performance_consistency'] = 0
        
        # Platform-specific history
        platform_history = user_profile.get(f'{platform}_history', {})
        features['platform_avg_engagement'] = platform_history.get('avg_engagement', 0)
        features['platform_best_performance'] = platform_history.get('best_engagement', 0)
        features['platform_worst_performance'] = platform_history.get('worst_engagement', 0)
        features['platform_post_count'] = platform_history.get('total_posts', 0)
        
        return features

    async def _predict_single_engagement(
        self,
        engagement_type: EngagementType,
        features: Dict[str, Any],
        timeframe: PredictionTimeframe,
        content_id: str
    ) -> EngagementPrediction:
        """Predict a single engagement metric"""
        
        try:
            # Prepare features for model
            feature_vector = self._prepare_feature_vector(features, engagement_type)
            
            # Get model prediction
            model = self.models[engagement_type]
            
            if hasattr(model, 'predict'):
                # Use trained model if available
                prediction = model.predict([feature_vector])[0]
                confidence = self._calculate_prediction_confidence(
                    model, feature_vector, engagement_type
                )
            else:
                # Fallback to heuristic prediction
                prediction, confidence = self._heuristic_prediction(
                    engagement_type, features, timeframe
                )
            
            # Adjust prediction for timeframe
            prediction = self._adjust_prediction_for_timeframe(prediction, timeframe)
            
            # Calculate uncertainty range
            uncertainty_range = self._calculate_uncertainty_range(
                prediction, confidence, engagement_type
            )
            
            # Identify prediction factors
            prediction_factors = self._identify_prediction_factors(
                features, engagement_type
            )
            
            return EngagementPrediction(
                prediction_id=self._generate_prediction_id(content_id, engagement_type),
                content_id=content_id,
                user_id=features.get('creator_id', ''),
                platform=features.get('platform', ''),
                engagement_type=engagement_type,
                predicted_value=max(0, prediction),
                confidence_score=confidence,
                timeframe=timeframe,
                prediction_factors=prediction_factors,
                uncertainty_range=uncertainty_range,
                created_at=datetime.utcnow(),
                model_version="v1.0"
            )
            
        except Exception as e:
            logger.error(f"Error predicting {engagement_type}: {e}")
            raise

    def _prepare_feature_vector(self, features: Dict[str, Any], engagement_type: EngagementType) -> List[float]:
        """Prepare feature vector for ML model"""
        
        # Select relevant features for this engagement type
        relevant_features = self._get_relevant_features(engagement_type)
        
        vector = []
        for feature_name in relevant_features:
            value = features.get(feature_name, 0)
            
            # Handle categorical features
            if isinstance(value, str):
                # Use label encoding
                if feature_name not in self.encoders[engagement_type]:
                    self.encoders[engagement_type][feature_name] = LabelEncoder()
                    # Fit with common values (in real implementation, use training data)
                    self.encoders[engagement_type][feature_name].fit(['unknown', value])
                
                try:
                    value = self.encoders[engagement_type][feature_name].transform([value])[0]
                except:
                    value = 0  # Unknown category
            
            vector.append(float(value))
        
        return vector

    def _get_relevant_features(self, engagement_type: EngagementType) -> List[str]:
        """Get relevant features for specific engagement type"""
        
        # Base features used for all engagement types
        base_features = [
            'follower_count', 'avg_engagement_rate', 'content_quality_score',
            'hour_of_day', 'day_of_week', 'is_weekend', 'trending_relevance'
        ]
        
        # Engagement-specific features
        specific_features = {
            EngagementType.VIEWS: [
                'title_length', 'has_audio', 'duration', 'thumbnail_quality'
            ],
            EngagementType.LIKES: [
                'visual_appeal', 'sentiment_score', 'trending_hashtag_count'
            ],
            EngagementType.COMMENTS: [
                'has_question_mark', 'controversy_score', 'discussion_potential'
            ],
            EngagementType.SHARES: [
                'emotional_impact', 'viral_potential', 'shareability_score'
            ],
            EngagementType.WATCH_TIME: [
                'duration', 'content_quality', 'engagement_velocity'
            ]
        }
        
        return base_features + specific_features.get(engagement_type, [])

    def _heuristic_prediction(
        self,
        engagement_type: EngagementType,
        features: Dict[str, Any],
        timeframe: PredictionTimeframe
    ) -> Tuple[float, float]:
        """Heuristic prediction when ML model is not available"""
        
        base_prediction = 0
        confidence = 0.5
        
        # Base prediction on follower count and historical performance
        follower_count = features.get('follower_count', 0)
        avg_engagement = features.get('recent_avg_engagement', 0.05)
        
        if engagement_type == EngagementType.VIEWS:
            # Views typically 10-30% of followers for good content
            base_prediction = follower_count * 0.2 * (1 + avg_engagement)
            confidence = 0.6
            
        elif engagement_type == EngagementType.LIKES:
            # Likes typically 3-10% of views
            estimated_views = follower_count * 0.2
            base_prediction = estimated_views * 0.05 * (1 + avg_engagement)
            confidence = 0.7
            
        elif engagement_type == EngagementType.COMMENTS:
            # Comments typically 0.1-1% of views
            estimated_views = follower_count * 0.2
            base_prediction = estimated_views * 0.005 * (1 + avg_engagement)
            confidence = 0.5
            
        elif engagement_type == EngagementType.SHARES:
            # Shares typically 0.01-0.1% of views
            estimated_views = follower_count * 0.2
            base_prediction = estimated_views * 0.001 * (1 + avg_engagement)
            confidence = 0.4
        
        # Apply quality and context multipliers
        quality_multiplier = features.get('quality_score', 0.5) + 0.5
        timing_multiplier = 1.2 if features.get('is_prime_time', 0) else 0.8
        trending_multiplier = 1 + features.get('trending_topic_relevance', 0) * 0.5
        
        final_prediction = base_prediction * quality_multiplier * timing_multiplier * trending_multiplier
        
        return final_prediction, confidence

    def _adjust_prediction_for_timeframe(self, prediction: float, timeframe: PredictionTimeframe) -> float:
        """Adjust prediction based on timeframe"""
        
        timeframe_multipliers = {
            PredictionTimeframe.FIRST_HOUR: 0.3,
            PredictionTimeframe.FIRST_DAY: 0.8,
            PredictionTimeframe.FIRST_WEEK: 0.95,
            PredictionTimeframe.FIRST_MONTH: 0.98,
            PredictionTimeframe.LIFETIME: 1.0
        }
        
        return prediction * timeframe_multipliers.get(timeframe, 1.0)

    def _calculate_prediction_confidence(
        self,
        model: Any,
        feature_vector: List[float],
        engagement_type: EngagementType
    ) -> float:
        """Calculate confidence for model prediction"""
        
        # For tree-based models, use variance of predictions across trees
        if hasattr(model, 'estimators_'):
            predictions = []
            for estimator in model.estimators_[:10]:  # Sample first 10 trees
                try:
                    pred = estimator.predict([feature_vector])[0]
                    predictions.append(pred)
                except:
                    continue
            
            if predictions:
                std_dev = np.std(predictions)
                mean_pred = np.mean(predictions)
                # Convert coefficient of variation to confidence
                confidence = max(0.1, 1.0 - (std_dev / (mean_pred + 1)))
                return min(0.95, confidence)
        
        # Default confidence based on model performance
        return self.model_performance.get(engagement_type, 0.6)

    def _calculate_uncertainty_range(
        self,
        prediction: float,
        confidence: float,
        engagement_type: EngagementType
    ) -> Tuple[float, float]:
        """Calculate uncertainty range for prediction"""
        
        # Calculate range based on confidence
        uncertainty_factor = (1 - confidence) * 0.5
        
        lower_bound = prediction * (1 - uncertainty_factor)
        upper_bound = prediction * (1 + uncertainty_factor)
        
        return (max(0, lower_bound), upper_bound)

    def _identify_prediction_factors(
        self,
        features: Dict[str, Any],
        engagement_type: EngagementType
    ) -> Dict[str, float]:
        """Identify key factors influencing prediction"""
        
        factors = {}
        
        # Get feature importance if available
        if engagement_type in self.feature_importance:
            importance = self.feature_importance[engagement_type]
            relevant_features = self._get_relevant_features(engagement_type)
            
            for i, feature_name in enumerate(relevant_features):
                if i < len(importance):
                    factors[feature_name] = importance[i]
        else:
            # Default factor analysis
            if features.get('follower_count', 0) > 10000:
                factors['large_audience'] = 0.8
            if features.get('avg_engagement_rate', 0) > 0.1:
                factors['high_engagement_history'] = 0.7
            if features.get('is_prime_time', 0):
                factors['optimal_timing'] = 0.6
            if features.get('trending_topic_relevance', 0) > 0.5:
                factors['trending_relevance'] = 0.9
        
        return factors

    async def _calculate_overall_engagement_score(
        self,
        predictions: Dict[EngagementType, EngagementPrediction]
    ) -> float:
        """Calculate overall engagement score from individual predictions"""
        
        weights = {
            EngagementType.VIEWS: 0.2,
            EngagementType.LIKES: 0.25,
            EngagementType.COMMENTS: 0.2,
            EngagementType.SHARES: 0.3,
            EngagementType.SAVES: 0.05
        }
        
        weighted_score = 0
        total_weight = 0
        
        for eng_type, prediction in predictions.items():
            if eng_type in weights:
                # Normalize prediction value (0-1 scale)
                normalized_value = min(1.0, prediction.predicted_value / 1000)
                weight = weights[eng_type] * prediction.confidence_score
                
                weighted_score += normalized_value * weight
                total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0

    async def _calculate_viral_potential(
        self,
        predictions: Dict[EngagementType, EngagementPrediction],
        features: Dict[str, Any]
    ) -> float:
        """Calculate viral potential score"""
        
        viral_indicators = []
        
        # High share-to-view ratio indicates viral potential
        if EngagementType.SHARES in predictions and EngagementType.VIEWS in predictions:
            shares = predictions[EngagementType.SHARES].predicted_value
            views = predictions[EngagementType.VIEWS].predicted_value
            if views > 0:
                share_ratio = shares / views
                viral_indicators.append(min(1.0, share_ratio * 100))  # Scale up
        
        # Content factors for virality
        trending_score = features.get('trending_topic_relevance', 0)
        viral_indicators.append(trending_score)
        
        emotional_impact = features.get('emotional_impact', 0.5)
        viral_indicators.append(emotional_impact)
        
        shareability = features.get('shareability_score', 0.5)
        viral_indicators.append(shareability)
        
        # Timing factors
        if features.get('is_prime_time', 0):
            viral_indicators.append(0.8)
        
        return np.mean(viral_indicators) if viral_indicators else 0.0

    async def _calculate_audience_match_score(self, features: Dict[str, Any]) -> float:
        """Calculate how well content matches target audience"""
        
        match_indicators = []
        
        # Content-audience alignment
        content_relevance = features.get('audience_relevance', 0.5)
        match_indicators.append(content_relevance)
        
        # Demographic match
        demographic_match = features.get('demographic_alignment', 0.5)
        match_indicators.append(demographic_match)
        
        # Interest alignment
        interest_match = features.get('interest_alignment', 0.5)
        match_indicators.append(interest_match)
        
        # Platform-audience fit
        platform_fit = features.get('platform_audience_fit', 0.5)
        match_indicators.append(platform_fit)
        
        return np.mean(match_indicators)

    async def _find_optimal_posting_time(self, features: Dict[str, Any], platform: str) -> datetime:
        """Find optimal posting time based on predictions"""
        
        current_time = datetime.utcnow()
        
        # Platform-specific optimal hours
        optimal_hours = {
            'tiktok': [19, 20, 21],  # Evening hours
            'instagram': [11, 13, 17, 19],  # Lunch and evening
            'youtube': [14, 20, 21],  # Afternoon and evening
            'facebook': [13, 15, 18],  # Afternoon hours
            'twitter': [9, 12, 18],  # Morning, lunch, evening
            'linkedin': [8, 12, 17]  # Business hours
        }
        
        platform_hours = optimal_hours.get(platform.lower(), [19, 20, 21])
        
        # Find next optimal hour
        for hour in platform_hours:
            optimal_time = current_time.replace(hour=hour, minute=0, second=0, microsecond=0)
            if optimal_time <= current_time:
                optimal_time += timedelta(days=1)
            return optimal_time
        
        # Default to evening if no specific optimal time found
        return current_time.replace(hour=19, minute=0, second=0, microsecond=0)

    async def _calculate_expected_reach(
        self,
        predictions: Dict[EngagementType, EngagementPrediction],
        features: Dict[str, Any]
    ) -> int:
        """Calculate expected reach based on predictions"""
        
        if EngagementType.VIEWS in predictions:
            base_reach = int(predictions[EngagementType.VIEWS].predicted_value)
        else:
            # Estimate based on follower count
            follower_count = features.get('follower_count', 0)
            avg_reach_rate = features.get('avg_reach_rate', 0.1)
            base_reach = int(follower_count * avg_reach_rate)
        
        # Apply viral multiplier
        viral_potential = await self._calculate_viral_potential(predictions, features)
        viral_multiplier = 1 + viral_potential * 2  # Up to 3x reach for high viral potential
        
        return int(base_reach * viral_multiplier)

    async def _identify_peak_engagement_window(
        self,
        optimal_time: datetime,
        features: Dict[str, Any]
    ) -> Tuple[datetime, datetime]:
        """Identify peak engagement window around optimal posting time"""
        
        # Peak engagement typically lasts 2-4 hours after posting
        window_duration = 3  # hours
        
        window_start = optimal_time + timedelta(minutes=30)  # Slight delay for algorithm pickup
        window_end = window_start + timedelta(hours=window_duration)
        
        return (window_start, window_end)

    async def _identify_risk_factors(
        self,
        features: Dict[str, Any],
        predictions: Dict[EngagementType, EngagementPrediction]
    ) -> List[str]:
        """Identify potential risk factors for low engagement"""
        
        risks = []
        
        # Low confidence predictions
        low_confidence_types = [
            eng_type.value for eng_type, pred in predictions.items()
            if pred.confidence_score < 0.5
        ]
        if low_confidence_types:
            risks.append(f"Low prediction confidence for: {', '.join(low_confidence_types)}")
        
        # Timing risks
        if not features.get('is_prime_time', 0) and not features.get('audience_online_ratio', 0.5) > 0.3:
            risks.append("Posting outside peak audience activity hours")
        
        # Competition risks
        if features.get('competitor_activity_level', 0.5) > 0.7:
            risks.append("High competitor activity during posting time")
        
        # Content risks
        if features.get('content_quality_score', 0.5) < 0.6:
            risks.append("Below-average content quality score")
        
        # Audience mismatch
        if features.get('audience_relevance', 0.5) < 0.4:
            risks.append("Content may not align with audience interests")
        
        # Platform algorithm changes
        if features.get('algorithm_favor_score', 0.5) < 0.4:
            risks.append("Current content type not favored by platform algorithm")
        
        return risks

    async def _generate_optimization_recommendations(
        self,
        predictions: Dict[EngagementType, EngagementPrediction],
        features: Dict[str, Any],
        risk_factors: List[str]
    ) -> List[str]:
        """Generate optimization recommendations"""
        
        recommendations = []
        
        # Timing optimization
        if not features.get('is_prime_time', 0):
            recommendations.append("Consider posting during prime time hours (7-10 PM)")
        
        # Content optimization
        if features.get('content_quality_score', 0.5) < 0.7:
            recommendations.append("Improve content quality (better lighting, audio, editing)")
        
        # Engagement optimization
        if EngagementType.COMMENTS in predictions:
            comment_pred = predictions[EngagementType.COMMENTS]
            if comment_pred.predicted_value < 10:
                recommendations.append("Add engaging questions or call-to-action to increase comments")
        
        # Hashtag optimization
        if features.get('trending_hashtag_count', 0) < 2:
            recommendations.append("Include more trending hashtags relevant to your content")
        
        # Platform-specific optimization
        platform = features.get('platform', '')
        if platform == 'tiktok' and features.get('duration', 0) > 60:
            recommendations.append("Consider shorter content (15-30 seconds) for better TikTok performance")
        elif platform == 'youtube' and features.get('duration', 0) < 300:
            recommendations.append("Consider longer content (8+ minutes) for better YouTube monetization")
        
        # Viral potential optimization
        viral_potential = await self._calculate_viral_potential(predictions, features)
        if viral_potential > 0.7:
            recommendations.append("High viral potential detected - consider paid promotion to amplify reach")
        
        return recommendations

    # Helper methods
    def _analyze_text_sentiment(self, text: str) -> float:
        """Simple sentiment analysis (placeholder for more sophisticated analysis)"""
        positive_words = ['amazing', 'awesome', 'great', 'love', 'best', 'incredible', 'fantastic']
        negative_words = ['hate', 'terrible', 'awful', 'worst', 'bad', 'horrible']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count + negative_count == 0:
            return 0.5  # Neutral
        
        return positive_count / (positive_count + negative_count)

    def _get_platform_algorithm_score(self, platform: str) -> float:
        """Get platform algorithm favorability score"""
        # Placeholder scores - would be based on real platform analysis
        scores = {
            'tiktok': 0.8,  # Favors engagement and trends
            'instagram': 0.7,  # Favors reels and stories
            'youtube': 0.6,  # Favors watch time and CTR
            'facebook': 0.5,  # Organic reach limited
            'twitter': 0.7,  # Favors engagement and timing
            'linkedin': 0.6   # Favors professional content
        }
        return scores.get(platform, 0.5)

    def _get_platform_competition_level(self, platform: str) -> float:
        """Get platform competition level"""
        levels = {
            'tiktok': 0.9,  # Very high competition
            'instagram': 0.8,  # High competition
            'youtube': 0.7,  # Moderate-high competition
            'facebook': 0.6,  # Moderate competition
            'twitter': 0.7,  # Moderate-high competition
            'linkedin': 0.5   # Moderate competition
        }
        return levels.get(platform, 0.6)

    def _get_platform_discovery_potential(self, platform: str) -> float:
        """Get platform content discovery potential"""
        potentials = {
            'tiktok': 0.9,  # High discovery through FYP
            'instagram': 0.7,  # Good discovery through explore
            'youtube': 0.6,  # Moderate discovery through recommendations
            'facebook': 0.4,  # Limited organic discovery
            'twitter': 0.6,  # Moderate discovery through trends
            'linkedin': 0.5   # Moderate discovery through network
        }
        return potentials.get(platform, 0.5)

    def _is_holiday(self, date: datetime) -> bool:
        """Check if date is a major holiday"""
        # Simplified holiday detection
        major_holidays = [
            (1, 1),   # New Year
            (2, 14),  # Valentine's Day
            (12, 25), # Christmas
            (7, 4),   # July 4th (US)
            (10, 31)  # Halloween
        ]
        return (date.month, date.day) in major_holidays

    def _get_season(self, date: datetime) -> str:
        """Get season for given date"""
        month = date.month
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'fall'

    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend direction for a series of values"""
        if len(values) < 2:
            return 0.0
        
        # Simple linear trend
        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)
        
        # Normalize slope to [-1, 1] range
        return np.tanh(slope)

    def _generate_prediction_id(self, content_id: str, engagement_type: EngagementType) -> str:
        """Generate unique prediction ID"""
        combined = f"{content_id}_{engagement_type.value}_{datetime.utcnow().isoformat()}"
        return hashlib.md5(combined.encode()).hexdigest()[:16]

    async def train_models_with_data(self, training_data: List[Dict[str, Any]]) -> bool:
        """Train engagement prediction models with historical data"""
        
        try:
            if not training_data:
                logger.warning("No training data provided")
                return False
            
            # Process training data for each engagement type
            for engagement_type in EngagementType:
                type_data = [
                    item for item in training_data 
                    if item.get('engagement_type') == engagement_type.value
                ]
                
                if len(type_data) < 10:  # Minimum samples required
                    logger.warning(f"Insufficient data for {engagement_type}: {len(type_data)} samples")
                    continue
                
                # Prepare features and targets
                X = []
                y = []
                
                for item in type_data:
                    features = item.get('features', {})
                    target = item.get('actual_engagement', 0)
                    
                    feature_vector = self._prepare_feature_vector(features, engagement_type)
                    X.append(feature_vector)
                    y.append(target)
                
                if len(X) < 10:
                    continue
                
                X = np.array(X)
                y = np.array(y)
                
                # Scale features
                X_scaled = self.scalers[engagement_type].fit_transform(X)
                
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    X_scaled, y, test_size=0.2, random_state=42
                )
                
                # Train model
                model = self.models[engagement_type]
                model.fit(X_train, y_train)
                
                # Evaluate model
                y_pred = model.predict(X_test)
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                self.model_performance[engagement_type] = r2
                
                # Store feature importance
                if hasattr(model, 'feature_importances_'):
                    self.feature_importance[engagement_type] = model.feature_importances_
                
                logger.info(f"Trained {engagement_type} model: R2={r2:.3f}, MSE={mse:.3f}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            return False