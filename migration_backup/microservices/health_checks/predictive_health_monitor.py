"""
Predictive Health Monitor - IA Chéries Health Checks Module
Monitoring santé prédictif avec ML forecasting, capacity planning,
failure prediction et proactive alerting.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture health checks et tous ses patterns sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel. Toute reproduction, modification, distribution ou vol 
d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import pickle
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
import joblib

logger = logging.getLogger(__name__)

class PredictionType(Enum):
    """Types de prédiction health"""
    CAPACITY_FORECASTING = "capacity_forecasting"
    FAILURE_PREDICTION = "failure_prediction"
    PERFORMANCE_PREDICTION = "performance_prediction"
    RESOURCE_OPTIMIZATION = "resource_optimization"
    TREND_FORECASTING = "trend_forecasting"
    ANOMALY_PREDICTION = "anomaly_prediction"

class PredictionHorizon(Enum):
    """Horizons de prédiction"""
    SHORT_TERM = "short_term"      # 5-30 minutes
    MEDIUM_TERM = "medium_term"    # 30 minutes - 4 hours
    LONG_TERM = "long_term"        # 4-24 hours
    EXTENDED = "extended"          # 1-7 days

class RiskLevel(Enum):
    """Niveaux de risque prédits"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PredictionConfig:
    """Configuration monitoring prédictif"""
    prediction_interval_minutes: int = 5
    model_retrain_hours: int = 24
    feature_window_minutes: int = 60
    prediction_horizons: List[int] = field(default_factory=lambda: [15, 60, 240, 1440])  # minutes
    model_types: List[str] = field(default_factory=lambda: ['rf', 'gb', 'linear'])
    accuracy_threshold: float = 0.8
    confidence_threshold: float = 0.7
    failure_probability_threshold: float = 0.6

@dataclass
class HealthPrediction:
    """Prédiction santé service"""
    prediction_id: str
    service_name: str
    metric_name: str
    prediction_type: PredictionType
    horizon: PredictionHorizon
    horizon_minutes: int
    current_value: float
    predicted_value: float
    confidence: float
    risk_level: RiskLevel
    probability_failure: float
    timestamp: datetime
    expiry_time: datetime
    model_used: str
    features_used: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CapacityForecast:
    """Prévision capacité ressource"""
    resource_type: str
    current_utilization: float
    predicted_utilization: float
    capacity_threshold: float
    time_to_threshold: Optional[timedelta]
    scaling_recommendation: str
    confidence: float
    forecast_horizon: timedelta

@dataclass 
class FailurePrediction:
    """Prédiction failure service"""
    service_name: str
    failure_probability: float
    predicted_failure_time: Optional[datetime]
    failure_indicators: List[str]
    preventive_actions: List[str]
    confidence: float
    risk_factors: Dict[str, float]

class PredictiveModelManager:
    """Gestionnaire modèles ML prédictifs"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.model_metrics: Dict[str, Dict[str, float]] = {}
        self.last_training: Dict[str, datetime] = {}
        
    async def train_prediction_model(self, service_name: str, metric_name: str, 
                                   training_data: List[Tuple[List[float], float]],
                                   model_type: str = 'rf') -> Dict[str, Any]:
        """Entraîner modèle prédiction pour service/métrique"""
        model_key = f"{service_name}_{metric_name}_{model_type}"
        
        if len(training_data) < 50:
            return {'status': 'insufficient_data', 'required': 50, 'available': len(training_data)}
            
        try:
            # Préparer données
            X = np.array([features for features, target in training_data])
            y = np.array([target for features, target in training_data])
            
            # Diviser données
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Normaliser features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Créer et entraîner modèle
            if model_type == 'rf':
                model = RandomForestRegressor(n_estimators=100, random_state=42)
            elif model_type == 'gb':
                model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            elif model_type == 'linear':
                model = Ridge(alpha=1.0)
            else:
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                
            model.fit(X_train_scaled, y_train)
            
            # Évaluer modèle
            train_predictions = model.predict(X_train_scaled)
            test_predictions = model.predict(X_test_scaled)
            
            train_mae = mean_absolute_error(y_train, train_predictions)
            test_mae = mean_absolute_error(y_test, test_predictions)
            train_rmse = np.sqrt(mean_squared_error(y_train, train_predictions))
            test_rmse = np.sqrt(mean_squared_error(y_test, test_predictions))
            
            # Stocker modèle et métriques
            self.models[model_key] = model
            self.scalers[model_key] = scaler
            self.model_metrics[model_key] = {
                'train_mae': train_mae,
                'test_mae': test_mae,
                'train_rmse': train_rmse,
                'test_rmse': test_rmse,
                'accuracy': max(0, 1 - (test_mae / (np.max(y) - np.min(y)))),
                'samples_trained': len(training_data)
            }
            self.last_training[model_key] = datetime.now()
            
            logger.info(f"Trained model {model_key} with accuracy {self.model_metrics[model_key]['accuracy']:.3f}")
            
            return {
                'status': 'success',
                'model_key': model_key,
                'accuracy': self.model_metrics[model_key]['accuracy'],
                'test_mae': test_mae,
                'samples_used': len(training_data)
            }
            
        except Exception as e:
            logger.error(f"Model training failed for {model_key}: {e}")
            return {'status': 'error', 'error': str(e)}
            
    async def predict_with_model(self, model_key: str, features: List[float]) -> Tuple[float, float]:
        """Faire prédiction avec modèle"""
        if model_key not in self.models:
            raise ValueError(f"Model {model_key} not found")
            
        try:
            # Normaliser features
            features_array = np.array([features])
            features_scaled = self.scalers[model_key].transform(features_array)
            
            # Faire prédiction
            prediction = self.models[model_key].predict(features_scaled)[0]
            
            # Calculer confidence basée sur accuracy du modèle
            confidence = self.model_metrics[model_key].get('accuracy', 0.5)
            
            return float(prediction), float(confidence)
            
        except Exception as e:
            logger.error(f"Prediction failed for {model_key}: {e}")
            return 0.0, 0.0
            
    def get_model_info(self, model_key: str) -> Optional[Dict[str, Any]]:
        """Obtenir info modèle"""
        if model_key not in self.models:
            return None
            
        return {
            'model_key': model_key,
            'metrics': self.model_metrics.get(model_key, {}),
            'last_training': self.last_training.get(model_key),
            'model_type': type(self.models[model_key]).__name__
        }

class PredictiveHealthMonitor:
    """
    Monitoring santé prédictif avec ML forecasting.
    Capacity planning + failure prediction + proactive alerting.
    
    Features:
    - ML-based health forecasting multiple horizons
    - Capacity planning et resource optimization
    - Failure prediction avec early warning
    - Performance trend prediction
    - Proactive alerting basé sur prédictions
    - Auto-scaling recommendations
    """
    
    def __init__(self, prediction_config: PredictionConfig):
        self.prediction_config = prediction_config
        self.model_manager = PredictiveModelManager()
        
        # Stockage données et prédictions
        self.health_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=2000))
        self.active_predictions: Dict[str, HealthPrediction] = {}
        self.prediction_history: deque = deque(maxlen=1000)
        
        # Features engineering
        self.feature_extractors = {
            'moving_average': self._calculate_moving_average,
            'trend_slope': self._calculate_trend_slope,
            'volatility': self._calculate_volatility,
            'seasonal_component': self._extract_seasonal_component,
            'lag_features': self._create_lag_features
        }
        
        # Monitoring stats
        self.monitoring_stats = {
            'predictions_made': 0,
            'models_trained': 0,
            'accurate_predictions': 0,
            'false_positives': 0,
            'missed_failures': 0,
            'average_accuracy': 0.0
        }
        
    async def ingest_health_metric(self, service_name: str, metric_name: str, 
                                 value: float, timestamp: datetime = None):
        """Ingérer nouvelle métrique health"""
        if timestamp is None:
            timestamp = datetime.now()
            
        metric_key = f"{service_name}:{metric_name}"
        self.health_data[metric_key].append({
            'timestamp': timestamp,
            'value': value,
            'service': service_name,
            'metric': metric_name
        })
        
        # Déclencher prédictions automatiques si suffisamment de données
        if len(self.health_data[metric_key]) >= 100:
            await self._trigger_automatic_predictions(service_name, metric_name)
            
    async def generate_health_predictions(self, services: List[str] = None, 
                                        prediction_types: List[PredictionType] = None) -> Dict[str, Any]:
        """
        Générer prédictions health pour services.
        
        Args:
            services: Services à analyser (None = tous)
            prediction_types: Types prédictions (None = tous)
            
        Returns:
            Dict avec prédictions détaillées par service/type
        """
        if prediction_types is None:
            prediction_types = list(PredictionType)
            
        prediction_start = datetime.now()
        results = {
            'prediction_session_id': f"pred_{int(prediction_start.timestamp())}",
            'timestamp': prediction_start.isoformat(),
            'predictions': {},
            'summary': {}
        }
        
        # Déterminer services à traiter
        if services is None:
            services = list(set(key.split(':')[0] for key in self.health_data.keys()))
            
        try:
            for service_name in services:
                service_predictions = {}
                
                # Capacity Forecasting
                if PredictionType.CAPACITY_FORECASTING in prediction_types:
                    capacity_forecasts = await self._generate_capacity_forecasts(service_name)
                    service_predictions['capacity_forecasting'] = capacity_forecasts
                    
                # Failure Prediction
                if PredictionType.FAILURE_PREDICTION in prediction_types:
                    failure_predictions = await self._generate_failure_predictions(service_name)
                    service_predictions['failure_prediction'] = failure_predictions
                    
                # Performance Prediction
                if PredictionType.PERFORMANCE_PREDICTION in prediction_types:
                    performance_predictions = await self._generate_performance_predictions(service_name)
                    service_predictions['performance_prediction'] = performance_predictions
                    
                # Resource Optimization
                if PredictionType.RESOURCE_OPTIMIZATION in prediction_types:
                    optimization_recommendations = await self._generate_optimization_recommendations(service_name)
                    service_predictions['resource_optimization'] = optimization_recommendations
                    
                # Trend Forecasting
                if PredictionType.TREND_FORECASTING in prediction_types:
                    trend_forecasts = await self._generate_trend_forecasts(service_name)
                    service_predictions['trend_forecasting'] = trend_forecasts
                    
                results['predictions'][service_name] = service_predictions
                
            # Générer synthèse
            results['summary'] = await self._generate_prediction_summary(results['predictions'])
            results['execution_time_seconds'] = (datetime.now() - prediction_start).total_seconds()
            
            # Mettre à jour stats
            self.monitoring_stats['predictions_made'] += len(results['predictions'])
            
            return results
            
        except Exception as e:
            logger.error(f"Health prediction generation failed: {e}")
            return {
                'prediction_session_id': results['prediction_session_id'],
                'timestamp': prediction_start.isoformat(),
                'status': 'error',
                'error': str(e)
            }
            
    async def _generate_capacity_forecasts(self, service_name: str) -> List[CapacityForecast]:
        """Générer prévisions capacité"""
        forecasts = []
        
        # Métriques capacité typiques
        capacity_metrics = ['cpu_utilization', 'memory_utilization', 'disk_utilization', 
                          'network_utilization', 'connection_count']
        
        for metric_name in capacity_metrics:
            metric_key = f"{service_name}:{metric_name}"
            if metric_key not in self.health_data or len(self.health_data[metric_key]) < 50:
                continue
                
            try:
                # Préparer données historiques
                data_points = list(self.health_data[metric_key])[-100:]  # 100 derniers points
                values = [dp['value'] for dp in data_points]
                
                # Extraire features et entraîner modèle si nécessaire
                features_targets = await self._prepare_capacity_features(data_points)
                if len(features_targets) < 20:
                    continue
                    
                # Entraîner modèle de prédiction capacité
                model_result = await self.model_manager.train_prediction_model(
                    service_name, f"{metric_name}_capacity", features_targets, 'rf'
                )
                
                if model_result['status'] == 'success':
                    # Faire prédictions à différents horizons
                    current_value = values[-1]
                    
                    for horizon_minutes in self.prediction_config.prediction_horizons:
                        # Extraire features actuelles
                        current_features = await self._extract_current_features(data_points, metric_name)
                        
                        # Prédire utilisation future
                        model_key = model_result['model_key']
                        predicted_value, confidence = await self.model_manager.predict_with_model(
                            model_key, current_features
                        )
                        
                        # Calculer time to threshold
                        capacity_threshold = 80.0  # 80% utilisation
                        time_to_threshold = None
                        
                        if predicted_value > capacity_threshold:
                            # Estimer temps jusqu'au threshold
                            growth_rate = (predicted_value - current_value) / horizon_minutes
                            if growth_rate > 0:
                                minutes_to_threshold = (capacity_threshold - current_value) / growth_rate
                                time_to_threshold = timedelta(minutes=max(0, minutes_to_threshold))
                                
                        # Recommandation scaling
                        scaling_recommendation = await self._generate_scaling_recommendation(
                            current_value, predicted_value, capacity_threshold
                        )
                        
                        forecast = CapacityForecast(
                            resource_type=metric_name,
                            current_utilization=current_value,
                            predicted_utilization=predicted_value,
                            capacity_threshold=capacity_threshold,
                            time_to_threshold=time_to_threshold,
                            scaling_recommendation=scaling_recommendation,
                            confidence=confidence,
                            forecast_horizon=timedelta(minutes=horizon_minutes)
                        )
                        
                        forecasts.append(forecast)
                        
            except Exception as e:
                logger.error(f"Capacity forecast failed for {service_name}:{metric_name}: {e}")
                continue
                
        return forecasts
        
    async def _generate_failure_predictions(self, service_name: str) -> List[FailurePrediction]:
        """Générer prédictions failure"""
        predictions = []
        
        try:
            # Collecter métriques santé pour service
            service_metrics = {}
            for metric_key, data in self.health_data.items():
                if metric_key.startswith(f"{service_name}:"):
                    metric_name = metric_key.split(':', 1)[1]
                    service_metrics[metric_name] = list(data)[-50:]  # 50 derniers points
                    
            if not service_metrics:
                return predictions
                
            # Analyser indicateurs failure
            failure_indicators = await self._analyze_failure_indicators(service_metrics)
            
            # Calculer probabilité failure globale
            failure_probability = await self._calculate_failure_probability(failure_indicators)
            
            # Estimer temps prédit failure si probabilité élevée
            predicted_failure_time = None
            if failure_probability > self.prediction_config.failure_probability_threshold:
                predicted_failure_time = await self._estimate_failure_time(
                    service_metrics, failure_indicators
                )
                
            # Générer actions préventives
            preventive_actions = await self._generate_preventive_actions(
                failure_indicators, failure_probability
            )
            
            # Calculer confidence
            confidence = min(1.0, max(0.0, 
                (len(failure_indicators) * 0.2) + 
                (failure_probability * 0.6) + 
                (0.2 if len(service_metrics) > 3 else 0.1)
            ))
            
            prediction = FailurePrediction(
                service_name=service_name,
                failure_probability=failure_probability,
                predicted_failure_time=predicted_failure_time,
                failure_indicators=list(failure_indicators.keys()),
                preventive_actions=preventive_actions,
                confidence=confidence,
                risk_factors=failure_indicators
            )
            
            predictions.append(prediction)
            
        except Exception as e:
            logger.error(f"Failure prediction failed for {service_name}: {e}")
            
        return predictions
        
    async def _generate_performance_predictions(self, service_name: str) -> Dict[str, Any]:
        """Générer prédictions performance"""
        performance_predictions = {}
        
        # Métriques performance clés
        performance_metrics = ['response_time_ms', 'throughput_rps', 'error_rate_percent', 
                             'latency_p95', 'latency_p99']
        
        for metric_name in performance_metrics:
            metric_key = f"{service_name}:{metric_name}"
            if metric_key not in self.health_data or len(self.health_data[metric_key]) < 30:
                continue
                
            try:
                data_points = list(self.health_data[metric_key])[-60:]  # 60 derniers points
                values = [dp['value'] for dp in data_points]
                
                # Prédictions simples basées sur tendance
                if len(values) >= 10:
                    # Calculer tendance récente
                    recent_trend = np.polyfit(range(len(values[-10:])), values[-10:], 1)[0]
                    current_value = values[-1]
                    
                    # Prédictions multiples horizons
                    horizon_predictions = {}
                    for horizon_minutes in [15, 60, 240]:
                        predicted_value = current_value + (recent_trend * horizon_minutes / 5)  # 5 min par point
                        
                        # Évaluer si performance sera acceptable
                        performance_acceptable = await self._evaluate_performance_acceptability(
                            metric_name, predicted_value
                        )
                        
                        horizon_predictions[f"{horizon_minutes}min"] = {
                            'predicted_value': predicted_value,
                            'current_value': current_value,
                            'trend_slope': recent_trend,
                            'performance_acceptable': performance_acceptable,
                            'change_percent': ((predicted_value - current_value) / current_value * 100) if current_value != 0 else 0
                        }
                        
                    performance_predictions[metric_name] = horizon_predictions
                    
            except Exception as e:
                logger.error(f"Performance prediction failed for {service_name}:{metric_name}: {e}")
                continue
                
        return performance_predictions
        
    async def _generate_optimization_recommendations(self, service_name: str) -> List[Dict[str, Any]]:
        """Générer recommandations optimisation ressources"""
        recommendations = []
        
        try:
            # Analyser utilisation ressources actuelles
            resource_utilization = await self._analyze_resource_utilization(service_name)
            
            # Recommandations basées sur patterns d'utilisation
            if resource_utilization.get('cpu_avg', 0) > 70:
                recommendations.append({
                    'type': 'cpu_scaling',
                    'priority': 'high',
                    'description': 'High CPU utilization detected',
                    'action': 'Consider scaling up CPU or adding instances',
                    'impact': 'performance_improvement',
                    'estimated_benefit': '20-40% performance gain'
                })
                
            if resource_utilization.get('memory_avg', 0) > 80:
                recommendations.append({
                    'type': 'memory_scaling',
                    'priority': 'high',
                    'description': 'High memory utilization detected',
                    'action': 'Consider increasing memory allocation',
                    'impact': 'stability_improvement',
                    'estimated_benefit': 'Reduced GC pressure and OOM risk'
                })
                
            # Recommandations efficacité
            if resource_utilization.get('cpu_avg', 0) < 20:
                recommendations.append({
                    'type': 'resource_optimization',
                    'priority': 'medium',
                    'description': 'Low resource utilization detected',
                    'action': 'Consider reducing allocated resources',
                    'impact': 'cost_optimization',
                    'estimated_benefit': '15-30% cost reduction'
                })
                
        except Exception as e:
            logger.error(f"Optimization recommendations failed for {service_name}: {e}")
            
        return recommendations
        
    async def _generate_trend_forecasts(self, service_name: str) -> Dict[str, Any]:
        """Générer prévisions tendances"""
        trend_forecasts = {}
        
        for metric_key, data in self.health_data.items():
            if not metric_key.startswith(f"{service_name}:"):
                continue
                
            metric_name = metric_key.split(':', 1)[1]
            data_points = list(data)[-100:]  # 100 derniers points
            
            if len(data_points) < 20:
                continue
                
            try:
                values = [dp['value'] for dp in data_points]
                
                # Analyser tendance avec différentes méthodes
                linear_trend = np.polyfit(range(len(values)), values, 1)[0]
                
                # Tendance récente (derniers 20 points)
                recent_trend = np.polyfit(range(20), values[-20:], 1)[0] if len(values) >= 20 else linear_trend
                
                # Volatilité
                volatility = np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
                
                # Classification tendance
                trend_classification = "stable"
                if abs(linear_trend) > np.std(values) * 0.1:
                    trend_classification = "increasing" if linear_trend > 0 else "decreasing"
                    
                if volatility > 0.2:
                    trend_classification += "_volatile"
                    
                trend_forecasts[metric_name] = {
                    'linear_trend_slope': linear_trend,
                    'recent_trend_slope': recent_trend,
                    'volatility': volatility,
                    'trend_classification': trend_classification,
                    'trend_strength': abs(linear_trend) / (np.std(values) + 1e-6),
                    'forecast_confidence': max(0, 1 - volatility)
                }
                
            except Exception as e:
                logger.error(f"Trend forecast failed for {service_name}:{metric_name}: {e}")
                continue
                
        return trend_forecasts
        
    # Méthodes utilitaires
    
    async def _trigger_automatic_predictions(self, service_name: str, metric_name: str):
        """Déclencher prédictions automatiques"""
        try:
            # Vérifier si modèle doit être ré-entraîné
            model_key = f"{service_name}_{metric_name}_rf"
            last_training = self.model_manager.last_training.get(model_key)
            
            if (last_training is None or 
                datetime.now() - last_training > timedelta(hours=self.prediction_config.model_retrain_hours)):
                
                # Préparer données entraînement
                metric_key = f"{service_name}:{metric_name}"
                data_points = list(self.health_data[metric_key])
                
                if len(data_points) >= 100:
                    features_targets = await self._prepare_training_features(data_points)
                    
                    if len(features_targets) >= 50:
                        await self.model_manager.train_prediction_model(
                            service_name, metric_name, features_targets
                        )
                        self.monitoring_stats['models_trained'] += 1
                        
        except Exception as e:
            logger.error(f"Automatic prediction trigger failed: {e}")
            
    async def _prepare_capacity_features(self, data_points: List[Dict]) -> List[Tuple[List[float], float]]:
        """Préparer features pour prédiction capacité"""
        features_targets = []
        
        if len(data_points) < 20:
            return features_targets
            
        values = [dp['value'] for dp in data_points]
        
        # Créer windows pour features/targets
        window_size = 10
        for i in range(window_size, len(values)):
            # Features: statistiques window précédent
            window_values = values[i-window_size:i]
            features = [
                np.mean(window_values),        # Moyenne
                np.std(window_values),         # Écart-type
                np.max(window_values),         # Maximum
                np.min(window_values),         # Minimum
                values[i-1],                   # Valeur précédente
                np.mean(window_values[-3:])    # Moyenne 3 derniers
            ]
            
            target = values[i]
            features_targets.append((features, target))
            
        return features_targets
        
    async def _extract_current_features(self, data_points: List[Dict], metric_name: str) -> List[float]:
        """Extraire features actuelles pour prédiction"""
        if len(data_points) < 10:
            return [0.0] * 6
            
        values = [dp['value'] for dp in data_points]
        recent_values = values[-10:]
        
        features = [
            np.mean(recent_values),
            np.std(recent_values),
            np.max(recent_values),
            np.min(recent_values),
            values[-1],
            np.mean(values[-3:])
        ]
        
        return features
        
    async def _generate_scaling_recommendation(self, current: float, predicted: float, 
                                             threshold: float) -> str:
        """Générer recommandation scaling"""
        if predicted > threshold:
            if predicted > threshold * 1.2:
                return "scale_up_urgent"
            else:
                return "scale_up_recommended"
        elif current > threshold * 0.8:
            return "monitor_closely"
        elif current < threshold * 0.3:
            return "consider_scale_down"
        else:
            return "maintain_current"
            
    async def _analyze_failure_indicators(self, service_metrics: Dict[str, List]) -> Dict[str, float]:
        """Analyser indicateurs failure"""
        indicators = {}
        
        for metric_name, data_points in service_metrics.items():
            if len(data_points) < 10:
                continue
                
            values = [dp['value'] for dp in data_points]
            
            # Indicateurs selon type métrique
            if 'error_rate' in metric_name.lower():
                recent_avg = np.mean(values[-5:])
                if recent_avg > 5.0:  # 5% error rate
                    indicators[f"{metric_name}_high"] = min(1.0, recent_avg / 10.0)
                    
            elif 'response_time' in metric_name.lower() or 'latency' in metric_name.lower():
                recent_avg = np.mean(values[-5:])
                historical_avg = np.mean(values[:-5]) if len(values) > 5 else recent_avg
                
                if recent_avg > historical_avg * 1.5:  # 50% augmentation
                    indicators[f"{metric_name}_degraded"] = min(1.0, (recent_avg / historical_avg - 1))
                    
            elif 'cpu' in metric_name.lower() or 'memory' in metric_name.lower():
                recent_max = np.max(values[-5:])
                if recent_max > 90.0:  # 90% utilisation
                    indicators[f"{metric_name}_saturated"] = min(1.0, recent_max / 100.0)
                    
        return indicators
        
    async def _calculate_failure_probability(self, failure_indicators: Dict[str, float]) -> float:
        """Calculer probabilité failure globale"""
        if not failure_indicators:
            return 0.0
            
        # Pondération différente selon type indicateur
        weights = {
            'error_rate': 0.4,
            'response_time': 0.3,
            'latency': 0.3,
            'cpu': 0.2,
            'memory': 0.2
        }
        
        weighted_prob = 0.0
        total_weight = 0.0
        
        for indicator, value in failure_indicators.items():
            weight = 0.1  # Poids par défaut
            for key, w in weights.items():
                if key in indicator.lower():
                    weight = w
                    break
                    
            weighted_prob += value * weight
            total_weight += weight
            
        return min(1.0, weighted_prob / total_weight if total_weight > 0 else 0.0)
        
    async def _estimate_failure_time(self, service_metrics: Dict[str, List], 
                                   failure_indicators: Dict[str, float]) -> Optional[datetime]:
        """Estimer temps failure prédit"""
        if not failure_indicators:
            return None
            
        # Analyser vitesse dégradation
        degradation_rates = []
        
        for metric_name, data_points in service_metrics.items():
            if len(data_points) < 10:
                continue
                
            values = [dp['value'] for dp in data_points]
            timestamps = [dp['timestamp'] for dp in data_points]
            
            # Calculer taux changement récent
            if len(values) >= 5:
                recent_change = (values[-1] - values[-5]) / 5  # Change per point
                if recent_change != 0:
                    # Estimer temps jusqu'à seuil critique
                    if 'error_rate' in metric_name.lower():
                        critical_threshold = 20.0  # 20% error rate
                        current_value = values[-1]
                        if recent_change > 0:
                            points_to_critical = (critical_threshold - current_value) / recent_change
                            if points_to_critical > 0:
                                degradation_rates.append(points_to_critical * 5)  # 5 minutes per point
                                
        if degradation_rates:
            # Prendre médiane des estimations
            estimated_minutes = np.median(degradation_rates)
            return datetime.now() + timedelta(minutes=max(5, estimated_minutes))
            
        return None
        
    async def _generate_preventive_actions(self, failure_indicators: Dict[str, float], 
                                         failure_probability: float) -> List[str]:
        """Générer actions préventives"""
        actions = []
        
        if failure_probability > 0.8:
            actions.append("Immediate manual intervention required")
            actions.append("Consider emergency scaling")
            
        if failure_probability > 0.6:
            actions.append("Increase monitoring frequency")
            actions.append("Prepare rollback procedures")
            
        for indicator in failure_indicators:
            if 'error_rate' in indicator:
                actions.append("Review application logs for errors")
                actions.append("Check dependent service health")
            elif 'response_time' in indicator or 'latency' in indicator:
                actions.append("Check database performance")
                actions.append("Review slow queries")
            elif 'cpu' in indicator or 'memory' in indicator:
                actions.append("Consider resource scaling")
                actions.append("Check for resource leaks")
                
        return list(set(actions))  # Remove duplicates
        
    async def _evaluate_performance_acceptability(self, metric_name: str, predicted_value: float) -> bool:
        """Évaluer si performance prédite sera acceptable"""
        # Seuils acceptabilité par métrique
        thresholds = {
            'response_time_ms': 1000,
            'latency_p95': 2000,
            'latency_p99': 5000,
            'error_rate_percent': 5.0,
            'throughput_rps': 100  # Minimum acceptable
        }
        
        threshold = thresholds.get(metric_name)
        if threshold is None:
            return True  # Unknown metric, assume acceptable
            
        if metric_name == 'throughput_rps':
            return predicted_value >= threshold
        else:
            return predicted_value <= threshold
            
    async def _analyze_resource_utilization(self, service_name: str) -> Dict[str, float]:
        """Analyser utilisation ressources service"""
        utilization = {}
        
        resource_metrics = ['cpu_utilization', 'memory_utilization', 'disk_utilization']
        
        for metric_name in resource_metrics:
            metric_key = f"{service_name}:{metric_name}"
            if metric_key in self.health_data and self.health_data[metric_key]:
                values = [dp['value'] for dp in list(self.health_data[metric_key])[-20:]]
                utilization[f"{metric_name.split('_')[0]}_avg"] = np.mean(values)
                utilization[f"{metric_name.split('_')[0]}_max"] = np.max(values)
                
        return utilization
        
    async def _prepare_training_features(self, data_points: List[Dict]) -> List[Tuple[List[float], float]]:
        """Préparer features pour entraînement modèle"""
        return await self._prepare_capacity_features(data_points)
        
    async def _generate_prediction_summary(self, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Générer synthèse prédictions"""
        summary = {
            'services_analyzed': len(predictions),
            'high_risk_services': 0,
            'capacity_warnings': 0,
            'performance_degradation_predicted': 0,
            'recommendations_generated': 0
        }
        
        for service_name, service_predictions in predictions.items():
            # Analyser failure predictions
            if 'failure_prediction' in service_predictions:
                for fp in service_predictions['failure_prediction']:
                    if fp.failure_probability > 0.6:
                        summary['high_risk_services'] += 1
                        
            # Analyser capacity forecasts
            if 'capacity_forecasting' in service_predictions:
                for cf in service_predictions['capacity_forecasting']:
                    if cf.predicted_utilization > cf.capacity_threshold:
                        summary['capacity_warnings'] += 1
                        
            # Compter recommandations
            if 'resource_optimization' in service_predictions:
                summary['recommendations_generated'] += len(service_predictions['resource_optimization'])
                
        return summary

# Example usage et testing
if __name__ == "__main__":
    async def test_predictive_monitor():
        """Test monitoring prédictif"""
        config = PredictionConfig(
            prediction_interval_minutes=5,
            model_retrain_hours=1,  # Plus fréquent pour test
            prediction_horizons=[15, 60, 240]
        )
        
        monitor = PredictiveHealthMonitor(config)
        
        # Simuler données health avec tendances
        base_time = datetime.now()
        for i in range(150):  # 150 points de données
            timestamp = base_time + timedelta(minutes=i)
            
            # CPU utilization avec tendance croissante
            cpu_value = 30 + i * 0.2 + np.random.normal(0, 5)
            await monitor.ingest_health_metric('api_service', 'cpu_utilization', cpu_value, timestamp)
            
            # Response time avec dégradation
            response_time = 100 + i * 2 + np.random.normal(0, 20)
            await monitor.ingest_health_metric('api_service', 'response_time_ms', response_time, timestamp)
            
            # Error rate avec pics occasionnels
            error_rate = 1.0 + (5.0 if i in [50, 100, 140] else 0) + np.random.normal(0, 0.5)
            await monitor.ingest_health_metric('api_service', 'error_rate_percent', max(0, error_rate), timestamp)
            
        # Générer prédictions
        predictions = await monitor.generate_health_predictions(['api_service'])
        
        print("🔮 Predictive Health Monitor Results:")
        print(f"Services Analyzed: {predictions['summary']['services_analyzed']}")
        print(f"High Risk Services: {predictions['summary']['high_risk_services']}")
        print(f"Capacity Warnings: {predictions['summary']['capacity_warnings']}")
        print(f"Execution Time: {predictions['execution_time_seconds']:.2f}s")
        
        # Afficher quelques prédictions détaillées
        if 'api_service' in predictions['predictions']:
            service_pred = predictions['predictions']['api_service']
            
            if 'failure_prediction' in service_pred:
                for fp in service_pred['failure_prediction']:
                    print(f"Failure Probability: {fp.failure_probability:.2%}")
                    print(f"Risk Factors: {list(fp.risk_factors.keys())}")
                    
            if 'capacity_forecasting' in service_pred:
                print(f"Capacity Forecasts: {len(service_pred['capacity_forecasting'])}")
                
        return predictions
        
    # Run test
    asyncio.run(test_predictive_monitor())