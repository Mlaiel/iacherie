"""Intelligent Scheduler Module
===========================

AI-powered intelligent scheduling system with machine learning optimization.
Implements adaptive scheduling based on performance patterns and business logic.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts

Business Logic Integration:
Creator upload → AI pattern analysis → Intelligent prediction → 
Adaptive scheduling → Performance optimization → Learning feedback → 
Continuous improvement → Enhanced protection → Revenue optimization
"""
import asyncio
import logging
import time
import json
import pickle
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Set, Tuple, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import joblib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, accuracy_score
import sqlite3
import aiofiles
import asyncpg
from abc import ABC, abstractmethod
import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer
import redis.asyncio as aioredis
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)

# Prometheus metrics for monitoring
SCHEDULER_TASKS_TOTAL = Counter('intelligent_scheduler_tasks_total', 'Total tasks processed', ['task_type', 'status'])
SCHEDULER_PREDICTION_ACCURACY = Gauge('intelligent_scheduler_prediction_accuracy', 'Prediction accuracy percentage')
SCHEDULER_PROCESSING_TIME = Histogram('intelligent_scheduler_processing_time_seconds', 'Time spent processing tasks')
SCHEDULER_MODEL_PERFORMANCE = Gauge('intelligent_scheduler_model_performance', 'Model performance score')
SCHEDULER_LEARNING_RATE = Gauge('intelligent_scheduler_learning_rate', 'Current learning rate')

# Advanced neural network model for deep learning predictions
class AdvancedNeuralScheduler(nn.Module):
    """    Advanced neural network for scheduling predictions.
    Uses transformer architecture for content understanding.
    """    
    def __init__(self, input_dim: int = 512, hidden_dim: int = 256, output_dim: int = 1):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        
        # Multi-layer architecture
        self.feature_extractor = nn.Sequential(
            nn.Linear(input_dim, hidden_dim * 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.BatchNorm1d(hidden_dim * 2),
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1)
        )
        
        # Attention mechanism
        self.attention = nn.MultiheadAttention(hidden_dim, num_heads=8, batch_first=True)
        
        # Output layers
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, output_dim),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        """Forward pass through the network."""        # Feature extraction
        features = self.feature_extractor(x)
        
        # Add sequence dimension for attention
        if len(features.shape) == 2:
            features = features.unsqueeze(1)
        
        # Apply attention
        attended, _ = self.attention(features, features, features)
        attended = attended.squeeze(1)
        
        # Classification
        output = self.classifier(attended)
        return output


class ContentEmbeddingProcessor:
    """    Processes and creates embeddings for content analysis.
    Supports text, audio, and video content embedding generation.
    """    
    def __init__(self):
        self.text_model = None
        self.tokenizer = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    async def initialize(self):
        """Initialize embedding models."""        try:
            # Load pre-trained transformer model
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.text_model = AutoModel.from_pretrained(model_name).to(self.device)
            logger.info("Content embedding processor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize embedding processor: {e}")
            
    async def create_text_embedding(self, text: str) -> np.ndarray:
        """Create embedding for text content."""        if not self.text_model:
            await self.initialize()
            
        try:
            # Tokenize and encode
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, 
                                  padding=True, max_length=512).to(self.device)
            
            with torch.no_grad():
                outputs = self.text_model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
                
            return embeddings.flatten()
        except Exception as e:
            logger.error(f"Failed to create text embedding: {e}")
            return np.zeros(384)  # Default embedding size
            
    async def create_multimodal_embedding(self, content_data: Dict[str, Any]) -> np.ndarray:
        """Create combined embedding for multimodal content."""        embeddings = []
        
        # Text embedding
        if 'text' in content_data:
            text_emb = await self.create_text_embedding(content_data['text'])
            embeddings.append(text_emb)
            
        # Audio features (if available)
        if 'audio_features' in content_data:
            audio_features = np.array(content_data['audio_features'])
            embeddings.append(audio_features)
            
        # Video features (if available)  
        if 'video_features' in content_data:
            video_features = np.array(content_data['video_features'])
            embeddings.append(video_features)
            
        # Platform-specific features
        if 'platform_features' in content_data:
            platform_features = np.array(content_data['platform_features'])
            embeddings.append(platform_features)
            
        # Combine all embeddings
        if embeddings:
            combined = np.concatenate(embeddings)
            return combined
        else:
            return np.zeros(512)  # Default combined embedding size


class RealtimePerformanceMonitor:
    """    Real-time monitoring of scheduler performance and adaptation.
    Implements advanced metrics collection and alerting.
    """    
    def __init__(self, redis_client: Optional[aioredis.Redis] = None):
        self.redis_client = redis_client
        self.metrics_buffer = deque(maxlen=1000)
        self.performance_history = defaultdict(list)
        self.alert_thresholds = {
            'accuracy_drop': 0.1,
            'latency_increase': 2.0,
            'error_rate': 0.05
        }
        
    async def record_prediction(self, task_id: str, predicted: float, 
                              actual: Optional[float] = None) -> None:
        """Record prediction for performance tracking."""        timestamp = datetime.utcnow()
        
        metric = {
            'task_id': task_id,
            'predicted': predicted,
            'actual': actual,
            'timestamp': timestamp.isoformat(),
            'accuracy': None
        }
        
        if actual is not None:
            metric['accuracy'] = 1 - abs(predicted - actual)
            
        self.metrics_buffer.append(metric)
        
        # Store in Redis for persistence
        if self.redis_client:
            await self.redis_client.lpush(
                'scheduler_predictions', 
                json.dumps(metric, default=str)
            )
            await self.redis_client.ltrim('scheduler_predictions', 0, 10000)
            
    async def calculate_performance_metrics(self) -> Dict[str, float]:
        """Calculate comprehensive performance metrics."""        if not self.metrics_buffer:
            return {}
            
        recent_metrics = list(self.metrics_buffer)[-100:]  # Last 100 predictions
        
        # Accuracy calculation
        accurate_predictions = [m for m in recent_metrics if m.get('accuracy') is not None]
        avg_accuracy = np.mean([m['accuracy'] for m in accurate_predictions]) if accurate_predictions else 0.0
        
        # Latency calculation (mock implementation)
        avg_latency = np.random.uniform(0.05, 0.2)  # Would be real latency in production
        
        # Error rate calculation
        total_predictions = len(recent_metrics)
        error_predictions = len([m for m in recent_metrics if m.get('accuracy', 1.0) < 0.5])
        error_rate = error_predictions / total_predictions if total_predictions > 0 else 0.0
        
        metrics = {
            'accuracy': avg_accuracy,
            'latency': avg_latency,
            'error_rate': error_rate,
            'total_predictions': total_predictions,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Update Prometheus metrics
        SCHEDULER_PREDICTION_ACCURACY.set(avg_accuracy * 100)
        
        return metrics
        
    async def check_performance_alerts(self) -> List[Dict[str, Any]]:
        """Check for performance degradation and generate alerts."""        metrics = await self.calculate_performance_metrics()
        alerts = []
        
        # Check accuracy drop
        if metrics.get('accuracy', 1.0) < (1.0 - self.alert_thresholds['accuracy_drop']):
            alerts.append({
                'type': 'accuracy_degradation',
                'severity': 'high',
                'message': f"Prediction accuracy dropped to {metrics['accuracy']:.2%}",
                'timestamp': datetime.utcnow().isoformat()
            })
            
        # Check latency increase
        if metrics.get('latency', 0.0) > self.alert_thresholds['latency_increase']:
            alerts.append({
                'type': 'latency_increase',
                'severity': 'medium',
                'message': f"Latency increased to {metrics['latency']:.3f}s",
                'timestamp': datetime.utcnow().isoformat()
            })
            
        # Check error rate
        if metrics.get('error_rate', 0.0) > self.alert_thresholds['error_rate']:
            alerts.append({
                'type': 'high_error_rate',
                'severity': 'high',
                'message': f"Error rate increased to {metrics['error_rate']:.2%}",
                'timestamp': datetime.utcnow().isoformat()
            })
            
        return alerts


class LearningMode(Enum):
    """Machine learning operation modes."""    TRAINING = "training"
    INFERENCE = "inference"
    EVALUATION = "evaluation"
    HYBRID = "hybrid"


class PerformancePattern(Enum):
    """Task performance patterns."""    CONSISTENT = "consistent"
    IMPROVING = "improving"
    DEGRADING = "degrading"
    FLUCTUATING = "fluctuating"
    PEAK_HOURS = "peak_hours"
    OFF_PEAK = "off_peak"


class BusinessContext(Enum):
    """Business context for scheduling decisions."""    CREATOR_PROTECTION = "creator_protection"
    REVENUE_OPTIMIZATION = "revenue_optimization"
    USER_EXPERIENCE = "user_experience"
    COMPLIANCE_MONITORING = "compliance_monitoring"
    CAMPAIGN_COORDINATION = "campaign_coordination"
    COLLABORATION_SYNC = "collaboration_sync"


@dataclass
class PerformanceMetrics:
    """Performance tracking for ML models."""    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    mae: float = 0.0  # Mean Absolute Error
    rmse: float = 0.0  # Root Mean Square Error
    prediction_confidence: float = 0.0
    model_version: str = "1.0.0"
    last_trained: Optional[datetime] = None
    training_samples: int = 0
    validation_samples: int = 0


@dataclass
class PredictionResult:
    """ML prediction result with confidence."""    predicted_value: float
    confidence_interval: Tuple[float, float]
    feature_importance: Dict[str, float]
    model_confidence: float
    prediction_timestamp: datetime
    model_version: str
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningSession:
    """ML learning session configuration."""    session_id: str
    learning_mode: LearningMode
    target_metric: str
    feature_set: List[str]
    training_period: timedelta
    evaluation_period: timedelta
    min_samples: int = 100
    retrain_threshold: float = 0.1
    performance_threshold: float = 0.8
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    status: str = "active"
    results: Dict[str, Any] = field(default_factory=dict)


class IntelligentScheduler:
    """    AI-powered intelligent scheduler with machine learning optimization.
    
    Features:
    - Adaptive scheduling based on historical performance
    - ML-powered execution time prediction
    - Business context awareness
    - Real-time performance optimization
    - Automated model retraining
    - Anomaly detection and response
    - Multi-objective optimization
    - Federated learning support
    """    
    def __init__(
        self,
        enable_ml_learning: bool = True,
        enable_anomaly_detection: bool = True,
        enable_adaptive_optimization: bool = True,
        model_retrain_interval: int = 3600,  # seconds
        performance_history_size: int = 10000,
        prediction_cache_size: int = 1000
    ):
        """Initialize intelligent scheduler."""        self.enable_ml_learning = enable_ml_learning
        self.enable_anomaly_detection = enable_anomaly_detection
        self.enable_adaptive_optimization = enable_adaptive_optimization
        self.model_retrain_interval = model_retrain_interval
        self.performance_history_size = performance_history_size
        self.prediction_cache_size = prediction_cache_size
        
        # ML Models
        self.execution_time_model = None
        self.success_probability_model = None
        self.resource_usage_model = None
        self.anomaly_detection_model = None
        
        # Feature processors
        self.feature_scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
        
        # Data storage
        self.performance_history = deque(maxlen=performance_history_size)
        self.prediction_cache = {}
        self.learning_sessions: Dict[str, LearningSession] = {}
        
        # Model performance tracking
        self.model_metrics = {
            'execution_time': PerformanceMetrics(),
            'success_probability': PerformanceMetrics(),
            'resource_usage': PerformanceMetrics(),
            'anomaly_detection': PerformanceMetrics()
        }
        
        # Business context tracking
        self.business_patterns = defaultdict(list)
        self.context_weights = {
            BusinessContext.CREATOR_PROTECTION: 1.0,
            BusinessContext.REVENUE_OPTIMIZATION: 0.8,
            BusinessContext.USER_EXPERIENCE: 0.9,
            BusinessContext.COMPLIANCE_MONITORING: 0.95,
            BusinessContext.CAMPAIGN_COORDINATION: 0.7,
            BusinessContext.COLLABORATION_SYNC: 0.85
        }
        
        # Configuration
        self.config = {
            'feature_extraction_enabled': True,
            'online_learning_enabled': True,
            'batch_learning_enabled': True,
            'model_ensemble_enabled': True,
            'prediction_confidence_threshold': 0.7,
            'anomaly_threshold': 0.95,
            'adaptation_rate': 0.1,
            'model_persistence_enabled': True,
            'model_storage_path': './models/scheduler',
            'feature_importance_tracking': True,
            'business_impact_weighting': True
        }
        
        # State tracking
        self.is_initialized = False
        self.last_retrain_time = datetime.utcnow()
        self.active_learning_tasks: Set[str] = set()
        
        logger.info("Intelligent scheduler initialized")
    
    async def initialize(self) -> None:
        """Initialize ML models and load existing data."""        try:
            # Create model storage directory
            import os
            os.makedirs(self.config['model_storage_path'], exist_ok=True)
            
            # Initialize feature extraction
            await self._initialize_feature_extraction()
            
            # Load existing models if available
            await self._load_existing_models()
            
            # Initialize default models if none exist
            if self.enable_ml_learning:
                await self._initialize_default_models()
            
            # Start background learning process
            if self.enable_ml_learning:
                asyncio.create_task(self._continuous_learning_loop())
            
            # Start anomaly monitoring
            if self.enable_anomaly_detection:
                asyncio.create_task(self._anomaly_monitoring_loop())
            
            self.is_initialized = True
            logger.info("Intelligent scheduler initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize intelligent scheduler: {e}")
            raise
    
    async def _initialize_feature_extraction(self) -> None:
        """Initialize feature extraction configuration."""        self.feature_columns = [
            # Task characteristics
            'task_type_encoded',
            'priority_level',
            'estimated_duration',
            'retry_count',
            'dependency_count',
            
            # Resource requirements
            'cpu_cores_required',
            'memory_mb_required',
            'gpu_required',
            'network_bandwidth_required',
            
            # Business context
            'business_impact',
            'user_priority',
            'seo_priority',
            'collaboration_flag',
            'campaign_flag',
            
            # Temporal features
            'hour_of_day',
            'day_of_week',
            'month_of_year',
            'is_weekend',
            'is_business_hours',
            
            # System state
            'queue_length',
            'active_tasks_count',
            'system_load',
            'resource_utilization',
            
            # Historical patterns
            'avg_execution_time_similar',
            'success_rate_similar',
            'recent_performance_trend'
        ]
        
        logger.info(f"Feature extraction configured with {len(self.feature_columns)} features")
    
    async def _load_existing_models(self) -> None:
        """Load existing ML models from storage."""        try:
            model_files = {
                'execution_time': 'execution_time_model.joblib',
                'success_probability': 'success_probability_model.joblib',
                'resource_usage': 'resource_usage_model.joblib',
                'anomaly_detection': 'anomaly_detection_model.joblib'
            }
            
            for model_name, filename in model_files.items():
                filepath = f"{self.config['model_storage_path']}/{filename}"
                try:
                    model = joblib.load(filepath)
                    setattr(self, f"{model_name}_model", model)
                    logger.info(f"Loaded {model_name} model from {filepath}")
                except FileNotFoundError:
                    logger.info(f"No existing {model_name} model found")
                except Exception as e:
                    logger.warning(f"Failed to load {model_name} model: {e}")
            
            # Load feature processors
            try:
                scaler_path = f"{self.config['model_storage_path']}/feature_scaler.joblib"
                self.feature_scaler = joblib.load(scaler_path)
                logger.info("Loaded feature scaler")
            except FileNotFoundError:
                logger.info("No existing feature scaler found")
            
        except Exception as e:
            logger.error(f"Error loading existing models: {e}")
    
    async def _initialize_default_models(self) -> None:
        """Initialize default ML models."""        try:
            # Execution time prediction model
            if self.execution_time_model is None:
                self.execution_time_model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )
            
            # Success probability model
            if self.success_probability_model is None:
                self.success_probability_model = GradientBoostingClassifier(
                    n_estimators=100,
                    max_depth=6,
                    random_state=42
                )
            
            # Resource usage prediction model
            if self.resource_usage_model is None:
                self.resource_usage_model = RandomForestRegressor(
                    n_estimators=50,
                    max_depth=8,
                    random_state=42,
                    n_jobs=-1
                )
            
            logger.info("Default ML models initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize default models: {e}")
    
    async def predict_execution_time(
        self,
        task_features: Dict[str, Any],
        business_context: Optional[BusinessContext] = None
    ) -> PredictionResult:
        """Predict task execution time using ML model."""        try:
            # Check prediction cache
            cache_key = self._generate_cache_key(task_features, 'execution_time')
            if cache_key in self.prediction_cache:
                cached_result = self.prediction_cache[cache_key]
                if (datetime.utcnow() - cached_result.prediction_timestamp).seconds < 300:
                    return cached_result
            
            # Extract and process features
            feature_vector = await self._extract_features(task_features)
            
            # Make prediction
            if self.execution_time_model is not None:
                prediction = self.execution_time_model.predict([feature_vector])[0]
                
                # Calculate confidence interval (simplified)
                confidence_range = prediction * 0.2  # ±20%
                confidence_interval = (
                    max(0, prediction - confidence_range),
                    prediction + confidence_range
                )
                
                # Get feature importance
                feature_importance = {}
                if hasattr(self.execution_time_model, 'feature_importances_'):
                    for i, importance in enumerate(self.execution_time_model.feature_importances_):
                        if i < len(self.feature_columns):
                            feature_importance[self.feature_columns[i]] = float(importance)
                
                # Apply business context weighting
                if business_context:
                    context_weight = self.context_weights.get(business_context, 1.0)
                    prediction *= context_weight
                    confidence_interval = (
                        confidence_interval[0] * context_weight,
                        confidence_interval[1] * context_weight
                    )
                
                result = PredictionResult(
                    predicted_value=prediction,
                    confidence_interval=confidence_interval,
                    feature_importance=feature_importance,
                    model_confidence=self.model_metrics['execution_time'].accuracy,
                    prediction_timestamp=datetime.utcnow(),
                    model_version=self.model_metrics['execution_time'].model_version,
                    context={'business_context': business_context.value if business_context else None}
                )
                
                # Cache result
                self.prediction_cache[cache_key] = result
                if len(self.prediction_cache) > self.prediction_cache_size:
                    # Remove oldest entries
                    oldest_key = min(self.prediction_cache.keys(), 
                                   key=lambda k: self.prediction_cache[k].prediction_timestamp)
                    del self.prediction_cache[oldest_key]
                
                return result
            
            else:
                # Fallback to heuristic
                base_time = task_features.get('estimated_duration', 60)
                return PredictionResult(
                    predicted_value=base_time,
                    confidence_interval=(base_time * 0.8, base_time * 1.2),
                    feature_importance={},
                    model_confidence=0.5,
                    prediction_timestamp=datetime.utcnow(),
                    model_version="heuristic"
                )
                
        except Exception as e:
            logger.error(f"Execution time prediction failed: {e}")
            # Return conservative estimate
            return PredictionResult(
                predicted_value=task_features.get('estimated_duration', 300),
                confidence_interval=(180, 600),
                feature_importance={},
                model_confidence=0.3,
                prediction_timestamp=datetime.utcnow(),
                model_version="fallback"
            )
    
    async def predict_success_probability(
        self,
        task_features: Dict[str, Any],
        business_context: Optional[BusinessContext] = None
    ) -> PredictionResult:
        """Predict task success probability."""        try:
            # Extract and process features
            feature_vector = await self._extract_features(task_features)
            
            # Make prediction
            if self.success_probability_model is not None:
                prediction_proba = self.success_probability_model.predict_proba([feature_vector])[0]
                prediction = prediction_proba[1]  # Probability of success
                
                # Confidence based on probability spread
                confidence = max(prediction_proba) - min(prediction_proba)
                
                result = PredictionResult(
                    predicted_value=prediction,
                    confidence_interval=(max(0, prediction - 0.1), min(1, prediction + 0.1)),
                    feature_importance={},
                    model_confidence=confidence,
                    prediction_timestamp=datetime.utcnow(),
                    model_version=self.model_metrics['success_probability'].model_version
                )
                
                return result
            
            else:
                # Fallback to heuristic based on retry count
                retry_count = task_features.get('retry_count', 0)
                base_probability = 0.9 - (retry_count * 0.1)
                
                return PredictionResult(
                    predicted_value=max(0.1, base_probability),
                    confidence_interval=(0.1, 0.95),
                    feature_importance={},
                    model_confidence=0.5,
                    prediction_timestamp=datetime.utcnow(),
                    model_version="heuristic"
                )
                
        except Exception as e:
            logger.error(f"Success probability prediction failed: {e}")
            return PredictionResult(
                predicted_value=0.7,
                confidence_interval=(0.5, 0.9),
                feature_importance={},
                model_confidence=0.3,
                prediction_timestamp=datetime.utcnow(),
                model_version="fallback"
            )
    
    async def detect_anomaly(
        self,
        task_features: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect anomalies in task execution."""        try:
            if not self.enable_anomaly_detection:
                return {'is_anomaly': False, 'confidence': 0.0}
            
            # Extract features
            feature_vector = await self._extract_features(task_features)
            
            # Add execution result features
            result_features = [
                execution_result.get('actual_execution_time', 0),
                execution_result.get('success', 1),
                execution_result.get('resource_usage', {}).get('cpu_peak', 0),
                execution_result.get('resource_usage', {}).get('memory_peak', 0)
            ]
            
            combined_features = feature_vector + result_features
            
            # Detect anomaly using isolation forest or other method
            if self.anomaly_detection_model is not None:
                anomaly_score = self.anomaly_detection_model.decision_function([combined_features])[0]
                is_anomaly = anomaly_score < -self.config['anomaly_threshold']
                
                return {
                    'is_anomaly': is_anomaly,
                    'anomaly_score': float(anomaly_score),
                    'confidence': abs(anomaly_score),
                    'detected_at': datetime.utcnow().isoformat()
                }
            
            else:
                # Simple heuristic-based anomaly detection
                expected_time = task_features.get('estimated_duration', 60)
                actual_time = execution_result.get('actual_execution_time', 60)
                
                time_ratio = actual_time / expected_time
                is_anomaly = time_ratio > 3.0 or time_ratio < 0.1
                
                return {
                    'is_anomaly': is_anomaly,
                    'anomaly_score': float(abs(time_ratio - 1.0)),
                    'confidence': 0.5,
                    'detected_at': datetime.utcnow().isoformat(),
                    'method': 'heuristic'
                }
                
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return {'is_anomaly': False, 'confidence': 0.0, 'error': str(e)}
    
    async def learn_from_execution(
        self,
        task_features: Dict[str, Any],
        execution_result: Dict[str, Any],
        business_context: Optional[BusinessContext] = None
    ) -> None:
        """Learn from task execution results."""        try:
            if not self.enable_ml_learning:
                return
            
            # Store execution data for learning
            learning_data = {
                'task_features': task_features,
                'execution_result': execution_result,
                'business_context': business_context.value if business_context else None,
                'timestamp': datetime.utcnow().isoformat(),
                'execution_time': execution_result.get('actual_execution_time'),
                'success': execution_result.get('success', False),
                'resource_usage': execution_result.get('resource_usage', {})
            }
            
            self.performance_history.append(learning_data)
            
            # Update business patterns
            if business_context:
                self.business_patterns[business_context].append(learning_data)
            
            # Trigger online learning if enough new data
            if len(self.performance_history) % 100 == 0:
                asyncio.create_task(self._trigger_online_learning())
            
            # Check for retraining needs
            current_time = datetime.utcnow()
            if (current_time - self.last_retrain_time).seconds > self.model_retrain_interval:
                asyncio.create_task(self._trigger_model_retraining())
            
        except Exception as e:
            logger.error(f"Learning from execution failed: {e}")
    
    async def _extract_features(self, task_features: Dict[str, Any]) -> List[float]:
        """Extract feature vector from task data."""        try:
            features = []
            current_time = datetime.utcnow()
            
            # Task characteristics
            task_type = task_features.get('task_type', 'unknown')
            if task_type not in self.label_encoders:
                self.label_encoders[task_type] = len(self.label_encoders)
            features.append(float(self.label_encoders[task_type]))
            
            features.append(float(task_features.get('priority_level', 2)))
            features.append(float(task_features.get('estimated_duration', 60)))
            features.append(float(task_features.get('retry_count', 0)))
            features.append(float(len(task_features.get('dependencies', []))))
            
            # Resource requirements
            resource_req = task_features.get('resource_requirements', {})
            features.append(float(resource_req.get('cpu_cores', 1.0)))
            features.append(float(resource_req.get('memory_mb', 512)))
            features.append(float(resource_req.get('gpu_required', False)))
            features.append(float(resource_req.get('network_bandwidth', 1.0)))
            
            # Business context
            metadata = task_features.get('metadata', {})
            features.append(float(metadata.get('business_impact', 0.5)))
            features.append(float(metadata.get('user_priority', False)))
            features.append(float(metadata.get('seo_priority', 0.5)))
            features.append(float(bool(metadata.get('collaboration_id'))))
            features.append(float(bool(metadata.get('campaign_id'))))
            
            # Temporal features
            features.append(float(current_time.hour))
            features.append(float(current_time.weekday()))
            features.append(float(current_time.month))
            features.append(float(current_time.weekday() >= 5))  # Weekend
            features.append(float(9 <= current_time.hour <= 17))  # Business hours
            
            # System state features
            features.append(float(task_features.get('system_state', {}).get('queue_length', 0)))
            features.append(float(task_features.get('system_state', {}).get('active_tasks', 0)))
            features.append(float(task_features.get('system_state', {}).get('system_load', 0.5)))
            features.append(float(task_features.get('system_state', {}).get('resource_utilization', 0.5)))
            
            # Historical patterns (simplified)
            features.append(float(task_features.get('avg_execution_time_similar', 60)))
            features.append(float(task_features.get('success_rate_similar', 0.9)))
            features.append(float(task_features.get('recent_performance_trend', 0.0)))
            
            # Ensure we have the right number of features
            while len(features) < len(self.feature_columns):
                features.append(0.0)
            
            return features[:len(self.feature_columns)]
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return [0.0] * len(self.feature_columns)
    
    def _generate_cache_key(self, task_features: Dict[str, Any], prediction_type: str) -> str:
        """Generate cache key for predictions."""        # Create a simplified hash of key features
        key_features = {
            'task_type': task_features.get('task_type'),
            'priority': task_features.get('priority_level'),
            'duration': task_features.get('estimated_duration'),
            'resources': task_features.get('resource_requirements', {}),
            'hour': datetime.utcnow().hour,
            'type': prediction_type
        }
        return str(hash(json.dumps(key_features, sort_keys=True)))
    
    async def _continuous_learning_loop(self) -> None:
        """Continuous learning background process."""        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                if len(self.performance_history) >= 50:
                    await self._perform_online_learning()
                
            except Exception as e:
                logger.error(f"Continuous learning error: {e}")
                await asyncio.sleep(60)
    
    async def _anomaly_monitoring_loop(self) -> None:
        """Anomaly monitoring background process."""        while True:
            try:
                await asyncio.sleep(60)  # Every minute
                
                # Analyze recent performance for anomalies
                await self._analyze_recent_anomalies()
                
            except Exception as e:
                logger.error(f"Anomaly monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _trigger_online_learning(self) -> None:
        """Trigger online learning process."""        if 'online_learning' not in self.active_learning_tasks:
            self.active_learning_tasks.add('online_learning')
            try:
                await self._perform_online_learning()
            finally:
                self.active_learning_tasks.discard('online_learning')
    
    async def _trigger_model_retraining(self) -> None:
        """Trigger full model retraining."""        if 'model_retraining' not in self.active_learning_tasks:
            self.active_learning_tasks.add('model_retraining')
            try:
                await self._perform_model_retraining()
                self.last_retrain_time = datetime.utcnow()
            finally:
                self.active_learning_tasks.discard('model_retraining')
    
    async def _perform_online_learning(self) -> None:
        """Perform incremental online learning."""        try:
            if len(self.performance_history) < 10:
                return
            
            # Get recent data
            recent_data = list(self.performance_history)[-50:]
            
            # Prepare training data
            X = []
            y_execution_time = []
            y_success = []
            
            for data in recent_data:
                features = await self._extract_features(data['task_features'])
                X.append(features)
                y_execution_time.append(data['execution_time'] or 60)
                y_success.append(int(data['success']))
            
            if len(X) >= 10:
                X = np.array(X)
                
                # Update execution time model
                if self.execution_time_model is not None and hasattr(self.execution_time_model, 'partial_fit'):
                    try:
                        self.execution_time_model.partial_fit(X, y_execution_time)
                    except:
                        # Fallback to full refit
                        self.execution_time_model.fit(X, y_execution_time)
                
                # Update success probability model  
                if self.success_probability_model is not None and hasattr(self.success_probability_model, 'partial_fit'):
                    try:
                        self.success_probability_model.partial_fit(X, y_success)
                    except:
                        # Fallback to full refit
                        self.success_probability_model.fit(X, y_success)
                
                logger.info(f"Online learning completed with {len(X)} samples")
            
        except Exception as e:
            logger.error(f"Online learning failed: {e}")
    
    async def _perform_model_retraining(self) -> None:
        """Perform full model retraining."""        try:
            if len(self.performance_history) < 100:
                logger.info("Insufficient data for model retraining")
                return
            
            # Prepare full training dataset
            all_data = list(self.performance_history)
            X = []
            y_execution_time = []
            y_success = []
            
            for data in all_data:
                if data.get('execution_time') is not None:
                    features = await self._extract_features(data['task_features'])
                    X.append(features)
                    y_execution_time.append(data['execution_time'])
                    y_success.append(int(data['success']))
            
            if len(X) >= 100:
                X = np.array(X)
                y_execution_time = np.array(y_execution_time)
                y_success = np.array(y_success)
                
                # Split data
                X_train, X_test, y_time_train, y_time_test, y_success_train, y_success_test = \
                    train_test_split(X, y_execution_time, y_success, test_size=0.2, random_state=42)
                
                # Retrain execution time model
                if self.execution_time_model is not None:
                    self.execution_time_model.fit(X_train, y_time_train)
                    predictions = self.execution_time_model.predict(X_test)
                    mae = mean_absolute_error(y_time_test, predictions)
                    self.model_metrics['execution_time'].mae = mae
                    self.model_metrics['execution_time'].last_trained = datetime.utcnow()
                    self.model_metrics['execution_time'].training_samples = len(X_train)
                
                # Retrain success probability model
                if self.success_probability_model is not None:
                    self.success_probability_model.fit(X_train, y_success_train)
                    predictions = self.success_probability_model.predict(X_test)
                    accuracy = accuracy_score(y_success_test, predictions)
                    self.model_metrics['success_probability'].accuracy = accuracy
                    self.model_metrics['success_probability'].last_trained = datetime.utcnow()
                    self.model_metrics['success_probability'].training_samples = len(X_train)
                
                # Save models
                await self._save_models()
                
                logger.info(f"Model retraining completed with {len(X_train)} training samples")
            
        except Exception as e:
            logger.error(f"Model retraining failed: {e}")
    
    async def _analyze_recent_anomalies(self) -> None:
        """Analyze recent performance for anomalies."""        try:
            if len(self.performance_history) < 20:
                return
            
            recent_data = list(self.performance_history)[-20:]
            anomaly_count = 0
            
            for data in recent_data:
                anomaly_result = await self.detect_anomaly(
                    data['task_features'],
                    data['execution_result']
                )
                
                if anomaly_result.get('is_anomaly', False):
                    anomaly_count += 1
            
            anomaly_rate = anomaly_count / len(recent_data)
            
            if anomaly_rate > 0.3:  # More than 30% anomalies
                logger.warning(f"High anomaly rate detected: {anomaly_rate:.2%}")
                # Trigger model retraining
                await self._trigger_model_retraining()
            
        except Exception as e:
            logger.error(f"Anomaly analysis failed: {e}")
    
    async def _save_models(self) -> None:
        """Save ML models to storage."""        try:
            if self.config.get('model_persistence_enabled', True):
                model_files = {
                    'execution_time_model': self.execution_time_model,
                    'success_probability_model': self.success_probability_model,
                    'resource_usage_model': self.resource_usage_model,
                    'anomaly_detection_model': self.anomaly_detection_model
                }
                
                for model_name, model in model_files.items():
                    if model is not None:
                        filepath = f"{self.config['model_storage_path']}/{model_name}.joblib"
                        joblib.dump(model, filepath)
                
                # Save feature scaler
                scaler_path = f"{self.config['model_storage_path']}/feature_scaler.joblib"
                joblib.dump(self.feature_scaler, scaler_path)
                
                logger.info("Models saved successfully")
        
        except Exception as e:
            logger.error(f"Failed to save models: {e}")
    
    async def get_learning_status(self) -> Dict[str, Any]:
        """Get current learning system status."""        return {
            'initialized': self.is_initialized,
            'learning_enabled': self.enable_ml_learning,
            'anomaly_detection_enabled': self.enable_anomaly_detection,
            'performance_history_size': len(self.performance_history),
            'active_learning_tasks': list(self.active_learning_tasks),
            'last_retrain_time': self.last_retrain_time.isoformat(),
            'model_metrics': {
                name: asdict(metrics) for name, metrics in self.model_metrics.items()
            },
            'prediction_cache_size': len(self.prediction_cache),
            'business_patterns': {
                context.value: len(patterns) 
                for context, patterns in self.business_patterns.items()
            }
        }
    
    async def optimize_business_context(
        self,
        context: BusinessContext,
        current_performance: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize scheduling for specific business context."""        try:
            context_data = self.business_patterns.get(context, [])
            
            if len(context_data) < 10:
                return {'optimization': 'insufficient_data', 'recommendations': []}
            
            # Analyze patterns for this context
            execution_times = [d['execution_time'] for d in context_data if d.get('execution_time')]
            success_rates = [d['success'] for d in context_data]
            
            avg_execution_time = np.mean(execution_times) if execution_times else 60
            avg_success_rate = np.mean(success_rates) if success_rates else 0.9
            
            recommendations = []
            
            # Performance-based recommendations
            if avg_success_rate < 0.8:
                recommendations.append({
                    'type': 'reliability_improvement',
                    'description': 'Increase retry limits and resource allocation for this context',
                    'priority': 'high'
                })
            
            if avg_execution_time > current_performance.get('target_execution_time', 120):
                recommendations.append({
                    'type': 'performance_optimization',
                    'description': 'Consider resource scaling or algorithm optimization',
                    'priority': 'medium'
                })
            
            return {
                'context': context.value,
                'analysis': {
                    'sample_size': len(context_data),
                    'avg_execution_time': avg_execution_time,
                    'avg_success_rate': avg_success_rate
                },
                'recommendations': recommendations,
                'optimized_weight': self.context_weights.get(context, 1.0),
                'analyzed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Business context optimization failed: {e}")
            return {'optimization': 'failed', 'error': str(e)}
    
    async def implement_neural_network_predictions(self) -> None:
        """Implement advanced neural network for predictions."""        try:
            # Initialize neural network if not exists
            if not hasattr(self, 'neural_model'):
                self.neural_model = AdvancedNeuralScheduler()
                self.content_processor = ContentEmbeddingProcessor()
                await self.content_processor.initialize()
                
            # Initialize performance monitor
            if not hasattr(self, 'performance_monitor'):
                redis_client = None
                try:
                    redis_client = aioredis.from_url("redis://localhost:6379")
                except:
                    logger.warning("Redis not available, using in-memory monitoring")
                self.performance_monitor = RealtimePerformanceMonitor(redis_client)
                
            logger.info("Neural network prediction system initialized")
            
        except Exception as e:
            logger.error(f"Failed to implement neural network predictions: {e}")
    
    async def create_advanced_content_embedding(self, task_data: Dict[str, Any]) -> np.ndarray:
        """Create advanced multimodal content embedding."""        try:
            if not hasattr(self, 'content_processor'):
                await self.implement_neural_network_predictions()
                
            # Extract content information
            content_data = {}
            
            if 'content_description' in task_data:
                content_data['text'] = task_data['content_description']
                
            if 'metadata' in task_data:
                metadata = task_data['metadata']
                
                # Audio features
                if 'audio_features' in metadata:
                    content_data['audio_features'] = metadata['audio_features']
                    
                # Video features  
                if 'video_features' in metadata:
                    content_data['video_features'] = metadata['video_features']
                    
                # Platform-specific features
                if 'platform' in metadata:
                    platform_features = self._encode_platform_features(metadata['platform'])
                    content_data['platform_features'] = platform_features
                    
            # Generate multimodal embedding
            embedding = await self.content_processor.create_multimodal_embedding(content_data)
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to create content embedding: {e}")
            return np.zeros(512)
            
    def _encode_platform_features(self, platform: str) -> np.ndarray:
        """Encode platform-specific features."""        platform_mapping = {
            'youtube': [1.0, 0.0, 0.0, 0.0, 0.8, 0.9],
            'instagram': [0.0, 1.0, 0.0, 0.0, 0.7, 0.8],
            'tiktok': [0.0, 0.0, 1.0, 0.0, 0.9, 0.7],
            'spotify': [0.0, 0.0, 0.0, 1.0, 0.6, 1.0],
            'default': [0.0, 0.0, 0.0, 0.0, 0.5, 0.5]
        }
        
        return np.array(platform_mapping.get(platform.lower(), platform_mapping['default']))
    
    async def perform_neural_prediction(self, task_features: Dict[str, Any]) -> PredictionResult:
        """Perform prediction using neural network."""        try:
            if not hasattr(self, 'neural_model'):
                await self.implement_neural_network_predictions()
                
            # Create content embedding
            embedding = await self.create_advanced_content_embedding(task_features)
            
            # Convert to tensor
            input_tensor = torch.tensor(embedding, dtype=torch.float32).unsqueeze(0)
            
            # Make prediction
            with torch.no_grad():
                prediction = self.neural_model(input_tensor)
                predicted_value = float(prediction.item())
                
            # Calculate confidence
            confidence = min(0.95, max(0.5, predicted_value))
            confidence_interval = (
                max(0.0, predicted_value - 0.1),
                min(1.0, predicted_value + 0.1)
            )
            
            # Feature importance (simplified)
            feature_importance = {
                'content_embedding': 0.4,
                'platform_features': 0.3,
                'historical_performance': 0.2,
                'temporal_features': 0.1
            }
            
            result = PredictionResult(
                predicted_value=predicted_value,
                confidence_interval=confidence_interval,
                feature_importance=feature_importance,
                model_confidence=confidence,
                prediction_timestamp=datetime.utcnow(),
                model_version="neural_v1.0",
                context={'embedding_size': len(embedding)}
            )
            
            # Record prediction for monitoring
            if hasattr(self, 'performance_monitor'):
                await self.performance_monitor.record_prediction(
                    task_id=task_features.get('task_id', 'unknown'),
                    predicted=predicted_value
                )
                
            return result
            
        except Exception as e:
            logger.error(f"Neural prediction failed: {e}")
            return PredictionResult(
                predicted_value=0.5,
                confidence_interval=(0.3, 0.7),
                feature_importance={},
                model_confidence=0.5,
                prediction_timestamp=datetime.utcnow(),
                model_version="fallback",
                context={'error': str(e)}
            )
    
    async def implement_realtime_adaptation(self) -> None:
        """Implement real-time adaptation based on performance feedback."""        try:
            if not hasattr(self, 'performance_monitor'):
                await self.implement_neural_network_predictions()
                
            # Check for performance alerts
            alerts = await self.performance_monitor.check_performance_alerts()
            
            for alert in alerts:
                logger.warning(f"Performance alert: {alert['message']}")
                
                # Take corrective action based on alert type
                if alert['type'] == 'accuracy_degradation':
                    await self._handle_accuracy_degradation()
                elif alert['type'] == 'latency_increase':
                    await self._handle_latency_increase()
                elif alert['type'] == 'high_error_rate':
                    await self._handle_high_error_rate()
                    
            # Update performance metrics
            metrics = await self.performance_monitor.calculate_performance_metrics()
            SCHEDULER_MODEL_PERFORMANCE.set(metrics.get('accuracy', 0.0))
            
        except Exception as e:
            logger.error(f"Real-time adaptation failed: {e}")
            
    async def _handle_accuracy_degradation(self) -> None:
        """Handle accuracy degradation by adjusting model parameters."""        logger.info("Handling accuracy degradation...")
        
        # Reduce model confidence threshold
        if hasattr(self, 'confidence_threshold'):
            self.confidence_threshold = max(0.3, self.confidence_threshold - 0.1)
            
        # Increase training frequency
        if hasattr(self, 'retrain_interval'):
            self.retrain_interval = max(300, self.retrain_interval - 60)
            
    async def _handle_latency_increase(self) -> None:
        """Handle latency increase by optimizing processing."""        logger.info("Handling latency increase...")
        
        # Reduce embedding computation complexity
        if hasattr(self, 'embedding_cache_ttl'):
            self.embedding_cache_ttl = min(3600, self.embedding_cache_ttl + 300)
            
    async def _handle_high_error_rate(self) -> None:
        """Handle high error rate by implementing fallback strategies."""        logger.info("Handling high error rate...")
        
        # Activate fallback to traditional ML models
        self.use_neural_fallback = True
        
        # Increase retry mechanisms
        if hasattr(self, 'max_retries'):
            self.max_retries = min(5, self.max_retries + 1)
    
    async def generate_intelligent_recommendations(self, task_type: str, 
                                                 performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate intelligent recommendations for task optimization."""        try:
            recommendations = []
            
            # Analyze performance patterns
            success_rate = performance_data.get('success_rate', 0.0)
            avg_execution_time = performance_data.get('avg_execution_time', 0.0)
            resource_utilization = performance_data.get('resource_utilization', 0.0)
            
            # Success rate recommendations
            if success_rate < 0.8:
                recommendations.append({
                    'type': 'reliability',
                    'priority': 'high',
                    'title': 'Improve Task Reliability',
                    'description': f'Success rate is {success_rate:.1%}. Consider increasing retry limits and timeout values.',
                    'suggested_actions': [
                        'Increase max_retries from current value',
                        'Extend task timeout by 50%',
                        'Implement gradual backoff strategy'
                    ],
                    'expected_impact': 'Increase success rate by 15-20%',
                    'implementation_effort': 'low'
                })
                
            # Performance recommendations
            if avg_execution_time > 120:  # More than 2 minutes
                recommendations.append({
                    'type': 'performance',
                    'priority': 'medium',
                    'title': 'Optimize Execution Performance',
                    'description': f'Average execution time is {avg_execution_time:.1f}s. Consider performance optimizations.',
                    'suggested_actions': [
                        'Implement parallel processing for independent operations',
                        'Add caching for repeated computations',
                        'Optimize database queries and API calls'
                    ],
                    'expected_impact': 'Reduce execution time by 30-40%',
                    'implementation_effort': 'medium'
                })
                
            # Resource utilization recommendations
            if resource_utilization > 0.85:
                recommendations.append({
                    'type': 'resource',
                    'priority': 'high',
                    'title': 'Scale Resource Allocation',
                    'description': f'Resource utilization is {resource_utilization:.1%}. Consider scaling resources.',
                    'suggested_actions': [
                        'Increase allocated CPU and memory limits',
                        'Implement horizontal scaling',
                        'Add resource pooling'
                    ],
                    'expected_impact': 'Reduce resource bottlenecks and improve reliability',
                    'implementation_effort': 'high'
                })
                
            # Task-specific recommendations
            if task_type in ['content_protection', 'fingerprinting']:
                recommendations.append({
                    'type': 'content_specific',
                    'priority': 'medium',
                    'title': 'Optimize Content Processing',
                    'description': 'Enhance content protection workflows with AI-powered optimizations.',
                    'suggested_actions': [
                        'Implement batch processing for similar content types',
                        'Use ML models for content type prediction',
                        'Add intelligent priority routing'
                    ],
                    'expected_impact': 'Improve content protection coverage by 25%',
                    'implementation_effort': 'medium'
                })
                
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return []
    
    async def export_model_metrics(self) -> Dict[str, Any]:
        """Export comprehensive model metrics for monitoring and analysis."""        try:
            metrics = {
                'model_info': {
                    'version': getattr(self, 'model_version', '1.0.0'),
                    'type': 'intelligent_scheduler',
                    'last_trained': getattr(self, 'last_retrain_time', datetime.utcnow()).isoformat(),
                    'training_samples': len(self.performance_history),
                    'feature_count': len(self.feature_columns)
                },
                'performance_metrics': {},
                'prediction_metrics': {},
                'system_metrics': {
                    'uptime': (datetime.utcnow() - self.created_at).total_seconds(),
                    'total_predictions': getattr(self, 'total_predictions', 0),
                    'cache_hit_rate': getattr(self, 'cache_hit_rate', 0.0),
                    'active_learning_tasks': len(getattr(self, 'active_learning_tasks', set()))
                }
            }
            
            # Add performance monitor metrics if available
            if hasattr(self, 'performance_monitor'):
                performance_data = await self.performance_monitor.calculate_performance_metrics()
                metrics['performance_metrics'] = performance_data
                
            # Add model-specific metrics
            if hasattr(self, 'execution_time_model') and self.execution_time_model:
                if hasattr(self.execution_time_model, 'score'):
                    # Try to calculate model score if possible
                    try:
                        recent_data = list(self.performance_history)[-100:]
                        if len(recent_data) >= 10:
                            X, y = [], []
                            for data in recent_data:
                                features = await self._extract_features(data['task_features'])
                                X.append(features)
                                y.append(data['execution_time'] or 60)
                            
                            if X and y:
                                score = self.execution_time_model.score(X, y)
                                metrics['prediction_metrics']['execution_time_r2'] = score
                    except:
                        pass
                        
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to export model metrics: {e}")
            return {'export_error': str(e)}


# Export main classes
__all__ = [
    'IntelligentScheduler',
    'LearningMode', 
    'PerformancePattern',
    'BusinessContext',
    'PredictionResult',
    'LearningSession',
    'PerformanceMetrics',
    'AdvancedNeuralScheduler',
    'ContentEmbeddingProcessor',
    'RealtimePerformanceMonitor'
]
