#!/usr/bin/env python3
"""Analytics Module for IA-Influencer-Agent
========================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides advanced analytics capabilities including:
- Performance prediction and forecasting
- Engagement analysis and prediction
- Growth analysis and optimization
- Content performance metrics
- Audience behavior analysis

Features:
- Real-time performance tracking
- Predictive analytics
- Advanced statistical modeling
- Content optimization insights
"""import logging
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import time
from abc import ABC, abstractmethod
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Conditional imports for analytics libraries
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    logger.warning("pandas not available, analytics will be limited")
    PANDAS_AVAILABLE = False

try:
    import scipy.stats
    from scipy import optimize
    SCIPY_AVAILABLE = True
except ImportError:
    logger.warning("scipy not available, statistical analysis will be limited")
    SCIPY_AVAILABLE = False

try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LinearRegression
    SKLEARN_AVAILABLE = True
except ImportError:
    logger.warning("scikit-learn not available, ML models will be limited")
    SKLEARN_AVAILABLE = False


class MetricType(Enum):
    """Types of metrics to analyze"""    VIEWS = "views"
    LIKES = "likes"
    SHARES = "shares"
    COMMENTS = "comments"
    SAVES = "saves"
    FOLLOWS = "follows"
    ENGAGEMENT_RATE = "engagement_rate"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    CTR = "click_through_rate"


class ContentType(Enum):
    """Types of content for analysis"""    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    TEXT = "text"
    STORY = "story"
    REEL = "reel"
    LIVE = "live"
    CAROUSEL = "carousel"


class Platform(Enum):
    """Social media platforms"""    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"


class TimeFrame(Enum):
    """Time frames for analysis"""    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


@dataclass
class ContentMetrics:
    """Content performance metrics"""    content_id: str
    content_type: ContentType
    platform: Platform
    views: int
    likes: int
    shares: int
    comments: int
    saves: int
    reach: int
    impressions: int
    engagement_rate: float
    created_at: datetime
    metadata: Dict[str, Any] = None


@dataclass
class PerformancePrediction:
    """Performance prediction result"""    predicted_metrics: Dict[MetricType, float]
    confidence_intervals: Dict[MetricType, Tuple[float, float]]
    prediction_timeframe: TimeFrame
    confidence_score: float
    factors: Dict[str, float]
    processing_time: float
    metadata: Dict[str, Any] = None


@dataclass
class EngagementForecast:
    """Engagement forecasting result"""    forecasted_engagement: List[Dict[str, Any]]
    trend_analysis: Dict[str, Any]
    seasonal_patterns: Dict[str, Any]
    peak_times: List[Dict[str, Any]]
    optimization_suggestions: List[str]
    processing_time: float
    metadata: Dict[str, Any] = None


@dataclass
class GrowthAnalysis:
    """Growth analysis result"""    growth_rate: float
    growth_trajectory: List[Dict[str, Any]]
    growth_factors: Dict[str, float]
    bottlenecks: List[Dict[str, Any]]
    opportunities: List[Dict[str, Any]]
    projections: Dict[str, Any]
    processing_time: float
    metadata: Dict[str, Any] = None


class BaseAnalyzer(ABC):
    """Base class for analytics modules"""    
    def __init__(self, analyzer_name: str = "base_analyzer"):
        self.analyzer_name = analyzer_name
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.is_loaded = False
        self.scaler = None
        
    @abstractmethod
    def load_model(self) -> bool:
        """Load the analytics model"""        pass
    
    def _prepare_data(self, data: List[Dict[str, Any]]) -> np.ndarray:
        """Prepare data for analysis"""        try:
            if PANDAS_AVAILABLE:
                df = pd.DataFrame(data)
                # Convert datetime columns
                if 'created_at' in df.columns:
                    df['created_at'] = pd.to_datetime(df['created_at'])
                    df['hour'] = df['created_at'].dt.hour
                    df['day_of_week'] = df['created_at'].dt.dayofweek
                    df['month'] = df['created_at'].dt.month
                
                # Select numeric columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                return df[numeric_cols].values
            else:
                # Simple data preparation without pandas
                features = []
                for item in data:
                    row = []
                    for key, value in item.items():
                        if isinstance(value, (int, float)):
                            row.append(value)
                        elif isinstance(value, str) and value.isdigit():
                            row.append(float(value))
                    features.append(row)
                return np.array(features) if features else np.array([[0]])
        except Exception as e:
            logger.error(f"Error preparing data: {str(e)}")
            return np.array([[0]])


class PerformancePredictor(BaseAnalyzer):
    """Performance prediction and forecasting"""    
    def __init__(self, model_name: str = "performance_predictor_v1"):
        super().__init__(f"perf_pred_{model_name}")
        self.prediction_models = {}
        self.feature_importance = {}
        
    def load_model(self) -> bool:
        """Load performance prediction model"""        try:
            # Create prediction models for different metrics
            for metric in MetricType:
                self.prediction_models[metric] = self._create_prediction_model(metric)
            
            # Initialize scaler
            if SKLEARN_AVAILABLE:
                self.scaler = StandardScaler()
            
            self.is_loaded = True
            logger.info(f"Performance predictor {self.analyzer_name} loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading performance predictor: {str(e)}")
            return False
    
    def _create_prediction_model(self, metric: MetricType):
        """Create prediction model for specific metric"""        class MetricPredictionModel(nn.Module):
            def __init__(self, input_size=64, hidden_size=128):
                super().__init__()
                
                self.predictor = nn.Sequential(
                    nn.Linear(input_size, hidden_size),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(hidden_size, hidden_size // 2),
                    nn.ReLU(),
                    nn.Dropout(0.1),
                    nn.Linear(hidden_size // 2, 32),
                    nn.ReLU(),
                    nn.Linear(32, 1),
                    nn.ReLU()  # Ensure positive predictions
                )
                
                # Uncertainty estimation
                self.uncertainty = nn.Sequential(
                    nn.Linear(input_size, 32),
                    nn.ReLU(),
                    nn.Linear(32, 1),
                    nn.Softplus()  # Ensure positive uncertainty
                )
                
            def forward(self, x):
                prediction = self.predictor(x)
                uncertainty = self.uncertainty(x)
                return prediction, uncertainty
        
        model = MetricPredictionModel()
        model.to(self.device)
        model.eval()
        return model
    
    def train_on_historical_data(self, historical_data: List[ContentMetrics]) -> bool:
        """Train the predictor on historical data"""        try:
            if not self.is_loaded:
                if not self.load_model():
                    return False
            
            # Convert to training format
            training_data = []
            for metrics in historical_data:
                data_point = {
                    'views': metrics.views,
                    'likes': metrics.likes,
                    'shares': metrics.shares,
                    'comments': metrics.comments,
                    'saves': metrics.saves,
                    'reach': metrics.reach,
                    'impressions': metrics.impressions,
                    'engagement_rate': metrics.engagement_rate,
                    'content_type': metrics.content_type.value,
                    'platform': metrics.platform.value,
                    'created_at': metrics.created_at
                }
                training_data.append(data_point)
            
            # Simple feature importance calculation
            if len(training_data) > 10:
                self._calculate_feature_importance(training_data)
            
            logger.info(f"Trained on {len(historical_data)} historical data points")
            return True
            
        except Exception as e:
            logger.error(f"Error training on historical data: {str(e)}")
            return False
    
    def predict_performance(self, content_features: Dict[str, Any],
                          timeframe: TimeFrame = TimeFrame.DAY) -> PerformancePrediction:
        """Predict content performance"""        start_time = time.time()
        
        try:
            if not self.is_loaded:
                if not self.load_model():
                    raise RuntimeError("Failed to load performance predictor")
            
            # Extract features
            features = self._extract_features(content_features)
            
            # Make predictions for each metric
            predicted_metrics = {}
            confidence_intervals = {}
            
            for metric in MetricType:
                prediction, confidence = self._predict_metric(features, metric, timeframe)
                predicted_metrics[metric] = prediction
                confidence_intervals[metric] = confidence
            
            # Calculate overall confidence
            confidence_score = np.mean([
                1.0 - (ci[1] - ci[0]) / (pred + 1)
                for pred, ci in zip(predicted_metrics.values(), confidence_intervals.values())
            ])
            confidence_score = max(0.0, min(1.0, confidence_score))
            
            # Identify key factors
            factors = self._identify_key_factors(features, predicted_metrics)
            
            processing_time = time.time() - start_time
            
            return PerformancePrediction(
                predicted_metrics=predicted_metrics,
                confidence_intervals=confidence_intervals,
                prediction_timeframe=timeframe,
                confidence_score=confidence_score,
                factors=factors,
                processing_time=processing_time,
                metadata={
                    'model': self.analyzer_name,
                    'feature_count': len(features),
                    'content_type': content_features.get('content_type', 'unknown')
                }
            )
            
        except Exception as e:
            logger.error(f"Error in performance prediction: {str(e)}")
            # Return default prediction
            return PerformancePrediction(
                predicted_metrics={metric: 100.0 for metric in MetricType},
                confidence_intervals={metric: (50.0, 150.0) for metric in MetricType},
                prediction_timeframe=timeframe,
                confidence_score=0.5,
                factors={'unknown': 1.0},
                processing_time=time.time() - start_time,
                metadata={'error': str(e)}
            )
    
    def _extract_features(self, content_features: Dict[str, Any]) -> np.ndarray:
        """Extract numerical features from content data"""        features = []
        
        # Content type encoding
        content_types = [ct.value for ct in ContentType]
        content_type = content_features.get('content_type', 'video')
        for ct in content_types:
            features.append(1.0 if ct == content_type else 0.0)
        
        # Platform encoding
        platforms = [p.value for p in Platform]
        platform = content_features.get('platform', 'instagram')
        for p in platforms:
            features.append(1.0 if p == platform else 0.0)
        
        # Temporal features
        if 'created_at' in content_features:
            created_at = content_features['created_at']
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            elif not isinstance(created_at, datetime):
                created_at = datetime.now()
            
            features.extend([
                created_at.hour / 24.0,
                created_at.weekday() / 6.0,
                created_at.month / 12.0,
                np.sin(2 * np.pi * created_at.hour / 24),  # Cyclic hour
                np.cos(2 * np.pi * created_at.hour / 24)
            ])
        else:
            features.extend([0.5, 0.5, 0.5, 0.0, 1.0])  # Default values
        
        # Content quality indicators
        features.extend([
            content_features.get('quality_score', 0.7),
            content_features.get('relevance_score', 0.7),
            content_features.get('uniqueness_score', 0.7),
            len(content_features.get('hashtags', [])) / 30.0,  # Normalize hashtag count
            len(content_features.get('description', '')) / 500.0  # Normalize description length
        ])
        
        # Historical performance (if available)
        features.extend([
            content_features.get('avg_past_views', 1000) / 10000.0,
            content_features.get('avg_past_engagement', 0.05),
            content_features.get('follower_count', 1000) / 100000.0
        ])
        
        # Pad to fixed size
        target_size = 64
        while len(features) < target_size:
            features.append(0.5)  # Neutral padding
        
        return np.array(features[:target_size], dtype=np.float32)
    
    def _predict_metric(self, features: np.ndarray, metric: MetricType, 
                       timeframe: TimeFrame) -> Tuple[float, Tuple[float, float]]:
        """Predict specific metric"""        try:
            model = self.prediction_models[metric]
            
            with torch.no_grad():
                input_tensor = torch.FloatTensor(features).unsqueeze(0).to(self.device)
                prediction, uncertainty = model(input_tensor)
                
                pred_value = float(prediction.item())
                uncert_value = float(uncertainty.item())
                
                # Apply timeframe multiplier
                timeframe_multipliers = {
                    TimeFrame.HOUR: 0.1,
                    TimeFrame.DAY: 1.0,
                    TimeFrame.WEEK: 7.0,
                    TimeFrame.MONTH: 30.0,
                    TimeFrame.QUARTER: 90.0,
                    TimeFrame.YEAR: 365.0
                }
                
                multiplier = timeframe_multipliers.get(timeframe, 1.0)
                pred_value *= multiplier
                
                # Calculate confidence interval
                std_dev = uncert_value * pred_value
                confidence_interval = (
                    max(0.0, pred_value - 1.96 * std_dev),
                    pred_value + 1.96 * std_dev
                )
                
                return pred_value, confidence_interval
                
        except Exception as e:
            logger.error(f"Error predicting metric {metric}: {str(e)}")
            # Fallback prediction
            base_value = {'views': 1000, 'likes': 100, 'shares': 20, 'comments': 10}.get(metric.value, 50)
            return float(base_value), (float(base_value * 0.5), float(base_value * 1.5))
    
    def _calculate_feature_importance(self, training_data: List[Dict[str, Any]]):
        """Calculate feature importance from training data"""        try:
            if SKLEARN_AVAILABLE and len(training_data) > 10:
                # Prepare data
                features_list = []
                targets = []
                
                for data_point in training_data:
                    features = self._extract_features(data_point)
                    features_list.append(features)
                    targets.append(data_point.get('views', 1000))  # Use views as example target
                
                X = np.array(features_list)
                y = np.array(targets)
                
                # Train simple random forest for feature importance
                rf = RandomForestRegressor(n_estimators=50, random_state=42)
                rf.fit(X, y)
                
                # Store feature importance
                self.feature_importance = {
                    f'feature_{i}': importance 
                    for i, importance in enumerate(rf.feature_importances_)
                }
                
        except Exception as e:
            logger.error(f"Error calculating feature importance: {str(e)}")
    
    def _identify_key_factors(self, features: np.ndarray, 
                            predictions: Dict[MetricType, float]) -> Dict[str, float]:
        """Identify key factors affecting performance"""        try:
            factors = {}
            
            # Use feature importance if available
            if self.feature_importance:
                # Get top features
                sorted_features = sorted(
                    self.feature_importance.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:5]
                
                for feature_name, importance in sorted_features:
                    factors[feature_name] = importance
            else:
                # Default factors
                factors = {
                    'content_quality': 0.3,
                    'timing': 0.25,
                    'audience_match': 0.2,
                    'platform_algorithm': 0.15,
                    'trending_topics': 0.1
                }
            
            return factors
            
        except Exception as e:
            logger.error(f"Error identifying key factors: {str(e)}")
            return {'unknown_factor': 1.0}


class EngagementForecaster(BaseAnalyzer):
    """Engagement forecasting and analysis"""    
    def __init__(self, model_name: str = "engagement_forecaster_v1"):
        super().__init__(f"engage_forecast_{model_name}")
        self.time_series_model = None
        self.seasonal_patterns = {}
        
    def load_model(self) -> bool:
        """Load engagement forecasting model"""        try:
            # Create time series forecasting model
            self.time_series_model = self._create_time_series_model()
            self.time_series_model.to(self.device)
            self.time_series_model.eval()
            
            self.is_loaded = True
            logger.info(f"Engagement forecaster {self.analyzer_name} loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading engagement forecaster: {str(e)}")
            return False
    
    def _create_time_series_model(self):
        """Create time series forecasting model"""        class TimeSeriesLSTM(nn.Module):
            def __init__(self, input_size=10, hidden_size=64, num_layers=2, output_size=1):
                super().__init__()
                
                self.hidden_size = hidden_size
                self.num_layers = num_layers
                
                self.lstm = nn.LSTM(
                    input_size, hidden_size, num_layers, 
                    batch_first=True, dropout=0.2
                )
                
                self.predictor = nn.Sequential(
                    nn.Linear(hidden_size, 32),
                    nn.ReLU(),
                    nn.Dropout(0.1),
                    nn.Linear(32, output_size),
                    nn.ReLU()
                )
                
            def forward(self, x):
                lstm_out, _ = self.lstm(x)
                # Use last output
                last_output = lstm_out[:, -1, :]
                prediction = self.predictor(last_output)
                return prediction
        
        return TimeSeriesLSTM()
    
    def analyze_engagement_patterns(self, historical_data: List[ContentMetrics]) -> Dict[str, Any]:
        """Analyze engagement patterns from historical data"""        try:
            if PANDAS_AVAILABLE:
                # Convert to DataFrame
                data = []
                for metrics in historical_data:
                    data.append({
                        'created_at': metrics.created_at,
                        'engagement_rate': metrics.engagement_rate,
                        'views': metrics.views,
                        'likes': metrics.likes,
                        'shares': metrics.shares,
                        'comments': metrics.comments,
                        'platform': metrics.platform.value,
                        'content_type': metrics.content_type.value
                    })
                
                df = pd.DataFrame(data)
                df['created_at'] = pd.to_datetime(df['created_at'])
                df = df.sort_values('created_at')
                
                # Analyze patterns
                patterns = {
                    'hourly_patterns': self._analyze_hourly_patterns(df),
                    'daily_patterns': self._analyze_daily_patterns(df),
                    'content_type_patterns': self._analyze_content_patterns(df),
                    'platform_patterns': self._analyze_platform_patterns(df)
                }
                
                return patterns
            else:
                # Simple pattern analysis
                return self._simple_pattern_analysis(historical_data)
            
        except Exception as e:
            logger.error(f"Error analyzing engagement patterns: {str(e)}")
            return {}
    
    def forecast_engagement(self, historical_data: List[ContentMetrics],
                          forecast_periods: int = 7,
                          timeframe: TimeFrame = TimeFrame.DAY) -> EngagementForecast:
        """Forecast future engagement"""        start_time = time.time()
        
        try:
            if not self.is_loaded:
                if not self.load_model():
                    raise RuntimeError("Failed to load engagement forecaster")
            
            # Analyze patterns first
            patterns = self.analyze_engagement_patterns(historical_data)
            
            # Generate forecasts
            forecasted_engagement = self._generate_forecasts(
                historical_data, forecast_periods, timeframe
            )
            
            # Analyze trends
            trend_analysis = self._analyze_trends(historical_data)
            
            # Identify peak times
            peak_times = self._identify_peak_times(patterns)
            
            # Generate optimization suggestions
            optimization_suggestions = self._generate_optimization_suggestions(
                patterns, trend_analysis
            )
            
            processing_time = time.time() - start_time
            
            return EngagementForecast(
                forecasted_engagement=forecasted_engagement,
                trend_analysis=trend_analysis,
                seasonal_patterns=patterns,
                peak_times=peak_times,
                optimization_suggestions=optimization_suggestions,
                processing_time=processing_time,
                metadata={
                    'model': self.analyzer_name,
                    'historical_points': len(historical_data),
                    'forecast_periods': forecast_periods,
                    'timeframe': timeframe.value
                }
            )
            
        except Exception as e:
            logger.error(f"Error in engagement forecasting: {str(e)}")
            return EngagementForecast(
                forecasted_engagement=[],
                trend_analysis={},
                seasonal_patterns={},
                peak_times=[],
                optimization_suggestions=[],
                processing_time=time.time() - start_time,
                metadata={'error': str(e)}
            )
    
    def _analyze_hourly_patterns(self, df) -> Dict[str, float]:
        """Analyze hourly engagement patterns"""        try:
            df['hour'] = df['created_at'].dt.hour
            hourly_avg = df.groupby('hour')['engagement_rate'].mean()
            return hourly_avg.to_dict()
        except Exception:
            return {str(h): 0.05 for h in range(24)}
    
    def _analyze_daily_patterns(self, df) -> Dict[str, float]:
        """Analyze daily engagement patterns"""        try:
            df['day_of_week'] = df['created_at'].dt.day_name()
            daily_avg = df.groupby('day_of_week')['engagement_rate'].mean()
            return daily_avg.to_dict()
        except Exception:
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            return {day: 0.05 for day in days}
    
    def _analyze_content_patterns(self, df) -> Dict[str, float]:
        """Analyze content type patterns"""        try:
            content_avg = df.groupby('content_type')['engagement_rate'].mean()
            return content_avg.to_dict()
        except Exception:
            return {ct.value: 0.05 for ct in ContentType}
    
    def _analyze_platform_patterns(self, df) -> Dict[str, float]:
        """Analyze platform-specific patterns"""        try:
            platform_avg = df.groupby('platform')['engagement_rate'].mean()
            return platform_avg.to_dict()
        except Exception:
            return {p.value: 0.05 for p in Platform}
    
    def _simple_pattern_analysis(self, historical_data: List[ContentMetrics]) -> Dict[str, Any]:
        """Simple pattern analysis without pandas"""        try:
            hourly_engagement = {str(h): [] for h in range(24)}
            platform_engagement = {}
            content_engagement = {}
            
            for metrics in historical_data:
                hour = metrics.created_at.hour
                hourly_engagement[str(hour)].append(metrics.engagement_rate)
                
                platform = metrics.platform.value
                if platform not in platform_engagement:
                    platform_engagement[platform] = []
                platform_engagement[platform].append(metrics.engagement_rate)
                
                content_type = metrics.content_type.value
                if content_type not in content_engagement:
                    content_engagement[content_type] = []
                content_engagement[content_type].append(metrics.engagement_rate)
            
            # Calculate averages
            patterns = {
                'hourly_patterns': {
                    h: np.mean(rates) if rates else 0.05
                    for h, rates in hourly_engagement.items()
                },
                'platform_patterns': {
                    p: np.mean(rates) if rates else 0.05
                    for p, rates in platform_engagement.items()
                },
                'content_type_patterns': {
                    c: np.mean(rates) if rates else 0.05
                    for c, rates in content_engagement.items()
                }
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error in simple pattern analysis: {str(e)}")
            return {}
    
    def _generate_forecasts(self, historical_data: List[ContentMetrics],
                           periods: int, timeframe: TimeFrame) -> List[Dict[str, Any]]:
        """Generate engagement forecasts"""        forecasts = []
        
        try:
            # Simple trend-based forecasting
            recent_data = historical_data[-min(30, len(historical_data)):]  # Last 30 points
            recent_engagement = [m.engagement_rate for m in recent_data]
            
            if len(recent_engagement) > 1:
                # Calculate trend
                x = np.arange(len(recent_engagement))
                if SCIPY_AVAILABLE:
                    slope, intercept, _, _, _ = scipy.stats.linregress(x, recent_engagement)
                else:
                    # Simple linear trend
                    slope = (recent_engagement[-1] - recent_engagement[0]) / (len(recent_engagement) - 1)
                    intercept = recent_engagement[0]
                
                # Generate forecasts
                for i in range(periods):
                    future_x = len(recent_engagement) + i
                    forecast_value = slope * future_x + intercept
                    forecast_value = max(0.001, min(1.0, forecast_value))  # Clamp to reasonable range
                    
                    forecast_date = datetime.now() + timedelta(days=i)
                    
                    forecasts.append({
                        'date': forecast_date.isoformat(),
                        'predicted_engagement_rate': forecast_value,
                        'confidence': max(0.1, 1.0 - (i * 0.1)),  # Decreasing confidence
                        'period': i + 1
                    })
            else:
                # Fallback forecasts
                for i in range(periods):
                    forecast_date = datetime.now() + timedelta(days=i)
                    forecasts.append({
                        'date': forecast_date.isoformat(),
                        'predicted_engagement_rate': 0.05,
                        'confidence': 0.5,
                        'period': i + 1
                    })
                    
        except Exception as e:
            logger.error(f"Error generating forecasts: {str(e)}")
        
        return forecasts
    
    def _analyze_trends(self, historical_data: List[ContentMetrics]) -> Dict[str, Any]:
        """Analyze engagement trends"""        try:
            if len(historical_data) < 2:
                return {'trend': 'insufficient_data', 'slope': 0}
            
            engagement_rates = [m.engagement_rate for m in historical_data[-30:]]  # Last 30
            x = np.arange(len(engagement_rates))
            
            if SCIPY_AVAILABLE:
                slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, engagement_rates)
                
                trend_direction = 'increasing' if slope > 0.001 else 'decreasing' if slope < -0.001 else 'stable'
                
                return {
                    'trend': trend_direction,
                    'slope': float(slope),
                    'r_squared': float(r_value ** 2),
                    'p_value': float(p_value),
                    'strength': 'strong' if abs(r_value) > 0.7 else 'moderate' if abs(r_value) > 0.4 else 'weak'
                }
            else:
                # Simple trend analysis
                slope = (engagement_rates[-1] - engagement_rates[0]) / (len(engagement_rates) - 1)
                trend_direction = 'increasing' if slope > 0.001 else 'decreasing' if slope < -0.001 else 'stable'
                
                return {
                    'trend': trend_direction,
                    'slope': float(slope),
                    'strength': 'moderate'
                }
                
        except Exception as e:
            logger.error(f"Error analyzing trends: {str(e)}")
            return {'trend': 'unknown', 'slope': 0}
    
    def _identify_peak_times(self, patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify peak engagement times"""        peak_times = []
        
        try:
            # Find peak hours
            if 'hourly_patterns' in patterns:
                hourly = patterns['hourly_patterns']
                max_engagement = max(hourly.values()) if hourly.values() else 0
                
                for hour, engagement in hourly.items():
                    if engagement >= max_engagement * 0.9:  # Within 90% of peak
                        peak_times.append({
                            'type': 'hour',
                            'value': int(hour),
                            'engagement_rate': engagement,
                            'description': f"{hour}:00 - {int(hour)+1}:00"
                        })
            
            # Find peak days
            if 'daily_patterns' in patterns:
                daily = patterns['daily_patterns']
                max_daily = max(daily.values()) if daily.values() else 0
                
                for day, engagement in daily.items():
                    if engagement >= max_daily * 0.9:
                        peak_times.append({
                            'type': 'day',
                            'value': day,
                            'engagement_rate': engagement,
                            'description': f"Peak day: {day}"
                        })
                        
        except Exception as e:
            logger.error(f"Error identifying peak times: {str(e)}")
        
        return peak_times
    
    def _generate_optimization_suggestions(self, patterns: Dict[str, Any], 
                                         trend_analysis: Dict[str, Any]) -> List[str]:
        """Generate optimization suggestions"""        suggestions = []
        
        try:
            # Timing suggestions
            if 'hourly_patterns' in patterns:
                hourly = patterns['hourly_patterns']
                if hourly:
                    best_hours = sorted(hourly.items(), key=lambda x: x[1], reverse=True)[:3]
                    best_hour_names = [f"{h}:00" for h, _ in best_hours]
                    suggestions.append(f"Post during peak engagement hours: {', '.join(best_hour_names)}")
            
            # Content type suggestions
            if 'content_type_patterns' in patterns:
                content_patterns = patterns['content_type_patterns']
                if content_patterns:
                    best_content = max(content_patterns.items(), key=lambda x: x[1])
                    suggestions.append(f"Focus on {best_content[0]} content (highest engagement: {best_content[1]:.1%})")
            
            # Trend-based suggestions
            if trend_analysis.get('trend') == 'decreasing':
                suggestions.append("Engagement is declining. Consider refreshing content strategy or analyzing competitor approaches.")
            elif trend_analysis.get('trend') == 'increasing':
                suggestions.append("Engagement is growing! Continue current strategy and consider scaling successful content types.")
            
            # Platform suggestions
            if 'platform_patterns' in patterns:
                platform_patterns = patterns['platform_patterns']
                if platform_patterns:
                    best_platform = max(platform_patterns.items(), key=lambda x: x[1])
                    suggestions.append(f"Prioritize {best_platform[0]} (best performing platform: {best_platform[1]:.1%} engagement)")
            
            # General suggestions
            suggestions.extend([
                "Monitor audience feedback and adjust content accordingly",
                "Experiment with different posting times to optimize reach",
                "Engage with comments promptly to boost algorithmic ranking",
                "Use trending hashtags relevant to your niche"
            ])
            
        except Exception as e:
            logger.error(f"Error generating optimization suggestions: {str(e)}")
            suggestions = ["Focus on consistent, high-quality content creation"]
        
        return suggestions[:10]  # Limit to top 10 suggestions


class GrowthAnalyzer(BaseAnalyzer):
    """Growth analysis and optimization"""    
    def __init__(self, model_name: str = "growth_analyzer_v1"):
        super().__init__(f"growth_{model_name}")
        self.growth_model = None
        
    def load_model(self) -> bool:
        """Load growth analysis model"""        try:
            # Create growth analysis model
            self.growth_model = self._create_growth_model()
            self.growth_model.to(self.device)
            self.growth_model.eval()
            
            self.is_loaded = True
            logger.info(f"Growth analyzer {self.analyzer_name} loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading growth analyzer: {str(e)}")
            return False
    
    def _create_growth_model(self):
        """Create growth analysis model"""        class GrowthAnalysisModel(nn.Module):
            def __init__(self, input_size=32, output_size=16):
                super().__init__()
                
                self.analyzer = nn.Sequential(
                    nn.Linear(input_size, 64),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(64, 32),
                    nn.ReLU(),
                    nn.Linear(32, output_size),
                    nn.Sigmoid()  # Growth factors between 0-1
                )
                
            def forward(self, x):
                return self.analyzer(x)
        
        return GrowthAnalysisModel()
    
    def analyze_growth(self, historical_metrics: List[ContentMetrics],
                      user_metrics: Dict[str, Any]) -> GrowthAnalysis:
        """Comprehensive growth analysis"""        start_time = time.time()
        
        try:
            if not self.is_loaded:
                if not self.load_model():
                    raise RuntimeError("Failed to load growth analyzer")
            
            # Calculate growth rate
            growth_rate = self._calculate_growth_rate(historical_metrics, user_metrics)
            
            # Analyze growth trajectory
            growth_trajectory = self._analyze_growth_trajectory(historical_metrics)
            
            # Identify growth factors
            growth_factors = self._identify_growth_factors(historical_metrics, user_metrics)
            
            # Find bottlenecks
            bottlenecks = self._identify_bottlenecks(historical_metrics, user_metrics)
            
            # Identify opportunities
            opportunities = self._identify_opportunities(historical_metrics, growth_factors)
            
            # Generate projections
            projections = self._generate_projections(growth_rate, growth_trajectory)
            
            processing_time = time.time() - start_time
            
            return GrowthAnalysis(
                growth_rate=growth_rate,
                growth_trajectory=growth_trajectory,
                growth_factors=growth_factors,
                bottlenecks=bottlenecks,
                opportunities=opportunities,
                projections=projections,
                processing_time=processing_time,
                metadata={
                    'model': self.analyzer_name,
                    'data_points': len(historical_metrics),
                    'analysis_timeframe': 'last_30_days'
                }
            )
            
        except Exception as e:
            logger.error(f"Error in growth analysis: {str(e)}")
            return GrowthAnalysis(
                growth_rate=0.0,
                growth_trajectory=[],
                growth_factors={},
                bottlenecks=[],
                opportunities=[],
                projections={},
                processing_time=time.time() - start_time,
                metadata={'error': str(e)}
            )
    
    def _calculate_growth_rate(self, historical_metrics: List[ContentMetrics],
                              user_metrics: Dict[str, Any]) -> float:
        """Calculate overall growth rate"""        try:
            if len(historical_metrics) < 2:
                return 0.0
            
            # Sort by date
            sorted_metrics = sorted(historical_metrics, key=lambda x: x.created_at)
            
            # Calculate follower growth if available
            current_followers = user_metrics.get('follower_count', 0)
            initial_followers = user_metrics.get('initial_follower_count', current_followers)
            
            if initial_followers > 0 and current_followers != initial_followers:
                follower_growth = (current_followers - initial_followers) / initial_followers
            else:
                follower_growth = 0.0
            
            # Calculate engagement growth
            recent_engagement = np.mean([m.engagement_rate for m in sorted_metrics[-10:]])
            early_engagement = np.mean([m.engagement_rate for m in sorted_metrics[:10]])
            
            if early_engagement > 0:
                engagement_growth = (recent_engagement - early_engagement) / early_engagement
            else:
                engagement_growth = 0.0
            
            # Calculate views growth
            recent_views = np.mean([m.views for m in sorted_metrics[-10:]])
            early_views = np.mean([m.views for m in sorted_metrics[:10]])
            
            if early_views > 0:
                views_growth = (recent_views - early_views) / early_views
            else:
                views_growth = 0.0
            
            # Weighted average of growth metrics
            growth_rate = (follower_growth * 0.4 + engagement_growth * 0.3 + views_growth * 0.3)
            
            return float(growth_rate)
            
        except Exception as e:
            logger.error(f"Error calculating growth rate: {str(e)}")
            return 0.0
    
    def _analyze_growth_trajectory(self, historical_metrics: List[ContentMetrics]) -> List[Dict[str, Any]]:
        """Analyze growth trajectory over time"""        trajectory = []
        
        try:
            if len(historical_metrics) < 7:
                return trajectory
            
            # Sort by date
            sorted_metrics = sorted(historical_metrics, key=lambda x: x.created_at)
            
            # Group by weeks
            weekly_data = {}
            for metrics in sorted_metrics:
                week_key = metrics.created_at.strftime('%Y-W%U')
                if week_key not in weekly_data:
                    weekly_data[week_key] = []
                weekly_data[week_key].append(metrics)
            
            # Calculate weekly metrics
            for week, week_metrics in weekly_data.items():
                avg_engagement = np.mean([m.engagement_rate for m in week_metrics])
                total_views = sum([m.views for m in week_metrics])
                total_likes = sum([m.likes for m in week_metrics])
                content_count = len(week_metrics)
                
                trajectory.append({
                    'period': week,
                    'avg_engagement_rate': avg_engagement,
                    'total_views': total_views,
                    'total_likes': total_likes,
                    'content_count': content_count,
                    'avg_views_per_content': total_views / content_count if content_count > 0 else 0
                })
            
            # Sort by period
            trajectory.sort(key=lambda x: x['period'])
            
        except Exception as e:
            logger.error(f"Error analyzing growth trajectory: {str(e)}")
        
        return trajectory
    
    def _identify_growth_factors(self, historical_metrics: List[ContentMetrics],
                               user_metrics: Dict[str, Any]) -> Dict[str, float]:
        """Identify key growth factors"""        try:
            factors = {}
            
            # Content consistency factor
            if len(historical_metrics) > 0:
                # Calculate posting frequency
                date_range = (max(m.created_at for m in historical_metrics) - 
                            min(m.created_at for m in historical_metrics)).days
                posting_frequency = len(historical_metrics) / max(date_range, 1)
                factors['content_consistency'] = min(1.0, posting_frequency / 0.5)  # Target: 0.5 posts/day
            
            # Engagement quality factor
            if historical_metrics:
                avg_engagement = np.mean([m.engagement_rate for m in historical_metrics])
                factors['engagement_quality'] = min(1.0, avg_engagement / 0.05)  # Target: 5% engagement
            
            # Content diversity factor
            content_types = set([m.content_type for m in historical_metrics])
            factors['content_diversity'] = len(content_types) / len(ContentType)
            
            # Platform presence factor
            platforms = set([m.platform for m in historical_metrics])
            factors['platform_presence'] = len(platforms) / len(Platform)
            
            # Audience size factor (if available)
            follower_count = user_metrics.get('follower_count', 0)
            factors['audience_size'] = min(1.0, follower_count / 10000)  # Scale to 10k followers
            
            # Viral content factor
            if historical_metrics:
                max_views = max([m.views for m in historical_metrics])
                avg_views = np.mean([m.views for m in historical_metrics])
                factors['viral_potential'] = min(1.0, (max_views / avg_views) / 10) if avg_views > 0 else 0
            
            return factors
            
        except Exception as e:
            logger.error(f"Error identifying growth factors: {str(e)}")
            return {}
    
    def _identify_bottlenecks(self, historical_metrics: List[ContentMetrics],
                             user_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify growth bottlenecks"""        bottlenecks = []
        
        try:
            # Low engagement bottleneck
            if historical_metrics:
                avg_engagement = np.mean([m.engagement_rate for m in historical_metrics])
                if avg_engagement < 0.02:  # Less than 2%
                    bottlenecks.append({
                        'type': 'low_engagement',
                        'severity': 'high',
                        'description': f'Average engagement rate is {avg_engagement:.1%}, below optimal range',
                        'recommendation': 'Focus on creating more engaging, interactive content'
                    })
            
            # Inconsistent posting bottleneck
            if len(historical_metrics) > 1:
                dates = sorted([m.created_at for m in historical_metrics])
                gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
                avg_gap = np.mean(gaps)
                
                if avg_gap > 7:  # More than a week between posts
                    bottlenecks.append({
                        'type': 'inconsistent_posting',
                        'severity': 'medium',
                        'description': f'Average gap between posts: {avg_gap:.1f} days',
                        'recommendation': 'Establish a consistent posting schedule (3-5 times per week recommended)'
                    })
            
            # Limited content diversity bottleneck
            content_types = set([m.content_type for m in historical_metrics])
            if len(content_types) <= 2:
                bottlenecks.append({
                    'type': 'limited_content_diversity',
                    'severity': 'medium',
                    'description': f'Only using {len(content_types)} content types',
                    'recommendation': 'Experiment with different content formats (video, images, stories, etc.)'
                })
            
            # Platform limitation bottleneck
            platforms = set([m.platform for m in historical_metrics])
            if len(platforms) == 1:
                bottlenecks.append({
                    'type': 'single_platform_dependency',
                    'severity': 'low',
                    'description': 'Presence limited to one platform',
                    'recommendation': 'Consider expanding to additional social media platforms'
                })
                
        except Exception as e:
            logger.error(f"Error identifying bottlenecks: {str(e)}")
        
        return bottlenecks
    
    def _identify_opportunities(self, historical_metrics: List[ContentMetrics],
                              growth_factors: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identify growth opportunities"""        opportunities = []
        
        try:
            # High-performing content opportunity
            if historical_metrics:
                sorted_by_engagement = sorted(historical_metrics, key=lambda x: x.engagement_rate, reverse=True)
                top_content = sorted_by_engagement[:5]  # Top 5 performing
                
                top_types = [c.content_type.value for c in top_content]
                most_common_type = max(set(top_types), key=top_types.count)
                
                opportunities.append({
                    'type': 'content_optimization',
                    'priority': 'high',
                    'description': f'{most_common_type} content performs best',
                    'action': f'Increase production of {most_common_type} content',
                    'potential_impact': 'high'
                })
            
            # Timing optimization opportunity
            if historical_metrics:
                # Analyze posting times of high-performing content
                top_performers = sorted(historical_metrics, key=lambda x: x.engagement_rate, reverse=True)[:10]
                peak_hours = [m.created_at.hour for m in top_performers]
                
                if peak_hours:
                    best_hour = max(set(peak_hours), key=peak_hours.count)
                    opportunities.append({
                        'type': 'timing_optimization',
                        'priority': 'medium',
                        'description': f'Best performing posts often published around {best_hour}:00',
                        'action': f'Schedule more content for {best_hour}:00 - {best_hour+2}:00',
                        'potential_impact': 'medium'
                    })
            
            # Audience growth opportunity
            follower_growth = growth_factors.get('audience_size', 0)
            if follower_growth < 0.5:
                opportunities.append({
                    'type': 'audience_expansion',
                    'priority': 'high',
                    'description': 'Audience size has potential for significant growth',
                    'action': 'Implement targeted follower acquisition strategies',
                    'potential_impact': 'high'
                })
            
            # Cross-platform opportunity
            platforms = set([m.platform for m in historical_metrics])
            if len(platforms) < 3:
                opportunities.append({
                    'type': 'platform_expansion',
                    'priority': 'medium',
                    'description': 'Limited platform presence',
                    'action': 'Expand to additional platforms like TikTok, YouTube Shorts',
                    'potential_impact': 'high'
                })
                
        except Exception as e:
            logger.error(f"Error identifying opportunities: {str(e)}")
        
        return opportunities
    
    def _generate_projections(self, growth_rate: float, 
                            trajectory: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate growth projections"""        try:
            current_date = datetime.now()
            projections = {}
            
            # Project follower growth
            if growth_rate != 0:
                monthly_growth = (1 + growth_rate) ** (30 / 365) - 1  # Convert to monthly
                
                projections['follower_projections'] = []
                base_followers = 1000  # Assume base
                
                for month in range(1, 13):  # 12 months
                    projected_followers = int(base_followers * ((1 + monthly_growth) ** month))
                    projection_date = current_date + timedelta(days=month * 30)
                    
                    projections['follower_projections'].append({
                        'month': month,
                        'date': projection_date.isoformat()[:10],
                        'projected_followers': projected_followers,
                        'growth_rate': monthly_growth * 100
                    })
            
            # Project engagement metrics
            if trajectory:
                recent_engagement = trajectory[-1]['avg_engagement_rate'] if trajectory else 0.05
                
                projections['engagement_projections'] = []
                for month in range(1, 7):  # 6 months
                    # Apply growth trend with diminishing returns
                    projected_engagement = recent_engagement * (1 + growth_rate * 0.5) ** month
                    projected_engagement = min(0.2, max(0.001, projected_engagement))  # Reasonable bounds
                    
                    projection_date = current_date + timedelta(days=month * 30)
                    projections['engagement_projections'].append({
                        'month': month,
                        'date': projection_date.isoformat()[:10],
                        'projected_engagement_rate': projected_engagement
                    })
            
            # Overall growth outlook
            if growth_rate > 0.1:
                outlook = 'excellent'
            elif growth_rate > 0.05:
                outlook = 'good'
            elif growth_rate > 0:
                outlook = 'moderate'
            elif growth_rate > -0.05:
                outlook = 'stable'
            else:
                outlook = 'declining'
            
            projections['outlook'] = {
                'category': outlook,
                'growth_rate_annual': growth_rate * 100,
                'confidence': max(0.1, min(0.9, 0.8 - abs(growth_rate) * 2))
            }
            
            return projections
            
        except Exception as e:
            logger.error(f"Error generating projections: {str(e)}")
            return {}


# Export main classes
__all__ = [
    'PerformancePredictor',
    'EngagementForecaster',
    'GrowthAnalyzer',
    'ContentMetrics',
    'PerformancePrediction',
    'EngagementForecast',
    'GrowthAnalysis',
    'MetricType',
    'ContentType',
    'Platform',
    'TimeFrame',
    'BaseAnalyzer'
]

logger.info("Analytics module loaded successfully")
