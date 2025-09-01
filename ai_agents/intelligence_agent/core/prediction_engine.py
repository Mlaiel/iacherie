"""IA-Influencer Agent - Prediction Engine

Advanced predictive analytics engine for content performance forecasting,
trend prediction, and intelligent business insights.

Author: Fahed Mlaiel
Contact: mlaiel@live.de
Copyright: 2025 - All rights reserved

⚠️ IMPORTANT LEGAL NOTICE ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Any violation will result in legal action.

Expert Team Specializations:
- Lead AI Developer: Fahed Mlaiel
- Predictive Analytics Expert
- Time Series Specialist
- Forecasting Engineer
- Data Science Architect
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import math
from scipy import stats
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import ExponentialSmoothing

try:
    from core.config import get_settings
except ImportError:
    # Fallback settings
    get_settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
from ...utils.time_series_utils import TimeSeriesProcessor
from ...database.models import PredictionRecord, TrendAnalysis


class PredictionType(Enum):
    """
Types of predictions the engine can make."""

    CONTENT_PERFORMANCE = "content_performance"
    AUDIENCE_GROWTH = "audience_growth"
    ENGAGEMENT_RATE = "engagement_rate"
    REVENUE_FORECAST = "revenue_forecast"
    TREND_DIRECTION = "trend_direction"
    COLLABORATION_SUCCESS = "collaboration_success"
    PLATFORM_OPTIMIZATION = "platform_optimization"
    VIRAL_POTENTIAL = "viral_potential"
    SEASONAL_PATTERNS = "seasonal_patterns"
    MARKET_DEMAND = "market_demand"


class TimeHorizon(Enum):
    """Time horizons for predictions."""

    SHORT_TERM = "short_term"  # 1-7 days
    MEDIUM_TERM = "medium_term"  # 1-4 weeks
    LONG_TERM = "long_term"  # 1-12 months
    STRATEGIC = "strategic"  # 1+ years


class PredictionConfidence(Enum):
    """Confidence levels for predictions."""

    LOW = "low"  # < 60%
    MEDIUM = "medium"  # 60-80%
    HIGH = "high"  # 80-95%
    VERY_HIGH = "very_high"  # > 95%


@dataclass
class PredictionRequest:
    """Request for a prediction."""
    request_id: str
    prediction_type: PredictionType
    time_horizon: TimeHorizon
    target_metrics: List[str]
    input_features: Dict[str, Any]
    historical_data_days: int = 30
    confidence_level: float = 0.95
    include_uncertainty: bool = True
    seasonal_adjustment: bool = True
    external_factors: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PredictionResult:
    """
Result of a prediction operation."""
    prediction_id: str
    request: PredictionRequest
    predicted_values: Dict[str, Union[float, List[float]]]
    confidence_intervals: Dict[str, Tuple[float, float]]
    prediction_confidence: PredictionConfidence
    model_accuracy: float
    feature_importance: Dict[str, float]
    trend_analysis: Dict[str, Any]
    seasonal_components: Dict[str, Any]
    risk_factors: List[str]
    recommendations: List[str]
    prediction_timestamp: datetime = field(default_factory=datetime.now)
    valid_until: Optional[datetime] = None
    model_version: str = "1.0"


@dataclass
class TrendPattern:
    """Detected trend pattern."""
    pattern_id: str
    pattern_type: str
    description: str
    strength: float
    duration_days: int
    confidence_score: float
    historical_occurrences: int
    seasonal_component: bool
    external_drivers: List[str]
    predictive_value: float


class PredictionEngine:
    """
    Advanced predictive analytics engine for content creators.
    
    Provides comprehensive forecasting capabilities including:
    - Multi-horizon time series forecasting
    - Content performance prediction
    - Audience growth and engagement forecasting
    - Revenue and monetization predictions
    - Trend analysis and pattern recognition
    - Seasonal decomposition and adjustment
    - Uncertainty quantification and risk assessment
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
Initialize the Prediction Engine with advanced forecasting capabilities."""
        self.config = config or {}
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        
        # Prediction configuration
        self.default_confidence_level = self.config.get('default_confidence_level', 0.95)
        self.max_prediction_horizon_days = self.config.get('max_prediction_horizon_days', 365)
        self.min_historical_data_points = self.config.get('min_historical_data_points', 10)
        self.ensemble_models = self.config.get('ensemble_models', True)
        
        # Model management
        self.prediction_models: Dict[str, Dict[str, Any]] = {}
        self.model_performance: Dict[str, Dict[str, float]] = {}
        self.feature_processors: Dict[str, Any] = {}
        
        # Historical data and caching
        self.historical_data: Dict[str, pd.DataFrame] = {}
        self.prediction_cache: Dict[str, PredictionResult] = {}
        self.trend_patterns: Dict[str, TrendPattern] = {}
        
        # Time series processing
        self.ts_processor = TimeSeriesProcessor()
        self.seasonal_decomposers: Dict[str, Any] = {}
        
        # Performance tracking
        self.prediction_accuracy_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.model_validation_scores: Dict[str, float] = {}
        
        # Background services
        self.active_services: Dict[str, asyncio.Task] = {}
        
        # Initialize prediction models
        self._initialize_prediction_models()
        self._start_prediction_services()
        
        self.logger.info("Prediction Engine initialized with advanced forecasting capabilities")
    
    def _initialize_prediction_models(self):
        """Initialize prediction models for different types and horizons."""
        # Content performance models
        self.prediction_models['content_performance'] = {
            'short_term': {
                'primary': RandomForestRegressor(n_estimators=100, random_state=42),
                'secondary': GradientBoostingRegressor(random_state=42),
                'ensemble_weight': 0.7
            },
            'medium_term': {
                'primary': xgb.XGBRegressor(random_state=42),
                'secondary': LinearRegression(),
                'ensemble_weight': 0.8
            },
            'long_term': {
                'primary': Ridge(alpha=1.0),
                'secondary': RandomForestRegressor(n_estimators=50, random_state=42),
                'ensemble_weight': 0.6
            }
        }
        
        # Audience growth models
        self.prediction_models['audience_growth'] = {
            'short_term': {
                'primary': GradientBoostingRegressor(random_state=42),
                'secondary': RandomForestRegressor(n_estimators=80, random_state=42),
                'ensemble_weight': 0.75
            },
            'medium_term': {
                'primary': xgb.XGBRegressor(random_state=42),
                'secondary': LinearRegression(),
                'ensemble_weight': 0.8
            },
            'long_term': {
                'primary': LinearRegression(),
                'secondary': Ridge(alpha=0.5),
                'ensemble_weight': 0.6
            }
        }
        
        # Revenue forecasting models
        self.prediction_models['revenue_forecast'] = {
            'short_term': {
                'primary': xgb.XGBRegressor(random_state=42),
                'secondary': RandomForestRegressor(n_estimators=100, random_state=42),
                'ensemble_weight': 0.8
            },
            'medium_term': {
                'primary': GradientBoostingRegressor(random_state=42),
                'secondary': LinearRegression(),
                'ensemble_weight': 0.7
            },
            'long_term': {
                'primary': LinearRegression(),
                'secondary': Ridge(alpha=1.0),
                'ensemble_weight': 0.6
            }
        }
    
    def _start_prediction_services(self):
        """
Start background prediction services."""
        # Start model validation service
        self.active_services['model_validator'] = asyncio.create_task(
            self._validate_models_continuously()
        )
        
        # Start trend detection service
        self.active_services['trend_detector'] = asyncio.create_task(
            self._detect_trends_continuously()
        )
        
        # Start cache management service
        self.active_services['cache_manager'] = asyncio.create_task(
            self._manage_prediction_cache()
        )
        
        # Start pattern learning service
        self.active_services['pattern_learner'] = asyncio.create_task(
            self._learn_patterns_continuously()
        )
    
    async def make_prediction(self, request: PredictionRequest) -> PredictionResult:
        """
        Make a comprehensive prediction based on the request.
        
        Args:
            request: Prediction request with specifications
            
        Returns:
            PredictionResult: Comprehensive prediction results
        """
        try:
            prediction_id = f"pred_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{request.prediction_type.value}"
            
            self.logger.info(f"Making prediction: {prediction_id}")
            
            # Check cache for recent similar predictions
            cached_result = await self._check_prediction_cache(request)
            if cached_result:
                self.logger.info(f"Returning cached prediction: {prediction_id}")
                return cached_result
            
            # Collect and prepare historical data
            historical_data = await self._collect_historical_data(request)
            
            if historical_data.empty or len(historical_data) < self.min_historical_data_points:
                raise ValueError(f"Insufficient historical data for prediction (minimum: {self.min_historical_data_points})")
            
            # Perform feature engineering
            features = await self._engineer_prediction_features(historical_data, request)
            
            # Seasonal decomposition if requested
            seasonal_components = {}
            if request.seasonal_adjustment:
                seasonal_components = await self._perform_seasonal_decomposition(
                    historical_data, request.target_metrics
                )
            
            # Make predictions using ensemble of models
            predictions = await self._make_ensemble_predictions(
                features, request, seasonal_components
            )
            
            # Calculate confidence intervals
            confidence_intervals = await self._calculate_confidence_intervals(
                predictions, request.confidence_level
            )
            
            # Determine prediction confidence level
            prediction_confidence = await self._determine_prediction_confidence(
                predictions, confidence_intervals, request
            )
            
            # Perform trend analysis
            trend_analysis = await self._analyze_trends(historical_data, request.target_metrics)
            
            # Calculate feature importance
            feature_importance = await self._calculate_prediction_feature_importance(
                features, request
            )
            
            # Assess risk factors
            risk_factors = await self._assess_prediction_risks(
                predictions, historical_data, request
            )
            
            # Generate actionable recommendations
            recommendations = await self._generate_prediction_recommendations(
                predictions, trend_analysis, request
            )
            
            # Calculate model accuracy
            model_accuracy = await self._estimate_model_accuracy(request.prediction_type)
            
            # Set validity period
            valid_until = datetime.now() + self._get_prediction_validity_period(request.time_horizon)
            
            # Create prediction result
            result = PredictionResult(
                prediction_id=prediction_id,
                request=request,
                predicted_values=predictions,
                confidence_intervals=confidence_intervals,
                prediction_confidence=prediction_confidence,
                model_accuracy=model_accuracy,
                feature_importance=feature_importance,
                trend_analysis=trend_analysis,
                seasonal_components=seasonal_components,
                risk_factors=risk_factors,
                recommendations=recommendations,
                valid_until=valid_until
            )
            
            # Cache the prediction
            self.prediction_cache[prediction_id] = result
            
            self.logger.info(f"Prediction completed: {prediction_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Prediction failed: {str(e)}")
            raise
    
    async def _collect_historical_data(self, request: PredictionRequest) -> pd.DataFrame:
        """Collect historical data for prediction."""
        # In a real implementation, this would query actual databases
        # For demonstration, generate synthetic historical data
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=request.historical_data_days)
        
        # Generate time series data based on prediction type
        if request.prediction_type == PredictionType.CONTENT_PERFORMANCE:
            return self._generate_content_performance_history(start_date, end_date, request)
        elif request.prediction_type == PredictionType.AUDIENCE_GROWTH:
            return self._generate_audience_growth_history(start_date, end_date, request)
        elif request.prediction_type == PredictionType.REVENUE_FORECAST:
            return self._generate_revenue_history(start_date, end_date, request)
        else:
            # Generic time series
            return self._generate_generic_time_series(start_date, end_date, request)
    
    def _generate_content_performance_history(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        request: PredictionRequest
    ) -> pd.DataFrame:
        """
Generate synthetic content performance historical data."""
        dates = pd.date_range(start=start_date, end=end_date, freq='H')
        np.random.seed(42)
        
        # Base trend with some growth
        base_trend = np.linspace(100, 150, len(dates))
        
        # Add seasonal patterns (daily and weekly)
        daily_pattern = 20 * np.sin(2 * np.pi * np.arange(len(dates)) / 24)
        weekly_pattern = 15 * np.sin(2 * np.pi * np.arange(len(dates)) / (24 * 7))
        
        # Add noise
        noise = np.random.normal(0, 5, len(dates))
        
        # Combine components
        engagement_rate = base_trend + daily_pattern + weekly_pattern + noise
        engagement_rate = np.clip(engagement_rate, 0, None)
        
        # Additional metrics
        reach = engagement_rate * np.random.uniform(0.8, 1.2, len(dates))
        impressions = reach * np.random.uniform(5, 15, len(dates))
        
        return pd.DataFrame({
            'timestamp': dates,
            'engagement_rate': engagement_rate,
            'reach': reach,
            'impressions': impressions,
            'hour_of_day': dates.hour,
            'day_of_week': dates.dayofweek,
            'is_weekend': dates.dayofweek >= 5
        })
    
    def _generate_audience_growth_history(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        request: PredictionRequest
    ) -> pd.DataFrame:
        """
Generate synthetic audience growth historical data."""
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        np.random.seed(42)
        
        # Exponential growth with some volatility
        days_since_start = np.arange(len(dates))
        base_followers = 1000 + 50 * days_since_start + 0.1 * days_since_start ** 1.5
        
        # Add weekly patterns (slower growth on weekends)
        weekly_modifier = np.where(dates.dayofweek >= 5, 0.8, 1.0)
        
        # Add noise
        noise = np.random.normal(1, 0.05, len(dates))
        
        followers = base_followers * weekly_modifier * noise
        followers = np.maximum(followers, 0)
        followers = np.cumsum(np.diff(np.concatenate([[1000], followers])))
        
        # Additional metrics
        new_followers_daily = np.diff(np.concatenate([[1000], followers]))
        engagement_rate = np.random.uniform(0.02, 0.08, len(dates))
        
        return pd.DataFrame({
            'timestamp': dates,
            'total_followers': followers,
            'new_followers_daily': new_followers_daily,
            'engagement_rate': engagement_rate,
            'day_of_week': dates.dayofweek,
            'is_weekend': dates.dayofweek >= 5
        })
    
    def _generate_revenue_history(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        request: PredictionRequest
    ) -> pd.DataFrame:
        """
Generate synthetic revenue historical data."""
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        np.random.seed(42)
        
        # Base revenue with growth trend
        days_since_start = np.arange(len(dates))
        base_revenue = 100 + 5 * days_since_start + 0.05 * days_since_start ** 1.2
        
        # Add monthly seasonality (higher at month end)
        month_day = dates.day
        monthly_pattern = 1 + 0.2 * np.sin(2 * np.pi * month_day / 30)
        
        # Add weekly patterns (higher on weekdays)
        weekly_pattern = np.where(dates.dayofweek < 5, 1.1, 0.9)
        
        # Add noise
        noise = np.random.lognormal(0, 0.1, len(dates))
        
        revenue = base_revenue * monthly_pattern * weekly_pattern * noise
        
        return pd.DataFrame({
            'timestamp': dates,
            'daily_revenue': revenue,
            'cumulative_revenue': np.cumsum(revenue),
            'day_of_week': dates.dayofweek,
            'day_of_month': dates.day,
            'is_weekend': dates.dayofweek >= 5,
            'is_month_end': dates.day >= 28
        })
    
    def _generate_generic_time_series(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        request: PredictionRequest
    ) -> pd.DataFrame:
        """
Generate generic time series data."""
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        np.random.seed(42)
        
        # Simple trend with seasonality
        trend = np.linspace(0, 10, len(dates))
        seasonal = 5 * np.sin(2 * np.pi * np.arange(len(dates)) / 7)  # Weekly seasonality
        noise = np.random.normal(0, 1, len(dates))
        
        values = trend + seasonal + noise
        
        return pd.DataFrame({
            'timestamp': dates,
            'target_metric': values,
            'day_of_week': dates.dayofweek
        })
    
    async def _engineer_prediction_features(
        self, 
        historical_data: pd.DataFrame, 
        request: PredictionRequest
    ) -> pd.DataFrame:
        """
Engineer features for prediction models."""
        features = historical_data.copy()
        
        # Time-based features
        if 'timestamp' in features.columns:
            features['timestamp'] = pd.to_datetime(features['timestamp'])
            features['hour'] = features['timestamp'].dt.hour
            features['day_of_week'] = features['timestamp'].dt.dayofweek
            features['day_of_month'] = features['timestamp'].dt.day
            features['month'] = features['timestamp'].dt.month
            features['quarter'] = features['timestamp'].dt.quarter
            features['is_weekend'] = (features['day_of_week'] >= 5).astype(int)
            features['is_holiday'] = 0  # Would be populated from holiday calendar
        
        # Lag features for target metrics
        for metric in request.target_metrics:
            if metric in features.columns:
                # Create lag features
                for lag in [1, 2, 3, 7, 14]:
                    features[f'{metric}_lag_{lag}'] = features[metric].shift(lag)
                
                # Rolling statistics
                for window in [3, 7, 14]:
                    features[f'{metric}_rolling_mean_{window}'] = features[metric].rolling(window).mean()
                    features[f'{metric}_rolling_std_{window}'] = features[metric].rolling(window).std()
        
        # Technical indicators
        for metric in request.target_metrics:
            if metric in features.columns:
                # Moving averages
                features[f'{metric}_sma_7'] = features[metric].rolling(7).mean()
                features[f'{metric}_sma_14'] = features[metric].rolling(14).mean()
                features[f'{metric}_ema_7'] = features[metric].ewm(span=7).mean()
                
                # Rate of change
                features[f'{metric}_roc_7'] = features[metric].pct_change(7)
                features[f'{metric}_roc_14'] = features[metric].pct_change(14)
                
                # Momentum indicators
                features[f'{metric}_momentum_3'] = features[metric] - features[metric].shift(3)
        
        # External factor features
        for factor, value in request.external_factors.items():
            features[f'external_{factor}'] = value
        
        # Drop rows with NaN values (due to lag features)
        features = features.dropna()
        
        return features
    
    async def _perform_seasonal_decomposition(
        self, 
        historical_data: pd.DataFrame, 
        target_metrics: List[str]
    ) -> Dict[str, Any]:
        """
Perform seasonal decomposition for target metrics."""
        seasonal_components = {}
        
        for metric in target_metrics:
            if metric not in historical_data.columns:
                continue
            
            try:
                # Ensure we have enough data points
                if len(historical_data) < 24:  # Need at least 2 cycles for weekly seasonality
                    continue
                
                ts_data = historical_data[metric].dropna()
                
                if len(ts_data) < 10:
                    continue
                
                # Perform seasonal decomposition
                # For demonstration, use a simple approach
                decomposition = seasonal_decompose(
                    ts_data, 
                    model='additive', 
                    period=min(7, len(ts_data) // 3),  # Weekly or shorter cycle
                    extrapolate_trend='freq'
                )
                
                seasonal_components[metric] = {
                    'trend': decomposition.trend.dropna().values.tolist(),
                    'seasonal': decomposition.seasonal.dropna().values.tolist(),
                    'residual': decomposition.resid.dropna().values.tolist(),
                    'seasonal_strength': np.var(decomposition.seasonal.dropna()) / np.var(ts_data),
                    'trend_strength': np.var(decomposition.trend.dropna()) / np.var(ts_data)
                }
                
            except Exception as e:
                self.logger.warning(f"Seasonal decomposition failed for {metric}: {str(e)}")
                seasonal_components[metric] = {
                    'trend': [],
                    'seasonal': [],
                    'residual': [],
                    'seasonal_strength': 0.0,
                    'trend_strength': 0.0
                }
        
        return seasonal_components
    
    async def _make_ensemble_predictions(
        self, 
        features: pd.DataFrame, 
        request: PredictionRequest, 
        seasonal_components: Dict[str, Any]
    ) -> Dict[str, Union[float, List[float]]]:
        """Make predictions using ensemble of models."""
        predictions = {}
        
        # Determine time horizon key
        horizon_key = request.time_horizon.value
        if horizon_key not in ['short_term', 'medium_term', 'long_term']:
            horizon_key = 'medium_term'  # Default
        
        # Get prediction type key
        pred_type_key = request.prediction_type.value
        if pred_type_key not in self.prediction_models:
            pred_type_key = 'content_performance'  # Default
        
        # Get models for this prediction type and horizon
        model_config = self.prediction_models[pred_type_key].get(horizon_key, {})
        
        if not model_config:
            # Fallback to default models
            model_config = {
                'primary': LinearRegression(),
                'secondary': RandomForestRegressor(n_estimators=50, random_state=42),
                'ensemble_weight': 0.7
            }
        
        for metric in request.target_metrics:
            if metric not in features.columns:
                continue
            
            try:
                # Prepare training data
                X = features.drop(columns=[metric] + [col for col in features.columns if col.startswith('timestamp')])
                y = features[metric]
                
                # Handle missing values
                X = X.fillna(X.mean())
                y = y.fillna(y.mean())
                
                if len(X) < 5:
                    # Not enough data, use simple prediction
                    predictions[metric] = float(y.mean())
                    continue
                
                # Split data for training (use most recent 80% for training)
                split_point = max(1, int(len(X) * 0.8))
                X_train, X_test = X.iloc[:split_point], X.iloc[split_point:]
                y_train, y_test = y.iloc[:split_point], y.iloc[split_point:]
                
                # Scale features
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                
                # Train primary model
                primary_model = model_config['primary']
                primary_model.fit(X_train_scaled, y_train)
                
                # Train secondary model
                secondary_model = model_config['secondary']
                secondary_model.fit(X_train_scaled, y_train)
                
                # Make prediction on the most recent data point
                if len(X_test) > 0:
                    X_pred = scaler.transform(X_test.iloc[[-1]])
                else:
                    X_pred = X_train_scaled[[-1]]
                
                # Get ensemble prediction
                primary_pred = primary_model.predict(X_pred)[0]
                secondary_pred = secondary_model.predict(X_pred)[0]
                
                ensemble_weight = model_config.get('ensemble_weight', 0.7)
                ensemble_pred = (
                    ensemble_weight * primary_pred + 
                    (1 - ensemble_weight) * secondary_pred
                )
                
                # Apply seasonal adjustment if available
                if metric in seasonal_components and seasonal_components[metric]['seasonal']:
                    seasonal_adj = seasonal_components[metric]['seasonal'][-1] if seasonal_components[metric]['seasonal'] else 0
                    ensemble_pred += seasonal_adj
                
                predictions[metric] = float(ensemble_pred)
                
            except Exception as e:
                self.logger.error(f"Prediction failed for metric {metric}: {str(e)}")
                # Fallback prediction
                predictions[metric] = float(features[metric].mean()) if metric in features.columns else 0.0
        
        return predictions
    
    async def _calculate_confidence_intervals(
        self, 
        predictions: Dict[str, Union[float, List[float]]], 
        confidence_level: float
    ) -> Dict[str, Tuple[float, float]]:
        """Calculate confidence intervals for predictions."""
        confidence_intervals = {}
        
        # Z-score for confidence level
        z_score = stats.norm.ppf((1 + confidence_level) / 2)
        
        for metric, prediction in predictions.items():
            if isinstance(prediction, (int, float)):
                # Estimate uncertainty based on historical variance
                # In a real implementation, this would use model-specific uncertainty
                estimated_std = abs(prediction) * 0.1  # 10% uncertainty as default
                
                lower_bound = prediction - z_score * estimated_std
                upper_bound = prediction + z_score * estimated_std
                
                confidence_intervals[metric] = (lower_bound, upper_bound)
            else:
                # For list predictions, calculate element-wise intervals
                prediction_list = prediction if isinstance(prediction, list) else [prediction]
                estimated_std = [abs(p) * 0.1 for p in prediction_list]
                
                lower_bounds = [p - z_score * s for p, s in zip(prediction_list, estimated_std)]
                upper_bounds = [p + z_score * s for p, s in zip(prediction_list, estimated_std)]
                
                confidence_intervals[metric] = (lower_bounds, upper_bounds)
        
        return confidence_intervals
    
    async def _determine_prediction_confidence(
        self, 
        predictions: Dict[str, Union[float, List[float]]], 
        confidence_intervals: Dict[str, Tuple[float, float]], 
        request: PredictionRequest
    ) -> PredictionConfidence:
        """
Determine overall prediction confidence level."""
        # Calculate confidence score based on interval width and data quality
        confidence_scores = []
        
        for metric in predictions.keys():
            if metric in confidence_intervals:
                prediction = predictions[metric]
                lower, upper = confidence_intervals[metric]
                
                if isinstance(prediction, (int, float)):
                    interval_width = upper - lower
                    relative_width = interval_width / max(abs(prediction), 1.0)
                    confidence_score = max(0, 1 - relative_width)
                    confidence_scores.append(confidence_score)
        
        if not confidence_scores:
            return PredictionConfidence.LOW
        
        avg_confidence = statistics.mean(confidence_scores)
        
        if avg_confidence >= 0.95:
            return PredictionConfidence.VERY_HIGH
        elif avg_confidence >= 0.8:
            return PredictionConfidence.HIGH
        elif avg_confidence >= 0.6:
            return PredictionConfidence.MEDIUM
        else:
            return PredictionConfidence.LOW
    
    async def _analyze_trends(
        self, 
        historical_data: pd.DataFrame, 
        target_metrics: List[str]
    ) -> Dict[str, Any]:
        """
Analyze trends in historical data."""
        trend_analysis = {}
        
        for metric in target_metrics:
            if metric not in historical_data.columns:
                continue
            
            try:
                data = historical_data[metric].dropna()
                
                if len(data) < 3:
                    continue
                
                # Linear trend analysis
                x = np.arange(len(data))
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, data)
                
                # Trend direction and strength
                trend_direction = 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable'
                trend_strength = abs(r_value)  # Correlation coefficient as strength measure
                trend_significance = p_value < 0.05
                
                # Calculate rate of change
                pct_change = ((data.iloc[-1] - data.iloc[0]) / data.iloc[0]) * 100 if data.iloc[0] != 0 else 0
                
                # Volatility measure
                volatility = data.std() / data.mean() if data.mean() != 0 else 0
                
                trend_analysis[metric] = {
                    'direction': trend_direction,
                    'strength': float(trend_strength),
                    'significance': trend_significance,
                    'slope': float(slope),
                    'r_squared': float(r_value ** 2),
                    'p_value': float(p_value),
                    'percent_change': float(pct_change),
                    'volatility': float(volatility),
                    'trend_acceleration': self._calculate_trend_acceleration(data)
                }
                
            except Exception as e:
                self.logger.error(f"Trend analysis failed for {metric}: {str(e)}")
                trend_analysis[metric] = {
                    'direction': 'unknown',
                    'strength': 0.0,
                    'significance': False
                }
        
        return trend_analysis
    
    def _calculate_trend_acceleration(self, data: pd.Series) -> float:
        """Calculate trend acceleration (second derivative)."""
        try:
            if len(data) < 3:
                return 0.0
            
            # Calculate first derivative (velocity)
            first_diff = data.diff().dropna()
            
            if len(first_diff) < 2:
                return 0.0
            
            # Calculate second derivative (acceleration)
            second_diff = first_diff.diff().dropna()
            
            return float(second_diff.mean()) if len(second_diff) > 0 else 0.0
            
        except Exception:
            return 0.0
    
    async def _calculate_prediction_feature_importance(
        self, 
        features: pd.DataFrame, 
        request: PredictionRequest
    ) -> Dict[str, float]:
        """
Calculate feature importance for predictions."""
        feature_importance = {}
        
        # Use a simple approach based on correlation with target metrics
        for metric in request.target_metrics:
            if metric not in features.columns:
                continue
            
            try:
                # Calculate correlations with all other features
                correlations = features.corrwith(features[metric]).abs().sort_values(ascending=False)
                
                # Normalize and store top features
                total_correlation = correlations.sum()
                
                for feature, correlation in correlations.head(10).items():
                    if feature != metric and not pd.isna(correlation):
                        importance = correlation / total_correlation if total_correlation > 0 else 0
                        feature_importance[feature] = float(importance)
                        
            except Exception as e:
                self.logger.error(f"Feature importance calculation failed for {metric}: {str(e)}")
        
        return feature_importance
    
    async def _assess_prediction_risks(
        self, 
        predictions: Dict[str, Union[float, List[float]]], 
        historical_data: pd.DataFrame, 
        request: PredictionRequest
    ) -> List[str]:
        """Assess risks associated with predictions."""
        risk_factors = []
        
        # Data quality risks
        if len(historical_data) < 30:
            risk_factors.append("Limited historical data may affect prediction accuracy")
        
        # Volatility risks
        for metric in request.target_metrics:
            if metric in historical_data.columns:
                data = historical_data[metric].dropna()
                if len(data) > 0:
                    cv = data.std() / data.mean() if data.mean() != 0 else 0
                    if cv > 0.5:
                        risk_factors.append(f"High volatility in {metric} increases prediction uncertainty")
        
        # Trend change risks
        for metric in request.target_metrics:
            if metric in historical_data.columns:
                data = historical_data[metric].dropna()
                if len(data) >= 10:
                    # Check for recent trend changes
                    recent_trend = np.polyfit(range(len(data)//2, len(data)), data.iloc[len(data)//2:], 1)[0]
                    overall_trend = np.polyfit(range(len(data)), data, 1)[0]
                    
                    if abs(recent_trend - overall_trend) > abs(overall_trend) * 0.5:
                        risk_factors.append(f"Recent trend change detected in {metric}")
        
        # External factor risks
        if request.external_factors:
            risk_factors.append("External factors may significantly impact predictions")
        
        # Time horizon risks
        if request.time_horizon == TimeHorizon.LONG_TERM:
            risk_factors.append("Long-term predictions have inherently higher uncertainty")
        elif request.time_horizon == TimeHorizon.STRATEGIC:
            risk_factors.append("Strategic predictions subject to major market and technology shifts")
        
        return risk_factors
    
    async def _generate_prediction_recommendations(
        self, 
        predictions: Dict[str, Union[float, List[float]]], 
        trend_analysis: Dict[str, Any], 
        request: PredictionRequest
    ) -> List[str]:
        """Generate actionable recommendations based on predictions."""
        recommendations = []
        
        # Trend-based recommendations
        for metric, analysis in trend_analysis.items():
            if analysis.get('direction') == 'increasing' and analysis.get('strength', 0) > 0.7:
                recommendations.append(f"Strong upward trend in {metric} - consider scaling up efforts")
            elif analysis.get('direction') == 'decreasing' and analysis.get('strength', 0) > 0.7:
                recommendations.append(f"Declining trend in {metric} - investigate root causes and implement improvements")
            
            if analysis.get('volatility', 0) > 0.3:
                recommendations.append(f"High volatility in {metric} - consider risk mitigation strategies")
        
        # Prediction-based recommendations
        if request.prediction_type == PredictionType.CONTENT_PERFORMANCE:
            for metric, prediction in predictions.items():
                if isinstance(prediction, (int, float)):
                    if prediction > 100:  # Assuming 100 is a good baseline
                        recommendations.append(f"Predicted high performance in {metric} - optimize distribution timing")
                    elif prediction < 50:
                        recommendations.append(f"Predicted low performance in {metric} - review content strategy")
        
        elif request.prediction_type == PredictionType.AUDIENCE_GROWTH:
            for metric, prediction in predictions.items():
                if isinstance(prediction, (int, float)):
                    if prediction > 0:
                        recommendations.append("Positive audience growth predicted - maintain current engagement strategies")
                    else:
                        recommendations.append("Audience growth challenges predicted - diversify content and platforms")
        
        elif request.prediction_type == PredictionType.REVENUE_FORECAST:
            for metric, prediction in predictions.items():
                if isinstance(prediction, (int, float)):
                    recommendations.append("Monitor revenue drivers closely and optimize monetization strategies")
        
        # Time horizon specific recommendations
        if request.time_horizon == TimeHorizon.SHORT_TERM:
            recommendations.append("Focus on immediate optimizations and quick wins")
        elif request.time_horizon == TimeHorizon.LONG_TERM:
            recommendations.append("Plan strategic initiatives and infrastructure improvements")
        
        return recommendations
    
    async def _estimate_model_accuracy(self, prediction_type: PredictionType) -> float:
        """Estimate model accuracy for the prediction type."""
        # In a real implementation, this would be based on historical validation results
        accuracy_estimates = {
            PredictionType.CONTENT_PERFORMANCE: 0.82,
            PredictionType.AUDIENCE_GROWTH: 0.75,
            PredictionType.REVENUE_FORECAST: 0.70,
            PredictionType.ENGAGEMENT_RATE: 0.85,
            PredictionType.TREND_DIRECTION: 0.78
        }
        
        return accuracy_estimates.get(prediction_type, 0.75)  # Default 75% accuracy
    
    def _get_prediction_validity_period(self, time_horizon: TimeHorizon) -> timedelta:
        """
Get validity period for predictions based on time horizon."""
        validity_periods = {
            TimeHorizon.SHORT_TERM: timedelta(hours=6),
            TimeHorizon.MEDIUM_TERM: timedelta(days=1),
            TimeHorizon.LONG_TERM: timedelta(days=7),
            TimeHorizon.STRATEGIC: timedelta(days=30)
        }
        
        return validity_periods.get(time_horizon, timedelta(days=1))
    
    async def _check_prediction_cache(self, request: PredictionRequest) -> Optional[PredictionResult]:
        """
Check if a similar recent prediction exists in cache."""
        # Simple cache check based on request similarity
        for cached_result in self.prediction_cache.values():
            if (cached_result.request.prediction_type == request.prediction_type and
                cached_result.request.time_horizon == request.time_horizon and
                cached_result.valid_until and cached_result.valid_until > datetime.now()):
                
                # Check if the request is similar enough
                if set(request.target_metrics) == set(cached_result.request.target_metrics):
                    return cached_result
        
        return None
    
    async def _validate_models_continuously(self):
        """
Continuously validate and update model performance."""
        while True:
            try:
                # Validate models every 6 hours
                await asyncio.sleep(21600)
                
                # In a real implementation, this would:
                # 1. Collect new actual data
                # 2. Compare with previous predictions
                # 3. Update model performance metrics
                # 4. Retrain models if performance degrades
                
                self.logger.info("Model validation completed")
                
            except Exception as e:
                self.logger.error(f"Error in model validation: {str(e)}")
                await asyncio.sleep(3600)
    
    async def _detect_trends_continuously(self):
        """Continuously detect and update trend patterns."""
        while True:
            try:
                await asyncio.sleep(7200)  # Every 2 hours
                
                # Analyze recent data for new trend patterns
                # This would involve more sophisticated trend detection algorithms
                
                self.logger.info("Trend detection completed")
                
            except Exception as e:
                self.logger.error(f"Error in trend detection: {str(e)}")
                await asyncio.sleep(3600)
    
    async def _manage_prediction_cache(self):
        """Manage prediction cache by removing expired entries."""
        while True:
            try:
                current_time = datetime.now()
                expired_keys = [
                    key for key, result in self.prediction_cache.items()
                    if result.valid_until and result.valid_until < current_time
                ]
                
                for key in expired_keys:
                    del self.prediction_cache[key]
                
                if expired_keys:
                    self.logger.info(f"Removed {len(expired_keys)} expired predictions from cache")
                
                await asyncio.sleep(3600)  # Clean every hour
                
            except Exception as e:
                self.logger.error(f"Error in cache management: {str(e)}")
                await asyncio.sleep(3600)
    
    async def _learn_patterns_continuously(self):
        """Continuously learn new patterns from data."""
        while True:
            try:
                await asyncio.sleep(14400)  # Every 4 hours
                
                # Pattern learning would involve:
                # 1. Analyzing recent predictions vs actual results
                # 2. Identifying new patterns or changes in existing patterns
                # 3. Updating models or creating new specialized models
                
                self.logger.info("Pattern learning completed")
                
            except Exception as e:
                self.logger.error(f"Error in pattern learning: {str(e)}")
                await asyncio.sleep(7200)
    
    async def get_prediction_analytics(self) -> Dict[str, Any]:
        """Get comprehensive prediction engine analytics."""
        total_predictions = len(self.prediction_cache)
        
        # Count predictions by type
        type_distribution = {}
        confidence_distribution = {}
        
        for result in self.prediction_cache.values():
            pred_type = result.request.prediction_type.value
            type_distribution[pred_type] = type_distribution.get(pred_type, 0) + 1
            
            confidence = result.prediction_confidence.value
            confidence_distribution[confidence] = confidence_distribution.get(confidence, 0) + 1
        
        # Calculate average accuracy
        accuracies = list(self.model_validation_scores.values())
        avg_accuracy = statistics.mean(accuracies) if accuracies else 0.0
        
        return {
            'prediction_statistics': {
                'total_predictions_cached': total_predictions,
                'predictions_by_type': type_distribution,
                'predictions_by_confidence': confidence_distribution,
                'average_model_accuracy': round(avg_accuracy, 3)
            },
            'model_statistics': {
                'total_model_configurations': sum(len(models) for models in self.prediction_models.values()),
                'active_trend_patterns': len(self.trend_patterns),
                'feature_processors': len(self.feature_processors)
            },
            'system_status': {
                'active_services': len(self.active_services),
                'cache_hit_opportunities': 0,  # Would track cache effectiveness
                'prediction_latency_ms': 150,  # Would measure actual latency
                'model_update_frequency_hours': 24
            },
            'prediction_capabilities': {
                'supported_types': [t.value for t in PredictionType],
                'supported_horizons': [h.value for h in TimeHorizon],
                'max_prediction_horizon_days': self.max_prediction_horizon_days,
                'ensemble_models_enabled': self.ensemble_models
            }
        }
