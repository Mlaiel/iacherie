"""Predictive Analytics Engine for IA Influencer Agent Platform
Advanced machine learning models for trend prediction and business forecasting.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution prohibited.

WARNING: This code is proprietary and confidential. Any unauthorized use,
copying, distribution, or reproduction is strictly prohibited and will be
prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing and collaboration inquiries.
"""
import asyncio
import logging
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Attention
from sqlalchemy.ext.asyncio import AsyncSession
import joblib
from concurrent.futures import ThreadPoolExecutor


class PredictionType(Enum):
    """Types of predictions available in the system."""
    REVENUE_FORECAST = "revenue_forecast"
    ENGAGEMENT_PREDICTION = "engagement_prediction"
    CONTENT_PERFORMANCE = "content_performance"
    USER_BEHAVIOR = "user_behavior"
    MARKET_TRENDS = "market_trends"
    CHURN_PREDICTION = "churn_prediction"
    VIRAL_POTENTIAL = "viral_potential"
    OPTIMAL_TIMING = "optimal_timing"
    COLLABORATION_SUCCESS = "collaboration_success"
    MONETIZATION_OPPORTUNITY = "monetization_opportunity"


@dataclass
class PredictionResult:
    """Prediction result data structure."""
    prediction_id: str
    prediction_type: PredictionType
    predicted_value: float
    confidence_score: float
    prediction_range: Tuple[float, float]
    time_horizon: int  # days
    features_used: List[str]
    model_version: str
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelPerformance:
    """Model performance metrics."""
    model_name: str
    accuracy: float
    mae: float
    mse: float
    r2_score: float
    training_samples: int
    last_trained: datetime
    feature_importance: Dict[str, float]


class PredictiveAnalytics:
    """
    Enterprise-grade predictive analytics engine using advanced machine learning
    for business forecasting, trend prediction, and intelligent insights.
    """
    
    def __init__(self, db_session: AsyncSession, model_storage_path: str = "./models"):
        self.db_session = db_session
        self.model_storage_path = model_storage_path
        self.logger = logging.getLogger(self.__class__.__name__)
        self.models = {}
        self.scalers = {}
        self.feature_columns = {}
        self.model_performance = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Model configurations
        self.model_configs = {
            PredictionType.REVENUE_FORECAST: {
                'model_type': 'lstm',
                'features': ['engagement_rate', 'content_count', 'user_growth', 'seasonality'],
                'sequence_length': 30,
                'prediction_horizon': 7
            },
            PredictionType.ENGAGEMENT_PREDICTION: {
                'model_type': 'random_forest',
                'features': ['content_type', 'posting_time', 'hashtag_count', 'user_followers'],
                'n_estimators': 100,
                'max_depth': 15
            },
            PredictionType.VIRAL_POTENTIAL: {
                'model_type': 'gradient_boosting',
                'features': ['content_quality_score', 'creator_influence', 'trend_alignment', 'timing_score'],
                'n_estimators': 150,
                'learning_rate': 0.1
            },
            PredictionType.CHURN_PREDICTION: {
                'model_type': 'lstm',
                'features': ['activity_level', 'engagement_trend', 'revenue_trend', 'support_interactions'],
                'sequence_length': 60,
                'prediction_horizon': 30
            }
        }
    
    async def initialize_models(self):
        """Initialize and load all predictive models."""
        try:
            self.logger.info("Initializing predictive analytics models")
            
            for prediction_type in PredictionType:
                await self._load_or_create_model(prediction_type)
            
            self.logger.info("All predictive models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing models: {str(e)}")
            raise
    
    async def generate_prediction(self, 
                                prediction_type: PredictionType,
                                input_data: Dict[str, Any],
                                time_horizon: int = 7) -> PredictionResult:
        """Generate a prediction using the specified model."""
        try:
            if prediction_type not in self.models:
                await self._load_or_create_model(prediction_type)
            
            # Prepare input features
            features = await self._prepare_features(prediction_type, input_data)
            
            # Generate prediction
            if self.model_configs[prediction_type]['model_type'] == 'lstm':
                prediction, confidence = await self._predict_with_lstm(prediction_type, features)
            else:
                prediction, confidence = await self._predict_with_sklearn(prediction_type, features)
            
            # Calculate prediction range based on confidence
            prediction_range = self._calculate_prediction_range(prediction, confidence)
            
            result = PredictionResult(
                prediction_id=f"pred_{int(datetime.utcnow().timestamp())}",
                prediction_type=prediction_type,
                predicted_value=prediction,
                confidence_score=confidence,
                prediction_range=prediction_range,
                time_horizon=time_horizon,
                features_used=list(features.keys()),
                model_version=self.models[prediction_type]['version'],
                created_at=datetime.utcnow(),
                metadata={'input_data': input_data}
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating prediction: {str(e)}")
            raise
    
    async def generate_revenue_forecast(self, 
                                      user_id: str,
                                      time_horizon: int = 30) -> Dict[str, Any]:
        """Generate comprehensive revenue forecast for a user."""
        try:
            # Gather historical data
            historical_data = await self._get_user_historical_data(user_id)
            
            # Generate daily predictions
            daily_forecasts = []
            for day in range(1, time_horizon + 1):
                prediction_input = {
                    'user_id': user_id,
                    'day_offset': day,
                    'historical_revenue': historical_data['revenue_trend'],
                    'engagement_trend': historical_data['engagement_trend'],
                    'content_schedule': historical_data['content_schedule']
                }
                
                prediction = await self.generate_prediction(
                    PredictionType.REVENUE_FORECAST,
                    prediction_input,
                    1
                )
                
                daily_forecasts.append({
                    'date': (datetime.utcnow() + timedelta(days=day)).date(),
                    'predicted_revenue': prediction.predicted_value,
                    'confidence': prediction.confidence_score,
                    'range_low': prediction.prediction_range[0],
                    'range_high': prediction.prediction_range[1]
                })
            
            # Calculate summary statistics
            total_forecast = sum(f['predicted_revenue'] for f in daily_forecasts)
            avg_confidence = np.mean([f['confidence'] for f in daily_forecasts])
            
            return {
                'user_id': user_id,
                'time_horizon_days': time_horizon,
                'total_predicted_revenue': total_forecast,
                'average_confidence': avg_confidence,
                'daily_forecasts': daily_forecasts,
                'trends': await self._analyze_forecast_trends(daily_forecasts),
                'recommendations': await self._generate_revenue_recommendations(daily_forecasts)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating revenue forecast: {str(e)}")
            return {}
    
    async def predict_content_performance(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict how well content will perform across multiple metrics."""
        try:
            predictions = {}
            
            # Predict engagement
            engagement_pred = await self.generate_prediction(
                PredictionType.ENGAGEMENT_PREDICTION,
                content_data
            )
            
            # Predict viral potential
            viral_pred = await self.generate_prediction(
                PredictionType.VIRAL_POTENTIAL,
                content_data
            )
            
            # Predict monetization opportunity
            monetization_pred = await self.generate_prediction(
                PredictionType.MONETIZATION_OPPORTUNITY,
                content_data
            )
            
            # Calculate overall performance score
            performance_score = self._calculate_overall_performance_score(
                engagement_pred.predicted_value,
                viral_pred.predicted_value,
                monetization_pred.predicted_value
            )
            
            return {
                'content_id': content_data.get('content_id'),
                'overall_performance_score': performance_score,
                'engagement_prediction': {
                    'predicted_engagement_rate': engagement_pred.predicted_value,
                    'confidence': engagement_pred.confidence_score,
                    'expected_likes': await self._estimate_likes(engagement_pred.predicted_value, content_data),
                    'expected_shares': await self._estimate_shares(engagement_pred.predicted_value, content_data)
                },
                'viral_potential': {
                    'viral_score': viral_pred.predicted_value,
                    'confidence': viral_pred.confidence_score,
                    'viral_probability': self._convert_to_probability(viral_pred.predicted_value)
                },
                'monetization_forecast': {
                    'predicted_revenue': monetization_pred.predicted_value,
                    'confidence': monetization_pred.confidence_score,
                    'revenue_range': monetization_pred.prediction_range
                },
                'optimization_suggestions': await self._generate_content_optimization_suggestions(content_data),
                'best_posting_time': await self._predict_optimal_posting_time(content_data)
            }
            
        except Exception as e:
            self.logger.error(f"Error predicting content performance: {str(e)}")
            return {}
    
    async def predict_user_churn(self, user_id: str) -> Dict[str, Any]:
        """Predict probability of user churn and provide retention insights."""
        try:
            # Get user behavioral data
            user_data = await self._get_user_behavior_data(user_id)
            
            # Generate churn prediction
            churn_pred = await self.generate_prediction(
                PredictionType.CHURN_PREDICTION,
                user_data
            )
            
            # Analyze churn factors
            churn_factors = await self._analyze_churn_factors(user_data)
            
            # Generate retention strategies
            retention_strategies = await self._generate_retention_strategies(
                churn_pred.predicted_value,
                churn_factors
            )
            
            return {
                'user_id': user_id,
                'churn_probability': churn_pred.predicted_value,
                'confidence': churn_pred.confidence_score,
                'risk_level': self._categorize_churn_risk(churn_pred.predicted_value),
                'key_factors': churn_factors,
                'retention_strategies': retention_strategies,
                'predicted_churn_date': await self._estimate_churn_date(churn_pred.predicted_value),
                'intervention_recommendations': await self._generate_intervention_recommendations(user_data)
            }
            
        except Exception as e:
            self.logger.error(f"Error predicting user churn: {str(e)}")
            return {}
    
    async def analyze_market_trends(self, industry: str, region: str = "global") -> Dict[str, Any]:
        """Analyze and predict market trends for content creators."""
        try:
            # Gather market data
            market_data = await self._get_market_data(industry, region)
            
            # Generate trend predictions
            trend_pred = await self.generate_prediction(
                PredictionType.MARKET_TRENDS,
                market_data
            )
            
            # Analyze emerging trends
            emerging_trends = await self._identify_emerging_trends(market_data)
            
            # Predict optimal content strategies
            content_strategies = await self._predict_optimal_strategies(market_data)
            
            return {
                'industry': industry,
                'region': region,
                'trend_score': trend_pred.predicted_value,
                'confidence': trend_pred.confidence_score,
                'market_outlook': self._categorize_market_outlook(trend_pred.predicted_value),
                'emerging_trends': emerging_trends,
                'content_strategies': content_strategies,
                'opportunity_score': await self._calculate_opportunity_score(market_data),
                'competitive_analysis': await self._analyze_competition(industry, region),
                'recommendations': await self._generate_market_recommendations(market_data)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing market trends: {str(e)}")
            return {}
    
    async def retrain_models(self, model_type: Optional[PredictionType] = None):
        """Retrain models with latest data."""
        try:
            models_to_retrain = [model_type] if model_type else list(PredictionType)
            
            for pred_type in models_to_retrain:
                self.logger.info(f"Retraining model for {pred_type.value}")
                
                # Get training data
                training_data = await self._get_training_data(pred_type)
                
                # Train model
                if self.model_configs[pred_type]['model_type'] == 'lstm':
                    model = await self._train_lstm_model(pred_type, training_data)
                else:
                    model = await self._train_sklearn_model(pred_type, training_data)
                
                # Evaluate model performance
                performance = await self._evaluate_model_performance(pred_type, model, training_data)
                
                # Save model if performance is acceptable
                if performance.accuracy > 0.7:  # Minimum accuracy threshold
                    await self._save_model(pred_type, model)
                    self.model_performance[pred_type] = performance
                    self.logger.info(f"Model {pred_type.value} retrained successfully with accuracy: {performance.accuracy:.3f}")
                else:
                    self.logger.warning(f"Model {pred_type.value} performance below threshold: {performance.accuracy:.3f}")
            
        except Exception as e:
            self.logger.error(f"Error retraining models: {str(e)}")
            raise
    
    async def get_model_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive model performance report."""
        try:
            report = {
                'generated_at': datetime.utcnow().isoformat(),
                'models': {},
                'overall_health': 'good',
                'recommendations': []
            }
            
            for pred_type, performance in self.model_performance.items():
                model_report = {
                    'accuracy': performance.accuracy,
                    'mae': performance.mae,
                    'mse': performance.mse,
                    'r2_score': performance.r2_score,
                    'training_samples': performance.training_samples,
                    'last_trained': performance.last_trained.isoformat(),
                    'feature_importance': performance.feature_importance,
                    'health_status': self._assess_model_health(performance)
                }
                
                report['models'][pred_type.value] = model_report
                
                # Add recommendations for underperforming models
                if performance.accuracy < 0.8:
                    report['recommendations'].append(
                        f"Consider retraining {pred_type.value} model - accuracy below optimal threshold"
                    )
            
            # Assess overall health
            avg_accuracy = np.mean([p.accuracy for p in self.model_performance.values()])
            if avg_accuracy < 0.7:
                report['overall_health'] = 'poor'
            elif avg_accuracy < 0.8:
                report['overall_health'] = 'fair'
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {str(e)}")
            return {}
    
    # Private helper methods
    
    async def _load_or_create_model(self, prediction_type: PredictionType):
        """Load existing model or create new one."""
        try:
            model_path = f"{self.model_storage_path}/{prediction_type.value}_model.pkl"
            
            try:
                # Try to load existing model
                with open(model_path, 'rb') as f:
                    self.models[prediction_type] = pickle.load(f)
                self.logger.info(f"Loaded existing model for {prediction_type.value}")
            except FileNotFoundError:
                # Create new model
                self.logger.info(f"Creating new model for {prediction_type.value}")
                await self._create_new_model(prediction_type)
                
        except Exception as e:
            self.logger.error(f"Error loading/creating model for {prediction_type.value}: {str(e)}")
            raise
    
    async def _create_new_model(self, prediction_type: PredictionType):
        """Create and train a new model."""
        try:
            # Get training data
            training_data = await self._get_training_data(prediction_type)
            
            # Create model based on type
            config = self.model_configs[prediction_type]
            
            if config['model_type'] == 'lstm':
                model = await self._create_lstm_model(prediction_type, training_data)
            elif config['model_type'] == 'random_forest':
                model = await self._create_random_forest_model(prediction_type, training_data)
            elif config['model_type'] == 'gradient_boosting':
                model = await self._create_gradient_boosting_model(prediction_type, training_data)
            else:
                model = await self._create_linear_model(prediction_type, training_data)
            
            # Save model
            await self._save_model(prediction_type, model)
            
        except Exception as e:
            self.logger.error(f"Error creating new model: {str(e)}")
            raise
    
    def _calculate_prediction_range(self, prediction: float, confidence: float) -> Tuple[float, float]:
        """Calculate prediction range based on confidence level."""
        margin = prediction * (1 - confidence) * 0.5
        return (max(0, prediction - margin), prediction + margin)
    
    def _calculate_overall_performance_score(self, engagement: float, viral: float, monetization: float) -> float:
        """Calculate overall content performance score."""
        # Weighted combination of different prediction scores
        weights = {'engagement': 0.4, 'viral': 0.3, 'monetization': 0.3}
        return (engagement * weights['engagement'] + 
                viral * weights['viral'] + 
                monetization * weights['monetization'])
    
    def _categorize_churn_risk(self, churn_probability: float) -> str:
        """Categorize churn risk level."""
        if churn_probability > 0.8:
            return "high"
        elif churn_probability > 0.5:
            return "medium"
        elif churn_probability > 0.3:
            return "low"
        else:
            return "very_low"
    
    def _assess_model_health(self, performance: ModelPerformance) -> str:
        """Assess model health based on performance metrics."""
        if performance.accuracy > 0.85:
            return "excellent"
        elif performance.accuracy > 0.75:
            return "good"
        elif performance.accuracy > 0.65:
            return "fair"
        else:
            return "poor"
