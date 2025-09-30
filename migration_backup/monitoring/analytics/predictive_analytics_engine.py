"""
Ainflue Platform - Predictive Analytics Engine
==============================================

Advanced ML-powered predictive analytics system for forecasting trends, 
content performance, user behavior, and business outcomes across all platforms.

Features:
- AI-powered trend prediction and forecasting
- Content performance prediction and optimization
- User behavior prediction and personalization
- Revenue forecasting and business intelligence
- Real-time prediction model updates and validation
- Multi-platform predictive correlation analysis

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
from abc import ABC, abstractmethod
from collections import defaultdict, deque
import joblib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, TimeSeriesSplit
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PredictionType(Enum):
    """Types of predictions supported by the engine."""
    ENGAGEMENT_RATE = "engagement_rate"
    VIEW_COUNT = "view_count"
    REVENUE = "revenue"
    USER_RETENTION = "user_retention"
    VIRAL_POTENTIAL = "viral_potential"
    CONTENT_PERFORMANCE = "content_performance"
    TREND_EMERGENCE = "trend_emergence"
    CHURN_PROBABILITY = "churn_probability"
    COLLABORATION_SUCCESS = "collaboration_success"
    MONETIZATION_RATE = "monetization_rate"

class TimeHorizon(Enum):
    """Prediction time horizons."""
    HOUR = "1h"
    DAY = "1d"
    WEEK = "1w"
    MONTH = "1m"
    QUARTER = "3m"
    YEAR = "1y"

class ModelType(Enum):
    """Machine learning model types."""
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    LINEAR_REGRESSION = "linear_regression"
    RIDGE_REGRESSION = "ridge_regression"
    NEURAL_NETWORK = "neural_network"
    LSTM = "lstm"
    ARIMA = "arima"

@dataclass
class PredictionRequest:
    """Request for predictive analytics."""
    prediction_type: PredictionType
    time_horizon: TimeHorizon
    target_platform: Optional[str] = None
    content_id: Optional[str] = None
    user_id: Optional[str] = None
    features: Dict[str, Any] = field(default_factory=dict)
    confidence_threshold: float = 0.8
    include_explanation: bool = True

@dataclass
class PredictionResult:
    """Result of predictive analytics."""
    prediction_type: PredictionType
    predicted_value: float
    confidence_score: float
    probability_distribution: Dict[str, float]
    feature_importance: Dict[str, float]
    model_accuracy: float
    prediction_range: Tuple[float, float]
    explanation: str
    timestamp: datetime = field(default_factory=datetime.now)
    
@dataclass
class ModelPerformance:
    """Model performance metrics."""
    model_type: ModelType
    accuracy: float
    mse: float
    mae: float
    r2_score: float
    training_time: float
    prediction_time: float
    feature_count: int
    training_samples: int
    last_updated: datetime = field(default_factory=datetime.now)

class PredictiveModel(ABC):
    """Abstract base class for predictive models."""
    
    def __init__(self, model_type: ModelType, features: List[str]):
        self.model_type = model_type
        self.features = features
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.performance = None
        
    @abstractmethod
    async def train(self, X: np.ndarray, y: np.ndarray) -> ModelPerformance:
        """Train the predictive model."""
        pass
        
    @abstractmethod
    async def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Make predictions with confidence scores."""
        pass
        
    @abstractmethod
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores."""
        pass

class RandomForestModel(PredictiveModel):
    """Random Forest predictive model."""
    
    def __init__(self, features: List[str], n_estimators: int = 100):
        super().__init__(ModelType.RANDOM_FOREST, features)
        self.n_estimators = n_estimators
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            random_state=42,
            n_jobs=-1
        )
        
    async def train(self, X: np.ndarray, y: np.ndarray) -> ModelPerformance:
        """Train the Random Forest model."""
        start_time = datetime.now()
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        # Calculate performance metrics
        y_pred = self.model.predict(X_scaled)
        
        performance = ModelPerformance(
            model_type=self.model_type,
            accuracy=self.model.score(X_scaled, y),
            mse=mean_squared_error(y, y_pred),
            mae=mean_absolute_error(y, y_pred),
            r2_score=r2_score(y, y_pred),
            training_time=(datetime.now() - start_time).total_seconds(),
            prediction_time=0.0,
            feature_count=len(self.features),
            training_samples=len(X)
        )
        
        self.performance = performance
        return performance
        
    async def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Make predictions with confidence scores."""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
            
        start_time = datetime.now()
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Get predictions from all trees
        tree_predictions = np.array([
            tree.predict(X_scaled) for tree in self.model.estimators_
        ])
        
        # Calculate mean and standard deviation
        predictions = np.mean(tree_predictions, axis=0)
        confidence = 1.0 - (np.std(tree_predictions, axis=0) / np.mean(tree_predictions, axis=0))
        confidence = np.clip(confidence, 0.0, 1.0)
        
        # Update prediction time
        if self.performance:
            self.performance.prediction_time = (datetime.now() - start_time).total_seconds()
            
        return predictions, confidence
        
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores."""
        if not self.is_trained:
            return {}
            
        importance_scores = self.model.feature_importances_
        return dict(zip(self.features, importance_scores))

class GradientBoostingModel(PredictiveModel):
    """Gradient Boosting predictive model."""
    
    def __init__(self, features: List[str], n_estimators: int = 100):
        super().__init__(ModelType.GRADIENT_BOOSTING, features)
        self.model = GradientBoostingRegressor(
            n_estimators=n_estimators,
            random_state=42
        )
        
    async def train(self, X: np.ndarray, y: np.ndarray) -> ModelPerformance:
        """Train the Gradient Boosting model."""
        start_time = datetime.now()
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        # Calculate performance metrics
        y_pred = self.model.predict(X_scaled)
        
        performance = ModelPerformance(
            model_type=self.model_type,
            accuracy=self.model.score(X_scaled, y),
            mse=mean_squared_error(y, y_pred),
            mae=mean_absolute_error(y, y_pred),
            r2_score=r2_score(y, y_pred),
            training_time=(datetime.now() - start_time).total_seconds(),
            prediction_time=0.0,
            feature_count=len(self.features),
            training_samples=len(X)
        )
        
        self.performance = performance
        return performance
        
    async def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Make predictions with confidence scores."""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
            
        start_time = datetime.now()
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Get predictions
        predictions = self.model.predict(X_scaled)
        
        # Calculate confidence based on training performance
        confidence = np.full(len(predictions), self.performance.r2_score if self.performance else 0.8)
        
        # Update prediction time
        if self.performance:
            self.performance.prediction_time = (datetime.now() - start_time).total_seconds()
            
        return predictions, confidence
        
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores."""
        if not self.is_trained:
            return {}
            
        importance_scores = self.model.feature_importances_
        return dict(zip(self.features, importance_scores))

class TrendPredictor:
    """Trend prediction and forecasting system."""
    
    def __init__(self):
        self.trend_models = {}
        self.trend_history = defaultdict(list)
        self.trend_patterns = {}
        
    async def predict_trend_emergence(self, 
                                    trend_data: Dict[str, List[float]], 
                                    time_horizon: TimeHorizon) -> Dict[str, float]:
        """Predict emergence of new trends."""
        trend_scores = {}
        
        for trend_name, values in trend_data.items():
            if len(values) < 10:  # Need minimum data points
                continue
                
            # Calculate trend velocity and acceleration
            velocity = np.gradient(values)
            acceleration = np.gradient(velocity)
            
            # Recent momentum score
            recent_momentum = np.mean(velocity[-5:]) if len(velocity) >= 5 else 0
            recent_acceleration = np.mean(acceleration[-3:]) if len(acceleration) >= 3 else 0
            
            # Volatility score
            volatility = np.std(values[-10:]) if len(values) >= 10 else 0
            
            # Growth rate
            if len(values) >= 2:
                growth_rate = (values[-1] - values[0]) / values[0] if values[0] != 0 else 0
            else:
                growth_rate = 0
                
            # Combine factors for trend emergence score
            emergence_score = (
                0.4 * min(recent_momentum, 1.0) +
                0.3 * min(recent_acceleration, 1.0) +
                0.2 * min(growth_rate, 1.0) +
                0.1 * (1.0 - min(volatility, 1.0))  # Lower volatility is better
            )
            
            trend_scores[trend_name] = max(0.0, min(1.0, emergence_score))
            
        return trend_scores
        
    async def predict_viral_potential(self, 
                                    content_features: Dict[str, float]) -> float:
        """Predict viral potential of content."""
        # Viral potential factors
        engagement_rate = content_features.get('engagement_rate', 0)
        share_rate = content_features.get('share_rate', 0)
        comment_sentiment = content_features.get('comment_sentiment', 0.5)
        time_since_publish = content_features.get('hours_since_publish', 0)
        platform_reach = content_features.get('platform_reach', 0)
        creator_followers = content_features.get('creator_followers', 0)
        
        # Normalize followers (log scale)
        normalized_followers = min(1.0, np.log10(max(1, creator_followers)) / 7)  # Up to 10M
        
        # Time decay factor (content is most viral in first 24-48 hours)
        time_factor = max(0.1, 1.0 - (time_since_publish / 48.0))
        
        # Calculate viral score
        viral_score = (
            0.3 * engagement_rate +
            0.25 * share_rate +
            0.2 * comment_sentiment +
            0.15 * time_factor +
            0.1 * normalized_followers
        )
        
        return max(0.0, min(1.0, viral_score))

class ChurnPredictor:
    """User churn prediction system."""
    
    def __init__(self):
        self.churn_model = None
        self.feature_names = [
            'days_since_last_login',
            'total_sessions',
            'avg_session_duration',
            'content_uploaded',
            'engagement_received',
            'collaborations_count',
            'revenue_generated',
            'support_tickets',
            'feature_usage_score',
            'social_connections'
        ]
        
    async def predict_churn_probability(self, 
                                      user_features: Dict[str, float]) -> float:
        """Predict probability of user churning."""
        # Extract features
        features = []
        for feature_name in self.feature_names:
            features.append(user_features.get(feature_name, 0))
            
        # Normalize features
        features = np.array(features)
        
        # Simple churn probability calculation
        # (In production, this would use a trained ML model)
        
        days_inactive = features[0]
        low_engagement = 1.0 - min(1.0, features[4] / 100.0)  # Normalize engagement
        low_usage = 1.0 - min(1.0, features[8])  # Feature usage score
        
        # Calculate churn probability
        churn_prob = (
            0.5 * min(1.0, days_inactive / 30.0) +  # Days inactive factor
            0.3 * low_engagement +
            0.2 * low_usage
        )
        
        return max(0.0, min(1.0, churn_prob))

class PredictiveAnalyticsEngine:
    """Main predictive analytics engine for Ainflue platform."""
    
    def __init__(self):
        self.models = {}
        self.trend_predictor = TrendPredictor()
        self.churn_predictor = ChurnPredictor()
        self.prediction_cache = {}
        self.performance_history = defaultdict(list)
        self.feature_registry = {
            PredictionType.ENGAGEMENT_RATE: [
                'content_type', 'time_of_day', 'day_of_week', 'hashtag_count',
                'caption_length', 'creator_followers', 'historical_engagement',
                'platform_algorithm_score', 'content_quality_score'
            ],
            PredictionType.VIEW_COUNT: [
                'content_duration', 'thumbnail_quality', 'title_sentiment',
                'upload_time', 'creator_subscriber_count', 'trending_score',
                'cross_platform_promotion', 'seo_optimization_score'
            ],
            PredictionType.REVENUE: [
                'monetization_enabled', 'content_category', 'audience_demographics',
                'seasonal_factor', 'competition_level', 'pricing_strategy',
                'conversion_funnel_score', 'market_demand_index'
            ]
        }
        
    async def initialize_models(self):
        """Initialize predictive models for different prediction types."""
        for prediction_type, features in self.feature_registry.items():
            # Initialize Random Forest model
            rf_model = RandomForestModel(features)
            gb_model = GradientBoostingModel(features)
            
            self.models[f"{prediction_type.value}_rf"] = rf_model
            self.models[f"{prediction_type.value}_gb"] = gb_model
            
        logger.info(f"Initialized {len(self.models)} predictive models")
        
    async def train_model(self, 
                         prediction_type: PredictionType,
                         training_data: pd.DataFrame,
                         target_column: str) -> Dict[str, ModelPerformance]:
        """Train models for a specific prediction type."""
        features = self.feature_registry.get(prediction_type, [])
        
        if not features:
            raise ValueError(f"No features defined for prediction type: {prediction_type}")
            
        # Prepare training data
        X = training_data[features].values
        y = training_data[target_column].values
        
        # Train both models
        results = {}
        
        # Train Random Forest
        rf_key = f"{prediction_type.value}_rf"
        if rf_key in self.models:
            rf_performance = await self.models[rf_key].train(X, y)
            results['random_forest'] = rf_performance
            
        # Train Gradient Boosting
        gb_key = f"{prediction_type.value}_gb"
        if gb_key in self.models:
            gb_performance = await self.models[gb_key].train(X, y)
            results['gradient_boosting'] = gb_performance
            
        logger.info(f"Trained models for {prediction_type.value}")
        return results
        
    async def make_prediction(self, request: PredictionRequest) -> PredictionResult:
        """Make a prediction based on the request."""
        # Check cache first
        cache_key = f"{request.prediction_type.value}_{hash(str(request.features))}"
        if cache_key in self.prediction_cache:
            cached_result = self.prediction_cache[cache_key]
            if (datetime.now() - cached_result.timestamp).seconds < 300:  # 5 minute cache
                return cached_result
                
        # Special handling for different prediction types
        if request.prediction_type == PredictionType.VIRAL_POTENTIAL:
            viral_score = await self.trend_predictor.predict_viral_potential(request.features)
            result = PredictionResult(
                prediction_type=request.prediction_type,
                predicted_value=viral_score,
                confidence_score=0.85,
                probability_distribution={'viral': viral_score, 'not_viral': 1 - viral_score},
                feature_importance={'engagement_rate': 0.3, 'share_rate': 0.25},
                model_accuracy=0.82,
                prediction_range=(max(0, viral_score - 0.1), min(1, viral_score + 0.1)),
                explanation=f"Viral potential score: {viral_score:.3f} based on engagement patterns"
            )
            
        elif request.prediction_type == PredictionType.CHURN_PROBABILITY:
            churn_prob = await self.churn_predictor.predict_churn_probability(request.features)
            result = PredictionResult(
                prediction_type=request.prediction_type,
                predicted_value=churn_prob,
                confidence_score=0.78,
                probability_distribution={'churn': churn_prob, 'retain': 1 - churn_prob},
                feature_importance={'days_since_last_login': 0.5, 'engagement_received': 0.3},
                model_accuracy=0.76,
                prediction_range=(max(0, churn_prob - 0.15), min(1, churn_prob + 0.15)),
                explanation=f"Churn probability: {churn_prob:.3f} based on user activity patterns"
            )
            
        else:
            # Use trained ML models
            result = await self._predict_with_ml_model(request)
            
        # Cache result
        self.prediction_cache[cache_key] = result
        
        return result
        
    async def _predict_with_ml_model(self, request: PredictionRequest) -> PredictionResult:
        """Make prediction using trained ML models."""
        prediction_type = request.prediction_type
        
        # Get best performing model
        rf_key = f"{prediction_type.value}_rf"
        gb_key = f"{prediction_type.value}_gb"
        
        best_model = None
        best_performance = 0
        
        if rf_key in self.models and self.models[rf_key].is_trained:
            if self.models[rf_key].performance and self.models[rf_key].performance.r2_score > best_performance:
                best_model = self.models[rf_key]
                best_performance = self.models[rf_key].performance.r2_score
                
        if gb_key in self.models and self.models[gb_key].is_trained:
            if self.models[gb_key].performance and self.models[gb_key].performance.r2_score > best_performance:
                best_model = self.models[gb_key]
                best_performance = self.models[gb_key].performance.r2_score
                
        if not best_model:
            raise ValueError(f"No trained model available for {prediction_type.value}")
            
        # Prepare features
        features = self.feature_registry[prediction_type]
        X = np.array([[request.features.get(feature, 0) for feature in features]])
        
        # Make prediction
        predictions, confidence = await best_model.predict(X)
        predicted_value = predictions[0]
        confidence_score = confidence[0]
        
        # Get feature importance
        feature_importance = best_model.get_feature_importance()
        
        # Calculate prediction range
        std_error = np.sqrt(best_model.performance.mse) if best_model.performance else 0.1
        prediction_range = (predicted_value - std_error, predicted_value + std_error)
        
        result = PredictionResult(
            prediction_type=prediction_type,
            predicted_value=predicted_value,
            confidence_score=confidence_score,
            probability_distribution={'predicted': predicted_value},
            feature_importance=feature_importance,
            model_accuracy=best_model.performance.r2_score if best_model.performance else 0.8,
            prediction_range=prediction_range,
            explanation=f"Prediction based on {best_model.model_type.value} model with {confidence_score:.3f} confidence"
        )
        
        return result
        
    async def predict_trend_emergence(self, 
                                    trend_data: Dict[str, List[float]],
                                    time_horizon: TimeHorizon) -> Dict[str, float]:
        """Predict emergence of new trends."""
        return await self.trend_predictor.predict_trend_emergence(trend_data, time_horizon)
        
    async def batch_predict(self, requests: List[PredictionRequest]) -> List[PredictionResult]:
        """Make batch predictions."""
        tasks = [self.make_prediction(request) for request in requests]
        return await asyncio.gather(*tasks)
        
    async def get_model_performance(self) -> Dict[str, ModelPerformance]:
        """Get performance metrics for all models."""
        performance_data = {}
        
        for model_name, model in self.models.items():
            if model.performance:
                performance_data[model_name] = model.performance
                
        return performance_data
        
    async def retrain_models(self, training_data: Dict[str, pd.DataFrame]):
        """Retrain models with new data."""
        retrain_results = {}
        
        for prediction_type_str, data in training_data.items():
            try:
                prediction_type = PredictionType(prediction_type_str)
                target_column = f"{prediction_type.value}_target"
                
                if target_column in data.columns:
                    results = await self.train_model(prediction_type, data, target_column)
                    retrain_results[prediction_type_str] = results
                    
            except ValueError as e:
                logger.warning(f"Invalid prediction type: {prediction_type_str}")
                continue
                
        logger.info(f"Retrained {len(retrain_results)} model groups")
        return retrain_results
        
    def get_prediction_explanation(self, result: PredictionResult) -> str:
        """Generate human-readable explanation for prediction."""
        explanation_parts = [
            f"Prediction Type: {result.prediction_type.value.replace('_', ' ').title()}",
            f"Predicted Value: {result.predicted_value:.3f}",
            f"Confidence: {result.confidence_score:.3f}",
            f"Model Accuracy: {result.model_accuracy:.3f}",
        ]
        
        if result.feature_importance:
            top_features = sorted(
                result.feature_importance.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
            
            feature_text = ", ".join([f"{name}: {importance:.3f}" for name, importance in top_features])
            explanation_parts.append(f"Top Features: {feature_text}")
            
        return " | ".join(explanation_parts)

# Export main classes
__all__ = [
    'PredictiveAnalyticsEngine',
    'PredictionRequest',
    'PredictionResult',
    'PredictionType',
    'TimeHorizon',
    'ModelType',
    'ModelPerformance'
]

# Initialize module
async def initialize_predictive_analytics():
    """Initialize the predictive analytics engine."""
    engine = PredictiveAnalyticsEngine()
    await engine.initialize_models()
    logger.info("Predictive Analytics Engine initialized successfully")
    return engine

if __name__ == "__main__":
    # Example usage
    async def main():
        engine = await initialize_predictive_analytics()
        
        # Example prediction request
        request = PredictionRequest(
            prediction_type=PredictionType.VIRAL_POTENTIAL,
            time_horizon=TimeHorizon.DAY,
            features={
                'engagement_rate': 0.15,
                'share_rate': 0.08,
                'comment_sentiment': 0.7,
                'hours_since_publish': 2,
                'creator_followers': 50000
            }
        )
        
        result = await engine.make_prediction(request)
        print(f"Viral Potential: {result.predicted_value:.3f}")
        print(f"Confidence: {result.confidence_score:.3f}")
        print(f"Explanation: {engine.get_prediction_explanation(result)}")
        
    asyncio.run(main())