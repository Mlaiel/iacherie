"""📈 Payment Forecasting - AI-Powered Predictive Analytics Engine
=================================================================

Advanced payment volume and revenue forecasting for Creator Economy Platform.
ML-driven predictions, trend analysis, and financial planning intelligence.

Performance Targets: < 500ms forecasting operations
Enterprise forecasting engine with deep learning models and scenario analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import time
from decimal import Decimal
from collections import defaultdict, deque
import statistics
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, cross_val_score
import structlog

logger = structlog.get_logger(__name__)

class ForecastType(Enum):
    """Types of payment forecasts"""
    VOLUME = "volume"
    REVENUE = "revenue"
    FRAUD_RATE = "fraud_rate"
    CHARGEBACK_RATE = "chargeback_rate"
    CONVERSION_RATE = "conversion_rate"
    AVERAGE_TRANSACTION = "average_transaction"
    GROWTH_RATE = "growth_rate"
    SEASONAL_TRENDS = "seasonal_trends"

class ForecastHorizon(Enum):
    """Forecast time horizons"""
    SHORT_TERM = "short_term"  # 1-7 days
    MEDIUM_TERM = "medium_term"  # 1-4 weeks
    LONG_TERM = "long_term"  # 1-12 months
    STRATEGIC = "strategic"  # 1-3 years

class ModelType(Enum):
    """ML model types for forecasting"""
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    NEURAL_NETWORK = "neural_network"
    ENSEMBLE = "ensemble"
    ARIMA = "arima"
    PROPHET = "prophet"

class SeasonalityType(Enum):
    """Types of seasonality patterns"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    NONE = "none"

@dataclass
class ForecastRequest:
    """Forecast request configuration"""
    forecast_type: ForecastType
    horizon: ForecastHorizon
    periods: int
    confidence_intervals: List[float] = field(default_factory=lambda: [0.8, 0.95])
    include_seasonality: bool = True
    model_type: Optional[ModelType] = None
    custom_features: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ForecastResult:
    """Forecast result with predictions and metadata"""
    forecast_type: ForecastType
    horizon: ForecastHorizon
    predictions: List[float]
    timestamps: List[datetime]
    confidence_intervals: Dict[str, List[Tuple[float, float]]]
    model_accuracy: Dict[str, float]
    seasonality_detected: Dict[SeasonalityType, float]
    trend_analysis: Dict[str, Any]
    feature_importance: Dict[str, float]
    forecast_metadata: Dict[str, Any]

@dataclass
class ScenarioAnalysis:
    """Scenario-based forecast analysis"""
    scenario_name: str
    description: str
    assumptions: Dict[str, Any]
    forecast_adjustments: Dict[str, float]
    predicted_outcomes: Dict[str, Any]
    confidence: float
    risk_factors: List[str]

class ForecastingEngine:
    """Core forecasting engine with ML models"""
    
    def __init__(self):
        self.models = self._initialize_models()
        self.scalers = {}
        self.forecast_cache = {}
        self.model_performance = defaultdict(dict)
        
    def _initialize_models(self) -> Dict[ModelType, Any]:
        """Initialize ML models for forecasting"""
        return {
            ModelType.LINEAR_REGRESSION: LinearRegression(),
            ModelType.RANDOM_FOREST: RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            ),
            ModelType.GRADIENT_BOOSTING: GradientBoostingRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            ),
            ModelType.ENSEMBLE: None  # Will be created dynamically
        }
    
    async def forecast_payment_volumes(
        self,
        historical_data: List[Dict[str, Any]],
        request: ForecastRequest
    ) -> ForecastResult:
        """Forecast payment volumes using ML models"""
        try:
            start_time = time.perf_counter()
            
            if len(historical_data) < 30:  # Minimum data requirement
                raise ValueError("Insufficient historical data for forecasting")
            
            # Prepare data for forecasting
            df = await self._prepare_volume_data(historical_data)
            
            # Feature engineering
            features_df = await self._engineer_features(df, request.forecast_type)
            
            # Detect seasonality
            seasonality = await self._detect_seasonality(df)
            
            # Select and train model
            model, scaler = await self._train_forecasting_model(
                features_df, request.model_type or ModelType.ENSEMBLE
            )
            
            # Generate predictions
            predictions, timestamps = await self._generate_predictions(
                model, scaler, features_df, request.periods, request.horizon
            )
            
            # Calculate confidence intervals
            confidence_intervals = await self._calculate_confidence_intervals(
                model, scaler, features_df, predictions, request.confidence_intervals
            )
            
            # Analyze trends
            trend_analysis = await self._analyze_trends(df, predictions)
            
            # Calculate feature importance
            feature_importance = await self._calculate_feature_importance(
                model, features_df.columns.tolist()
            )
            
            # Model accuracy metrics
            accuracy_metrics = await self._calculate_model_accuracy(
                model, features_df
            )
            
            result = ForecastResult(
                forecast_type=request.forecast_type,
                horizon=request.horizon,
                predictions=predictions,
                timestamps=timestamps,
                confidence_intervals=confidence_intervals,
                model_accuracy=accuracy_metrics,
                seasonality_detected=seasonality,
                trend_analysis=trend_analysis,
                feature_importance=feature_importance,
                forecast_metadata={
                    "data_points": len(historical_data),
                    "model_type": request.model_type.value if request.model_type else "ensemble",
                    "forecast_periods": request.periods,
                    "generated_at": datetime.utcnow().isoformat()
                }
            )
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Payment volumes forecasted",
                forecast_type=request.forecast_type.value,
                horizon=request.horizon.value,
                periods=request.periods,
                accuracy=accuracy_metrics.get('r2_score', 0),
                duration_ms=duration_ms
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error forecasting payment volumes: {e}")
            raise
    
    async def _prepare_volume_data(
        self,
        historical_data: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """Prepare historical data for volume forecasting"""
        # Convert to DataFrame
        df = pd.DataFrame(historical_data)
        
        # Ensure required columns
        required_columns = ['timestamp', 'volume', 'amount']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Convert timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        # Fill missing values
        df['volume'] = df['volume'].fillna(0)
        df['amount'] = df['amount'].fillna(0)
        
        # Add time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['day_of_month'] = df['timestamp'].dt.day
        df['month'] = df['timestamp'].dt.month
        df['quarter'] = df['timestamp'].dt.quarter
        df['year'] = df['timestamp'].dt.year
        
        return df
    
    async def _engineer_features(
        self,
        df: pd.DataFrame,
        forecast_type: ForecastType
    ) -> pd.DataFrame:
        """Engineer features for forecasting models"""
        features_df = df.copy()
        
        # Lag features
        for lag in [1, 2, 3, 7, 14, 30]:
            if len(df) > lag:
                features_df[f'volume_lag_{lag}'] = df['volume'].shift(lag)
                features_df[f'amount_lag_{lag}'] = df['amount'].shift(lag)
        
        # Rolling statistics
        for window in [3, 7, 14, 30]:
            if len(df) > window:
                features_df[f'volume_ma_{window}'] = df['volume'].rolling(window).mean()
                features_df[f'amount_ma_{window}'] = df['amount'].rolling(window).mean()
                features_df[f'volume_std_{window}'] = df['volume'].rolling(window).std()
        
        # Growth rates
        features_df['volume_growth_1d'] = df['volume'].pct_change(1)
        features_df['volume_growth_7d'] = df['volume'].pct_change(7)
        features_df['amount_growth_1d'] = df['amount'].pct_change(1)
        
        # Cyclical features
        features_df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        features_df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        features_df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        features_df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        features_df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        features_df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        # Drop rows with NaN values (from lag features)
        features_df = features_df.dropna()
        
        return features_df
    
    async def _detect_seasonality(
        self,
        df: pd.DataFrame
    ) -> Dict[SeasonalityType, float]:
        """Detect seasonality patterns in the data"""
        seasonality = {}
        
        if len(df) < 24:  # Need minimum data
            return {s: 0.0 for s in SeasonalityType}
        
        # Daily seasonality (hourly patterns)
        if 'hour' in df.columns:
            hourly_means = df.groupby('hour')['volume'].mean()
            hourly_var = hourly_means.var()
            overall_var = df['volume'].var()
            seasonality[SeasonalityType.DAILY] = min(1.0, hourly_var / overall_var if overall_var > 0 else 0)
        
        # Weekly seasonality
        if len(df) >= 7:
            weekly_means = df.groupby('day_of_week')['volume'].mean()
            weekly_var = weekly_means.var()
            seasonality[SeasonalityType.WEEKLY] = min(1.0, weekly_var / overall_var if overall_var > 0 else 0)
        
        # Monthly seasonality
        if len(df) >= 30:
            monthly_means = df.groupby('day_of_month')['volume'].mean()
            monthly_var = monthly_means.var()
            seasonality[SeasonalityType.MONTHLY] = min(1.0, monthly_var / overall_var if overall_var > 0 else 0)
        
        # Fill missing seasonality types
        for s_type in SeasonalityType:
            if s_type not in seasonality:
                seasonality[s_type] = 0.0
        
        return seasonality
    
    async def _train_forecasting_model(
        self,
        features_df: pd.DataFrame,
        model_type: ModelType
    ) -> Tuple[Any, Any]:
        """Train forecasting model"""
        # Prepare features and target
        feature_columns = [col for col in features_df.columns 
                          if col not in ['timestamp', 'volume'] and not col.startswith('volume_')]
        
        X = features_df[feature_columns].fillna(0)
        y = features_df['volume']
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Select model
        if model_type == ModelType.ENSEMBLE:
            # Create ensemble model
            models = [
                self.models[ModelType.RANDOM_FOREST],
                self.models[ModelType.GRADIENT_BOOSTING],
                Ridge(alpha=1.0)
            ]
            
            # Train individual models
            trained_models = []
            for model in models:
                model_copy = type(model)(**model.get_params())
                model_copy.fit(X_scaled, y)
                trained_models.append(model_copy)
            
            # Create ensemble wrapper
            ensemble_model = EnsembleModel(trained_models)
            
        else:
            ensemble_model = self.models[model_type]
            ensemble_model.fit(X_scaled, y)
        
        return ensemble_model, scaler
    
    async def _generate_predictions(
        self,
        model: Any,
        scaler: StandardScaler,
        features_df: pd.DataFrame,
        periods: int,
        horizon: ForecastHorizon
    ) -> Tuple[List[float], List[datetime]]:
        """Generate future predictions"""
        predictions = []
        timestamps = []
        
        # Get the last known data point
        last_timestamp = features_df['timestamp'].iloc[-1]
        
        # Determine time interval based on horizon
        if horizon == ForecastHorizon.SHORT_TERM:
            interval = timedelta(hours=1)
        elif horizon == ForecastHorizon.MEDIUM_TERM:
            interval = timedelta(hours=6)
        elif horizon == ForecastHorizon.LONG_TERM:
            interval = timedelta(days=1)
        else:  # STRATEGIC
            interval = timedelta(days=7)
        
        # Feature columns for prediction
        feature_columns = [col for col in features_df.columns 
                          if col not in ['timestamp', 'volume'] and not col.startswith('volume_')]
        
        # Use the most recent feature values as a base
        last_features = features_df[feature_columns].iloc[-1:].copy()
        
        # Generate predictions for each future period
        for i in range(periods):
            # Calculate future timestamp
            future_timestamp = last_timestamp + (interval * (i + 1))
            timestamps.append(future_timestamp)
            
            # Update time-based features
            updated_features = last_features.copy()
            updated_features['hour'] = future_timestamp.hour
            updated_features['day_of_week'] = future_timestamp.weekday()
            updated_features['day_of_month'] = future_timestamp.day
            updated_features['month'] = future_timestamp.month
            updated_features['quarter'] = (future_timestamp.month - 1) // 3 + 1
            updated_features['year'] = future_timestamp.year
            
            # Update cyclical features
            updated_features['hour_sin'] = np.sin(2 * np.pi * future_timestamp.hour / 24)
            updated_features['hour_cos'] = np.cos(2 * np.pi * future_timestamp.hour / 24)
            updated_features['day_sin'] = np.sin(2 * np.pi * future_timestamp.weekday() / 7)
            updated_features['day_cos'] = np.cos(2 * np.pi * future_timestamp.weekday() / 7)
            updated_features['month_sin'] = np.sin(2 * np.pi * future_timestamp.month / 12)
            updated_features['month_cos'] = np.cos(2 * np.pi * future_timestamp.month / 12)
            
            # Scale features
            X_scaled = scaler.transform(updated_features.fillna(0))
            
            # Make prediction
            prediction = model.predict(X_scaled)[0]
            predictions.append(max(0, prediction))  # Ensure non-negative predictions
        
        return predictions, timestamps
    
    async def _calculate_confidence_intervals(
        self,
        model: Any,
        scaler: StandardScaler,
        features_df: pd.DataFrame,
        predictions: List[float],
        confidence_levels: List[float]
    ) -> Dict[str, List[Tuple[float, float]]]:
        """Calculate confidence intervals for predictions"""
        confidence_intervals = {}
        
        # Calculate prediction errors from historical data
        feature_columns = [col for col in features_df.columns 
                          if col not in ['timestamp', 'volume'] and not col.startswith('volume_')]
        
        X = features_df[feature_columns].fillna(0)
        y = features_df['volume']
        X_scaled = scaler.transform(X)
        
        # Get historical predictions
        historical_predictions = model.predict(X_scaled)
        errors = y - historical_predictions
        
        # Calculate error statistics
        error_std = np.std(errors)
        
        # Calculate confidence intervals for each level
        for confidence_level in confidence_levels:
            # Calculate z-score for confidence level
            z_score = np.percentile(np.abs(errors), confidence_level * 100)
            
            intervals = []
            for pred in predictions:
                lower_bound = max(0, pred - z_score)
                upper_bound = pred + z_score
                intervals.append((lower_bound, upper_bound))
            
            confidence_intervals[f"{confidence_level:.0%}"] = intervals
        
        return confidence_intervals
    
    async def _analyze_trends(
        self,
        historical_df: pd.DataFrame,
        predictions: List[float]
    ) -> Dict[str, Any]:
        """Analyze trends in historical data and predictions"""
        # Historical trend
        historical_volumes = historical_df['volume'].values
        x_hist = np.arange(len(historical_volumes))
        
        if len(historical_volumes) > 1:
            hist_slope, hist_intercept = np.polyfit(x_hist, historical_volumes, 1)
        else:
            hist_slope, hist_intercept = 0, 0
        
        # Predicted trend
        if len(predictions) > 1:
            x_pred = np.arange(len(predictions))
            pred_slope, pred_intercept = np.polyfit(x_pred, predictions, 1)
        else:
            pred_slope, pred_intercept = 0, 0
        
        # Trend analysis
        historical_trend = "increasing" if hist_slope > 0 else "decreasing" if hist_slope < 0 else "stable"
        predicted_trend = "increasing" if pred_slope > 0 else "decreasing" if pred_slope < 0 else "stable"
        
        # Calculate growth rates
        if len(historical_volumes) > 0 and len(predictions) > 0:
            last_historical = historical_volumes[-1]
            first_prediction = predictions[0]
            short_term_growth = ((first_prediction - last_historical) / last_historical * 100) if last_historical > 0 else 0
        else:
            short_term_growth = 0
        
        return {
            "historical_trend": historical_trend,
            "historical_slope": float(hist_slope),
            "predicted_trend": predicted_trend,
            "predicted_slope": float(pred_slope),
            "short_term_growth_rate": float(short_term_growth),
            "trend_acceleration": float(pred_slope - hist_slope)
        }
    
    async def _calculate_feature_importance(
        self,
        model: Any,
        feature_names: List[str]
    ) -> Dict[str, float]:
        """Calculate feature importance"""
        importance_dict = {}
        
        try:
            if hasattr(model, 'feature_importances_'):
                # Tree-based models
                importances = model.feature_importances_
                for name, importance in zip(feature_names, importances):
                    importance_dict[name] = float(importance)
            elif hasattr(model, 'coef_'):
                # Linear models
                coefficients = np.abs(model.coef_)
                for name, coef in zip(feature_names, coefficients):
                    importance_dict[name] = float(coef)
            elif hasattr(model, 'models'):  # Ensemble model
                # Average importance across ensemble models
                all_importances = []
                for sub_model in model.models:
                    if hasattr(sub_model, 'feature_importances_'):
                        all_importances.append(sub_model.feature_importances_)
                
                if all_importances:
                    avg_importances = np.mean(all_importances, axis=0)
                    for name, importance in zip(feature_names, avg_importances):
                        importance_dict[name] = float(importance)
        except Exception as e:
            logger.warning(f"Could not calculate feature importance: {e}")
            # Return uniform importance
            uniform_importance = 1.0 / len(feature_names) if feature_names else 0
            importance_dict = {name: uniform_importance for name in feature_names}
        
        return importance_dict
    
    async def _calculate_model_accuracy(
        self,
        model: Any,
        features_df: pd.DataFrame
    ) -> Dict[str, float]:
        """Calculate model accuracy metrics"""
        feature_columns = [col for col in features_df.columns 
                          if col not in ['timestamp', 'volume'] and not col.startswith('volume_')]
        
        X = features_df[feature_columns].fillna(0)
        y = features_df['volume']
        
        # Use StandardScaler for consistency
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Split data for validation
        if len(X) > 10:
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # Train model on training data
            model_copy = type(model)(**model.get_params()) if hasattr(model, 'get_params') else model
            model_copy.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model_copy.predict(X_test)
            
            # Calculate metrics
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_test, y_pred)
            
            # Calculate MAPE (Mean Absolute Percentage Error)
            mape = np.mean(np.abs((y_test - y_pred) / np.maximum(y_test, 1))) * 100
            
        else:
            # Fallback for small datasets
            mae = mse = rmse = mape = 0
            r2 = 0
        
        return {
            "mae": float(mae),
            "mse": float(mse),
            "rmse": float(rmse),
            "r2_score": float(r2),
            "mape": float(mape)
        }

class EnsembleModel:
    """Ensemble model wrapper for combining multiple models"""
    
    def __init__(self, models: List[Any]):
        self.models = models
    
    def fit(self, X, y):
        """Fit all models in the ensemble"""
        for model in self.models:
            model.fit(X, y)
    
    def predict(self, X):
        """Make predictions using ensemble averaging"""
        predictions = []
        for model in self.models:
            pred = model.predict(X)
            predictions.append(pred)
        
        # Average predictions
        return np.mean(predictions, axis=0)
    
    def get_params(self):
        """Get parameters (placeholder for compatibility)"""
        return {}

class MLPredictor:
    """Advanced ML predictor with multiple algorithms"""
    
    def __init__(self):
        self.trained_models = {}
        self.feature_scalers = {}
        
    async def predict_revenue_trends(
        self,
        historical_revenue: List[Dict[str, Any]],
        prediction_periods: int = 30
    ) -> Dict[str, Any]:
        """Predict revenue trends using advanced ML"""
        try:
            start_time = time.perf_counter()
            
            if len(historical_revenue) < 10:
                raise ValueError("Insufficient revenue data for prediction")
            
            # Prepare revenue data
            df = pd.DataFrame(historical_revenue)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # Feature engineering for revenue
            df['revenue_ma_7'] = df['revenue'].rolling(7).mean()
            df['revenue_ma_30'] = df['revenue'].rolling(30).mean()
            df['revenue_growth'] = df['revenue'].pct_change()
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['month'] = df['timestamp'].dt.month
            
            # Prepare features
            feature_cols = ['revenue_ma_7', 'revenue_ma_30', 'revenue_growth', 'day_of_week', 'month']
            X = df[feature_cols].fillna(0)
            y = df['revenue']
            
            # Train multiple models
            models = {
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'linear_regression': LinearRegression()
            }
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            predictions = {}
            model_scores = {}
            
            # Train and evaluate each model
            for name, model in models.items():
                # Cross-validation
                cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='r2')
                model_scores[name] = np.mean(cv_scores)
                
                # Train on full data
                model.fit(X_scaled, y)
                
                # Generate predictions
                last_features = X.iloc[-1:].copy()
                future_predictions = []
                
                for i in range(prediction_periods):
                    # Use last known features for prediction
                    pred_features = scaler.transform(last_features.fillna(0))
                    pred = model.predict(pred_features)[0]
                    future_predictions.append(max(0, pred))
                
                predictions[name] = future_predictions
            
            # Select best model based on cross-validation score
            best_model = max(model_scores.keys(), key=lambda k: model_scores[k])
            
            # Generate ensemble prediction
            ensemble_pred = np.mean([predictions[name] for name in predictions.keys()], axis=0).tolist()
            
            # Calculate trend metrics
            recent_revenue = df['revenue'].tail(30).mean()
            predicted_revenue = np.mean(ensemble_pred)
            revenue_trend = ((predicted_revenue - recent_revenue) / recent_revenue * 100) if recent_revenue > 0 else 0
            
            result = {
                "prediction_periods": prediction_periods,
                "model_scores": model_scores,
                "best_model": best_model,
                "predictions": {
                    "ensemble": ensemble_pred,
                    "individual_models": predictions
                },
                "trend_analysis": {
                    "current_average_revenue": float(recent_revenue),
                    "predicted_average_revenue": float(predicted_revenue),
                    "revenue_trend_percentage": float(revenue_trend),
                    "trend_direction": "increasing" if revenue_trend > 0 else "decreasing" if revenue_trend < 0 else "stable"
                },
                "confidence_metrics": {
                    "ensemble_confidence": float(np.mean(list(model_scores.values()))),
                    "prediction_variance": float(np.var([predictions[name] for name in predictions.keys()]))
                }
            }
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Revenue trends predicted",
                prediction_periods=prediction_periods,
                best_model=best_model,
                confidence=result["confidence_metrics"]["ensemble_confidence"],
                duration_ms=duration_ms
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error predicting revenue trends: {e}")
            raise
    
    async def predict_fraud_rates(
        self,
        historical_fraud_data: List[Dict[str, Any]],
        external_factors: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Predict fraud rates with external factor consideration"""
        try:
            start_time = time.perf_counter()
            
            external_factors = external_factors or {}
            
            if len(historical_fraud_data) < 20:
                raise ValueError("Insufficient fraud data for prediction")
            
            # Prepare fraud data
            df = pd.DataFrame(historical_fraud_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # Calculate fraud rate
            df['fraud_rate'] = (df['fraud_count'] / df['total_transactions'] * 100).fillna(0)
            
            # Feature engineering
            df['fraud_rate_ma_7'] = df['fraud_rate'].rolling(7).mean()
            df['fraud_rate_ma_30'] = df['fraud_rate'].rolling(30).mean()
            df['fraud_trend'] = df['fraud_rate'].pct_change()
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
            
            # Add external factors if provided
            for factor, value in external_factors.items():
                df[f'external_{factor}'] = value
            
            # Prepare features
            feature_cols = [col for col in df.columns 
                          if col not in ['timestamp', 'fraud_count', 'total_transactions', 'fraud_rate']]
            
            X = df[feature_cols].fillna(0)
            y = df['fraud_rate']
            
            # Train fraud prediction model
            model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            scaler = StandardScaler()
            
            X_scaled = scaler.fit_transform(X)
            model.fit(X_scaled, y)
            
            # Generate future predictions (7 days)
            future_predictions = []
            last_features = X.iloc[-1:].copy()
            
            for i in range(7):  # 7-day forecast
                pred_features = scaler.transform(last_features.fillna(0))
                pred = model.predict(pred_features)[0]
                future_predictions.append(max(0, min(100, pred)))  # Bound between 0-100%
            
            # Calculate risk assessment
            current_fraud_rate = df['fraud_rate'].tail(7).mean()
            predicted_fraud_rate = np.mean(future_predictions)
            risk_increase = predicted_fraud_rate - current_fraud_rate
            
            # Risk level classification
            if predicted_fraud_rate > 5:
                risk_level = "critical"
            elif predicted_fraud_rate > 2:
                risk_level = "high"
            elif predicted_fraud_rate > 1:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            result = {
                "current_fraud_rate": float(current_fraud_rate),
                "predicted_fraud_rate": float(predicted_fraud_rate),
                "fraud_rate_predictions": future_predictions,
                "risk_assessment": {
                    "risk_level": risk_level,
                    "risk_increase_percentage": float(risk_increase),
                    "trend": "increasing" if risk_increase > 0 else "decreasing" if risk_increase < 0 else "stable"
                },
                "model_confidence": float(model.score(X_scaled, y)),
                "external_factors_impact": external_factors
            }
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Fraud rates predicted",
                current_rate=current_fraud_rate,
                predicted_rate=predicted_fraud_rate,
                risk_level=risk_level,
                duration_ms=duration_ms
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error predicting fraud rates: {e}")
            raise

class TrendAnalyzer:
    """Advanced trend analysis engine"""
    
    def __init__(self):
        self.trend_models = {}
        
    async def analyze_payment_trends(
        self,
        time_series_data: List[Dict[str, Any]],
        trend_types: List[str] = None
    ) -> Dict[str, Any]:
        """Comprehensive payment trend analysis"""
        try:
            start_time = time.perf_counter()
            
            trend_types = trend_types or ['volume', 'revenue', 'average_transaction']
            
            if len(time_series_data) < 10:
                raise ValueError("Insufficient data for trend analysis")
            
            # Prepare data
            df = pd.DataFrame(time_series_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            trends = {}
            
            for trend_type in trend_types:
                if trend_type in df.columns:
                    trend_result = await self._analyze_single_trend(df, trend_type)
                    trends[trend_type] = trend_result
            
            # Cross-trend analysis
            correlations = await self._analyze_trend_correlations(df, trend_types)
            
            # Seasonal decomposition
            seasonal_analysis = await self._decompose_seasonality(df, trend_types)
            
            # Overall trend summary
            trend_summary = await self._create_trend_summary(trends)
            
            result = {
                "trend_analysis": trends,
                "correlations": correlations,
                "seasonal_analysis": seasonal_analysis,
                "trend_summary": trend_summary,
                "analysis_period": {
                    "start": df['timestamp'].min().isoformat(),
                    "end": df['timestamp'].max().isoformat(),
                    "data_points": len(df)
                }
            }
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Payment trends analyzed",
                trend_types=len(trend_types),
                data_points=len(df),
                duration_ms=duration_ms
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing payment trends: {e}")
            raise
    
    async def _analyze_single_trend(
        self,
        df: pd.DataFrame,
        column: str
    ) -> Dict[str, Any]:
        """Analyze trend for a single metric"""
        values = df[column].dropna()
        
        if len(values) < 2:
            return {"trend": "insufficient_data"}
        
        # Linear trend
        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)
        
        # Trend classification
        value_std = values.std()
        trend_strength = abs(slope) / value_std if value_std > 0 else 0
        
        if trend_strength < 0.1:
            trend_direction = "stable"
        elif slope > 0:
            trend_direction = "increasing"
        else:
            trend_direction = "decreasing"
        
        # Calculate growth rate
        if len(values) > 1:
            period_growth = ((values.iloc[-1] - values.iloc[0]) / values.iloc[0] * 100) if values.iloc[0] != 0 else 0
        else:
            period_growth = 0
        
        # Volatility analysis
        volatility = values.std() / values.mean() * 100 if values.mean() != 0 else 0
        
        return {
            "trend_direction": trend_direction,
            "trend_strength": float(trend_strength),
            "slope": float(slope),
            "period_growth_percentage": float(period_growth),
            "volatility": float(volatility),
            "current_value": float(values.iloc[-1]),
            "average_value": float(values.mean()),
            "min_value": float(values.min()),
            "max_value": float(values.max())
        }
    
    async def _analyze_trend_correlations(
        self,
        df: pd.DataFrame,
        trend_types: List[str]
    ) -> Dict[str, float]:
        """Analyze correlations between different trends"""
        correlations = {}
        
        available_columns = [col for col in trend_types if col in df.columns]
        
        for i, col1 in enumerate(available_columns):
            for col2 in available_columns[i+1:]:
                if col1 in df.columns and col2 in df.columns:
                    corr = df[[col1, col2]].corr().iloc[0, 1]
                    correlations[f"{col1}_vs_{col2}"] = float(corr) if not np.isnan(corr) else 0.0
        
        return correlations
    
    async def _decompose_seasonality(
        self,
        df: pd.DataFrame,
        trend_types: List[str]
    ) -> Dict[str, Any]:
        """Decompose seasonality patterns"""
        seasonal_analysis = {}
        
        for trend_type in trend_types:
            if trend_type in df.columns and len(df) >= 24:  # Need sufficient data
                values = df[trend_type].dropna()
                
                # Simple seasonal decomposition
                # Daily patterns (if timestamp includes hours)
                df_temp = df.copy()
                df_temp['hour'] = df_temp['timestamp'].dt.hour
                
                if 'hour' in df_temp.columns:
                    hourly_pattern = df_temp.groupby('hour')[trend_type].mean()
                    hourly_variation = hourly_pattern.std() / hourly_pattern.mean() * 100 if hourly_pattern.mean() != 0 else 0
                    
                    seasonal_analysis[trend_type] = {
                        "daily_seasonality": float(hourly_variation),
                        "peak_hour": int(hourly_pattern.idxmax()),
                        "low_hour": int(hourly_pattern.idxmin()),
                        "seasonality_strength": "high" if hourly_variation > 20 else "medium" if hourly_variation > 10 else "low"
                    }
        
        return seasonal_analysis
    
    async def _create_trend_summary(
        self,
        trends: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create overall trend summary"""
        if not trends:
            return {"status": "no_trends_analyzed"}
        
        # Count trend directions
        trend_directions = [trend["trend_direction"] for trend in trends.values() if "trend_direction" in trend]
        
        direction_counts = {
            "increasing": trend_directions.count("increasing"),
            "decreasing": trend_directions.count("decreasing"),
            "stable": trend_directions.count("stable")
        }
        
        # Overall assessment
        if direction_counts["increasing"] > direction_counts["decreasing"]:
            overall_trend = "positive"
        elif direction_counts["decreasing"] > direction_counts["increasing"]:
            overall_trend = "negative"
        else:
            overall_trend = "mixed"
        
        # Average growth rate
        growth_rates = [trend.get("period_growth_percentage", 0) for trend in trends.values()]
        avg_growth = statistics.mean(growth_rates) if growth_rates else 0
        
        return {
            "overall_trend": overall_trend,
            "trend_directions": direction_counts,
            "average_growth_rate": float(avg_growth),
            "total_metrics_analyzed": len(trends),
            "growth_assessment": "strong" if avg_growth > 10 else "moderate" if avg_growth > 5 else "weak"
        }

class PaymentForecasting:
    """Main payment forecasting orchestrator"""
    
    def __init__(self):
        self.forecasting_engine = ForecastingEngine()
        self.ml_predictor = MLPredictor()
        self.trend_analyzer = TrendAnalyzer()
        self.scenario_cache = {}
        
    async def forecast_payment_volumes(
        self,
        historical_data: List[Dict[str, Any]],
        forecast_horizon: ForecastHorizon = ForecastHorizon.MEDIUM_TERM,
        periods: int = 30
    ) -> ForecastResult:
        """Main entry point for payment volume forecasting"""
        request = ForecastRequest(
            forecast_type=ForecastType.VOLUME,
            horizon=forecast_horizon,
            periods=periods
        )
        
        return await self.forecasting_engine.forecast_payment_volumes(historical_data, request)
    
    async def predict_revenue_trends(
        self,
        revenue_data: List[Dict[str, Any]],
        prediction_periods: int = 30
    ) -> Dict[str, Any]:
        """Predict revenue trends"""
        return await self.ml_predictor.predict_revenue_trends(revenue_data, prediction_periods)
    
    async def forecast_fraud_rates(
        self,
        fraud_data: List[Dict[str, Any]],
        external_factors: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Forecast fraud rates"""
        return await self.ml_predictor.predict_fraud_rates(fraud_data, external_factors)
    
    async def predict_seasonal_patterns(
        self,
        historical_data: List[Dict[str, Any]],
        seasonality_types: List[SeasonalityType] = None
    ) -> Dict[str, Any]:
        """Predict seasonal patterns and their impact"""
        try:
            start_time = time.perf_counter()
            
            seasonality_types = seasonality_types or [SeasonalityType.DAILY, SeasonalityType.WEEKLY, SeasonalityType.MONTHLY]
            
            # Analyze trends first
            trends = await self.trend_analyzer.analyze_payment_trends(historical_data)
            
            # Detect seasonality in the data
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            seasonality_analysis = await self.forecasting_engine._detect_seasonality(df)
            
            # Predict future seasonal patterns
            seasonal_predictions = {}
            
            for seasonality_type in seasonality_types:
                if seasonality_type in seasonality_analysis:
                    strength = seasonality_analysis[seasonality_type]
                    
                    # Generate seasonal predictions based on strength
                    if strength > 0.3:  # Significant seasonality
                        prediction = await self._predict_seasonal_impact(
                            df, seasonality_type, strength
                        )
                        seasonal_predictions[seasonality_type.value] = prediction
            
            result = {
                "seasonality_detected": {k.value: v for k, v in seasonality_analysis.items()},
                "seasonal_predictions": seasonal_predictions,
                "trend_context": trends["trend_summary"],
                "overall_seasonality_score": sum(seasonality_analysis.values()) / len(seasonality_analysis)
            }
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Seasonal patterns predicted",
                seasonality_types=len(seasonality_types),
                patterns_detected=len(seasonal_predictions),
                duration_ms=duration_ms
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error predicting seasonal patterns: {e}")
            raise
    
    async def _predict_seasonal_impact(
        self,
        df: pd.DataFrame,
        seasonality_type: SeasonalityType,
        strength: float
    ) -> Dict[str, Any]:
        """Predict impact of specific seasonality type"""
        if seasonality_type == SeasonalityType.DAILY:
            # Hourly impact prediction
            hourly_avg = df.groupby(df['timestamp'].dt.hour)['volume'].mean()
            peak_hour = hourly_avg.idxmax()
            low_hour = hourly_avg.idxmin()
            
            return {
                "type": "daily",
                "strength": float(strength),
                "peak_period": f"Hour {peak_hour}",
                "low_period": f"Hour {low_hour}",
                "impact_multiplier": float(hourly_avg.max() / hourly_avg.mean()) if hourly_avg.mean() > 0 else 1,
                "recommendation": f"Expect {(hourly_avg.max() / hourly_avg.mean() - 1) * 100:.0f}% increase during peak hour"
            }
        
        elif seasonality_type == SeasonalityType.WEEKLY:
            # Weekly pattern prediction
            daily_avg = df.groupby(df['timestamp'].dt.dayofweek)['volume'].mean()
            peak_day = daily_avg.idxmax()
            low_day = daily_avg.idxmin()
            
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            return {
                "type": "weekly",
                "strength": float(strength),
                "peak_period": day_names[peak_day],
                "low_period": day_names[low_day],
                "impact_multiplier": float(daily_avg.max() / daily_avg.mean()) if daily_avg.mean() > 0 else 1,
                "recommendation": f"Plan for higher volume on {day_names[peak_day]}"
            }
        
        else:
            return {
                "type": seasonality_type.value,
                "strength": float(strength),
                "impact_multiplier": 1 + strength,
                "recommendation": f"Monitor {seasonality_type.value} patterns"
            }
    
    async def generate_demand_forecasts(
        self,
        historical_data: List[Dict[str, Any]],
        external_indicators: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate demand forecasts with external indicators"""
        try:
            start_time = time.perf_counter()
            
            external_indicators = external_indicators or {}
            
            # Forecast different aspects of demand
            volume_forecast = await self.forecast_payment_volumes(historical_data)
            revenue_forecast = await self.predict_revenue_trends(historical_data)
            
            # Analyze current trends
            trends = await self.trend_analyzer.analyze_payment_trends(historical_data)
            
            # Incorporate external indicators
            demand_adjustments = await self._calculate_demand_adjustments(
                external_indicators, trends
            )
            
            # Create comprehensive demand forecast
            result = {
                "volume_forecast": {
                    "predictions": volume_forecast.predictions,
                    "confidence": volume_forecast.model_accuracy.get('r2_score', 0),
                    "trend": volume_forecast.trend_analysis
                },
                "revenue_forecast": {
                    "predictions": revenue_forecast["predictions"]["ensemble"],
                    "confidence": revenue_forecast["confidence_metrics"]["ensemble_confidence"],
                    "trend": revenue_forecast["trend_analysis"]
                },
                "demand_adjustments": demand_adjustments,
                "external_factors_impact": external_indicators,
                "overall_demand_outlook": await self._assess_demand_outlook(
                    volume_forecast, revenue_forecast, demand_adjustments
                )
            }
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Demand forecasts generated",
                external_factors=len(external_indicators),
                outlook=result["overall_demand_outlook"]["assessment"],
                duration_ms=duration_ms
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating demand forecasts: {e}")
            raise
    
    async def _calculate_demand_adjustments(
        self,
        external_indicators: Dict[str, Any],
        trends: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate demand adjustments based on external factors"""
        adjustments = {}
        
        # Economic indicators
        if 'economic_growth' in external_indicators:
            growth = external_indicators['economic_growth']
            adjustments['economic_impact'] = growth * 0.5  # 50% correlation
        
        # Market conditions
        if 'market_volatility' in external_indicators:
            volatility = external_indicators['market_volatility']
            adjustments['volatility_impact'] = -volatility * 0.3  # Negative correlation
        
        # Seasonal factors
        if 'holiday_season' in external_indicators:
            adjustments['seasonal_impact'] = external_indicators['holiday_season'] * 0.2
        
        # Competition
        if 'competitive_pressure' in external_indicators:
            pressure = external_indicators['competitive_pressure']
            adjustments['competition_impact'] = -pressure * 0.4
        
        return adjustments
    
    async def _assess_demand_outlook(
        self,
        volume_forecast: ForecastResult,
        revenue_forecast: Dict[str, Any],
        demand_adjustments: Dict[str, float]
    ) -> Dict[str, Any]:
        """Assess overall demand outlook"""
        # Aggregate trend signals
        volume_trend = volume_forecast.trend_analysis.get('predicted_trend', 'stable')
        revenue_trend = revenue_forecast["trend_analysis"]["trend_direction"]
        
        # Calculate adjustment impact
        total_adjustment = sum(demand_adjustments.values()) if demand_adjustments else 0
        
        # Determine outlook
        positive_signals = 0
        negative_signals = 0
        
        if volume_trend == 'increasing':
            positive_signals += 1
        elif volume_trend == 'decreasing':
            negative_signals += 1
            
        if revenue_trend == 'increasing':
            positive_signals += 1
        elif revenue_trend == 'decreasing':
            negative_signals += 1
        
        if total_adjustment > 0:
            positive_signals += 1
        elif total_adjustment < 0:
            negative_signals += 1
        
        # Overall assessment
        if positive_signals > negative_signals:
            assessment = "positive"
        elif negative_signals > positive_signals:
            assessment = "negative"
        else:
            assessment = "neutral"
        
        return {
            "assessment": assessment,
            "confidence": abs(positive_signals - negative_signals) / max(positive_signals + negative_signals, 1),
            "key_factors": {
                "volume_trend": volume_trend,
                "revenue_trend": revenue_trend,
                "external_adjustment": total_adjustment
            },
            "recommendations": await self._generate_demand_recommendations(assessment, total_adjustment)
        }
    
    async def _generate_demand_recommendations(
        self,
        assessment: str,
        adjustment: float
    ) -> List[str]:
        """Generate recommendations based on demand assessment"""
        recommendations = []
        
        if assessment == "positive":
            recommendations.extend([
                "Prepare for increased demand by scaling infrastructure",
                "Consider expanding service offerings",
                "Optimize pricing strategies to capture value"
            ])
        elif assessment == "negative":
            recommendations.extend([
                "Implement cost reduction measures",
                "Focus on customer retention strategies",
                "Diversify revenue streams"
            ])
        else:
            recommendations.extend([
                "Maintain current operational capacity",
                "Monitor market conditions closely",
                "Prepare contingency plans for demand shifts"
            ])
        
        if abs(adjustment) > 0.1:
            recommendations.append(f"External factors indicate {abs(adjustment)*100:.0f}% impact on demand")
        
        return recommendations
    
    async def create_scenario_projections(
        self,
        base_data: List[Dict[str, Any]],
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create scenario-based projections"""
        try:
            start_time = time.perf_counter()
            
            # Base forecast
            base_forecast = await self.forecast_payment_volumes(base_data)
            
            scenario_results = {}
            
            for scenario in scenarios:
                scenario_name = scenario.get('name', 'unnamed_scenario')
                scenario_adjustments = scenario.get('adjustments', {})
                
                # Apply scenario adjustments to base predictions
                adjusted_predictions = []
                for pred in base_forecast.predictions:
                    adjusted_pred = pred
                    
                    # Apply volume adjustments
                    if 'volume_multiplier' in scenario_adjustments:
                        adjusted_pred *= scenario_adjustments['volume_multiplier']
                    
                    # Apply additive adjustments
                    if 'volume_change' in scenario_adjustments:
                        adjusted_pred += scenario_adjustments['volume_change']
                    
                    adjusted_predictions.append(max(0, adjusted_pred))
                
                # Calculate scenario impact
                base_total = sum(base_forecast.predictions)
                scenario_total = sum(adjusted_predictions)
                impact_percentage = ((scenario_total - base_total) / base_total * 100) if base_total > 0 else 0
                
                scenario_results[scenario_name] = {
                    "predictions": adjusted_predictions,
                    "total_impact_percentage": float(impact_percentage),
                    "adjustments_applied": scenario_adjustments,
                    "scenario_description": scenario.get('description', ''),
                    "confidence": base_forecast.model_accuracy.get('r2_score', 0) * 0.8  # Reduced confidence for scenarios
                }
            
            result = {
                "base_forecast": {
                    "predictions": base_forecast.predictions,
                    "timestamps": [ts.isoformat() for ts in base_forecast.timestamps],
                    "confidence": base_forecast.model_accuracy.get('r2_score', 0)
                },
                "scenarios": scenario_results,
                "scenario_comparison": await self._compare_scenarios(scenario_results)
            }
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Scenario projections created",
                scenarios_count=len(scenarios),
                duration_ms=duration_ms
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating scenario projections: {e}")
            raise
    
    async def _compare_scenarios(
        self,
        scenario_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare different scenarios"""
        if not scenario_results:
            return {}
        
        # Find best and worst case scenarios
        impacts = {name: result["total_impact_percentage"] 
                  for name, result in scenario_results.items()}
        
        best_case = max(impacts.keys(), key=lambda k: impacts[k])
        worst_case = min(impacts.keys(), key=lambda k: impacts[k])
        
        return {
            "best_case_scenario": {
                "name": best_case,
                "impact": impacts[best_case]
            },
            "worst_case_scenario": {
                "name": worst_case,
                "impact": impacts[worst_case]
            },
            "scenario_range": {
                "max_impact": max(impacts.values()),
                "min_impact": min(impacts.values()),
                "range_percentage": max(impacts.values()) - min(impacts.values())
            }
        }

if __name__ == "__main__":
    # Enterprise testing and validation
    async def test_payment_forecasting():
        """Test payment forecasting functionality"""
        forecasting = PaymentForecasting()
        
        # Create test historical data
        base_time = datetime.utcnow() - timedelta(days=90)
        historical_data = []
        
        for i in range(90):  # 90 days of data
            daily_volume = 1000 + np.random.normal(0, 100) + (i * 2)  # Upward trend
            daily_amount = daily_volume * (50 + np.random.normal(0, 10))
            
            historical_data.append({
                'timestamp': base_time + timedelta(days=i),
                'volume': max(0, int(daily_volume)),
                'amount': max(0, daily_amount),
                'revenue': max(0, daily_amount)
            })
        
        # Test volume forecasting
        print("Testing volume forecasting...")
        volume_forecast = await forecasting.forecast_payment_volumes(historical_data)
        print(f"Volume forecast: {len(volume_forecast.predictions)} predictions")
        print(f"Model accuracy (R²): {volume_forecast.model_accuracy.get('r2_score', 0):.3f}")
        
        # Test revenue trend prediction
        print("\nTesting revenue trend prediction...")
        revenue_trends = await forecasting.predict_revenue_trends(historical_data)
        print(f"Revenue trend: {revenue_trends['trend_analysis']['trend_direction']}")
        
        # Test seasonal pattern prediction
        print("\nTesting seasonal pattern prediction...")
        seasonal_patterns = await forecasting.predict_seasonal_patterns(historical_data)
        print(f"Seasonality score: {seasonal_patterns['overall_seasonality_score']:.3f}")
        
        # Test scenario projections
        print("\nTesting scenario projections...")
        scenarios = [
            {
                'name': 'optimistic',
                'description': 'High growth scenario',
                'adjustments': {'volume_multiplier': 1.2}
            },
            {
                'name': 'pessimistic',
                'description': 'Economic downturn',
                'adjustments': {'volume_multiplier': 0.8}
            }
        ]
        
        scenario_projections = await forecasting.create_scenario_projections(historical_data, scenarios)
        print(f"Created {len(scenario_projections['scenarios'])} scenario projections")
        
        print("\nForecasting tests completed successfully!")
    
    # Run tests
    asyncio.run(test_payment_forecasting())