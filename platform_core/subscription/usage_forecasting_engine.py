# WARNING: Potential SQL injection risk - use parameterized queries
"""🚀 Platform Core Subscription - Usage Forecasting Engine
===========================================================
Module: backend/platform_core/subscription/usage_forecasting_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
===========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🚨 AVERTISSEMENT LÉGAL OBLIGATOIRE:
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

🎯 MOTEUR DE PRÉDICTION D'USAGE ML
Prédiction avancée de consommation avec deep learning
- Modèles ML temporels pour prédiction usage
- Détection patterns saisonniers et cycliques
- Alertes préventives de dépassement quotas
- Optimisation capacité et scaling automatique
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
import logging
import asyncio
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
from decimal import Decimal

# Configure logging
logger = logging.getLogger(__name__)

try:
    # Import TensorFlow via gestionnaire centralisé
    from core.tensorflow_singleton import get_tensorflow
    tf_manager = get_tensorflow()
    tf = tf_manager.get_tf() if tf_manager.is_available else None
    if tf_manager.is_available:
        Sequential = tf.keras.models.Sequential
        LSTM = tf.keras.layers.LSTM
        Dense = tf.keras.layers.Dense
        Dropout = tf.keras.layers.Dropout
        TENSORFLOW_AVAILABLE = True
    else:
        Sequential = None
        LSTM = Dense = Dropout = None
        TENSORFLOW_AVAILABLE = False
except ImportError:
    tf = None
    Sequential = None
    LSTM = Dense = Dropout = None
    TENSORFLOW_AVAILABLE = False
    logger.warning("TensorFlow not available, LSTM models will be disabled")


class ForecastHorizon(Enum):
    """Horizons de prédiction"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class UsageMetricType(Enum):
    """Types de métriques d'usage"""
    STORAGE = "storage"
    BANDWIDTH = "bandwidth"
    API_CALLS = "api_calls"
    CONTENT_UPLOADS = "content_uploads"
    COLLABORATION_SESSIONS = "collaboration_sessions"
    PROCESSING_HOURS = "processing_hours"


class ForecastAccuracy(Enum):
    """Niveaux de précision de prédiction"""
    EXCELLENT = "excellent"  # >95%
    GOOD = "good"  # 85-95%
    MODERATE = "moderate"  # 70-85%
    POOR = "poor"  # <70%


@dataclass
class UsageDataPoint:
    """Point de données d'usage"""
    timestamp: datetime
    creator_id: str
    metric_type: UsageMetricType
    value: float
    context: Dict[str, Any]
    seasonal_factors: Dict[str, Any]


@dataclass
class UsageForecast:
    """Prédiction d'usage"""
    creator_id: str
    metric_type: UsageMetricType
    forecast_horizon: ForecastHorizon
    predicted_values: List[float]
    confidence_intervals: List[Tuple[float, float]]
    accuracy_score: float
    accuracy_level: ForecastAccuracy
    trend_analysis: Dict[str, Any]
    seasonal_patterns: Dict[str, Any]
    anomaly_alerts: List[str]
    scaling_recommendations: List[str]


@dataclass
class ForecastingModel:
    """Modèle de prédiction"""
    model_id: str
    model_type: str
    metric_type: UsageMetricType
    training_data_size: int
    accuracy_metrics: Dict[str, float]
    last_training: datetime
    feature_importance: Dict[str, float]


class UsageForecastingEngine:
    """🚀 Moteur de Prédiction d'Usage ML Enterprise
    
    Système ML avancé pour prédiction de consommation avec
    deep learning et analyse temporelle sophistiquée.
    """
    
    def __init__(self):
        """Initialise le moteur de prédiction"""
        self.ml_models = {}
        self.lstm_models = {}
        self.scalers = {}
        self.forecast_cache = {}
        self.historical_data = {}
        
        # Configuration des modèles
        self.model_configs = {
            'random_forest': {
                'n_estimators': 100,
                'max_depth': 20,
                'random_state': 42
            },
            'gradient_boosting': {
                'n_estimators': 100,
                'learning_rate': 0.1,
                'max_depth': 10,
                'random_state': 42
            },
            'lstm': {
                'sequence_length': 30,
                'units': 50,
                'dropout': 0.2,
                'epochs': 100,
                'batch_size': 32
            }
        }
        
        # Facteurs saisonniers
        self.seasonal_factors = {
            'monthly': [1.0, 0.9, 1.1, 1.2, 1.3, 1.4, 1.5, 1.4, 1.3, 1.2, 1.0, 0.8],
            'weekly': [0.8, 1.0, 1.1, 1.2, 1.3, 1.4, 1.2],  # Lun-Dim
            'daily': [0.3, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.5, 1.3, 1.1, 0.9, 0.7,
                     0.8, 1.0, 1.2, 1.3, 1.4, 1.5, 1.4, 1.2, 1.0, 0.8, 0.6, 0.4]
        }
        
        logger.info("🚀 Usage Forecasting Engine initialized")
    
    async def generate_usage_forecast(
        self,
        creator_id: str,
        metric_type: UsageMetricType,
        forecast_horizon: ForecastHorizon,
        periods: int = 30
    ) -> UsageForecast:
        """Génère une prédiction d'usage avancée"""
        try:
            # Récupération des données historiques
            historical_data = await self._get_historical_data(creator_id, metric_type)
            
            if len(historical_data) < 30:  # Minimum de données requis
                return await self._generate_baseline_forecast(creator_id, metric_type, forecast_horizon, periods)
            
            # Préparation des données
            features, targets = await self._prepare_forecasting_data(historical_data)
            
            # Sélection du modèle optimal
            best_model = await self._select_best_model(features, targets, metric_type)
            
            # Génération de la prédiction
            predictions = await self._generate_predictions(best_model, features, periods)
            
            # Calcul des intervalles de confiance
            confidence_intervals = await self._calculate_confidence_intervals(
                predictions, historical_data, metric_type
            )
            
            # Analyse de tendance
            trend_analysis = await self._analyze_trend(historical_data, predictions)
            
            # Détection de patterns saisonniers
            seasonal_patterns = await self._detect_seasonal_patterns(historical_data)
            
            # Détection d'anomalies
            anomaly_alerts = await self._detect_usage_anomalies(predictions, historical_data)
            
            # Recommandations de scaling
            scaling_recommendations = await self._generate_scaling_recommendations(
                predictions, creator_id, metric_type
            )
            
            # Évaluation de la précision
            accuracy_score = await self._evaluate_forecast_accuracy(best_model, features, targets)
            accuracy_level = self._get_accuracy_level(accuracy_score)
            
            forecast = UsageForecast(
                creator_id=creator_id,
                metric_type=metric_type,
                forecast_horizon=forecast_horizon,
                predicted_values=predictions.tolist(),
                confidence_intervals=confidence_intervals,
                accuracy_score=accuracy_score,
                accuracy_level=accuracy_level,
                trend_analysis=trend_analysis,
                seasonal_patterns=seasonal_patterns,
                anomaly_alerts=anomaly_alerts,
                scaling_recommendations=scaling_recommendations
            )
            
            # Cache de la prédiction
            cache_key = f"{creator_id}_{metric_type.value}_{forecast_horizon.value}"
            self.forecast_cache[cache_key] = forecast
            
            logger.info(f"✅ Usage forecast generated for creator {creator_id}, metric {metric_type.value}")
            return forecast
            
        except Exception as e:
            logger.error(f"❌ Error generating usage forecast: {e}")
            return await self._generate_baseline_forecast(creator_id, metric_type, forecast_horizon, periods)
    
    async def _get_historical_data(self, creator_id: str, metric_type: UsageMetricType) -> pd.DataFrame:
        """Récupère les données historiques d'usage"""
        try:
            # Simulation de données historiques (à remplacer par requête DB réelle)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            
            # Génération de données synthétiques réalistes
            base_value = self._get_base_value_for_metric(metric_type)
            trend = np.linspace(0.8, 1.2, len(dates))
            
            # Ajout de saisonnalité
            seasonal = np.sin(2 * np.pi * np.arange(len(dates)) / 7) * 0.2 + 1  # Saisonnalité hebdomadaire
            
            # Ajout de bruit
            noise = np.random.normal(0, 0.1, len(dates))
            
            values = base_value * trend * seasonal * (1 + noise)
            values = np.maximum(values, 0)  # Pas de valeurs négatives
            
            data = pd.DataFrame({
                'timestamp': dates,
                'creator_id': creator_id,
                'metric_type': metric_type.value,
                'value': values
            })
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Error getting historical data: {e}")
            return pd.DataFrame()
    
    def _get_base_value_for_metric(self, metric_type: UsageMetricType) -> float:
        """Retourne la valeur de base pour un type de métrique"""
        base_values = {
            UsageMetricType.STORAGE: 100.0,  # GB
            UsageMetricType.BANDWIDTH: 50.0,  # GB
            UsageMetricType.API_CALLS: 1000.0,  # Calls
            UsageMetricType.CONTENT_UPLOADS: 10.0,  # Files
            UsageMetricType.COLLABORATION_SESSIONS: 5.0,  # Sessions
            UsageMetricType.PROCESSING_HOURS: 2.0  # Hours
        }
        return base_values.get(metric_type, 10.0)
    
    async def _prepare_forecasting_data(self, historical_data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prépare les données pour la prédiction"""
        try:
            # Tri par timestamp
            data = historical_data.sort_values('timestamp').copy()
            
            # Extraction des features temporelles
            data['day_of_week'] = data['timestamp'].dt.dayofweek
            data['day_of_month'] = data['timestamp'].dt.day
            data['month'] = data['timestamp'].dt.month
            data['quarter'] = data['timestamp'].dt.quarter
            
            # Features de lag
            for lag in [1, 7, 14, 30]:
                data[f'value_lag_{lag}'] = data['value'].shift(lag)
            
            # Features de rolling statistics
            for window in [7, 14, 30]:
                data[f'rolling_mean_{window}'] = data['value'].rolling(window=window).mean()
                data[f'rolling_std_{window}'] = data['value'].rolling(window=window).std()
            
            # Suppression des NaN
            data = data.dropna()
            
            # Séparation features/targets
            feature_cols = [col for col in data.columns if col not in ['timestamp', 'creator_id', 'metric_type', 'value']]
            features = data[feature_cols].values
            targets = data['value'].values
            
            return features, targets
            
        except Exception as e:
            logger.error(f"❌ Error preparing forecasting data: {e}")
            return np.array([]), np.array([])
    
    async def _select_best_model(
        self,
        features: np.ndarray,
        targets: np.ndarray,
        metric_type: UsageMetricType
    ) -> Dict[str, Any]:
        """Sélectionne le meilleur modèle pour la prédiction"""
        try:
            if len(features) == 0 or len(targets) == 0:
                return {'type': 'baseline', 'model': None}
            
            # Division des données
            split_point = int(len(features) * 0.8)
            X_train, X_test = features[:split_point], features[split_point:]
            y_train, y_test = targets[:split_point], targets[split_point:]
            
            if len(X_train) == 0 or len(X_test) == 0:
                return {'type': 'baseline', 'model': None}
            
            # Normalisation
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            models = {}
            scores = {}
            
            # Random Forest
            try:
                rf_model = RandomForestRegressor(**self.model_configs['random_forest'])
                rf_model.fit(X_train_scaled, y_train)
                rf_pred = rf_model.predict(X_test_scaled)
                scores['random_forest'] = r2_score(y_test, rf_pred)
                models['random_forest'] = {'model': rf_model, 'scaler': scaler}
            except Exception as e:
                logger.warning(f"Random Forest failed: {e}")
                scores['random_forest'] = -np.inf
            
            # Gradient Boosting
            try:
                gb_model = GradientBoostingRegressor(**self.model_configs['gradient_boosting'])
                gb_model.fit(X_train_scaled, y_train)
                gb_pred = gb_model.predict(X_test_scaled)
                scores['gradient_boosting'] = r2_score(y_test, gb_pred)
                models['gradient_boosting'] = {'model': gb_model, 'scaler': scaler}
            except Exception as e:
                logger.warning(f"Gradient Boosting failed: {e}")
                scores['gradient_boosting'] = -np.inf
            
            # LSTM (si suffisamment de données et TensorFlow disponible)
            if len(X_train) >= 100 and TENSORFLOW_AVAILABLE:
                try:
                    lstm_model = await self._build_lstm_model(X_train.shape[1])
                    lstm_score = await self._train_lstm_model(lstm_model, X_train_scaled, y_train, X_test_scaled, y_test)
                    scores['lstm'] = lstm_score
                    models['lstm'] = {'model': lstm_model, 'scaler': scaler}
                except Exception as e:
                    logger.warning(f"LSTM failed: {e}")
                    scores['lstm'] = -np.inf
            
            # Sélection du meilleur modèle
            if not scores or all(score == -np.inf for score in scores.values()):
                return {'type': 'baseline', 'model': None}
            
            best_model_type = max(scores, key=scores.get)
            best_model = models[best_model_type]
            best_model['type'] = best_model_type
            best_model['score'] = scores[best_model_type]
            
            # Sauvegarde pour réutilisation
            model_key = f"{metric_type.value}_{best_model_type}"
            self.ml_models[model_key] = best_model
            
            logger.info(f"✅ Best model selected: {best_model_type} (R² = {scores[best_model_type]:.3f})")
            return best_model
            
        except Exception as e:
            logger.error(f"❌ Error selecting best model: {e}")
            return {'type': 'baseline', 'model': None}
    
    async def _build_lstm_model(self, input_dim: int) -> Sequential:
        """Construit un modèle LSTM"""
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow is required for LSTM models")
            
        model = Sequential([
            LSTM(self.model_configs['lstm']['units'], return_sequences=True, input_shape=(1, input_dim)),
            Dropout(self.model_configs['lstm']['dropout']),
            LSTM(self.model_configs['lstm']['units'], return_sequences=False),
            Dropout(self.model_configs['lstm']['dropout']),
            Dense(25),
            Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return model
    
    async def _train_lstm_model(
        self,
        model: Sequential,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> float:
        """Entraîne le modèle LSTM"""
        try:
            # Reshape pour LSTM
            X_train_lstm = X_train.reshape((X_train.shape[0], 1, X_train.shape[1]))
            X_test_lstm = X_test.reshape((X_test.shape[0], 1, X_test.shape[1]))
            
            # Entraînement
            model.fit(
                X_train_lstm, y_train,
                epochs=self.model_configs['lstm']['epochs'],
                batch_size=self.model_configs['lstm']['batch_size'],
                validation_split=0.2,
                verbose=0
            )
            
            # Évaluation
            predictions = model.predict(X_test_lstm)
            score = r2_score(y_test, predictions.flatten())
            
            return score
            
        except Exception as e:
            logger.error(f"❌ Error training LSTM: {e}")
            return -np.inf
    
    async def _generate_predictions(
        self,
        model: Dict[str, Any],
        features: np.ndarray,
        periods: int
    ) -> np.ndarray:
        """Génère les prédictions"""
        try:
            if model['type'] == 'baseline' or model['model'] is None:
                # Prédiction baseline basée sur la moyenne des derniers points
                if len(features) > 0:
                    last_values = features[-7:, -1] if features.shape[1] > 0 else [10.0]
                    mean_value = np.mean(last_values) if len(last_values) > 0 else 10.0
                    return np.full(periods, mean_value)
                else:
                    return np.full(periods, 10.0)
            
            predictions = []
            current_features = features[-1:].copy()  # Dernières features
            
            for _ in range(periods):
                if model['type'] == 'lstm':
                    # Prédiction LSTM
                    features_scaled = model['scaler'].transform(current_features)
                    features_lstm = features_scaled.reshape((1, 1, features_scaled.shape[1]))
                    pred = model['model'].predict(features_lstm, verbose=0)[0, 0]
                else:
                    # Prédiction ML classique
                    features_scaled = model['scaler'].transform(current_features)
                    pred = model['model'].predict(features_scaled)[0]
                
                predictions.append(max(pred, 0))  # Pas de valeurs négatives
                
                # Mise à jour des features pour la prochaine prédiction
                if len(current_features[0]) > 1:
                    # Décalage des features de lag
                    current_features[0, 1:] = current_features[0, :-1]
                    current_features[0, 0] = pred
            
            return np.array(predictions)
            
        except Exception as e:
            logger.error(f"❌ Error generating predictions: {e}")
            return np.full(periods, 10.0)  # Valeur par défaut
    
    async def _calculate_confidence_intervals(
        self,
        predictions: np.ndarray,
        historical_data: pd.DataFrame,
        metric_type: UsageMetricType
    ) -> List[Tuple[float, float]]:
        """Calcule les intervalles de confiance"""
        try:
            # Calcul de l'erreur standard basée sur les données historiques
            historical_values = historical_data['value'].values
            std_error = np.std(historical_values) * 1.96  # Intervalle 95%
            
            intervals = []
            for pred in predictions:
                lower_bound = max(pred - std_error, 0)  # Pas de valeurs négatives
                upper_bound = pred + std_error
                intervals.append((lower_bound, upper_bound))
            
            return intervals
            
        except Exception as e:
            logger.error(f"❌ Error calculating confidence intervals: {e}")
            return [(pred * 0.8, pred * 1.2) for pred in predictions]
    
    async def _analyze_trend(
        self,
        historical_data: pd.DataFrame,
        predictions: np.ndarray
    ) -> Dict[str, Any]:
        """Analyse la tendance des données"""
        try:
            historical_values = historical_data['value'].values
            
            # Tendance historique
            if len(historical_values) >= 30:
                recent_avg = np.mean(historical_values[-30:])
                older_avg = np.mean(historical_values[-60:-30]) if len(historical_values) >= 60 else recent_avg
                historical_trend = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
            else:
                historical_trend = 0
            
            # Tendance prédite
            if len(predictions) >= 7:
                early_pred_avg = np.mean(predictions[:7])
                late_pred_avg = np.mean(predictions[-7:])
                predicted_trend = (late_pred_avg - early_pred_avg) / early_pred_avg if early_pred_avg > 0 else 0
            else:
                predicted_trend = 0
            
            # Classification de la tendance
            def classify_trend(trend_value):
                if trend_value > 0.1:
                    return "forte_croissance"
                elif trend_value > 0.05:
                    return "croissance_moderee"
                elif trend_value > -0.05:
                    return "stable"
                elif trend_value > -0.1:
                    return "declin_modere"
                else:
                    return "fort_declin"
            
            return {
                'historical_trend_percent': historical_trend * 100,
                'predicted_trend_percent': predicted_trend * 100,
                'historical_trend_class': classify_trend(historical_trend),
                'predicted_trend_class': classify_trend(predicted_trend),
                'trend_acceleration': predicted_trend - historical_trend
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing trend: {e}")
            return {'historical_trend_percent': 0, 'predicted_trend_percent': 0}
    
    async def _detect_seasonal_patterns(self, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Détecte les patterns saisonniers"""
        try:
            if len(historical_data) < 14:  # Minimum pour détecter des patterns
                return {'patterns_detected': False}
            
            data = historical_data.copy()
            data['day_of_week'] = data['timestamp'].dt.dayofweek
            data['hour'] = data['timestamp'].dt.hour
            
            # Pattern hebdomadaire
            weekly_pattern = data.groupby('day_of_week')['value'].mean().to_dict()
            weekly_variance = data.groupby('day_of_week')['value'].std().mean()
            
            # Pattern journalier (si données horaires disponibles)
            hourly_pattern = data.groupby('hour')['value'].mean().to_dict() if 'hour' in data.columns else {}
            
            # Détection de saisonnalité significative
            weekly_max = max(weekly_pattern.values()) if weekly_pattern else 0
            weekly_min = min(weekly_pattern.values()) if weekly_pattern else 0
            weekly_seasonality_strength = (weekly_max - weekly_min) / weekly_max if weekly_max > 0 else 0
            
            return {
                'patterns_detected': weekly_seasonality_strength > 0.2,
                'weekly_pattern': weekly_pattern,
                'hourly_pattern': hourly_pattern,
                'seasonality_strength': weekly_seasonality_strength,
                'peak_day': max(weekly_pattern, key=weekly_pattern.get) if weekly_pattern else 0,
                'low_day': min(weekly_pattern, key=weekly_pattern.get) if weekly_pattern else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error detecting seasonal patterns: {e}")
            return {'patterns_detected': False}
    
    async def _detect_usage_anomalies(
        self,
        predictions: np.ndarray,
        historical_data: pd.DataFrame
    ) -> List[str]:
        """Détecte les anomalies d'usage prédites"""
        alerts = []
        
        try:
            if len(historical_data) == 0:
                return alerts
            
            historical_mean = historical_data['value'].mean()
            historical_std = historical_data['value'].std()
            
            # Détection de spikes prédits
            for i, pred in enumerate(predictions):
                if pred > historical_mean + 3 * historical_std:
                    alerts.append(f"Pic d'usage prédit au jour {i+1}: {pred:.1f} (normal: {historical_mean:.1f})")
                elif pred < historical_mean - 2 * historical_std and historical_mean > 0:
                    alerts.append(f"Chute d'usage prédite au jour {i+1}: {pred:.1f} (normal: {historical_mean:.1f})")
            
            # Détection de tendances extrêmes
            if len(predictions) >= 7:
                trend_slope = (predictions[-1] - predictions[0]) / len(predictions)
                if abs(trend_slope) > historical_std:
                    direction = "hausse" if trend_slope > 0 else "baisse"
                    alerts.append(f"Tendance extrême détectée: {direction} de {abs(trend_slope):.1f} par jour")
            
            return alerts[:5]  # Maximum 5 alertes
            
        except Exception as e:
            logger.error(f"❌ Error detecting anomalies: {e}")
            return []
    
    async def _generate_scaling_recommendations(
        self,
        predictions: np.ndarray,
        creator_id: str,
        metric_type: UsageMetricType
    ) -> List[str]:
        """Génère des recommandations de scaling"""
        recommendations = []
        
        try:
            max_predicted = np.max(predictions)
            mean_predicted = np.mean(predictions)
            
            # Seuils par type de métrique
            thresholds = {
                UsageMetricType.STORAGE: {'warning': 500, 'critical': 1000},
                UsageMetricType.BANDWIDTH: {'warning': 200, 'critical': 500},
                UsageMetricType.API_CALLS: {'warning': 10000, 'critical': 50000},
                UsageMetricType.CONTENT_UPLOADS: {'warning': 100, 'critical': 500},
                UsageMetricType.COLLABORATION_SESSIONS: {'warning': 50, 'critical': 100},
                UsageMetricType.PROCESSING_HOURS: {'warning': 20, 'critical': 50}
            }
            
            threshold = thresholds.get(metric_type, {'warning': 100, 'critical': 500})
            
            # Recommandations basées sur les prédictions
            if max_predicted > threshold['critical']:
                recommendations.append(f"⚠️ Scaling critique requis: pic de {max_predicted:.1f} prédit")
                recommendations.append("Recommandation: Upgrade immédiat vers plan supérieur")
            elif max_predicted > threshold['warning']:
                recommendations.append(f"⚠️ Surveillance recommandée: usage élevé prédit ({max_predicted:.1f})")
                recommendations.append("Recommandation: Préparer upgrade dans les 7 jours")
            
            # Recommandations d'optimisation
            if mean_predicted > threshold['warning'] * 0.8:
                recommendations.append("💡 Optimisation recommandée: implémenter cache et compression")
            
            # Recommandations de timing
            peak_day = np.argmax(predictions) + 1
            if peak_day <= 7:
                recommendations.append(f"📅 Pic d'usage prévu le jour {peak_day}")
            
            return recommendations[:4]  # Maximum 4 recommandations
            
        except Exception as e:
            logger.error(f"❌ Error generating scaling recommendations: {e}")
            return []
    
    async def _evaluate_forecast_accuracy(
        self,
        model: Dict[str, Any],
        features: np.ndarray,
        targets: np.ndarray
    ) -> float:
        """Évalue la précision de la prédiction"""
        try:
            if model['type'] == 'baseline' or len(features) == 0:
                return 0.5  # Précision moyenne pour baseline
            
            return min(max(model.get('score', 0.5), 0.0), 1.0)  # Score entre 0 et 1
            
        except Exception as e:
            logger.error(f"❌ Error evaluating forecast accuracy: {e}")
            return 0.5
    
    def _get_accuracy_level(self, score: float) -> ForecastAccuracy:
        """Détermine le niveau de précision"""
        if score >= 0.95:
            return ForecastAccuracy.EXCELLENT
        elif score >= 0.85:
            return ForecastAccuracy.GOOD
        elif score >= 0.70:
            return ForecastAccuracy.MODERATE
        else:
            return ForecastAccuracy.POOR
    
    async def _generate_baseline_forecast(
        self,
        creator_id: str,
        metric_type: UsageMetricType,
        forecast_horizon: ForecastHorizon,
        periods: int
    ) -> UsageForecast:
        """Génère une prédiction baseline simple"""
        try:
            # Valeurs par défaut basées sur le type de métrique
            base_value = self._get_base_value_for_metric(metric_type)
            
            # Génération de prédictions simples avec légère tendance
            predictions = []
            for i in range(periods):
                # Tendance légère + variation aléatoire
                value = base_value * (1 + i * 0.01) * (0.9 + np.random.random() * 0.2)
                predictions.append(max(value, 0))
            
            # Intervalles de confiance larges
            confidence_intervals = [(p * 0.7, p * 1.3) for p in predictions]
            
            return UsageForecast(
                creator_id=creator_id,
                metric_type=metric_type,
                forecast_horizon=forecast_horizon,
                predicted_values=predictions,
                confidence_intervals=confidence_intervals,
                accuracy_score=0.5,
                accuracy_level=ForecastAccuracy.MODERATE,
                trend_analysis={'predicted_trend_percent': 1.0},
                seasonal_patterns={'patterns_detected': False},
                anomaly_alerts=[],
                scaling_recommendations=["📊 Données insuffisantes pour recommandations précises"]
            )
            
        except Exception as e:
            logger.error(f"❌ Error generating baseline forecast: {e}")
            return None
    
    async def batch_forecast_all_creators(
        self,
        creator_ids: List[str],
        metric_types: List[UsageMetricType],
        forecast_horizon: ForecastHorizon = ForecastHorizon.MONTHLY
    ) -> Dict[str, List[UsageForecast]]:
        """Génère des prédictions pour plusieurs créateurs"""
        try:
            all_forecasts = {}
            
            for creator_id in creator_ids:
                creator_forecasts = []
                for metric_type in metric_types:
                    forecast = await self.generate_usage_forecast(
                        creator_id, metric_type, forecast_horizon
                    )
                    if forecast:
                        creator_forecasts.append(forecast)
                
                all_forecasts[creator_id] = creator_forecasts
            
            logger.info(f"✅ Batch forecasting completed for {len(creator_ids)} creators")
            return all_forecasts
            
        except Exception as e:
            logger.error(f"❌ Error in batch forecasting: {e}")
            return {}
    
    async def update_model_performance(
        self,
        metric_type: UsageMetricType,
        actual_values: List[float],
        predicted_values: List[float]
    ) -> Dict[str, float]:
        """Met à jour les métriques de performance des modèles"""
        try:
            if len(actual_values) != len(predicted_values) or len(actual_values) == 0:
                return {}
            
            # Calcul des métriques
            mae = mean_absolute_error(actual_values, predicted_values)
            mse = mean_squared_error(actual_values, predicted_values)
            rmse = np.sqrt(mse)
            r2 = r2_score(actual_values, predicted_values)
            
            # Pourcentage d'erreur moyenne
            mape = np.mean(np.abs((np.array(actual_values) - np.array(predicted_values)) / np.array(actual_values))) * 100
            
            metrics = {
                'mae': mae,
                'mse': mse,
                'rmse': rmse,
                'r2_score': r2,
                'mape': mape,
                'accuracy': max(0, 1 - mape / 100)
            }
            
            logger.info(f"✅ Model performance updated for {metric_type.value}: R² = {r2:.3f}")
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error updating model performance: {e}")
            return {}


# Instance globale
usage_forecasting_engine = UsageForecastingEngine()

# Export des classes principales
__all__ = [
    'UsageForecastingEngine',
    'UsageForecast',
    'UsageDataPoint',
    'ForecastingModel',
    'ForecastHorizon',
    'UsageMetricType',
    'ForecastAccuracy',
    'usage_forecasting_engine'
]