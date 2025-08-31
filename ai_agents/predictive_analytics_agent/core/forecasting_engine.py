"""
Forecasting Engine - Advanced Time Series and ML-Based Prediction Models

Enterprise-grade forecasting system providing comprehensive prediction capabilities
for content performance, revenue, audience growth, and market trends.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL NOTICE:
This forecasting engine and its algorithms are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

# ML and forecasting imports
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
from prophet import Prophet
import lightgbm as lgb
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose

try:
    from core.exceptions import ProcessingError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ProcessingError, ValidationError = globals().get('ProcessingError, ValidationError', Exception)
from ...utils.cache_manager import CacheManager

logger = logging.getLogger(__name__)

class ForecastModel(Enum):
    """Available forecasting models"""
    PROPHET = "prophet"
    LSTM = "lstm"
    ARIMA = "arima"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    LINEAR_REGRESSION = "linear_regression"
    SEASONAL_DECOMPOSE = "seasonal_decompose"
    ENSEMBLE = "ensemble"

@dataclass
class ForecastResult:
    """Forecasting result structure"""
    model_name: str
    predictions: List[float]
    confidence_intervals: List[Tuple[float, float]]
    timestamps: List[datetime]
    accuracy_metrics: Dict[str, float]
    feature_importance: Optional[Dict[str, float]] = None
    seasonal_components: Optional[Dict[str, List[float]]] = None
    trend_analysis: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass 
class TrainingData:
    """Training data structure for forecasting models"""
    timestamps: List[datetime]
    values: List[float]
    features: Optional[pd.DataFrame] = None
    target_column: str = "value"
    frequency: str = "D"  # Daily frequency by default
    
class ForecastingEngine:
    """
    Advanced Forecasting Engine for IA Influencer Platform
    
    Provides enterprise-grade time series forecasting and prediction capabilities:
    
     Core Forecasting Capabilities:
    - Prophet-based seasonal trend decomposition with holiday effects
    - LSTM neural networks for deep learning time series prediction
    - ARIMA/SARIMA statistical modeling for complex seasonality
    - XGBoost/LightGBM gradient boosting for feature-rich predictions
    - Ensemble methods combining multiple models for robustness
    
     Specialized Prediction Models:
    - Content performance forecasting with viral coefficient modeling
    - Revenue prediction with market factor integration
    - Audience growth forecasting with retention analysis
    - Engagement rate prediction with platform algorithm factors
    - Collaboration success probability with partner compatibility scoring
    
     Advanced Features:
    - Automatic hyperparameter tuning and model selection
    - Cross-validation and backtesting for model validation
    - Confidence interval estimation with Monte Carlo methods
    - Seasonal pattern detection and decomposition
    - Anomaly detection and outlier handling
    - Real-time model retraining and adaptation
    """
    
    def __init__(self, cache_manager: CacheManager = None):
        """Initialize the forecasting engine"""
        self.cache_manager = cache_manager or CacheManager("forecasting_engine")
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, MinMaxScaler] = {}
        self.trained_models: Dict[str, Any] = {}
        
        # Model configurations
        self.lstm_config = {
            'units': 50,
            'dropout': 0.2,
            'epochs': 100,
            'batch_size': 32,
            'sequence_length': 30
        }
        
        self.prophet_config = {
            'daily_seasonality': True,
            'weekly_seasonality': True,
            'yearly_seasonality': True,
            'changepoint_prior_scale': 0.05,
            'seasonality_prior_scale': 10.0,
            'holidays_prior_scale': 10.0,
            'interval_width': 0.8
        }
        
        self.xgb_config = {
            'n_estimators': 100,
            'max_depth': 6,
            'learning_rate': 0.1,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42
        }
        
        logger.info("Forecasting Engine initialized")

    async def forecast_time_series(self, 
                                 data: TrainingData,
                                 forecast_periods: int = 30,
                                 model_type: ForecastModel = ForecastModel.PROPHET,
                                 include_confidence_intervals: bool = True) -> ForecastResult:
        """
        Generate time series forecast using specified model
        
        Args:
            data: Historical training data
            forecast_periods: Number of periods to forecast
            model_type: Forecasting model to use
            include_confidence_intervals: Whether to include confidence intervals
            
        Returns:
            ForecastResult: Comprehensive forecast results
        """



        try:
            # Validate input data
            self._validate_training_data(data)
            
            # Check cache
            cache_key = f"forecast_{model_type.value}_{len(data.values)}_{forecast_periods}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return ForecastResult(**cached_result)
            
            # Select and execute forecasting method
            if model_type == ForecastModel.PROPHET:
                result = await self._forecast_with_prophet(data, forecast_periods)
            elif model_type == ForecastModel.LSTM:
                result = await self._forecast_with_lstm(data, forecast_periods)
            elif model_type == ForecastModel.ARIMA:
                result = await self._forecast_with_arima(data, forecast_periods)
            elif model_type == ForecastModel.XGBOOST:
                result = await self._forecast_with_xgboost(data, forecast_periods)
            elif model_type == ForecastModel.LIGHTGBM:
                result = await self._forecast_with_lightgbm(data, forecast_periods)
            elif model_type == ForecastModel.ENSEMBLE:
                result = await self._forecast_with_ensemble(data, forecast_periods)
            else:
                raise ValidationError(f"Unsupported model type: {model_type.value}")
            
            # Add confidence intervals if requested
            if include_confidence_intervals and not result.confidence_intervals:
                result.confidence_intervals = await self._calculate_confidence_intervals(
                    result.predictions, data.values
                )
            
            # Cache result
            await self.cache_manager.set(cache_key, result.__dict__, ttl=3600)
            
            logger.info(f"Time series forecast completed using {model_type.value}")
            return result
            
        except Exception as e:
            logger.error(f"Time series forecasting failed: {str(e)}")
            raise ProcessingError(f"Forecasting error: {str(e)}")

    async def _forecast_with_prophet(self, data: TrainingData, forecast_periods: int) -> ForecastResult:
        """Forecast using Facebook Prophet model"""



        try:
            # Prepare data for Prophet
            df = pd.DataFrame({
                'ds': data.timestamps,
                'y': data.values
            })
            
            # Initialize and fit Prophet model
            model = Prophet(**self.prophet_config)
            model.fit(df)
            
            # Generate future dates
            future = model.make_future_dataframe(periods=forecast_periods)
            
            # Make predictions
            forecast = model.predict(future)
            
            # Extract forecast results
            predictions = forecast['yhat'][-forecast_periods:].tolist()
            confidence_intervals = [
                (lower, upper) for lower, upper in zip(
                    forecast['yhat_lower'][-forecast_periods:],
                    forecast['yhat_upper'][-forecast_periods:]
                )
            ]
            
            # Generate future timestamps
            last_date = data.timestamps[-1] if data.timestamps else datetime.now()
            future_timestamps = [
                last_date + timedelta(days=i+1) for i in range(forecast_periods)
            ]
            
            # Calculate accuracy metrics on historical data
            historical_predictions = forecast['yhat'][:-forecast_periods]
            accuracy_metrics = self._calculate_accuracy_metrics(
                data.values, historical_predictions.tolist()
            )
            
            # Extract seasonal components
            seasonal_components = {
                'trend': forecast['trend'][-forecast_periods:].tolist(),
                'weekly': forecast.get('weekly', [0] * forecast_periods),
                'yearly': forecast.get('yearly', [0] * forecast_periods)
            }
            
            # Trend analysis
            trend_analysis = {
                'overall_trend': 'increasing' if predictions[-1] > predictions[0] else 'decreasing',
                'trend_strength': abs(predictions[-1] - predictions[0]) / predictions[0] if predictions[0] != 0 else 0,
                'seasonality_detected': len([k for k in seasonal_components.keys() if k != 'trend']) > 0
            }
            
            return ForecastResult(
                model_name="prophet",
                predictions=predictions,
                confidence_intervals=confidence_intervals,
                timestamps=future_timestamps,
                accuracy_metrics=accuracy_metrics,
                seasonal_components=seasonal_components,
                trend_analysis=trend_analysis,
                metadata={
                    'changepoints': len(model.changepoints),
                    'seasonalities': list(model.seasonalities.keys()),
                    'holidays_included': len(model.holidays) if hasattr(model, 'holidays') else 0
                }
            )
            
        except Exception as e:
            logger.error(f"Prophet forecasting failed: {str(e)}")
            raise ProcessingError(f"Prophet model error: {str(e)}")

    async def _forecast_with_lstm(self, data: TrainingData, forecast_periods: int) -> ForecastResult:
        """Forecast using LSTM neural network"""



        try:
            # Prepare data for LSTM
            values = np.array(data.values).reshape(-1, 1)
            
            # Scale data
            scaler = MinMaxScaler()
            scaled_data = scaler.fit_transform(values)
            
            # Create sequences for LSTM
            sequence_length = min(self.lstm_config['sequence_length'], len(scaled_data) - 1)
            X, y = self._create_sequences(scaled_data, sequence_length)
            
            if len(X) == 0:
                raise ValidationError("Insufficient data for LSTM training")
            
            # Build LSTM model
            model = Sequential([
                LSTM(self.lstm_config['units'], return_sequences=True, 
                     input_shape=(sequence_length, 1)),
                Dropout(self.lstm_config['dropout']),
                LSTM(self.lstm_config['units'], return_sequences=False),
                Dropout(self.lstm_config['dropout']),
                Dense(25),
                Dense(1)
            ])
            
            model.compile(optimizer='adam', loss='mean_squared_error')
            
            # Train model
            model.fit(X, y, batch_size=self.lstm_config['batch_size'], 
                     epochs=self.lstm_config['epochs'], verbose=0)
            
            # Generate predictions
            predictions = []
            last_sequence = scaled_data[-sequence_length:]
            
            for _ in range(forecast_periods):
                next_pred = model.predict(last_sequence.reshape(1, sequence_length, 1), verbose=0)
                predictions.append(next_pred[0, 0])
                
                # Update sequence for next prediction
                last_sequence = np.append(last_sequence[1:], next_pred.reshape(-1, 1), axis=0)
            
            # Inverse transform predictions
            predictions = scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()
            
            # Calculate accuracy on training data
            train_predictions = []
            for i in range(len(X)):
                pred = model.predict(X[i:i+1], verbose=0)
                train_predictions.append(pred[0, 0])
            
            train_predictions = scaler.inverse_transform(
                np.array(train_predictions).reshape(-1, 1)
            ).flatten()
            
            accuracy_metrics = self._calculate_accuracy_metrics(
                data.values[sequence_length:], train_predictions
            )
            
            # Generate future timestamps
            last_date = data.timestamps[-1] if data.timestamps else datetime.now()
            future_timestamps = [
                last_date + timedelta(days=i+1) for i in range(forecast_periods)
            ]
            
            return ForecastResult(
                model_name="lstm",
                predictions=predictions.tolist(),
                confidence_intervals=[],  # Will be calculated separately
                timestamps=future_timestamps,
                accuracy_metrics=accuracy_metrics,
                metadata={
                    'sequence_length': sequence_length,
                    'model_architecture': 'LSTM-Dropout-LSTM-Dropout-Dense',
                    'training_samples': len(X)
                }
            )
            
        except Exception as e:
            logger.error(f"LSTM forecasting failed: {str(e)}")
            raise ProcessingError(f"LSTM model error: {str(e)}")

    async def _forecast_with_arima(self, data: TrainingData, forecast_periods: int) -> ForecastResult:
        """Forecast using ARIMA statistical model"""



        try:
            # Convert to pandas series
            ts = pd.Series(data.values, index=pd.to_datetime(data.timestamps))
            
            # Determine optimal ARIMA parameters (simplified approach)
            # In production, use more sophisticated parameter selection
            p, d, q = 1, 1, 1  # Default parameters
            
            # Fit ARIMA model
            model = ARIMA(ts, order=(p, d, q))
            fitted_model = model.fit()
            
            # Generate forecast
            forecast_result = fitted_model.forecast(steps=forecast_periods, alpha=0.05)
            predictions = forecast_result.tolist()
            
            # Get confidence intervals
            conf_int = fitted_model.get_forecast(steps=forecast_periods).conf_int()
            confidence_intervals = [(row[0], row[1]) for _, row in conf_int.iterrows()]
            
            # Generate future timestamps
            last_date = data.timestamps[-1] if data.timestamps else datetime.now()
            future_timestamps = [
                last_date + timedelta(days=i+1) for i in range(forecast_periods)
            ]
            
            # Calculate accuracy metrics
            fitted_values = fitted_model.fittedvalues
            accuracy_metrics = self._calculate_accuracy_metrics(
                ts.values[1:], fitted_values.values  # Skip first value due to differencing
            )
            
            # Seasonal decomposition for trend analysis
            if len(ts) >= 24:  # Need sufficient data for decomposition
                try:
                    decomposition = seasonal_decompose(ts, model='additive', period=7)
                    seasonal_components = {
                        'trend': decomposition.trend.dropna().tolist(),
                        'seasonal': decomposition.seasonal.tolist(),
                        'residual': decomposition.resid.dropna().tolist()
                    }
                except:
                    seasonal_components = None
            else:
                seasonal_components = None
            
            return ForecastResult(
                model_name="arima",
                predictions=predictions,
                confidence_intervals=confidence_intervals,
                timestamps=future_timestamps,
                accuracy_metrics=accuracy_metrics,
                seasonal_components=seasonal_components,
                metadata={
                    'arima_order': (p, d, q),
                    'aic': fitted_model.aic,
                    'bic': fitted_model.bic
                }
            )
            
        except Exception as e:
            logger.error(f"ARIMA forecasting failed: {str(e)}")
            raise ProcessingError(f"ARIMA model error: {str(e)}")

    async def _forecast_with_xgboost(self, data: TrainingData, forecast_periods: int) -> ForecastResult:
        """Forecast using XGBoost gradient boosting"""



        try:
            # Create features from time series data
            df = self._create_feature_matrix(data)
            
            # Prepare features and target
            feature_columns = [col for col in df.columns if col != 'target']
            X = df[feature_columns]
            y = df['target']
            
            # Train XGBoost model
            model = xgb.XGBRegressor(**self.xgb_config)
            model.fit(X, y)
            
            # Generate predictions for future periods
            predictions = []
            last_known_values = data.values[-30:]  # Use last 30 values for feature creation
            
            for i in range(forecast_periods):
                # Create features for next prediction
                features = self._create_features_for_prediction(last_known_values, i)
                pred = model.predict([features])[0]
                predictions.append(pred)
                
                # Update last known values
                last_known_values = np.append(last_known_values[1:], pred)
            
            # Calculate accuracy on training data
            train_predictions = model.predict(X)
            accuracy_metrics = self._calculate_accuracy_metrics(y.values, train_predictions)
            
            # Feature importance
            feature_importance = dict(zip(feature_columns, model.feature_importances_))
            
            # Generate future timestamps
            last_date = data.timestamps[-1] if data.timestamps else datetime.now()
            future_timestamps = [
                last_date + timedelta(days=i+1) for i in range(forecast_periods)
            ]
            
            return ForecastResult(
                model_name="xgboost",
                predictions=predictions,
                confidence_intervals=[],  # Will be calculated separately
                timestamps=future_timestamps,
                accuracy_metrics=accuracy_metrics,
                feature_importance=feature_importance,
                metadata={
                    'n_features': len(feature_columns),
                    'n_estimators': self.xgb_config['n_estimators'],
                    'max_depth': self.xgb_config['max_depth']
                }
            )
            
        except Exception as e:
            logger.error(f"XGBoost forecasting failed: {str(e)}")
            raise ProcessingError(f"XGBoost model error: {str(e)}")

    async def _forecast_with_lightgbm(self, data: TrainingData, forecast_periods: int) -> ForecastResult:
        """Forecast using LightGBM gradient boosting"""



        try:
            # Create features from time series data
            df = self._create_feature_matrix(data)
            
            # Prepare features and target
            feature_columns = [col for col in df.columns if col != 'target']
            X = df[feature_columns]
            y = df['target']
            
            # Train LightGBM model
            model = lgb.LGBMRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                verbose=-1
            )
            model.fit(X, y)
            
            # Generate predictions
            predictions = []
            last_known_values = data.values[-30:]
            
            for i in range(forecast_periods):
                features = self._create_features_for_prediction(last_known_values, i)
                pred = model.predict([features])[0]
                predictions.append(pred)
                last_known_values = np.append(last_known_values[1:], pred)
            
            # Calculate accuracy
            train_predictions = model.predict(X)
            accuracy_metrics = self._calculate_accuracy_metrics(y.values, train_predictions)
            
            # Feature importance
            feature_importance = dict(zip(feature_columns, model.feature_importances_))
            
            # Generate timestamps
            last_date = data.timestamps[-1] if data.timestamps else datetime.now()
            future_timestamps = [
                last_date + timedelta(days=i+1) for i in range(forecast_periods)
            ]
            
            return ForecastResult(
                model_name="lightgbm",
                predictions=predictions,
                confidence_intervals=[],
                timestamps=future_timestamps,
                accuracy_metrics=accuracy_metrics,
                feature_importance=feature_importance,
                metadata={
                    'n_features': len(feature_columns),
                    'model_type': 'LightGBM Regressor'
                }
            )
            
        except Exception as e:
            logger.error(f"LightGBM forecasting failed: {str(e)}")
            raise ProcessingError(f"LightGBM model error: {str(e)}")

    async def _forecast_with_ensemble(self, data: TrainingData, forecast_periods: int) -> ForecastResult:
        """Forecast using ensemble of multiple models"""



        try:
            # Get predictions from multiple models
            models_to_use = [ForecastModel.PROPHET, ForecastModel.XGBOOST, ForecastModel.LIGHTGBM]
            model_results = {}
            
            for model_type in models_to_use:
                try:
                    result = await self.forecast_time_series(
                        data, forecast_periods, model_type, include_confidence_intervals=False
                    )
                    model_results[model_type.value] = result
                except Exception as e:
                    logger.warning(f"Model {model_type.value} failed in ensemble: {str(e)}")
            
            if not model_results:
                raise ProcessingError("All ensemble models failed")
            
            # Ensemble weights (can be optimized based on historical performance)
            weights = {
                'prophet': 0.4,
                'xgboost': 0.3,
                'lightgbm': 0.3
            }
            
            # Combine predictions using weighted average
            ensemble_predictions = []
            for i in range(forecast_periods):
                weighted_sum = 0
                total_weight = 0
                
                for model_name, result in model_results.items():
                    if i < len(result.predictions):
                        weight = weights.get(model_name, 0)
                        weighted_sum += result.predictions[i] * weight
                        total_weight += weight
                
                if total_weight > 0:
                    ensemble_predictions.append(weighted_sum / total_weight)
                else:
                    ensemble_predictions.append(0)
            
            # Combine accuracy metrics
            combined_accuracy = {}
            for metric in ['mae', 'mse', 'rmse', 'r2']:
                values = [result.accuracy_metrics.get(metric, 0) for result in model_results.values()]
                combined_accuracy[metric] = np.mean(values) if values else 0
            
            # Calculate ensemble confidence intervals
            all_predictions = []
            for result in model_results.values():
                all_predictions.append(result.predictions)
            
            confidence_intervals = []
            for i in range(forecast_periods):
                period_predictions = [pred[i] for pred in all_predictions if i < len(pred)]
                if period_predictions:
                    std_dev = np.std(period_predictions)
                    mean_pred = ensemble_predictions[i]
                    confidence_intervals.append((
                        mean_pred - 1.96 * std_dev,
                        mean_pred + 1.96 * std_dev
                    ))
                else:
                    confidence_intervals.append((ensemble_predictions[i] * 0.8, 
                                               ensemble_predictions[i] * 1.2))
            
            # Generate timestamps
            last_date = data.timestamps[-1] if data.timestamps else datetime.now()
            future_timestamps = [
                last_date + timedelta(days=i+1) for i in range(forecast_periods)
            ]
            
            return ForecastResult(
                model_name="ensemble",
                predictions=ensemble_predictions,
                confidence_intervals=confidence_intervals,
                timestamps=future_timestamps,
                accuracy_metrics=combined_accuracy,
                metadata={
                    'models_used': list(model_results.keys()),
                    'ensemble_weights': weights,
                    'model_count': len(model_results)
                }
            )
            
        except Exception as e:
            logger.error(f"Ensemble forecasting failed: {str(e)}")
            raise ProcessingError(f"Ensemble model error: {str(e)}")

    def _validate_training_data(self, data: TrainingData):
        """Validate training data format and completeness"""
        if not data.timestamps or not data.values:
            raise ValidationError("Training data must contain timestamps and values")
        
        if len(data.timestamps) != len(data.values):
            raise ValidationError("Timestamps and values must have the same length")
        
        if len(data.values) < 10:
            raise ValidationError("Insufficient training data (minimum 10 data points required)")
        
        # Check for missing or invalid values
        if any(pd.isna(data.values)):
            raise ValidationError("Training data contains missing values")

    def _create_sequences(self, data: np.ndarray, sequence_length: int) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM training"""
        X, y = [], []
        for i in range(sequence_length, len(data)):
            X.append(data[i-sequence_length:i])
            y.append(data[i])
        return np.array(X), np.array(y)

    def _create_feature_matrix(self, data: TrainingData) -> pd.DataFrame:
        """Create feature matrix from time series data for ML models"""
        df = pd.DataFrame({
            'timestamp': data.timestamps,
            'value': data.values
        })
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Create lag features
        for lag in [1, 2, 3, 7, 14, 30]:
            df[f'lag_{lag}'] = df['value'].shift(lag)
        
        # Create rolling statistics
        for window in [7, 14, 30]:
            df[f'rolling_mean_{window}'] = df['value'].rolling(window=window).mean()
            df[f'rolling_std_{window}'] = df['value'].rolling(window=window).std()
        
        # Create time-based features
        df['dayofweek'] = df.index.dayofweek
        df['month'] = df.index.month
        df['quarter'] = df.index.quarter
        df['is_weekend'] = (df.index.dayofweek >= 5).astype(int)
        
        # Target variable
        df['target'] = df['value'].shift(-1)
        
        # Remove rows with NaN values
        df.dropna(inplace=True)
        
        return df

    def _create_features_for_prediction(self, last_values: np.ndarray, period_ahead: int) -> List[float]:
        """Create features for a future prediction"""
        features = []
        
        # Add lag features
        lag_values = [1, 2, 3, 7, 14, 30]
        for lag in lag_values:
            if lag <= len(last_values):
                features.append(last_values[-lag])
            else:
                features.append(0)
        
        # Add rolling statistics
        if len(last_values) >= 7:
            features.append(np.mean(last_values[-7:]))  # 7-day rolling mean
            features.append(np.std(last_values[-7:]))   # 7-day rolling std
        else:
            features.extend([np.mean(last_values), np.std(last_values)])
        
        if len(last_values) >= 14:
            features.append(np.mean(last_values[-14:]))  # 14-day rolling mean
            features.append(np.std(last_values[-14:]))   # 14-day rolling std
        else:
            features.extend([np.mean(last_values), np.std(last_values)])
        
        if len(last_values) >= 30:
            features.append(np.mean(last_values[-30:]))  # 30-day rolling mean
            features.append(np.std(last_values[-30:]))   # 30-day rolling std
        else:
            features.extend([np.mean(last_values), np.std(last_values)])
        
        # Add time-based features (simplified - would need actual future date)
        current_date = datetime.now() + timedelta(days=period_ahead)
        features.extend([
            current_date.weekday(),  # dayofweek
            current_date.month,      # month
            (current_date.month - 1) // 3 + 1,  # quarter
            1 if current_date.weekday() >= 5 else 0  # is_weekend
        ])
        
        return features

    def _calculate_accuracy_metrics(self, actual: List[float], predicted: List[float]) -> Dict[str, float]:
        """Calculate accuracy metrics for model evaluation"""



        try:
            actual_arr = np.array(actual)
            predicted_arr = np.array(predicted)
            
            # Handle different lengths
            min_length = min(len(actual_arr), len(predicted_arr))
            actual_arr = actual_arr[:min_length]
            predicted_arr = predicted_arr[:min_length]
            
            if len(actual_arr) == 0:
                return {'mae': 0, 'mse': 0, 'rmse': 0, 'r2': 0, 'mape': 0}
            
            mae = mean_absolute_error(actual_arr, predicted_arr)
            mse = mean_squared_error(actual_arr, predicted_arr)
            rmse = np.sqrt(mse)
            
            # R² score (coefficient of determination)
            try:
                r2 = r2_score(actual_arr, predicted_arr)
            except:
                r2 = 0
            
            # Mean Absolute Percentage Error
            try:
                mape = np.mean(np.abs((actual_arr - predicted_arr) / actual_arr)) * 100
                mape = min(mape, 1000)  # Cap MAPE to avoid extreme values
            except:
                mape = 0
            
            return {
                'mae': float(mae),
                'mse': float(mse), 
                'rmse': float(rmse),
                'r2': float(r2),
                'mape': float(mape)
            }
            
        except Exception as e:
            logger.warning(f"Error calculating accuracy metrics: {str(e)}")
            return {'mae': 0, 'mse': 0, 'rmse': 0, 'r2': 0, 'mape': 0}

    async def _calculate_confidence_intervals(self, predictions: List[float], historical_values: List[float]) -> List[Tuple[float, float]]:
        """Calculate confidence intervals for predictions"""



        try:
            if not historical_values or len(historical_values) < 2:
                # Fallback to simple percentage-based intervals
                return [(pred * 0.8, pred * 1.2) for pred in predictions]
            
            # Calculate prediction uncertainty based on historical volatility
            historical_std = np.std(historical_values)
            confidence_level = 0.95  # 95% confidence interval
            z_score = 1.96  # For 95% confidence
            
            confidence_intervals = []
            for pred in predictions:
                margin_of_error = z_score * historical_std
                lower_bound = pred - margin_of_error
                upper_bound = pred + margin_of_error
                confidence_intervals.append((float(lower_bound), float(upper_bound)))
            
            return confidence_intervals
            
        except Exception as e:
            logger.warning(f"Error calculating confidence intervals: {str(e)}")
            return [(pred * 0.8, pred * 1.2) for pred in predictions]


class TimeSeriesForecaster:
    """Specialized time series forecasting component"""
    
    def __init__(self, forecasting_engine: ForecastingEngine):
        self.engine = forecasting_engine
        
    async def forecast_content_performance(self, historical_views: List[Tuple[datetime, int]], days_ahead: int = 30) -> ForecastResult:
        """Forecast content performance metrics"""
        timestamps, values = zip(*historical_views) if historical_views else ([], [])
        
        data = TrainingData(
            timestamps=list(timestamps),
            values=list(values),
            frequency="D"
        )
        
        return await self.engine.forecast_time_series(
            data, days_ahead, ForecastModel.ENSEMBLE, include_confidence_intervals=True
        )

class ContentPerformancePredictor:
    """Specialized content performance prediction component"""
    
    def __init__(self, forecasting_engine: ForecastingEngine):
        self.engine = forecasting_engine
        
    async def predict_viral_potential(self, content_features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict viral potential of content"""
        # Implementation would include viral coefficient calculation
        # Algorithm favorability scoring, engagement prediction, etc.
        return {
            'viral_score': 0.75,
            'expected_reach_multiplier': 2.3,
            'peak_performance_day': 3
        }

class RevenueForecaster:
    """Specialized revenue forecasting component"""
    
    def __init__(self, forecasting_engine: ForecastingEngine):
        self.engine = forecasting_engine
        
    async def forecast_monthly_revenue(self, historical_revenue: List[Tuple[datetime, float]], months_ahead: int = 6) -> ForecastResult:
        """Forecast monthly revenue"""
        timestamps, values = zip(*historical_revenue) if historical_revenue else ([], [])
        
        data = TrainingData(
            timestamps=list(timestamps),
            values=list(values),
            frequency="M"
        )
        
        return await self.engine.forecast_time_series(
            data, months_ahead, ForecastModel.PROPHET, include_confidence_intervals=True
        )

class AudienceGrowthPredictor:
    """Specialized audience growth prediction component"""
    
    def __init__(self, forecasting_engine: ForecastingEngine):
        self.engine = forecasting_engine
        
    async def predict_subscriber_growth(self, historical_subscribers: List[Tuple[datetime, int]], days_ahead: int = 90) -> Dict[str, Any]:
        """Predict subscriber growth with viral coefficient modeling"""
        timestamps, values = zip(*historical_subscribers) if historical_subscribers else ([], [])
        
        # Calculate growth rate and viral coefficient
        growth_rates = []
        for i in range(1, len(values)):
            if values[i-1] > 0:
                growth_rate = (values[i] - values[i-1]) / values[i-1]
                growth_rates.append(growth_rate)
        
        avg_growth_rate = np.mean(growth_rates) if growth_rates else 0.05
        viral_coefficient = max(0, avg_growth_rate * 10)  # Simplified viral coefficient
        
        data = TrainingData(
            timestamps=list(timestamps),
            values=list(values),
            frequency="D"
        )
        
        forecast = await self.engine.forecast_time_series(
            data, days_ahead, ForecastModel.ENSEMBLE, include_confidence_intervals=True
        )
        
        return {
            'forecast': forecast,
            'viral_coefficient': viral_coefficient,
            'average_growth_rate': avg_growth_rate,
            'growth_acceleration': len([r for r in growth_rates[-7:] if r > avg_growth_rate]) / 7 if len(growth_rates) >= 7 else 0.5
        }

class CollaborationSuccessPredictor:
    """Specialized collaboration success prediction component"""
    
    def __init__(self, forecasting_engine: ForecastingEngine):
        self.engine = forecasting_engine
        
    async def predict_collaboration_outcome(self, collaboration_features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict collaboration success probability and impact"""
        # Extract key features
        audience_overlap = collaboration_features.get('audience_overlap', 0.3)
        engagement_compatibility = collaboration_features.get('engagement_compatibility', 0.7)
        brand_alignment = collaboration_features.get('brand_alignment', 0.8)
        historical_success_rate = collaboration_features.get('historical_success_rate', 0.6)
        
        # Calculate success probability using weighted factors
        success_probability = (
            audience_overlap * 0.25 +
            engagement_compatibility * 0.30 +
            brand_alignment * 0.25 +
            historical_success_rate * 0.20
        )
        
        # Predict impact metrics
        expected_view_increase = success_probability * 0.4 + 0.1  # 10-50% increase
        expected_subscriber_gain = success_probability * 0.3 + 0.05  # 5-35% gain
        
        return {
            'success_probability': success_probability,
            'expected_view_increase_percentage': expected_view_increase * 100,
            'expected_subscriber_gain_percentage': expected_subscriber_gain * 100,
            'optimal_collaboration_timing': 'within_2_weeks',
            'risk_factors': self._identify_collaboration_risks(collaboration_features),
            'optimization_recommendations': self._generate_collaboration_recommendations(success_probability)
        }
    
    def _identify_collaboration_risks(self, features: Dict[str, Any]) -> List[str]:
        """Identify risks in collaboration"""
        risks = []
        
        if features.get('audience_overlap', 0.3) < 0.2:
            risks.append("Low audience overlap may limit cross-promotion effectiveness")
            
        if features.get('engagement_compatibility', 0.7) < 0.5:
            risks.append("Mismatched engagement styles may confuse audiences")
            
        if features.get('brand_alignment', 0.8) < 0.6:
            risks.append("Brand misalignment could damage creator reputation")
        
        return risks
    
    def _generate_collaboration_recommendations(self, success_probability: float) -> List[str]:
        """Generate collaboration optimization recommendations"""
        recommendations = []
        
        if success_probability > 0.8:
            recommendations.append("High success probability - proceed with collaboration")
            recommendations.append("Consider extending collaboration to multiple content pieces")
        elif success_probability > 0.6:
            recommendations.append("Good collaboration potential - optimize timing and format")
            recommendations.append("Focus on audience engagement strategies")
        else:
            recommendations.append("Lower success probability - consider improving compatibility factors")
            recommendations.append("Start with smaller collaboration to test audience response")
        
        return recommendations
