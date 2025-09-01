"""🚀 Revenue Forecaster - AI-Powered Revenue Prediction Engine
==========================================================

Ultra-advanced revenue forecasting system using machine learning,
statistical modeling, and predictive analytics to provide accurate
revenue predictions for content creators.

Created by: Fahed Mlaiel <mlaiel@live.de>
© 2025 Fahed Mlaiel. All rights reserved.

Team Specialists:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ STRICT COPYRIGHT WARNING - UNAUTHORIZED USE PROHIBITED ⚠️
Contact mlaiel@live.de for licensing inquiries.

Business Logic: Multi-Format Upload → AI Protection → SEO → Collaboration → Revenue Forecasting
=============================================================================================
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, ElasticNet
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose

from ...core.database import DatabaseManager
from ...core.security import SecurityManager
from ...core.monitoring import MetricsCollector
from ...ai.engines.ml_pipeline import MLPipeline

logger = logging.getLogger(__name__)


class ForecastHorizon(Enum):
    """Forecast time horizons"""
    SHORT_TERM = "short_term"  # 1-7 days
    MEDIUM_TERM = "medium_term"  # 1-4 weeks
    LONG_TERM = "long_term"  # 1-12 months


class ForecastModel(Enum):
    """Available forecasting models"""
    ARIMA = "arima"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    XGBOOST = "xgboost"
    LINEAR_REGRESSION = "linear_regression"
    ENSEMBLE = "ensemble"


@dataclass
class ForecastResult:
    """Revenue forecast result"""
    forecast_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    model_used: ForecastModel = ForecastModel.ENSEMBLE
    horizon: ForecastHorizon = ForecastHorizon.MEDIUM_TERM
    predictions: List[Dict[str, Any]] = field(default_factory=list)
    confidence_intervals: Dict[str, List[float]] = field(default_factory=dict)
    model_accuracy: Dict[str, float] = field(default_factory=dict)
    feature_importance: Dict[str, float] = field(default_factory=dict)
    scenarios: Dict[str, List[float]] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelPerformance:
    """Model performance metrics"""
    model_name: str
    mae: float  # Mean Absolute Error
    rmse: float  # Root Mean Square Error
    mape: float  # Mean Absolute Percentage Error
    r2: float  # R-squared
    accuracy_score: float
    last_updated: datetime = field(default_factory=datetime.utcnow)


class RevenueForecaster:
    """
    Ultra-advanced AI-powered revenue forecasting system
    
    Features:
    - Multiple ML models (ARIMA, Random Forest, XGBoost, etc.)
    - Ensemble modeling for improved accuracy
    - Seasonal and trend decomposition
    - Feature engineering with external factors
    - Confidence intervals and scenario analysis
    - Model performance monitoring and retraining
    - Real-time prediction updates
    - Multi-horizon forecasting
    """
    
    def __init__(self,
                 db_manager: DatabaseManager,
                 security_manager: SecurityManager,
                 metrics_collector: MetricsCollector):
        self.db = db_manager
        self.security = security_manager
        self.metrics = metrics_collector
        self.ml_pipeline = MLPipeline()
        
        # Forecasting models
        self.models = {
            ForecastModel.RANDOM_FOREST: RandomForestRegressor(n_estimators=100, random_state=42),
            ForecastModel.GRADIENT_BOOSTING: GradientBoostingRegressor(n_estimators=100, random_state=42),
            ForecastModel.XGBOOST: xgb.XGBRegressor(n_estimators=100, random_state=42),
            ForecastModel.LINEAR_REGRESSION: LinearRegression(),
            ForecastModel.ENSEMBLE: None  # Ensemble of above models
        }
        
        # Model performance tracking
        self._model_performance = {}
        self._model_weights = {}
        
        # Data preprocessing
        self.scalers = {
            'standard': StandardScaler(),
            'minmax': MinMaxScaler()
        }
        
        # Forecast cache
        self._forecast_cache = {}
        
    async def initialize(self):
        """Initialize the revenue forecaster"""
        try:
            # Initialize ML pipeline
            await self.ml_pipeline.initialize()
            
            # Load trained models if available
            await self._load_trained_models()
            
            # Initialize model performance tracking
            await self._initialize_model_performance()
            
            # Load external data sources for features
            await self._setup_external_data_sources()
            
            logger.info("Revenue forecaster initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize revenue forecaster: {e}")
            raise

    async def generate_forecast(self,
                              creator_id: str,
                              horizon: ForecastHorizon = ForecastHorizon.MEDIUM_TERM,
                              model: ForecastModel = ForecastModel.ENSEMBLE,
                              include_scenarios: bool = True,
                              confidence_level: float = 0.95) -> ForecastResult:
        """
        Generate revenue forecast for a creator
        
        Args:
            creator_id: Creator ID
            horizon: Forecast horizon
            model: ML model to use
            include_scenarios: Include scenario analysis
            confidence_level: Confidence level for intervals
            
        Returns:
            Comprehensive forecast results
        """
        try:
            # Validate inputs
            await self._validate_forecast_request(creator_id, horizon, model)
            
            # Prepare historical data for modeling
            historical_data = await self._prepare_historical_data(creator_id, horizon)
            
            if len(historical_data) < 30:  # Need minimum data for reliable forecasting
                raise ValueError("Insufficient historical data for reliable forecasting")
            
            # Feature engineering
            features_df = await self._engineer_features(creator_id, historical_data, horizon)
            
            # Split data for validation
            train_data, validation_data = await self._split_time_series_data(features_df)
            
            # Train and select best model
            if model == ForecastModel.ENSEMBLE:
                best_model = await self._train_ensemble_model(train_data, validation_data)
            else:
                best_model = await self._train_single_model(model, train_data, validation_data)
            
            # Generate predictions
            predictions = await self._generate_predictions(
                best_model, features_df, horizon
            )
            
            # Calculate confidence intervals
            confidence_intervals = await self._calculate_confidence_intervals(
                best_model, predictions, confidence_level
            )
            
            # Feature importance analysis
            feature_importance = await self._analyze_feature_importance(best_model)
            
            # Scenario analysis
            scenarios = {}
            if include_scenarios:
                scenarios = await self._generate_scenarios(
                    creator_id, best_model, features_df, horizon
                )
            
            # Model accuracy metrics
            model_accuracy = await self._calculate_model_accuracy(
                best_model, validation_data
            )
            
            # Create forecast result
            forecast = ForecastResult(
                creator_id=creator_id,
                model_used=model if model != ForecastModel.ENSEMBLE else ForecastModel.ENSEMBLE,
                horizon=horizon,
                predictions=predictions,
                confidence_intervals=confidence_intervals,
                model_accuracy=model_accuracy,
                feature_importance=feature_importance,
                scenarios=scenarios,
                metadata={
                    'data_points_used': len(historical_data),
                    'confidence_level': confidence_level,
                    'forecast_generation_time': datetime.utcnow().isoformat()
                }
            )
            
            # Store forecast result
            await self._store_forecast_result(forecast)
            
            # Update model performance metrics
            await self._update_model_performance(model, model_accuracy)
            
            # Cache forecast for quick retrieval
            self._forecast_cache[f"{creator_id}_{horizon.value}_{model.value}"] = forecast
            
            logger.info(f"Revenue forecast generated for creator {creator_id} using {model.value}")
            return forecast
            
        except Exception as e:
            logger.error(f"Revenue forecast generation failed: {e}")
            raise

    async def _prepare_historical_data(self,
                                     creator_id: str,
                                     horizon: ForecastHorizon) -> pd.DataFrame:
        """Prepare historical revenue data for modeling"""
        try:
            # Determine lookback period based on horizon
            if horizon == ForecastHorizon.SHORT_TERM:
                lookback_days = 90  # 3 months
            elif horizon == ForecastHorizon.MEDIUM_TERM:
                lookback_days = 365  # 1 year
            else:  # LONG_TERM
                lookback_days = 730  # 2 years
            
            # Fetch historical revenue data
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=lookback_days)
            
            query = """
                SELECT 
                    DATE(calculation_date) as date,
                    platform,
                    revenue_type,
                    SUM(gross_amount) as gross_revenue,
                    SUM(net_amount) as net_revenue,
                    SUM(platform_fee) as platform_fees,
                    COUNT(*) as transaction_count
                FROM revenue_calculations 
                WHERE creator_id = %s 
                AND calculation_date BETWEEN %s AND %s
                GROUP BY DATE(calculation_date), platform, revenue_type
                ORDER BY date ASC
            """
            
            data = await self.db.fetch_all(query, (creator_id, start_date, end_date))
            
            # Convert to DataFrame
            df = pd.DataFrame([
                {
                    'date': row['date'],
                    'platform': row['platform'],
                    'revenue_type': row['revenue_type'],
                    'gross_revenue': float(row['gross_revenue']),
                    'net_revenue': float(row['net_revenue']),
                    'platform_fees': float(row['platform_fees']),
                    'transaction_count': row['transaction_count']
                }
                for row in data
            ])
            
            if df.empty:
                return df
            
            # Aggregate by date (sum across platforms and revenue types)
            daily_df = df.groupby('date').agg({
                'gross_revenue': 'sum',
                'net_revenue': 'sum',
                'platform_fees': 'sum',
                'transaction_count': 'sum'
            }).reset_index()
            
            # Ensure continuous date range (fill missing dates with zeros)
            daily_df['date'] = pd.to_datetime(daily_df['date'])
            daily_df = daily_df.set_index('date')
            full_date_range = pd.date_range(start=start_date.date(), end=end_date.date(), freq='D')
            daily_df = daily_df.reindex(full_date_range, fill_value=0)
            daily_df.index.name = 'date'
            
            return daily_df.reset_index()
            
        except Exception as e:
            logger.error(f"Historical data preparation failed: {e}")
            raise

    async def _engineer_features(self,
                               creator_id: str,
                               historical_data: pd.DataFrame,
                               horizon: ForecastHorizon) -> pd.DataFrame:
        """Engineer features for forecasting models"""
        try:
            df = historical_data.copy()
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            
            # Time-based features
            df['day_of_week'] = df.index.dayofweek
            df['day_of_month'] = df.index.day
            df['day_of_year'] = df.index.dayofyear
            df['week_of_year'] = df.index.isocalendar().week
            df['month'] = df.index.month
            df['quarter'] = df.index.quarter
            df['is_weekend'] = (df.index.dayofweek >= 5).astype(int)
            df['is_month_end'] = df.index.is_month_end.astype(int)
            df['is_month_start'] = df.index.is_month_start.astype(int)
            
            # Revenue-based features
            for col in ['net_revenue', 'gross_revenue', 'transaction_count']:
                if col in df.columns:
                    # Lagged features
                    df[f'{col}_lag_1'] = df[col].shift(1)
                    df[f'{col}_lag_7'] = df[col].shift(7)
                    df[f'{col}_lag_30'] = df[col].shift(30)
                    
                    # Rolling statistics
                    df[f'{col}_ma_7'] = df[col].rolling(window=7).mean()
                    df[f'{col}_ma_30'] = df[col].rolling(window=30).mean()
                    df[f'{col}_std_7'] = df[col].rolling(window=7).std()
                    df[f'{col}_std_30'] = df[col].rolling(window=30).std()
                    
                    # Growth rates
                    df[f'{col}_pct_change_1'] = df[col].pct_change(1)
                    df[f'{col}_pct_change_7'] = df[col].pct_change(7)
                    df[f'{col}_pct_change_30'] = df[col].pct_change(30)
            
            # Seasonal decomposition for net_revenue
            if len(df) > 60 and 'net_revenue' in df.columns:
                try:
                    decomposition = seasonal_decompose(
                        df['net_revenue'].fillna(0), 
                        model='additive', 
                        period=7  # Weekly seasonality
                    )
                    df['revenue_trend'] = decomposition.trend
                    df['revenue_seasonal'] = decomposition.seasonal
                    df['revenue_residual'] = decomposition.resid
                except Exception:
                    # If seasonal decomposition fails, use simple moving averages
                    df['revenue_trend'] = df['net_revenue'].rolling(window=14).mean()
                    df['revenue_seasonal'] = 0
                    df['revenue_residual'] = df['net_revenue'] - df['revenue_trend']
            
            # External factors (if available)
            external_features = await self._get_external_factors(creator_id, df.index)
            df = df.join(external_features)
            
            # Drop rows with too many NaN values
            df = df.dropna(thresh=len(df.columns) * 0.7)  # Keep rows with at least 70% non-null values
            
            # Fill remaining NaN values
            df = df.fillna(method='ffill').fillna(method='bfill').fillna(0)
            
            return df.reset_index()
            
        except Exception as e:
            logger.error(f"Feature engineering failed: {e}")
            raise

    async def _train_ensemble_model(self, train_data: pd.DataFrame, validation_data: pd.DataFrame) -> Dict[str, Any]:
        """Train ensemble model combining multiple algorithms"""
        try:
            # Prepare training data
            feature_cols = [col for col in train_data.columns if col not in ['date', 'net_revenue']]
            X_train = train_data[feature_cols]
            y_train = train_data['net_revenue']
            X_val = validation_data[feature_cols]
            y_val = validation_data['net_revenue']
            
            # Scale features
            X_train_scaled = self.scalers['standard'].fit_transform(X_train)
            X_val_scaled = self.scalers['standard'].transform(X_val)
            
            # Train individual models
            ensemble_models = {}
            model_weights = {}
            
            for model_name, model in self.models.items():
                if model_name == ForecastModel.ENSEMBLE or model_name == ForecastModel.ARIMA:
                    continue
                
                try:
                    # Train model
                    if model_name in [ForecastModel.RANDOM_FOREST, ForecastModel.GRADIENT_BOOSTING, ForecastModel.XGBOOST]:
                        model.fit(X_train, y_train)
                    else:  # Linear models
                        model.fit(X_train_scaled, y_train)
                    
                    # Validate model
                    if model_name in [ForecastModel.RANDOM_FOREST, ForecastModel.GRADIENT_BOOSTING, ForecastModel.XGBOOST]:
                        y_pred = model.predict(X_val)
                    else:
                        y_pred = model.predict(X_val_scaled)
                    
                    # Calculate model performance
                    mae = mean_absolute_error(y_val, y_pred)
                    rmse = np.sqrt(mean_squared_error(y_val, y_pred))
                    r2 = r2_score(y_val, y_pred)
                    
                    # Weight based on inverse of MAE (better models get higher weight)
                    model_weight = 1 / (mae + 1e-6)
                    
                    ensemble_models[model_name] = {
                        'model': model,
                        'mae': mae,
                        'rmse': rmse,
                        'r2': r2,
                        'weight': model_weight
                    }
                    
                    model_weights[model_name.value] = model_weight
                    
                except Exception as e:
                    logger.warning(f"Failed to train {model_name.value}: {e}")
                    continue
            
            # Normalize weights
            total_weight = sum(model_weights.values())
            if total_weight > 0:
                model_weights = {k: v / total_weight for k, v in model_weights.items()}
            
            return {
                'type': 'ensemble',
                'models': ensemble_models,
                'weights': model_weights,
                'feature_columns': feature_cols,
                'scaler': self.scalers['standard']
            }
            
        except Exception as e:
            logger.error(f"Ensemble model training failed: {e}")
            raise

    async def _generate_predictions(self,
                                  model_info: Dict[str, Any],
                                  features_df: pd.DataFrame,
                                  horizon: ForecastHorizon) -> List[Dict[str, Any]]:
        """Generate revenue predictions using trained model"""
        try:
            predictions = []
            
            # Determine prediction periods
            if horizon == ForecastHorizon.SHORT_TERM:
                prediction_days = 7
            elif horizon == ForecastHorizon.MEDIUM_TERM:
                prediction_days = 30
            else:  # LONG_TERM
                prediction_days = 365
            
            # Get the last date from features
            last_date = pd.to_datetime(features_df['date']).max()
            
            # Generate predictions for each future period
            for i in range(1, prediction_days + 1):
                prediction_date = last_date + timedelta(days=i)
                
                # Create features for prediction date
                pred_features = await self._create_prediction_features(
                    features_df, prediction_date, i
                )
                
                # Make prediction using ensemble or single model
                if model_info['type'] == 'ensemble':
                    pred_value = await self._predict_ensemble(model_info, pred_features)
                else:
                    pred_value = await self._predict_single(model_info, pred_features)
                
                predictions.append({
                    'date': prediction_date.isoformat(),
                    'predicted_revenue': max(0, float(pred_value)),  # Ensure non-negative
                    'period': i,
                    'horizon': horizon.value
                })
            
            return predictions
            
        except Exception as e:
            logger.error(f"Prediction generation failed: {e}")
            raise

    async def _predict_ensemble(self, model_info: Dict[str, Any], features: np.ndarray) -> float:
        """Make prediction using ensemble model"""
        try:
            weighted_predictions = []
            
            for model_name, model_data in model_info['models'].items():
                model = model_data['model']
                weight = model_data['weight']
                
                # Make prediction based on model type
                if model_name in [ForecastModel.RANDOM_FOREST, ForecastModel.GRADIENT_BOOSTING, ForecastModel.XGBOOST]:
                    prediction = model.predict(features.reshape(1, -1))[0]
                else:
                    # Scale features for linear models
                    features_scaled = model_info['scaler'].transform(features.reshape(1, -1))
                    prediction = model.predict(features_scaled)[0]
                
                weighted_predictions.append(prediction * weight)
            
            return sum(weighted_predictions)
            
        except Exception as e:
            logger.error(f"Ensemble prediction failed: {e}")
            return 0.0

    async def _generate_scenarios(self,
                                creator_id: str,
                                model_info: Dict[str, Any],
                                features_df: pd.DataFrame,
                                horizon: ForecastHorizon) -> Dict[str, List[float]]:
        """Generate optimistic, pessimistic, and realistic scenarios"""
        try:
            # Get baseline predictions
            baseline_predictions = await self._generate_predictions(model_info, features_df, horizon)
            baseline_values = [pred['predicted_revenue'] for pred in baseline_predictions]
            
            # Calculate historical volatility
            historical_revenue = features_df['net_revenue'].values
            revenue_std = np.std(historical_revenue)
            revenue_mean = np.mean(historical_revenue)
            volatility_factor = revenue_std / revenue_mean if revenue_mean > 0 else 0.2
            
            scenarios = {
                'realistic': baseline_values,
                'optimistic': [val * (1 + volatility_factor) for val in baseline_values],
                'pessimistic': [max(0, val * (1 - volatility_factor)) for val in baseline_values],
                'best_case': [val * 1.5 for val in baseline_values],
                'worst_case': [max(0, val * 0.5) for val in baseline_values]
            }
            
            # Add market condition scenarios
            market_scenarios = await self._generate_market_scenarios(
                creator_id, baseline_values, horizon
            )
            scenarios.update(market_scenarios)
            
            return scenarios
            
        except Exception as e:
            logger.error(f"Scenario generation failed: {e}")
            return {}

    async def get_forecast_accuracy(self, creator_id: str) -> Dict[str, Any]:
        """Get forecast accuracy metrics for a creator"""
        try:
            # Get recent forecasts and actual results
            query = """
                SELECT 
                    f.forecast_id,
                    f.model_used,
                    f.horizon,
                    f.predictions,
                    f.created_at,
                    r.actual_revenue
                FROM forecasts f
                LEFT JOIN (
                    SELECT 
                        creator_id,
                        DATE(calculation_date) as date,
                        SUM(net_amount) as actual_revenue
                    FROM revenue_calculations
                    GROUP BY creator_id, DATE(calculation_date)
                ) r ON f.creator_id = r.creator_id
                WHERE f.creator_id = %s 
                AND f.created_at >= NOW() - INTERVAL '90 days'
                ORDER BY f.created_at DESC
            """
            
            forecast_data = await self.db.fetch_all(query, (creator_id,))
            
            # Calculate accuracy metrics
            accuracy_metrics = {
                'overall_accuracy': 0.0,
                'model_comparison': {},
                'horizon_comparison': {},
                'recent_performance': []
            }
            
            # Process forecast accuracy
            for forecast in forecast_data:
                predictions = json.loads(forecast['predictions'])
                # Compare with actual results and calculate metrics
                # Implementation would involve detailed comparison logic
            
            return accuracy_metrics
            
        except Exception as e:
            logger.error(f"Forecast accuracy calculation failed: {e}")
            return {}

    async def cleanup(self):
        """Cleanup forecaster resources"""
        try:
            # Clear model cache
            self._forecast_cache.clear()
            
            # Cleanup ML pipeline
            await self.ml_pipeline.cleanup()
            
            logger.info("Revenue forecaster cleanup completed")
            
        except Exception as e:
            logger.error(f"Revenue forecaster cleanup failed: {e}")
