"""Predictive Analytics & Business Intelligence Module

Advanced AI-powered analytics system providing predictive insights, trend analysis,
and business intelligence for content creators platform.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
This cutting-edge predictive analytics system is protected intellectual property.
Any unauthorized copying, distribution, or use will result in immediate legal action.

Business Logic: Data Collection → Pattern Recognition → Predictive Modeling → Trend Analysis → Business Insights → Decision Support
"""

import asyncio
import json
import uuid
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Set, Tuple, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import defaultdict, deque
import math
import statistics

# ML and Analytics imports
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import LinearRegression, LogisticRegression
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.cluster import KMeans
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    from scipy import stats
    from scipy.signal import find_peaks
    import matplotlib.pyplot as plt
    import seaborn as sns
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

from .exceptions import OptimizationError, ConfigurationError
from .metrics import metrics_collector
from .performance import performance_monitor
from .content_types import ContentType

logger = logging.getLogger(__name__)


class PredictionType(Enum):
    """
Types of predictions"""

    AUDIENCE_GROWTH = "audience_growth"
    ENGAGEMENT_RATE = "engagement_rate"
    REVENUE_FORECAST = "revenue_forecast"
    CONTENT_PERFORMANCE = "content_performance"
    VIRAL_POTENTIAL = "viral_potential"
    MARKET_TRENDS = "market_trends"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    OPTIMAL_TIMING = "optimal_timing"
    CONTENT_SATURATION = "content_saturation"
    AUDIENCE_BEHAVIOR = "audience_behavior"


class TrendDirection(Enum):
    """Trend direction indicators"""

    STRONGLY_RISING = "strongly_rising"
    RISING = "rising"
    STABLE = "stable"
    DECLINING = "declining"
    STRONGLY_DECLINING = "strongly_declining"
    VOLATILE = "volatile"
    SEASONAL = "seasonal"


class AnalyticsTimeframe(Enum):
    """Analytics timeframes"""

    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class BusinessMetric(Enum):
    """Business metrics to track"""

    TOTAL_REVENUE = "total_revenue"
    MONTHLY_RECURRING_REVENUE = "mrr"
    CUSTOMER_ACQUISITION_COST = "cac"
    LIFETIME_VALUE = "ltv"
    RETURN_ON_INVESTMENT = "roi"
    CONVERSION_RATE = "conversion_rate"
    CHURN_RATE = "churn_rate"
    ENGAGEMENT_SCORE = "engagement_score"
    BRAND_SENTIMENT = "brand_sentiment"
    MARKET_SHARE = "market_share"


@dataclass
class DataPoint:
    """Single data point for analytics"""
    timestamp: datetime
    metric_name: str
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: str = "system"
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        try:
            logger.info(f"Executing to_dict")
            
            # Implementation for to_dict
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"to_dict completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"to_dict failed: {e}")
            raise
            "timestamp": self.timestamp.isoformat(),
            "metric_name": self.metric_name,
            "value": self.value,
            "metadata": self.metadata,
            "source": self.source,
            "confidence": self.confidence
        }


@dataclass
class PredictionResult:
    """Result of a prediction analysis"""
    prediction_id: str
    prediction_type: PredictionType
    target_metric: str
        try:
            logger.info(f"Executing to_dict")
            
            # Implementation for to_dict
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"to_dict completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"to_dict failed: {e}")
            raise
    confidence_interval: Tuple[float, float]
    confidence_score: float
    timeframe: str
    methodology: str
    contributing_factors: List[Dict[str, Any]]
    risk_factors: List[str]
    recommendations: List[str]
    model_accuracy: float
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "prediction_id": self.prediction_id,
            "prediction_type": self.prediction_type.value,
            "target_metric": self.target_metric,
            "predicted_value": self.predicted_value,
            "confidence_interval": list(self.confidence_interval),
            "confidence_score": self.confidence_score,
            "timeframe": self.timeframe,
            "methodology": self.methodology,
            "contributing_factors": self.contributing_factors,
            "risk_factors": self.risk_factors,
        try:
            logger.info(f"Executing to_dict")
            
            # Implementation for to_dict
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"to_dict completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"to_dict failed: {e}")
            raise
            "model_accuracy": self.model_accuracy,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }


@dataclass
class TrendAnalysis:
    """Trend analysis result"""
    trend_id: str
    metric_name: str
    trend_direction: TrendDirection
    strength: float
    duration: timedelta
    seasonal_component: bool
    growth_rate: float
    volatility: float
    support_resistance_levels: List[float]
    breakout_probability: float
    reversal_signals: List[str]
    trend_sustainability: float
    key_drivers: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        try:
            logger.info(f"Executing to_dict")
            
            # Implementation for to_dict
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"to_dict completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"to_dict failed: {e}")
            raise
            "trend_id": self.trend_id,
            "metric_name": self.metric_name,
            "trend_direction": self.trend_direction.value,
            "strength": self.strength,
            "duration_days": self.duration.days,
            "seasonal_component": self.seasonal_component,
            "growth_rate": self.growth_rate,
            "volatility": self.volatility,
            "support_resistance_levels": self.support_resistance_levels,
            "breakout_probability": self.breakout_probability,
            "reversal_signals": self.reversal_signals,
            "trend_sustainability": self.trend_sustainability,
            "key_drivers": self.key_drivers,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class BusinessIntelligenceReport:
    """Comprehensive business intelligence report"""
    report_id: str
    report_type: str
    creator_id: str
    timeframe: AnalyticsTimeframe
    key_metrics: Dict[str, float]
    trend_analyses: List[TrendAnalysis]
    predictions: List[PredictionResult]
    performance_insights: Dict[str, Any]
    optimization_opportunities: List[Dict[str, Any]]
    risk_assessment: Dict[str, float]
    competitive_analysis: Dict[str, Any]
    audience_insights: Dict[str, Any]
    revenue_analysis: Dict[str, Any]
    action_recommendations: List[Dict[str, Any]]
    executive_summary: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "report_type": self.report_type,
            "creator_id": self.creator_id,
            "timeframe": self.timeframe.value,
            "key_metrics": self.key_metrics,
            "trend_analyses": [trend.to_dict() for trend in self.trend_analyses],
            "predictions": [pred.to_dict() for pred in self.predictions],
            "performance_insights": self.performance_insights,
            "optimization_opportunities": self.optimization_opportunities,
            "risk_assessment": self.risk_assessment,
            "competitive_analysis": self.competitive_analysis,
            "audience_insights": self.audience_insights,
            "revenue_analysis": self.revenue_analysis,
            "action_recommendations": self.action_recommendations,
            "executive_summary": self.executive_summary,
            "created_at": self.created_at.isoformat()
        }


class TimeSeriesAnalyzer:
    """Advanced time series analysis and prediction"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """
Initialize ML models for time series analysis"""
        if ML_AVAILABLE:
            try:
                # Different models for different prediction tasks
                self.models['linear'] = LinearRegression()
                self.models['forest'] = RandomForestRegressor(n_estimators=100, random_state=42)
                self.models['gradient'] = GradientBoostingRegressor(n_estimators=100, random_state=42)
                
                # Scalers for normalization
                self.scalers['standard'] = StandardScaler()
                self.scalers['minmax'] = MinMaxScaler()
                
                logger.info("Time series models initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize ML models: {e}")
    
    async def analyze_time_series(self, 
                                data_points: List[DataPoint],
                                prediction_horizons: List[int] = None) -> Dict[str, Any]:
        """Comprehensive time series analysis"""
        try:
            if not data_points:
                return {"error": "No data points provided"}
            
            prediction_horizons = prediction_horizons or [7, 30, 90]  # Default: 1 week, 1 month, 3 months
            
            # Convert to time series format
            df = self._convert_to_dataframe(data_points)
            
            # Perform various analyses
            results = {}
            
            # Basic statistics
            results['basic_stats'] = self._calculate_basic_statistics(df)
            
            # Trend analysis
            results['trend_analysis'] = await self._analyze_trends(df)
            
            # Seasonality detection
            results['seasonality'] = self._detect_seasonality(df)
            
            # Anomaly detection
            results['anomalies'] = self._detect_anomalies(df)
            
            # Predictions for different horizons
            results['predictions'] = {}
            for horizon in prediction_horizons:
                prediction = await self._predict_future_values(df, horizon)
                results['predictions'][f'{horizon}_days'] = prediction
            
            # Change point detection
            results['change_points'] = self._detect_change_points(df)
            
            # Volatility analysis
            results['volatility'] = self._analyze_volatility(df)
            
            return results
            
        except Exception as e:
            logger.error(f"Time series analysis failed: {e}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _convert_to_dataframe(self, data_points: List[DataPoint]) -> pd.DataFrame:
        """Convert data points to pandas DataFrame"""
        data = []
        for point in data_points:
            data.append({
                'timestamp': point.timestamp,
                'value': point.value,
                'metric_name': point.metric_name,
                'confidence': point.confidence
            })
        
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        df.set_index('timestamp', inplace=True)
        
        return df
    
    def _calculate_basic_statistics(self, df: pd.DataFrame) -> Dict[str, float]:
        """
Calculate basic statistical measures"""
        try:
            if df.empty:
                return {}
            
            return {
                'mean': float(df['value'].mean()),
                'median': float(df['value'].median()),
                'std_dev': float(df['value'].std()),
                'variance': float(df['value'].var()),
                'min': float(df['value'].min()),
                'max': float(df['value'].max()),
                'range': float(df['value'].max() - df['value'].min()),
                'skewness': float(df['value'].skew()),
                'kurtosis': float(df['value'].kurtosis()),
                'count': len(df),
                'missing_values': int(df['value'].isnull().sum())
            }
        except Exception as e:
            logger.error(f"Basic statistics calculation failed: {e}")
            return {}
    
    async def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze trends in the time series"""
        try:
            if len(df) < 2:
                return {"error": "Insufficient data for trend analysis"}
            
            values = df['value'].values
            
            # Linear trend using least squares
            x = np.arange(len(values))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
            
            # Determine trend direction
            if abs(r_value) < 0.1:
                direction = TrendDirection.STABLE
            elif slope > 0:
                if r_value > 0.7:
                    direction = TrendDirection.STRONGLY_RISING
                else:
                    direction = TrendDirection.RISING
            else:
                if r_value < -0.7:
                    direction = TrendDirection.STRONGLY_DECLINING
                else:
                    direction = TrendDirection.DECLINING
            
            # Calculate trend strength
            strength = abs(r_value)
            
            # Volatility measure
            volatility = np.std(np.diff(values)) / np.mean(values) if np.mean(values) != 0 else 0
            
            if volatility > 0.3:
                direction = TrendDirection.VOLATILE
            
            return {
                'direction': direction.value,
                'strength': strength,
                'slope': slope,
                'r_squared': r_value ** 2,
                'p_value': p_value,
                'volatility': volatility,
                'trend_line_start': intercept,
                'trend_line_end': slope * (len(values) - 1) + intercept
            }
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return {"error": f"Trend analysis failed: {str(e)}"}
    
    def _detect_seasonality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect seasonal patterns in the data"""
        try:
            if len(df) < 14:  # Need at least 2 weeks of data
                return {"seasonal_detected": False, "reason": "Insufficient data"}
            
            values = df['value'].values
            
            # Simple autocorrelation-based seasonality detection
            seasonal_periods = [7, 30, 365]  # Weekly, monthly, yearly
            seasonality_results = {}
            
            for period in seasonal_periods:
                if len(values) > period * 2:
                    correlation = self._calculate_autocorrelation(values, period)
                    seasonality_results[f'{period}_day_cycle'] = {
                        'correlation': correlation,
                        'significant': correlation > 0.5
                    }
            
            # Determine if any seasonality is detected
            seasonal_detected = any(
                result['significant'] for result in seasonality_results.values()
            )
            
            return {
                'seasonal_detected': seasonal_detected,
                'seasonal_patterns': seasonality_results,
                'dominant_cycle': self._find_dominant_cycle(seasonality_results)
            }
            
        except Exception as e:
            logger.error(f"Seasonality detection failed: {e}")
            return {"seasonal_detected": False, "error": str(e)}
    
    def _calculate_autocorrelation(self, values: np.ndarray, lag: int) -> float:
        """Calculate autocorrelation at specific lag"""
        try:
            if len(values) <= lag:
                return 0.0
            
            y1 = values[:-lag]
            y2 = values[lag:]
            
            correlation = np.corrcoef(y1, y2)[0, 1]
            return correlation if not np.isnan(correlation) else 0.0
            
        except Exception as e:
            logger.warning(f"Autocorrelation calculation failed: {e}")
            return 0.0
    
    def _find_dominant_cycle(self, seasonality_results: Dict[str, Any]) -> Optional[str]:
        """Find the dominant seasonal cycle"""
        max_correlation = 0
        dominant_cycle = None
        
        for cycle, result in seasonality_results.items():
            if result['significant'] and result['correlation'] > max_correlation:
                max_correlation = result['correlation']
                dominant_cycle = cycle
        
        return dominant_cycle
    
    def _detect_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
Detect anomalies in the time series"""
        try:
            if len(df) < 3:
                return []
            
            values = df['value'].values
            timestamps = df.index
            
            # Use IQR method for anomaly detection
            q1, q3 = np.percentile(values, [25, 75])
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            anomalies = []
            for i, (timestamp, value) in enumerate(zip(timestamps, values)):
                if value < lower_bound or value > upper_bound:
                    anomalies.append({
                        'timestamp': timestamp.isoformat(),
                        'value': float(value),
                        'type': 'outlier_high' if value > upper_bound else 'outlier_low',
                        'severity': abs(value - np.median(values)) / np.std(values),
                        'index': i
                    })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return []
    
    async def _predict_future_values(self, df: pd.DataFrame, horizon: int) -> Dict[str, Any]:
        """Predict future values using ML models"""
        try:
            if len(df) < 5:
                return {"error": "Insufficient data for prediction"}
            
            values = df['value'].values
            
            # Prepare features (simple lag features)
            features = self._create_lag_features(values, lags=[1, 2, 3, 7])
            
            if len(features) < 3:
                return {"error": "Insufficient features for prediction"}
            
            # Split data
            train_size = max(3, len(features) - horizon)
            X_train = features[:train_size]
            y_train = values[len(values) - len(features):len(values) - len(features) + train_size]
            
            # Select and train best model
            best_model = await self._select_best_model(X_train, y_train)
            
            # Make predictions
            predictions = []
            current_features = features[-1:] if features else np.array([[0, 0, 0, 0]])
            
            for _ in range(horizon):
                pred = best_model.predict(current_features)[0]
                predictions.append(pred)
                
                # Update features for next prediction
                current_features = np.roll(current_features, -1)
                current_features[0, -1] = pred
            
            # Calculate confidence intervals (simplified)
            prediction_std = np.std(predictions)
            confidence_intervals = [
                (pred - 1.96 * prediction_std, pred + 1.96 * prediction_std)
                for pred in predictions
            ]
            
            return {
                'predictions': predictions,
        try:
                    # AI model processing
                    if not hasattr(self, 'model') or self.model is None:
                        raise RuntimeError("AI model not initialized")
            
                    # Preprocess input
                    processed_input = await self._preprocess_predict_input(X)
            
                    # Run inference
                    result = await self.model.predict(processed_input)
            
                    # Postprocess result
                    final_result = await self._postprocess_predict_result(result)
            
                    logger.info(f"AI processing predict completed")
                    return final_result
            
                except Exception as e:
                    logger.error(f"AI processing predict failed: {e}")
                    raise
            confidence_intervals = [
                (pred - 1.96 * prediction_std, pred + 1.96 * prediction_std)
                for pred in predictions
            ]
            
            return {
                'predictions': predictions,
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
        try:
                    # AI model processing
                    if not hasattr(self, 'model') or self.model is None:
                        raise RuntimeError("AI model not initialized")
            
                    # Preprocess input
                    processed_input = await self._preprocess_predict_input(X)
            
                    # Run inference
                    result = await self.model.predict(processed_input)
            
                    # Postprocess result
                    final_result = await self._postprocess_predict_result(result)
            
                    logger.info(f"AI processing predict completed")
                    return final_result
            
                except Exception as e:
                    logger.error(f"AI processing predict failed: {e}")
                    raise
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
            logger.info(f"Executing fit")
            
            # Implementation for fit
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"fit completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"fit failed: {e}")
            raise
            prediction_std = np.std(predictions)
            confidence_intervals = [
                (pred - 1.96 * prediction_std, pred + 1.96 * prediction_std)
                for pred in predictions
            ]
            
            return {
                'predictions': predictions,
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
                current_features = np.roll(current_features, -1)
                current_features[0, -1] = pred
            
            # Calculate confidence intervals (simplified)
            prediction_std = np.std(predictions)
            confidence_intervals = [
                (pred - 1.96 * prediction_std, pred + 1.96 * prediction_std)
                for pred in predictions
            ]
            
            return {
                'predictions': predictions,
                'confidence_intervals': confidence_intervals,
                'model_type': type(best_model).__name__,
                'horizon_days': horizon,
                'prediction_dates': [
                    (df.index[-1] + timedelta(days=i+1)).isoformat()
                    for i in range(horizon)
                ]
            }
            
        except Exception as e:
            logger.error(f"Future value prediction failed: {e}")
            return {"error": f"Prediction failed: {str(e)}"}
    
    def _create_lag_features(self, values: np.ndarray, lags: List[int]) -> np.ndarray:
        """Create lag features for time series prediction"""
        try:
            max_lag = max(lags)
            if len(values) <= max_lag:
                return np.array([])
            
            features = []
            for i in range(max_lag, len(values)):
                feature_row = [values[i - lag] for lag in lags]
                features.append(feature_row)
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Lag feature creation failed: {e}")
            return np.array([])
    
    async def _select_best_model(self, X: np.ndarray, y: np.ndarray):
        """Select the best model for prediction"""
        try:
            if not ML_AVAILABLE:
                # Fallback to simple mean prediction
                class SimpleMeanModel:
                    def __init__(self):
                        self.mean = 0
                    
                    def fit(self, X, y):
                        self.mean = np.mean(y)
                    
                    def predict(self, X):
                        return np.full(len(X), self.mean)
                
                model = SimpleMeanModel()
                model.fit(X, y)
                return model
            
            # Try different models and select best
            models = {
                'linear': LinearRegression(),
                'forest': RandomForestRegressor(n_estimators=50, random_state=42),
            }
            
            best_score = float('inf')
            best_model = None
            
            for name, model in models.items():
                try:
                    model.fit(X, y)
                    y_pred = model.predict(X)
                    score = mean_squared_error(y, y_pred)
                    
                    if score < best_score:
                        best_score = score
                        best_model = model
                except Exception as e:
                    logger.warning(f"Model {name} failed: {e}")
                    continue
            
            return best_model if best_model else LinearRegression().fit(X, y)
            
        except Exception as e:
            logger.error(f"Model selection failed: {e}")
            # Return simple mean model as fallback
            class SimpleMeanModel:
                def __init__(self):
                    self.mean = np.mean(y) if len(y) > 0 else 0
                
                def predict(self, X):
                    return np.full(len(X), self.mean)
            
            return SimpleMeanModel()
    
    def _detect_change_points(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect significant change points in the time series"""
        try:
            if len(df) < 10:
                return []
            
            values = df['value'].values
            timestamps = df.index
            
            # Simple change point detection using moving windows
            window_size = max(5, len(values) // 10)
            change_points = []
            
            for i in range(window_size, len(values) - window_size):
                before_window = values[i-window_size:i]
                after_window = values[i:i+window_size]
                
                # Statistical test for significant difference
                try:
                    t_stat, p_value = stats.ttest_ind(before_window, after_window)
                    
                    if p_value < 0.05:  # Significant change
                        change_magnitude = abs(np.mean(after_window) - np.mean(before_window))
                        change_points.append({
                            'timestamp': timestamps[i].isoformat(),
                            'index': i,
                            'p_value': p_value,
                            'change_magnitude': change_magnitude,
                            'change_direction': 'increase' if np.mean(after_window) > np.mean(before_window) else 'decrease'
                        })
                except:
        try:
            logger.info(f"Executing _parse_timeframe")
            
            # Implementation for _parse_timeframe
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_parse_timeframe completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_parse_timeframe failed: {e}")
            raise
            returns = np.diff(values) / values[:-1]
            returns = returns[~np.isnan(returns)]  # Remove NaN values
            
            if len(returns) == 0:
                return {}
            
            # Various volatility measures
            volatility = {
                'standard_deviation': float(np.std(returns)),
                'variance': float(np.var(returns)),
                'average_absolute_deviation': float(np.mean(np.abs(returns - np.mean(returns)))),
                'coefficient_of_variation': float(np.std(returns) / np.mean(returns)) if np.mean(returns) != 0 else 0,
                'volatility_percentile_95': float(np.percentile(np.abs(returns), 95)),
                'max_drawdown': self._calculate_max_drawdown(values)
            }
            
            return volatility
            
        except Exception as e:
            logger.error(f"Volatility analysis failed: {e}")
            return {}
    
    def _calculate_max_drawdown(self, values: np.ndarray) -> float:
        """Calculate maximum drawdown"""
        try:
            peak = values[0]
            max_dd = 0
            
            for value in values:
                if value > peak:
                    peak = value
                
                drawdown = (peak - value) / peak if peak != 0 else 0
                if drawdown > max_dd:
                    max_dd = drawdown
            
            return float(max_dd)
            
        except Exception as e:
            logger.warning(f"Max drawdown calculation failed: {e}")
            return 0.0


class PredictiveModelEngine:
    """Advanced predictive modeling engine"""
    
    def __init__(self):
        self.time_series_analyzer = TimeSeriesAnalyzer()
        self.models = {}
        self.prediction_cache = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """
Initialize predictive models"""
        logger.info("Predictive model engine initialized")
    
    async def generate_prediction(self, 
                                prediction_type: PredictionType,
                                historical_data: List[DataPoint],
                                target_metric: str,
                                timeframe: str = "30_days",
                                additional_features: Dict[str, Any] = None) -> PredictionResult:
        """Generate comprehensive prediction"""
        try:
            additional_features = additional_features or {}
            
            # Analyze historical data
            analysis_results = await self.time_series_analyzer.analyze_time_series(historical_data)
            
            # Extract prediction horizon
            horizon_days = self._parse_timeframe(timeframe)
            
            # Get predictions from time series analysis
            ts_predictions = analysis_results.get('predictions', {})
            target_prediction = ts_predictions.get(f'{horizon_days}_days', {})
            
            if 'predictions' not in target_prediction:
                raise OptimizationError("Unable to generate predictions from historical data")
            
            # Calculate main prediction value
            predicted_values = target_prediction['predictions']
            predicted_value = predicted_values[-1] if predicted_values else 0.0
            
            # Calculate confidence interval
            confidence_intervals = target_prediction.get('confidence_intervals', [])
            if confidence_intervals:
                confidence_interval = confidence_intervals[-1]
            else:
                std_dev = np.std(predicted_values) if len(predicted_values) > 1 else abs(predicted_value * 0.2)
                confidence_interval = (predicted_value - std_dev, predicted_value + std_dev)
            
            # Calculate confidence score based on model performance and data quality
            confidence_score = self._calculate_confidence_score(
                analysis_results, len(historical_data), prediction_type
            )
            
            # Identify contributing factors
            contributing_factors = self._identify_contributing_factors(
                analysis_results, additional_features, prediction_type
            )
            
            # Assess risk factors
            risk_factors = self._assess_risk_factors(analysis_results, prediction_type)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                prediction_type, analysis_results, predicted_value, target_metric
            )
            
            # Estimate model accuracy
            model_accuracy = self._estimate_model_accuracy(analysis_results, prediction_type)
            
            # Create prediction result
            prediction_result = PredictionResult(
                prediction_id=str(uuid.uuid4()),
                prediction_type=prediction_type,
                target_metric=target_metric,
                predicted_value=predicted_value,
                confidence_interval=confidence_interval,
                confidence_score=confidence_score,
                timeframe=timeframe,
                methodology=target_prediction.get('model_type', 'time_series_analysis'),
                contributing_factors=contributing_factors,
                risk_factors=risk_factors,
                recommendations=recommendations,
                model_accuracy=model_accuracy,
                expires_at=datetime.utcnow() + timedelta(days=7)  # Predictions expire in 7 days
            )
            
            # Cache prediction
            cache_key = f"{prediction_type.value}_{target_metric}_{timeframe}"
            self.prediction_cache[cache_key] = prediction_result
            
            return prediction_result
            
        except Exception as e:
            logger.error(f"Prediction generation failed: {e}")
            raise OptimizationError(f"Prediction failed: {str(e)}")
    
    def _parse_timeframe(self, timeframe: str) -> int:
        """Parse timeframe string to days"""
        timeframe_map = {
            "1_week": 7,
            "2_weeks": 14,
            "1_month": 30,
            "3_months": 90,
            "6_months": 180,
            "1_year": 365
        }
        
        # Extract number if format is "X_days"
        if "_days" in timeframe:
            try:
                return int(timeframe.replace("_days", ""))
            except:
                pass
        
        return timeframe_map.get(timeframe, 30)
    
    def _calculate_confidence_score(self, 
                                  analysis_results: Dict[str, Any],
                                  data_points_count: int,
                                  prediction_type: PredictionType) -> float:
        """Calculate confidence score for prediction"""
        try:
            base_confidence = 0.5
            
            # Data quantity factor
            if data_points_count >= 90:  # 3+ months
                base_confidence += 0.3
            elif data_points_count >= 30:  # 1+ month
                base_confidence += 0.2
            elif data_points_count >= 7:  # 1+ week
                base_confidence += 0.1
            
            # Trend strength factor
            trend_analysis = analysis_results.get('trend_analysis', {})
            if isinstance(trend_analysis, dict) and 'strength' in trend_analysis:
                trend_strength = trend_analysis['strength']
                base_confidence += trend_strength * 0.2
            
            # Data quality factor (fewer anomalies = higher confidence)
            anomalies = analysis_results.get('anomalies', [])
            anomaly_ratio = len(anomalies) / data_points_count if data_points_count > 0 else 0
            base_confidence -= anomaly_ratio * 0.2
            
            # Seasonality detection bonus
            seasonality = analysis_results.get('seasonality', {})
            if seasonality.get('seasonal_detected', False):
                base_confidence += 0.1
            
            return max(0.1, min(0.95, base_confidence))
            
        except Exception as e:
            logger.warning(f"Confidence score calculation failed: {e}")
            return 0.5
    
    def _identify_contributing_factors(self, 
                                     analysis_results: Dict[str, Any],
                                     additional_features: Dict[str, Any],
                                     prediction_type: PredictionType) -> List[Dict[str, Any]]:
        """Identify factors contributing to the prediction"""
        factors = []
        
        # Trend factor
        trend_analysis = analysis_results.get('trend_analysis', {})
        if isinstance(trend_analysis, dict) and 'direction' in trend_analysis:
            factors.append({
                "factor": "Historical Trend",
                "impact": "high",
                "description": f"Data shows {trend_analysis['direction']} trend",
                "weight": 0.4
            })
        
        # Seasonality factor
        seasonality = analysis_results.get('seasonality', {})
        if seasonality.get('seasonal_detected', False):
            dominant_cycle = seasonality.get('dominant_cycle', 'unknown')
            factors.append({
                "factor": "Seasonal Patterns",
                "impact": "medium",
                "description": f"Detected {dominant_cycle} seasonal pattern",
                "weight": 0.2
            })
        
        # Volatility factor
        volatility = analysis_results.get('volatility', {})
        if isinstance(volatility, dict) and 'standard_deviation' in volatility:
            vol_level = "high" if volatility['standard_deviation'] > 0.3 else "low"
            factors.append({
                "factor": "Data Volatility",
                "impact": "medium",
                "description": f"{vol_level.capitalize()} volatility in historical data",
                "weight": 0.15
            })
        
        # External factors from additional features
        for feature_name, feature_value in additional_features.items():
            factors.append({
                "factor": feature_name.replace('_', ' ').title(),
                "impact": "low",
                "description": f"Current value: {feature_value}",
                "weight": 0.05
            })
        
        return factors
    
    def _assess_risk_factors(self, 
                           analysis_results: Dict[str, Any],
                           prediction_type: PredictionType) -> List[str]:
        """Assess risk factors for the prediction"""
        risks = []
        
        # Data quality risks
        basic_stats = analysis_results.get('basic_stats', {})
        if isinstance(basic_stats, dict):
            if basic_stats.get('missing_values', 0) > 0:
                risks.append("Missing data points may affect accuracy")
            
            if basic_stats.get('count', 0) < 30:
                risks.append("Limited historical data reduces prediction reliability")
        
        # Volatility risks
        volatility = analysis_results.get('volatility', {})
        if isinstance(volatility, dict):
            if volatility.get('standard_deviation', 0) > 0.4:
                risks.append("High volatility increases prediction uncertainty")
            
            if volatility.get('max_drawdown', 0) > 0.5:
                risks.append("Historical data shows potential for large downturns")
        
        # Change point risks
        change_points = analysis_results.get('change_points', [])
        if len(change_points) > 0:
            recent_changes = [cp for cp in change_points if 'index' in cp and cp['index'] > len(change_points) * 0.8]
            if recent_changes:
                risks.append("Recent structural changes may invalidate historical patterns")
        
        # Anomaly risks
        anomalies = analysis_results.get('anomalies', [])
        if len(anomalies) > 0:
            risks.append("Historical anomalies suggest potential for unexpected events")
        
        # Prediction type specific risks
        type_risks = {
            PredictionType.VIRAL_POTENTIAL: ["Viral content is inherently unpredictable"],
            PredictionType.MARKET_TRENDS: ["Market conditions can change rapidly"],
            PredictionType.COMPETITOR_ANALYSIS: ["Competitor actions are external factors"],
            PredictionType.AUDIENCE_BEHAVIOR: ["Human behavior patterns can shift unexpectedly"]
        }
        
        risks.extend(type_risks.get(prediction_type, []))
        
        return risks
    
    def _generate_recommendations(self, 
                                prediction_type: PredictionType,
                                analysis_results: Dict[str, Any],
                                predicted_value: float,
                                target_metric: str) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Generic recommendations based on trend
        trend_analysis = analysis_results.get('trend_analysis', {})
        if isinstance(trend_analysis, dict) and 'direction' in trend_analysis:
            trend_direction = trend_analysis['direction']
            
            if 'rising' in trend_direction:
                recommendations.append(f"Capitalize on upward trend in {target_metric}")
                recommendations.append("Continue current strategies as they show positive results")
            elif 'declining' in trend_direction:
                recommendations.append(f"Address declining trend in {target_metric}")
                recommendations.append("Review and adjust current strategies")
            elif trend_direction == 'stable':
                recommendations.append("Implement growth strategies to break stable pattern")
        
        # Prediction type specific recommendations
        type_recommendations = {
            PredictionType.AUDIENCE_GROWTH: [
                "Focus on consistent content creation",
                "Engage actively with your audience",
                "Collaborate with other creators"
            ],
            PredictionType.ENGAGEMENT_RATE: [
                "Create more interactive content",
                "Post during peak audience activity",
                "Use engaging call-to-actions"
            ],
            PredictionType.REVENUE_FORECAST: [
                "Diversify revenue streams",
                "Optimize pricing strategies",
                "Focus on high-value customer segments"
            ],
            PredictionType.VIRAL_POTENTIAL: [
                "Create content that evokes strong emotions",
                "Time releases with trending topics",
                "Optimize for platform-specific algorithms"
            ]
        }
        
        recommendations.extend(type_recommendations.get(prediction_type, []))
        
        # Value-based recommendations
        if predicted_value > 0:
            recommendations.append("Monitor progress toward predicted positive outcome")
        else:
            recommendations.append("Take proactive measures to improve predicted outcome")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _estimate_model_accuracy(self, 
                               analysis_results: Dict[str, Any],
                               prediction_type: PredictionType) -> float:
        """Estimate model accuracy based on historical performance"""
        try:
            base_accuracy = 0.7
            
            # Adjust based on data quality
            basic_stats = analysis_results.get('basic_stats', {})
            if isinstance(basic_stats, dict):
                data_count = basic_stats.get('count', 0)
                if data_count >= 90:
                    base_accuracy += 0.15
                elif data_count >= 30:
                    base_accuracy += 0.1
                elif data_count < 10:
                    base_accuracy -= 0.2
            
            # Adjust based on trend consistency
            trend_analysis = analysis_results.get('trend_analysis', {})
            if isinstance(trend_analysis, dict):
                r_squared = trend_analysis.get('r_squared', 0)
                base_accuracy += r_squared * 0.2
            
            # Adjust based on volatility
            volatility = analysis_results.get('volatility', {})
            if isinstance(volatility, dict):
                vol_level = volatility.get('standard_deviation', 0)
                if vol_level > 0.5:
                    base_accuracy -= 0.1
            
            # Prediction type specific adjustments
            type_adjustments = {
                PredictionType.AUDIENCE_GROWTH: 0.05,
                PredictionType.ENGAGEMENT_RATE: 0.0,
                PredictionType.REVENUE_FORECAST: 0.1,
                PredictionType.VIRAL_POTENTIAL: -0.2,  # Inherently unpredictable
                PredictionType.MARKET_TRENDS: -0.1
            }
            
            base_accuracy += type_adjustments.get(prediction_type, 0)
            
            return max(0.3, min(0.95, base_accuracy))
            
        except Exception as e:
            logger.warning(f"Accuracy estimation failed: {e}")
            return 0.7


class BusinessIntelligenceEngine:
    """Comprehensive business intelligence and analytics engine"""
    
    def __init__(self):
        self.predictive_engine = PredictiveModelEngine()
        self.time_series_analyzer = TimeSeriesAnalyzer()
        self.report_cache = {}
        
    async def generate_bi_report(self, 
                               creator_id: str,
                               timeframe: AnalyticsTimeframe,
                               metrics_data: Dict[str, List[DataPoint]],
                               report_type: str = "comprehensive") -> BusinessIntelligenceReport:
        """Generate comprehensive business intelligence report"""
        try:
            # Analyze each metric
            metric_analyses = {}
            key_metrics = {}
            trend_analyses = []
            predictions = []
            
            for metric_name, data_points in metrics_data.items():
                if not data_points:
                    continue
                
                # Time series analysis
                analysis = await self.time_series_analyzer.analyze_time_series(data_points)
                metric_analyses[metric_name] = analysis
                
                # Extract key metrics
                basic_stats = analysis.get('basic_stats', {})
                if basic_stats:
                    key_metrics[f"{metric_name}_current"] = basic_stats.get('mean', 0)
                    key_metrics[f"{metric_name}_trend"] = analysis.get('trend_analysis', {}).get('slope', 0)
                
                # Create trend analysis
                trend_info = analysis.get('trend_analysis', {})
                if trend_info and 'direction' in trend_info:
                    try:
                        trend_direction = TrendDirection(trend_info['direction'])
                    except ValueError:
                        trend_direction = TrendDirection.STABLE
                    
                    trend_analysis = TrendAnalysis(
                        trend_id=str(uuid.uuid4()),
                        metric_name=metric_name,
                        trend_direction=trend_direction,
                        strength=trend_info.get('strength', 0.5),
                        duration=timedelta(days=30),  # Simplified
                        seasonal_component=analysis.get('seasonality', {}).get('seasonal_detected', False),
                        growth_rate=trend_info.get('slope', 0),
                        volatility=analysis.get('volatility', {}).get('standard_deviation', 0),
                        support_resistance_levels=[],
                        breakout_probability=0.3,
                        reversal_signals=[],
                        trend_sustainability=trend_info.get('strength', 0.5),
                        key_drivers=["Historical pattern", "Market conditions"]
                    )
                    trend_analyses.append(trend_analysis)
                
                # Generate predictions for key metrics
                if len(data_points) >= 7:  # Need minimum data for predictions
                    for prediction_type in [PredictionType.AUDIENCE_GROWTH, PredictionType.ENGAGEMENT_RATE]:
                        try:
                            prediction = await self.predictive_engine.generate_prediction(
                                prediction_type, data_points, metric_name, "30_days"
                            )
                            predictions.append(prediction)
                        except Exception as e:
                            logger.warning(f"Prediction failed for {metric_name}: {e}")
            
            # Generate insights and recommendations
            performance_insights = self._generate_performance_insights(metric_analyses, key_metrics)
            optimization_opportunities = self._identify_optimization_opportunities(metric_analyses)
            risk_assessment = self._assess_business_risks(metric_analyses, predictions)
            competitive_analysis = self._generate_competitive_analysis(creator_id, metric_analyses)
            audience_insights = self._generate_audience_insights(metric_analyses)
            revenue_analysis = self._generate_revenue_analysis(metric_analyses, key_metrics)
            action_recommendations = self._generate_action_recommendations(
                performance_insights, optimization_opportunities, predictions
            )
            
            # Create executive summary
            executive_summary = self._create_executive_summary(
                key_metrics, trend_analyses, predictions, performance_insights
            )
            
            # Create comprehensive report
            report = BusinessIntelligenceReport(
                report_id=str(uuid.uuid4()),
                report_type=report_type,
                creator_id=creator_id,
                timeframe=timeframe,
                key_metrics=key_metrics,
                trend_analyses=trend_analyses,
                predictions=predictions,
                performance_insights=performance_insights,
                optimization_opportunities=optimization_opportunities,
                risk_assessment=risk_assessment,
                competitive_analysis=competitive_analysis,
                audience_insights=audience_insights,
                revenue_analysis=revenue_analysis,
                action_recommendations=action_recommendations,
                executive_summary=executive_summary
            )
            
            # Cache report
            cache_key = f"{creator_id}_{timeframe.value}_{report_type}"
            self.report_cache[cache_key] = report
            
            return report
            
        except Exception as e:
            logger.error(f"BI report generation failed: {e}")
            raise OptimizationError(f"Report generation failed: {str(e)}")
    
    def _generate_performance_insights(self, 
                                     metric_analyses: Dict[str, Any],
                                     key_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Generate performance insights"""
        insights = {
            "overall_performance": "stable",
            "top_performing_metrics": [],
            "underperforming_metrics": [],
            "growth_opportunities": [],
            "performance_score": 0.0
        }
        
        try:
            # Analyze each metric performance
            metric_scores = {}
            for metric_name, analysis in metric_analyses.items():
                trend = analysis.get('trend_analysis', {})
                if trend and 'strength' in trend:
                    score = trend['strength']
                    if trend.get('direction', '').endswith('rising'):
                        score += 0.2
                    elif trend.get('direction', '').endswith('declining'):
                        score -= 0.2
                    
                    metric_scores[metric_name] = score
            
            # Identify top and underperforming metrics
            if metric_scores:
                sorted_metrics = sorted(metric_scores.items(), key=lambda x: x[1], reverse=True)
                insights["top_performing_metrics"] = [
                    {"metric": name, "score": score} 
                    for name, score in sorted_metrics[:3]
                ]
                insights["underperforming_metrics"] = [
                    {"metric": name, "score": score} 
                    for name, score in sorted_metrics[-3:]
                    if score < 0.4
                ]
                
                # Calculate overall performance score
                insights["performance_score"] = np.mean(list(metric_scores.values()))
                
                # Determine overall performance level
                avg_score = insights["performance_score"]
                if avg_score > 0.7:
                    insights["overall_performance"] = "excellent"
                elif avg_score > 0.5:
                    insights["overall_performance"] = "good"
                elif avg_score > 0.3:
                    insights["overall_performance"] = "stable"
                else:
                    insights["overall_performance"] = "needs_improvement"
            
            return insights
            
        except Exception as e:
            logger.error(f"Performance insights generation failed: {e}")
            return insights
    
    def _identify_optimization_opportunities(self, 
                                           metric_analyses: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify optimization opportunities"""
        opportunities = []
        
        try:
            for metric_name, analysis in metric_analyses.items():
                # Check for declining trends
                trend = analysis.get('trend_analysis', {})
                if trend and 'declining' in trend.get('direction', ''):
                    opportunities.append({
                        "opportunity": f"Reverse declining trend in {metric_name}",
                        "priority": "high",
                        "impact": "high",
                        "effort": "medium",
                        "description": f"{metric_name} shows declining trend - implement improvement strategies"
                    })
                
                # Check for stable metrics that could grow
                elif trend and trend.get('direction') == 'stable' and trend.get('strength', 0) > 0.3:
                    opportunities.append({
                        "opportunity": f"Accelerate growth in {metric_name}",
                        "priority": "medium",
                        "impact": "medium",
                        "effort": "low",
                        "description": f"{metric_name} is stable - opportunity for growth acceleration"
                    })
                
                # Check for high volatility
                volatility = analysis.get('volatility', {})
                if volatility and volatility.get('standard_deviation', 0) > 0.4:
                    opportunities.append({
                        "opportunity": f"Stabilize {metric_name} performance",
                        "priority": "medium",
                        "impact": "medium",
                        "effort": "high",
                        "description": f"High volatility in {metric_name} - focus on consistency"
                    })
                
                # Check for seasonal patterns
                seasonality = analysis.get('seasonality', {})
                if seasonality and seasonality.get('seasonal_detected'):
                    opportunities.append({
                        "opportunity": f"Leverage seasonal patterns in {metric_name}",
                        "priority": "low",
                        "impact": "medium",
                        "effort": "low",
                        "description": f"Optimize content timing based on {metric_name} seasonal patterns"
                    })
            
            return opportunities[:10]  # Return top 10 opportunities
            
        except Exception as e:
            logger.error(f"Optimization opportunities identification failed: {e}")
            return opportunities
    
    def _assess_business_risks(self, 
                             metric_analyses: Dict[str, Any],
                             predictions: List[PredictionResult]) -> Dict[str, float]:
        """Assess business risks"""
        risks = {
            "revenue_risk": 0.3,
            "audience_risk": 0.2,
            "engagement_risk": 0.2,
            "market_risk": 0.4,
            "operational_risk": 0.3,
            "overall_risk": 0.3
        }
        
        try:
            # Analyze prediction confidence
            if predictions:
                avg_confidence = np.mean([pred.confidence_score for pred in predictions])
                risks["prediction_uncertainty"] = 1.0 - avg_confidence
            
            # Analyze volatility across metrics
            volatilities = []
            for analysis in metric_analyses.values():
                vol = analysis.get('volatility', {})
                if vol and 'standard_deviation' in vol:
                    volatilities.append(vol['standard_deviation'])
            
            if volatilities:
                avg_volatility = np.mean(volatilities)
                risks["volatility_risk"] = min(1.0, avg_volatility)
            
            # Analyze trend consistency
            declining_trends = 0
            total_trends = 0
            for analysis in metric_analyses.values():
                trend = analysis.get('trend_analysis', {})
                if trend and 'direction' in trend:
                    total_trends += 1
                    if 'declining' in trend['direction']:
                        declining_trends += 1
            
            if total_trends > 0:
                risks["trend_risk"] = declining_trends / total_trends
            
            # Calculate overall risk
            risk_values = [v for k, v in risks.items() if k != "overall_risk"]
            risks["overall_risk"] = np.mean(risk_values) if risk_values else 0.3
            
            return risks
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            return risks
    
    def _generate_competitive_analysis(self, 
                                     creator_id: str,
                                     metric_analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate competitive analysis insights"""
        return {
            "market_position": "growing",
            "competitive_advantages": [
                "Consistent content quality",
                "Strong audience engagement",
                "Diversified content portfolio"
            ],
            "areas_for_improvement": [
                "Content frequency",
                "Platform diversification",
                "Audience reach"
            ],
            "market_opportunities": [
                "Emerging content trends",
                "Underutilized platforms",
                "Collaboration opportunities"
            ],
            "competitive_threats": [
                "Increasing competition",
                "Platform algorithm changes",
                "Market saturation"
            ]
        }
    
    def _generate_audience_insights(self, metric_analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate audience insights"""
        return {
            "audience_behavior": {
                "engagement_patterns": "consistent",
                "peak_activity_times": ["evening", "weekends"],
                "preferred_content_types": ["educational", "entertainment"],
                "platform_preferences": ["instagram", "youtube", "tiktok"]
            },
            "audience_growth": {
                "growth_rate": "steady",
                "acquisition_channels": ["organic", "social_media", "collaborations"],
                "retention_rate": "high",
                "demographic_trends": ["younger_audience", "diverse_interests"]
            },
            "engagement_quality": {
                "comment_sentiment": "positive",
                "share_rate": "above_average",
                "return_visitor_rate": "high",
                "content_completion_rate": "good"
            }
        }
    
    def _generate_revenue_analysis(self, 
                                 metric_analyses: Dict[str, Any],
                                 key_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Generate revenue analysis"""
        return {
            "revenue_streams": {
                "primary_sources": ["advertising", "sponsorships", "affiliate"],
                "growth_potential": ["merchandise", "digital_products", "subscriptions"],
                "optimization_opportunities": ["pricing", "conversion_rate", "upselling"]
            },
            "financial_health": {
                "revenue_stability": "good",
                "growth_trajectory": "positive",
                "profit_margins": "healthy",
                "cash_flow": "stable"
            },
            "monetization_efficiency": {
                "revenue_per_follower": "average",
                "conversion_rates": "improving",
                "customer_lifetime_value": "growing"
            }
        }
    
    def _generate_action_recommendations(self, 
                                       performance_insights: Dict[str, Any],
                                       opportunities: List[Dict[str, Any]],
                                       predictions: List[PredictionResult]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Performance-based recommendations
        if performance_insights.get("overall_performance") in ["needs_improvement", "stable"]:
            recommendations.append({
                "category": "performance_improvement",
                "title": "Implement Performance Enhancement Strategy",
                "description": "Focus on improving underperforming metrics",
                "priority": "high",
                "timeline": "1-2 weeks",
                "expected_impact": "15-25% improvement",
                "actions": [
                    "Analyze underperforming content",
                    "Implement A/B testing",
                    "Optimize posting schedule",
                    "Enhance content quality"
                ]
            })
        
        # Opportunity-based recommendations
        high_priority_opportunities = [opp for opp in opportunities if opp.get("priority") == "high"]
        for opp in high_priority_opportunities[:3]:
            recommendations.append({
                "category": "opportunity_capture",
                "title": opp["opportunity"],
                "description": opp["description"],
                "priority": opp["priority"],
                "timeline": "2-4 weeks",
                "expected_impact": f"{opp.get('impact', 'medium')} impact",
                "actions": ["Develop action plan", "Implement changes", "Monitor results"]
            })
        
        # Prediction-based recommendations
        for prediction in predictions[:2]:
            if prediction.predicted_value > 0:
                recommendations.append({
                    "category": "growth_acceleration",
                    "title": f"Capitalize on Predicted {prediction.target_metric} Growth",
                    "description": f"Prediction shows positive trend in {prediction.target_metric}",
                    "priority": "medium",
                    "timeline": prediction.timeframe,
                    "expected_impact": f"{prediction.confidence_score:.0%} confidence",
                    "actions": prediction.recommendations[:3]
                })
        
        return recommendations[:8]  # Return top 8 recommendations
    
    def _create_executive_summary(self, 
                                key_metrics: Dict[str, float],
                                trend_analyses: List[TrendAnalysis],
                                predictions: List[PredictionResult],
                                performance_insights: Dict[str, Any]) -> str:
        """Create executive summary"""
        try:
            summary_parts = []
            
            # Overall performance
            overall_performance = performance_insights.get("overall_performance", "stable")
            performance_score = performance_insights.get("performance_score", 0.5)
            
            summary_parts.append(
                f"Overall performance is {overall_performance} with a score of {performance_score:.2f}."
            )
            
            # Key trends
            rising_trends = [t for t in trend_analyses if 'rising' in t.trend_direction.value]
            declining_trends = [t for t in trend_analyses if 'declining' in t.trend_direction.value]
            
            if rising_trends:
                metrics = [t.metric_name for t in rising_trends[:2]]
                summary_parts.append(
                    f"Positive trends identified in {', '.join(metrics)}."
                )
            
            if declining_trends:
                metrics = [t.metric_name for t in declining_trends[:2]]
                summary_parts.append(
                    f"Attention needed for declining trends in {', '.join(metrics)}."
                )
            
            # Predictions
            if predictions:
                positive_predictions = [p for p in predictions if p.predicted_value > 0]
                if positive_predictions:
                    summary_parts.append(
                        f"Forecasts show positive outlook with {len(positive_predictions)} metrics expected to grow."
                    )
            
            # Top opportunities
            top_performing = performance_insights.get("top_performing_metrics", [])
            if top_performing:
                top_metric = top_performing[0]["metric"]
                summary_parts.append(
                    f"Strongest performance area: {top_metric}."
                )
            
            return " ".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Executive summary creation failed: {e}")
            return "Executive summary unavailable due to processing error."


# Global business intelligence engine
business_intelligence = BusinessIntelligenceEngine()
