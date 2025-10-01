"""
Predictive Incident Engine for IA Chéries Platform
ML-powered incident prediction and proactive alerting for Creator Economy

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import logging
import json
import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import uuid
import hashlib
from collections import defaultdict, deque

try:
    from sklearn.ensemble import IsolationForest, RandomForestRegressor
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.metrics import mean_squared_error, mean_absolute_error
    from sklearn.model_selection import train_test_split
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

logger = logging.getLogger(__name__)


class PredictionType(Enum):
    """Types of incident predictions"""
    SERVICE_OUTAGE = "service_outage"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    CAPACITY_OVERFLOW = "capacity_overflow"
    SECURITY_THREAT = "security_threat"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    CASCADE_FAILURE = "cascade_failure"
    CREATOR_CHURN_RISK = "creator_churn_risk"
    REVENUE_IMPACT = "revenue_impact"
    ANOMALY_DETECTION = "anomaly_detection"
    COMPLIANCE_VIOLATION = "compliance_violation"


class PredictionConfidence(Enum):
    """Confidence levels for predictions"""
    VERY_HIGH = "very_high"    # >95% confidence
    HIGH = "high"              # 85-95% confidence
    MEDIUM = "medium"          # 70-85% confidence
    LOW = "low"                # 50-70% confidence
    VERY_LOW = "very_low"      # <50% confidence


class AlertPriority(Enum):
    """Priority levels for proactive alerts"""
    IMMEDIATE = "immediate"    # Act within minutes
    URGENT = "urgent"          # Act within hours
    NORMAL = "normal"          # Act within days
    INFORMATIONAL = "informational"  # Monitor only


@dataclass
class MetricData:
    """Time series metric data point"""
    metric_name: str
    timestamp: datetime
    value: float
    labels: Dict[str, str]
    source_service: str
    creator_id: Optional[str] = None
    additional_context: Dict[str, Any] = None


@dataclass
class PredictionModel:
    """ML model configuration for predictions"""
    model_id: str
    model_type: str  # isolation_forest, random_forest, lstm, autoencoder
    prediction_type: PredictionType
    features: List[str]
    target_variable: Optional[str]
    lookback_window_hours: int
    prediction_horizon_hours: int
    model_file_path: Optional[str]
    last_trained: Optional[datetime]
    training_data_size: int
    model_accuracy: float
    model_parameters: Dict[str, Any]
    is_active: bool


@dataclass
class IncidentPrediction:
    """Incident prediction result"""
    prediction_id: str
    prediction_type: PredictionType
    predicted_at: datetime
    predicted_incident_time: datetime
    confidence_level: PredictionConfidence
    confidence_score: float  # 0.0 to 1.0
    alert_priority: AlertPriority
    affected_services: List[str]
    affected_creators: List[str]
    predicted_impact: Dict[str, Any]
    contributing_factors: List[Dict[str, Any]]
    recommended_actions: List[str]
    anomaly_scores: Dict[str, float]
    feature_importance: Dict[str, float]
    model_used: str
    threshold_values: Dict[str, float]
    historical_context: Dict[str, Any]
    prevention_window_hours: float
    similar_incidents: List[str]


@dataclass
class AnomalyAlert:
    """Anomaly detection alert"""
    alert_id: str
    detected_at: datetime
    metric_name: str
    anomaly_score: float
    threshold: float
    current_value: float
    expected_value: float
    deviation_percentage: float
    affected_service: str
    severity_level: str
    pattern_type: str  # spike, drop, trend_change, seasonal_deviation
    duration_minutes: int
    correlation_events: List[str]
    root_cause_hypothesis: List[str]


class PredictiveIncidentEngine:
    """
    Advanced ML-powered incident prediction engine
    Proactive incident detection and prevention for Creator Economy
    """
    
    def __init__(self, model_storage_path: str = "/tmp/incident_models"):
        """Initialize the predictive incident engine"""
        self.model_storage_path = model_storage_path
        self.models = {}
        self.metric_buffer = defaultdict(lambda: deque(maxlen=10000))
        self.prediction_cache = {}
        self.anomaly_detectors = {}
        self.scalers = {}
        self.label_encoders = {}
        
        # Configuration
        self.config = self._load_default_config()
        self.active_predictions = {}
        self.historical_incidents = []
        self.feature_extractors = self._initialize_feature_extractors()
        
        # Initialize models if available
        if ML_AVAILABLE:
            self._initialize_ml_models()
        else:
            logger.warning("ML libraries not available. Using rule-based predictions only.")
        
        logger.info("Predictive Incident Engine initialized")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            "prediction_intervals": {
                "service_health_check": 300,  # 5 minutes
                "anomaly_detection": 60,      # 1 minute
                "capacity_monitoring": 900,   # 15 minutes
                "creator_behavior": 1800      # 30 minutes
            },
            
            "anomaly_thresholds": {
                "cpu_usage": {"warning": 80, "critical": 95},
                "memory_usage": {"warning": 85, "critical": 98},
                "response_time": {"warning": 2000, "critical": 5000},  # ms
                "error_rate": {"warning": 0.05, "critical": 0.10},    # 5%, 10%
                "creator_session_drop": {"warning": 0.20, "critical": 0.40}
            },
            
            "prediction_models": {
                "service_outage": {
                    "features": ["cpu_usage", "memory_usage", "error_rate", "response_time"],
                    "lookback_hours": 24,
                    "prediction_horizon": 2
                },
                "capacity_overflow": {
                    "features": ["active_users", "requests_per_second", "storage_usage"],
                    "lookback_hours": 168,  # 1 week
                    "prediction_horizon": 24
                },
                "creator_churn": {
                    "features": ["session_duration", "upload_frequency", "engagement_rate"],
                    "lookback_hours": 720,  # 30 days
                    "prediction_horizon": 168  # 1 week
                }
            },
            
            "alert_routing": {
                PredictionType.SERVICE_OUTAGE: ["devops_oncall", "platform_team"],
                PredictionType.SECURITY_THREAT: ["security_team", "incident_commander"],
                PredictionType.CREATOR_CHURN_RISK: ["creator_success", "product_team"],
                PredictionType.REVENUE_IMPACT: ["business_team", "finance"]
            }
        }
    
    def _initialize_feature_extractors(self) -> Dict[str, Any]:
        """Initialize feature extraction functions"""
        return {
            "time_based": {
                "hour_of_day": lambda ts: ts.hour,
                "day_of_week": lambda ts: ts.weekday(),
                "is_weekend": lambda ts: ts.weekday() >= 5,
                "is_business_hours": lambda ts: 9 <= ts.hour <= 17
            },
            
            "statistical": {
                "rolling_mean_1h": self._rolling_mean_1h,
                "rolling_std_1h": self._rolling_std_1h,
                "rolling_percentile_95": self._rolling_percentile_95,
                "trend_slope": self._calculate_trend_slope,
                "seasonal_component": self._extract_seasonal_component
            },
            
            "creator_specific": {
                "session_quality_score": self._calculate_session_quality,
                "content_velocity": self._calculate_content_velocity,
                "engagement_momentum": self._calculate_engagement_momentum,
                "collaboration_health": self._calculate_collaboration_health
            }
        }
    
    def _initialize_ml_models(self):
        """Initialize ML models for different prediction types"""
        try:
            # Service outage prediction model
            self.models["service_outage"] = PredictionModel(
                model_id="service_outage_v1",
                model_type="isolation_forest",
                prediction_type=PredictionType.SERVICE_OUTAGE,
                features=["cpu_usage", "memory_usage", "error_rate", "response_time"],
                target_variable=None,
                lookback_window_hours=24,
                prediction_horizon_hours=2,
                model_file_path=None,
                last_trained=None,
                training_data_size=0,
                model_accuracy=0.0,
                model_parameters={"contamination": 0.1, "random_state": 42},
                is_active=False
            )
            
            # Capacity overflow prediction
            self.models["capacity_overflow"] = PredictionModel(
                model_id="capacity_overflow_v1",
                model_type="random_forest",
                prediction_type=PredictionType.CAPACITY_OVERFLOW,
                features=["active_users", "requests_per_second", "storage_usage"],
                target_variable="capacity_utilization",
                lookback_window_hours=168,
                prediction_horizon_hours=24,
                model_file_path=None,
                last_trained=None,
                training_data_size=0,
                model_accuracy=0.0,
                model_parameters={"n_estimators": 100, "random_state": 42},
                is_active=False
            )
            
            # Creator churn risk prediction
            self.models["creator_churn"] = PredictionModel(
                model_id="creator_churn_v1",
                model_type="random_forest",
                prediction_type=PredictionType.CREATOR_CHURN_RISK,
                features=["session_duration", "upload_frequency", "engagement_rate"],
                target_variable="churn_probability",
                lookback_window_hours=720,
                prediction_horizon_hours=168,
                model_file_path=None,
                last_trained=None,
                training_data_size=0,
                model_accuracy=0.0,
                model_parameters={"n_estimators": 100, "random_state": 42},
                is_active=False
            )
            
            logger.info(f"Initialized {len(self.models)} ML prediction models")
            
        except Exception as e:
            logger.error(f"Failed to initialize ML models: {e}")
    
    async def ingest_metric(self, metric: MetricData):
        """
        Ingest a metric data point for analysis
        
        Args:
            metric: Metric data point to ingest
        """
        try:
            # Store in buffer
            metric_key = f"{metric.source_service}:{metric.metric_name}"
            self.metric_buffer[metric_key].append(metric)
            
            # Check for immediate anomalies
            await self._check_real_time_anomalies(metric)
            
            # Update feature cache if needed
            await self._update_feature_cache(metric)
            
        except Exception as e:
            logger.error(f"Failed to ingest metric {metric.metric_name}: {e}")
    
    async def _check_real_time_anomalies(self, metric: MetricData):
        """Check for real-time anomalies in incoming metrics"""
        try:
            metric_key = f"{metric.source_service}:{metric.metric_name}"
            recent_values = [m.value for m in list(self.metric_buffer[metric_key])[-100:]]
            
            if len(recent_values) < 10:
                return  # Not enough data
            
            # Calculate basic statistics
            mean_value = np.mean(recent_values[:-1])  # Exclude current value
            std_value = np.std(recent_values[:-1])
            current_value = metric.value
            
            # Z-score anomaly detection
            if std_value > 0:
                z_score = abs((current_value - mean_value) / std_value)
                
                # Check thresholds
                anomaly_threshold = 3.0  # 3 standard deviations
                if z_score > anomaly_threshold:
                    await self._create_anomaly_alert(metric, z_score, mean_value)
            
            # Check configured thresholds
            await self._check_threshold_violations(metric)
            
        except Exception as e:
            logger.error(f"Failed to check real-time anomalies: {e}")
    
    async def _create_anomaly_alert(self, metric: MetricData, anomaly_score: float, expected_value: float):
        """Create an anomaly alert"""
        try:
            alert_id = f"ANOM-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
            
            deviation_pct = abs((metric.value - expected_value) / expected_value * 100) if expected_value != 0 else 0
            
            # Determine pattern type
            pattern_type = "spike" if metric.value > expected_value else "drop"
            if anomaly_score > 5.0:
                pattern_type = f"extreme_{pattern_type}"
            
            # Determine severity
            if anomaly_score > 5.0:
                severity = "critical"
            elif anomaly_score > 4.0:
                severity = "high"
            elif anomaly_score > 3.0:
                severity = "medium"
            else:
                severity = "low"
            
            alert = AnomalyAlert(
                alert_id=alert_id,
                detected_at=datetime.utcnow(),
                metric_name=metric.metric_name,
                anomaly_score=anomaly_score,
                threshold=3.0,
                current_value=metric.value,
                expected_value=expected_value,
                deviation_percentage=deviation_pct,
                affected_service=metric.source_service,
                severity_level=severity,
                pattern_type=pattern_type,
                duration_minutes=1,  # Initial duration
                correlation_events=[],
                root_cause_hypothesis=[]
            )
            
            # Find correlations
            await self._find_anomaly_correlations(alert)
            
            # Generate root cause hypotheses
            await self._generate_root_cause_hypotheses(alert)
            
            logger.warning(f"Anomaly detected: {alert.metric_name} = {alert.current_value:.2f} "
                          f"(expected: {alert.expected_value:.2f}, score: {alert.anomaly_score:.2f})")
            
            # Store alert
            # TODO: Send to alerting system
            
        except Exception as e:
            logger.error(f"Failed to create anomaly alert: {e}")
    
    async def _check_threshold_violations(self, metric: MetricData):
        """Check configured threshold violations"""
        thresholds = self.config["anomaly_thresholds"].get(metric.metric_name)
        if not thresholds:
            return
        
        value = metric.value
        
        if value >= thresholds.get("critical", float('inf')):
            await self._trigger_threshold_alert(metric, "critical", thresholds["critical"])
        elif value >= thresholds.get("warning", float('inf')):
            await self._trigger_threshold_alert(metric, "warning", thresholds["warning"])
    
    async def _trigger_threshold_alert(self, metric: MetricData, level: str, threshold: float):
        """Trigger threshold-based alert"""
        logger.warning(f"Threshold {level} violated: {metric.metric_name} = {metric.value} "
                      f"(threshold: {threshold})")
        # TODO: Send to alerting system
    
    async def predict_incidents(self, prediction_types: List[PredictionType] = None) -> List[IncidentPrediction]:
        """
        Run incident predictions for specified types
        
        Args:
            prediction_types: Types of predictions to run (None for all)
            
        Returns:
            List of incident predictions
        """
        if not ML_AVAILABLE:
            logger.warning("ML not available, using rule-based predictions")
            return await self._rule_based_predictions(prediction_types)
        
        try:
            predictions = []
            
            # Default to all prediction types
            if prediction_types is None:
                prediction_types = list(PredictionType)
            
            for pred_type in prediction_types:
                model_key = pred_type.value
                if model_key in self.models:
                    model = self.models[model_key]
                    if model.is_active:
                        pred = await self._run_ml_prediction(model)
                        if pred:
                            predictions.append(pred)
                else:
                    # Use rule-based prediction
                    pred = await self._rule_based_prediction(pred_type)
                    if pred:
                        predictions.append(pred)
            
            # Cache predictions
            for pred in predictions:
                self.prediction_cache[pred.prediction_id] = pred
            
            logger.info(f"Generated {len(predictions)} incident predictions")
            return predictions
            
        except Exception as e:
            logger.error(f"Failed to predict incidents: {e}")
            return []
    
    async def _run_ml_prediction(self, model: PredictionModel) -> Optional[IncidentPrediction]:
        """Run ML-based prediction"""
        try:
            # Extract features for the model
            features = await self._extract_model_features(model)
            if not features:
                return None
            
            # Load trained model
            ml_model = await self._load_trained_model(model)
            if not ml_model:
                return None
            
            # Make prediction
            if model.model_type == "isolation_forest":
                prediction_result = await self._run_anomaly_prediction(ml_model, features, model)
            elif model.model_type == "random_forest":
                prediction_result = await self._run_regression_prediction(ml_model, features, model)
            else:
                logger.warning(f"Unsupported model type: {model.model_type}")
                return None
            
            return prediction_result
            
        except Exception as e:
            logger.error(f"Failed to run ML prediction for {model.model_id}: {e}")
            return None
    
    async def _extract_model_features(self, model: PredictionModel) -> Optional[Dict[str, Any]]:
        """Extract features required for the model"""
        try:
            features = {}
            current_time = datetime.utcnow()
            
            # Get recent metric data
            lookback_start = current_time - timedelta(hours=model.lookback_window_hours)
            
            for feature_name in model.features:
                feature_values = []
                
                # Find metric data for this feature
                for metric_key, metric_deque in self.metric_buffer.items():
                    if feature_name in metric_key:
                        for metric in metric_deque:
                            if metric.timestamp >= lookback_start:
                                feature_values.append(metric.value)
                
                if feature_values:
                    # Calculate feature statistics
                    features[feature_name] = {
                        "current": feature_values[-1] if feature_values else 0,
                        "mean": np.mean(feature_values),
                        "std": np.std(feature_values),
                        "min": np.min(feature_values),
                        "max": np.max(feature_values),
                        "trend": self._calculate_trend(feature_values),
                        "values": feature_values[-100:]  # Last 100 values
                    }
                else:
                    logger.warning(f"No data found for feature: {feature_name}")
                    return None
            
            # Add time-based features
            features["time_features"] = {
                "hour_of_day": current_time.hour,
                "day_of_week": current_time.weekday(),
                "is_weekend": current_time.weekday() >= 5,
                "is_business_hours": 9 <= current_time.hour <= 17
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to extract features for model {model.model_id}: {e}")
            return None
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend in time series values"""
        if len(values) < 2:
            return 0.0
        
        x = np.arange(len(values))
        y = np.array(values)
        
        # Simple linear regression slope
        n = len(values)
        slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x * x) - np.sum(x) * np.sum(x))
        
        return slope
    
    async def _load_trained_model(self, model: PredictionModel) -> Optional[Any]:
        """Load trained ML model from storage"""
        if not model.model_file_path:
            # Train a new model if no saved model
            return await self._train_new_model(model)
        
        try:
            # TODO: Load from actual storage
            # For now, create a new model
            return await self._train_new_model(model)
        except Exception as e:
            logger.error(f"Failed to load model {model.model_id}: {e}")
            return None
    
    async def _train_new_model(self, model: PredictionModel) -> Optional[Any]:
        """Train a new ML model"""
        try:
            if model.model_type == "isolation_forest":
                from sklearn.ensemble import IsolationForest
                ml_model = IsolationForest(**model.model_parameters)
                
                # Get training data
                training_data = await self._get_training_data(model)
                if training_data is not None and len(training_data) > 10:
                    ml_model.fit(training_data)
                    model.is_active = True
                    model.last_trained = datetime.utcnow()
                    model.training_data_size = len(training_data)
                    logger.info(f"Trained {model.model_type} model for {model.prediction_type.value}")
                    return ml_model
                
            elif model.model_type == "random_forest":
                from sklearn.ensemble import RandomForestRegressor
                ml_model = RandomForestRegressor(**model.model_parameters)
                
                # Get training data with labels
                X, y = await self._get_supervised_training_data(model)
                if X is not None and y is not None and len(X) > 10:
                    ml_model.fit(X, y)
                    model.is_active = True
                    model.last_trained = datetime.utcnow()
                    model.training_data_size = len(X)
                    logger.info(f"Trained {model.model_type} model for {model.prediction_type.value}")
                    return ml_model
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to train model {model.model_id}: {e}")
            return None
    
    async def _get_training_data(self, model: PredictionModel) -> Optional[np.ndarray]:
        """Get training data for unsupervised models"""
        try:
            training_samples = []
            
            # Collect historical data
            for metric_key, metric_deque in self.metric_buffer.items():
                if any(feature in metric_key for feature in model.features):
                    for metric in metric_deque:
                        sample = [metric.value]  # Simple single-feature sample
                        training_samples.append(sample)
            
            if training_samples:
                return np.array(training_samples)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get training data: {e}")
            return None
    
    async def _get_supervised_training_data(self, model: PredictionModel) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Get training data for supervised models"""
        try:
            # TODO: Implement supervised training data collection
            # For now, generate synthetic data
            
            n_samples = 100
            n_features = len(model.features)
            
            X = np.random.random((n_samples, n_features))
            y = np.random.random(n_samples)  # Target values
            
            return X, y
            
        except Exception as e:
            logger.error(f"Failed to get supervised training data: {e}")
            return None, None
    
    async def _run_anomaly_prediction(self, ml_model: Any, features: Dict[str, Any], model: PredictionModel) -> Optional[IncidentPrediction]:
        """Run anomaly-based prediction"""
        try:
            # Prepare feature vector
            feature_vector = []
            for feature_name in model.features:
                if feature_name in features:
                    feature_vector.append(features[feature_name]["current"])
                else:
                    feature_vector.append(0.0)
            
            # Predict anomaly
            X = np.array([feature_vector])
            anomaly_score = ml_model.decision_function(X)[0]
            is_anomaly = ml_model.predict(X)[0] == -1
            
            if not is_anomaly:
                return None  # No incident predicted
            
            # Calculate confidence
            confidence_score = abs(anomaly_score)
            confidence_level = self._score_to_confidence_level(confidence_score)
            
            # Predict incident time (soon if anomaly detected)
            predicted_time = datetime.utcnow() + timedelta(hours=model.prediction_horizon_hours)
            
            # Determine priority
            priority = AlertPriority.URGENT if confidence_score > 0.5 else AlertPriority.NORMAL
            
            # Create prediction
            prediction = IncidentPrediction(
                prediction_id=f"PRED-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}",
                prediction_type=model.prediction_type,
                predicted_at=datetime.utcnow(),
                predicted_incident_time=predicted_time,
                confidence_level=confidence_level,
                confidence_score=confidence_score,
                alert_priority=priority,
                affected_services=self._identify_affected_services(features),
                affected_creators=[],  # TODO: Identify from context
                predicted_impact={"severity": "medium", "estimated_downtime_minutes": 30},
                contributing_factors=self._identify_contributing_factors(features, model),
                recommended_actions=self._generate_recommended_actions(model.prediction_type),
                anomaly_scores={f"feature_{i}": float(feature_vector[i]) for i in range(len(feature_vector))},
                feature_importance={},  # TODO: Calculate feature importance
                model_used=model.model_id,
                threshold_values={},
                historical_context={},
                prevention_window_hours=model.prediction_horizon_hours,
                similar_incidents=[]
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Failed to run anomaly prediction: {e}")
            return None
    
    async def _run_regression_prediction(self, ml_model: Any, features: Dict[str, Any], model: PredictionModel) -> Optional[IncidentPrediction]:
        """Run regression-based prediction"""
        try:
            # Prepare feature vector
            feature_vector = []
            for feature_name in model.features:
                if feature_name in features:
                    feature_vector.append(features[feature_name]["current"])
                else:
                    feature_vector.append(0.0)
            
            # Predict target value
            X = np.array([feature_vector])
            predicted_value = ml_model.predict(X)[0]
            
            # Check if prediction indicates incident
            incident_threshold = 0.7  # Threshold for incident prediction
            if predicted_value < incident_threshold:
                return None
            
            # Calculate confidence
            confidence_score = predicted_value
            confidence_level = self._score_to_confidence_level(confidence_score)
            
            # Predict incident time
            predicted_time = datetime.utcnow() + timedelta(hours=model.prediction_horizon_hours)
            
            # Determine priority
            if predicted_value > 0.9:
                priority = AlertPriority.IMMEDIATE
            elif predicted_value > 0.8:
                priority = AlertPriority.URGENT
            else:
                priority = AlertPriority.NORMAL
            
            # Create prediction
            prediction = IncidentPrediction(
                prediction_id=f"PRED-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}",
                prediction_type=model.prediction_type,
                predicted_at=datetime.utcnow(),
                predicted_incident_time=predicted_time,
                confidence_level=confidence_level,
                confidence_score=confidence_score,
                alert_priority=priority,
                affected_services=self._identify_affected_services(features),
                affected_creators=[],
                predicted_impact={"severity": "high" if predicted_value > 0.8 else "medium"},
                contributing_factors=self._identify_contributing_factors(features, model),
                recommended_actions=self._generate_recommended_actions(model.prediction_type),
                anomaly_scores={},
                feature_importance={},
                model_used=model.model_id,
                threshold_values={"incident_threshold": incident_threshold},
                historical_context={},
                prevention_window_hours=model.prediction_horizon_hours,
                similar_incidents=[]
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Failed to run regression prediction: {e}")
            return None
    
    def _score_to_confidence_level(self, score: float) -> PredictionConfidence:
        """Convert numeric score to confidence level"""
        if score >= 0.95:
            return PredictionConfidence.VERY_HIGH
        elif score >= 0.85:
            return PredictionConfidence.HIGH
        elif score >= 0.70:
            return PredictionConfidence.MEDIUM
        elif score >= 0.50:
            return PredictionConfidence.LOW
        else:
            return PredictionConfidence.VERY_LOW
    
    def _identify_affected_services(self, features: Dict[str, Any]) -> List[str]:
        """Identify services that might be affected"""
        affected = []
        
        # Analyze features to identify services
        for feature_name, feature_data in features.items():
            if "cpu" in feature_name or "memory" in feature_name:
                affected.append("compute-cluster")
            elif "response_time" in feature_name or "error_rate" in feature_name:
                affected.append("api-gateway")
            elif "storage" in feature_name:
                affected.append("storage-service")
        
        return list(set(affected))
    
    def _identify_contributing_factors(self, features: Dict[str, Any], model: PredictionModel) -> List[Dict[str, Any]]:
        """Identify contributing factors to the prediction"""
        factors = []
        
        for feature_name, feature_data in features.items():
            if feature_name == "time_features":
                continue
                
            # Check if feature is trending upward (potential issue)
            trend = feature_data.get("trend", 0)
            if abs(trend) > 0.1:  # Significant trend
                factors.append({
                    "factor": feature_name,
                    "type": "trend",
                    "value": trend,
                    "description": f"{feature_name} trending {'upward' if trend > 0 else 'downward'}"
                })
            
            # Check if feature is above normal levels
            current = feature_data.get("current", 0)
            mean = feature_data.get("mean", 0)
            std = feature_data.get("std", 0)
            
            if std > 0:
                z_score = (current - mean) / std
                if abs(z_score) > 2:  # More than 2 standard deviations
                    factors.append({
                        "factor": feature_name,
                        "type": "anomaly",
                        "value": z_score,
                        "description": f"{feature_name} is {abs(z_score):.1f} std devs from normal"
                    })
        
        return factors
    
    def _generate_recommended_actions(self, prediction_type: PredictionType) -> List[str]:
        """Generate recommended actions based on prediction type"""
        action_mapping = {
            PredictionType.SERVICE_OUTAGE: [
                "Scale up compute resources",
                "Check service health endpoints",
                "Review recent deployments",
                "Activate incident response team"
            ],
            PredictionType.CAPACITY_OVERFLOW: [
                "Scale up infrastructure capacity",
                "Enable auto-scaling policies",
                "Review traffic patterns",
                "Prepare capacity upgrade plan"
            ],
            PredictionType.CREATOR_CHURN_RISK: [
                "Reach out to at-risk creators",
                "Review creator support metrics",
                "Analyze recent platform changes",
                "Prepare retention offers"
            ],
            PredictionType.SECURITY_THREAT: [
                "Review security logs",
                "Check for unauthorized access",
                "Verify system integrity",
                "Alert security team"
            ],
            PredictionType.PERFORMANCE_DEGRADATION: [
                "Monitor response times",
                "Check database performance",
                "Review system resources",
                "Prepare performance tuning"
            ]
        }
        
        return action_mapping.get(prediction_type, ["Monitor situation closely", "Prepare incident response"])
    
    async def _rule_based_predictions(self, prediction_types: List[PredictionType]) -> List[IncidentPrediction]:
        """Fallback rule-based predictions when ML is not available"""
        predictions = []
        
        for pred_type in prediction_types:
            pred = await self._rule_based_prediction(pred_type)
            if pred:
                predictions.append(pred)
        
        return predictions
    
    async def _rule_based_prediction(self, prediction_type: PredictionType) -> Optional[IncidentPrediction]:
        """Generate rule-based prediction for a specific type"""
        try:
            current_time = datetime.utcnow()
            
            # Simple rule-based logic
            if prediction_type == PredictionType.SERVICE_OUTAGE:
                # Check if any critical metrics are trending badly
                critical_metrics = ["cpu_usage", "memory_usage", "error_rate"]
                warning_count = 0
                
                for metric_name in critical_metrics:
                    for metric_key, metric_deque in self.metric_buffer.items():
                        if metric_name in metric_key and len(metric_deque) > 5:
                            recent_values = [m.value for m in list(metric_deque)[-5:]]
                            if self._is_trending_badly(recent_values, metric_name):
                                warning_count += 1
                
                if warning_count >= 2:  # Multiple metrics trending badly
                    return IncidentPrediction(
                        prediction_id=f"RULE-{current_time.strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}",
                        prediction_type=prediction_type,
                        predicted_at=current_time,
                        predicted_incident_time=current_time + timedelta(hours=1),
                        confidence_level=PredictionConfidence.MEDIUM,
                        confidence_score=0.75,
                        alert_priority=AlertPriority.URGENT,
                        affected_services=["platform-services"],
                        affected_creators=[],
                        predicted_impact={"severity": "medium"},
                        contributing_factors=[{"factor": "multiple_metrics_trending", "type": "rule"}],
                        recommended_actions=self._generate_recommended_actions(prediction_type),
                        anomaly_scores={},
                        feature_importance={},
                        model_used="rule_based",
                        threshold_values={},
                        historical_context={},
                        prevention_window_hours=1.0,
                        similar_incidents=[]
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to generate rule-based prediction: {e}")
            return None
    
    def _is_trending_badly(self, values: List[float], metric_name: str) -> bool:
        """Check if metric values are trending in a bad direction"""
        if len(values) < 3:
            return False
        
        trend = self._calculate_trend(values)
        
        # Define what's "bad" for different metrics
        bad_trends = {
            "cpu_usage": trend > 0.5,      # Increasing CPU usage
            "memory_usage": trend > 0.5,   # Increasing memory usage
            "error_rate": trend > 0.01,    # Increasing error rate
            "response_time": trend > 10    # Increasing response time
        }
        
        return bad_trends.get(metric_name, False)
    
    # Feature extraction helper methods
    def _rolling_mean_1h(self, values: List[float]) -> float:
        """Calculate 1-hour rolling mean"""
        return np.mean(values[-60:]) if len(values) >= 60 else np.mean(values)
    
    def _rolling_std_1h(self, values: List[float]) -> float:
        """Calculate 1-hour rolling standard deviation"""
        return np.std(values[-60:]) if len(values) >= 60 else np.std(values)
    
    def _rolling_percentile_95(self, values: List[float]) -> float:
        """Calculate 95th percentile"""
        return np.percentile(values, 95) if values else 0.0
    
    def _calculate_trend_slope(self, values: List[float]) -> float:
        """Calculate trend slope using linear regression"""
        return self._calculate_trend(values)
    
    def _extract_seasonal_component(self, values: List[float]) -> float:
        """Extract seasonal component (simplified)"""
        if len(values) < 24:  # Need at least 24 hours of data
            return 0.0
        
        # Simple daily seasonality check
        daily_means = [np.mean(values[i:i+24]) for i in range(0, len(values)-24, 24)]
        return np.std(daily_means) if len(daily_means) > 1 else 0.0
    
    def _calculate_session_quality(self, creator_id: str) -> float:
        """Calculate creator session quality score"""
        # TODO: Implement based on creator session data
        return 0.8  # Placeholder
    
    def _calculate_content_velocity(self, creator_id: str) -> float:
        """Calculate content creation velocity"""
        # TODO: Implement based on content upload frequency
        return 0.7  # Placeholder
    
    def _calculate_engagement_momentum(self, creator_id: str) -> float:
        """Calculate engagement momentum"""
        # TODO: Implement based on engagement metrics
        return 0.6  # Placeholder
    
    def _calculate_collaboration_health(self, creator_id: str) -> float:
        """Calculate collaboration health score"""
        # TODO: Implement based on collaboration metrics
        return 0.9  # Placeholder
    
    async def _update_feature_cache(self, metric: MetricData):
        """Update feature cache with new metric"""
        # TODO: Implement feature caching for performance
        pass
    
    async def _find_anomaly_correlations(self, alert: AnomalyAlert):
        """Find correlations with other anomalies"""
        # TODO: Implement correlation analysis
        pass
    
    async def _generate_root_cause_hypotheses(self, alert: AnomalyAlert):
        """Generate root cause hypotheses"""
        # TODO: Implement root cause analysis
        pass
    
    def get_prediction_statistics(self) -> Dict[str, Any]:
        """Get prediction engine statistics"""
        return {
            "models_initialized": len(self.models),
            "active_models": sum(1 for m in self.models.values() if m.is_active),
            "metrics_buffer_size": sum(len(deque) for deque in self.metric_buffer.values()),
            "cached_predictions": len(self.prediction_cache),
            "ml_available": ML_AVAILABLE,
            "last_prediction_run": datetime.utcnow().isoformat()
        }
    
    def export_prediction_report(self, prediction_id: str) -> Dict[str, Any]:
        """Export detailed prediction report"""
        prediction = self.prediction_cache.get(prediction_id)
        if not prediction:
            return {"error": "Prediction not found"}
        
        return {
            "prediction_details": asdict(prediction),
            "model_performance": self._get_model_performance(prediction.model_used),
            "feature_analysis": self._analyze_prediction_features(prediction),
            "historical_accuracy": self._get_historical_accuracy(prediction.prediction_type),
            "recommended_monitoring": self._get_monitoring_recommendations(prediction)
        }
    
    def _get_model_performance(self, model_id: str) -> Dict[str, Any]:
        """Get model performance metrics"""
        model = self.models.get(model_id.replace("_v1", ""))
        if model:
            return {
                "model_accuracy": model.model_accuracy,
                "training_data_size": model.training_data_size,
                "last_trained": model.last_trained.isoformat() if model.last_trained else None,
                "is_active": model.is_active
            }
        return {}
    
    def _analyze_prediction_features(self, prediction: IncidentPrediction) -> Dict[str, Any]:
        """Analyze features that contributed to prediction"""
        return {
            "contributing_factors_count": len(prediction.contributing_factors),
            "top_contributing_factors": prediction.contributing_factors[:3],
            "anomaly_scores": prediction.anomaly_scores,
            "feature_importance": prediction.feature_importance
        }
    
    def _get_historical_accuracy(self, prediction_type: PredictionType) -> Dict[str, Any]:
        """Get historical accuracy for prediction type"""
        # TODO: Implement historical accuracy tracking
        return {
            "accuracy_rate": 0.85,
            "false_positive_rate": 0.10,
            "false_negative_rate": 0.05,
            "total_predictions": 100
        }
    
    def _get_monitoring_recommendations(self, prediction: IncidentPrediction) -> List[str]:
        """Get monitoring recommendations for prediction"""
        return [
            f"Monitor {', '.join(prediction.affected_services)} closely",
            f"Set up alerts for {prediction.prediction_type.value}",
            "Review prediction accuracy after incident resolution",
            "Update model if prediction accuracy is low"
        ]


# Factory function
def create_predictive_incident_engine(model_storage_path: str = "/tmp/incident_models") -> PredictiveIncidentEngine:
    """Create new predictive incident engine instance"""
    return PredictiveIncidentEngine(model_storage_path)


# Export all classes and functions
__all__ = [
    'PredictiveIncidentEngine',
    'PredictionType',
    'PredictionConfidence',
    'AlertPriority',
    'MetricData',
    'PredictionModel',
    'IncidentPrediction',
    'AnomalyAlert',
    'create_predictive_incident_engine'
]