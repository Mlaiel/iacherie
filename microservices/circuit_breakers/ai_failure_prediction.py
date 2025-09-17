"""
AI Failure Prediction - Enterprise Circuit Breakers
Machine Learning-based failure prediction and proactive action system

This module implements advanced AI/ML models for predicting service failures
and recommending proactive actions to prevent cascade failures.

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
            Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - PROTECTION FORTE
Cette implémentation est la propriété exclusive de Fahed Mlaiel.
Toute reproduction ou utilisation non autorisée est strictement interdite.
"""

import asyncio
import logging
import time
import uuid
import json
import pickle
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from datetime import datetime, timedelta
import statistics
from collections import defaultdict, deque
import warnings
warnings.filterwarnings('ignore')

# ML Libraries
try:
    from sklearn.ensemble import RandomForestClassifier, IsolationForest
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, confusion_matrix
    from sklearn.cluster import DBSCAN
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("⚠️ Scikit-learn not available - AI prediction features limited")

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logging.warning("⚠️ TensorFlow not available - Deep learning features limited")


logger = logging.getLogger(__name__)


class PredictionModel(Enum):
    """Types of prediction models"""
    RANDOM_FOREST = "random_forest"
    NEURAL_NETWORK = "neural_network"
    ISOLATION_FOREST = "isolation_forest"
    ENSEMBLE = "ensemble"
    TIME_SERIES = "time_series"


class FailureType(Enum):
    """Types of failures to predict"""
    SERVICE_FAILURE = "service_failure"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    CASCADE_FAILURE = "cascade_failure"
    NETWORK_PARTITION = "network_partition"
    DATABASE_ISSUE = "database_issue"


class PredictionConfidence(Enum):
    """Confidence levels for predictions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionType(Enum):
    """Types of proactive actions"""
    SCALE_UP = "scale_up"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"
    LOAD_BALANCER_ADJUST = "load_balancer_adjust"
    CACHE_WARM_UP = "cache_warm_up"
    RESOURCE_CLEANUP = "resource_cleanup"
    ALERT_NOTIFICATION = "alert_notification"
    FAILOVER_INITIATE = "failover_initiate"
    TRAFFIC_REDIRECT = "traffic_redirect"


@dataclass
class FeatureVector:
    """Feature vector for ML model"""
    timestamp: datetime
    service_name: str
    response_time: float = 0.0
    error_rate: float = 0.0
    throughput: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_latency: float = 0.0
    active_connections: int = 0
    queue_length: int = 0
    circuit_state: str = "CLOSED"
    dependency_health: float = 1.0
    time_of_day: int = 0
    day_of_week: int = 0
    seasonal_factor: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FailurePrediction:
    """Failure prediction result"""
    prediction_id: str
    service_name: str
    failure_type: FailureType
    probability: float
    confidence: PredictionConfidence
    time_to_failure_minutes: Optional[int]
    features_used: List[str]
    model_used: str
    timestamp: datetime
    contributing_factors: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)


@dataclass
class ProactiveAction:
    """Proactive action recommendation"""
    action_id: str
    action_type: ActionType
    target_service: str
    priority: int  # 1-10, 10 being highest
    estimated_impact: float  # 0-1, 1 being maximum positive impact
    implementation_complexity: int  # 1-5, 5 being most complex
    resource_cost: float  # Relative cost
    success_probability: float  # 0-1
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)


class FeatureExtractor:
    """Extract features from service metrics for ML models"""
    
    def __init__(self):
        self.feature_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.label_encoders: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def extract_features(self, service_name: str, metrics: Dict[str, Any]) -> FeatureVector:
        """Extract feature vector from service metrics"""
        timestamp = datetime.now()
        
        feature_vector = FeatureVector(
            timestamp=timestamp,
            service_name=service_name,
            response_time=metrics.get('response_time', 0.0),
            error_rate=metrics.get('error_rate', 0.0),
            throughput=metrics.get('throughput', 0.0),
            cpu_usage=metrics.get('cpu_usage', 0.0),
            memory_usage=metrics.get('memory_usage', 0.0),
            disk_usage=metrics.get('disk_usage', 0.0),
            network_latency=metrics.get('network_latency', 0.0),
            active_connections=metrics.get('active_connections', 0),
            queue_length=metrics.get('queue_length', 0),
            circuit_state=metrics.get('circuit_state', 'CLOSED'),
            dependency_health=metrics.get('dependency_health', 1.0),
            time_of_day=timestamp.hour,
            day_of_week=timestamp.weekday(),
            seasonal_factor=self._calculate_seasonal_factor(timestamp)
        )
        
        # Add to history
        self.feature_history[service_name].append(feature_vector)
        
        return feature_vector
    
    def _calculate_seasonal_factor(self, timestamp: datetime) -> float:
        """Calculate seasonal factor based on time patterns"""
        # Simple seasonal factor based on hour of day
        hour = timestamp.hour
        if 9 <= hour <= 17:  # Business hours
            return 1.2
        elif 22 <= hour or hour <= 6:  # Night hours
            return 0.6
        else:
            return 1.0
    
    def get_feature_matrix(self, service_name: str, lookback_hours: int = 24) -> np.ndarray:
        """Get feature matrix for ML training"""
        if not SKLEARN_AVAILABLE:
            return np.array([])
        
        cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
        features = [fv for fv in self.feature_history[service_name] 
                   if fv.timestamp >= cutoff_time]
        
        if not features:
            return np.array([])
        
        # Convert to numerical matrix
        feature_matrix = []
        for fv in features:
            row = [
                fv.response_time,
                fv.error_rate,
                fv.throughput,
                fv.cpu_usage,
                fv.memory_usage,
                fv.disk_usage,
                fv.network_latency,
                float(fv.active_connections),
                float(fv.queue_length),
                self._encode_circuit_state(fv.circuit_state),
                fv.dependency_health,
                float(fv.time_of_day) / 24.0,  # Normalize
                float(fv.day_of_week) / 7.0,   # Normalize
                fv.seasonal_factor
            ]
            feature_matrix.append(row)
        
        return np.array(feature_matrix)
    
    def _encode_circuit_state(self, state: str) -> float:
        """Encode circuit breaker state as numerical value"""
        state_mapping = {
            'CLOSED': 0.0,
            'HALF_OPEN': 0.5,
            'OPEN': 1.0
        }
        return state_mapping.get(state, 0.0)
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names"""
        return [
            'response_time',
            'error_rate',
            'throughput',
            'cpu_usage',
            'memory_usage',
            'disk_usage',
            'network_latency',
            'active_connections',
            'queue_length',
            'circuit_state',
            'dependency_health',
            'time_of_day',
            'day_of_week',
            'seasonal_factor'
        ]


class AnomalyDetector:
    """Anomaly detection for unusual service behavior"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.is_trained: Dict[str, bool] = defaultdict(bool)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def train_anomaly_detector(self, service_name: str, feature_matrix: np.ndarray) -> bool:
        """Train anomaly detection model for service"""
        if not SKLEARN_AVAILABLE or feature_matrix.size == 0:
            return False
        
        try:
            # Use Isolation Forest for anomaly detection
            model = IsolationForest(
                contamination=0.1,  # Assume 10% of data points are anomalies
                random_state=42,
                n_estimators=100
            )
            
            model.fit(feature_matrix)
            self.models[service_name] = model
            self.is_trained[service_name] = True
            
            self.logger.info(f"✅ Anomaly detector trained for {service_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to train anomaly detector for {service_name}: {e}")
            return False
    
    async def detect_anomalies(self, service_name: str, features: np.ndarray) -> Dict[str, Any]:
        """Detect anomalies in service behavior"""
        if not self.is_trained.get(service_name, False):
            return {'anomalies_detected': False, 'reason': 'Model not trained'}
        
        try:
            model = self.models[service_name]
            predictions = model.predict(features)
            anomaly_scores = model.decision_function(features)
            
            # -1 indicates anomaly, 1 indicates normal
            anomalies = predictions == -1
            anomaly_count = np.sum(anomalies)
            
            return {
                'anomalies_detected': anomaly_count > 0,
                'anomaly_count': int(anomaly_count),
                'total_samples': len(predictions),
                'anomaly_rate': float(anomaly_count / len(predictions)),
                'anomaly_scores': anomaly_scores.tolist(),
                'anomaly_indices': np.where(anomalies)[0].tolist()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to detect anomalies for {service_name}: {e}")
            return {'anomalies_detected': False, 'error': str(e)}


class FailurePredictor:
    """ML-based failure prediction engine"""
    
    def __init__(self):
        self.models: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.model_performance: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.is_trained: Dict[str, Dict[str, bool]] = defaultdict(lambda: defaultdict(bool))
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def train_prediction_model(self, service_name: str, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """Train failure prediction model for service"""
        try:
            model_type = PredictionModel[training_data.get('model_type', 'RANDOM_FOREST')]
            features = np.array(training_data.get('features', []))
            labels = np.array(training_data.get('labels', []))
            
            if features.size == 0 or labels.size == 0:
                return {'success': False, 'reason': 'No training data provided'}
            
            # Split data for training and validation
            X_train, X_test, y_train, y_test = train_test_split(
                features, labels, test_size=0.2, random_state=42, stratify=labels
            )
            
            if model_type == PredictionModel.RANDOM_FOREST and SKLEARN_AVAILABLE:
                model = await self._train_random_forest(X_train, y_train)
            elif model_type == PredictionModel.NEURAL_NETWORK and TENSORFLOW_AVAILABLE:
                model = await self._train_neural_network(X_train, y_train)
            elif model_type == PredictionModel.ENSEMBLE and SKLEARN_AVAILABLE:
                model = await self._train_ensemble_model(X_train, y_train)
            else:
                return {'success': False, 'reason': f'Model type {model_type} not available'}
            
            # Evaluate model
            performance = await self._evaluate_model(model, X_test, y_test, model_type)
            
            # Store model and performance
            self.models[service_name][model_type.value] = model
            self.model_performance[service_name][model_type.value] = performance
            self.is_trained[service_name][model_type.value] = True
            
            self.logger.info(f"✅ {model_type.value} model trained for {service_name} - Accuracy: {performance.get('accuracy', 0):.3f}")
            
            return {
                'success': True,
                'service_name': service_name,
                'model_type': model_type.value,
                'performance': performance,
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to train prediction model: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _train_random_forest(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train Random Forest model"""
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
        model.fit(X_train, y_train)
        return model
    
    async def _train_neural_network(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train Neural Network model"""
        model = keras.Sequential([
            layers.Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
            layers.Dropout(0.3),
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(16, activation='relu'),
            layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        # Train model
        model.fit(
            X_train, y_train,
            epochs=50,
            batch_size=32,
            validation_split=0.2,
            verbose=0
        )
        
        return model
    
    async def _train_ensemble_model(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train ensemble model combining multiple approaches"""
        from sklearn.ensemble import VotingClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.svm import SVC
        
        # Create ensemble of different models
        rf_model = RandomForestClassifier(n_estimators=50, random_state=42)
        lr_model = LogisticRegression(random_state=42, max_iter=1000)
        svm_model = SVC(probability=True, random_state=42)
        
        ensemble = VotingClassifier(
            estimators=[
                ('rf', rf_model),
                ('lr', lr_model),
                ('svm', svm_model)
            ],
            voting='soft'
        )
        
        ensemble.fit(X_train, y_train)
        return ensemble
    
    async def _evaluate_model(self, model, X_test: np.ndarray, y_test: np.ndarray, 
                            model_type: PredictionModel) -> Dict[str, float]:
        """Evaluate model performance"""
        try:
            if model_type == PredictionModel.NEURAL_NETWORK and TENSORFLOW_AVAILABLE:
                # Neural network evaluation
                predictions = (model.predict(X_test) > 0.5).astype(int).flatten()
                probabilities = model.predict(X_test).flatten()
            else:
                # Scikit-learn model evaluation
                predictions = model.predict(X_test)
                probabilities = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else predictions
            
            # Calculate metrics
            accuracy = np.mean(predictions == y_test)
            
            # Calculate precision, recall, F1 manually
            tp = np.sum((predictions == 1) & (y_test == 1))
            fp = np.sum((predictions == 1) & (y_test == 0))
            fn = np.sum((predictions == 0) & (y_test == 1))
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            return {
                'accuracy': float(accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1),
                'auc_score': float(np.mean(probabilities))  # Simplified AUC approximation
            }
            
        except Exception as e:
            self.logger.error(f"❌ Model evaluation error: {e}")
            return {'accuracy': 0.0, 'precision': 0.0, 'recall': 0.0, 'f1_score': 0.0}
    
    async def predict_service_failures(self, service_name: str, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Predict service failures using trained models"""
        try:
            predictions = {}
            
            # Get feature vector
            feature_extractor = FeatureExtractor()
            features = feature_extractor.extract_features(service_name, current_metrics)
            feature_array = np.array([[
                features.response_time,
                features.error_rate,
                features.throughput,
                features.cpu_usage,
                features.memory_usage,
                features.disk_usage,
                features.network_latency,
                float(features.active_connections),
                float(features.queue_length),
                feature_extractor._encode_circuit_state(features.circuit_state),
                features.dependency_health,
                float(features.time_of_day) / 24.0,
                float(features.day_of_week) / 7.0,
                features.seasonal_factor
            ]])
            
            # Make predictions with all available models
            for model_type, model in self.models[service_name].items():
                if not self.is_trained[service_name][model_type]:
                    continue
                
                try:
                    if model_type == 'neural_network' and TENSORFLOW_AVAILABLE:
                        prediction_prob = float(model.predict(feature_array)[0][0])
                        prediction = prediction_prob > 0.5
                    else:
                        prediction = bool(model.predict(feature_array)[0])
                        prediction_prob = float(model.predict_proba(feature_array)[0][1]) if hasattr(model, 'predict_proba') else (1.0 if prediction else 0.0)
                    
                    # Determine confidence level
                    if prediction_prob >= 0.9:
                        confidence = PredictionConfidence.CRITICAL
                    elif prediction_prob >= 0.7:
                        confidence = PredictionConfidence.HIGH
                    elif prediction_prob >= 0.5:
                        confidence = PredictionConfidence.MEDIUM
                    else:
                        confidence = PredictionConfidence.LOW
                    
                    predictions[model_type] = {
                        'failure_predicted': prediction,
                        'probability': prediction_prob,
                        'confidence': confidence.value,
                        'model_performance': self.model_performance[service_name].get(model_type, {})
                    }
                    
                except Exception as e:
                    self.logger.error(f"❌ Prediction error with {model_type}: {e}")
                    continue
            
            # Ensemble prediction if multiple models available
            if len(predictions) > 1:
                avg_probability = np.mean([p['probability'] for p in predictions.values()])
                ensemble_prediction = avg_probability > 0.5
                
                predictions['ensemble'] = {
                    'failure_predicted': ensemble_prediction,
                    'probability': float(avg_probability),
                    'confidence': self._determine_confidence(avg_probability).value,
                    'models_used': list(predictions.keys())
                }
            
            return {
                'service_name': service_name,
                'predictions': predictions,
                'feature_vector': features.__dict__,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to predict service failures: {e}")
            return {'service_name': service_name, 'error': str(e)}
    
    def _determine_confidence(self, probability: float) -> PredictionConfidence:
        """Determine confidence level from probability"""
        if probability >= 0.9:
            return PredictionConfidence.CRITICAL
        elif probability >= 0.7:
            return PredictionConfidence.HIGH
        elif probability >= 0.5:
            return PredictionConfidence.MEDIUM
        else:
            return PredictionConfidence.LOW


class ActionRecommendationEngine:
    """Recommend proactive actions based on failure predictions"""
    
    def __init__(self):
        self.action_templates: Dict[FailureType, List[ProactiveAction]] = {}
        self.action_history: List[Dict[str, Any]] = []
        self.success_rates: Dict[str, float] = defaultdict(float)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize default action templates
        self._initialize_action_templates()
    
    def _initialize_action_templates(self):
        """Initialize default action templates"""
        # Service failure actions
        self.action_templates[FailureType.SERVICE_FAILURE] = [
            ProactiveAction(
                action_id=str(uuid.uuid4()),
                action_type=ActionType.CIRCUIT_BREAKER_OPEN,
                target_service="",
                priority=9,
                estimated_impact=0.8,
                implementation_complexity=2,
                resource_cost=0.1,
                success_probability=0.9,
                description="Open circuit breaker to prevent cascade failures",
                parameters={"timeout_seconds": 60}
            ),
            ProactiveAction(
                action_id=str(uuid.uuid4()),
                action_type=ActionType.FAILOVER_INITIATE,
                target_service="",
                priority=8,
                estimated_impact=0.7,
                implementation_complexity=4,
                resource_cost=0.5,
                success_probability=0.8,
                description="Initiate failover to backup service instance"
            )
        ]
        
        # Performance degradation actions
        self.action_templates[FailureType.PERFORMANCE_DEGRADATION] = [
            ProactiveAction(
                action_id=str(uuid.uuid4()),
                action_type=ActionType.SCALE_UP,
                target_service="",
                priority=7,
                estimated_impact=0.6,
                implementation_complexity=3,
                resource_cost=0.8,
                success_probability=0.7,
                description="Scale up service instances to handle increased load",
                parameters={"scale_factor": 2, "min_instances": 3}
            ),
            ProactiveAction(
                action_id=str(uuid.uuid4()),
                action_type=ActionType.CACHE_WARM_UP,
                target_service="",
                priority=5,
                estimated_impact=0.4,
                implementation_complexity=2,
                resource_cost=0.2,
                success_probability=0.6,
                description="Warm up caches to improve response times"
            )
        ]
        
        # Resource exhaustion actions
        self.action_templates[FailureType.RESOURCE_EXHAUSTION] = [
            ProactiveAction(
                action_id=str(uuid.uuid4()),
                action_type=ActionType.RESOURCE_CLEANUP,
                target_service="",
                priority=8,
                estimated_impact=0.7,
                implementation_complexity=2,
                resource_cost=0.1,
                success_probability=0.8,
                description="Clean up unused resources and optimize memory usage"
            ),
            ProactiveAction(
                action_id=str(uuid.uuid4()),
                action_type=ActionType.LOAD_BALANCER_ADJUST,
                target_service="",
                priority=6,
                estimated_impact=0.5,
                implementation_complexity=3,
                resource_cost=0.3,
                success_probability=0.7,
                description="Adjust load balancer weights to redistribute traffic"
            )
        ]
    
    async def recommend_proactive_actions(self, prediction_results: Dict[str, Any]) -> List[str]:
        """Recommend proactive actions based on prediction results"""
        try:
            service_name = prediction_results.get('service_name')
            predictions = prediction_results.get('predictions', {})
            
            recommendations = []
            
            # Analyze each prediction
            for model_type, prediction in predictions.items():
                if not prediction.get('failure_predicted', False):
                    continue
                
                probability = prediction.get('probability', 0.0)
                confidence = prediction.get('confidence', 'low')
                
                # Determine failure type based on feature analysis
                failure_type = await self._infer_failure_type(prediction_results)
                
                # Get appropriate actions for this failure type
                action_templates = self.action_templates.get(failure_type, [])
                
                for template in action_templates:
                    # Customize action for this service
                    action = ProactiveAction(
                        action_id=str(uuid.uuid4()),
                        action_type=template.action_type,
                        target_service=service_name,
                        priority=template.priority,
                        estimated_impact=template.estimated_impact * probability,  # Scale by probability
                        implementation_complexity=template.implementation_complexity,
                        resource_cost=template.resource_cost,
                        success_probability=template.success_probability,
                        description=f"{template.description} (Service: {service_name})",
                        parameters=template.parameters.copy()
                    )
                    
                    # Adjust priority based on confidence
                    if confidence == 'critical':
                        action.priority = min(10, action.priority + 2)
                    elif confidence == 'high':
                        action.priority = min(10, action.priority + 1)
                    
                    action_description = f"{action.action_type.value}: {action.description} " \
                                       f"(Priority: {action.priority}, Impact: {action.estimated_impact:.2f})"
                    
                    recommendations.append(action_description)
            
            # Remove duplicates and sort by priority
            unique_recommendations = list(set(recommendations))
            unique_recommendations.sort(key=lambda x: int(x.split('Priority: ')[1].split(',')[0]), reverse=True)
            
            self.logger.info(f"💡 Generated {len(unique_recommendations)} action recommendations for {service_name}")
            return unique_recommendations
            
        except Exception as e:
            self.logger.error(f"❌ Failed to recommend proactive actions: {e}")
            return []
    
    async def _infer_failure_type(self, prediction_results: Dict[str, Any]) -> FailureType:
        """Infer failure type from feature analysis"""
        feature_vector = prediction_results.get('feature_vector', {})
        
        # Simple heuristics to infer failure type
        cpu_usage = feature_vector.get('cpu_usage', 0)
        memory_usage = feature_vector.get('memory_usage', 0)
        error_rate = feature_vector.get('error_rate', 0)
        response_time = feature_vector.get('response_time', 0)
        
        if cpu_usage > 80 or memory_usage > 85:
            return FailureType.RESOURCE_EXHAUSTION
        elif response_time > 5.0:
            return FailureType.PERFORMANCE_DEGRADATION
        elif error_rate > 0.1:
            return FailureType.SERVICE_FAILURE
        else:
            return FailureType.SERVICE_FAILURE  # Default
    
    def record_action_outcome(self, action_id: str, success: bool, impact_metrics: Dict[str, Any]):
        """Record the outcome of a proactive action"""
        self.action_history.append({
            'action_id': action_id,
            'success': success,
            'impact_metrics': impact_metrics,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update success rates
        if action_id in self.success_rates:
            current_rate = self.success_rates[action_id]
            self.success_rates[action_id] = (current_rate + (1.0 if success else 0.0)) / 2
        else:
            self.success_rates[action_id] = 1.0 if success else 0.0
        
        self.logger.info(f"📊 Recorded action outcome: {action_id} ({'✅' if success else '❌'})")


class AIFailurePrediction:
    """
    Enterprise AI failure prediction system with ML models.
    Implements predictive analytics and proactive action recommendations.
    """
    
    def __init__(self):
        """Initialize AI failure prediction system"""
        self.feature_extractor = FeatureExtractor()
        self.anomaly_detector = AnomalyDetector()
        self.failure_predictor = FailurePredictor()
        self.action_engine = ActionRecommendationEngine()
        
        self.prediction_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.model_registry: Dict[str, Dict[str, Any]] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.auto_training_enabled = True
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        self.logger.info("🤖 AI Failure Prediction System initialized - Machine learning ready")
    
    async def train_failure_prediction_models(self, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """Train failure prediction models with ML pipeline"""
        try:
            service_name = training_data.get('service_name')
            if not service_name:
                raise ValueError("Service name required for model training")
            
            results = {}
            
            # Extract features from historical data
            historical_metrics = training_data.get('historical_metrics', [])
            features = []
            labels = []
            
            for record in historical_metrics:
                feature_vector = self.feature_extractor.extract_features(service_name, record['metrics'])
                feature_array = [
                    feature_vector.response_time,
                    feature_vector.error_rate,
                    feature_vector.throughput,
                    feature_vector.cpu_usage,
                    feature_vector.memory_usage,
                    feature_vector.disk_usage,
                    feature_vector.network_latency,
                    float(feature_vector.active_connections),
                    float(feature_vector.queue_length),
                    self.feature_extractor._encode_circuit_state(feature_vector.circuit_state),
                    feature_vector.dependency_health,
                    float(feature_vector.time_of_day) / 24.0,
                    float(feature_vector.day_of_week) / 7.0,
                    feature_vector.seasonal_factor
                ]
                
                features.append(feature_array)
                labels.append(1 if record.get('failure_occurred', False) else 0)
            
            if len(features) < 50:  # Minimum data requirement
                return {
                    'success': False,
                    'reason': f'Insufficient training data: {len(features)} samples (minimum 50 required)'
                }
            
            # Train multiple models
            model_types = training_data.get('model_types', ['RANDOM_FOREST'])
            
            for model_type in model_types:
                try:
                    model_training_data = {
                        'model_type': model_type,
                        'features': features,
                        'labels': labels
                    }
                    
                    result = await self.failure_predictor.train_prediction_model(
                        service_name, model_training_data
                    )
                    
                    results[model_type] = result
                    
                except Exception as e:
                    results[model_type] = {'success': False, 'error': str(e)}
            
            # Train anomaly detector
            feature_matrix = np.array(features)
            anomaly_result = await self.anomaly_detector.train_anomaly_detector(
                service_name, feature_matrix
            )
            
            results['anomaly_detector'] = {'success': anomaly_result}
            
            # Update model registry
            self.model_registry[service_name] = {
                'models_trained': [mt for mt, r in results.items() if r.get('success', False)],
                'training_timestamp': datetime.now().isoformat(),
                'training_samples': len(features),
                'feature_names': self.feature_extractor.get_feature_names()
            }
            
            self.logger.info(f"🎓 ML pipeline training completed for {service_name}: {len([r for r in results.values() if r.get('success', False)])} models trained")
            
            return {
                'service_name': service_name,
                'training_results': results,
                'total_samples': len(features),
                'successful_models': len([r for r in results.values() if r.get('success', False)]),
                'model_registry': self.model_registry[service_name]
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to train failure prediction models: {e}")
            raise
    
    async def predict_service_failures(self, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Predict service failures with ensemble models"""
        try:
            service_name = current_metrics.get('service_name')
            if not service_name:
                raise ValueError("Service name required for failure prediction")
            
            # Make predictions
            prediction_results = await self.failure_predictor.predict_service_failures(
                service_name, current_metrics
            )
            
            # Detect anomalies
            feature_vector = self.feature_extractor.extract_features(service_name, current_metrics)
            feature_array = np.array([[
                feature_vector.response_time,
                feature_vector.error_rate,
                feature_vector.throughput,
                feature_vector.cpu_usage,
                feature_vector.memory_usage,
                feature_vector.disk_usage,
                feature_vector.network_latency,
                float(feature_vector.active_connections),
                float(feature_vector.queue_length),
                self.feature_extractor._encode_circuit_state(feature_vector.circuit_state),
                feature_vector.dependency_health,
                float(feature_vector.time_of_day) / 24.0,
                float(feature_vector.day_of_week) / 7.0,
                feature_vector.seasonal_factor
            ]])
            
            anomaly_results = await self.anomaly_detector.detect_anomalies(service_name, feature_array)
            
            # Combine results
            combined_results = {
                **prediction_results,
                'anomaly_detection': anomaly_results,
                'risk_assessment': await self._assess_overall_risk(prediction_results, anomaly_results)
            }
            
            # Store prediction history
            self.prediction_history[service_name].append({
                'timestamp': datetime.now(),
                'results': combined_results
            })
            
            self.logger.info(f"🔮 Failure prediction completed for {service_name}")
            return combined_results
            
        except Exception as e:
            self.logger.error(f"❌ Failed to predict service failures: {e}")
            raise
    
    async def _assess_overall_risk(self, prediction_results: Dict[str, Any], 
                                 anomaly_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall risk level combining predictions and anomalies"""
        predictions = prediction_results.get('predictions', {})
        
        # Calculate average failure probability
        probabilities = [p.get('probability', 0.0) for p in predictions.values() 
                        if isinstance(p, dict)]
        avg_probability = np.mean(probabilities) if probabilities else 0.0
        
        # Factor in anomaly detection
        anomaly_factor = 0.0
        if anomaly_results.get('anomalies_detected', False):
            anomaly_rate = anomaly_results.get('anomaly_rate', 0.0)
            anomaly_factor = min(0.3, anomaly_rate)  # Cap at 30% additional risk
        
        # Combined risk score
        overall_risk = min(1.0, avg_probability + anomaly_factor)
        
        # Risk level classification
        if overall_risk >= 0.8:
            risk_level = "CRITICAL"
        elif overall_risk >= 0.6:
            risk_level = "HIGH"
        elif overall_risk >= 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            'overall_risk_score': float(overall_risk),
            'risk_level': risk_level,
            'prediction_component': float(avg_probability),
            'anomaly_component': float(anomaly_factor),
            'confidence': 'high' if len(probabilities) > 1 else 'medium'
        }
    
    async def recommend_proactive_actions(self, prediction_results: Dict[str, Any]) -> List[str]:
        """Recommend proactive actions based on failure predictions"""
        try:
            return await self.action_engine.recommend_proactive_actions(prediction_results)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to recommend proactive actions: {e}")
            return []
    
    async def get_prediction_analytics(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive prediction analytics"""
        try:
            if service_name:
                # Single service analytics
                history = list(self.prediction_history.get(service_name, []))
                registry_info = self.model_registry.get(service_name, {})
                
                if not history:
                    return {'error': f'No prediction history for service {service_name}'}
                
                # Calculate analytics
                recent_predictions = history[-10:]  # Last 10 predictions
                risk_scores = [h['results'].get('risk_assessment', {}).get('overall_risk_score', 0.0) 
                              for h in recent_predictions]
                
                return {
                    'service_name': service_name,
                    'total_predictions': len(history),
                    'recent_predictions': len(recent_predictions),
                    'avg_risk_score': float(np.mean(risk_scores)) if risk_scores else 0.0,
                    'max_risk_score': float(np.max(risk_scores)) if risk_scores else 0.0,
                    'trend': self._calculate_trend(risk_scores),
                    'model_info': registry_info,
                    'last_prediction': history[-1]['timestamp'].isoformat() if history else None
                }
            else:
                # System-wide analytics
                total_predictions = sum(len(hist) for hist in self.prediction_history.values())
                trained_services = len(self.model_registry)
                
                return {
                    'total_services_monitored': len(self.prediction_history),
                    'total_predictions_made': total_predictions,
                    'services_with_trained_models': trained_services,
                    'active_monitoring_tasks': len(self.monitoring_tasks),
                    'auto_training_enabled': self.auto_training_enabled,
                    'ml_libraries_available': {
                        'sklearn': SKLEARN_AVAILABLE,
                        'tensorflow': TENSORFLOW_AVAILABLE
                    },
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get prediction analytics: {e}")
            raise
    
    def _calculate_trend(self, risk_scores: List[float]) -> str:
        """Calculate trend from risk scores"""
        if len(risk_scores) < 2:
            return "insufficient_data"
        
        # Simple trend calculation
        recent_avg = np.mean(risk_scores[-3:]) if len(risk_scores) >= 3 else risk_scores[-1]
        older_avg = np.mean(risk_scores[:-3]) if len(risk_scores) >= 6 else np.mean(risk_scores[:-1])
        
        if recent_avg > older_avg * 1.1:
            return "increasing"
        elif recent_avg < older_avg * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    async def start_continuous_monitoring(self, service_configs: Dict[str, Dict[str, Any]]):
        """Start continuous monitoring and prediction for services"""
        for service_name, config in service_configs.items():
            if service_name not in self.monitoring_tasks:
                task = asyncio.create_task(self._continuous_monitoring_loop(service_name, config))
                self.monitoring_tasks[service_name] = task
                self.logger.info(f"📊 Started continuous monitoring for {service_name}")
    
    async def _continuous_monitoring_loop(self, service_name: str, config: Dict[str, Any]):
        """Continuous monitoring loop for service"""
        monitoring_interval = config.get('monitoring_interval_seconds', 60)
        
        while True:
            try:
                # In a real implementation, this would fetch actual metrics
                # For demo purposes, we'll simulate metrics
                simulated_metrics = {
                    'service_name': service_name,
                    'response_time': random.uniform(0.1, 2.0),
                    'error_rate': random.uniform(0.0, 0.1),
                    'cpu_usage': random.uniform(20, 80),
                    'memory_usage': random.uniform(40, 85),
                    'throughput': random.uniform(50, 200)
                }
                
                # Make prediction
                results = await self.predict_service_failures(simulated_metrics)
                
                # Check if proactive actions are needed
                risk_assessment = results.get('risk_assessment', {})
                if risk_assessment.get('risk_level') in ['HIGH', 'CRITICAL']:
                    actions = await self.recommend_proactive_actions(results)
                    if actions:
                        self.logger.warning(f"🚨 High risk detected for {service_name}. Recommended actions: {actions[:2]}")
                
                await asyncio.sleep(monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Monitoring error for {service_name}: {e}")
                await asyncio.sleep(monitoring_interval)
    
    async def stop_continuous_monitoring(self, service_name: Optional[str] = None):
        """Stop continuous monitoring"""
        if service_name:
            if service_name in self.monitoring_tasks:
                self.monitoring_tasks[service_name].cancel()
                try:
                    await self.monitoring_tasks[service_name]
                except asyncio.CancelledError:
                    pass
                del self.monitoring_tasks[service_name]
                self.logger.info(f"⏹️ Stopped monitoring for {service_name}")
        else:
            # Stop all monitoring tasks
            for task in self.monitoring_tasks.values():
                task.cancel()
            
            await asyncio.gather(*self.monitoring_tasks.values(), return_exceptions=True)
            self.monitoring_tasks.clear()
            self.logger.info("⏹️ Stopped all monitoring tasks")
    
    async def cleanup(self):
        """Cleanup AI failure prediction system"""
        try:
            await self.stop_continuous_monitoring()
            
            self.prediction_history.clear()
            self.model_registry.clear()
            
            self.logger.info("🧹 AI Failure Prediction System cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Cleanup error: {e}")


# Global AI failure prediction instance
ai_failure_prediction = AIFailurePrediction()


# Export main classes and functions
__all__ = [
    'AIFailurePrediction',
    'FeatureExtractor',
    'AnomalyDetector',
    'FailurePredictor',
    'ActionRecommendationEngine',
    'PredictionModel',
    'FailureType',
    'PredictionConfidence',
    'ActionType',
    'FeatureVector',
    'FailurePrediction',
    'ProactiveAction',
    'ai_failure_prediction'
]


if __name__ == "__main__":
    # Import for demo
    import random
    
    async def demo():
        """Demo AI failure prediction functionality"""
        prediction_system = AIFailurePrediction()
        
        # Generate sample training data
        training_data = {
            'service_name': 'user-service',
            'model_types': ['RANDOM_FOREST'],
            'historical_metrics': []
        }
        
        # Generate 200 sample records
        for i in range(200):
            failure_occurred = random.random() < 0.1  # 10% failure rate
            
            # Simulate metrics with failure correlation
            if failure_occurred:
                response_time = random.uniform(2.0, 10.0)
                error_rate = random.uniform(0.2, 0.8)
                cpu_usage = random.uniform(80, 100)
            else:
                response_time = random.uniform(0.1, 1.5)
                error_rate = random.uniform(0.0, 0.05)
                cpu_usage = random.uniform(20, 70)
            
            record = {
                'metrics': {
                    'response_time': response_time,
                    'error_rate': error_rate,
                    'cpu_usage': cpu_usage,
                    'memory_usage': random.uniform(30, 80),
                    'throughput': random.uniform(50, 200)
                },
                'failure_occurred': failure_occurred
            }
            
            training_data['historical_metrics'].append(record)
        
        # Train models
        if SKLEARN_AVAILABLE:
            training_result = await prediction_system.train_failure_prediction_models(training_data)
            print(f"Training result: {json.dumps(training_result, indent=2, default=str)}")
        
        # Make prediction
        current_metrics = {
            'service_name': 'user-service',
            'response_time': 5.0,  # High response time
            'error_rate': 0.3,     # High error rate
            'cpu_usage': 85,       # High CPU
            'memory_usage': 70,
            'throughput': 80
        }
        
        prediction_result = await prediction_system.predict_service_failures(current_metrics)
        print(f"Prediction result: {json.dumps(prediction_result, indent=2, default=str)}")
        
        # Get action recommendations
        actions = await prediction_system.recommend_proactive_actions(prediction_result)
        print(f"Recommended actions: {actions}")
        
        # Get analytics
        analytics = await prediction_system.get_prediction_analytics('user-service')
        print(f"Analytics: {json.dumps(analytics, indent=2, default=str)}")
        
        # Cleanup
        await prediction_system.cleanup()
    
    # Run demo
    asyncio.run(demo())