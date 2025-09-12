"""{{agent_name}} Trend Prediction Agent for Ainflue Platform
{{agent_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum
import asyncio
import json

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import TimeSeriesSplit
import torch
import torch.nn as nn
from transformers import pipeline, AutoTokenizer, AutoModel
from pydantic import BaseModel, Field, validator
import scipy.stats as stats

from ai.base_agent import BaseAIAgent
from ai.models import TrendModelManager
from analytics.time_series import TimeSeriesAnalyzer, SeasonalityDetector
from analytics.social_signals import SocialSignalProcessor
from analytics.market_data import MarketDataCollector
from analytics.content_analysis import ContentTrendAnalyzer
from core.config import get_settings
from utils.exceptions import TrendException
from monitoring.trend_metrics import TrendMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class TrendType(Enum):
    """Types of trends to predict"""
    CONTENT_POPULARITY = "content_popularity"
    HASHTAG_TRENDS = "hashtag_trends"
    ENGAGEMENT_RATES = "engagement_rates"
    VIRAL_POTENTIAL = "viral_potential"
    CREATOR_GROWTH = "creator_growth"
    MARKET_SENTIMENT = "market_sentiment"
    SEASONAL_PATTERNS = "seasonal_patterns"
    PLATFORM_ADOPTION = "platform_adoption"
    GENRE_POPULARITY = "genre_popularity"
    DEMOGRAPHIC_SHIFTS = "demographic_shifts"


class PredictionHorizon(Enum):
    """Prediction time horizons"""
    SHORT_TERM = "short_term"  # 1-7 days
    MEDIUM_TERM = "medium_term"  # 1-4 weeks
    LONG_TERM = "long_term"  # 1-6 months
    EXTENDED = "extended"  # 6+ months


class TrendConfidence(Enum):
    """Confidence levels for predictions"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class TrendDirection(Enum):
    """Trend direction indicators"""
    STRONGLY_DECLINING = "strongly_declining"
    DECLINING = "declining"
    STABLE = "stable"
    GROWING = "growing"
    STRONGLY_GROWING = "strongly_growing"
    VOLATILE = "volatile"


class TrendRequest(BaseModel):
    """Trend prediction request model"""
    trend_type: TrendType
    target: str  # The specific item to predict (hashtag, creator, content type, etc.)
    horizon: PredictionHorizon = PredictionHorizon.MEDIUM_TERM
    historical_data: Optional[Dict[str, Any]] = None
    context_data: Optional[Dict[str, Any]] = None
    include_confidence: bool = True
    include_factors: bool = True
    include_scenarios: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('target')
    def validate_target(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Target cannot be empty')
        return v.strip()


class TrendPrediction(BaseModel):
    """Trend prediction result"""
    value: float
    direction: TrendDirection
    confidence: float = Field(ge=0.0, le=1.0)
    growth_rate: float
    peak_estimate: Optional[datetime] = None
    decline_estimate: Optional[datetime] = None


class TrendFactor(BaseModel):
    """Factor influencing the trend"""
    name: str
    impact: float = Field(ge=-1.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    description: str


class TrendScenario(BaseModel):
    """Alternative trend scenario"""
    name: str
    probability: float = Field(ge=0.0, le=1.0)
    prediction: TrendPrediction
    description: str


class TrendResult(BaseModel):
    """Trend prediction result model"""
    target: str
    trend_type: TrendType
    horizon: PredictionHorizon
    prediction: TrendPrediction
    factors: List[TrendFactor] = Field(default_factory=list)
    scenarios: List[TrendScenario] = Field(default_factory=list)
    historical_analysis: Dict[str, Any] = Field(default_factory=dict)
    prediction_time: float
    model_performance: Dict[str, float] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TrendConfig(BaseModel):
    """Trend prediction configuration"""
    primary_model: str = "ensemble"
    enable_deep_learning: bool = True
    enable_sentiment_analysis: bool = True
    enable_social_signals: bool = True
    confidence_threshold: float = 0.6
    max_features: int = 50
    cross_validation_folds: int = 5
    seasonal_adjustment: bool = True
    outlier_detection: bool = True


class LSTMTrendModel(nn.Module):
    """LSTM model for trend prediction"""
    
    def __init__(self, input_size: int, hidden_size: int = 128, num_layers: int = 2):
        super(LSTMTrendModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_size, 1)
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x):
        h_0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        c_0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        
        if torch.cuda.is_available():
            h_0 = h_0.cuda()
            c_0 = c_0.cuda()
        
        out, _ = self.lstm(x, (h_0, c_0))
        out = self.dropout(out[:, -1, :])
        out = self.fc(out)
        
        return out


class {{agent_class_name}}(BaseAIAgent):
    """
    Advanced trend prediction agent for Ainflue platform.
    
    Features:
    - Multi-modal trend prediction (content, hashtags, creators)
    - Time series analysis with seasonality detection
    - Social signal integration
    - Ensemble modeling with ML and DL approaches
    - Confidence scoring and uncertainty quantification
    - Scenario analysis and factor attribution
    - Real-time trend monitoring
    - Performance tracking and model updating
    """
    
    def __init__(
        self,
        name: str = "{{agent_name}}",
        config: Optional[TrendConfig] = None,
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self.config = config or TrendConfig()
        
        # Initialize components
        self.model_manager = TrendModelManager()
        self.time_series_analyzer = TimeSeriesAnalyzer()
        self.seasonality_detector = SeasonalityDetector()
        self.social_signal_processor = SocialSignalProcessor()
        self.market_data_collector = MarketDataCollector()
        self.content_trend_analyzer = ContentTrendAnalyzer()
        
        # Initialize scalers
        self.feature_scaler = StandardScaler()
        self.target_scaler = MinMaxScaler()
        
        # Initialize metrics collector
        self.metrics = TrendMetricsCollector()
        
        # Load models
        self._load_models()
        
        logger.info(f"Trend prediction agent '{name}' initialized successfully")

    def _load_models(self) -> None:
        """Load and initialize prediction models"""
        try:
            # Initialize traditional ML models
            self.rf_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            self.gb_model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            
            self.linear_model = Ridge(alpha=1.0)
            
            # Initialize LSTM model if deep learning is enabled
            if self.config.enable_deep_learning:
                self.lstm_model = LSTMTrendModel(input_size=20)  # Will be adjusted based on features
                if torch.cuda.is_available():
                    self.lstm_model = self.lstm_model.cuda()
            
            # Initialize sentiment analysis pipeline if enabled
            if self.config.enable_sentiment_analysis:
                self.sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    device=0 if torch.cuda.is_available() else -1
                )
            
            logger.info("All trend prediction models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading trend models: {str(e)}")
            raise TrendException(f"Model loading failed: {str(e)}")

    async def predict_trend(
        self,
        request: TrendRequest
    ) -> TrendResult:
        """
        Predict trend for specified target.
        
        Args:
            request: Trend prediction request
            
        Returns:
            TrendResult with predictions and analysis
        """
        start_time = datetime.utcnow()
        
        try:
            # Collect and prepare data
            data = await self._collect_trend_data(request)
            
            # Extract features
            features = await self._extract_features(data, request)
            
            # Perform historical analysis
            historical_analysis = await self._analyze_historical_data(data, request)
            
            # Generate predictions
            prediction = await self._generate_prediction(features, request)
            
            # Identify influencing factors
            factors = []
            if request.include_factors:
                factors = await self._identify_trend_factors(features, prediction, request)
            
            # Generate scenarios
            scenarios = []
            if request.include_scenarios:
                scenarios = await self._generate_scenarios(features, prediction, request)
            
            # Calculate prediction time
            prediction_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Evaluate model performance
            model_performance = await self._evaluate_model_performance(data, features)
            
            # Create result
            result = TrendResult(
                target=request.target,
                trend_type=request.trend_type,
                horizon=request.horizon,
                prediction=prediction,
                factors=factors,
                scenarios=scenarios,
                historical_analysis=historical_analysis,
                prediction_time=prediction_time,
                model_performance=model_performance,
                metadata={
                    "data_points": len(data),
                    "feature_count": len(features) if isinstance(features, dict) else features.shape[1] if hasattr(features, 'shape') else 0,
                    "model_type": self.config.primary_model
                }
            )
            
            # Record metrics
            await self.metrics.record_prediction(request, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Trend prediction failed: {str(e)}")
            raise TrendException(f"Prediction failed: {str(e)}")

    async def _collect_trend_data(
        self,
        request: TrendRequest
    ) -> pd.DataFrame:
        """Collect relevant data for trend analysis"""
        try:
            data_sources = []
            
            # Use provided historical data
            if request.historical_data:
                historical_df = pd.DataFrame(request.historical_data)
                data_sources.append(historical_df)
            
            # Collect additional data based on trend type
            if request.trend_type == TrendType.CONTENT_POPULARITY:
                content_data = await self._collect_content_data(request.target)
                data_sources.append(content_data)
            
            elif request.trend_type == TrendType.HASHTAG_TRENDS:
                hashtag_data = await self._collect_hashtag_data(request.target)
                data_sources.append(hashtag_data)
            
            elif request.trend_type == TrendType.CREATOR_GROWTH:
                creator_data = await self._collect_creator_data(request.target)
                data_sources.append(creator_data)
            
            elif request.trend_type == TrendType.ENGAGEMENT_RATES:
                engagement_data = await self._collect_engagement_data(request.target)
                data_sources.append(engagement_data)
            
            # Collect social signals if enabled
            if self.config.enable_social_signals:
                social_data = await self.social_signal_processor.collect_signals(
                    target=request.target,
                    trend_type=request.trend_type
                )
                data_sources.append(social_data)
            
            # Collect market data
            market_data = await self.market_data_collector.collect_data(
                target=request.target,
                trend_type=request.trend_type
            )
            data_sources.append(market_data)
            
            # Merge all data sources
            if data_sources:
                combined_data = pd.concat(data_sources, axis=1, sort=False)
                combined_data = combined_data.fillna(method='ffill').fillna(0)
            else:
                # Create minimal dataset
                combined_data = pd.DataFrame({
                    'timestamp': pd.date_range(
                        start=datetime.now() - timedelta(days=30),
                        end=datetime.now(),
                        freq='D'
                    ),
                    'value': np.random.randn(31)  # Placeholder data
                })
            
            return combined_data
            
        except Exception as e:
            logger.error(f"Data collection failed: {str(e)}")
            raise TrendException(f"Data collection failed: {str(e)}")

    async def _extract_features(
        self,
        data: pd.DataFrame,
        request: TrendRequest
    ) -> np.ndarray:
        """Extract features for trend prediction"""
        try:
            features = []
            
            # Time-based features
            if 'timestamp' in data.columns:
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data.set_index('timestamp')
                
                # Extract temporal features
                features.extend([
                    data.index.dayofweek.values,
                    data.index.hour.values if hasattr(data.index, 'hour') else np.zeros(len(data)),
                    data.index.month.values,
                    data.index.quarter.values
                ])
            
            # Statistical features
            if 'value' in data.columns:
                value_series = data['value'].values
                window_size = min(7, len(value_series) // 2)
                
                if window_size > 0:
                    # Moving averages
                    ma_short = pd.Series(value_series).rolling(window=window_size).mean().fillna(0).values
                    ma_long = pd.Series(value_series).rolling(window=window_size*2).mean().fillna(0).values
                    
                    # Volatility
                    volatility = pd.Series(value_series).rolling(window=window_size).std().fillna(0).values
                    
                    # Momentum
                    momentum = np.gradient(value_series)
                    
                    features.extend([ma_short, ma_long, volatility, momentum])
            
            # Social signal features
            if self.config.enable_social_signals:
                social_features = await self._extract_social_features(data)
                features.extend(social_features)
            
            # Sentiment features
            if self.config.enable_sentiment_analysis:
                sentiment_features = await self._extract_sentiment_features(data, request)
                features.extend(sentiment_features)
            
            # Seasonal features
            if self.config.seasonal_adjustment:
                seasonal_features = await self._extract_seasonal_features(data)
                features.extend(seasonal_features)
            
            # Convert to numpy array
            features_array = np.column_stack(features) if features else np.array([]).reshape(len(data), 0)
            
            # Handle missing values
            features_array = np.nan_to_num(features_array)
            
            # Limit features if too many
            if features_array.shape[1] > self.config.max_features:
                # Use feature selection or dimensionality reduction
                features_array = features_array[:, :self.config.max_features]
            
            return features_array
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {str(e)}")
            raise TrendException(f"Feature extraction failed: {str(e)}")

    async def _generate_prediction(
        self,
        features: np.ndarray,
        request: TrendRequest
    ) -> TrendPrediction:
        """Generate trend prediction using ensemble methods"""
        try:
            if len(features) < 2:
                # Insufficient data for prediction
                return TrendPrediction(
                    value=0.0,
                    direction=TrendDirection.STABLE,
                    confidence=0.1,
                    growth_rate=0.0
                )
            
            # Prepare training data (use most recent data for prediction)
            X = features[:-1]  # All but last observation
            y = features[1:, 0] if features.shape[1] > 0 else np.arange(len(features)-1)  # Target values (shifted)
            
            if len(X) == 0 or len(y) == 0:
                return TrendPrediction(
                    value=0.0,
                    direction=TrendDirection.STABLE,
                    confidence=0.1,
                    growth_rate=0.0
                )
            
            predictions = []
            weights = []
            
            # Random Forest prediction
            try:
                self.rf_model.fit(X, y)
                rf_pred = self.rf_model.predict([features[-1]])[0]
                predictions.append(rf_pred)
                weights.append(0.3)
            except Exception:
                pass
            
            # Gradient Boosting prediction
            try:
                self.gb_model.fit(X, y)
                gb_pred = self.gb_model.predict([features[-1]])[0]
                predictions.append(gb_pred)
                weights.append(0.3)
            except Exception:
                pass
            
            # Linear model prediction
            try:
                self.linear_model.fit(X, y)
                linear_pred = self.linear_model.predict([features[-1]])[0]
                predictions.append(linear_pred)
                weights.append(0.2)
            except Exception:
                pass
            
            # LSTM prediction (if enabled and data is sufficient)
            if self.config.enable_deep_learning and len(X) > 10:
                try:
                    lstm_pred = await self._lstm_predict(features)
                    predictions.append(lstm_pred)
                    weights.append(0.2)
                except Exception:
                    pass
            
            # Ensemble prediction
            if predictions:
                weights = np.array(weights[:len(predictions)])
                weights = weights / weights.sum()  # Normalize weights
                ensemble_pred = np.average(predictions, weights=weights)
            else:
                ensemble_pred = 0.0
            
            # Calculate growth rate
            current_value = features[-1, 0] if features.shape[1] > 0 else 1.0
            growth_rate = (ensemble_pred - current_value) / max(abs(current_value), 1e-6)
            
            # Determine trend direction
            direction = self._determine_trend_direction(growth_rate, predictions)
            
            # Calculate confidence
            confidence = self._calculate_prediction_confidence(predictions, X, y)
            
            # Estimate timing (simplified)
            horizon_days = self._get_horizon_days(request.horizon)
            peak_estimate = datetime.utcnow() + timedelta(days=horizon_days // 2)
            decline_estimate = datetime.utcnow() + timedelta(days=horizon_days)
            
            return TrendPrediction(
                value=float(ensemble_pred),
                direction=direction,
                confidence=confidence,
                growth_rate=float(growth_rate),
                peak_estimate=peak_estimate if growth_rate > 0 else None,
                decline_estimate=decline_estimate if growth_rate < 0 else None
            )
            
        except Exception as e:
            logger.error(f"Prediction generation failed: {str(e)}")
            raise TrendException(f"Prediction generation failed: {str(e)}")

    async def _lstm_predict(self, features: np.ndarray) -> float:
        """Generate prediction using LSTM model"""
        try:
            # Prepare sequence data for LSTM
            sequence_length = min(10, len(features) // 2)
            if sequence_length < 2:
                return 0.0
            
            # Create sequences
            sequences = []
            for i in range(len(features) - sequence_length):
                sequences.append(features[i:i + sequence_length])
            
            if not sequences:
                return 0.0
            
            # Convert to tensor
            X_lstm = torch.FloatTensor(sequences)
            if torch.cuda.is_available():
                X_lstm = X_lstm.cuda()
            
            # Update model input size if needed
            if X_lstm.shape[2] != self.lstm_model.lstm.input_size:
                self.lstm_model = LSTMTrendModel(input_size=X_lstm.shape[2])
                if torch.cuda.is_available():
                    self.lstm_model = self.lstm_model.cuda()
            
            # Simple training (in production, this would be pre-trained)
            criterion = nn.MSELoss()
            optimizer = torch.optim.Adam(self.lstm_model.parameters(), lr=0.001)
            
            # Create targets (next values)
            y_lstm = torch.FloatTensor([features[i + sequence_length, 0] for i in range(len(sequences))])
            if torch.cuda.is_available():
                y_lstm = y_lstm.cuda()
            
            # Quick training
            self.lstm_model.train()
            for epoch in range(10):  # Quick training
                optimizer.zero_grad()
                outputs = self.lstm_model(X_lstm).squeeze()
                loss = criterion(outputs, y_lstm)
                loss.backward()
                optimizer.step()
            
            # Prediction
            self.lstm_model.eval()
            with torch.no_grad():
                last_sequence = torch.FloatTensor([features[-sequence_length:]]).unsqueeze(0)
                if torch.cuda.is_available():
                    last_sequence = last_sequence.cuda()
                pred = self.lstm_model(last_sequence).squeeze().item()
            
            return pred
            
        except Exception as e:
            logger.error(f"LSTM prediction failed: {str(e)}")
            return 0.0

    def _determine_trend_direction(
        self,
        growth_rate: float,
        predictions: List[float]
    ) -> TrendDirection:
        """Determine trend direction based on growth rate and prediction variance"""
        # Calculate prediction variance for volatility assessment
        pred_variance = np.var(predictions) if len(predictions) > 1 else 0.0
        
        # High variance indicates volatility
        if pred_variance > 1.0:
            return TrendDirection.VOLATILE
        
        # Classify based on growth rate
        if growth_rate > 0.2:
            return TrendDirection.STRONGLY_GROWING
        elif growth_rate > 0.05:
            return TrendDirection.GROWING
        elif growth_rate < -0.2:
            return TrendDirection.STRONGLY_DECLINING
        elif growth_rate < -0.05:
            return TrendDirection.DECLINING
        else:
            return TrendDirection.STABLE

    def _calculate_prediction_confidence(
        self,
        predictions: List[float],
        X: np.ndarray,
        y: np.ndarray
    ) -> float:
        """Calculate confidence score for predictions"""
        try:
            if len(predictions) < 2 or len(X) == 0:
                return 0.5
            
            # Prediction agreement (lower variance = higher confidence)
            pred_variance = np.var(predictions)
            agreement_score = 1.0 / (1.0 + pred_variance)
            
            # Data quality score (more data = higher confidence)
            data_score = min(len(X) / 50.0, 1.0)  # Normalize to 0-1
            
            # Model performance score (simplified)
            try:
                # Cross-validation score for confidence estimation
                cv_scores = []
                tscv = TimeSeriesSplit(n_splits=min(3, len(X) // 5))
                for train_idx, test_idx in tscv.split(X):
                    X_train, X_test = X[train_idx], X[test_idx]
                    y_train, y_test = y[train_idx], y[test_idx]
                    
                    # Simple model for CV
                    model = LinearRegression()
                    model.fit(X_train, y_train)
                    pred = model.predict(X_test)
                    score = 1.0 / (1.0 + mean_squared_error(y_test, pred))
                    cv_scores.append(score)
                
                model_score = np.mean(cv_scores) if cv_scores else 0.5
            except Exception:
                model_score = 0.5
            
            # Combine scores
            confidence = (agreement_score * 0.4 + data_score * 0.3 + model_score * 0.3)
            return float(np.clip(confidence, 0.0, 1.0))
            
        except Exception:
            return 0.5

    def _get_horizon_days(self, horizon: PredictionHorizon) -> int:
        """Get number of days for prediction horizon"""
        horizon_map = {
            PredictionHorizon.SHORT_TERM: 7,
            PredictionHorizon.MEDIUM_TERM: 30,
            PredictionHorizon.LONG_TERM: 180,
            PredictionHorizon.EXTENDED: 365
        }
        return horizon_map.get(horizon, 30)

    async def _collect_content_data(self, target: str) -> pd.DataFrame:
        """Collect content-related data"""
        # Placeholder implementation
        return pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=30, freq='D'),
            'views': np.random.exponential(1000, 30),
            'likes': np.random.exponential(100, 30),
            'shares': np.random.exponential(50, 30)
        })

    async def _collect_hashtag_data(self, target: str) -> pd.DataFrame:
        """Collect hashtag trend data"""
        # Placeholder implementation
        return pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=30, freq='D'),
            'mentions': np.random.exponential(500, 30),
            'reach': np.random.exponential(10000, 30)
        })

    async def _collect_creator_data(self, target: str) -> pd.DataFrame:
        """Collect creator growth data"""
        # Placeholder implementation
        return pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=30, freq='D'),
            'followers': np.cumsum(np.random.normal(10, 5, 30)) + 1000,
            'posts': np.random.poisson(2, 30),
            'engagement': np.random.beta(2, 5, 30)
        })

    async def _collect_engagement_data(self, target: str) -> pd.DataFrame:
        """Collect engagement metrics data"""
        # Placeholder implementation
        return pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=30, freq='D'),
            'engagement_rate': np.random.beta(2, 8, 30),
            'comments': np.random.exponential(20, 30),
            'saves': np.random.exponential(15, 30)
        })

    async def _extract_social_features(self, data: pd.DataFrame) -> List[np.ndarray]:
        """Extract social signal features"""
        # Placeholder implementation
        return [np.random.randn(len(data)) for _ in range(3)]

    async def _extract_sentiment_features(
        self,
        data: pd.DataFrame,
        request: TrendRequest
    ) -> List[np.ndarray]:
        """Extract sentiment-based features"""
        # Placeholder implementation
        return [np.random.randn(len(data)) for _ in range(2)]

    async def _extract_seasonal_features(self, data: pd.DataFrame) -> List[np.ndarray]:
        """Extract seasonal pattern features"""
        # Placeholder implementation
        return [np.sin(np.arange(len(data)) * 2 * np.pi / 7)]  # Weekly seasonality

    async def _analyze_historical_data(
        self,
        data: pd.DataFrame,
        request: TrendRequest
    ) -> Dict[str, Any]:
        """Analyze historical patterns in the data"""
        try:
            analysis = {}
            
            if 'value' in data.columns and len(data) > 1:
                values = data['value'].values
                
                # Basic statistics
                analysis['statistics'] = {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values)),
                    'min': float(np.min(values)),
                    'max': float(np.max(values)),
                    'trend': float(np.polyfit(range(len(values)), values, 1)[0])
                }
                
                # Seasonality detection
                if len(values) > 14:
                    analysis['seasonality'] = await self.seasonality_detector.detect(values)
                
                # Volatility analysis
                if len(values) > 2:
                    returns = np.diff(values) / values[:-1]
                    analysis['volatility'] = {
                        'daily_volatility': float(np.std(returns)),
                        'max_drawdown': float(np.min(np.cumsum(returns)))
                    }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Historical analysis failed: {str(e)}")
            return {}

    async def _identify_trend_factors(
        self,
        features: np.ndarray,
        prediction: TrendPrediction,
        request: TrendRequest
    ) -> List[TrendFactor]:
        """Identify factors influencing the trend"""
        try:
            factors = []
            
            # Feature importance from Random Forest
            if hasattr(self.rf_model, 'feature_importances_'):
                importances = self.rf_model.feature_importances_
                
                # Create factor names (simplified)
                factor_names = [
                    "Temporal Patterns", "Moving Average", "Volatility", "Momentum",
                    "Social Signals", "Sentiment", "Seasonality"
                ]
                
                for i, importance in enumerate(importances[:len(factor_names)]):
                    if importance > 0.05:  # Only significant factors
                        factor = TrendFactor(
                            name=factor_names[i % len(factor_names)],
                            impact=float(importance * (1 if prediction.growth_rate > 0 else -1)),
                            confidence=float(importance),
                            description=f"Factor with {importance:.2%} importance in prediction"
                        )
                        factors.append(factor)
            
            # Sort by impact magnitude
            factors.sort(key=lambda x: abs(x.impact), reverse=True)
            
            return factors[:10]  # Return top 10 factors
            
        except Exception as e:
            logger.error(f"Factor identification failed: {str(e)}")
            return []

    async def _generate_scenarios(
        self,
        features: np.ndarray,
        prediction: TrendPrediction,
        request: TrendRequest
    ) -> List[TrendScenario]:
        """Generate alternative trend scenarios"""
        try:
            scenarios = []
            
            # Optimistic scenario
            optimistic_pred = TrendPrediction(
                value=prediction.value * 1.3,
                direction=TrendDirection.STRONGLY_GROWING if prediction.growth_rate > 0 else TrendDirection.GROWING,
                confidence=prediction.confidence * 0.8,
                growth_rate=prediction.growth_rate * 1.5
            )
            
            scenarios.append(TrendScenario(
                name="Optimistic",
                probability=0.25,
                prediction=optimistic_pred,
                description="Best-case scenario with favorable conditions"
            ))
            
            # Pessimistic scenario
            pessimistic_pred = TrendPrediction(
                value=prediction.value * 0.7,
                direction=TrendDirection.DECLINING if prediction.growth_rate > 0 else TrendDirection.STRONGLY_DECLINING,
                confidence=prediction.confidence * 0.8,
                growth_rate=prediction.growth_rate * 0.5
            )
            
            scenarios.append(TrendScenario(
                name="Pessimistic",
                probability=0.25,
                prediction=pessimistic_pred,
                description="Worst-case scenario with unfavorable conditions"
            ))
            
            # Most likely scenario (base prediction)
            scenarios.append(TrendScenario(
                name="Most Likely",
                probability=0.5,
                prediction=prediction,
                description="Expected scenario based on current trends"
            ))
            
            return scenarios
            
        except Exception as e:
            logger.error(f"Scenario generation failed: {str(e)}")
            return []

    async def _evaluate_model_performance(
        self,
        data: pd.DataFrame,
        features: np.ndarray
    ) -> Dict[str, float]:
        """Evaluate model performance metrics"""
        try:
            if len(features) < 10:
                return {"insufficient_data": 1.0}
            
            # Split data for evaluation
            split_idx = int(len(features) * 0.8)
            X_train, X_test = features[:split_idx], features[split_idx:]
            
            if len(X_test) == 0:
                return {"insufficient_test_data": 1.0}
            
            # Simple evaluation using linear model
            y_train = np.arange(len(X_train))  # Simplified target
            y_test = np.arange(len(X_train), len(X_train) + len(X_test))
            
            model = LinearRegression()
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            return {
                "mse": float(mse),
                "mae": float(mae),
                "rmse": float(np.sqrt(mse))
            }
            
        except Exception as e:
            logger.error(f"Performance evaluation failed: {str(e)}")
            return {"evaluation_error": 1.0}

    async def monitor_trends(
        self,
        targets: List[str],
        trend_type: TrendType,
        update_interval: int = 3600  # seconds
    ) -> None:
        """Monitor trends in real-time"""
        logger.info(f"Starting trend monitoring for {len(targets)} targets")
        
        while True:
            try:
                for target in targets:
                    request = TrendRequest(
                        trend_type=trend_type,
                        target=target,
                        horizon=PredictionHorizon.SHORT_TERM
                    )
                    
                    result = await self.predict_trend(request)
                    
                    # Store or alert based on significant changes
                    await self._handle_trend_update(target, result)
                
                # Wait for next update
                await asyncio.sleep(update_interval)
                
            except Exception as e:
                logger.error(f"Trend monitoring error: {str(e)}")
                await asyncio.sleep(update_interval)

    async def _handle_trend_update(
        self,
        target: str,
        result: TrendResult
    ) -> None:
        """Handle trend update (store, alert, etc.)"""
        # Placeholder for trend update handling
        logger.info(f"Trend update for {target}: {result.prediction.direction.value}")

    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities"""
        return {
            "trend_types": [t.value for t in TrendType],
            "prediction_horizons": [h.value for h in PredictionHorizon],
            "trend_directions": [d.value for d in TrendDirection],
            "supports_ensemble": True,
            "supports_deep_learning": self.config.enable_deep_learning,
            "supports_real_time": True,
            "supports_scenarios": True,
            "max_features": self.config.max_features
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get trend prediction metrics"""
        return self.metrics.get_summary()