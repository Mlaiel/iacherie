"""
Revenue Forecasting & Predictive Analytics

Système avancé de prévision des revenus avec intelligence artificielle,
machine learning et analytics prédictifs pour la plateforme IA Influencer Agent.

Architecture: AI-powered revenue forecasting with predictive analytics and ML models
Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe Projet: Lead AI Developer + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

  AVERTISSEMENT DE PROPRIÉTÉ INTELLECTUELLE 
Ce code et concept sont la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute utilisation, reproduction, ou distribution sans autorisation écrite explicite est strictement interdite.
Violation = Poursuites judiciaires selon le droit allemand et international.
"""

from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import uuid
import logging
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from sqlalchemy import Column, String, Numeric, DateTime, Integer, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base

# ML imports
import tensorflow as tf
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from ..models.base import BaseModel, TimestampMixin
from ...core.database import DatabaseManager
from ...core.cache import CacheManager
from ...core.events import EventEmitter
from ...ml.feature_engineering import FeatureEngineeringEngine
from ...ml.model_training import ModelTrainingEngine

logger = logging.getLogger(__name__)

Base = declarative_base()


class ForecastHorizon(Enum):
    """Horizons de prévision"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class ForecastModel(Enum):
    """Modèles de prévision disponibles"""
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    XGBOOST = "xgboost"
    LSTM_NEURAL_NETWORK = "lstm_neural_network"
    TRANSFORMER = "transformer"
    ARIMA = "arima"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    ENSEMBLE = "ensemble"
    AI_HYBRID = "ai_hybrid"


class ForecastAccuracy(Enum):
    """Niveaux de précision des prévisions"""
    EXCELLENT = "excellent"  # > 95%
    VERY_GOOD = "very_good"  # 90-95%
    GOOD = "good"           # 80-90%
    FAIR = "fair"           # 70-80%
    POOR = "poor"           # < 70%


@dataclass
class RevenueForecastModel(BaseModel, TimestampMixin):
    """
    Modèle des prévisions de revenus
    """
    __tablename__ = "revenue_forecasts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    forecast_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Identifiants
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    content_id = Column(UUID(as_uuid=True), ForeignKey("content.id"), nullable=True, index=True)
    
    # Paramètres de prévision
    forecast_horizon = Column(String(20), nullable=False)
    forecast_periods = Column(Integer, nullable=False)
    prediction_model = Column(String(50), nullable=False)
    
    # Données historiques utilisées
    training_data_start = Column(DateTime, nullable=False)
    training_data_end = Column(DateTime, nullable=False)
    training_samples_count = Column(Integer, nullable=False)
    
    # Prévisions
    forecasted_revenue = Column(Numeric(15, 4), nullable=False)
    confidence_interval_lower = Column(Numeric(15, 4), nullable=False)
    confidence_interval_upper = Column(Numeric(15, 4), nullable=False)
    confidence_level = Column(Numeric(3, 2), nullable=False, default=0.95)
    
    # Métriques de qualité
    model_accuracy = Column(Numeric(5, 4), nullable=False)
    accuracy_rating = Column(String(20), nullable=False)
    mae_score = Column(Numeric(15, 4), nullable=True)
    rmse_score = Column(Numeric(15, 4), nullable=True)
    r2_score = Column(Numeric(5, 4), nullable=True)
    
    # Facteurs influents
    key_features = Column(JSONB, nullable=True)
    seasonal_factors = Column(JSONB, nullable=True)
    trend_analysis = Column(JSONB, nullable=True)
    
    # Prévision détaillée par période
    period_breakdown = Column(JSONB, nullable=False)
    platform_breakdown = Column(JSONB, nullable=True)
    content_type_breakdown = Column(JSONB, nullable=True)
    
    # Métadonnées du modèle
    model_parameters = Column(JSONB, nullable=True)
    feature_importance = Column(JSONB, nullable=True)
    training_metrics = Column(JSONB, nullable=True)
    
    # Validité
    forecast_created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    forecast_valid_until = Column(DateTime, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)


@dataclass
class ForecastAccuracyTrackingModel(BaseModel, TimestampMixin):
    """
    Modèle de suivi de la précision des prévisions
    """
    __tablename__ = "forecast_accuracy_tracking"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tracking_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Prévision liée
    forecast_id = Column(UUID(as_uuid=True), ForeignKey("revenue_forecasts.id"), nullable=False, index=True)
    
    # Période de validation
    validation_date = Column(DateTime, nullable=False)
    actual_revenue = Column(Numeric(15, 4), nullable=False)
    predicted_revenue = Column(Numeric(15, 4), nullable=False)
    
    # Métriques d'erreur
    absolute_error = Column(Numeric(15, 4), nullable=False)
    percentage_error = Column(Numeric(5, 4), nullable=False)
    squared_error = Column(Numeric(15, 4), nullable=False)
    
    # Analyse de l'erreur
    error_analysis = Column(JSONB, nullable=True)
    contributing_factors = Column(JSONB, nullable=True)
    
    # Actions correctives
    model_adjustment_needed = Column(Boolean, nullable=False, default=False)
    adjustment_recommendations = Column(JSONB, nullable=True)


@dataclass
class MarketTrendAnalysisModel(BaseModel, TimestampMixin):
    """
    Modèle d'analyse des tendances de marché
    """
    __tablename__ = "market_trend_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Paramètres d'analyse
    analysis_period_start = Column(DateTime, nullable=False)
    analysis_period_end = Column(DateTime, nullable=False)
    market_segment = Column(String(100), nullable=False)
    
    # Tendances identifiées
    overall_trend = Column(String(20), nullable=False)  # rising, falling, stable
    trend_strength = Column(Numeric(3, 2), nullable=False)
    volatility_index = Column(Numeric(5, 4), nullable=False)
    
    # Facteurs saisonniers
    seasonal_patterns = Column(JSONB, nullable=True)
    cyclical_patterns = Column(JSONB, nullable=True)
    irregular_patterns = Column(JSONB, nullable=True)
    
    # Analyse concurrentielle
    market_share_trends = Column(JSONB, nullable=True)
    competitive_intelligence = Column(JSONB, nullable=True)
    platform_performance = Column(JSONB, nullable=True)
    
    # Prédictions de marché
    market_forecast = Column(JSONB, nullable=False)
    risk_factors = Column(JSONB, nullable=True)
    opportunity_analysis = Column(JSONB, nullable=True)
    
    # Recommandations
    strategic_recommendations = Column(JSONB, nullable=True)
    tactical_suggestions = Column(JSONB, nullable=True)


class RevenueForecastingEngine:
    """
    Moteur principal de prévision des revenus par IA
    """
    
    def __init__(self, db_session: Session, cache_manager: CacheManager):
        self.db_session = db_session
        self.cache_manager = cache_manager
        self.feature_engineer = FeatureEngineeringEngine()
        self.model_trainer = ModelTrainingEngine()
        self.event_emitter = EventEmitter()
        
        # Modèles ML pré-entraînés
        self.models = {}
        self.scalers = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """
        Initialise les modèles de machine learning
        """
        self.models = {
            'linear_regression': LinearRegression(),
            'random_forest': RandomForestRegressor(
                n_estimators=200,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            ),
            'gradient_boosting': GradientBoostingRegressor(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            ),
            'xgboost': xgb.XGBRegressor(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1
            )
        }
        
        # Scalers pour la normalisation
        self.scalers = {
            'standard': StandardScaler(),
            'minmax': MinMaxScaler()
        }
    
    async def generate_revenue_forecast(
        self,
        user_id: uuid.UUID,
        forecast_horizon: ForecastHorizon,
        forecast_periods: int = 12,
        model_type: ForecastModel = ForecastModel.ENSEMBLE,
        content_id: Optional[uuid.UUID] = None
    ) -> RevenueForecastModel:
        """
        Génère une prévision de revenus complète
        """



        try:
            # Préparation des données
            training_data = await self._prepare_training_data(user_id, content_id)
            
            if len(training_data) < 10:  # Données insuffisantes
                raise ValueError("Insufficient historical data for forecasting")
            
            # Ingénierie des caractéristiques
            features, targets = await self._engineer_features(training_data, forecast_horizon)
            
            # Sélection et entraînement du modèle
            if model_type == ForecastModel.ENSEMBLE:
                forecast_results = await self._generate_ensemble_forecast(
                    features, targets, forecast_periods
                )
            else:
                forecast_results = await self._generate_single_model_forecast(
                    features, targets, forecast_periods, model_type
                )
            
            # Analyse de tendance et saisonnalité
            trend_analysis = await self._analyze_trends(training_data)
            seasonal_analysis = await self._analyze_seasonality(training_data, forecast_horizon)
            
            # Calcul des intervalles de confiance
            confidence_intervals = await self._calculate_confidence_intervals(
                forecast_results, training_data
            )
            
            # Création de la prévision
            forecast = RevenueForecastModel(
                forecast_id=f"FORECAST_{datetime.utcnow().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}",
                user_id=user_id,
                content_id=content_id,
                forecast_horizon=forecast_horizon.value,
                forecast_periods=forecast_periods,
                prediction_model=model_type.value,
                training_data_start=training_data['date'].min(),
                training_data_end=training_data['date'].max(),
                training_samples_count=len(training_data),
                forecasted_revenue=forecast_results['total_forecast'],
                confidence_interval_lower=confidence_intervals['lower'],
                confidence_interval_upper=confidence_intervals['upper'],
                model_accuracy=forecast_results['accuracy'],
                accuracy_rating=self._get_accuracy_rating(forecast_results['accuracy']),
                mae_score=forecast_results.get('mae'),
                rmse_score=forecast_results.get('rmse'),
                r2_score=forecast_results.get('r2'),
                key_features=forecast_results['feature_importance'],
                seasonal_factors=seasonal_analysis,
                trend_analysis=trend_analysis,
                period_breakdown=forecast_results['period_forecasts'],
                platform_breakdown=await self._generate_platform_breakdown(forecast_results, user_id),
                model_parameters=forecast_results['model_params'],
                forecast_valid_until=datetime.utcnow() + timedelta(days=30)
            )
            
            # Sauvegarde
            self.db_session.add(forecast)
            await self.db_session.commit()
            
            # Émission d'événement
            await self.event_emitter.emit("forecast_generated", {
                "forecast_id": forecast.forecast_id,
                "user_id": str(user_id),
                "forecasted_revenue": float(forecast.forecasted_revenue),
                "accuracy": float(forecast.model_accuracy)
            })
            
            logger.info(f"Revenue forecast generated: {forecast.forecast_id}")
            return forecast
            
        except Exception as e:
            logger.error(f"Revenue forecasting failed: {e}")
            raise
    
    async def _prepare_training_data(
        self,
        user_id: uuid.UUID,
        content_id: Optional[uuid.UUID] = None
    ) -> pd.DataFrame:
        """
        Prépare les données d'entraînement
        """
        # Récupération des données historiques
        query_filters = {'user_id': user_id}
        if content_id:
            query_filters['content_id'] = content_id
        
        revenue_data = await self._get_historical_revenue_data(query_filters)
        
        # Conversion en DataFrame
        df = pd.DataFrame(revenue_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Agrégation par période
        df_daily = df.groupby(df['date'].dt.date).agg({
            'amount_net': 'sum',
            'platform_name': lambda x: list(x.unique()),
            'content_type': lambda x: list(x.unique()) if 'content_type' in df.columns else []
        }).reset_index()
        
        # Ajout de caractéristiques temporelles
        df_daily['day_of_week'] = pd.to_datetime(df_daily['date']).dt.dayofweek
        df_daily['month'] = pd.to_datetime(df_daily['date']).dt.month
        df_daily['quarter'] = pd.to_datetime(df_daily['date']).dt.quarter
        df_daily['is_weekend'] = df_daily['day_of_week'].isin([5, 6])
        
        return df_daily
    
    async def _engineer_features(
        self,
        data: pd.DataFrame,
        forecast_horizon: ForecastHorizon
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Ingénierie des caractéristiques pour le ML
        """
        # Caractéristiques de base
        features = []
        targets = []
        
        # Fenêtre glissante basée sur l'horizon
        window_sizes = {
            ForecastHorizon.DAILY: 7,
            ForecastHorizon.WEEKLY: 4,
            ForecastHorizon.MONTHLY: 3,
            ForecastHorizon.QUARTERLY: 4,
            ForecastHorizon.YEARLY: 3
        }
        
        window_size = window_sizes.get(forecast_horizon, 7)
        
        for i in range(window_size, len(data)):
            # Caractéristiques historiques (fenêtre glissante)
            historical_revenues = data['amount_net'].iloc[i-window_size:i].values
            
            # Statistiques de la fenêtre
            feature_vector = [
                historical_revenues.mean(),
                historical_revenues.std(),
                historical_revenues.min(),
                historical_revenues.max(),
                np.percentile(historical_revenues, 25),
                np.percentile(historical_revenues, 75),
                len(set(data['platform_name'].iloc[i-window_size:i].sum())),  # Diversité des plateformes
            ]
            
            # Caractéristiques temporelles
            current_row = data.iloc[i]
            feature_vector.extend([
                current_row['day_of_week'],
                current_row['month'],
                current_row['quarter'],
                int(current_row['is_weekend'])
            ])
            
            # Tendances (pentes)
            if len(historical_revenues) > 1:
                trend = np.polyfit(range(len(historical_revenues)), historical_revenues, 1)[0]
                feature_vector.append(trend)
            else:
                feature_vector.append(0)
            
            # Volatilité
            if len(historical_revenues) > 1:
                volatility = historical_revenues.std() / historical_revenues.mean() if historical_revenues.mean() > 0 else 0
                feature_vector.append(volatility)
            else:
                feature_vector.append(0)
            
            features.append(feature_vector)
            targets.append(current_row['amount_net'])
        
        return np.array(features), np.array(targets)
    
    async def _generate_ensemble_forecast(
        self,
        features: np.ndarray,
        targets: np.ndarray,
        forecast_periods: int
    ) -> Dict[str, Any]:
        """
        Génère une prévision d'ensemble (combinaison de modèles)
        """
        # Division des données
        split_point = int(len(features) * 0.8)
        X_train, X_test = features[:split_point], features[split_point:]
        y_train, y_test = targets[:split_point], targets[split_point:]
        
        # Normalisation
        scaler = self.scalers['standard']
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Entraînement de plusieurs modèles
        model_predictions = {}
        model_weights = {}
        
        for model_name, model in self.models.items():
            try:
                # Entraînement
                model.fit(X_train_scaled, y_train)
                
                # Prédiction sur test
                y_pred = model.predict(X_test_scaled)
                
                # Calcul de la performance
                mae = mean_absolute_error(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                r2 = r2_score(y_test, y_pred)
                
                # Poids basé sur la performance (inverse de l'erreur)
                weight = 1 / (1 + mae) if mae > 0 else 1
                
                model_predictions[model_name] = {
                    'predictions': y_pred,
                    'mae': mae,
                    'rmse': rmse,
                    'r2': r2,
                    'weight': weight
                }
                model_weights[model_name] = weight
                
            except Exception as e:
                logger.warning(f"Model {model_name} failed: {e}")
                continue
        
        # Normalisation des poids
        total_weight = sum(model_weights.values())
        normalized_weights = {k: v/total_weight for k, v in model_weights.items()}
        
        # Prédiction d'ensemble pour les périodes futures
        last_features = features[-1:].copy()
        period_forecasts = []
        
        for period in range(forecast_periods):
            period_predictions = []
            
            for model_name, model in self.models.items():
                if model_name in model_predictions:
                    scaled_features = scaler.transform(last_features)
                    pred = model.predict(scaled_features)[0]
                    weighted_pred = pred * normalized_weights[model_name]
                    period_predictions.append(weighted_pred)
            
            # Prédiction d'ensemble
            ensemble_prediction = sum(period_predictions)
            period_forecasts.append(float(ensemble_prediction))
            
            # Mise à jour des caractéristiques pour la prochaine période
            # (simulation simple - dans un système réel, ceci serait plus sophistiqué)
            last_features[0] = np.roll(last_features[0], -1)
            last_features[0][-1] = ensemble_prediction
        
        # Calcul des métriques globales
        ensemble_predictions = []
        for i in range(len(y_test)):
            pred_sum = sum([
                model_predictions[name]['predictions'][i] * normalized_weights[name]
                for name in model_predictions
            ])
            ensemble_predictions.append(pred_sum)
        
        ensemble_mae = mean_absolute_error(y_test, ensemble_predictions)
        ensemble_rmse = np.sqrt(mean_squared_error(y_test, ensemble_predictions))
        ensemble_r2 = r2_score(y_test, ensemble_predictions)
        
        # Calcul de la précision (1 - erreur relative moyenne)
        mape = np.mean(np.abs((y_test - ensemble_predictions) / y_test)) * 100
        accuracy = max(0, (100 - mape) / 100)
        
        return {
            'total_forecast': Decimal(str(sum(period_forecasts))),
            'period_forecasts': [{'period': i+1, 'forecast': f} for i, f in enumerate(period_forecasts)],
            'accuracy': Decimal(str(accuracy)),
            'mae': Decimal(str(ensemble_mae)),
            'rmse': Decimal(str(ensemble_rmse)),
            'r2': Decimal(str(ensemble_r2)),
            'feature_importance': self._get_ensemble_feature_importance(model_predictions),
            'model_params': {
                'model_weights': normalized_weights,
                'individual_performances': {
                    name: {
                        'mae': float(data['mae']),
                        'rmse': float(data['rmse']),
                        'r2': float(data['r2'])
                    }
                    for name, data in model_predictions.items()
                }
            }
        }
    
    async def _analyze_trends(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyse les tendances dans les données historiques
        """
        revenue_series = data['amount_net'].values
        
        # Décomposition de série temporelle
        if len(revenue_series) >= 14:  # Minimum pour décomposition
            try:
                decomposition = seasonal_decompose(
                    revenue_series, 
                    model='additive', 
                    period=7  # Cycle hebdomadaire
                )
                
                trend_component = decomposition.trend
                seasonal_component = decomposition.seasonal
                residual_component = decomposition.resid
                
                # Calcul de la force de tendance
                trend_strength = 1 - (np.nanvar(residual_component) / np.nanvar(trend_component + residual_component))
                
                # Direction de la tendance
                valid_trend = trend_component[~np.isnan(trend_component)]
                if len(valid_trend) > 1:
                    trend_slope = np.polyfit(range(len(valid_trend)), valid_trend, 1)[0]
                    if trend_slope > 0:
                        trend_direction = "rising"
                    elif trend_slope < 0:
                        trend_direction = "falling"
                    else:
                        trend_direction = "stable"
                else:
                    trend_direction = "stable"
                    trend_slope = 0
                
                return {
                    'trend_direction': trend_direction,
                    'trend_slope': float(trend_slope),
                    'trend_strength': float(trend_strength),
                    'has_seasonality': True,
                    'seasonal_strength': float(1 - (np.nanvar(residual_component) / np.nanvar(seasonal_component + residual_component))),
                    'volatility': float(np.std(revenue_series) / np.mean(revenue_series)) if np.mean(revenue_series) > 0 else 0
                }
                
            except Exception as e:
                logger.warning(f"Seasonal decomposition failed: {e}")
        
        # Analyse simple si décomposition impossible
        if len(revenue_series) > 1:
            trend_slope = np.polyfit(range(len(revenue_series)), revenue_series, 1)[0]
            trend_direction = "rising" if trend_slope > 0 else "falling" if trend_slope < 0 else "stable"
        else:
            trend_slope = 0
            trend_direction = "stable"
        
        return {
            'trend_direction': trend_direction,
            'trend_slope': float(trend_slope),
            'trend_strength': 0.5,  # Valeur par défaut
            'has_seasonality': False,
            'seasonal_strength': 0.0,
            'volatility': float(np.std(revenue_series) / np.mean(revenue_series)) if np.mean(revenue_series) > 0 else 0
        }
    
    async def _analyze_seasonality(
        self,
        data: pd.DataFrame,
        forecast_horizon: ForecastHorizon
    ) -> Dict[str, Any]:
        """
        Analyse la saisonnalité dans les données
        """
        data_copy = data.copy()
        data_copy['date'] = pd.to_datetime(data_copy['date'])
        
        seasonal_analysis = {
            'patterns_detected': [],
            'seasonal_indices': {},
            'peak_periods': [],
            'low_periods': []
        }
        
        # Analyse par jour de la semaine
        if forecast_horizon in [ForecastHorizon.DAILY, ForecastHorizon.WEEKLY]:
            daily_avg = data_copy.groupby('day_of_week')['amount_net'].mean()
            overall_avg = data_copy['amount_net'].mean()
            
            daily_indices = (daily_avg / overall_avg).to_dict()
            seasonal_analysis['seasonal_indices']['day_of_week'] = {
                int(k): float(v) for k, v in daily_indices.items()
            }
            
            # Identification des pics et creux
            max_day = daily_avg.idxmax()
            min_day = daily_avg.idxmin()
            
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            seasonal_analysis['peak_periods'].append(f"{day_names[max_day]} (weekday)")
            seasonal_analysis['low_periods'].append(f"{day_names[min_day]} (weekday)")
        
        # Analyse par mois
        if forecast_horizon in [ForecastHorizon.MONTHLY, ForecastHorizon.QUARTERLY, ForecastHorizon.YEARLY]:
            monthly_avg = data_copy.groupby('month')['amount_net'].mean()
            overall_avg = data_copy['amount_net'].mean()
            
            monthly_indices = (monthly_avg / overall_avg).to_dict()
            seasonal_analysis['seasonal_indices']['month'] = {
                int(k): float(v) for k, v in monthly_indices.items()
            }
            
            # Identification des mois pics et creux
            max_month = monthly_avg.idxmax()
            min_month = monthly_avg.idxmin()
            
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            seasonal_analysis['peak_periods'].append(f"{month_names[max_month-1]} (month)")
            seasonal_analysis['low_periods'].append(f"{month_names[min_month-1]} (month)")
        
        # Détection de patterns
        seasonal_analysis['patterns_detected'] = self._detect_seasonal_patterns(data_copy)
        
        return seasonal_analysis
    
    def _get_accuracy_rating(self, accuracy_score: float) -> str:
        """
        Convertit le score de précision en rating
        """
        if accuracy_score >= 0.95:
            return ForecastAccuracy.EXCELLENT.value
        elif accuracy_score >= 0.90:
            return ForecastAccuracy.VERY_GOOD.value
        elif accuracy_score >= 0.80:
            return ForecastAccuracy.GOOD.value
        elif accuracy_score >= 0.70:
            return ForecastAccuracy.FAIR.value
        else:
            return ForecastAccuracy.POOR.value


class ForecastAccuracyTracker:
    """
    Suivi de la précision des prévisions
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.event_emitter = EventEmitter()
    
    async def validate_forecast_accuracy(
        self,
        forecast_id: uuid.UUID,
        actual_revenue: Decimal,
        validation_date: datetime
    ) -> ForecastAccuracyTrackingModel:
        """
        Valide la précision d'une prévision contre les résultats réels
        """
        # Récupération de la prévision
        forecast = await self._get_forecast(forecast_id)
        
        if not forecast:
            raise ValueError(f"Forecast {forecast_id} not found")
        
        # Calcul des erreurs
        predicted_revenue = forecast.forecasted_revenue
        absolute_error = abs(actual_revenue - predicted_revenue)
        percentage_error = (absolute_error / actual_revenue * 100) if actual_revenue > 0 else 100
        squared_error = (actual_revenue - predicted_revenue) ** 2
        
        # Analyse de l'erreur
        error_analysis = await self._analyze_prediction_error(
            forecast, actual_revenue, predicted_revenue
        )
        
        # Création du tracking
        tracking = ForecastAccuracyTrackingModel(
            tracking_id=f"TRACK_{datetime.utcnow().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}",
            forecast_id=forecast_id,
            validation_date=validation_date,
            actual_revenue=actual_revenue,
            predicted_revenue=predicted_revenue,
            absolute_error=absolute_error,
            percentage_error=percentage_error,
            squared_error=squared_error,
            error_analysis=error_analysis,
            model_adjustment_needed=percentage_error > 20  # Seuil de 20%
        )
        
        # Sauvegarde
        self.db_session.add(tracking)
        await self.db_session.commit()
        
        # Notification si grosse erreur
        if percentage_error > 25:
            await self.event_emitter.emit("forecast_accuracy_alert", {
                "forecast_id": str(forecast_id),
                "percentage_error": float(percentage_error),
                "adjustment_needed": True
            })
        
        return tracking


class MarketTrendAnalyzer:
    """
    Analyseur de tendances de marché
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    async def analyze_market_trends(
        self,
        market_segment: str,
        analysis_period_days: int = 90
    ) -> MarketTrendAnalysisModel:
        """
        Analyse les tendances du marché pour un segment donné
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=analysis_period_days)
        
        # Récupération des données de marché
        market_data = await self._get_market_data(market_segment, start_date, end_date)
        
        # Analyse des tendances
        trend_analysis = await self._perform_trend_analysis(market_data)
        
        # Analyse de la volatilité
        volatility_analysis = await self._analyze_volatility(market_data)
        
        # Prédictions de marché
        market_forecast = await self._generate_market_forecast(market_data)
        
        # Analyse concurrentielle
        competitive_analysis = await self._analyze_competition(market_segment)
        
        analysis = MarketTrendAnalysisModel(
            analysis_id=f"MARKET_{datetime.utcnow().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}",
            analysis_period_start=start_date,
            analysis_period_end=end_date,
            market_segment=market_segment,
            overall_trend=trend_analysis['direction'],
            trend_strength=Decimal(str(trend_analysis['strength'])),
            volatility_index=Decimal(str(volatility_analysis['index'])),
            seasonal_patterns=trend_analysis.get('seasonality'),
            market_share_trends=competitive_analysis.get('market_share'),
            market_forecast=market_forecast,
            strategic_recommendations=await self._generate_strategic_recommendations(
                trend_analysis, volatility_analysis, competitive_analysis
            )
        )
        
        # Sauvegarde
        self.db_session.add(analysis)
        await self.db_session.commit()
        
        return analysis


class RevenueForecastManager:
    """
    Gestionnaire principal des prévisions de revenus
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.cache_manager = CacheManager()
        self.forecasting_engine = RevenueForecastingEngine(
            db_manager.get_session(), 
            self.cache_manager
        )
        self.accuracy_tracker = ForecastAccuracyTracker(db_manager.get_session())
        self.market_analyzer = MarketTrendAnalyzer(db_manager.get_session())
    
    async def create_comprehensive_forecast(
        self,
        user_id: uuid.UUID,
        forecast_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Crée une prévision complète avec analyse de marché
        """
        # Prévision des revenus
        revenue_forecast = await self.forecasting_engine.generate_revenue_forecast(
            user_id=user_id,
            forecast_horizon=ForecastHorizon(forecast_config.get('horizon', 'monthly')),
            forecast_periods=forecast_config.get('periods', 12),
            model_type=ForecastModel(forecast_config.get('model', 'ensemble')),
            content_id=forecast_config.get('content_id')
        )
        
        # Analyse des tendances de marché
        market_segment = forecast_config.get('market_segment', 'music_streaming')
        market_analysis = await self.market_analyzer.analyze_market_trends(market_segment)
        
        # Combinaison des résultats
        comprehensive_forecast = {
            'revenue_forecast': {
                'forecast_id': revenue_forecast.forecast_id,
                'total_forecasted': float(revenue_forecast.forecasted_revenue),
                'confidence_interval': {
                    'lower': float(revenue_forecast.confidence_interval_lower),
                    'upper': float(revenue_forecast.confidence_interval_upper)
                },
                'accuracy_rating': revenue_forecast.accuracy_rating,
                'period_breakdown': revenue_forecast.period_breakdown,
                'key_factors': revenue_forecast.key_features
            },
            'market_analysis': {
                'analysis_id': market_analysis.analysis_id,
                'market_trend': market_analysis.overall_trend,
                'volatility': float(market_analysis.volatility_index),
                'market_forecast': market_analysis.market_forecast,
                'recommendations': market_analysis.strategic_recommendations
            },
            'combined_insights': await self._generate_combined_insights(
                revenue_forecast, market_analysis
            )
        }
        
        return comprehensive_forecast
    
    async def setup_automated_forecasting(
        self,
        user_id: uuid.UUID,
        forecasting_schedule: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Configure la prévision automatisée pour un utilisateur
        """
        # Configuration de tâches périodiques
        schedule_config = {
            'user_id': str(user_id),
            'frequency': forecasting_schedule.get('frequency', 'weekly'),
            'forecast_horizon': forecasting_schedule.get('horizon', 'monthly'),
            'model_preferences': forecasting_schedule.get('models', ['ensemble']),
            'accuracy_threshold': forecasting_schedule.get('accuracy_threshold', 0.8),
            'auto_adjust_models': forecasting_schedule.get('auto_adjust', True)
        }
        
        # Création de la tâche automatique
        task_id = await self._create_automated_task(schedule_config)
        
        return {
            'task_id': task_id,
            'schedule_config': schedule_config,
            'next_execution': await self._calculate_next_execution(schedule_config['frequency'])
        }
    
    async def validate_and_improve_forecasts(
        self,
        user_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Valide et améliore les prévisions existantes
        """
        # Récupération des prévisions à valider
        forecasts_to_validate = await self._get_forecasts_for_validation(user_id)
        
        validation_results = []
        
        for forecast in forecasts_to_validate:
            # Récupération des revenus réels
            actual_revenue = await self._get_actual_revenue_for_period(
                user_id, forecast.forecast_created_date
            )
            
            if actual_revenue is not None:
                # Validation de la précision
                accuracy_tracking = await self.accuracy_tracker.validate_forecast_accuracy(
                    forecast.id, actual_revenue, datetime.utcnow()
                )
                
                validation_results.append({
                    'forecast_id': forecast.forecast_id,
                    'predicted': float(forecast.forecasted_revenue),
                    'actual': float(actual_revenue),
                    'accuracy': float(100 - accuracy_tracking.percentage_error),
                    'adjustment_needed': accuracy_tracking.model_adjustment_needed
                })
        
        # Amélioration des modèles si nécessaire
        improvement_actions = await self._improve_models_based_on_validation(validation_results)
        
        return {
            'validation_results': validation_results,
            'overall_accuracy': np.mean([r['accuracy'] for r in validation_results]) if validation_results else 0,
            'improvement_actions': improvement_actions
        }
