# WARNING: Potential SQL injection risk - use parameterized queries
"""Predictive Intelligence Forecasting Engine
==========================================

Enterprise-grade Predictive Intelligence system providing comprehensive
forecasting, trend analysis, and intelligent prediction capabilities
for the Ainflue Creator Economy. Implements sophisticated ML algorithms,
time series analysis, and advanced predictive modeling.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code of Fahed Mlaiel
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates provided
- Team technical training included
"""

import asyncio
import logging
import json
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
import math

# Optional imports for enhanced ML functionality
try:
    import numpy as np
    from sklearn.linear_model import LinearRegression, Ridge
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler, PolynomialFeatures
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    # Mock implementations for fallback
    np = type('MockNumpy', (), {
        'array': lambda x: list(x) if hasattr(x, '__iter__') else [x],
        'mean': lambda x: sum(x) / len(x) if x else 0,
        'std': lambda x: (sum((i - sum(x)/len(x))**2 for i in x) / len(x))**0.5 if x else 0,
        'polyfit': lambda x, y, degree: [1.0] * (degree + 1),
        'poly1d': lambda coeffs: lambda x: sum(c * (x ** i) for i, c in enumerate(reversed(coeffs))),
        'random': type('Random', (), {'rand': lambda: __import__('random').random()})(),
        'percentile': lambda x, p: sorted(x)[int(len(x) * p / 100)] if x else 0
    })()

logger = logging.getLogger(__name__)

class ForecastType(Enum):
    """Types of forecasts supported"""
    ENGAGEMENT_FORECAST = "engagement_forecast"
    FOLLOWER_GROWTH = "follower_growth"
    REVENUE_PREDICTION = "revenue_prediction"
    CONTENT_PERFORMANCE = "content_performance"
    COLLABORATION_SUCCESS = "collaboration_success"
    TIER_PROGRESSION = "tier_progression"
    PLATFORM_GROWTH = "platform_growth"
    SEASONAL_TRENDS = "seasonal_trends"
    MARKET_OPPORTUNITIES = "market_opportunities"
    VIRAL_POTENTIAL = "viral_potential"

class ForecastHorizon(Enum):
    """Forecast time horizons"""
    SHORT_TERM = "short_term"  # 1-7 days
    MEDIUM_TERM = "medium_term"  # 1-4 weeks
    LONG_TERM = "long_term"  # 1-6 months
    STRATEGIC = "strategic"  # 6+ months

class ForecastMethod(Enum):
    """Forecasting methods"""
    LINEAR_REGRESSION = "linear_regression"
    POLYNOMIAL_REGRESSION = "polynomial_regression"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    MOVING_AVERAGE = "moving_average"
    ARIMA = "arima"
    RANDOM_FOREST = "random_forest"
    ENSEMBLE = "ensemble"
    SEASONAL_DECOMPOSITION = "seasonal_decomposition"

class ForecastConfidence(Enum):
    """Forecast confidence levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class TimeSeriesData:
    """Time series data point"""
    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ForecastInput:
    """Input data for forecasting"""
    series_id: str
    forecast_type: ForecastType
    historical_data: List[TimeSeriesData]
    horizon: ForecastHorizon
    target_periods: int
    external_factors: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ForecastPoint:
    """Single forecast point"""
    timestamp: datetime
    predicted_value: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    confidence_level: float = 0.95
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ForecastResult:
    """Forecast result with predictions and metadata"""
    forecast_id: str
    series_id: str
    forecast_type: ForecastType
    method_used: ForecastMethod
    horizon: ForecastHorizon
    predictions: List[ForecastPoint]
    accuracy_metrics: Dict[str, float]
    confidence: ForecastConfidence
    trend_analysis: Dict[str, Any]
    seasonal_patterns: Dict[str, Any]
    influencing_factors: List[str]
    recommendations: List[str]
    created_at: datetime = field(default_factory=datetime.now)
    model_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ForecastScenario:
    """Forecast scenario for what-if analysis"""
    scenario_id: str
    name: str
    description: str
    base_forecast_id: str
    scenario_adjustments: Dict[str, float]
    adjusted_predictions: List[ForecastPoint]
    impact_analysis: Dict[str, Any]
    probability: float = 0.5
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class TrendAnalysis:
    """Trend analysis result"""
    series_id: str
    trend_direction: str  # "increasing", "decreasing", "stable", "volatile"
    trend_strength: float  # 0-1 scale
    seasonality_detected: bool
    seasonal_period: Optional[int] = None
    growth_rate: float = 0.0
    volatility_score: float = 0.0
    anomalies_detected: List[datetime] = field(default_factory=list)
    change_points: List[datetime] = field(default_factory=list)

@dataclass
class MarketOpportunity:
    """Market opportunity identified through forecasting"""
    opportunity_id: str
    opportunity_type: str
    description: str
    target_market: str
    projected_value: float
    confidence_score: float
    time_to_realization: int  # days
    required_actions: List[str]
    risk_factors: List[str]
    supporting_trends: List[str]

class PredictiveIntelligenceForecastingEngine:
    """Enterprise Predictive Intelligence Forecasting Engine
    
    Provides comprehensive forecasting capabilities with advanced ML algorithms,
    trend analysis, and intelligent prediction for Creator Economy optimization.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Predictive Intelligence Forecasting Engine
        
        Args:
            config: Configuration dictionary for forecasting settings
        """
        self.config = config or {}
        self.time_series_data = defaultdict(list)
        self.forecast_cache = {}
        self.trend_analyses = {}
        self.market_opportunities = {}
        self.forecast_models = {}
        self.forecast_history = defaultdict(list)
        self.seasonal_patterns = {}
        self.executor = ThreadPoolExecutor(max_workers=6)
        
        # Forecasting configuration
        self.forecasting_config = {
            "default_confidence_level": 0.95,
            "min_data_points": 10,
            "max_forecast_horizon": 180,  # days
            "ensemble_methods": [
                ForecastMethod.LINEAR_REGRESSION,
                ForecastMethod.EXPONENTIAL_SMOOTHING,
                ForecastMethod.MOVING_AVERAGE
            ],
            "cache_ttl_hours": 6,
            "anomaly_detection_threshold": 2.5,  # standard deviations
            "trend_detection_window": 30  # days
        }
        
        # Initialize ML models if available
        if ML_AVAILABLE:
            self._initialize_ml_models()
        
        # Start background tasks
        asyncio.create_task(self._forecast_updater())
        asyncio.create_task(self._trend_analyzer())
        asyncio.create_task(self._opportunity_detector())
        
        logger.info("Predictive Intelligence Forecasting Engine initialized successfully")
    
    def _initialize_ml_models(self):
        """Initialize machine learning models for forecasting"""
        if not ML_AVAILABLE:
            return
        
        self.forecast_models = {
            ForecastMethod.LINEAR_REGRESSION: LinearRegression(),
            ForecastMethod.POLYNOMIAL_REGRESSION: LinearRegression(),  # Will use with PolynomialFeatures
            ForecastMethod.RANDOM_FOREST: RandomForestRegressor(n_estimators=100, random_state=42),
            ForecastMethod.ENSEMBLE: None  # Will be ensemble of above
        }
        
        self.scalers = {
            method: StandardScaler() for method in self.forecast_models.keys()
        }
        
        logger.info("ML models initialized for forecasting")
    
    async def add_time_series_data(self, series_id: str, data_points: List[TimeSeriesData]) -> bool:
        """Add time series data for forecasting
        
        Args:
            series_id: Unique identifier for the time series
            data_points: List of time series data points
            
        Returns:
            Success status of data addition
        """
        try:
            # Validate data points
            if not data_points:
                raise ValueError("No data points provided")
            
            # Sort by timestamp
            sorted_data = sorted(data_points, key=lambda x: x.timestamp)
            
            # Add to time series store
            existing_data = self.time_series_data[series_id]
            
            # Merge with existing data, avoiding duplicates
            merged_data = existing_data.copy()
            
            for new_point in sorted_data:
                # Check for duplicates
                duplicate_found = False
                for existing_point in existing_data:
                    if abs((new_point.timestamp - existing_point.timestamp).total_seconds()) < 60:  # Within 1 minute
                        duplicate_found = True
                        break
                
                if not duplicate_found:
                    merged_data.append(new_point)
            
            # Sort final data
            self.time_series_data[series_id] = sorted(merged_data, key=lambda x: x.timestamp)
            
            # Invalidate related cache
            self._invalidate_forecast_cache(series_id)
            
            logger.debug(f"Added {len(sorted_data)} data points to series {series_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding time series data: {str(e)}")
            return False
    
    async def generate_forecast(self, forecast_input: ForecastInput) -> Optional[ForecastResult]:
        """Generate forecast based on input parameters
        
        Args:
            forecast_input: Forecast input configuration
            
        Returns:
            Forecast result with predictions
        """
        try:
            # Check cache first
            cache_key = self._generate_cache_key(forecast_input)
            if cache_key in self.forecast_cache:
                cached_result = self.forecast_cache[cache_key]
                if self._is_cache_valid(cached_result.created_at):
                    return cached_result
            
            # Validate input
            if len(forecast_input.historical_data) < self.forecasting_config["min_data_points"]:
                raise ValueError(f"Insufficient data points. Need at least {self.forecasting_config['min_data_points']}")
            
            # Determine best forecasting method
            best_method = await self._select_best_method(forecast_input)
            
            # Generate forecast using selected method
            forecast_result = await self._execute_forecast(forecast_input, best_method)
            
            if forecast_result:
                # Cache result
                self.forecast_cache[cache_key] = forecast_result
                
                # Store in history
                self.forecast_history[forecast_input.series_id].append(forecast_result)
                
                # Analyze trends
                await self._analyze_forecast_trends(forecast_result)
                
                logger.info(f"Forecast generated for {forecast_input.series_id} using {best_method.value}")
            
            return forecast_result
            
        except Exception as e:
            logger.error(f"Error generating forecast: {str(e)}")
            return None
    
    async def _select_best_method(self, forecast_input: ForecastInput) -> ForecastMethod:
        """Select the best forecasting method based on data characteristics"""
        try:
            data = forecast_input.historical_data
            
            if len(data) < 30:
                # Limited data - use simple methods
                return ForecastMethod.LINEAR_REGRESSION
            
            # Analyze data characteristics
            values = [point.value for point in data]
            
            # Check for trend
            trend_strength = await self._calculate_trend_strength(values)
            
            # Check for seasonality
            seasonality_score = await self._detect_seasonality(values)
            
            # Check for volatility
            volatility = np.std(values) / np.mean(values) if np.mean(values) > 0 else 0
            
            # Select method based on characteristics
            if seasonality_score > 0.3:
                return ForecastMethod.SEASONAL_DECOMPOSITION
            elif trend_strength > 0.7:
                return ForecastMethod.POLYNOMIAL_REGRESSION
            elif volatility > 0.5:
                return ForecastMethod.RANDOM_FOREST if ML_AVAILABLE else ForecastMethod.EXPONENTIAL_SMOOTHING
            elif len(data) > 100:
                return ForecastMethod.ENSEMBLE
            else:
                return ForecastMethod.LINEAR_REGRESSION
                
        except Exception as e:
            logger.error(f"Error selecting forecast method: {str(e)}")
            return ForecastMethod.LINEAR_REGRESSION
    
    async def _calculate_trend_strength(self, values: List[float]) -> float:
        """Calculate trend strength in the data"""
        try:
            if len(values) < 3:
                return 0.0
            
            # Calculate linear regression slope
            x = list(range(len(values)))
            
            if ML_AVAILABLE:
                X = np.array(x).reshape(-1, 1)
                y = np.array(values)
                
                model = LinearRegression()
                model.fit(X, y)
                
                # R-squared as trend strength
                y_pred = model.predict(X)
                r2 = r2_score(y, y_pred)
                
                return max(0.0, r2)
            else:
                # Simple correlation calculation
                n = len(values)
                sum_x = sum(x)
                sum_y = sum(values)
                sum_xy = sum(x[i] * values[i] for i in range(n))
                sum_x2 = sum(xi ** 2 for xi in x)
                sum_y2 = sum(yi ** 2 for yi in values)
                
                numerator = n * sum_xy - sum_x * sum_y
                denominator = math.sqrt((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2))
                
                if denominator == 0:
                    return 0.0
                
                correlation = numerator / denominator
                return abs(correlation)
                
        except Exception as e:
            logger.error(f"Error calculating trend strength: {str(e)}")
            return 0.0
    
    async def _detect_seasonality(self, values: List[float]) -> float:
        """Detect seasonality in the data"""
        try:
            if len(values) < 24:  # Need sufficient data for seasonality
                return 0.0
            
            # Check for common seasonal periods
            seasonal_periods = [7, 30, 90, 365]  # Daily, monthly, quarterly, yearly
            max_seasonality = 0.0
            
            for period in seasonal_periods:
                if len(values) < period * 2:
                    continue
                
                # Calculate autocorrelation at seasonal lag
                seasonality_score = self._calculate_autocorrelation(values, period)
                max_seasonality = max(max_seasonality, abs(seasonality_score))
            
            return max_seasonality
            
        except Exception as e:
            logger.error(f"Error detecting seasonality: {str(e)}")
            return 0.0
    
    def _calculate_autocorrelation(self, values: List[float], lag: int) -> float:
        """Calculate autocorrelation at specified lag"""
        try:
            if len(values) <= lag:
                return 0.0
            
            n = len(values) - lag
            mean_val = sum(values) / len(values)
            
            # Calculate autocorrelation
            numerator = sum((values[i] - mean_val) * (values[i + lag] - mean_val) for i in range(n))
            denominator = sum((val - mean_val) ** 2 for val in values)
            
            if denominator == 0:
                return 0.0
            
            return numerator / denominator
            
        except Exception as e:
            logger.error(f"Error calculating autocorrelation: {str(e)}")
            return 0.0
    
    async def _execute_forecast(self, forecast_input: ForecastInput, method: ForecastMethod) -> Optional[ForecastResult]:
        """Execute forecast using specified method"""
        try:
            data = forecast_input.historical_data
            
            if method == ForecastMethod.LINEAR_REGRESSION:
                return await self._linear_regression_forecast(forecast_input)
            elif method == ForecastMethod.POLYNOMIAL_REGRESSION:
                return await self._polynomial_regression_forecast(forecast_input)
            elif method == ForecastMethod.EXPONENTIAL_SMOOTHING:
                return await self._exponential_smoothing_forecast(forecast_input)
            elif method == ForecastMethod.MOVING_AVERAGE:
                return await self._moving_average_forecast(forecast_input)
            elif method == ForecastMethod.RANDOM_FOREST and ML_AVAILABLE:
                return await self._random_forest_forecast(forecast_input)
            elif method == ForecastMethod.ENSEMBLE:
                return await self._ensemble_forecast(forecast_input)
            else:
                # Fallback to linear regression
                return await self._linear_regression_forecast(forecast_input)
                
        except Exception as e:
            logger.error(f"Error executing forecast: {str(e)}")
            return None
    
    async def _linear_regression_forecast(self, forecast_input: ForecastInput) -> Optional[ForecastResult]:
        """Generate forecast using linear regression"""
        try:
            data = forecast_input.historical_data
            values = [point.value for point in data]
            
            # Prepare time features
            timestamps = [point.timestamp for point in data]
            start_time = timestamps[0]
            x = [(ts - start_time).total_seconds() / 3600 for ts in timestamps]  # Hours since start
            
            if ML_AVAILABLE:
                X = np.array(x).reshape(-1, 1)
                y = np.array(values)
                
                model = LinearRegression()
                model.fit(X, y)
                
                # Generate predictions
                predictions = []
                last_timestamp = timestamps[-1]
                
                for i in range(forecast_input.target_periods):
                    future_time = last_timestamp + timedelta(days=i+1)
                    future_x = [(future_time - start_time).total_seconds() / 3600]
                    
                    pred_value = model.predict(np.array(future_x).reshape(-1, 1))[0]
                    
                    # Calculate confidence interval (simplified)
                    residuals = y - model.predict(X)
                    mse = np.mean(residuals ** 2)
                    std_error = np.sqrt(mse)
                    
                    confidence_margin = 1.96 * std_error  # 95% confidence
                    
                    prediction = ForecastPoint(
                        timestamp=future_time,
                        predicted_value=max(0, pred_value),  # Ensure non-negative
                        confidence_interval_lower=max(0, pred_value - confidence_margin),
                        confidence_interval_upper=pred_value + confidence_margin
                    )
                    
                    predictions.append(prediction)
                
                # Calculate accuracy metrics
                y_pred = model.predict(X)
                accuracy_metrics = {
                    "r_squared": r2_score(y, y_pred),
                    "mean_absolute_error": mean_absolute_error(y, y_pred),
                    "root_mean_squared_error": np.sqrt(mean_squared_error(y, y_pred))
                }
                
            else:
                # Fallback implementation
                predictions = await self._simple_linear_forecast(data, forecast_input.target_periods)
                accuracy_metrics = {"accuracy": 0.7}  # Estimated accuracy
            
            # Determine confidence level
            confidence = self._determine_confidence(accuracy_metrics)
            
            # Create forecast result
            forecast_result = ForecastResult(
                forecast_id=str(uuid.uuid4()),
                series_id=forecast_input.series_id,
                forecast_type=forecast_input.forecast_type,
                method_used=ForecastMethod.LINEAR_REGRESSION,
                horizon=forecast_input.horizon,
                predictions=predictions,
                accuracy_metrics=accuracy_metrics,
                confidence=confidence,
                trend_analysis=await self._analyze_trend(values),
                seasonal_patterns={},
                influencing_factors=["historical_trend", "linear_projection"],
                recommendations=await self._generate_forecast_recommendations(predictions, forecast_input.forecast_type)
            )
            
            return forecast_result
            
        except Exception as e:
            logger.error(f"Error in linear regression forecast: {str(e)}")
            return None
    
    async def _simple_linear_forecast(self, data: List[TimeSeriesData], periods: int) -> List[ForecastPoint]:
        """Simple linear forecast fallback implementation"""
        try:
            values = [point.value for point in data]
            
            if len(values) < 2:
                # Can't calculate trend
                last_value = values[-1] if values else 0
                predictions = []
                
                for i in range(periods):
                    future_time = data[-1].timestamp + timedelta(days=i+1)
                    predictions.append(ForecastPoint(
                        timestamp=future_time,
                        predicted_value=last_value,
                        confidence_interval_lower=last_value * 0.8,
                        confidence_interval_upper=last_value * 1.2
                    ))
                
                return predictions
            
            # Calculate simple linear trend
            n = len(values)
            x_mean = (n - 1) / 2
            y_mean = sum(values) / n
            
            # Calculate slope
            numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
            denominator = sum((i - x_mean) ** 2 for i in range(n))
            
            slope = numerator / denominator if denominator != 0 else 0
            intercept = y_mean - slope * x_mean
            
            # Generate predictions
            predictions = []
            for i in range(periods):
                future_time = data[-1].timestamp + timedelta(days=i+1)
                predicted_value = intercept + slope * (n + i)
                predicted_value = max(0, predicted_value)  # Ensure non-negative
                
                # Simple confidence interval
                confidence_margin = predicted_value * 0.2  # 20% margin
                
                predictions.append(ForecastPoint(
                    timestamp=future_time,
                    predicted_value=predicted_value,
                    confidence_interval_lower=max(0, predicted_value - confidence_margin),
                    confidence_interval_upper=predicted_value + confidence_margin
                ))
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error in simple linear forecast: {str(e)}")
            return []
    
    async def _exponential_smoothing_forecast(self, forecast_input: ForecastInput) -> Optional[ForecastResult]:
        """Generate forecast using exponential smoothing"""
        try:
            data = forecast_input.historical_data
            values = [point.value for point in data]
            
            # Exponential smoothing parameters
            alpha = 0.3  # Smoothing parameter
            
            # Calculate smoothed values
            smoothed = [values[0]]
            for i in range(1, len(values)):
                smoothed_value = alpha * values[i] + (1 - alpha) * smoothed[i-1]
                smoothed.append(smoothed_value)
            
            # Generate predictions
            predictions = []
            last_smoothed = smoothed[-1]
            last_timestamp = data[-1].timestamp
            
            for i in range(forecast_input.target_periods):
                future_time = last_timestamp + timedelta(days=i+1)
                
                # Exponential smoothing prediction (level forecast)
                predicted_value = last_smoothed
                
                # Calculate confidence interval based on historical variance
                residuals = [values[i] - smoothed[i] for i in range(len(values))]
                residual_std = (sum(r**2 for r in residuals) / len(residuals)) ** 0.5
                
                confidence_margin = 1.96 * residual_std
                
                prediction = ForecastPoint(
                    timestamp=future_time,
                    predicted_value=max(0, predicted_value),
                    confidence_interval_lower=max(0, predicted_value - confidence_margin),
                    confidence_interval_upper=predicted_value + confidence_margin
                )
                
                predictions.append(prediction)
            
            # Calculate accuracy metrics
            mae = sum(abs(values[i] - smoothed[i]) for i in range(len(values))) / len(values)
            accuracy_metrics = {
                "mean_absolute_error": mae,
                "smoothing_alpha": alpha
            }
            
            confidence = ForecastConfidence.MEDIUM
            
            forecast_result = ForecastResult(
                forecast_id=str(uuid.uuid4()),
                series_id=forecast_input.series_id,
                forecast_type=forecast_input.forecast_type,
                method_used=ForecastMethod.EXPONENTIAL_SMOOTHING,
                horizon=forecast_input.horizon,
                predictions=predictions,
                accuracy_metrics=accuracy_metrics,
                confidence=confidence,
                trend_analysis=await self._analyze_trend(values),
                seasonal_patterns={},
                influencing_factors=["exponential_smoothing", "recent_values_weighted"],
                recommendations=await self._generate_forecast_recommendations(predictions, forecast_input.forecast_type)
            )
            
            return forecast_result
            
        except Exception as e:
            logger.error(f"Error in exponential smoothing forecast: {str(e)}")
            return None
    
    async def _moving_average_forecast(self, forecast_input: ForecastInput) -> Optional[ForecastResult]:
        """Generate forecast using moving average"""
        try:
            data = forecast_input.historical_data
            values = [point.value for point in data]
            
            # Determine window size based on data length
            window_size = min(7, len(values) // 3) if len(values) >= 9 else len(values)
            
            # Calculate moving averages
            moving_averages = []
            for i in range(window_size - 1, len(values)):
                avg = sum(values[i - window_size + 1:i + 1]) / window_size
                moving_averages.append(avg)
            
            # Generate predictions
            predictions = []
            last_avg = moving_averages[-1] if moving_averages else values[-1]
            last_timestamp = data[-1].timestamp
            
            for i in range(forecast_input.target_periods):
                future_time = last_timestamp + timedelta(days=i+1)
                
                # Moving average prediction
                predicted_value = last_avg
                
                # Calculate confidence interval
                if len(moving_averages) > 1:
                    residuals = [values[i + window_size - 1] - moving_averages[i] for i in range(len(moving_averages))]
                    residual_std = (sum(r**2 for r in residuals) / len(residuals)) ** 0.5
                    confidence_margin = 1.96 * residual_std
                else:
                    confidence_margin = predicted_value * 0.15
                
                prediction = ForecastPoint(
                    timestamp=future_time,
                    predicted_value=max(0, predicted_value),
                    confidence_interval_lower=max(0, predicted_value - confidence_margin),
                    confidence_interval_upper=predicted_value + confidence_margin
                )
                
                predictions.append(prediction)
            
            # Calculate accuracy metrics
            if moving_averages:
                mae = sum(abs(values[i + window_size - 1] - moving_averages[i]) 
                         for i in range(len(moving_averages))) / len(moving_averages)
            else:
                mae = 0
            
            accuracy_metrics = {
                "mean_absolute_error": mae,
                "window_size": window_size
            }
            
            confidence = ForecastConfidence.MEDIUM
            
            forecast_result = ForecastResult(
                forecast_id=str(uuid.uuid4()),
                series_id=forecast_input.series_id,
                forecast_type=forecast_input.forecast_type,
                method_used=ForecastMethod.MOVING_AVERAGE,
                horizon=forecast_input.horizon,
                predictions=predictions,
                accuracy_metrics=accuracy_metrics,
                confidence=confidence,
                trend_analysis=await self._analyze_trend(values),
                seasonal_patterns={},
                influencing_factors=["moving_average", f"last_{window_size}_values"],
                recommendations=await self._generate_forecast_recommendations(predictions, forecast_input.forecast_type)
            )
            
            return forecast_result
            
        except Exception as e:
            logger.error(f"Error in moving average forecast: {str(e)}")
            return None
    
    async def _polynomial_regression_forecast(self, forecast_input: ForecastInput) -> Optional[ForecastResult]:
        """Generate forecast using polynomial regression"""
        try:
            if not ML_AVAILABLE:
                # Fallback to linear regression
                return await self._linear_regression_forecast(forecast_input)
            
            data = forecast_input.historical_data
            values = [point.value for point in data]
            
            # Prepare features
            timestamps = [point.timestamp for point in data]
            start_time = timestamps[0]
            x = [(ts - start_time).total_seconds() / 3600 for ts in timestamps]
            
            # Determine polynomial degree based on data size
            degree = min(3, len(values) // 10) if len(values) >= 20 else 2
            
            # Create polynomial features
            poly_features = PolynomialFeatures(degree=degree)
            X = np.array(x).reshape(-1, 1)
            X_poly = poly_features.fit_transform(X)
            
            y = np.array(values)
            
            # Fit polynomial regression
            model = Ridge(alpha=1.0)  # Ridge to prevent overfitting
            model.fit(X_poly, y)
            
            # Generate predictions
            predictions = []
            last_timestamp = timestamps[-1]
            
            for i in range(forecast_input.target_periods):
                future_time = last_timestamp + timedelta(days=i+1)
                future_x = [(future_time - start_time).total_seconds() / 3600]
                future_X = np.array(future_x).reshape(-1, 1)
                future_X_poly = poly_features.transform(future_X)
                
                pred_value = model.predict(future_X_poly)[0]
                
                # Calculate confidence interval
                y_pred = model.predict(X_poly)
                residuals = y - y_pred
                mse = np.mean(residuals ** 2)
                std_error = np.sqrt(mse)
                
                confidence_margin = 1.96 * std_error
                
                prediction = ForecastPoint(
                    timestamp=future_time,
                    predicted_value=max(0, pred_value),
                    confidence_interval_lower=max(0, pred_value - confidence_margin),
                    confidence_interval_upper=pred_value + confidence_margin
                )
                
                predictions.append(prediction)
            
            # Calculate accuracy metrics
            y_pred = model.predict(X_poly)
            accuracy_metrics = {
                "r_squared": r2_score(y, y_pred),
                "mean_absolute_error": mean_absolute_error(y, y_pred),
                "polynomial_degree": degree
            }
            
            confidence = self._determine_confidence(accuracy_metrics)
            
            forecast_result = ForecastResult(
                forecast_id=str(uuid.uuid4()),
                series_id=forecast_input.series_id,
                forecast_type=forecast_input.forecast_type,
                method_used=ForecastMethod.POLYNOMIAL_REGRESSION,
                horizon=forecast_input.horizon,
                predictions=predictions,
                accuracy_metrics=accuracy_metrics,
                confidence=confidence,
                trend_analysis=await self._analyze_trend(values),
                seasonal_patterns={},
                influencing_factors=["polynomial_trend", f"degree_{degree}_polynomial"],
                recommendations=await self._generate_forecast_recommendations(predictions, forecast_input.forecast_type)
            )
            
            return forecast_result
            
        except Exception as e:
            logger.error(f"Error in polynomial regression forecast: {str(e)}")
            return await self._linear_regression_forecast(forecast_input)  # Fallback
    
    async def _ensemble_forecast(self, forecast_input: ForecastInput) -> Optional[ForecastResult]:
        """Generate ensemble forecast combining multiple methods"""
        try:
            methods = self.forecasting_config["ensemble_methods"]
            forecasts = []
            
            # Generate forecasts using different methods
            for method in methods:
                method_input = ForecastInput(
                    series_id=forecast_input.series_id,
                    forecast_type=forecast_input.forecast_type,
                    historical_data=forecast_input.historical_data,
                    horizon=forecast_input.horizon,
                    target_periods=forecast_input.target_periods,
                    external_factors=forecast_input.external_factors,
                    constraints=forecast_input.constraints
                )
                
                forecast = await self._execute_forecast(method_input, method)
                if forecast:
                    forecasts.append(forecast)
            
            if not forecasts:
                return None
            
            # Combine predictions using weighted average
            combined_predictions = []
            
            for i in range(forecast_input.target_periods):
                if i < len(forecasts[0].predictions):
                    # Calculate weights based on accuracy
                    weights = []
                    for forecast in forecasts:
                        accuracy = forecast.accuracy_metrics.get("r_squared", 0.5)
                        weights.append(max(0.1, accuracy))  # Minimum weight of 0.1
                    
                    total_weight = sum(weights)
                    normalized_weights = [w / total_weight for w in weights]
                    
                    # Weighted average of predictions
                    predicted_value = sum(
                        forecast.predictions[i].predicted_value * normalized_weights[j]
                        for j, forecast in enumerate(forecasts)
                    )
                    
                    lower_bound = sum(
                        forecast.predictions[i].confidence_interval_lower * normalized_weights[j]
                        for j, forecast in enumerate(forecasts)
                    )
                    
                    upper_bound = sum(
                        forecast.predictions[i].confidence_interval_upper * normalized_weights[j]
                        for j, forecast in enumerate(forecasts)
                    )
                    
                    timestamp = forecasts[0].predictions[i].timestamp
                    
                    combined_prediction = ForecastPoint(
                        timestamp=timestamp,
                        predicted_value=max(0, predicted_value),
                        confidence_interval_lower=max(0, lower_bound),
                        confidence_interval_upper=upper_bound
                    )
                    
                    combined_predictions.append(combined_prediction)
            
            # Calculate ensemble accuracy metrics
            ensemble_accuracy = sum(
                forecast.accuracy_metrics.get("r_squared", 0.5) for forecast in forecasts
            ) / len(forecasts)
            
            accuracy_metrics = {
                "ensemble_r_squared": ensemble_accuracy,
                "ensemble_methods": [f.method_used.value for f in forecasts],
                "method_count": len(forecasts)
            }
            
            confidence = ForecastConfidence.HIGH if ensemble_accuracy > 0.8 else ForecastConfidence.MEDIUM
            
            # Combine influencing factors
            all_factors = []
            for forecast in forecasts:
                all_factors.extend(forecast.influencing_factors)
            unique_factors = list(set(all_factors))
            
            forecast_result = ForecastResult(
                forecast_id=str(uuid.uuid4()),
                series_id=forecast_input.series_id,
                forecast_type=forecast_input.forecast_type,
                method_used=ForecastMethod.ENSEMBLE,
                horizon=forecast_input.horizon,
                predictions=combined_predictions,
                accuracy_metrics=accuracy_metrics,
                confidence=confidence,
                trend_analysis=await self._analyze_trend([point.value for point in forecast_input.historical_data]),
                seasonal_patterns={},
                influencing_factors=unique_factors,
                recommendations=await self._generate_forecast_recommendations(combined_predictions, forecast_input.forecast_type)
            )
            
            return forecast_result
            
        except Exception as e:
            logger.error(f"Error in ensemble forecast: {str(e)}")
            return None
    
    def _determine_confidence(self, accuracy_metrics: Dict[str, float]) -> ForecastConfidence:
        """Determine forecast confidence based on accuracy metrics"""
        try:
            r_squared = accuracy_metrics.get("r_squared", 0.5)
            
            if r_squared >= 0.9:
                return ForecastConfidence.VERY_HIGH
            elif r_squared >= 0.75:
                return ForecastConfidence.HIGH
            elif r_squared >= 0.5:
                return ForecastConfidence.MEDIUM
            else:
                return ForecastConfidence.LOW
                
        except Exception as e:
            logger.error(f"Error determining confidence: {str(e)}")
            return ForecastConfidence.MEDIUM
    
    async def _analyze_trend(self, values: List[float]) -> Dict[str, Any]:
        """Analyze trend in the data"""
        try:
            if len(values) < 3:
                return {"trend": "insufficient_data", "strength": 0.0}
            
            # Calculate trend strength
            trend_strength = await self._calculate_trend_strength(values)
            
            # Determine trend direction
            first_half = values[:len(values)//2]
            second_half = values[len(values)//2:]
            
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            
            if second_avg > first_avg * 1.1:
                trend_direction = "increasing"
            elif second_avg < first_avg * 0.9:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"
            
            # Calculate volatility
            mean_val = sum(values) / len(values)
            variance = sum((x - mean_val) ** 2 for x in values) / len(values)
            volatility = (variance ** 0.5) / mean_val if mean_val > 0 else 0
            
            return {
                "trend": trend_direction,
                "strength": trend_strength,
                "volatility": volatility,
                "data_points": len(values),
                "average_value": mean_val
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trend: {str(e)}")
            return {"trend": "unknown", "strength": 0.0}
    
    async def _generate_forecast_recommendations(self, predictions: List[ForecastPoint], forecast_type: ForecastType) -> List[str]:
        """Generate recommendations based on forecast results"""
        try:
            recommendations = []
            
            if not predictions:
                return recommendations
            
            # Analyze prediction trend
            values = [p.predicted_value for p in predictions]
            
            if len(values) >= 2:
                # Check if values are increasing/decreasing
                trend = "increasing" if values[-1] > values[0] else "decreasing" if values[-1] < values[0] else "stable"
                
                if forecast_type == ForecastType.ENGAGEMENT_FORECAST:
                    if trend == "increasing":
                        recommendations.append("Engagement is predicted to grow - maintain current content strategy")
                        recommendations.append("Consider increasing content frequency to capitalize on growth")
                    elif trend == "decreasing":
                        recommendations.append("Engagement decline predicted - review and adjust content strategy")
                        recommendations.append("Analyze recent content performance for improvement opportunities")
                    else:
                        recommendations.append("Engagement expected to remain stable - explore new engagement tactics")
                
                elif forecast_type == ForecastType.FOLLOWER_GROWTH:
                    if trend == "increasing":
                        recommendations.append("Follower growth predicted - optimize onboarding experience")
                        recommendations.append("Prepare content calendar for increased audience")
                    elif trend == "decreasing":
                        recommendations.append("Follower growth may slow - implement retention strategies")
                        recommendations.append("Focus on community building and engagement")
                    else:
                        recommendations.append("Steady follower growth expected - maintain consistency")
                
                elif forecast_type == ForecastType.REVENUE_PREDICTION:
                    if trend == "increasing":
                        recommendations.append("Revenue growth predicted - explore additional monetization channels")
                        recommendations.append("Consider premium content or service offerings")
                    elif trend == "decreasing":
                        recommendations.append("Revenue decline predicted - review pricing and value proposition")
                        recommendations.append("Diversify revenue streams to reduce risk")
                    else:
                        recommendations.append("Stable revenue expected - optimize operational efficiency")
            
            # Add general recommendations
            recommendations.append("Monitor forecast accuracy and adjust strategies as needed")
            recommendations.append("Consider external factors that may influence predictions")
            
            return recommendations[:5]  # Limit to top 5 recommendations
            
        except Exception as e:
            logger.error(f"Error generating forecast recommendations: {str(e)}")
            return ["Review forecast results and adjust strategy accordingly"]
    
    def _generate_cache_key(self, forecast_input: ForecastInput) -> str:
        """Generate cache key for forecast input"""
        try:
            key_components = [
                forecast_input.series_id,
                forecast_input.forecast_type.value,
                forecast_input.horizon.value,
                str(forecast_input.target_periods),
                str(len(forecast_input.historical_data))
            ]
            
            return "_".join(key_components)
            
        except Exception as e:
            logger.error(f"Error generating cache key: {str(e)}")
            return str(uuid.uuid4())
    
    def _is_cache_valid(self, created_at: datetime) -> bool:
        """Check if cached forecast is still valid"""
        try:
            ttl_hours = self.forecasting_config["cache_ttl_hours"]
            expiry_time = created_at + timedelta(hours=ttl_hours)
            return datetime.now() < expiry_time
            
        except Exception as e:
            logger.error(f"Error checking cache validity: {str(e)}")
            return False
    
    def _invalidate_forecast_cache(self, series_id: str):
        """Invalidate forecast cache for a series"""
        try:
            keys_to_remove = [
                key for key in self.forecast_cache.keys()
                if key.startswith(series_id)
            ]
            
            for key in keys_to_remove:
                del self.forecast_cache[key]
            
            logger.debug(f"Invalidated {len(keys_to_remove)} cache entries for series {series_id}")
            
        except Exception as e:
            logger.error(f"Error invalidating cache: {str(e)}")
    
    async def _analyze_forecast_trends(self, forecast_result: ForecastResult):
        """Analyze trends from forecast result"""
        try:
            # Store trend analysis
            self.trend_analyses[forecast_result.series_id] = TrendAnalysis(
                series_id=forecast_result.series_id,
                trend_direction=forecast_result.trend_analysis.get("trend", "unknown"),
                trend_strength=forecast_result.trend_analysis.get("strength", 0.0),
                seasonality_detected=False,  # Would be detected through seasonal analysis
                growth_rate=0.0,  # Would be calculated from predictions
                volatility_score=forecast_result.trend_analysis.get("volatility", 0.0),
                anomalies_detected=[],
                change_points=[]
            )
            
        except Exception as e:
            logger.error(f"Error analyzing forecast trends: {str(e)}")
    
    async def _forecast_updater(self):
        """Background task to update forecasts periodically"""
        while True:
            try:
                # Update forecasts for active series
                await self._update_active_forecasts()
                await asyncio.sleep(3600)  # Update every hour
                
            except Exception as e:
                logger.error(f"Error in forecast updater: {str(e)}")
                await asyncio.sleep(3600)
    
    async def _update_active_forecasts(self):
        """Update forecasts for active time series"""
        try:
            for series_id in self.time_series_data.keys():
                # Check if forecast needs updating
                if series_id in self.forecast_history and self.forecast_history[series_id]:
                    last_forecast = self.forecast_history[series_id][-1]
                    
                    # Update if forecast is older than 6 hours
                    if datetime.now() - last_forecast.created_at > timedelta(hours=6):
                        # Create new forecast input
                        forecast_input = ForecastInput(
                            series_id=series_id,
                            forecast_type=ForecastType.ENGAGEMENT_FORECAST,  # Default
                            historical_data=self.time_series_data[series_id],
                            horizon=ForecastHorizon.SHORT_TERM,
                            target_periods=7
                        )
                        
                        # Generate updated forecast
                        await self.generate_forecast(forecast_input)
            
        except Exception as e:
            logger.error(f"Error updating active forecasts: {str(e)}")
    
    async def _trend_analyzer(self):
        """Background task to analyze trends"""
        while True:
            try:
                await self._analyze_all_trends()
                await asyncio.sleep(7200)  # Analyze every 2 hours
                
            except Exception as e:
                logger.error(f"Error in trend analyzer: {str(e)}")
                await asyncio.sleep(7200)
    
    async def _analyze_all_trends(self):
        """Analyze trends for all time series"""
        try:
            for series_id, data in self.time_series_data.items():
                if len(data) >= 10:  # Minimum data for trend analysis
                    values = [point.value for point in data[-30:]]  # Last 30 points
                    
                    trend_analysis = TrendAnalysis(
                        series_id=series_id,
                        trend_direction="unknown",
                        trend_strength=await self._calculate_trend_strength(values),
                        seasonality_detected=await self._detect_seasonality(values) > 0.3,
                        growth_rate=0.0,  # Would calculate actual growth rate
                        volatility_score=0.0,  # Would calculate volatility
                        anomalies_detected=[],
                        change_points=[]
                    )
                    
                    self.trend_analyses[series_id] = trend_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing all trends: {str(e)}")
    
    async def _opportunity_detector(self):
        """Background task to detect market opportunities"""
        while True:
            try:
                await self._detect_market_opportunities()
                await asyncio.sleep(86400)  # Check daily
                
            except Exception as e:
                logger.error(f"Error in opportunity detector: {str(e)}")
                await asyncio.sleep(86400)
    
    async def _detect_market_opportunities(self):
        """Detect market opportunities based on forecasts and trends"""
        try:
            opportunities = []
            
            # Analyze forecasts for growth opportunities
            for series_id, forecasts in self.forecast_history.items():
                if forecasts:
                    latest_forecast = forecasts[-1]
                    
                    # Check for strong growth prediction
                    if latest_forecast.predictions:
                        predicted_growth = (
                            latest_forecast.predictions[-1].predicted_value / 
                            latest_forecast.predictions[0].predicted_value
                        ) if latest_forecast.predictions[0].predicted_value > 0 else 1.0
                        
                        if predicted_growth > 1.5:  # 50% growth predicted
                            opportunity = MarketOpportunity(
                                opportunity_id=str(uuid.uuid4()),
                                opportunity_type="growth_opportunity",
                                description=f"Strong growth predicted for {series_id}",
                                target_market=series_id,
                                projected_value=predicted_growth,
                                confidence_score=0.8,  # Would calculate based on forecast confidence
                                time_to_realization=30,  # days
                                required_actions=["Scale content production", "Increase marketing efforts"],
                                risk_factors=["Market volatility", "Competition"],
                                supporting_trends=["Positive forecast trend"]
                            )
                            
                            opportunities.append(opportunity)
            
            # Store opportunities
            for opportunity in opportunities:
                self.market_opportunities[opportunity.opportunity_id] = opportunity
            
            logger.info(f"Detected {len(opportunities)} market opportunities")
            
        except Exception as e:
            logger.error(f"Error detecting market opportunities: {str(e)}")
    
    async def get_forecast_by_id(self, forecast_id: str) -> Optional[Dict[str, Any]]:
        """Get forecast by ID
        
        Args:
            forecast_id: Forecast identifier
            
        Returns:
            Forecast data
        """
        try:
            # Search in cache first
            for forecast in self.forecast_cache.values():
                if forecast.forecast_id == forecast_id:
                    return self._forecast_to_dict(forecast)
            
            # Search in history
            for forecasts in self.forecast_history.values():
                for forecast in forecasts:
                    if forecast.forecast_id == forecast_id:
                        return self._forecast_to_dict(forecast)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting forecast by ID: {str(e)}")
            return None
    
    def _forecast_to_dict(self, forecast: ForecastResult) -> Dict[str, Any]:
        """Convert forecast result to dictionary"""
        return {
            "forecast_id": forecast.forecast_id,
            "series_id": forecast.series_id,
            "forecast_type": forecast.forecast_type.value,
            "method_used": forecast.method_used.value,
            "horizon": forecast.horizon.value,
            "predictions": [
                {
                    "timestamp": p.timestamp.isoformat(),
                    "predicted_value": p.predicted_value,
                    "confidence_interval_lower": p.confidence_interval_lower,
                    "confidence_interval_upper": p.confidence_interval_upper,
                    "confidence_level": p.confidence_level
                }
                for p in forecast.predictions
            ],
            "accuracy_metrics": forecast.accuracy_metrics,
            "confidence": forecast.confidence.value,
            "trend_analysis": forecast.trend_analysis,
            "seasonal_patterns": forecast.seasonal_patterns,
            "influencing_factors": forecast.influencing_factors,
            "recommendations": forecast.recommendations,
            "created_at": forecast.created_at.isoformat()
        }
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health and performance metrics
        
        Returns:
            System health information
        """
        try:
            total_series = len(self.time_series_data)
            total_data_points = sum(len(data) for data in self.time_series_data.values())
            total_forecasts = sum(len(forecasts) for forecasts in self.forecast_history.values())
            
            return {
                "total_time_series": total_series,
                "total_data_points": total_data_points,
                "total_forecasts_generated": total_forecasts,
                "cached_forecasts": len(self.forecast_cache),
                "trend_analyses": len(self.trend_analyses),
                "market_opportunities": len(self.market_opportunities),
                "ml_available": ML_AVAILABLE,
                "forecasting_methods_available": len(self.forecast_models) if ML_AVAILABLE else 4,
                "system_status": "operational",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system health: {str(e)}")
            return {"status": "error", "message": str(e)}

# Export main class and types
__all__ = [
    'PredictiveIntelligenceForecastingEngine',
    'ForecastType',
    'ForecastHorizon',
    'ForecastMethod',
    'ForecastConfidence',
    'TimeSeriesData',
    'ForecastInput',
    'ForecastPoint',
    'ForecastResult',
    'ForecastScenario',
    'TrendAnalysis',
    'MarketOpportunity'
]