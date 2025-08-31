"""
AI-Powered Load Balancer Optimization Engine for IA Influencer Agent Platform

Provides intelligent load balancing optimization using machine learning algorithms
for content protection, fingerprinting, and monetization services with adaptive
traffic management, predictive scaling, and automated performance tuning.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

 WARNING: This code is proprietary and confidential.
Unauthorized copying, distribution, or use without explicit written
permission from Fahed Mlaiel is strictly prohibited and may result
in legal action.
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
import statistics
from collections import defaultdict, deque
import pickle
import aiofiles
from pathlib import Path
import yaml
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from prometheus_client import Counter, Histogram, Gauge
import redis

# ML libraries
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, r2_score
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logger.warning("ML libraries not available, using simplified algorithms")

logger = logging.getLogger(__name__)

# Prometheus metrics for AI optimization
AI_OPTIMIZATIONS_APPLIED = Counter('ai_optimizations_applied_total', 'Total AI optimizations applied', ['type', 'service'])
AI_PREDICTION_ACCURACY = Gauge('ai_prediction_accuracy_ratio', 'AI prediction accuracy', ['model', 'metric'])
AI_OPTIMIZATION_LATENCY = Histogram('ai_optimization_latency_seconds', 'AI optimization processing time')
AI_PERFORMANCE_IMPROVEMENT = Gauge('ai_performance_improvement_ratio', 'Performance improvement from AI optimization')
AI_MODEL_TRAINING_TIME = Histogram('ai_model_training_time_seconds', 'Model training duration')


class OptimizationType(Enum):
    """Types of AI optimizations"""
    TRAFFIC_DISTRIBUTION = "traffic_distribution"
    CAPACITY_SCALING = "capacity_scaling"
    ROUTING_OPTIMIZATION = "routing_optimization"
    RESOURCE_ALLOCATION = "resource_allocation"
    LATENCY_OPTIMIZATION = "latency_optimization"
    COST_OPTIMIZATION = "cost_optimization"


class MLModel(Enum):
    """Machine learning models available"""
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    ENSEMBLE = "ensemble"


@dataclass
class TrainingData:
    """Training data for ML models"""
    timestamp: datetime
    service_name: str
    features: Dict[str, float]  # Input features
    targets: Dict[str, float]   # Target values to predict
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""



        return {
            'timestamp': self.timestamp.isoformat(),
            'service_name': self.service_name,
            'features': self.features,
            'targets': self.targets,
            'metadata': self.metadata
        }


@dataclass
class OptimizationRecommendation:
    """AI optimization recommendation"""
    optimization_type: OptimizationType
    service_name: str
    confidence: float  # 0.0 to 1.0
    expected_improvement: float  # Expected percentage improvement
    recommended_action: str
    parameters: Dict[str, Any]
    reasoning: str
    created_at: datetime
    applied: bool = False
    results: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""



        return {
            'optimization_type': self.optimization_type.value,
            'service_name': self.service_name,
            'confidence': self.confidence,
            'expected_improvement': self.expected_improvement,
            'recommended_action': self.recommended_action,
            'parameters': self.parameters,
            'reasoning': self.reasoning,
            'created_at': self.created_at.isoformat(),
            'applied': self.applied,
            'results': self.results
        }


class FeatureExtractor:
    """Extract features for ML models"""
    
    def __init__(self):
        self.feature_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
    
    def extract_features(self, service_metrics: List[Dict[str, Any]], 
                        timestamp: datetime) -> Dict[str, float]:
        """Extract features from service metrics"""
        features = {}
        
        if not service_metrics:
            return features
        
        # Time-based features
        features['hour_of_day'] = timestamp.hour
        features['day_of_week'] = timestamp.weekday()
        features['is_weekend'] = timestamp.weekday() >= 5
        
        # Recent metrics aggregation
        for metric in service_metrics:
            metric_type = metric.get('metric_type', '')
            value = metric.get('value', 0)
            
            # Current values
            features[f'current_{metric_type}'] = value
            
            # Store in history
            key = f"{metric.get('service_name', '')}_{metric_type}"
            self.feature_history[key].append(value)
            
            # Historical aggregations
            if len(self.feature_history[key]) > 1:
                values = list(self.feature_history[key])
                features[f'avg_{metric_type}_5min'] = np.mean(values[-5:])
                features[f'max_{metric_type}_15min'] = np.max(values[-15:])
                features[f'min_{metric_type}_15min'] = np.min(values[-15:])
                features[f'std_{metric_type}_15min'] = np.std(values[-15:])
                
                # Trend calculation
                if len(values) >= 10:
                    recent = values[-5:]
                    older = values[-10:-5]
                    trend = (np.mean(recent) - np.mean(older)) / (np.mean(older) + 1e-6)
                    features[f'trend_{metric_type}'] = trend
        
        # Cross-metric features
        if 'current_response_time' in features and 'current_throughput' in features:
            features['latency_throughput_ratio'] = features['current_response_time'] / (features['current_throughput'] + 1e-6)
        
        if 'current_cpu_usage' in features and 'current_memory_usage' in features:
            features['resource_utilization'] = (features['current_cpu_usage'] + features['current_memory_usage']) / 2
        
        return features


class PredictiveModel:
    """ML model for performance prediction"""
    
    def __init__(self, model_type: MLModel = MLModel.RANDOM_FOREST):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler() if ML_AVAILABLE else None
        self.feature_names = []
        self.is_trained = False
        self.training_score = 0.0
        self.validation_score = 0.0
        self.last_training_time = None
        
    def _create_model(self) -> Any:
        """Create ML model based on type"""
        if not ML_AVAILABLE:
            return None
        
        if self.model_type == MLModel.LINEAR_REGRESSION:
            return LinearRegression()
        elif self.model_type == MLModel.RANDOM_FOREST:
            return RandomForestRegressor(n_estimators=100, random_state=42)
        elif self.model_type == MLModel.GRADIENT_BOOSTING:
            return GradientBoostingRegressor(n_estimators=100, random_state=42)
        elif self.model_type == MLModel.ENSEMBLE:
            # Simple ensemble of models
            return {
                'rf': RandomForestRegressor(n_estimators=50, random_state=42),
                'gb': GradientBoostingRegressor(n_estimators=50, random_state=42),
                'lr': LinearRegression()
            }
        
        return None
    
    def train(self, training_data: List[TrainingData], target_metric: str) -> bool:
        """Train the model with provided data"""
        if not ML_AVAILABLE or not training_data:
            return False
        
        try:
            start_time = time.time()
            
            # Prepare training data
            features_list = []
            targets_list = []
            
            for data in training_data:
                if target_metric in data.targets:
                    # Convert features dict to list
                    feature_vector = []
                    if not self.feature_names:
                        self.feature_names = sorted(data.features.keys())
                    
                    for feature_name in self.feature_names:
                        feature_vector.append(data.features.get(feature_name, 0.0))
                    
                    features_list.append(feature_vector)
                    targets_list.append(data.targets[target_metric])
            
            if len(features_list) < 10:  # Need minimum training data
                logger.warning(f"Insufficient training data: {len(features_list)} samples")
                return False
            
            X = np.array(features_list)
            y = np.array(targets_list)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Create and train model
            self.model = self._create_model()
            
            if self.model_type == MLModel.ENSEMBLE:
                # Train ensemble
                for model_name, model in self.model.items():
                    model.fit(X_train_scaled, y_train)
                
                # Evaluate ensemble
                predictions = self._predict_ensemble(X_test_scaled)
                self.validation_score = r2_score(y_test, predictions)
                
            else:
                # Train single model
                self.model.fit(X_train_scaled, y_train)
                
                # Evaluate
                train_predictions = self.model.predict(X_train_scaled)
                test_predictions = self.model.predict(X_test_scaled)
                
                self.training_score = r2_score(y_train, train_predictions)
                self.validation_score = r2_score(y_test, test_predictions)
            
            self.is_trained = True
            self.last_training_time = datetime.now()
            
            training_time = time.time() - start_time
            AI_MODEL_TRAINING_TIME.observe(training_time)
            
            logger.info(f"Model trained successfully - Validation R²: {self.validation_score:.3f}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to train model: {e}")
            return False
    
    def _predict_ensemble(self, X: np.ndarray) -> np.ndarray:
        """Make predictions using ensemble model"""
        if not isinstance(self.model, dict):
            return np.array([])
        
        predictions = []
        for model_name, model in self.model.items():
            pred = model.predict(X)
            predictions.append(pred)
        
        # Simple average ensemble
        return np.mean(predictions, axis=0)
    
    def predict(self, features: Dict[str, float]) -> Optional[float]:
        """Make prediction for given features"""
        if not self.is_trained or not ML_AVAILABLE:
            return None
        
        try:
            # Convert features to vector
            feature_vector = []
            for feature_name in self.feature_names:
                feature_vector.append(features.get(feature_name, 0.0))
            
            X = np.array([feature_vector])
            X_scaled = self.scaler.transform(X)
            
            if self.model_type == MLModel.ENSEMBLE:
                prediction = self._predict_ensemble(X_scaled)[0]
            else:
                prediction = self.model.predict(X_scaled)[0]
            
            return float(prediction)
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return None
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance for tree-based models"""
        if not self.is_trained or not ML_AVAILABLE:
            return {}
        
        try:
            if self.model_type in [MLModel.RANDOM_FOREST, MLModel.GRADIENT_BOOSTING]:
                importance = self.model.feature_importances_
                return dict(zip(self.feature_names, importance))
            elif self.model_type == MLModel.ENSEMBLE:
                # Average importance across tree models
                importance_dict = {}
                for model_name, model in self.model.items():
                    if hasattr(model, 'feature_importances_'):
                        for i, feature in enumerate(self.feature_names):
                            importance_dict[feature] = importance_dict.get(feature, 0) + model.feature_importances_[i]
                
                # Normalize
                total_importance = sum(importance_dict.values())
                if total_importance > 0:
                    for feature in importance_dict:
                        importance_dict[feature] /= total_importance
                
                return importance_dict
        except Exception as e:
            logger.error(f"Failed to get feature importance: {e}")
        
        return {}
    
    def save_model(self, filepath: str) -> bool:
        """Save trained model to file"""
        if not self.is_trained or not ML_AVAILABLE:
            return False
        
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'model_type': self.model_type.value,
                'training_score': self.training_score,
                'validation_score': self.validation_score,
                'last_training_time': self.last_training_time.isoformat() if self.last_training_time else None
            }
            
            joblib.dump(model_data, filepath)
            logger.info(f"Model saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False
    
    def load_model(self, filepath: str) -> bool:
        """Load trained model from file"""
        if not ML_AVAILABLE:
            return False
        
        try:
            model_data = joblib.load(filepath)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            self.model_type = MLModel(model_data['model_type'])
            self.training_score = model_data.get('training_score', 0.0)
            self.validation_score = model_data.get('validation_score', 0.0)
            
            last_training_str = model_data.get('last_training_time')
            if last_training_str:
                self.last_training_time = datetime.fromisoformat(last_training_str)
            
            self.is_trained = True
            logger.info(f"Model loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False


class AILoadBalancerOptimizer:
    """
    AI-Powered Load Balancer Optimization Engine
    
    Provides intelligent optimization using machine learning:
    - Predictive traffic analysis
    - Automated capacity scaling
    - Intelligent routing optimization
    - Performance anomaly detection
    - Cost optimization recommendations
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "/etc/ia-influencer/ai-optimizer.yaml"
        self.config = {}
        
        # Core components
        self.feature_extractor = FeatureExtractor()
        self.models: Dict[str, PredictiveModel] = {}
        self.training_data: deque = deque(maxlen=10000)
        
        # Optimization components
        self.optimization_history: deque = deque(maxlen=1000)
        self.active_optimizations: Dict[str, OptimizationRecommendation] = {}
        
        # State management
        self.is_optimizing = False
        self.optimizer_thread = None
        self.last_optimization_time = None
        
        # Performance tracking
        self.baseline_performance = {}
        self.optimization_results = defaultdict(list)
        
        # Redis for distributed optimization
        self.redis_client = None
        
        logger.info("AI Load Balancer Optimizer initialized")
    
    async def initialize(self) -> bool:
        """Initialize AI optimization system"""



        try:
            # Load configuration
            await self._load_configuration()
            
            # Initialize Redis connection
            await self._initialize_redis()
            
            # Initialize ML models
            self._initialize_models()
            
            # Load pre-trained models if available
            await self._load_pretrained_models()
            
            logger.info("AI optimization system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize AI optimizer: {e}")
            return False
    
    async def _load_configuration(self) -> None:
        """Load AI optimizer configuration"""



        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                async with aiofiles.open(config_file, 'r') as f:
                    content = await f.read()
                    self.config = yaml.safe_load(content)
            else:
                self.config = self._get_default_configuration()
            
            logger.info("AI optimizer configuration loaded")
            
        except Exception as e:
            logger.warning(f"Failed to load configuration: {e}, using defaults")
            self.config = self._get_default_configuration()
    
    def _get_default_configuration(self) -> Dict[str, Any]:
        """Get default AI optimizer configuration"""



        return {
            'optimization': {
                'interval_seconds': 300,  # 5 minutes
                'min_confidence_threshold': 0.7,
                'auto_apply_threshold': 0.9,
                'models_to_use': ['random_forest', 'gradient_boosting'],
                'retraining_interval_hours': 24
            },
            'models': {
                'response_time': {
                    'type': 'random_forest',
                    'target_metric': 'response_time',
                    'enabled': True
                },
                'throughput': {
                    'type': 'gradient_boosting',
                    'target_metric': 'throughput',
                    'enabled': True
                },
                'error_rate': {
                    'type': 'ensemble',
                    'target_metric': 'error_rate',
                    'enabled': True
                }
            },
            'optimizations': {
                'traffic_distribution': {
                    'enabled': True,
                    'weight_adjustment_limit': 0.3
                },
                'capacity_scaling': {
                    'enabled': True,
                    'max_scale_factor': 2.0,
                    'min_scale_factor': 0.5
                },
                'routing_optimization': {
                    'enabled': True,
                    'latency_weight': 0.4,
                    'capacity_weight': 0.6
                }
            }
        }
    
    async def _initialize_redis(self) -> None:
        """Initialize Redis connection for distributed optimization"""



        try:
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=1,  # Different DB than monitoring
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established for AI optimization")
            
        except Exception as e:
            logger.warning(f"Redis not available for AI optimization: {e}")
            self.redis_client = None
    
    def _initialize_models(self) -> None:
        """Initialize ML models"""
        models_config = self.config.get('models', {})
        
        for model_name, model_config in models_config.items():
            if not model_config.get('enabled', True):
                continue
            
            model_type_str = model_config.get('type', 'random_forest')
            try:
                model_type = MLModel(model_type_str)
                self.models[model_name] = PredictiveModel(model_type)
                logger.info(f"Initialized {model_type_str} model for {model_name}")
            except ValueError:
                logger.error(f"Invalid model type: {model_type_str}")
    
    async def _load_pretrained_models(self) -> None:
        """Load pre-trained models if available"""
        models_dir = Path("/var/lib/ia-influencer/ai-models")
        models_dir.mkdir(parents=True, exist_ok=True)
        
        for model_name, model in self.models.items():
            model_file = models_dir / f"{model_name}.joblib"
            if model_file.exists():
                success = model.load_model(str(model_file))
                if success:
                    logger.info(f"Loaded pre-trained model: {model_name}")
    
    async def start_optimization(self) -> None:
        """Start AI optimization engine"""
        if self.is_optimizing:
            logger.warning("AI optimization already started")
            return
        
        self.is_optimizing = True
        
        # Start optimization loop
        self.optimizer_thread = threading.Thread(target=self._optimization_loop, daemon=True)
        self.optimizer_thread.start()
        
        logger.info("AI optimization engine started")
    
    def _optimization_loop(self) -> None:
        """Main AI optimization loop"""
        interval = self.config.get('optimization', {}).get('interval_seconds', 300)
        
        while self.is_optimizing:
            try:
                # Collect data and generate recommendations
                asyncio.run(self._run_optimization_cycle())
                
                # Apply high-confidence optimizations
                asyncio.run(self._apply_optimizations())
                
                # Retrain models if needed
                asyncio.run(self._retrain_models_if_needed())
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in AI optimization loop: {e}")
                time.sleep(interval * 2)  # Wait longer on error
    
    async def _run_optimization_cycle(self) -> None:
        """Run one optimization cycle"""



        try:
            start_time = time.time()
            
            # Analyze current performance
            performance_analysis = await self._analyze_current_performance()
            
            # Generate optimization recommendations
            recommendations = await self._generate_recommendations(performance_analysis)
            
            # Store recommendations
            for recommendation in recommendations:
                self.active_optimizations[recommendation.service_name] = recommendation
            
            # Update metrics
            optimization_time = time.time() - start_time
            AI_OPTIMIZATION_LATENCY.observe(optimization_time)
            
            self.last_optimization_time = datetime.now()
            
            logger.info(f"Generated {len(recommendations)} optimization recommendations")
            
        except Exception as e:
            logger.error(f"Failed to run optimization cycle: {e}")
    
    async def _analyze_current_performance(self) -> Dict[str, Any]:
        """Analyze current system performance"""
        analysis = {
            'services': {},
            'overall_performance': 0.0,
            'bottlenecks': [],
            'optimization_opportunities': []
        }
        
        try:
            # Get recent metrics from monitoring system
            services = ['fingerprinting', 'protection', 'monetization', 'ai_agent', 'crawlers']
            
            for service in services:
                service_analysis = await self._analyze_service_performance(service)
                analysis['services'][service] = service_analysis
                
                # Identify bottlenecks
                if service_analysis.get('performance_score', 0) < 0.7:
                    analysis['bottlenecks'].append({
                        'service': service,
                        'issue': service_analysis.get('primary_issue', 'Unknown'),
                        'severity': service_analysis.get('severity', 'medium')
                    })
            
            # Calculate overall performance
            service_scores = [
                analysis['services'][service].get('performance_score', 0)
                for service in services
            ]
            analysis['overall_performance'] = statistics.mean(service_scores) if service_scores else 0.0
            
        except Exception as e:
            logger.error(f"Failed to analyze performance: {e}")
        
        return analysis
    
    async def _analyze_service_performance(self, service_name: str) -> Dict[str, Any]:
        """Analyze performance of specific service"""
        analysis = {
            'performance_score': 0.0,
            'response_time': 0.0,
            'throughput': 0.0,
            'error_rate': 0.0,
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'primary_issue': None,
            'severity': 'low',
            'predictions': {}
        }
        
        try:
            # Simulate getting metrics (in real implementation, get from monitoring)
            current_metrics = self._simulate_service_metrics(service_name)
            
            # Extract features
            features = self.feature_extractor.extract_features([current_metrics], datetime.now())
            
            # Update analysis with current metrics
            analysis.update({
                'response_time': current_metrics.get('response_time', 0.0),
                'throughput': current_metrics.get('throughput', 0.0),
                'error_rate': current_metrics.get('error_rate', 0.0),
                'cpu_usage': current_metrics.get('cpu_usage', 0.0),
                'memory_usage': current_metrics.get('memory_usage', 0.0)
            })
            
            # Calculate performance score
            score = self._calculate_service_performance_score(analysis)
            analysis['performance_score'] = score
            
            # Identify primary issue
            if analysis['response_time'] > 2.0:
                analysis['primary_issue'] = 'high_latency'
                analysis['severity'] = 'high'
            elif analysis['error_rate'] > 0.05:
                analysis['primary_issue'] = 'high_error_rate'
                analysis['severity'] = 'critical'
            elif analysis['cpu_usage'] > 80:
                analysis['primary_issue'] = 'high_cpu_usage'
                analysis['severity'] = 'medium'
            elif analysis['memory_usage'] > 85:
                analysis['primary_issue'] = 'high_memory_usage'
                analysis['severity'] = 'medium'
            elif analysis['throughput'] < 10:
                analysis['primary_issue'] = 'low_throughput'
                analysis['severity'] = 'medium'
            
            # Generate predictions if models are available
            for model_name, model in self.models.items():
                if model.is_trained:
                    prediction = model.predict(features)
                    if prediction is not None:
                        analysis['predictions'][model_name] = prediction
            
        except Exception as e:
            logger.error(f"Failed to analyze service {service_name}: {e}")
        
        return analysis
    
    def _simulate_service_metrics(self, service_name: str) -> Dict[str, Any]:
        """Simulate service metrics for demo purposes"""
        # In real implementation, this would fetch from monitoring system
        base_metrics = {
            'fingerprinting': {'response_time': 1.5, 'throughput': 50, 'error_rate': 0.02},
            'protection': {'response_time': 0.8, 'throughput': 100, 'error_rate': 0.01},
            'monetization': {'response_time': 0.5, 'throughput': 200, 'error_rate': 0.005},
            'ai_agent': {'response_time': 1.2, 'throughput': 80, 'error_rate': 0.015},
            'crawlers': {'response_time': 2.0, 'throughput': 30, 'error_rate': 0.03}
        }
        
        base = base_metrics.get(service_name, {'response_time': 1.0, 'throughput': 100, 'error_rate': 0.01})
        
        # Add some variation
        metrics = {
            'service_name': service_name,
            'metric_type': 'performance',
            'value': 1.0,
            'timestamp': datetime.now().isoformat(),
            'response_time': base['response_time'] * np.random.normal(1.0, 0.1),
            'throughput': base['throughput'] * np.random.normal(1.0, 0.15),
            'error_rate': max(0, base['error_rate'] * np.random.normal(1.0, 0.2)),
            'cpu_usage': np.random.normal(60, 15),
            'memory_usage': np.random.normal(65, 12)
        }
        
        return metrics
    
    def _calculate_service_performance_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate performance score for service"""



        try:
            # Response time score (inverse)
            response_score = max(0, 100 - (analysis['response_time'] * 50))
            
            # Throughput score (normalized)
            throughput_score = min(100, analysis['throughput'])
            
            # Error rate score (inverse)
            error_score = max(0, 100 - (analysis['error_rate'] * 10000))
            
            # Resource usage scores
            cpu_score = max(0, 100 - analysis['cpu_usage'])
            memory_score = max(0, 100 - analysis['memory_usage'])
            
            # Weighted average
            score = (
                response_score * 0.3 +
                throughput_score * 0.25 +
                error_score * 0.25 +
                cpu_score * 0.1 +
                memory_score * 0.1
            ) / 100.0
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"Failed to calculate performance score: {e}")
            return 0.0
    
    async def _generate_recommendations(self, performance_analysis: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Generate AI optimization recommendations"""
        recommendations = []
        
        try:
            for service_name, service_analysis in performance_analysis['services'].items():
                # Generate recommendations based on analysis
                service_recommendations = await self._generate_service_recommendations(
                    service_name, service_analysis
                )
                recommendations.extend(service_recommendations)
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
        
        return recommendations
    
    async def _generate_service_recommendations(self, service_name: str, 
                                              analysis: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Generate recommendations for specific service"""
        recommendations = []
        
        try:
            performance_score = analysis.get('performance_score', 0.0)
            primary_issue = analysis.get('primary_issue')
            
            # Traffic distribution optimization
            if performance_score < 0.8 and analysis.get('response_time', 0) > 1.5:
                recommendations.append(OptimizationRecommendation(
                    optimization_type=OptimizationType.TRAFFIC_DISTRIBUTION,
                    service_name=service_name,
                    confidence=0.8,
                    expected_improvement=15.0,
                    recommended_action="Redistribute traffic to less loaded servers",
                    parameters={
                        'adjustment_factor': 0.2,
                        'target_servers': ['server-1', 'server-3'],
                        'reduce_load_servers': ['server-2']
                    },
                    reasoning=f"High response time ({analysis.get('response_time', 0):.2f}s) indicates uneven load distribution",
                    created_at=datetime.now()
                ))
            
            # Capacity scaling recommendation
            if primary_issue in ['high_cpu_usage', 'high_memory_usage', 'low_throughput']:
                confidence = 0.9 if primary_issue == 'high_cpu_usage' else 0.75
                recommendations.append(OptimizationRecommendation(
                    optimization_type=OptimizationType.CAPACITY_SCALING,
                    service_name=service_name,
                    confidence=confidence,
                    expected_improvement=25.0,
                    recommended_action="Scale up service capacity",
                    parameters={
                        'scale_factor': 1.5,
                        'additional_instances': 1,
                        'resource_allocation': {
                            'cpu': f"{analysis.get('cpu_usage', 0) + 20}%",
                            'memory': f"{analysis.get('memory_usage', 0) + 15}%"
                        }
                    },
                    reasoning=f"Resource constraint detected: {primary_issue}",
                    created_at=datetime.now()
                ))
            
            # Routing optimization
            if analysis.get('error_rate', 0) > 0.02:
                recommendations.append(OptimizationRecommendation(
                    optimization_type=OptimizationType.ROUTING_OPTIMIZATION,
                    service_name=service_name,
                    confidence=0.7,
                    expected_improvement=20.0,
                    recommended_action="Optimize routing to healthier instances",
                    parameters={
                        'health_threshold': 0.95,
                        'failover_strategy': 'immediate',
                        'circuit_breaker_threshold': 0.05
                    },
                    reasoning=f"High error rate ({analysis.get('error_rate', 0):.3f}) suggests routing to unhealthy instances",
                    created_at=datetime.now()
                ))
            
            # Latency optimization
            if analysis.get('response_time', 0) > 2.0:
                recommendations.append(OptimizationRecommendation(
                    optimization_type=OptimizationType.LATENCY_OPTIMIZATION,
                    service_name=service_name,
                    confidence=0.85,
                    expected_improvement=30.0,
                    recommended_action="Enable caching and optimize connection pooling",
                    parameters={
                        'enable_caching': True,
                        'cache_ttl': 300,
                        'connection_pool_size': 50,
                        'keep_alive_timeout': 65
                    },
                    reasoning=f"High response time ({analysis.get('response_time', 0):.2f}s) can be improved with caching",
                    created_at=datetime.now()
                ))
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations for {service_name}: {e}")
        
        return recommendations
    
    async def _apply_optimizations(self) -> None:
        """Apply high-confidence optimizations automatically"""
        auto_apply_threshold = self.config.get('optimization', {}).get('auto_apply_threshold', 0.9)
        
        for service_name, recommendation in list(self.active_optimizations.items()):
            if recommendation.applied or recommendation.confidence < auto_apply_threshold:
                continue
            
            try:
                success = await self._apply_optimization(recommendation)
                if success:
                    recommendation.applied = True
                    AI_OPTIMIZATIONS_APPLIED.labels(
                        type=recommendation.optimization_type.value,
                        service=service_name
                    ).inc()
                    
                    logger.info(f"Applied optimization: {recommendation.recommended_action}")
                
            except Exception as e:
                logger.error(f"Failed to apply optimization for {service_name}: {e}")
    
    async def _apply_optimization(self, recommendation: OptimizationRecommendation) -> bool:
        """Apply specific optimization recommendation"""



        try:
            # This would implement actual optimization logic
            # For demo purposes, we'll simulate the application
            
            optimization_type = recommendation.optimization_type
            parameters = recommendation.parameters
            
            if optimization_type == OptimizationType.TRAFFIC_DISTRIBUTION:
                # Simulate traffic redistribution
                logger.info(f"Redistributing traffic for {recommendation.service_name}")
                # Implementation would update load balancer weights
                
            elif optimization_type == OptimizationType.CAPACITY_SCALING:
                # Simulate capacity scaling
                scale_factor = parameters.get('scale_factor', 1.0)
                logger.info(f"Scaling {recommendation.service_name} by factor {scale_factor}")
                # Implementation would trigger container scaling
                
            elif optimization_type == OptimizationType.ROUTING_OPTIMIZATION:
                # Simulate routing optimization
                logger.info(f"Optimizing routing for {recommendation.service_name}")
                # Implementation would update routing rules
                
            elif optimization_type == OptimizationType.LATENCY_OPTIMIZATION:
                # Simulate latency optimization
                logger.info(f"Optimizing latency for {recommendation.service_name}")
                # Implementation would update caching and connection settings
            
            # Record results
            recommendation.results = {
                'applied_at': datetime.now().isoformat(),
                'success': True,
                'applied_parameters': parameters
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply optimization: {e}")
            recommendation.results = {
                'applied_at': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            }
            return False
    
    async def _retrain_models_if_needed(self) -> None:
        """Retrain ML models if needed"""
        retrain_interval = self.config.get('optimization', {}).get('retraining_interval_hours', 24)
        
        for model_name, model in self.models.items():
            try:
                should_retrain = False
                
                # Check if model needs retraining
                if not model.is_trained:
                    should_retrain = True
                elif model.last_training_time:
                    time_since_training = datetime.now() - model.last_training_time
                    if time_since_training > timedelta(hours=retrain_interval):
                        should_retrain = True
                
                if should_retrain and len(self.training_data) >= 100:
                    logger.info(f"Retraining model: {model_name}")
                    
                    # Prepare training data
                    relevant_data = [
                        data for data in self.training_data
                        if model_name in data.targets
                    ]
                    
                    if len(relevant_data) >= 50:
                        success = model.train(relevant_data, model_name)
                        if success:
                            # Save model
                            model_path = f"/var/lib/ia-influencer/ai-models/{model_name}.joblib"
                            model.save_model(model_path)
                            
                            # Update prediction accuracy metrics
                            AI_PREDICTION_ACCURACY.labels(
                                model=model_name,
                                metric='validation'
                            ).set(model.validation_score)
                
            except Exception as e:
                logger.error(f"Failed to retrain model {model_name}: {e}")
    
    def add_training_data(self, service_name: str, features: Dict[str, float], 
                         targets: Dict[str, float]) -> None:
        """Add training data for ML models"""
        training_data = TrainingData(
            timestamp=datetime.now(),
            service_name=service_name,
            features=features,
            targets=targets
        )
        
        self.training_data.append(training_data)
        
        # Store in Redis if available
        if self.redis_client:
            try:
                key = f"training_data:{service_name}"
                self.redis_client.lpush(key, json.dumps(training_data.to_dict()))
                # Keep only last 1000 entries
                self.redis_client.ltrim(key, 0, 999)
            except Exception as e:
                logger.error(f"Failed to store training data in Redis: {e}")
    
    def get_recommendations(self, service_name: Optional[str] = None) -> List[OptimizationRecommendation]:
        """Get current optimization recommendations"""
        if service_name:
            recommendation = self.active_optimizations.get(service_name)
            return [recommendation] if recommendation else []
        else:
            return list(self.active_optimizations.values())
    
    def get_optimization_history(self) -> List[Dict[str, Any]]:
        """Get optimization history"""



        return [opt.to_dict() for opt in self.optimization_history]
    
    def get_model_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all ML models"""
        status = {}
        
        for model_name, model in self.models.items():
            status[model_name] = {
                'is_trained': model.is_trained,
                'model_type': model.model_type.value,
                'training_score': model.training_score,
                'validation_score': model.validation_score,
                'last_training_time': model.last_training_time.isoformat() if model.last_training_time else None,
                'feature_count': len(model.feature_names),
                'feature_importance': model.get_feature_importance()
            }
        
        return status
    
    async def stop_optimization(self) -> None:
        """Stop AI optimization engine"""
        self.is_optimizing = False
        
        if self.optimizer_thread and self.optimizer_thread.is_alive():
            self.optimizer_thread.join(timeout=10)
        
        logger.info("AI optimization engine stopped")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of AI optimizer"""



        return {
            'is_optimizing': self.is_optimizing,
            'ml_available': ML_AVAILABLE,
            'models_trained': sum(1 for model in self.models.values() if model.is_trained),
            'total_models': len(self.models),
            'training_data_size': len(self.training_data),
            'active_optimizations': len(self.active_optimizations),
            'optimization_history_size': len(self.optimization_history),
            'last_optimization_time': self.last_optimization_time.isoformat() if self.last_optimization_time else None,
            'redis_available': self.redis_client is not None,
            'config_loaded': bool(self.config),
            'timestamp': datetime.now().isoformat()
        }


async def main():
    """Demo function for AI optimization"""
    optimizer = AILoadBalancerOptimizer()
    
    try:
        # Initialize optimizer
        await optimizer.initialize()
        
        # Add some training data
        for i in range(100):
            features = {
                'current_response_time': np.random.normal(1.0, 0.3),
                'current_throughput': np.random.normal(100, 20),
                'current_cpu_usage': np.random.normal(60, 15),
                'current_memory_usage': np.random.normal(65, 12),
                'hour_of_day': np.random.randint(0, 24),
                'day_of_week': np.random.randint(0, 7)
            }
            
            targets = {
                'response_time': features['current_response_time'] * 1.1,
                'throughput': features['current_throughput'] * 0.95,
                'error_rate': np.random.normal(0.01, 0.005)
            }
            
            optimizer.add_training_data('test_service', features, targets)
        
        # Start optimization
        await optimizer.start_optimization()
        
        print("AI optimization started. Press Ctrl+C to stop...")
        
        # Run for demo
        for i in range(5):
            await asyncio.sleep(60)  # Wait 1 minute
            
            # Print status
            status = await optimizer.get_status()
            print(f"Optimization cycle {i+1}:")
            print(f"  Models trained: {status['models_trained']}/{status['total_models']}")
            print(f"  Active optimizations: {status['active_optimizations']}")
            print(f"  Training data: {status['training_data_size']} samples")
            
            # Print recommendations
            recommendations = optimizer.get_recommendations()
            for rec in recommendations:
                print(f"  Recommendation: {rec.recommended_action} (confidence: {rec.confidence:.2f})")
            
            print("-" * 60)
        
    except KeyboardInterrupt:
        print("Stopping AI optimization...")
    finally:
        await optimizer.stop_optimization()


if __name__ == "__main__":
    asyncio.run(main())
