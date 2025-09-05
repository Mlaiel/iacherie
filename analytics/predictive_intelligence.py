"""Predictive Intelligence
======================

Advanced predictive analytics engine with AI-powered forecasting.
Provides trend prediction, virality forecasting, and market opportunity analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
License: Proprietary - Unauthorized use prohibited

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import redis
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
import math


class PredictionType(Enum):
    """Types of predictions supported"""
    REVENUE_FORECAST = "revenue_forecast"
    ENGAGEMENT_PREDICTION = "engagement_prediction"
    VIRALITY_PREDICTION = "virality_prediction"
    GROWTH_PROJECTION = "growth_projection"
    TREND_ANALYSIS = "trend_analysis"
    MARKET_OPPORTUNITY = "market_opportunity"
    USER_BEHAVIOR = "user_behavior"
    CONTENT_PERFORMANCE = "content_performance"
    PLATFORM_OPTIMIZATION = "platform_optimization"
    COLLABORATION_SUCCESS = "collaboration_success"
    RISK_ASSESSMENT = "risk_assessment"
    SEASONAL_PATTERNS = "seasonal_patterns"


class TimeHorizon(Enum):
    """Prediction time horizons"""
    REAL_TIME = "real_time"      # Minutes to hours
    SHORT_TERM = "short_term"    # Days to weeks
    MEDIUM_TERM = "medium_term"  # Weeks to months
    LONG_TERM = "long_term"      # Months to years
    STRATEGIC = "strategic"       # Years


class ConfidenceLevel(Enum):
    """Prediction confidence levels"""
    VERY_HIGH = "very_high"    # 90%+
    HIGH = "high"              # 80-90%
    MEDIUM = "medium"          # 60-80%
    LOW = "low"                # 40-60%
    VERY_LOW = "very_low"      # <40%


@dataclass
class PredictionFeatures:
    """Features used for making predictions"""
    historical_data: Dict[str, List[float]]
    external_factors: Dict[str, Any] = field(default_factory=dict)
    seasonal_indicators: Dict[str, float] = field(default_factory=dict)
    trend_indicators: Dict[str, float] = field(default_factory=dict)
    market_conditions: Dict[str, float] = field(default_factory=dict)
    user_behavior_patterns: Dict[str, Any] = field(default_factory=dict)
    content_characteristics: Dict[str, Any] = field(default_factory=dict)
    platform_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class PredictionResult:
    """Result of a prediction analysis"""
    prediction_id: str
    prediction_type: PredictionType
    target_metric: str
    predicted_value: float
    confidence_level: ConfidenceLevel
    confidence_score: float
    time_horizon: TimeHorizon
    prediction_range: Tuple[float, float]  # min, max
    methodology: str
    feature_importance: Dict[str, float] = field(default_factory=dict)
    assumptions: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    model_accuracy: Optional[float] = None
    validation_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class TrendAnalysis:
    """Comprehensive trend analysis"""
    trend_id: str
    metric_name: str
    time_series_data: List[Tuple[datetime, float]]
    trend_direction: str  # "upward", "downward", "stable", "volatile"
    trend_strength: float  # 0-1
    seasonality_detected: bool
    seasonal_patterns: Dict[str, float] = field(default_factory=dict)
    growth_rate: float = 0.0
    acceleration: float = 0.0  # Rate of change of growth rate
    volatility: float = 0.0
    turning_points: List[datetime] = field(default_factory=list)
    forecast_points: List[Tuple[datetime, float]] = field(default_factory=list)
    anomalies: List[Tuple[datetime, float]] = field(default_factory=list)


@dataclass
class MarketOpportunity:
    """Market opportunity analysis"""
    opportunity_id: str
    opportunity_type: str
    market_segment: str
    potential_value: float
    probability_score: float
    time_to_market: int  # days
    investment_required: float
    roi_projection: float
    risk_level: str
    competitive_landscape: Dict[str, Any] = field(default_factory=dict)
    entry_barriers: List[str] = field(default_factory=list)
    success_factors: List[str] = field(default_factory=list)
    market_size: float = 0.0
    growth_potential: float = 0.0


@dataclass
class PredictiveIntelligenceMetrics:
    """Comprehensive predictive analytics metrics"""
    time_period: Tuple[datetime, datetime]
    total_predictions_made: int = 0
    predictions_by_type: Dict[str, int] = field(default_factory=dict)
    average_confidence_score: float = 0.0
    model_accuracy_scores: Dict[str, float] = field(default_factory=dict)
    successful_predictions: int = 0
    prediction_success_rate: float = 0.0
    trending_opportunities: List[MarketOpportunity] = field(default_factory=list)
    risk_assessments: Dict[str, float] = field(default_factory=dict)
    forecast_accuracy: Dict[str, float] = field(default_factory=dict)
    model_performance: Dict[str, Dict[str, float]] = field(default_factory=dict)


class PredictiveIntelligenceEngine:
    """
    Advanced predictive intelligence and forecasting analytics engine.
    
    Provides AI-powered predictions for revenue, engagement, virality,
    market opportunities, and strategic business insights.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Data storage
        self.prediction_results = deque(maxlen=100000)
        self.trend_analyses = deque(maxlen=50000)
        self.market_opportunities = deque(maxlen=10000)
        self.metrics_history = deque(maxlen=1000)
        
        # Historical data for training
        self.historical_data = defaultdict(list)
        
        # ML models for different prediction types
        self.prediction_models = {}
        self.model_scalers = {}
        
        # Redis for real-time predictions
        self.redis_client = None
        self._initialize_redis()
        
        # Model configurations
        self.model_configs = {
            PredictionType.REVENUE_FORECAST: {
                "model_class": GradientBoostingRegressor,
                "hyperparameters": {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 6},
                "features": ["historical_revenue", "engagement_rate", "user_growth", "seasonality"]
            },
            PredictionType.ENGAGEMENT_PREDICTION: {
                "model_class": RandomForestRegressor,
                "hyperparameters": {"n_estimators": 100, "max_depth": 8, "random_state": 42},
                "features": ["content_quality", "posting_time", "platform", "user_engagement_history"]
            },
            PredictionType.VIRALITY_PREDICTION: {
                "model_class": GradientBoostingRegressor,
                "hyperparameters": {"n_estimators": 150, "learning_rate": 0.05, "max_depth": 8},
                "features": ["early_engagement", "content_type", "trending_topics", "influencer_activity"]
            },
            PredictionType.GROWTH_PROJECTION: {
                "model_class": LinearRegression,
                "hyperparameters": {},
                "features": ["historical_growth", "market_trends", "user_acquisition", "retention_rate"]
            }
        }
        
        # External data sources for enhanced predictions
        self.external_factors = {
            "market_volatility": 0.3,
            "economic_indicators": {"gdp_growth": 2.5, "inflation": 3.2},
            "seasonal_factors": {"holiday_season": False, "summer_break": False},
            "competitive_landscape": {"new_competitors": 2, "market_share": 15.5},
            "technology_trends": {"ai_adoption": 0.8, "mobile_usage": 0.9}
        }
        
        # Initialize ML models
        self._ml_models_initialized = False
    
    def _initialize_redis(self):
        """Initialize Redis connection for real-time predictions"""
        try:
            redis_host = self.config.get("redis_host", "localhost")
            redis_port = self.config.get("redis_port", 6379)
            self.redis_client = redis.Redis(
                host=redis_host, 
                port=redis_port, 
                decode_responses=True
            )
        except Exception as e:
            self.logger.warning(f"Redis connection failed: {e}")
    
    async def _initialize_ml_models(self):
        """Initialize ML models for different prediction types"""
        try:
            if self._ml_models_initialized:
                return
            
            for prediction_type, config in self.model_configs.items():
                model_class = config["model_class"]
                hyperparameters = config["hyperparameters"]
                
                # Initialize model
                model = model_class(**hyperparameters)
                self.prediction_models[prediction_type] = model
                
                # Initialize scaler
                self.model_scalers[prediction_type] = StandardScaler()
            
            self._ml_models_initialized = True
            self.logger.info("Predictive intelligence ML models initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ML models: {e}")
    
    async def add_historical_data(
        self,
        metric_name: str,
        timestamp: datetime,
        value: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add historical data point for training models"""
        try:
            data_point = {
                "timestamp": timestamp,
                "value": value,
                "metadata": metadata or {}
            }
            
            self.historical_data[metric_name].append(data_point)
            
            # Keep only recent data (last 2 years)
            cutoff_date = datetime.now() - timedelta(days=730)
            self.historical_data[metric_name] = [
                point for point in self.historical_data[metric_name]
                if point["timestamp"] >= cutoff_date
            ]
            
            # Cache in Redis
            if self.redis_client:
                key = f"historical_data:{metric_name}"
                self.redis_client.lpush(key, json.dumps(data_point, default=str))
                self.redis_client.ltrim(key, 0, 10000)  # Keep last 10000 points
                self.redis_client.expire(key, 86400 * 365)  # 1 year expiry
            
        except Exception as e:
            self.logger.error(f"Error adding historical data: {e}")
    
    async def predict_revenue(
        self,
        time_horizon: TimeHorizon,
        target_date: Optional[datetime] = None,
        external_factors: Optional[Dict[str, Any]] = None
    ) -> PredictionResult:
        """Predict revenue for specified time horizon"""
        try:
            if not self._ml_models_initialized:
                await self._initialize_ml_models()
            
            target_date = target_date or self._get_target_date(time_horizon)
            
            # Prepare features
            features = await self._prepare_revenue_features(time_horizon, external_factors)
            
            # Make prediction
            model = self.prediction_models[PredictionType.REVENUE_FORECAST]
            scaler = self.model_scalers[PredictionType.REVENUE_FORECAST]
            
            # Train model if not already trained
            if not hasattr(model, 'feature_importances_'):
                await self._train_revenue_model(model, scaler)
            
            # Prepare feature vector
            feature_vector = await self._features_to_vector(features, PredictionType.REVENUE_FORECAST)
            
            if len(feature_vector) > 0:
                scaled_features = scaler.transform([feature_vector])
                predicted_value = model.predict(scaled_features)[0]
            else:
                # Fallback to simple trend-based prediction
                predicted_value = await self._simple_revenue_prediction(time_horizon)
            
            # Calculate confidence
            confidence_score, confidence_level = await self._calculate_prediction_confidence(
                PredictionType.REVENUE_FORECAST, features, predicted_value
            )
            
            # Calculate prediction range
            prediction_range = await self._calculate_prediction_range(predicted_value, confidence_score)
            
            # Generate recommendations
            recommendations = await self._generate_revenue_recommendations(predicted_value, features)
            
            # Get feature importance
            feature_importance = await self._get_feature_importance(model, features)
            
            prediction = PredictionResult(
                prediction_id=f"pred_{int(datetime.now().timestamp())}_{hash('revenue') % 10000}",
                prediction_type=PredictionType.REVENUE_FORECAST,
                target_metric="revenue",
                predicted_value=predicted_value,
                confidence_level=confidence_level,
                confidence_score=confidence_score,
                time_horizon=time_horizon,
                prediction_range=prediction_range,
                methodology="Gradient Boosting with external factors",
                feature_importance=feature_importance,
                assumptions=[
                    "Historical patterns continue",
                    "No major market disruptions",
                    "Current growth trends maintained"
                ],
                risk_factors=await self._identify_revenue_risks(features),
                recommendations=recommendations,
                model_accuracy=getattr(model, 'score_', None)
            )
            
            # Store prediction
            self.prediction_results.append(prediction)
            
            # Cache in Redis
            if self.redis_client:
                await self._cache_prediction(prediction)
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error predicting revenue: {e}")
            return self._create_fallback_prediction(PredictionType.REVENUE_FORECAST, time_horizon)
    
    async def predict_virality(
        self,
        content_id: str,
        content_metadata: Dict[str, Any],
        early_metrics: Optional[Dict[str, float]] = None
    ) -> PredictionResult:
        """Predict virality potential of content"""
        try:
            if not self._ml_models_initialized:
                await self._initialize_ml_models()
            
            # Prepare features for virality prediction
            features = await self._prepare_virality_features(content_id, content_metadata, early_metrics)
            
            # Make prediction
            model = self.prediction_models[PredictionType.VIRALITY_PREDICTION]
            scaler = self.model_scalers[PredictionType.VIRALITY_PREDICTION]
            
            # Train model if needed
            if not hasattr(model, 'feature_importances_'):
                await self._train_virality_model(model, scaler)
            
            # Prepare feature vector
            feature_vector = await self._features_to_vector(features, PredictionType.VIRALITY_PREDICTION)
            
            if len(feature_vector) > 0:
                scaled_features = scaler.transform([feature_vector])
                virality_score = model.predict(scaled_features)[0]
            else:
                # Fallback prediction
                virality_score = await self._simple_virality_prediction(content_metadata, early_metrics)
            
            # Convert to probability (0-1)
            virality_probability = min(1.0, max(0.0, virality_score))
            
            # Calculate confidence
            confidence_score, confidence_level = await self._calculate_prediction_confidence(
                PredictionType.VIRALITY_PREDICTION, features, virality_probability
            )
            
            # Calculate range
            prediction_range = await self._calculate_prediction_range(virality_probability, confidence_score)
            
            # Generate recommendations
            recommendations = await self._generate_virality_recommendations(virality_probability, features)
            
            prediction = PredictionResult(
                prediction_id=f"pred_{int(datetime.now().timestamp())}_{hash(content_id) % 10000}",
                prediction_type=PredictionType.VIRALITY_PREDICTION,
                target_metric="virality_probability",
                predicted_value=virality_probability,
                confidence_level=confidence_level,
                confidence_score=confidence_score,
                time_horizon=TimeHorizon.SHORT_TERM,
                prediction_range=prediction_range,
                methodology="Gradient Boosting with early engagement signals",
                feature_importance=await self._get_feature_importance(model, features),
                assumptions=[
                    "Current engagement patterns continue",
                    "No algorithm changes",
                    "Content remains accessible"
                ],
                risk_factors=await self._identify_virality_risks(features),
                recommendations=recommendations
            )
            
            self.prediction_results.append(prediction)
            
            if self.redis_client:
                await self._cache_prediction(prediction)
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error predicting virality: {e}")
            return self._create_fallback_prediction(PredictionType.VIRALITY_PREDICTION, TimeHorizon.SHORT_TERM)
    
    async def analyze_trends(
        self,
        metric_name: str,
        time_window_days: int = 90,
        forecast_days: int = 30
    ) -> TrendAnalysis:
        """Analyze trends and forecast future values"""
        try:
            # Get historical data
            historical_points = self.historical_data.get(metric_name, [])
            
            if len(historical_points) < 10:
                # Not enough data for trend analysis
                return TrendAnalysis(
                    trend_id=f"trend_{int(datetime.now().timestamp())}_{metric_name}",
                    metric_name=metric_name,
                    time_series_data=[],
                    trend_direction="insufficient_data",
                    trend_strength=0.0,
                    seasonality_detected=False
                )
            
            # Filter by time window
            cutoff_date = datetime.now() - timedelta(days=time_window_days)
            filtered_points = [
                point for point in historical_points
                if point["timestamp"] >= cutoff_date
            ]
            
            if len(filtered_points) < 5:
                return TrendAnalysis(
                    trend_id=f"trend_{int(datetime.now().timestamp())}_{metric_name}",
                    metric_name=metric_name,
                    time_series_data=[],
                    trend_direction="insufficient_recent_data",
                    trend_strength=0.0,
                    seasonality_detected=False
                )
            
            # Convert to time series
            time_series = [(point["timestamp"], point["value"]) for point in filtered_points]
            time_series.sort(key=lambda x: x[0])
            
            # Analyze trend direction and strength
            values = [point[1] for point in time_series]
            trend_direction, trend_strength = await self._analyze_trend_direction(values)
            
            # Calculate growth rate
            growth_rate = await self._calculate_growth_rate(values)
            
            # Calculate acceleration
            acceleration = await self._calculate_acceleration(values)
            
            # Calculate volatility
            volatility = await self._calculate_volatility(values)
            
            # Detect seasonality
            seasonality_detected, seasonal_patterns = await self._detect_seasonality(time_series)
            
            # Identify turning points
            turning_points = await self._identify_turning_points(time_series)
            
            # Detect anomalies
            anomalies = await self._detect_anomalies(time_series)
            
            # Generate forecast
            forecast_points = await self._generate_forecast(time_series, forecast_days)
            
            trend_analysis = TrendAnalysis(
                trend_id=f"trend_{int(datetime.now().timestamp())}_{metric_name}",
                metric_name=metric_name,
                time_series_data=time_series,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                seasonality_detected=seasonality_detected,
                seasonal_patterns=seasonal_patterns,
                growth_rate=growth_rate,
                acceleration=acceleration,
                volatility=volatility,
                turning_points=turning_points,
                forecast_points=forecast_points,
                anomalies=anomalies
            )
            
            self.trend_analyses.append(trend_analysis)
            
            return trend_analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing trends for {metric_name}: {e}")
            return TrendAnalysis(
                trend_id=f"trend_error_{int(datetime.now().timestamp())}",
                metric_name=metric_name,
                time_series_data=[],
                trend_direction="error",
                trend_strength=0.0,
                seasonality_detected=False
            )
    
    async def identify_market_opportunities(
        self,
        market_segment: Optional[str] = None,
        investment_budget: Optional[float] = None,
        risk_tolerance: str = "medium"
    ) -> List[MarketOpportunity]:
        """Identify and analyze market opportunities"""
        try:
            opportunities = []
            
            # Analyze different opportunity types
            opportunity_types = [
                "new_platform_expansion",
                "content_format_innovation",
                "audience_segment_targeting",
                "geographic_expansion",
                "technology_adoption",
                "partnership_opportunities"
            ]
            
            for opp_type in opportunity_types:
                opportunity = await self._analyze_opportunity_type(
                    opp_type, market_segment, investment_budget, risk_tolerance
                )
                if opportunity:
                    opportunities.append(opportunity)
            
            # Sort by potential value and probability
            opportunities.sort(
                key=lambda x: x.potential_value * x.probability_score,
                reverse=True
            )
            
            # Store top opportunities
            for opp in opportunities[:10]:
                self.market_opportunities.append(opp)
            
            return opportunities[:10]  # Return top 10
            
        except Exception as e:
            self.logger.error(f"Error identifying market opportunities: {e}")
            return []
    
    async def _analyze_opportunity_type(
        self,
        opportunity_type: str,
        market_segment: Optional[str],
        investment_budget: Optional[float],
        risk_tolerance: str
    ) -> Optional[MarketOpportunity]:
        """Analyze specific type of market opportunity"""
        try:
            if opportunity_type == "new_platform_expansion":
                return MarketOpportunity(
                    opportunity_id=f"opp_{int(datetime.now().timestamp())}_{opportunity_type}",
                    opportunity_type=opportunity_type,
                    market_segment="emerging_platforms",
                    potential_value=250000.0,
                    probability_score=0.7,
                    time_to_market=90,
                    investment_required=50000.0,
                    roi_projection=4.0,
                    risk_level="medium",
                    competitive_landscape={
                        "competitors": 3,
                        "market_saturation": 0.3,
                        "differentiation_potential": 0.8
                    },
                    entry_barriers=[
                        "Platform API access",
                        "Content adaptation required",
                        "Audience building needed"
                    ],
                    success_factors=[
                        "Early mover advantage",
                        "Strong content library",
                        "Community engagement"
                    ],
                    market_size=1000000.0,
                    growth_potential=0.6
                )
            
            elif opportunity_type == "content_format_innovation":
                return MarketOpportunity(
                    opportunity_id=f"opp_{int(datetime.now().timestamp())}_{opportunity_type}",
                    opportunity_type=opportunity_type,
                    market_segment="interactive_content",
                    potential_value=180000.0,
                    probability_score=0.6,
                    time_to_market=120,
                    investment_required=75000.0,
                    roi_projection=2.4,
                    risk_level="high",
                    competitive_landscape={
                        "competitors": 2,
                        "market_saturation": 0.2,
                        "differentiation_potential": 0.9
                    },
                    entry_barriers=[
                        "Technology development",
                        "User education required",
                        "Platform support needed"
                    ],
                    success_factors=[
                        "Innovative technology",
                        "User experience design",
                        "Marketing execution"
                    ],
                    market_size=500000.0,
                    growth_potential=0.8
                )
            
            # Add more opportunity types...
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error analyzing opportunity type {opportunity_type}: {e}")
            return None
    
    async def _prepare_revenue_features(
        self,
        time_horizon: TimeHorizon,
        external_factors: Optional[Dict[str, Any]]
    ) -> PredictionFeatures:
        """Prepare features for revenue prediction"""
        # Get historical revenue data
        revenue_data = self.historical_data.get("revenue", [])
        historical_revenue = [point["value"] for point in revenue_data[-30:]]  # Last 30 points
        
        # Get related metrics
        engagement_data = self.historical_data.get("engagement_rate", [])
        historical_engagement = [point["value"] for point in engagement_data[-30:]]
        
        user_growth_data = self.historical_data.get("user_count", [])
        historical_user_growth = [point["value"] for point in user_growth_data[-30:]]
        
        # Seasonal indicators
        now = datetime.now()
        seasonal_indicators = {
            "month": now.month,
            "quarter": (now.month - 1) // 3 + 1,
            "is_holiday_season": now.month in [11, 12],
            "is_summer": now.month in [6, 7, 8],
            "day_of_week": now.weekday()
        }
        
        # Market conditions
        market_conditions = {
            "economic_growth": self.external_factors["economic_indicators"]["gdp_growth"],
            "market_volatility": self.external_factors["market_volatility"],
            "competitive_pressure": self.external_factors["competitive_landscape"]["new_competitors"]
        }
        
        # External factors
        if external_factors:
            market_conditions.update(external_factors)
        
        return PredictionFeatures(
            historical_data={
                "revenue": historical_revenue,
                "engagement": historical_engagement,
                "user_growth": historical_user_growth
            },
            external_factors=external_factors or {},
            seasonal_indicators=seasonal_indicators,
            market_conditions=market_conditions
        )
    
    async def _prepare_virality_features(
        self,
        content_id: str,
        content_metadata: Dict[str, Any],
        early_metrics: Optional[Dict[str, float]]
    ) -> PredictionFeatures:
        """Prepare features for virality prediction"""
        # Early engagement signals
        historical_data = {}
        if early_metrics:
            historical_data["early_views"] = [early_metrics.get("views", 0)]
            historical_data["early_likes"] = [early_metrics.get("likes", 0)]
            historical_data["early_shares"] = [early_metrics.get("shares", 0)]
            historical_data["early_comments"] = [early_metrics.get("comments", 0)]
        
        # Content characteristics
        content_characteristics = {
            "content_type": content_metadata.get("type", "unknown"),
            "duration": content_metadata.get("duration", 0),
            "quality_score": content_metadata.get("quality_score", 0.5),
            "trending_topics": len(content_metadata.get("hashtags", [])),
            "creator_follower_count": content_metadata.get("creator_followers", 0)
        }
        
        # Timing factors
        now = datetime.now()
        external_factors = {
            "posting_hour": now.hour,
            "posting_day": now.weekday(),
            "is_weekend": now.weekday() >= 5,
            "is_peak_time": now.hour in [12, 18, 20, 21]
        }
        
        return PredictionFeatures(
            historical_data=historical_data,
            external_factors=external_factors,
            content_characteristics=content_characteristics
        )
    
    async def _train_revenue_model(self, model, scaler):
        """Train revenue prediction model"""
        try:
            # Get training data
            revenue_data = self.historical_data.get("revenue", [])
            
            if len(revenue_data) < 50:
                # Not enough data to train
                return
            
            # Prepare training data
            X, y = await self._prepare_training_data(revenue_data, "revenue")
            
            if len(X) > 0:
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                
                # Scale features
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                
                # Train model
                model.fit(X_train_scaled, y_train)
                
                # Evaluate model
                y_pred = model.predict(X_test_scaled)
                model.score_ = r2_score(y_test, y_pred)
                
                self.logger.info(f"Revenue model trained with R² score: {model.score_:.3f}")
            
        except Exception as e:
            self.logger.error(f"Error training revenue model: {e}")
    
    async def _train_virality_model(self, model, scaler):
        """Train virality prediction model"""
        try:
            # Get training data (simulated)
            # In production, would use actual virality data
            
            # Generate synthetic training data for demonstration
            X, y = await self._generate_synthetic_virality_data()
            
            if len(X) > 0:
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                
                # Scale features
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                
                # Train model
                model.fit(X_train_scaled, y_train)
                
                # Evaluate model
                y_pred = model.predict(X_test_scaled)
                model.score_ = r2_score(y_test, y_pred)
                
                self.logger.info(f"Virality model trained with R² score: {model.score_:.3f}")
            
        except Exception as e:
            self.logger.error(f"Error training virality model: {e}")
    
    async def _prepare_training_data(self, data_points: List[Dict], target_metric: str) -> Tuple[List[List[float]], List[float]]:
        """Prepare training data from historical points"""
        X, y = [], []
        
        for i in range(len(data_points) - 5):  # Need at least 5 points for features
            # Create features from previous points
            features = []
            
            # Historical values
            for j in range(5):
                features.append(data_points[i + j]["value"])
            
            # Time-based features
            timestamp = data_points[i + 5]["timestamp"]
            features.extend([
                timestamp.month,
                timestamp.weekday(),
                timestamp.hour if hasattr(timestamp, 'hour') else 12
            ])
            
            # Target value
            target = data_points[i + 5]["value"]
            
            X.append(features)
            y.append(target)
        
        return X, y
    
    async def _generate_synthetic_virality_data(self) -> Tuple[List[List[float]], List[float]]:
        """Generate synthetic training data for virality prediction"""
        X, y = [], []
        
        # Generate 1000 synthetic data points
        for _ in range(1000):
            # Features: early_views, early_likes, early_shares, content_quality, follower_count, posting_hour
            early_views = np.random.exponential(1000)
            early_likes = early_views * np.random.uniform(0.01, 0.1)
            early_shares = early_likes * np.random.uniform(0.1, 0.5)
            content_quality = np.random.uniform(0.3, 1.0)
            follower_count = np.random.exponential(10000)
            posting_hour = np.random.randint(0, 24)
            
            features = [early_views, early_likes, early_shares, content_quality, follower_count, posting_hour]
            
            # Virality score (0-1) based on features
            virality_score = (
                min(1.0, early_likes / early_views) * 0.3 +
                min(1.0, early_shares / early_likes) * 0.3 +
                content_quality * 0.2 +
                min(1.0, follower_count / 100000) * 0.1 +
                (1.0 if posting_hour in [12, 18, 20, 21] else 0.5) * 0.1
            )
            
            X.append(features)
            y.append(virality_score)
        
        return X, y
    
    async def _features_to_vector(self, features: PredictionFeatures, prediction_type: PredictionType) -> List[float]:
        """Convert features object to feature vector"""
        vector = []
        
        try:
            if prediction_type == PredictionType.REVENUE_FORECAST:
                # Add historical data
                if "revenue" in features.historical_data:
                    vector.extend(features.historical_data["revenue"][-5:])  # Last 5 values
                else:
                    vector.extend([0] * 5)
                
                # Add seasonal indicators
                vector.extend([
                    features.seasonal_indicators.get("month", 1),
                    features.seasonal_indicators.get("quarter", 1),
                    1 if features.seasonal_indicators.get("is_holiday_season", False) else 0
                ])
                
                # Add market conditions
                vector.extend([
                    features.market_conditions.get("economic_growth", 0),
                    features.market_conditions.get("market_volatility", 0)
                ])
            
            elif prediction_type == PredictionType.VIRALITY_PREDICTION:
                # Add early metrics
                vector.extend([
                    features.historical_data.get("early_views", [0])[0] if features.historical_data.get("early_views") else 0,
                    features.historical_data.get("early_likes", [0])[0] if features.historical_data.get("early_likes") else 0,
                    features.historical_data.get("early_shares", [0])[0] if features.historical_data.get("early_shares") else 0,
                    features.content_characteristics.get("quality_score", 0.5),
                    features.content_characteristics.get("creator_follower_count", 0),
                    features.external_factors.get("posting_hour", 12)
                ])
        
        except Exception as e:
            self.logger.error(f"Error converting features to vector: {e}")
            return []
        
        return vector
    
    async def _calculate_prediction_confidence(
        self,
        prediction_type: PredictionType,
        features: PredictionFeatures,
        predicted_value: float
    ) -> Tuple[float, ConfidenceLevel]:
        """Calculate confidence score and level for prediction"""
        try:
            confidence_factors = []
            
            # Data quality factor
            data_quality = 0.8  # Would be calculated based on actual data quality
            confidence_factors.append(data_quality)
            
            # Model accuracy factor
            model = self.prediction_models.get(prediction_type)
            if model and hasattr(model, 'score_'):
                model_accuracy = max(0, model.score_)
                confidence_factors.append(model_accuracy)
            else:
                confidence_factors.append(0.6)  # Default for untrained models
            
            # Feature completeness factor
            feature_completeness = 0.9  # Would calculate based on available features
            confidence_factors.append(feature_completeness)
            
            # External stability factor
            external_stability = 0.8  # Based on market conditions
            confidence_factors.append(external_stability)
            
            # Calculate overall confidence
            confidence_score = statistics.mean(confidence_factors)
            
            # Determine confidence level
            if confidence_score >= 0.9:
                confidence_level = ConfidenceLevel.VERY_HIGH
            elif confidence_score >= 0.8:
                confidence_level = ConfidenceLevel.HIGH
            elif confidence_score >= 0.6:
                confidence_level = ConfidenceLevel.MEDIUM
            elif confidence_score >= 0.4:
                confidence_level = ConfidenceLevel.LOW
            else:
                confidence_level = ConfidenceLevel.VERY_LOW
            
            return confidence_score, confidence_level
            
        except Exception as e:
            self.logger.error(f"Error calculating prediction confidence: {e}")
            return 0.5, ConfidenceLevel.MEDIUM
    
    async def _calculate_prediction_range(self, predicted_value: float, confidence_score: float) -> Tuple[float, float]:
        """Calculate prediction range based on confidence"""
        # Calculate margin of error based on confidence
        margin_factor = 1 - confidence_score
        margin = predicted_value * margin_factor * 0.5  # Max 50% margin
        
        min_value = max(0, predicted_value - margin)
        max_value = predicted_value + margin
        
        return (min_value, max_value)
    
    async def _get_feature_importance(self, model, features: PredictionFeatures) -> Dict[str, float]:
        """Get feature importance from trained model"""
        try:
            if hasattr(model, 'feature_importances_'):
                # For tree-based models
                feature_names = ["historical_1", "historical_2", "historical_3", "seasonal_1", "seasonal_2", "market_1"]
                importances = model.feature_importances_
                
                return dict(zip(feature_names[:len(importances)], importances))
            else:
                # Default importance
                return {
                    "historical_data": 0.4,
                    "seasonal_factors": 0.2,
                    "market_conditions": 0.2,
                    "external_factors": 0.2
                }
        except Exception as e:
            self.logger.error(f"Error getting feature importance: {e}")
            return {}
    
    async def _generate_revenue_recommendations(self, predicted_value: float, features: PredictionFeatures) -> List[str]:
        """Generate recommendations based on revenue prediction"""
        recommendations = []
        
        # Get current revenue trend
        historical_revenue = features.historical_data.get("revenue", [])
        if len(historical_revenue) >= 2:
            current_trend = historical_revenue[-1] - historical_revenue[-2] if len(historical_revenue) >= 2 else 0
            
            if current_trend > 0:
                recommendations.append("Maintain current growth strategies")
                recommendations.append("Consider scaling successful campaigns")
            else:
                recommendations.append("Review underperforming revenue streams")
                recommendations.append("Implement revenue optimization tactics")
        
        # Seasonal recommendations
        if features.seasonal_indicators.get("is_holiday_season", False):
            recommendations.append("Prepare for holiday season revenue boost")
            recommendations.append("Increase marketing spend during peak season")
        
        # Market condition recommendations
        if features.market_conditions.get("market_volatility", 0) > 0.5:
            recommendations.append("Diversify revenue streams to reduce risk")
            recommendations.append("Focus on stable, recurring revenue")
        
        return recommendations
    
    async def _generate_virality_recommendations(self, virality_score: float, features: PredictionFeatures) -> List[str]:
        """Generate recommendations for improving virality"""
        recommendations = []
        
        if virality_score < 0.3:
            recommendations.extend([
                "Improve content quality and engagement factor",
                "Optimize posting time for target audience",
                "Add trending hashtags and topics",
                "Encourage early engagement from loyal followers"
            ])
        elif virality_score < 0.7:
            recommendations.extend([
                "Amplify initial momentum with targeted promotion",
                "Engage actively with early commenters",
                "Cross-promote on other platforms",
                "Consider influencer collaboration"
            ])
        else:
            recommendations.extend([
                "Content has strong viral potential",
                "Prepare for scale and engagement management",
                "Monitor for potential issues or negative feedback",
                "Capitalize on momentum with follow-up content"
            ])
        
        return recommendations
    
    async def _identify_revenue_risks(self, features: PredictionFeatures) -> List[str]:
        """Identify risks for revenue prediction"""
        risks = []
        
        # Market volatility risk
        if features.market_conditions.get("market_volatility", 0) > 0.4:
            risks.append("High market volatility may impact revenue stability")
        
        # Competitive risk
        if features.market_conditions.get("competitive_pressure", 0) > 0.6:
            risks.append("Increased competition may reduce market share")
        
        # Seasonal risk
        if features.seasonal_indicators.get("is_summer", False):
            risks.append("Summer seasonality may reduce engagement")
        
        # Economic risk
        if features.market_conditions.get("economic_growth", 0) < 2.0:
            risks.append("Slow economic growth may impact spending")
        
        return risks
    
    async def _identify_virality_risks(self, features: PredictionFeatures) -> List[str]:
        """Identify risks for virality prediction"""
        risks = []
        
        # Content quality risk
        if features.content_characteristics.get("quality_score", 0) < 0.6:
            risks.append("Low content quality may limit viral potential")
        
        # Timing risk
        if not features.external_factors.get("is_peak_time", False):
            risks.append("Sub-optimal posting time may reduce visibility")
        
        # Creator reach risk
        if features.content_characteristics.get("creator_follower_count", 0) < 1000:
            risks.append("Limited initial reach may slow viral spread")
        
        return risks
    
    # Trend analysis methods
    async def _analyze_trend_direction(self, values: List[float]) -> Tuple[str, float]:
        """Analyze trend direction and strength"""
        if len(values) < 3:
            return "insufficient_data", 0.0
        
        # Calculate linear regression slope
        x = list(range(len(values)))
        slope = np.polyfit(x, values, 1)[0]
        
        # Calculate correlation coefficient for trend strength
        correlation = np.corrcoef(x, values)[0, 1] if len(values) > 1 else 0
        trend_strength = abs(correlation)
        
        # Determine direction
        if abs(slope) < 0.01:
            direction = "stable"
        elif slope > 0:
            direction = "upward"
        else:
            direction = "downward"
        
        return direction, trend_strength
    
    async def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calculate growth rate"""
        if len(values) < 2:
            return 0.0
        
        # Calculate compound growth rate
        start_value = values[0] if values[0] != 0 else 0.01
        end_value = values[-1]
        periods = len(values) - 1
        
        if start_value > 0 and end_value > 0 and periods > 0:
            growth_rate = (end_value / start_value) ** (1 / periods) - 1
            return growth_rate
        
        return 0.0
    
    async def _calculate_acceleration(self, values: List[float]) -> float:
        """Calculate acceleration (rate of change of growth rate)"""
        if len(values) < 4:
            return 0.0
        
        # Calculate growth rates for different periods
        mid_point = len(values) // 2
        early_growth = await self._calculate_growth_rate(values[:mid_point + 1])
        late_growth = await self._calculate_growth_rate(values[mid_point:])
        
        return late_growth - early_growth
    
    async def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility (standard deviation of returns)"""
        if len(values) < 2:
            return 0.0
        
        # Calculate returns
        returns = [(values[i] - values[i-1]) / values[i-1] for i in range(1, len(values)) if values[i-1] != 0]
        
        if returns:
            return statistics.stdev(returns)
        
        return 0.0
    
    async def _detect_seasonality(self, time_series: List[Tuple[datetime, float]]) -> Tuple[bool, Dict[str, float]]:
        """Detect seasonal patterns in time series"""
        if len(time_series) < 12:  # Need at least 12 points for seasonality
            return False, {}
        
        # Group by month
        monthly_values = defaultdict(list)
        for timestamp, value in time_series:
            month = timestamp.month
            monthly_values[month].append(value)
        
        # Calculate monthly averages
        monthly_averages = {}
        for month, values in monthly_values.items():
            if values:
                monthly_averages[month] = statistics.mean(values)
        
        # Check if there's significant variation
        if len(monthly_averages) >= 3:
            avg_values = list(monthly_averages.values())
            overall_mean = statistics.mean(avg_values)
            variation = statistics.stdev(avg_values) / overall_mean if overall_mean != 0 else 0
            
            seasonality_detected = variation > 0.1  # 10% threshold
            
            return seasonality_detected, monthly_averages
        
        return False, {}
    
    async def _identify_turning_points(self, time_series: List[Tuple[datetime, float]]) -> List[datetime]:
        """Identify significant turning points in time series"""
        if len(time_series) < 5:
            return []
        
        turning_points = []
        values = [point[1] for point in time_series]
        
        # Simple peak/valley detection
        for i in range(2, len(values) - 2):
            # Check for local maximum
            if values[i] > values[i-1] and values[i] > values[i+1] and values[i] > values[i-2] and values[i] > values[i+2]:
                turning_points.append(time_series[i][0])
            # Check for local minimum
            elif values[i] < values[i-1] and values[i] < values[i+1] and values[i] < values[i-2] and values[i] < values[i+2]:
                turning_points.append(time_series[i][0])
        
        return turning_points
    
    async def _detect_anomalies(self, time_series: List[Tuple[datetime, float]]) -> List[Tuple[datetime, float]]:
        """Detect anomalies in time series"""
        if len(time_series) < 10:
            return []
        
        values = [point[1] for point in time_series]
        
        # Calculate z-scores
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values) if len(values) > 1 else 0
        
        anomalies = []
        if std_val > 0:
            for i, (timestamp, value) in enumerate(time_series):
                z_score = abs(value - mean_val) / std_val
                if z_score > 2.5:  # 2.5 standard deviations
                    anomalies.append((timestamp, value))
        
        return anomalies
    
    async def _generate_forecast(self, time_series: List[Tuple[datetime, float]], forecast_days: int) -> List[Tuple[datetime, float]]:
        """Generate forecast points"""
        if len(time_series) < 3:
            return []
        
        values = [point[1] for point in time_series]
        
        # Simple linear trend forecast
        x = list(range(len(values)))
        slope, intercept = np.polyfit(x, values, 1)
        
        # Generate forecast points
        forecast_points = []
        last_timestamp = time_series[-1][0]
        
        for i in range(1, forecast_days + 1):
            forecast_date = last_timestamp + timedelta(days=i)
            forecast_value = slope * (len(values) + i - 1) + intercept
            forecast_points.append((forecast_date, max(0, forecast_value)))  # Ensure non-negative
        
        return forecast_points
    
    # Utility methods
    def _get_target_date(self, time_horizon: TimeHorizon) -> datetime:
        """Get target date based on time horizon"""
        now = datetime.now()
        
        if time_horizon == TimeHorizon.REAL_TIME:
            return now + timedelta(hours=1)
        elif time_horizon == TimeHorizon.SHORT_TERM:
            return now + timedelta(days=7)
        elif time_horizon == TimeHorizon.MEDIUM_TERM:
            return now + timedelta(days=90)
        elif time_horizon == TimeHorizon.LONG_TERM:
            return now + timedelta(days=365)
        elif time_horizon == TimeHorizon.STRATEGIC:
            return now + timedelta(days=1095)  # 3 years
        
        return now + timedelta(days=30)  # Default
    
    async def _simple_revenue_prediction(self, time_horizon: TimeHorizon) -> float:
        """Simple fallback revenue prediction"""
        # Get recent revenue data
        revenue_data = self.historical_data.get("revenue", [])
        
        if len(revenue_data) >= 3:
            recent_values = [point["value"] for point in revenue_data[-3:]]
            trend = recent_values[-1] - recent_values[0]
            
            # Project trend
            if time_horizon == TimeHorizon.SHORT_TERM:
                return recent_values[-1] + (trend * 0.5)
            elif time_horizon == TimeHorizon.MEDIUM_TERM:
                return recent_values[-1] + (trend * 2.0)
            elif time_horizon == TimeHorizon.LONG_TERM:
                return recent_values[-1] + (trend * 8.0)
        
        return 10000.0  # Default fallback
    
    async def _simple_virality_prediction(self, content_metadata: Dict[str, Any], early_metrics: Optional[Dict[str, float]]) -> float:
        """Simple fallback virality prediction"""
        score = 0.3  # Base score
        
        # Quality factor
        quality = content_metadata.get("quality_score", 0.5)
        score += quality * 0.3
        
        # Early engagement factor
        if early_metrics:
            views = early_metrics.get("views", 0)
            likes = early_metrics.get("likes", 0)
            
            if views > 0:
                engagement_rate = likes / views
                score += min(0.4, engagement_rate * 4)  # Cap at 0.4
        
        return min(1.0, score)
    
    def _create_fallback_prediction(self, prediction_type: PredictionType, time_horizon: TimeHorizon) -> PredictionResult:
        """Create fallback prediction when ML models fail"""
        return PredictionResult(
            prediction_id=f"fallback_{int(datetime.now().timestamp())}",
            prediction_type=prediction_type,
            target_metric=prediction_type.value,
            predicted_value=0.5,
            confidence_level=ConfidenceLevel.LOW,
            confidence_score=0.3,
            time_horizon=time_horizon,
            prediction_range=(0.0, 1.0),
            methodology="Fallback heuristic",
            assumptions=["Insufficient data for ML prediction"],
            risk_factors=["High uncertainty due to limited data"],
            recommendations=["Collect more historical data for better predictions"]
        )
    
    # Redis caching methods
    async def _cache_prediction(self, prediction: PredictionResult):
        """Cache prediction result in Redis"""
        if self.redis_client:
            try:
                key = f"prediction:{prediction.prediction_id}"
                data = {
                    "prediction_type": prediction.prediction_type.value,
                    "predicted_value": prediction.predicted_value,
                    "confidence_score": prediction.confidence_score,
                    "time_horizon": prediction.time_horizon.value,
                    "created_at": prediction.created_at.isoformat()
                }
                self.redis_client.hset(key, mapping=data)
                self.redis_client.expire(key, 86400)  # 24 hour expiry
            except Exception as e:
                self.logger.error(f"Redis cache error: {e}")
    
    def get_predictive_intelligence_summary(self) -> Dict[str, Any]:
        """Get summary of predictive intelligence system"""
        try:
            total_predictions = len(self.prediction_results)
            total_trends = len(self.trend_analyses)
            total_opportunities = len(self.market_opportunities)
            
            # Calculate accuracy for recent predictions
            recent_predictions = [p for p in self.prediction_results if (datetime.now() - p.created_at).days <= 30]
            avg_confidence = statistics.mean([p.confidence_score for p in recent_predictions]) if recent_predictions else 0
            
            # Count by prediction type
            predictions_by_type = defaultdict(int)
            for prediction in recent_predictions:
                predictions_by_type[prediction.prediction_type.value] += 1
            
            return {
                "system_stats": {
                    "total_predictions": total_predictions,
                    "total_trend_analyses": total_trends,
                    "total_market_opportunities": total_opportunities,
                    "ml_models_initialized": self._ml_models_initialized
                },
                "performance_metrics": {
                    "average_confidence_score": round(avg_confidence, 3),
                    "predictions_last_30_days": len(recent_predictions),
                    "redis_connected": self.redis_client is not None
                },
                "prediction_distribution": dict(predictions_by_type),
                "recent_activity": {
                    "predictions_today": len([
                        p for p in self.prediction_results 
                        if (datetime.now() - p.created_at).days == 0
                    ])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting predictive intelligence summary: {e}")
            return {"error": str(e)}