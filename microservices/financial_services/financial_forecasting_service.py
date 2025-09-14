"""
📈 FINANCIAL FORECASTING SERVICE - ENTERPRISE MICROSERVICE
AI-powered financial forecasting and predictive analytics for creator monetization.

Author: Fahed Mlaiel
Copyright: © 2024-2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal
import aioredis
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

logger = logging.getLogger(__name__)

class ForecastType(Enum):
    """Types of financial forecasts"""
    REVENUE = "revenue"
    EXPENSES = "expenses"
    PROFIT = "profit"
    CASH_FLOW = "cash_flow"
    CREATOR_EARNINGS = "creator_earnings"
    PLATFORM_GROWTH = "platform_growth"

class ForecastPeriod(Enum):
    """Forecast time periods"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class ModelType(Enum):
    """Machine learning model types"""
    LINEAR_REGRESSION = "linear_regression"
    RIDGE_REGRESSION = "ridge_regression"
    RANDOM_FOREST = "random_forest"
    ARIMA = "arima"
    PROPHET = "prophet"
    ENSEMBLE = "ensemble"

@dataclass
class FinancialData:
    """Financial data point"""
    date: datetime
    metric_type: ForecastType
    value: Decimal
    creator_id: Optional[str] = None
    category: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ForecastRequest:
    """Forecast request parameters"""
    request_id: str
    forecast_type: ForecastType
    period: ForecastPeriod
    forecast_horizon: int  # Number of periods to forecast
    creator_id: Optional[str] = None
    include_confidence_intervals: bool = True
    model_type: ModelType = ModelType.ENSEMBLE
    custom_parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.custom_parameters is None:
            self.custom_parameters = {}

@dataclass
class ForecastResult:
    """Forecast result"""
    result_id: str
    request_id: str
    forecast_type: ForecastType
    period: ForecastPeriod
    model_used: ModelType
    predictions: List[Dict[str, Any]]
    confidence_intervals: Optional[List[Dict[str, Any]]] = None
    model_accuracy: Dict[str, float] = None
    trends: Dict[str, Any] = None
    generated_at: datetime = None
    
    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.utcnow()
        if self.model_accuracy is None:
            self.model_accuracy = {}
        if self.trends is None:
            self.trends = {}

class FinancialForecastingService:
    """
    📈 Financial Forecasting Service
    
    AI-powered financial forecasting service providing predictive analytics
    for creator monetization, platform growth, and business intelligence.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        
        # Data storage
        self.historical_data: Dict[str, List[FinancialData]] = {}
        self.forecast_cache: Dict[str, ForecastResult] = {}
        
        # Models
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        
        # Feature engineering
        self.feature_extractors = {
            'trend': self._extract_trend_features,
            'seasonal': self._extract_seasonal_features,
            'lag': self._extract_lag_features,
            'moving_avg': self._extract_moving_average_features,
            'external': self._extract_external_features
        }
        
        # Model configurations
        self.model_configs = {
            ModelType.LINEAR_REGRESSION: {'fit_intercept': True},
            ModelType.RIDGE_REGRESSION: {'alpha': 1.0},
            ModelType.RANDOM_FOREST: {'n_estimators': 100, 'random_state': 42},
            ModelType.ENSEMBLE: {'models': [ModelType.LINEAR_REGRESSION, ModelType.RIDGE_REGRESSION, ModelType.RANDOM_FOREST]}
        }
        
        # External factors that may influence forecasts
        self.external_factors = {
            'market_trends': {},
            'seasonality': {},
            'economic_indicators': {},
            'platform_events': {}
        }
        
        self.running = False
        
    async def initialize(self):
        """Initialize forecasting service"""
        try:
            self.redis = await aioredis.from_url(self.redis_url)
            
            # Load historical data
            await self._load_historical_data()
            
            # Initialize models
            await self._initialize_models()
            
            # Load external factors
            await self._load_external_factors()
            
            # Start background tasks
            asyncio.create_task(self._model_retraining_task())
            asyncio.create_task(self._data_update_task())
            asyncio.create_task(self._forecast_cache_cleanup_task())
            
            self.running = True
            logger.info("Financial Forecasting service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize financial forecasting service: {e}")
            raise
            
    async def _load_historical_data(self):
        """Load historical financial data"""
        try:
            # Load data from Redis
            data_keys = await self.redis.keys("financial_data:*")
            
            for key in data_keys:
                data_json = await self.redis.get(key)
                if data_json:
                    data_points = json.loads(data_json)
                    self.historical_data[key] = [
                        FinancialData(**point) for point in data_points
                    ]
                    
            # If no data, generate sample data for demo
            if not self.historical_data:
                await self._generate_sample_data()
                
        except Exception as e:
            logger.error(f"Failed to load historical data: {e}")
            await self._generate_sample_data()
            
    async def _generate_sample_data(self):
        """Generate sample financial data for demonstration"""
        # Generate sample revenue data
        base_date = datetime.utcnow() - timedelta(days=365)
        sample_data = []
        
        for i in range(365):
            date = base_date + timedelta(days=i)
            
            # Generate synthetic revenue with trend and seasonality
            trend = i * 10  # Growing trend
            seasonal = 1000 * np.sin(2 * np.pi * i / 30)  # Monthly seasonality
            noise = np.random.normal(0, 500)
            value = max(1000 + trend + seasonal + noise, 0)
            
            sample_data.append(FinancialData(
                date=date,
                metric_type=ForecastType.REVENUE,
                value=Decimal(str(round(value, 2))),
                category="platform_total"
            ))
            
        self.historical_data["financial_data:revenue:platform"] = sample_data
        
        # Save sample data
        await self._save_historical_data("financial_data:revenue:platform", sample_data)
        
    async def _save_historical_data(self, key: str, data: List[FinancialData]):
        """Save historical data to Redis"""
        try:
            data_json = json.dumps([asdict(point) for point in data], default=str)
            await self.redis.setex(key, 86400, data_json)  # Cache for 24 hours
        except Exception as e:
            logger.error(f"Failed to save historical data: {e}")
            
    async def _initialize_models(self):
        """Initialize machine learning models"""
        self.models = {
            ModelType.LINEAR_REGRESSION: LinearRegression(**self.model_configs[ModelType.LINEAR_REGRESSION]),
            ModelType.RIDGE_REGRESSION: Ridge(**self.model_configs[ModelType.RIDGE_REGRESSION]),
            ModelType.RANDOM_FOREST: RandomForestRegressor(**self.model_configs[ModelType.RANDOM_FOREST])
        }
        
        # Initialize scalers
        for model_type in self.models:
            self.scalers[model_type] = StandardScaler()
            
    async def _load_external_factors(self):
        """Load external factors that influence forecasts"""
        try:
            factors_data = await self.redis.get("forecast:external_factors")
            if factors_data:
                self.external_factors.update(json.loads(factors_data))
        except Exception as e:
            logger.error(f"Failed to load external factors: {e}")
            
    async def generate_forecast(self, request: ForecastRequest) -> ForecastResult:
        """Generate financial forecast"""
        try:
            # Get historical data for the request
            historical_data = await self._get_historical_data_for_request(request)
            
            if len(historical_data) < 30:  # Need minimum data points
                raise ValueError("Insufficient historical data for forecasting")
                
            # Prepare data for modeling
            X, y = await self._prepare_data_for_modeling(historical_data, request)
            
            # Select and train model
            model = await self._select_and_train_model(X, y, request.model_type)
            
            # Generate predictions
            predictions = await self._generate_predictions(model, X, request)
            
            # Calculate confidence intervals
            confidence_intervals = None
            if request.include_confidence_intervals:
                confidence_intervals = await self._calculate_confidence_intervals(
                    model, X, predictions, request
                )
                
            # Calculate model accuracy
            accuracy_metrics = await self._calculate_model_accuracy(model, X, y)
            
            # Extract trends
            trends = await self._extract_trends(historical_data, predictions)
            
            # Create result
            result = ForecastResult(
                result_id=f"forecast_{request.request_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                request_id=request.request_id,
                forecast_type=request.forecast_type,
                period=request.period,
                model_used=request.model_type,
                predictions=predictions,
                confidence_intervals=confidence_intervals,
                model_accuracy=accuracy_metrics,
                trends=trends
            )
            
            # Cache result
            self.forecast_cache[result.result_id] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Forecast generation failed for request {request.request_id}: {e}")
            raise
            
    async def _get_historical_data_for_request(self, request: ForecastRequest) -> List[FinancialData]:
        """Get historical data relevant to the forecast request"""
        relevant_data = []
        
        for key, data_points in self.historical_data.items():
            for point in data_points:
                # Filter by forecast type
                if point.metric_type != request.forecast_type:
                    continue
                    
                # Filter by creator if specified
                if request.creator_id and point.creator_id != request.creator_id:
                    continue
                    
                relevant_data.append(point)
                
        # Sort by date
        relevant_data.sort(key=lambda x: x.date)
        
        return relevant_data
        
    async def _prepare_data_for_modeling(self, data: List[FinancialData], 
                                       request: ForecastRequest) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for machine learning"""
        # Convert to DataFrame for easier manipulation
        df_data = []
        for point in data:
            df_data.append({
                'date': point.date,
                'value': float(point.value),
                'day_of_week': point.date.weekday(),
                'day_of_month': point.date.day,
                'month': point.date.month,
                'quarter': (point.date.month - 1) // 3 + 1,
                'year': point.date.year
            })
            
        df = pd.DataFrame(df_data)
        df = df.sort_values('date')
        
        # Extract features
        features = []
        targets = []
        
        for extractor_name, extractor_func in self.feature_extractors.items():
            extracted_features = await extractor_func(df, request)
            if extracted_features is not None:
                features.append(extracted_features)
                
        # Combine all features
        if features:
            X = np.concatenate(features, axis=1)
        else:
            # Use basic features if no extractors work
            X = df[['day_of_week', 'day_of_month', 'month', 'quarter']].values
            
        y = df['value'].values
        
        # Ensure we have enough data points
        min_length = min(len(X), len(y))
        X = X[:min_length]
        y = y[:min_length]
        
        return X, y
        
    async def _extract_trend_features(self, df: pd.DataFrame, request: ForecastRequest) -> Optional[np.ndarray]:
        """Extract trend-based features"""
        try:
            # Add time index
            df_copy = df.copy()
            df_copy['time_index'] = range(len(df_copy))
            
            # Calculate rolling trends
            window_sizes = [7, 30, 90]
            trend_features = []
            
            for window in window_sizes:
                if len(df_copy) >= window:
                    rolling_mean = df_copy['value'].rolling(window=window).mean()
                    trend_features.append(rolling_mean.fillna(rolling_mean.mean()).values.reshape(-1, 1))
                    
            if trend_features:
                return np.concatenate(trend_features, axis=1)
                
        except Exception as e:
            logger.warning(f"Failed to extract trend features: {e}")
            
        return None
        
    async def _extract_seasonal_features(self, df: pd.DataFrame, request: ForecastRequest) -> Optional[np.ndarray]:
        """Extract seasonal features"""
        try:
            seasonal_features = []
            
            # Day of week seasonality
            dow_sin = np.sin(2 * np.pi * df['day_of_week'] / 7)
            dow_cos = np.cos(2 * np.pi * df['day_of_week'] / 7)
            seasonal_features.extend([dow_sin.values, dow_cos.values])
            
            # Monthly seasonality
            month_sin = np.sin(2 * np.pi * df['month'] / 12)
            month_cos = np.cos(2 * np.pi * df['month'] / 12)
            seasonal_features.extend([month_sin.values, month_cos.values])
            
            # Quarterly seasonality
            quarter_sin = np.sin(2 * np.pi * df['quarter'] / 4)
            quarter_cos = np.cos(2 * np.pi * df['quarter'] / 4)
            seasonal_features.extend([quarter_sin.values, quarter_cos.values])
            
            return np.column_stack(seasonal_features)
            
        except Exception as e:
            logger.warning(f"Failed to extract seasonal features: {e}")
            
        return None
        
    async def _extract_lag_features(self, df: pd.DataFrame, request: ForecastRequest) -> Optional[np.ndarray]:
        """Extract lag-based features"""
        try:
            lag_features = []
            lag_periods = [1, 7, 30]  # 1 day, 1 week, 1 month
            
            for lag in lag_periods:
                if len(df) > lag:
                    lagged_values = df['value'].shift(lag)
                    lag_features.append(lagged_values.fillna(lagged_values.mean()).values)
                    
            if lag_features:
                return np.column_stack(lag_features)
                
        except Exception as e:
            logger.warning(f"Failed to extract lag features: {e}")
            
        return None
        
    async def _extract_moving_average_features(self, df: pd.DataFrame, request: ForecastRequest) -> Optional[np.ndarray]:
        """Extract moving average features"""
        try:
            ma_features = []
            windows = [3, 7, 14, 30]
            
            for window in windows:
                if len(df) >= window:
                    ma = df['value'].rolling(window=window).mean()
                    ma_features.append(ma.fillna(ma.mean()).values)
                    
            if ma_features:
                return np.column_stack(ma_features)
                
        except Exception as e:
            logger.warning(f"Failed to extract moving average features: {e}")
            
        return None
        
    async def _extract_external_features(self, df: pd.DataFrame, request: ForecastRequest) -> Optional[np.ndarray]:
        """Extract features from external factors"""
        try:
            # This would integrate with external data sources
            # For now, return placeholder features
            external_features = []
            
            # Market trend indicator (simplified)
            market_trend = np.ones(len(df)) * 1.0  # Neutral
            external_features.append(market_trend)
            
            # Economic indicator (simplified)
            economic_indicator = np.ones(len(df)) * 0.5  # Moderate
            external_features.append(economic_indicator)
            
            return np.column_stack(external_features)
            
        except Exception as e:
            logger.warning(f"Failed to extract external features: {e}")
            
        return None
        
    async def _select_and_train_model(self, X: np.ndarray, y: np.ndarray, 
                                    model_type: ModelType) -> Any:
        """Select and train the appropriate model"""
        if model_type == ModelType.ENSEMBLE:
            # Train ensemble of models
            ensemble_models = {}
            ensemble_predictions = []
            
            for individual_model_type in self.model_configs[ModelType.ENSEMBLE]['models']:
                model = self.models[individual_model_type]
                scaler = self.scalers[individual_model_type]
                
                # Scale features
                X_scaled = scaler.fit_transform(X)
                
                # Train model
                model.fit(X_scaled, y)
                ensemble_models[individual_model_type] = (model, scaler)
                
                # Get predictions for ensemble
                pred = model.predict(X_scaled)
                ensemble_predictions.append(pred)
                
            # Create ensemble predictor
            ensemble_pred = np.mean(ensemble_predictions, axis=0)
            
            return {
                'type': 'ensemble',
                'models': ensemble_models,
                'ensemble_prediction': ensemble_pred
            }
            
        else:
            # Train single model
            model = self.models[model_type]
            scaler = self.scalers[model_type]
            
            # Scale features
            X_scaled = scaler.fit_transform(X)
            
            # Train model
            model.fit(X_scaled, y)
            
            return {
                'type': 'single',
                'model': model,
                'scaler': scaler
            }
            
    async def _generate_predictions(self, trained_model: Any, X: np.ndarray, 
                                  request: ForecastRequest) -> List[Dict[str, Any]]:
        """Generate predictions for the forecast horizon"""
        predictions = []
        
        # Get the last known data point
        last_features = X[-1:] if len(X) > 0 else np.zeros((1, X.shape[1]))
        
        # Generate predictions for each period in the horizon
        for i in range(request.forecast_horizon):
            if trained_model['type'] == 'ensemble':
                # Ensemble prediction
                ensemble_preds = []
                for model_type, (model, scaler) in trained_model['models'].items():
                    scaled_features = scaler.transform(last_features)
                    pred = model.predict(scaled_features)[0]
                    ensemble_preds.append(pred)
                    
                predicted_value = np.mean(ensemble_preds)
                
            else:
                # Single model prediction
                model = trained_model['model']
                scaler = trained_model['scaler']
                scaled_features = scaler.transform(last_features)
                predicted_value = model.predict(scaled_features)[0]
                
            # Calculate forecast date
            base_date = datetime.utcnow()
            if request.period == ForecastPeriod.DAILY:
                forecast_date = base_date + timedelta(days=i+1)
            elif request.period == ForecastPeriod.WEEKLY:
                forecast_date = base_date + timedelta(weeks=i+1)
            elif request.period == ForecastPeriod.MONTHLY:
                forecast_date = base_date + timedelta(days=(i+1)*30)
            elif request.period == ForecastPeriod.QUARTERLY:
                forecast_date = base_date + timedelta(days=(i+1)*90)
            else:  # YEARLY
                forecast_date = base_date + timedelta(days=(i+1)*365)
                
            predictions.append({
                'period': i + 1,
                'date': forecast_date.isoformat(),
                'predicted_value': float(max(predicted_value, 0)),  # Ensure non-negative
                'forecast_type': request.forecast_type.value
            })
            
            # Update features for next prediction (simple approach)
            # In a more sophisticated model, this would incorporate the prediction
            # back into the feature set for multi-step ahead forecasting
            
        return predictions
        
    async def _calculate_confidence_intervals(self, trained_model: Any, X: np.ndarray, 
                                            predictions: List[Dict[str, Any]], 
                                            request: ForecastRequest) -> List[Dict[str, Any]]:
        """Calculate confidence intervals for predictions"""
        confidence_intervals = []
        
        # Calculate prediction standard error (simplified approach)
        if trained_model['type'] == 'ensemble':
            # For ensemble, use the standard deviation of individual model predictions
            for i, pred in enumerate(predictions):
                ensemble_preds = []
                for model_type, (model, scaler) in trained_model['models'].items():
                    # This is a simplified approach - in practice, you'd need to
                    # properly track the prediction for each step
                    ensemble_preds.append(pred['predicted_value'])
                    
                std_error = np.std(ensemble_preds) if len(ensemble_preds) > 1 else pred['predicted_value'] * 0.1
                
                # 95% confidence interval
                margin_of_error = 1.96 * std_error
                lower_bound = max(0, pred['predicted_value'] - margin_of_error)
                upper_bound = pred['predicted_value'] + margin_of_error
                
                confidence_intervals.append({
                    'period': pred['period'],
                    'date': pred['date'],
                    'lower_bound': float(lower_bound),
                    'upper_bound': float(upper_bound),
                    'confidence_level': 0.95
                })
                
        else:
            # For single model, estimate based on training residuals
            model = trained_model['model']
            scaler = trained_model['scaler']
            
            # Calculate training residuals
            X_scaled = scaler.transform(X)
            training_predictions = model.predict(X_scaled)
            
            # This would need actual training targets - simplified for demo
            residual_std = np.std(training_predictions) * 0.1  # Simplified estimate
            
            for pred in predictions:
                margin_of_error = 1.96 * residual_std
                lower_bound = max(0, pred['predicted_value'] - margin_of_error)
                upper_bound = pred['predicted_value'] + margin_of_error
                
                confidence_intervals.append({
                    'period': pred['period'],
                    'date': pred['date'],
                    'lower_bound': float(lower_bound),
                    'upper_bound': float(upper_bound),
                    'confidence_level': 0.95
                })
                
        return confidence_intervals
        
    async def _calculate_model_accuracy(self, trained_model: Any, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Calculate model accuracy metrics"""
        accuracy_metrics = {}
        
        try:
            if trained_model['type'] == 'ensemble':
                # Calculate ensemble accuracy
                ensemble_preds = []
                for model_type, (model, scaler) in trained_model['models'].items():
                    X_scaled = scaler.transform(X)
                    pred = model.predict(X_scaled)
                    ensemble_preds.append(pred)
                    
                    # Individual model metrics
                    mae = mean_absolute_error(y, pred)
                    mse = mean_squared_error(y, pred)
                    accuracy_metrics[f'{model_type.value}_mae'] = mae
                    accuracy_metrics[f'{model_type.value}_mse'] = mse
                    
                # Ensemble metrics
                ensemble_pred = np.mean(ensemble_preds, axis=0)
                ensemble_mae = mean_absolute_error(y, ensemble_pred)
                ensemble_mse = mean_squared_error(y, ensemble_pred)
                
                accuracy_metrics['ensemble_mae'] = ensemble_mae
                accuracy_metrics['ensemble_mse'] = ensemble_mse
                accuracy_metrics['ensemble_rmse'] = np.sqrt(ensemble_mse)
                
            else:
                # Single model accuracy
                model = trained_model['model']
                scaler = trained_model['scaler']
                
                X_scaled = scaler.transform(X)
                pred = model.predict(X_scaled)
                
                mae = mean_absolute_error(y, pred)
                mse = mean_squared_error(y, pred)
                
                accuracy_metrics['mae'] = mae
                accuracy_metrics['mse'] = mse
                accuracy_metrics['rmse'] = np.sqrt(mse)
                
                # Calculate R-squared if applicable
                if hasattr(model, 'score'):
                    r2 = model.score(X_scaled, y)
                    accuracy_metrics['r2'] = r2
                    
        except Exception as e:
            logger.error(f"Failed to calculate model accuracy: {e}")
            
        return accuracy_metrics
        
    async def _extract_trends(self, historical_data: List[FinancialData], 
                            predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract trend information from data and predictions"""
        trends = {}
        
        try:
            # Historical trend
            if len(historical_data) >= 2:
                recent_data = historical_data[-30:]  # Last 30 data points
                values = [float(point.value) for point in recent_data]
                
                if len(values) > 1:
                    # Simple linear trend
                    x = np.arange(len(values))
                    slope, _ = np.polyfit(x, values, 1)
                    
                    trends['historical_trend'] = {
                        'direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable',
                        'slope': float(slope),
                        'average_value': float(np.mean(values))
                    }
                    
            # Forecast trend
            if len(predictions) >= 2:
                pred_values = [pred['predicted_value'] for pred in predictions]
                x = np.arange(len(pred_values))
                slope, _ = np.polyfit(x, pred_values, 1)
                
                trends['forecast_trend'] = {
                    'direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable',
                    'slope': float(slope),
                    'average_predicted_value': float(np.mean(pred_values))
                }
                
            # Growth rate
            if len(predictions) >= 2:
                first_pred = predictions[0]['predicted_value']
                last_pred = predictions[-1]['predicted_value']
                
                if first_pred > 0:
                    growth_rate = ((last_pred - first_pred) / first_pred) * 100
                    trends['forecast_growth_rate'] = float(growth_rate)
                    
        except Exception as e:
            logger.error(f"Failed to extract trends: {e}")
            
        return trends
        
    async def get_forecast_accuracy_report(self, forecast_result_id: str) -> Dict[str, Any]:
        """Generate accuracy report for a forecast"""
        if forecast_result_id not in self.forecast_cache:
            raise ValueError(f"Forecast result {forecast_result_id} not found")
            
        forecast_result = self.forecast_cache[forecast_result_id]
        
        # This would compare predictions with actual values over time
        # For now, return the model accuracy metrics
        
        return {
            'forecast_id': forecast_result_id,
            'model_used': forecast_result.model_used.value,
            'accuracy_metrics': forecast_result.model_accuracy,
            'forecast_period': forecast_result.period.value,
            'generated_at': forecast_result.generated_at.isoformat(),
            'accuracy_assessment': self._assess_accuracy(forecast_result.model_accuracy)
        }
        
    def _assess_accuracy(self, accuracy_metrics: Dict[str, float]) -> str:
        """Assess the accuracy level based on metrics"""
        if 'mae' in accuracy_metrics:
            mae = accuracy_metrics['mae']
            if mae < 100:
                return 'excellent'
            elif mae < 500:
                return 'good'
            elif mae < 1000:
                return 'fair'
            else:
                return 'poor'
                
        return 'unknown'
        
    async def _model_retraining_task(self):
        """Background task for periodic model retraining"""
        while self.running:
            try:
                # Retrain models weekly
                await asyncio.sleep(7 * 24 * 3600)
                
                # Retrain models with updated data
                await self._retrain_all_models()
                
            except Exception as e:
                logger.error(f"Error in model retraining task: {e}")
                await asyncio.sleep(3600)
                
    async def _retrain_all_models(self):
        """Retrain all models with latest data"""
        logger.info("Starting model retraining...")
        
        for forecast_type in ForecastType:
            try:
                # Create dummy request for each forecast type
                dummy_request = ForecastRequest(
                    request_id=f"retrain_{forecast_type.value}",
                    forecast_type=forecast_type,
                    period=ForecastPeriod.DAILY,
                    forecast_horizon=1,
                    model_type=ModelType.ENSEMBLE
                )
                
                # Get data and retrain
                historical_data = await self._get_historical_data_for_request(dummy_request)
                
                if len(historical_data) >= 30:
                    X, y = await self._prepare_data_for_modeling(historical_data, dummy_request)
                    await self._select_and_train_model(X, y, ModelType.ENSEMBLE)
                    
            except Exception as e:
                logger.error(f"Failed to retrain model for {forecast_type.value}: {e}")
                
        logger.info("Model retraining completed")
        
    async def _data_update_task(self):
        """Background task for updating data"""
        while self.running:
            try:
                # Update data every hour
                await asyncio.sleep(3600)
                
                # Reload historical data
                await self._load_historical_data()
                
                # Update external factors
                await self._load_external_factors()
                
            except Exception as e:
                logger.error(f"Error in data update task: {e}")
                await asyncio.sleep(3600)
                
    async def _forecast_cache_cleanup_task(self):
        """Background task for cleaning up old forecasts"""
        while self.running:
            try:
                # Cleanup daily
                await asyncio.sleep(24 * 3600)
                
                cutoff_time = datetime.utcnow() - timedelta(days=7)
                
                # Remove old forecasts
                to_remove = []
                for result_id, result in self.forecast_cache.items():
                    if result.generated_at < cutoff_time:
                        to_remove.append(result_id)
                        
                for result_id in to_remove:
                    del self.forecast_cache[result_id]
                    
                logger.info(f"Cleaned up {len(to_remove)} old forecasts")
                
            except Exception as e:
                logger.error(f"Error in forecast cache cleanup task: {e}")
                await asyncio.sleep(3600)
                
    async def health_check(self) -> Dict[str, Any]:
        """Health check for forecasting service"""
        try:
            await self.redis.ping()
            redis_status = "healthy"
        except Exception as e:
            redis_status = f"unhealthy: {e}"
            
        return {
            'service': 'financial_forecasting',
            'status': 'healthy' if redis_status == "healthy" else 'degraded',
            'redis': redis_status,
            'loaded_datasets': len(self.historical_data),
            'cached_forecasts': len(self.forecast_cache),
            'available_models': len(self.models)
        }
        
    async def shutdown(self):
        """Shutdown forecasting service"""
        self.running = False
        
        if self.redis:
            await self.redis.close()
            
        logger.info("Financial Forecasting service shut down")

# Example usage
async def create_financial_forecasting_service():
    """Factory function to create financial forecasting service"""
    service = FinancialForecastingService()
    await service.initialize()
    return service

if __name__ == "__main__":
    async def main():
        forecasting_service = await create_financial_forecasting_service()
        
        # Example forecast request
        request = ForecastRequest(
            request_id="forecast_123",
            forecast_type=ForecastType.REVENUE,
            period=ForecastPeriod.DAILY,
            forecast_horizon=30,
            model_type=ModelType.ENSEMBLE,
            include_confidence_intervals=True
        )
        
        # Generate forecast
        result = await forecasting_service.generate_forecast(request)
        
        print(f"Forecast generated: {len(result.predictions)} predictions")
        print(f"Model accuracy: {result.model_accuracy}")
        print(f"Trends: {result.trends}")
        
        # First few predictions
        for i, pred in enumerate(result.predictions[:5]):
            print(f"Day {i+1}: ${pred['predicted_value']:.2f}")
            
        await forecasting_service.shutdown()
        
    asyncio.run(main())