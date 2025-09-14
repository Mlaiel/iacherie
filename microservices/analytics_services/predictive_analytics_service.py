"""
Predictive Analytics Service module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
📋 PREDICTIVE ANALYTICS SERVICE
==============================

Advanced predictive analytics and machine learning service for the Ainflue platform.
Provides AI-powered forecasting, trend prediction, and intelligent insights.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.
"""

import asyncio
import logging
import time
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import uuid
import redis.asyncio as redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PredictionType(Enum):
    """Prediction type enumeration"""
    REVENUE_FORECAST = "revenue_forecast"
    ENGAGEMENT_PREDICTION = "engagement_prediction"
    GROWTH_TRAJECTORY = "growth_trajectory"
    TREND_ANALYSIS = "trend_analysis"
    CHURN_PREDICTION = "churn_prediction"
    CONTENT_PERFORMANCE = "content_performance"
    MARKET_ANALYSIS = "market_analysis"
    AUDIENCE_BEHAVIOR = "audience_behavior"

class ModelType(Enum):
    """ML model type enumeration"""
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    TIME_SERIES = "time_series"
    ENSEMBLE = "ensemble"

class PredictionHorizon(Enum):
    """Prediction time horizon"""
    SHORT_TERM = "1_week"
    MEDIUM_TERM = "1_month"
    LONG_TERM = "3_months"
    YEARLY = "1_year"

@dataclass
class PredictionRequest:
    """Prediction request definition"""
    id: str
    prediction_type: PredictionType
    model_type: ModelType
    horizon: PredictionHorizon
    features: Dict[str, Any]
    creator_id: Optional[str] = None
    platform: Optional[str] = None
    content_type: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class PredictionResult:
    """Prediction result"""
    id: str
    request_id: str
    prediction_value: float
    confidence_interval: Tuple[float, float]
    confidence_score: float
    model_accuracy: float
    feature_importance: Dict[str, float]
    insights: List[str]
    recommendations: List[str]
    created_at: datetime = None
    
    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class ModelMetrics:
    """ML model performance metrics"""
    model_id: str
    model_type: ModelType
    prediction_type: PredictionType
    accuracy: float
    mae: float  # Mean Absolute Error
    mse: float  # Mean Squared Error
    r2_score: float
    training_samples: int
    last_trained: datetime
    feature_count: int
    prediction_count: int = 0
    
    def __post_init__(self) -> None:
        if self.last_trained is None:
            self.last_trained = datetime.utcnow()

@dataclass
class AnalyticsMetrics:
    """Predictive analytics service metrics"""
    total_predictions: int = 0
    active_models: int = 0
    avg_accuracy: float = 0.0
    prediction_types: Dict[str, int] = None
    model_performance: Dict[str, float] = None
    
    def __post_init__(self) -> None:
        if self.prediction_types is None:
            self.prediction_types = {}
        if self.model_performance is None:
            self.model_performance = {}

class PredictiveAnalyticsService:
    """Enterprise predictive analytics service"""
    
    def __init__(self, redis_url -> None: str = "redis -> None://localhost -> None:6379") -> None:
        self.redis_url = redis_url
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.model_metrics: Dict[str, ModelMetrics] = {}
        self.prediction_cache: Dict[str, PredictionResult] = {}
        self.training_data: Dict[PredictionType, pd.DataFrame] = {}
        self.metrics = AnalyticsMetrics()
        self.running = False
        self.redis_client = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize models
        self._init_models()
        self._init_training_data()
    
    async def start(self) -> None:
        """Start the predictive analytics service"""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            self.running = True
            self.logger.info("🚀 Predictive Analytics Service started")
            
            # Start background tasks
            asyncio.create_task(self._model_retraining())
            asyncio.create_task(self._metrics_collector())
            asyncio.create_task(self._cache_cleanup())
            
        except Exception as e:
            self.logger.error(f"❌ Error starting predictive analytics service: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the predictive analytics service"""
        try:
            self.running = False
            if self.redis_client:
                await self.redis_client.close()
            
            self.logger.info("🛑 Predictive Analytics Service stopped")
            
        except Exception as e:
            self.logger.error(f"❌ Error stopping predictive analytics service: {e}")
    
    def _init_models(self) -> None:
        """Initialize ML models"""
        self.models = {
            ModelType.LINEAR_REGRESSION: LinearRegression(),
            ModelType.RANDOM_FOREST: RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            ),
            ModelType.GRADIENT_BOOSTING: GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
        }
        
        # Initialize scalers
        for model_type in self.models.keys():
            self.scalers[model_type] = StandardScaler()
    
    def _init_training_data(self) -> None:
        """Initialize synthetic training data for demonstration"""
        # Generate synthetic data for different prediction types
        np.random.seed(42)
        
        # Revenue forecast data
        dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
        revenue_data = []
        
        for i, date in enumerate(dates):
            base_revenue = 1000 + i * 0.5  # Growing trend
            seasonal = 200 * np.sin(2 * np.pi * i / 365)  # Yearly seasonality
            weekly = 100 * np.sin(2 * np.pi * i / 7)  # Weekly seasonality
            noise = np.random.normal(0, 50)
            
            revenue = max(0, base_revenue + seasonal + weekly + noise)
            
            revenue_data.append({
                'date': date,
                'revenue': revenue,
                'followers': 10000 + i * 10 + np.random.normal(0, 100),
                'engagement_rate': max(0.01, 0.05 + np.random.normal(0, 0.01)),
                'content_count': max(1, 10 + np.random.poisson(2)),
                'platform_score': min(100, max(1, 75 + np.random.normal(0, 10)))
            })
        
        self.training_data[PredictionType.REVENUE_FORECAST] = pd.DataFrame(revenue_data)
        
        # Engagement prediction data
        engagement_data = []
        for i in range(1000):
            followers = np.random.uniform(1000, 100000)
            content_quality = np.random.uniform(0.1, 1.0)
            posting_frequency = np.random.uniform(1, 10)
            optimal_time = np.random.choice([0, 1])  # Boolean for optimal posting time
            
            # Engagement formula (simplified)
            engagement = (
                followers * 0.0001 * content_quality * 
                (1.5 if optimal_time else 1.0) * 
                min(posting_frequency, 5) / 5 +
                np.random.normal(0, 100)
            )
            
            engagement_data.append({
                'followers': followers,
                'content_quality': content_quality,
                'posting_frequency': posting_frequency,
                'optimal_time': optimal_time,
                'engagement': max(0, engagement)
            })
        
        self.training_data[PredictionType.ENGAGEMENT_PREDICTION] = pd.DataFrame(engagement_data)
    
    async def create_prediction(
        self,
        prediction_type: PredictionType,
        features: Dict[str, Any],
        model_type: ModelType = ModelType.RANDOM_FOREST,
        horizon: PredictionHorizon = PredictionHorizon.MEDIUM_TERM,
        creator_id: Optional[str] = None
    ) -> str:
        """Create a new prediction request"""
        try:
            request_id = str(uuid.uuid4())
            
            request = PredictionRequest(
                id=request_id,
                prediction_type=prediction_type,
                model_type=model_type,
                horizon=horizon,
                features=features,
                creator_id=creator_id
            )
            
            # Process prediction
            result = await self._process_prediction(request)
            
            # Cache result
            self.prediction_cache[request_id] = result
            
            # Store in Redis
            if self.redis_client:
                await self.redis_client.setex(
                    f"prediction:{request_id}",
                    86400,  # 24 hours
                    json.dumps(asdict(result), default=str)
                )
            
            self.logger.info(f"✅ Created prediction {request_id} for {prediction_type.value}")
            return request_id
            
        except Exception as e:
            self.logger.error(f"❌ Error creating prediction: {e}")
            raise
    
    async def _process_prediction(self, request: PredictionRequest) -> PredictionResult:
        """Process prediction request"""
        try:
            model_key = f"{request.prediction_type}_{request.model_type}"
            
            # Train model if not exists or needs retraining
            if model_key not in self.models or await self._needs_retraining(model_key):
                await self._train_model(request.prediction_type, request.model_type)
            
            # Get model and scaler
            model = self.models.get(model_key)
            scaler = self.scalers.get(model_key)
            
            if not model or not scaler:
                raise ValueError(f"Model not available for {request.prediction_type}")
            
            # Prepare features
            feature_vector = self._prepare_features(request.features, request.prediction_type)
            feature_vector_scaled = scaler.transform([feature_vector])
            
            # Make prediction
            prediction = model.predict(feature_vector_scaled)[0]
            
            # Calculate confidence interval (simplified)
            if hasattr(model, 'predict_proba'):
                confidence_score = 0.85  # Simplified
            else:
                confidence_score = 0.80  # Default for regression
            
            margin = prediction * 0.15  # 15% margin
            confidence_interval = (prediction - margin, prediction + margin)
            
            # Get feature importance
            feature_importance = {}
            if hasattr(model, 'feature_importances_'):
                feature_names = self._get_feature_names(request.prediction_type)
                for i, importance in enumerate(model.feature_importances_):
                    if i < len(feature_names):
                        feature_importance[feature_names[i]] = float(importance)
            
            # Generate insights and recommendations
            insights, recommendations = self._generate_insights(
                request.prediction_type,
                prediction,
                request.features,
                feature_importance
            )
            
            # Get model metrics
            model_metrics = self.model_metrics.get(model_key)
            model_accuracy = model_metrics.accuracy if model_metrics else 0.8
            
            result = PredictionResult(
                id=str(uuid.uuid4()),
                request_id=request.id,
                prediction_value=float(prediction),
                confidence_interval=confidence_interval,
                confidence_score=confidence_score,
                model_accuracy=model_accuracy,
                feature_importance=feature_importance,
                insights=insights,
                recommendations=recommendations
            )
            
            # Update metrics
            self.metrics.total_predictions += 1
            if request.prediction_type.value not in self.metrics.prediction_types:
                self.metrics.prediction_types[request.prediction_type.value] = 0
            self.metrics.prediction_types[request.prediction_type.value] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error processing prediction: {e}")
            raise
    
    def _prepare_features(self, features: Dict[str, Any], prediction_type: PredictionType) -> List[float]:
        """Prepare features for model input"""
        if prediction_type == PredictionType.REVENUE_FORECAST:
            return [
                float(features.get('followers', 10000)),
                float(features.get('engagement_rate', 0.05)),
                float(features.get('content_count', 10)),
                float(features.get('platform_score', 75))
            ]
        elif prediction_type == PredictionType.ENGAGEMENT_PREDICTION:
            return [
                float(features.get('followers', 10000)),
                float(features.get('content_quality', 0.7)),
                float(features.get('posting_frequency', 3)),
                float(features.get('optimal_time', 0))
            ]
        else:
            # Generic feature extraction
            return [float(v) for v in features.values() if isinstance(v, (int, float))]
    
    def _get_feature_names(self, prediction_type: PredictionType) -> List[str]:
        """Get feature names for prediction type"""
        if prediction_type == PredictionType.REVENUE_FORECAST:
            return ['followers', 'engagement_rate', 'content_count', 'platform_score']
        elif prediction_type == PredictionType.ENGAGEMENT_PREDICTION:
            return ['followers', 'content_quality', 'posting_frequency', 'optimal_time']
        else:
            return ['feature_1', 'feature_2', 'feature_3', 'feature_4']
    
    def _generate_insights(
        self,
        prediction_type: PredictionType,
        prediction_value: float,
        features: Dict[str, Any],
        feature_importance: Dict[str, float]
    ) -> Tuple[List[str], List[str]]:
        """Generate insights and recommendations"""
        insights = []
        recommendations = []
        
        if prediction_type == PredictionType.REVENUE_FORECAST:
            if prediction_value > 5000:
                insights.append("Strong revenue growth trajectory predicted")
                recommendations.append("Consider expanding content production")
            elif prediction_value < 1000:
                insights.append("Revenue below expected threshold")
                recommendations.append("Focus on audience engagement strategies")
            
            # Feature-based insights
            if 'engagement_rate' in feature_importance and feature_importance['engagement_rate'] > 0.3:
                insights.append("Engagement rate is a key driver of revenue")
                recommendations.append("Prioritize content that drives engagement")
        
        elif prediction_type == PredictionType.ENGAGEMENT_PREDICTION:
            if prediction_value > 1000:
                insights.append("High engagement potential detected")
                recommendations.append("Optimize posting schedule for maximum reach")
            
            if features.get('content_quality', 0) < 0.5:
                insights.append("Content quality may be limiting engagement")
                recommendations.append("Invest in content production quality")
        
        # Generic insights
        top_feature = max(feature_importance.items(), key=lambda x: x[1]) if feature_importance else None
        if top_feature:
            insights.append(f"'{top_feature[0]}' is the most influential factor")
            recommendations.append(f"Focus on optimizing {top_feature[0]}")
        
        return insights, recommendations
    
    async def _train_model(self, prediction_type: PredictionType, model_type: ModelType) -> None:
        """Train ML model for specific prediction type"""
        try:
            training_data = self.training_data.get(prediction_type)
            if training_data is None or training_data.empty:
                self.logger.warning(f"No training data available for {prediction_type}")
                return
            
            model_key = f"{prediction_type}_{model_type}"
            
            # Prepare training data
            if prediction_type == PredictionType.REVENUE_FORECAST:
                X = training_data[['followers', 'engagement_rate', 'content_count', 'platform_score']]
                y = training_data['revenue']
            elif prediction_type == PredictionType.ENGAGEMENT_PREDICTION:
                X = training_data[['followers', 'content_quality', 'posting_frequency', 'optimal_time']]
                y = training_data['engagement']
            else:
                self.logger.warning(f"No training configuration for {prediction_type}")
                return
            
            # Split data (80/20)
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
            y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = self.models[model_type]
            model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test_scaled)
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            accuracy = max(0, 1 - mae / y_test.mean())  # Simplified accuracy
            
            # Store model and scaler
            self.models[model_key] = model
            self.scalers[model_key] = scaler
            
            # Store metrics
            self.model_metrics[model_key] = ModelMetrics(
                model_id=model_key,
                model_type=model_type,
                prediction_type=prediction_type,
                accuracy=accuracy,
                mae=mae,
                mse=mse,
                r2_score=r2,
                training_samples=len(X_train),
                feature_count=X_train.shape[1]
            )
            
            self.logger.info(f"✅ Trained model {model_key} - Accuracy: {accuracy:.3f}")
            
        except Exception as e:
            self.logger.error(f"❌ Error training model: {e}")
    
    async def _needs_retraining(self, model_key: str) -> bool:
        """Check if model needs retraining"""
        metrics = self.model_metrics.get(model_key)
        if not metrics:
            return True
        
        # Retrain if model is older than 24 hours or accuracy is low
        age = datetime.utcnow() - metrics.last_trained
        return age > timedelta(hours=24) or metrics.accuracy < 0.7
    
    async def get_prediction_result(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get prediction result by request ID"""
        try:
            result = self.prediction_cache.get(request_id)
            if result:
                return asdict(result)
            
            # Try Redis cache
            if self.redis_client:
                cached = await self.redis_client.get(f"prediction:{request_id}")
                if cached:
                    return json.loads(cached)
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error getting prediction result: {e}")
            return None
    
    async def get_model_performance(self) -> Dict[str, Dict[str, Any]]:
        """Get model performance metrics"""
        try:
            performance = {}
            for model_key, metrics in self.model_metrics.items():
                performance[model_key] = {
                    "accuracy": metrics.accuracy,
                    "mae": metrics.mae,
                    "mse": metrics.mse,
                    "r2_score": metrics.r2_score,
                    "training_samples": metrics.training_samples,
                    "prediction_count": metrics.prediction_count,
                    "last_trained": metrics.last_trained.isoformat()
                }
            
            return performance
            
        except Exception as e:
            self.logger.error(f"❌ Error getting model performance: {e}")
            return {}
    
    async def _model_retraining(self) -> None:
        """Background task for model retraining"""
        while self.running:
            try:
                for prediction_type in PredictionType:
                    for model_type in [ModelType.RANDOM_FOREST, ModelType.GRADIENT_BOOSTING]:
                        model_key = f"{prediction_type}_{model_type}"
                        if await self._needs_retraining(model_key):
                            await self._train_model(prediction_type, model_type)
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                self.logger.error(f"❌ Error in model retraining: {e}")
                await asyncio.sleep(300)
    
    async def _metrics_collector(self) -> None:
        """Collect service metrics"""
        while self.running:
            try:
                # Update metrics
                self.metrics.active_models = len(self.model_metrics)
                
                if self.model_metrics:
                    self.metrics.avg_accuracy = sum(m.accuracy for m in self.model_metrics.values()) / len(self.model_metrics)
                    
                    for model_key, metrics in self.model_metrics.items():
                        self.metrics.model_performance[model_key] = metrics.accuracy
                
                # Store in Redis
                if self.redis_client:
                    await self.redis_client.setex(
                        "predictive_analytics:metrics",
                        300,  # 5 minutes
                        json.dumps(asdict(self.metrics), default=str)
                    )
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                self.logger.error(f"❌ Error collecting metrics: {e}")
                await asyncio.sleep(60)
    
    async def _cache_cleanup(self) -> None:
        """Clean up old predictions from cache"""
        while self.running:
            try:
                current_time = datetime.utcnow()
                expired_predictions = []
                
                for request_id, result in self.prediction_cache.items():
                    if current_time - result.created_at > timedelta(hours=24):
                        expired_predictions.append(request_id)
                
                for request_id in expired_predictions:
                    del self.prediction_cache[request_id]
                
                if expired_predictions:
                    self.logger.info(f"🧹 Cleaned up {len(expired_predictions)} expired predictions")
                
                await asyncio.sleep(3600)  # Clean every hour
                
            except Exception as e:
                self.logger.error(f"❌ Error in cache cleanup: {e}")
                await asyncio.sleep(300)
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics"""
        return asdict(self.metrics)


# Example usage and testing
async def main() -> None:
    """Test the predictive analytics service"""
    service = PredictiveAnalyticsService()
    
    try:
        await service.start()
        
        # Create revenue forecast prediction
        revenue_prediction_id = await service.create_prediction(
            PredictionType.REVENUE_FORECAST,
            {
                "followers": 50000,
                "engagement_rate": 0.08,
                "content_count": 25,
                "platform_score": 85
            },
            ModelType.RANDOM_FOREST,
            PredictionHorizon.MEDIUM_TERM,
            "creator_123"
        )
        
        # Create engagement prediction
        engagement_prediction_id = await service.create_prediction(
            PredictionType.ENGAGEMENT_PREDICTION,
            {
                "followers": 25000,
                "content_quality": 0.8,
                "posting_frequency": 5,
                "optimal_time": 1
            },
            ModelType.GRADIENT_BOOSTING,
            PredictionHorizon.SHORT_TERM
        )
        
        # Get results
        revenue_result = await service.get_prediction_result(revenue_prediction_id)
        engagement_result = await service.get_prediction_result(engagement_prediction_id)
        
        print(f"Revenue Prediction: ${revenue_result['prediction_value']:.2f}")
        print(f"Engagement Prediction: {engagement_result['prediction_value']:.0f} interactions")
        
        # Get model performance
        performance = await service.get_model_performance()
        print(f"Model Performance: {len(performance)} models active")
        
        # Get metrics
        metrics = await service.get_metrics()
        print(f"Service Metrics: {metrics}")
        
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())