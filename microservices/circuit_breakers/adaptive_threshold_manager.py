"""
Adaptive Threshold Manager - IA Chérie Platform
===========================================

Gestionnaire seuils adaptatifs avec ML prédictif.
Real-time threshold adjustment + pattern recognition + anomaly detection.

Author: Fahed Mlaiel (mlaiel@live.de)
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture circuit breakers et tous ses patterns sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, distribution 
ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.

Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import logging
import math
import statistics
from typing import Dict, Any, Optional, List, AsyncIterator, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from collections import deque, defaultdict
import json

# ML imports with graceful degradation
try:
    import numpy as np
    from sklearn.ensemble import GradientBoostingRegressor, IsolationForest
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, accuracy_score
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    np = None

# Try to import additional ML libraries
try:
    import joblib
    HAS_JOBLIB = True
except ImportError:
    HAS_JOBLIB = False

logger = logging.getLogger(__name__)

class ThresholdMetric(Enum):
    """Types of threshold metrics"""
    FAILURE_RATE = "FAILURE_RATE"
    RESPONSE_TIME = "RESPONSE_TIME"
    ERROR_RATE = "ERROR_RATE"
    THROUGHPUT = "THROUGHPUT"
    CPU_USAGE = "CPU_USAGE"
    MEMORY_USAGE = "MEMORY_USAGE"
    NETWORK_LATENCY = "NETWORK_LATENCY"

class AnomalyType(Enum):
    """Types of anomalies detected"""
    PERFORMANCE_DEGRADATION = "PERFORMANCE_DEGRADATION"
    TRAFFIC_SPIKE = "TRAFFIC_SPIKE"
    ERROR_BURST = "ERROR_BURST"
    RESOURCE_EXHAUSTION = "RESOURCE_EXHAUSTION"
    NETWORK_ISSUE = "NETWORK_ISSUE"
    UNKNOWN = "UNKNOWN"

@dataclass
class Anomaly:
    """Anomaly detection result"""
    anomaly_type: AnomalyType
    severity: float  # 0.0 to 1.0
    timestamp: datetime
    service_name: str
    metric_values: Dict[str, float]
    description: str
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'anomaly_type': self.anomaly_type.value,
            'severity': self.severity,
            'timestamp': self.timestamp.isoformat(),
            'service_name': self.service_name,
            'metric_values': self.metric_values,
            'description': self.description,
            'confidence': self.confidence
        }

@dataclass
class ThresholdRecommendation:
    """Threshold adjustment recommendation"""
    metric: ThresholdMetric
    current_value: float
    recommended_value: float
    confidence: float
    reason: str
    impact_estimate: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'metric': self.metric.value,
            'current_value': self.current_value,
            'recommended_value': self.recommended_value,
            'confidence': self.confidence,
            'reason': self.reason,
            'impact_estimate': self.impact_estimate
        }

@dataclass
class MLConfig:
    """ML configuration for adaptive thresholds"""
    # Model settings
    enable_ml: bool = True
    model_retrain_interval_hours: int = 6
    min_training_samples: int = 100
    
    # Feature engineering
    time_window_minutes: int = 30
    feature_history_hours: int = 24
    seasonal_adjustment: bool = True
    
    # Anomaly detection
    anomaly_contamination: float = 0.1
    anomaly_confidence_threshold: float = 0.7
    
    # Prediction settings
    prediction_horizon_minutes: int = 15
    prediction_confidence_threshold: float = 0.8
    
    # Performance tuning
    max_models_cache: int = 10
    model_validation_split: float = 0.2

class LSTMModel:
    """Simplified LSTM-like time series model (without TensorFlow)"""
    
    def __init__(self, sequence_length: int = 10):
        self.sequence_length = sequence_length
        self.weights = None
        self.scaler = MinMaxScaler() if HAS_SKLEARN else None
        self.is_trained = False
    
    def fit(self, data: List[float]) -> bool:
        """Fit the model on time series data"""
        if not HAS_SKLEARN or len(data) < self.sequence_length * 2:
            return False
        
        try:
            # Simple pattern-based learning (simplified LSTM)
            scaled_data = self.scaler.fit_transform(np.array(data).reshape(-1, 1)).flatten()
            
            # Create sequences
            sequences = []
            targets = []
            for i in range(len(scaled_data) - self.sequence_length):
                sequences.append(scaled_data[i:i + self.sequence_length])
                targets.append(scaled_data[i + self.sequence_length])
            
            # Simple linear regression on sequences (LSTM approximation)
            X = np.array(sequences)
            y = np.array(targets)
            
            # Calculate simple weights (mean-based)
            self.weights = np.mean(X, axis=0)
            self.is_trained = True
            return True
            
        except Exception as e:
            logger.error(f"LSTM model training failed: {str(e)}")
            return False
    
    def predict(self, sequence: List[float]) -> Optional[float]:
        """Predict next value in sequence"""
        if not self.is_trained or not HAS_SKLEARN:
            return None
        
        try:
            if len(sequence) < self.sequence_length:
                return None
            
            # Take last sequence_length values
            input_seq = sequence[-self.sequence_length:]
            scaled_seq = self.scaler.transform(np.array(input_seq).reshape(-1, 1)).flatten()
            
            # Simple prediction (weighted average)
            prediction = np.dot(scaled_seq, self.weights)
            
            # Inverse transform
            prediction_reshaped = np.array([[prediction]])
            result = self.scaler.inverse_transform(prediction_reshaped)[0][0]
            
            return float(result)
            
        except Exception as e:
            logger.debug(f"LSTM prediction failed: {str(e)}")
            return None

class ProphetModel:
    """Simplified Prophet-like model for load forecasting"""
    
    def __init__(self):
        self.trend_model = None
        self.seasonal_components = {}
        self.is_trained = False
        self.training_data = []
    
    def fit(self, timestamps: List[datetime], values: List[float]) -> bool:
        """Fit the model on time series data"""
        if len(timestamps) != len(values) or len(values) < 50:
            return False
        
        try:
            self.training_data = list(zip(timestamps, values))
            
            # Extract trends and seasonality (simplified)
            self._extract_trend(values)
            self._extract_seasonality(timestamps, values)
            
            self.is_trained = True
            return True
            
        except Exception as e:
            logger.error(f"Prophet model training failed: {str(e)}")
            return False
    
    def predict(self, future_timestamp: datetime) -> Optional[float]:
        """Predict value at future timestamp"""
        if not self.is_trained:
            return None
        
        try:
            # Get trend component
            trend = self._get_trend_component(future_timestamp)
            
            # Get seasonal component
            seasonal = self._get_seasonal_component(future_timestamp)
            
            return trend + seasonal
            
        except Exception as e:
            logger.debug(f"Prophet prediction failed: {str(e)}")
            return None
    
    def _extract_trend(self, values: List[float]):
        """Extract trend component (simplified linear trend)"""
        if HAS_SKLEARN:
            # Simple linear regression for trend
            X = np.arange(len(values)).reshape(-1, 1)
            y = np.array(values)
            
            # Calculate slope and intercept manually
            x_mean = np.mean(X.flatten())
            y_mean = np.mean(y)
            
            numerator = np.sum((X.flatten() - x_mean) * (y - y_mean))
            denominator = np.sum((X.flatten() - x_mean) ** 2)
            
            slope = numerator / denominator if denominator != 0 else 0
            intercept = y_mean - slope * x_mean
            
            self.trend_model = {'slope': slope, 'intercept': intercept}
        else:
            # Fallback: simple mean
            self.trend_model = {'slope': 0, 'intercept': statistics.mean(values)}
    
    def _extract_seasonality(self, timestamps: List[datetime], values: List[float]):
        """Extract seasonal components"""
        # Daily seasonality (hour of day)
        hourly_values = defaultdict(list)
        for ts, val in zip(timestamps, values):
            hourly_values[ts.hour].append(val)
        
        self.seasonal_components['hourly'] = {
            hour: statistics.mean(vals) for hour, vals in hourly_values.items()
        }
        
        # Weekly seasonality (day of week)
        daily_values = defaultdict(list)
        for ts, val in zip(timestamps, values):
            daily_values[ts.weekday()].append(val)
        
        self.seasonal_components['daily'] = {
            day: statistics.mean(vals) for day, vals in daily_values.items()
        }
    
    def _get_trend_component(self, timestamp: datetime) -> float:
        """Get trend component for timestamp"""
        if not self.trend_model:
            return 0.0
        
        # Calculate time index (days since training start)
        if self.training_data:
            start_time = self.training_data[0][0]
            time_index = (timestamp - start_time).total_seconds() / 86400  # days
        else:
            time_index = 0
        
        return self.trend_model['slope'] * time_index + self.trend_model['intercept']
    
    def _get_seasonal_component(self, timestamp: datetime) -> float:
        """Get seasonal component for timestamp"""
        seasonal_value = 0.0
        
        # Hourly seasonality
        if 'hourly' in self.seasonal_components:
            hourly_mean = statistics.mean(self.seasonal_components['hourly'].values())
            seasonal_value += self.seasonal_components['hourly'].get(timestamp.hour, hourly_mean) - hourly_mean
        
        # Daily seasonality
        if 'daily' in self.seasonal_components:
            daily_mean = statistics.mean(self.seasonal_components['daily'].values())
            seasonal_value += self.seasonal_components['daily'].get(timestamp.weekday(), daily_mean) - daily_mean
        
        return seasonal_value

class AdaptiveThresholdManager:
    """
    Gestionnaire seuils adaptatifs avec ML prédictif.
    Real-time threshold adjustment + pattern recognition + anomaly detection.
    """
    
    def __init__(self, service_name: str, ml_config: Optional[MLConfig] = None):
        self.service_name = service_name
        self.ml_config = ml_config or MLConfig()
        
        # ML Models
        self.ml_models = {}
        self._initialize_ml_models()
        
        # Data storage
        self.metrics_history = defaultdict(lambda: deque(maxlen=10000))
        self.threshold_history = defaultdict(lambda: deque(maxlen=1000))
        self.anomaly_history = deque(maxlen=1000)
        
        # Current thresholds
        self.current_thresholds = {
            ThresholdMetric.FAILURE_RATE: 0.1,
            ThresholdMetric.RESPONSE_TIME: 1000.0,
            ThresholdMetric.ERROR_RATE: 0.05,
            ThresholdMetric.THROUGHPUT: 100.0,
            ThresholdMetric.CPU_USAGE: 0.8,
            ThresholdMetric.MEMORY_USAGE: 0.8,
            ThresholdMetric.NETWORK_LATENCY: 100.0
        }
        
        # Model training status
        self.last_training = {}
        self.model_performance = {}
        
        # Background tasks
        self.training_task = None
        self.anomaly_detection_task = None
        
        logger.info(f"Adaptive threshold manager initialized for service: {service_name}")
    
    def _initialize_ml_models(self):
        """Initialize ML models"""
        if not self.ml_config.enable_ml or not HAS_SKLEARN:
            logger.warning("ML disabled or scikit-learn not available")
            return
        
        try:
            self.ml_models = {
                'threshold_predictor': GradientBoostingRegressor(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=6,
                    random_state=42
                ),
                'anomaly_detector': IsolationForest(
                    contamination=self.ml_config.anomaly_contamination,
                    random_state=42
                ),
                'pattern_recognizer': LSTMModel(sequence_length=10),
                'load_forecaster': ProphetModel()
            }
            
            # Scalers for feature preprocessing
            self.feature_scaler = StandardScaler()
            self.target_scaler = MinMaxScaler()
            
            logger.info("ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ML models: {str(e)}")
            self.ml_models = {}
    
    async def start_background_tasks(self):
        """Start background tasks for model training and anomaly detection"""
        if self.ml_config.enable_ml:
            self.training_task = asyncio.create_task(self._periodic_model_training())
            self.anomaly_detection_task = asyncio.create_task(self._continuous_anomaly_detection())
    
    async def stop_background_tasks(self):
        """Stop background tasks"""
        if self.training_task:
            self.training_task.cancel()
        if self.anomaly_detection_task:
            self.anomaly_detection_task.cancel()
    
    async def calculate_dynamic_thresholds(self, service_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcul seuils dynamiques basés sur ML et patterns.
        
        Features:
        - Machine Learning threshold prediction
        - Real-time pattern recognition
        - Seasonal adjustment algorithms
        - Load forecasting integration
        - Anomaly-based threshold adaptation
        """
        current_time = datetime.now()
        
        # Store current metrics
        await self._store_metrics(service_metrics, current_time)
        
        # Calculate new thresholds
        new_thresholds = {}
        threshold_recommendations = []
        
        for metric_type in ThresholdMetric:
            try:
                # Get current and recommended threshold
                current_threshold = self.current_thresholds.get(metric_type, 0.0)
                recommended_threshold = await self._calculate_threshold_for_metric(
                    metric_type, service_metrics, current_time
                )
                
                # Create recommendation
                recommendation = ThresholdRecommendation(
                    metric=metric_type,
                    current_value=current_threshold,
                    recommended_value=recommended_threshold,
                    confidence=await self._calculate_recommendation_confidence(metric_type),
                    reason=await self._get_recommendation_reason(metric_type, service_metrics),
                    impact_estimate=await self._estimate_threshold_impact(metric_type, recommended_threshold)
                )
                
                threshold_recommendations.append(recommendation)
                new_thresholds[metric_type.value] = recommended_threshold
                
                # Update current threshold if confidence is high enough
                if recommendation.confidence > self.ml_config.prediction_confidence_threshold:
                    self.current_thresholds[metric_type] = recommended_threshold
                
            except Exception as e:
                logger.error(f"Failed to calculate threshold for {metric_type.value}: {str(e)}")
                new_thresholds[metric_type.value] = self.current_thresholds.get(metric_type, 0.0)
        
        return {
            'service_name': self.service_name,
            'timestamp': current_time.isoformat(),
            'current_thresholds': {k.value: v for k, v in self.current_thresholds.items()},
            'recommended_thresholds': new_thresholds,
            'recommendations': [rec.to_dict() for rec in threshold_recommendations],
            'ml_enabled': self.ml_config.enable_ml and bool(self.ml_models),
            'model_performance': self.model_performance
        }
    
    async def _calculate_threshold_for_metric(self, metric_type: ThresholdMetric, 
                                            service_metrics: Dict[str, Any], 
                                            current_time: datetime) -> float:
        """Calculate threshold for specific metric"""
        current_threshold = self.current_thresholds.get(metric_type, 0.0)
        
        # Get metric history
        metric_history = list(self.metrics_history.get(metric_type.value, []))
        if len(metric_history) < 10:
            return current_threshold
        
        # Extract values and timestamps
        values = [point['value'] for point in metric_history[-100:]]  # Last 100 points
        timestamps = [point['timestamp'] for point in metric_history[-100:]]
        
        # Statistical analysis
        mean_value = statistics.mean(values)
        std_value = statistics.stdev(values) if len(values) > 1 else 0
        percentile_95 = np.percentile(values, 95) if HAS_SKLEARN else max(values)
        
        # Base threshold calculation
        if metric_type in [ThresholdMetric.FAILURE_RATE, ThresholdMetric.ERROR_RATE]:
            # For rates, use percentile-based approach
            base_threshold = min(percentile_95 * 1.2, mean_value + 2 * std_value)
        elif metric_type == ThresholdMetric.RESPONSE_TIME:
            # For response time, be more conservative
            base_threshold = min(percentile_95 * 1.5, mean_value + 3 * std_value)
        else:
            # For other metrics, use standard approach
            base_threshold = mean_value + 2 * std_value
        
        # ML-based adjustment
        if self.ml_config.enable_ml and self.ml_models.get('threshold_predictor'):
            try:
                ml_threshold = await self._predict_optimal_threshold(metric_type, service_metrics)
                if ml_threshold is not None:
                    # Blend statistical and ML predictions
                    ml_weight = 0.3  # Weight for ML prediction
                    base_threshold = base_threshold * (1 - ml_weight) + ml_threshold * ml_weight
            except Exception as e:
                logger.debug(f"ML threshold prediction failed for {metric_type.value}: {str(e)}")
        
        # Seasonal adjustment
        if self.ml_config.seasonal_adjustment:
            seasonal_factor = await self._calculate_seasonal_factor(metric_type, current_time)
            base_threshold *= seasonal_factor
        
        # Ensure reasonable bounds
        base_threshold = max(base_threshold, current_threshold * 0.5)  # Don't decrease too much
        base_threshold = min(base_threshold, current_threshold * 2.0)  # Don't increase too much
        
        return float(base_threshold)
    
    async def _predict_optimal_threshold(self, metric_type: ThresholdMetric, 
                                       service_metrics: Dict[str, Any]) -> Optional[float]:
        """Predict optimal threshold using ML"""
        model = self.ml_models.get('threshold_predictor')
        if not model or not hasattr(model, 'predict'):
            return None
        
        try:
            # Prepare features
            features = await self._extract_features_for_prediction(metric_type, service_metrics)
            if not features:
                return None
            
            # Make prediction
            features_array = np.array(features).reshape(1, -1)
            
            # Scale features if scaler is trained
            if hasattr(self.feature_scaler, 'scale_') and self.feature_scaler.scale_ is not None:
                features_scaled = self.feature_scaler.transform(features_array)
            else:
                features_scaled = features_array
            
            prediction = model.predict(features_scaled)[0]
            
            # Scale back if target scaler is trained
            if hasattr(self.target_scaler, 'scale_') and self.target_scaler.scale_ is not None:
                prediction_reshaped = np.array([[prediction]])
                prediction = self.target_scaler.inverse_transform(prediction_reshaped)[0][0]
            
            return float(prediction)
            
        except Exception as e:
            logger.debug(f"ML threshold prediction failed: {str(e)}")
            return None
    
    async def _extract_features_for_prediction(self, metric_type: ThresholdMetric, 
                                             service_metrics: Dict[str, Any]) -> Optional[List[float]]:
        """Extract features for ML prediction"""
        try:
            current_time = datetime.now()
            
            features = [
                # Current metric values
                service_metrics.get('cpu_usage', 0.0),
                service_metrics.get('memory_usage', 0.0),
                service_metrics.get('network_latency', 0.0),
                service_metrics.get('request_rate', 0.0),
                service_metrics.get('error_rate', 0.0),
                
                # Time-based features
                current_time.hour,
                current_time.weekday(),
                current_time.day,
                
                # Historical features
                await self._get_recent_trend(metric_type),
                await self._get_volatility_measure(metric_type),
            ]
            
            return features
            
        except Exception as e:
            logger.debug(f"Feature extraction failed: {str(e)}")
            return None
    
    async def detect_service_anomalies(self, metrics_stream: AsyncIterator[Dict[str, Any]]) -> List[Anomaly]:
        """Détection anomalies temps réel avec ML"""
        anomalies = []
        
        if not self.ml_config.enable_ml or not self.ml_models.get('anomaly_detector'):
            return anomalies
        
        try:
            async for metrics in metrics_stream:
                anomaly = await self._detect_single_anomaly(metrics)
                if anomaly:
                    anomalies.append(anomaly)
                    self.anomaly_history.append(anomaly)
        
        except Exception as e:
            logger.error(f"Anomaly detection failed: {str(e)}")
        
        return anomalies
    
    async def _detect_single_anomaly(self, metrics: Dict[str, Any]) -> Optional[Anomaly]:
        """Detect anomaly in single metrics point"""
        model = self.ml_models.get('anomaly_detector')
        if not model or not hasattr(model, 'predict'):
            return None
        
        try:
            # Extract features
            features = [
                metrics.get('cpu_usage', 0.0),
                metrics.get('memory_usage', 0.0),
                metrics.get('network_latency', 0.0),
                metrics.get('request_rate', 0.0),
                metrics.get('error_rate', 0.0),
                metrics.get('response_time', 0.0),
            ]
            
            features_array = np.array(features).reshape(1, -1)
            
            # Scale features if possible
            if hasattr(self.feature_scaler, 'scale_') and self.feature_scaler.scale_ is not None:
                features_scaled = self.feature_scaler.transform(features_array)
            else:
                features_scaled = features_array
            
            # Predict anomaly
            anomaly_score = model.decision_function(features_scaled)[0]
            is_anomaly = model.predict(features_scaled)[0] == -1
            
            if is_anomaly:
                # Classify anomaly type
                anomaly_type = await self._classify_anomaly_type(metrics, features)
                
                # Calculate severity based on score
                severity = min(1.0, max(0.0, (abs(anomaly_score) - 0.1) / 0.4))
                
                return Anomaly(
                    anomaly_type=anomaly_type,
                    severity=severity,
                    timestamp=datetime.now(),
                    service_name=self.service_name,
                    metric_values=metrics.copy(),
                    description=f"Anomaly detected: {anomaly_type.value}",
                    confidence=min(1.0, abs(anomaly_score))
                )
        
        except Exception as e:
            logger.debug(f"Single anomaly detection failed: {str(e)}")
        
        return None
    
    async def _classify_anomaly_type(self, metrics: Dict[str, Any], features: List[float]) -> AnomalyType:
        """Classify the type of anomaly"""
        cpu_usage = metrics.get('cpu_usage', 0.0)
        memory_usage = metrics.get('memory_usage', 0.0)
        error_rate = metrics.get('error_rate', 0.0)
        response_time = metrics.get('response_time', 0.0)
        request_rate = metrics.get('request_rate', 0.0)
        
        # Rule-based classification
        if cpu_usage > 0.9 or memory_usage > 0.9:
            return AnomalyType.RESOURCE_EXHAUSTION
        elif error_rate > 0.1:
            return AnomalyType.ERROR_BURST
        elif response_time > 5000:  # 5 seconds
            return AnomalyType.PERFORMANCE_DEGRADATION
        elif request_rate > statistics.mean([point['value'] for point in self.metrics_history['request_rate']][-10:]) * 3:
            return AnomalyType.TRAFFIC_SPIKE
        elif metrics.get('network_latency', 0) > 1000:
            return AnomalyType.NETWORK_ISSUE
        else:
            return AnomalyType.UNKNOWN
    
    async def predict_failure_probability(self, current_metrics: Dict[str, Any]) -> float:
        """Prédiction probabilité panne avec ensemble models"""
        if not self.ml_config.enable_ml:
            return 0.0
        
        try:
            # Get predictions from different models
            predictions = []
            
            # Anomaly-based prediction
            anomaly_model = self.ml_models.get('anomaly_detector')
            if anomaly_model and hasattr(anomaly_model, 'decision_function'):
                features = await self._extract_features_for_prediction(
                    ThresholdMetric.FAILURE_RATE, current_metrics
                )
                if features:
                    features_array = np.array(features).reshape(1, -1)
                    if hasattr(self.feature_scaler, 'scale_') and self.feature_scaler.scale_ is not None:
                        features_scaled = self.feature_scaler.transform(features_array)
                    else:
                        features_scaled = features_array
                    
                    anomaly_score = anomaly_model.decision_function(features_scaled)[0]
                    anomaly_probability = max(0.0, min(1.0, (1 - anomaly_score) / 2))
                    predictions.append(anomaly_probability)
            
            # Pattern-based prediction
            pattern_model = self.ml_models.get('pattern_recognizer')
            if pattern_model and pattern_model.is_trained:
                failure_history = [point['value'] for point in self.metrics_history.get('error_rate', [])][-10:]
                if len(failure_history) >= 5:
                    next_error_rate = pattern_model.predict(failure_history)
                    if next_error_rate is not None:
                        pattern_probability = min(1.0, max(0.0, next_error_rate * 10))  # Scale to probability
                        predictions.append(pattern_probability)
            
            # Statistical prediction
            error_rates = [point['value'] for point in self.metrics_history.get('error_rate', [])][-20:]
            if len(error_rates) > 5:
                recent_mean = statistics.mean(error_rates[-5:])
                historical_mean = statistics.mean(error_rates)
                if historical_mean > 0:
                    statistical_probability = min(1.0, recent_mean / (historical_mean * 2))
                    predictions.append(statistical_probability)
            
            # Ensemble prediction (average)
            if predictions:
                return statistics.mean(predictions)
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Failure probability prediction failed: {str(e)}")
            return 0.0
    
    async def adjust_thresholds_realtime(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ajustement seuils temps réel basé sur feedback"""
        adjustment_results = {}
        
        for metric_name, feedback in feedback_data.items():
            try:
                metric_type = ThresholdMetric(metric_name)
                current_threshold = self.current_thresholds.get(metric_type, 0.0)
                
                # Parse feedback
                too_sensitive = feedback.get('too_sensitive', False)
                not_sensitive_enough = feedback.get('not_sensitive_enough', False)
                optimal = feedback.get('optimal', False)
                
                if too_sensitive:
                    # Increase threshold to reduce sensitivity
                    new_threshold = current_threshold * 1.1
                    reason = "Reduced sensitivity based on feedback"
                elif not_sensitive_enough:
                    # Decrease threshold to increase sensitivity
                    new_threshold = current_threshold * 0.9
                    reason = "Increased sensitivity based on feedback"
                elif optimal:
                    # Keep current threshold
                    new_threshold = current_threshold
                    reason = "Threshold confirmed as optimal"
                else:
                    # No change
                    new_threshold = current_threshold
                    reason = "No feedback provided"
                
                # Apply adjustment
                self.current_thresholds[metric_type] = new_threshold
                
                adjustment_results[metric_name] = {
                    'previous_threshold': current_threshold,
                    'new_threshold': new_threshold,
                    'adjustment_factor': new_threshold / current_threshold if current_threshold > 0 else 1.0,
                    'reason': reason
                }
                
            except (ValueError, KeyError) as e:
                logger.warning(f"Invalid metric name in feedback: {metric_name}")
                adjustment_results[metric_name] = {'error': f'Invalid metric: {str(e)}'}
        
        return {
            'service_name': self.service_name,
            'timestamp': datetime.now().isoformat(),
            'adjustments': adjustment_results,
            'feedback_processed': len(feedback_data)
        }
    
    async def _store_metrics(self, metrics: Dict[str, Any], timestamp: datetime):
        """Store metrics in history"""
        for metric_name, value in metrics.items():
            if isinstance(value, (int, float)):
                self.metrics_history[metric_name].append({
                    'timestamp': timestamp,
                    'value': float(value)
                })
    
    async def _calculate_recommendation_confidence(self, metric_type: ThresholdMetric) -> float:
        """Calculate confidence in threshold recommendation"""
        # Base confidence
        confidence = 0.5
        
        # Increase confidence based on data availability
        metric_history = self.metrics_history.get(metric_type.value, [])
        if len(metric_history) > 100:
            confidence += 0.2
        if len(metric_history) > 500:
            confidence += 0.1
        
        # Increase confidence based on model performance
        model_perf = self.model_performance.get(metric_type.value, {})
        if model_perf.get('accuracy', 0) > 0.8:
            confidence += 0.2
        
        return min(1.0, confidence)
    
    async def _get_recommendation_reason(self, metric_type: ThresholdMetric, 
                                       service_metrics: Dict[str, Any]) -> str:
        """Get reason for threshold recommendation"""
        current_value = service_metrics.get(metric_type.value.lower(), 0)
        current_threshold = self.current_thresholds.get(metric_type, 0)
        
        if current_value > current_threshold:
            return f"Current {metric_type.value} ({current_value:.2f}) exceeds threshold ({current_threshold:.2f})"
        elif len(self.anomaly_history) > 0:
            recent_anomalies = [a for a in self.anomaly_history if a.timestamp > datetime.now() - timedelta(hours=1)]
            if recent_anomalies:
                return f"Recent anomalies detected ({len(recent_anomalies)} in last hour)"
        
        return "Threshold adjustment based on historical patterns and ML prediction"
    
    async def _estimate_threshold_impact(self, metric_type: ThresholdMetric, 
                                       new_threshold: float) -> Dict[str, float]:
        """Estimate impact of threshold change"""
        current_threshold = self.current_thresholds.get(metric_type, 0.0)
        
        if current_threshold == 0:
            return {'sensitivity_change': 0.0, 'false_positive_change': 0.0}
        
        threshold_ratio = new_threshold / current_threshold
        
        # Estimate changes
        sensitivity_change = 1.0 / threshold_ratio - 1.0  # Higher threshold = lower sensitivity
        false_positive_change = threshold_ratio - 1.0      # Higher threshold = fewer false positives
        
        return {
            'sensitivity_change': sensitivity_change,
            'false_positive_change': false_positive_change,
            'threshold_ratio': threshold_ratio
        }
    
    async def _calculate_seasonal_factor(self, metric_type: ThresholdMetric, 
                                       current_time: datetime) -> float:
        """Calculate seasonal adjustment factor"""
        # Simple seasonal factors based on time of day and day of week
        hour_factor = 1.0
        day_factor = 1.0
        
        # Hour-based adjustment
        if current_time.hour < 6 or current_time.hour > 22:  # Night hours
            hour_factor = 0.8  # Lower thresholds at night
        elif 9 <= current_time.hour <= 17:  # Business hours
            hour_factor = 1.2  # Higher thresholds during business hours
        
        # Day-based adjustment
        if current_time.weekday() >= 5:  # Weekend
            day_factor = 0.9  # Lower thresholds on weekends
        
        return hour_factor * day_factor
    
    async def _get_recent_trend(self, metric_type: ThresholdMetric) -> float:
        """Calculate recent trend in metric"""
        metric_history = list(self.metrics_history.get(metric_type.value, []))
        if len(metric_history) < 10:
            return 0.0
        
        recent_values = [point['value'] for point in metric_history[-10:]]
        older_values = [point['value'] for point in metric_history[-20:-10]] if len(metric_history) >= 20 else recent_values
        
        recent_mean = statistics.mean(recent_values)
        older_mean = statistics.mean(older_values)
        
        if older_mean == 0:
            return 0.0
        
        return (recent_mean - older_mean) / older_mean
    
    async def _get_volatility_measure(self, metric_type: ThresholdMetric) -> float:
        """Calculate volatility measure for metric"""
        metric_history = list(self.metrics_history.get(metric_type.value, []))
        if len(metric_history) < 5:
            return 0.0
        
        values = [point['value'] for point in metric_history[-50:]]  # Last 50 points
        if len(values) < 2:
            return 0.0
        
        mean_value = statistics.mean(values)
        std_value = statistics.stdev(values)
        
        if mean_value == 0:
            return 0.0
        
        return std_value / mean_value  # Coefficient of variation
    
    async def _periodic_model_training(self):
        """Periodic model training task"""
        while True:
            try:
                await asyncio.sleep(self.ml_config.model_retrain_interval_hours * 3600)
                await self.train_failure_prediction_models({})
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Periodic model training failed: {str(e)}")
    
    async def _continuous_anomaly_detection(self):
        """Continuous anomaly detection task"""
        while True:
            try:
                # Create metrics stream from recent data
                recent_metrics = []
                for metric_type in ThresholdMetric:
                    metric_history = list(self.metrics_history.get(metric_type.value, []))
                    if metric_history:
                        latest_metric = metric_history[-1]
                        recent_metrics.append({
                            metric_type.value.lower(): latest_metric['value']
                        })
                
                if recent_metrics:
                    # Convert to async iterator
                    async def metrics_stream():
                        for metrics in recent_metrics[-10:]:  # Last 10 data points
                            yield metrics
                    
                    anomalies = await self.detect_service_anomalies(metrics_stream())
                    if anomalies:
                        logger.info(f"Detected {len(anomalies)} anomalies for {self.service_name}")
                
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Continuous anomaly detection failed: {str(e)}")
                await asyncio.sleep(60)
    
    async def train_failure_prediction_models(self, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """Entraînement models prédiction pannes avec ML pipeline"""
        if not self.ml_config.enable_ml or not HAS_SKLEARN:
            return {'status': 'skipped', 'reason': 'ML disabled or scikit-learn not available'}
        
        training_results = {}
        
        try:
            # Prepare training data from history
            training_features = []
            training_targets = []
            
            for metric_type in ThresholdMetric:
                metric_history = list(self.metrics_history.get(metric_type.value, []))
                if len(metric_history) < self.ml_config.min_training_samples:
                    continue
                
                # Create feature-target pairs
                for i in range(10, len(metric_history)):
                    # Features: last 10 values + contextual info
                    recent_values = [point['value'] for point in metric_history[i-10:i]]
                    timestamp = metric_history[i]['timestamp']
                    
                    features = recent_values + [
                        timestamp.hour,
                        timestamp.weekday(),
                        timestamp.day
                    ]
                    
                    # Target: next threshold that would be optimal
                    target_value = metric_history[i]['value']
                    
                    training_features.append(features)
                    training_targets.append(target_value)
            
            if len(training_features) < self.ml_config.min_training_samples:
                return {'status': 'insufficient_data', 'samples_available': len(training_features)}
            
            # Convert to numpy arrays
            X = np.array(training_features)
            y = np.array(training_targets)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=self.ml_config.model_validation_split, random_state=42
            )
            
            # Train threshold predictor
            if 'threshold_predictor' in self.ml_models:
                model = self.ml_models['threshold_predictor']
                
                # Scale features
                X_train_scaled = self.feature_scaler.fit_transform(X_train)
                X_test_scaled = self.feature_scaler.transform(X_test)
                
                # Scale targets
                y_train_scaled = self.target_scaler.fit_transform(y_train.reshape(-1, 1)).flatten()
                
                # Train model
                model.fit(X_train_scaled, y_train_scaled)
                
                # Evaluate
                y_pred_scaled = model.predict(X_test_scaled)
                y_pred = self.target_scaler.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
                
                mse = mean_squared_error(y_test, y_pred)
                training_results['threshold_predictor'] = {
                    'mse': float(mse),
                    'samples': len(X_train),
                    'status': 'trained'
                }
            
            # Train anomaly detector
            if 'anomaly_detector' in self.ml_models:
                anomaly_model = self.ml_models['anomaly_detector']
                anomaly_model.fit(X_train_scaled)
                
                training_results['anomaly_detector'] = {
                    'samples': len(X_train),
                    'status': 'trained'
                }
            
            # Train pattern recognizer
            if 'pattern_recognizer' in self.ml_models:
                pattern_model = self.ml_models['pattern_recognizer']
                
                # Use error rate history for pattern recognition
                error_history = [point['value'] for point in self.metrics_history.get('error_rate', [])]
                if len(error_history) >= 20:
                    pattern_trained = pattern_model.fit(error_history)
                    training_results['pattern_recognizer'] = {
                        'status': 'trained' if pattern_trained else 'failed',
                        'samples': len(error_history)
                    }
            
            # Train load forecaster
            if 'load_forecaster' in self.ml_models:
                forecaster = self.ml_models['load_forecaster']
                
                # Use request rate history
                request_history = list(self.metrics_history.get('request_rate', []))
                if len(request_history) >= 50:
                    timestamps = [point['timestamp'] for point in request_history]
                    values = [point['value'] for point in request_history]
                    
                    forecaster_trained = forecaster.fit(timestamps, values)
                    training_results['load_forecaster'] = {
                        'status': 'trained' if forecaster_trained else 'failed',
                        'samples': len(request_history)
                    }
            
            # Update training status
            for model_name in training_results:
                self.last_training[model_name] = datetime.now()
                self.model_performance[model_name] = training_results[model_name]
            
            logger.info(f"Model training completed for {self.service_name}: {training_results}")
            
            return {
                'status': 'completed',
                'service_name': self.service_name,
                'training_results': training_results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Model training failed: {str(e)}")
            return {'status': 'failed', 'error': str(e)}
    
    async def recommend_proactive_actions(self, prediction_results: Dict[str, Any]) -> List[str]:
        """Recommandations actions proactives basées sur prédictions"""
        recommendations = []
        
        failure_probability = prediction_results.get('failure_probability', 0.0)
        anomalies = prediction_results.get('anomalies', [])
        threshold_adjustments = prediction_results.get('threshold_adjustments', {})
        
        # High failure probability
        if failure_probability > 0.7:
            recommendations.append("CRITICAL: High failure probability detected - consider circuit breaker activation")
            recommendations.append("Scale up resources immediately")
            recommendations.append("Enable enhanced monitoring")
        elif failure_probability > 0.5:
            recommendations.append("WARNING: Elevated failure risk - prepare contingency plans")
            recommendations.append("Review recent changes and configurations")
        
        # Anomaly-based recommendations
        for anomaly in anomalies:
            if anomaly.get('severity', 0) > 0.8:
                recommendations.append(f"URGENT: {anomaly.get('description', 'Critical anomaly')} - immediate action required")
            elif anomaly.get('severity', 0) > 0.5:
                recommendations.append(f"WARNING: {anomaly.get('description', 'Anomaly detected')} - monitor closely")
        
        # Threshold adjustment recommendations
        for metric, adjustment in threshold_adjustments.items():
            if adjustment.get('confidence', 0) > 0.8:
                recommendations.append(f"Adjust {metric} threshold from {adjustment.get('current_value', 'N/A')} to {adjustment.get('recommended_value', 'N/A')}")
        
        # General recommendations
        if not recommendations:
            recommendations.append("System operating normally - continue standard monitoring")
        
        return recommendations
    
    async def get_manager_status(self) -> Dict[str, Any]:
        """Get adaptive threshold manager status"""
        return {
            'service_name': self.service_name,
            'ml_enabled': self.ml_config.enable_ml and bool(self.ml_models),
            'models_available': list(self.ml_models.keys()) if self.ml_models else [],
            'metrics_tracked': len(self.metrics_history),
            'current_thresholds': {k.value: v for k, v in self.current_thresholds.items()},
            'anomalies_detected': len(self.anomaly_history),
            'last_training': {k: v.isoformat() for k, v in self.last_training.items()},
            'model_performance': self.model_performance,
            'background_tasks_active': {
                'training': self.training_task is not None and not self.training_task.done(),
                'anomaly_detection': self.anomaly_detection_task is not None and not self.anomaly_detection_task.done()
            }
        }

# Export main classes
__all__ = [
    'AdaptiveThresholdManager',
    'MLConfig', 
    'ThresholdMetric',
    'AnomalyType',
    'Anomaly',
    'ThresholdRecommendation',
    'LSTMModel',
    'ProphetModel'
]