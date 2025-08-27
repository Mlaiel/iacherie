"""
AI Observability Module - Advanced AI/ML Model Monitoring

Provides comprehensive monitoring and observability for AI/ML models
including performance tracking, bias detection, model drift analysis,
explainability monitoring, and model lifecycle management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL / LEGAL WARNING ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
import time
import threading
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Tuple, Set, Union
from uuid import uuid4
import warnings
import hashlib
import pickle

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)

# AI/ML specific imports
try:
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    from sklearn.preprocessing import LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import IsolationForest
    from sklearn.decomposition import PCA
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    import tensorflow as tf
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False

try:
    import torch
    HAS_PYTORCH = True
except ImportError:
    HAS_PYTORCH = False


class ModelType(Enum):
    """Types of AI/ML models"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    RECOMMENDATION = "recommendation"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    CONTENT_PROTECTION = "content_protection"
    FINGERPRINTING = "fingerprinting"
    COPYRIGHT_DETECTION = "copyright_detection"
    SIMILARITY_MATCHING = "similarity_matching"


class ModelFramework(Enum):
    """AI/ML frameworks"""
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"
    SCIKIT_LEARN = "scikit_learn"
    XGBOOST = "xgboost"
    HUGGING_FACE = "hugging_face"
    CUSTOM = "custom"
    ONNX = "onnx"
    TENSORRT = "tensorrt"


class ModelStatus(Enum):
    """Model deployment status"""
    TRAINING = "training"
    VALIDATION = "validation"
    DEPLOYED = "deployed"
    DEPRECATED = "deprecated"
    FAILED = "failed"
    MAINTENANCE = "maintenance"


class DriftType(Enum):
    """Types of model drift"""
    DATA_DRIFT = "data_drift"
    CONCEPT_DRIFT = "concept_drift"
    PREDICTION_DRIFT = "prediction_drift"
    FEATURE_DRIFT = "feature_drift"
    LABEL_DRIFT = "label_drift"


class BiasType(Enum):
    """Types of bias in AI models"""
    DEMOGRAPHIC_PARITY = "demographic_parity"
    EQUALIZED_ODDS = "equalized_odds"
    STATISTICAL_PARITY = "statistical_parity"
    INDIVIDUAL_FAIRNESS = "individual_fairness"
    CALIBRATION = "calibration"
    TREATMENT_EQUALITY = "treatment_equality"


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ModelMetrics:
    """Model performance metrics"""
    model_id: str
    model_name: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Classification metrics
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    auc_roc: Optional[float] = None
    
    # Regression metrics
    mse: Optional[float] = None
    mae: Optional[float] = None
    r2_score: Optional[float] = None
    rmse: Optional[float] = None
    
    # General metrics
    latency_ms: float = 0.0
    throughput_rps: float = 0.0
    error_rate: float = 0.0
    confidence_score: Optional[float] = None
    
    # Resource metrics
    cpu_usage: float = 0.0
    memory_usage_mb: float = 0.0
    gpu_usage: Optional[float] = None
    gpu_memory_mb: Optional[float] = None
    
    # Custom metrics
    custom_metrics: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result
    
    def get_performance_score(self) -> float:
        """Calculate overall performance score (0-1)"""
        scores = []
        
        if self.accuracy is not None:
            scores.append(self.accuracy)
        if self.f1_score is not None:
            scores.append(self.f1_score)
        if self.r2_score is not None:
            scores.append(max(0, self.r2_score))  # R2 can be negative
        
        # Penalize high latency and error rate
        latency_score = max(0, 1 - (self.latency_ms / 5000))  # Normalize to 5s max
        error_score = max(0, 1 - self.error_rate)
        
        scores.extend([latency_score, error_score])
        
        return sum(scores) / len(scores) if scores else 0.0


@dataclass
class DriftDetectionResult:
    """Result of drift detection analysis"""
    model_id: str
    drift_type: DriftType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Drift scores (0-1, higher = more drift)
    drift_score: float = 0.0
    threshold: float = 0.1
    is_drifting: bool = False
    
    # Statistical measures
    p_value: Optional[float] = None
    test_statistic: Optional[float] = None
    confidence_interval: Optional[Tuple[float, float]] = None
    
    # Detailed analysis
    affected_features: List[str] = field(default_factory=list)
    drift_magnitude: float = 0.0
    drift_direction: str = ""  # "increase", "decrease", "mixed"
    
    # Recommendations
    recommended_actions: List[str] = field(default_factory=list)
    severity: AlertSeverity = AlertSeverity.LOW
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['drift_type'] = self.drift_type.value
        result['timestamp'] = self.timestamp.isoformat()
        result['severity'] = self.severity.value
        return result


@dataclass  
class BiasDetectionResult:
    """Result of bias detection analysis"""
    model_id: str
    bias_type: BiasType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Bias scores (0-1, higher = more biased)
    bias_score: float = 0.0
    threshold: float = 0.2
    is_biased: bool = False
    
    # Protected attributes analyzed
    protected_attributes: List[str] = field(default_factory=list)
    affected_groups: Dict[str, float] = field(default_factory=dict)
    
    # Statistical measures
    statistical_significance: Optional[float] = None
    effect_size: Optional[float] = None
    
    # Detailed analysis
    group_performance: Dict[str, Dict[str, float]] = field(default_factory=dict)
    disparity_ratios: Dict[str, float] = field(default_factory=dict)
    
    # Recommendations
    recommended_mitigations: List[str] = field(default_factory=list)
    severity: AlertSeverity = AlertSeverity.MEDIUM
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['bias_type'] = self.bias_type.value
        result['timestamp'] = self.timestamp.isoformat()
        result['severity'] = self.severity.value
        return result


@dataclass
class ModelExplainabilityResult:
    """Result of model explainability analysis"""
    model_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Feature importance
    feature_importance: Dict[str, float] = field(default_factory=dict)
    global_explanations: Dict[str, Any] = field(default_factory=dict)
    
    # Instance-level explanations
    local_explanations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Explanation quality metrics
    explanation_quality: float = 0.0
    interpretability_score: float = 0.0
    consistency_score: float = 0.0
    
    # Stakeholder-specific explanations
    technical_explanation: str = ""
    business_explanation: str = ""
    regulatory_explanation: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result


class BaseModelMonitor(ABC):
    """Abstract base class for model monitors"""
    
    def __init__(self, model_id: str, model_name: str, model_type: ModelType):
        self.model_id = model_id
        self.model_name = model_name
        self.model_type = model_type
        self.logger = logging.getLogger(f"ai_observability.monitor.{model_id}")
        self.metrics_history: deque = deque(maxlen=10000)
        self.last_update = datetime.utcnow()
        
    @abstractmethod
    async def collect_metrics(self) -> ModelMetrics:
        """Collect model performance metrics"""
        pass
    
    @abstractmethod
    async def detect_drift(self, reference_data: np.ndarray, 
                          current_data: np.ndarray) -> List[DriftDetectionResult]:
        """Detect model drift"""
        pass
    
    @abstractmethod
    async def detect_bias(self, predictions: np.ndarray, 
                         ground_truth: np.ndarray,
                         protected_attributes: np.ndarray) -> List[BiasDetectionResult]:
        """Detect model bias"""
        pass


class ContentProtectionModelMonitor(BaseModelMonitor):
    """Specialized monitor for content protection models"""
    
    def __init__(self, model_id: str, model_name: str, endpoint_url: str = None):
        super().__init__(model_id, model_name, ModelType.CONTENT_PROTECTION)
        self.endpoint_url = endpoint_url
        self.protection_accuracy_threshold = 0.95
        self.false_positive_threshold = 0.05
        self.processing_time_threshold = 2000  # ms
        
    async def collect_metrics(self) -> ModelMetrics:
        """Collect content protection model metrics"""
        start_time = time.time()
        
        # Simulate or collect real metrics
        metrics = ModelMetrics(
            model_id=self.model_id,
            model_name=self.model_name,
            timestamp=datetime.utcnow()
        )
        
        # Test model performance with sample data
        if self.endpoint_url:
            try:
                import requests
                
                # Test with sample content
                test_samples = [
                    {"content": "Original music composition test"},
                    {"content": "Copyright protected content test"},
                    {"content": "Public domain content test"}
                ]
                
                correct_predictions = 0
                total_predictions = len(test_samples)
                total_latency = 0
                
                for sample in test_samples:
                    sample_start = time.time()
                    
                    response = requests.post(
                        self.endpoint_url,
                        json=sample,
                        timeout=10
                    )
                    
                    latency = (time.time() - sample_start) * 1000
                    total_latency += latency
                    
                    if response.status_code == 200:
                        result = response.json()
                        # Evaluate prediction accuracy (simplified)
                        if "protection_score" in result:
                            if result["protection_score"] > 0.8:
                                correct_predictions += 1
                    
                metrics.accuracy = correct_predictions / total_predictions
                metrics.latency_ms = total_latency / total_predictions
                metrics.error_rate = 0.0 if correct_predictions == total_predictions else 0.1
                
            except Exception as e:
                self.logger.error(f"Error collecting metrics from endpoint: {str(e)}")
                metrics.error_rate = 1.0
        
        # Simulate additional metrics
        metrics.precision = np.random.uniform(0.90, 0.98)
        metrics.recall = np.random.uniform(0.88, 0.96)
        metrics.f1_score = 2 * (metrics.precision * metrics.recall) / (metrics.precision + metrics.recall)
        metrics.confidence_score = np.random.uniform(0.85, 0.95)
        
        # Resource usage
        import psutil
        metrics.cpu_usage = psutil.cpu_percent()
        metrics.memory_usage_mb = psutil.virtual_memory().used / (1024 * 1024)
        
        # Custom metrics for content protection
        metrics.custom_metrics = {
            "fingerprint_match_rate": np.random.uniform(0.92, 0.98),
            "copyright_detection_rate": np.random.uniform(0.89, 0.95),
            "false_positive_rate": np.random.uniform(0.02, 0.08),
            "content_similarity_accuracy": np.random.uniform(0.93, 0.97),
            "processing_queue_size": np.random.randint(50, 200),
            "model_confidence_distribution": np.random.uniform(0.8, 0.95)
        }
        
        # Store in history
        self.metrics_history.append(metrics)
        self.last_update = datetime.utcnow()
        
        return metrics
    
    async def detect_drift(self, reference_data: np.ndarray, 
                          current_data: np.ndarray) -> List[DriftDetectionResult]:
        """Detect drift in content protection models"""
        results = []
        
        if not HAS_SKLEARN:
            self.logger.warning("scikit-learn not available, skipping drift detection")
            return results
        
        try:
            from scipy import stats
            
            # Data drift detection using KS test
            if reference_data.shape[1] == current_data.shape[1]:
                drift_scores = []
                affected_features = []
                
                for i in range(reference_data.shape[1]):
                    ref_feature = reference_data[:, i]
                    cur_feature = current_data[:, i]
                    
                    # Kolmogorov-Smirnov test
                    ks_stat, p_value = stats.ks_2samp(ref_feature, cur_feature)
                    
                    if p_value < 0.05:  # Significant drift
                        drift_scores.append(ks_stat)
                        affected_features.append(f"feature_{i}")
                
                if drift_scores:
                    avg_drift_score = np.mean(drift_scores)
                    
                    result = DriftDetectionResult(
                        model_id=self.model_id,
                        drift_type=DriftType.DATA_DRIFT,
                        drift_score=avg_drift_score,
                        threshold=0.1,
                        is_drifting=avg_drift_score > 0.1,
                        affected_features=affected_features,
                        drift_magnitude=avg_drift_score,
                        drift_direction="mixed",
                        recommended_actions=[
                            "Retrain model with recent data",
                            "Update feature preprocessing",
                            "Review data collection pipeline"
                        ],
                        severity=AlertSeverity.HIGH if avg_drift_score > 0.2 else AlertSeverity.MEDIUM
                    )
                    
                    results.append(result)
            
            # Prediction drift detection (comparing prediction distributions)
            if len(self.metrics_history) > 50:
                recent_accuracy = [m.accuracy for m in list(self.metrics_history)[-20:] if m.accuracy]
                historical_accuracy = [m.accuracy for m in list(self.metrics_history)[-50:-20] if m.accuracy]
                
                if recent_accuracy and historical_accuracy:
                    t_stat, p_value = stats.ttest_ind(recent_accuracy, historical_accuracy)
                    
                    if p_value < 0.05:
                        drift_score = abs(np.mean(recent_accuracy) - np.mean(historical_accuracy))
                        
                        result = DriftDetectionResult(
                            model_id=self.model_id,
                            drift_type=DriftType.PREDICTION_DRIFT,
                            drift_score=drift_score,
                            threshold=0.05,
                            is_drifting=drift_score > 0.05,
                            p_value=p_value,
                            test_statistic=t_stat,
                            drift_magnitude=drift_score,
                            drift_direction="decrease" if np.mean(recent_accuracy) < np.mean(historical_accuracy) else "increase",
                            recommended_actions=[
                                "Investigate model performance degradation",
                                "Check for data quality issues",
                                "Consider model retraining"
                            ],
                            severity=AlertSeverity.CRITICAL if drift_score > 0.1 else AlertSeverity.HIGH
                        )
                        
                        results.append(result)
            
        except Exception as e:
            self.logger.error(f"Error in drift detection: {str(e)}")
        
        return results
    
    async def detect_bias(self, predictions: np.ndarray, 
                         ground_truth: np.ndarray,
                         protected_attributes: np.ndarray) -> List[BiasDetectionResult]:
        """Detect bias in content protection models"""
        results = []
        
        if not HAS_SKLEARN:
            self.logger.warning("scikit-learn not available, skipping bias detection")
            return results
        
        try:
            # Analyze bias across different content types or creator demographics
            unique_groups = np.unique(protected_attributes)
            
            if len(unique_groups) < 2:
                return results
            
            group_performance = {}
            disparity_ratios = {}
            
            # Calculate performance metrics for each group
            for group in unique_groups:
                group_mask = protected_attributes == group
                group_pred = predictions[group_mask]
                group_truth = ground_truth[group_mask]
                
                if len(group_pred) > 0:
                    accuracy = accuracy_score(group_truth, group_pred > 0.5)
                    precision = precision_score(group_truth, group_pred > 0.5, average='weighted', zero_division=0)
                    recall = recall_score(group_truth, group_pred > 0.5, average='weighted', zero_division=0)
                    
                    group_performance[str(group)] = {
                        "accuracy": accuracy,
                        "precision": precision,
                        "recall": recall,
                        "sample_size": len(group_pred)
                    }
            
            # Calculate disparity ratios (demographic parity)
            if len(group_performance) >= 2:
                group_names = list(group_performance.keys())
                reference_group = group_names[0]
                
                for group_name in group_names[1:]:
                    ref_accuracy = group_performance[reference_group]["accuracy"]
                    group_accuracy = group_performance[group_name]["accuracy"]
                    
                    if ref_accuracy > 0:
                        disparity_ratio = group_accuracy / ref_accuracy
                        disparity_ratios[f"{group_name}_vs_{reference_group}"] = disparity_ratio
                
                # Identify significant bias
                max_disparity = max(abs(1 - ratio) for ratio in disparity_ratios.values()) if disparity_ratios else 0
                
                if max_disparity > 0.1:  # More than 10% disparity
                    result = BiasDetectionResult(
                        model_id=self.model_id,
                        bias_type=BiasType.DEMOGRAPHIC_PARITY,
                        bias_score=max_disparity,
                        threshold=0.1,
                        is_biased=max_disparity > 0.1,
                        protected_attributes=["content_creator_type"],
                        group_performance=group_performance,
                        disparity_ratios=disparity_ratios,
                        recommended_mitigations=[
                            "Balance training data across creator types",
                            "Apply fairness constraints during training",
                            "Implement bias correction in predictions",
                            "Monitor ongoing performance by group"
                        ],
                        severity=AlertSeverity.CRITICAL if max_disparity > 0.2 else AlertSeverity.HIGH
                    )
                    
                    results.append(result)
        
        except Exception as e:
            self.logger.error(f"Error in bias detection: {str(e)}")
        
        return results


class FingerprintingModelMonitor(BaseModelMonitor):
    """Specialized monitor for fingerprinting models"""
    
    def __init__(self, model_id: str, model_name: str):
        super().__init__(model_id, model_name, ModelType.FINGERPRINTING)
        self.similarity_threshold = 0.8
        self.processing_time_threshold = 1000  # ms
        
    async def collect_metrics(self) -> ModelMetrics:
        """Collect fingerprinting model metrics"""
        metrics = ModelMetrics(
            model_id=self.model_id,
            model_name=self.model_name,
            timestamp=datetime.utcnow()
        )
        
        # Simulate fingerprinting-specific metrics
        metrics.accuracy = np.random.uniform(0.92, 0.98)
        metrics.precision = np.random.uniform(0.90, 0.97)
        metrics.recall = np.random.uniform(0.88, 0.96)
        metrics.f1_score = 2 * (metrics.precision * metrics.recall) / (metrics.precision + metrics.recall)
        metrics.latency_ms = np.random.uniform(800, 1200)
        metrics.error_rate = np.random.uniform(0.01, 0.05)
        
        # Resource usage
        import psutil
        metrics.cpu_usage = psutil.cpu_percent()
        metrics.memory_usage_mb = psutil.virtual_memory().used / (1024 * 1024)
        
        # Custom fingerprinting metrics
        metrics.custom_metrics = {
            "fingerprint_generation_time_ms": np.random.uniform(300, 800),
            "fingerprint_match_accuracy": np.random.uniform(0.94, 0.99),
            "duplicate_detection_rate": np.random.uniform(0.91, 0.97),
            "hash_collision_rate": np.random.uniform(0.001, 0.01),
            "feature_extraction_time_ms": np.random.uniform(200, 500),
            "similarity_computation_time_ms": np.random.uniform(100, 300)
        }
        
        self.metrics_history.append(metrics)
        return metrics
    
    async def detect_drift(self, reference_data: np.ndarray, 
                          current_data: np.ndarray) -> List[DriftDetectionResult]:
        """Detect drift in fingerprinting models"""
        # Implementation similar to ContentProtectionModelMonitor
        # but with fingerprinting-specific considerations
        results = []
        
        if not HAS_SKLEARN:
            return results
        
        try:
            # Feature drift detection for audio/visual features
            if reference_data.shape == current_data.shape:
                from scipy.spatial.distance import cosine
                
                # Compare feature distributions
                ref_mean = np.mean(reference_data, axis=0)
                cur_mean = np.mean(current_data, axis=0)
                
                # Cosine similarity between mean feature vectors
                similarity = 1 - cosine(ref_mean, cur_mean)
                drift_score = 1 - similarity
                
                if drift_score > 0.1:
                    result = DriftDetectionResult(
                        model_id=self.model_id,
                        drift_type=DriftType.FEATURE_DRIFT,
                        drift_score=drift_score,
                        threshold=0.1,
                        is_drifting=True,
                        drift_magnitude=drift_score,
                        drift_direction="feature_distribution_shift",
                        recommended_actions=[
                            "Retrain fingerprinting model",
                            "Update feature extraction pipeline",
                            "Validate audio/visual preprocessing"
                        ],
                        severity=AlertSeverity.HIGH
                    )
                    results.append(result)
        
        except Exception as e:
            self.logger.error(f"Error in fingerprinting drift detection: {str(e)}")
        
        return results
    
    async def detect_bias(self, predictions: np.ndarray,
                         ground_truth: np.ndarray, 
                         protected_attributes: np.ndarray) -> List[BiasDetectionResult]:
        """Detect bias in fingerprinting models"""
        # Fingerprinting models might show bias based on content type, quality, or format
        results = []
        
        # Implementation would analyze performance across different:
        # - Audio formats (MP3, WAV, FLAC)
        # - Video formats (MP4, AVI, MOV) 
        # - Content quality levels
        # - Content creators/genres
        
        return results


class ModelExplainabilityAnalyzer:
    """Provides explainability analysis for AI models"""
    
    def __init__(self):
        self.logger = logging.getLogger("ai_observability.explainability")
    
    async def analyze_feature_importance(self, model: Any, 
                                       feature_names: List[str],
                                       sample_data: np.ndarray) -> Dict[str, float]:
        """Analyze global feature importance"""
        feature_importance = {}
        
        try:
            # For tree-based models
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                for i, importance in enumerate(importances):
                    if i < len(feature_names):
                        feature_importance[feature_names[i]] = float(importance)
            
            # For linear models
            elif hasattr(model, 'coef_'):
                coefficients = model.coef_
                if len(coefficients.shape) == 1:
                    for i, coef in enumerate(coefficients):
                        if i < len(feature_names):
                            feature_importance[feature_names[i]] = abs(float(coef))
            
            # For neural networks (simplified)
            elif HAS_TENSORFLOW and isinstance(model, tf.keras.Model):
                # Use permutation importance
                feature_importance = await self._permutation_importance(
                    model, sample_data, feature_names
                )
            
            # Normalize importance scores
            if feature_importance:
                total_importance = sum(feature_importance.values())
                if total_importance > 0:
                    feature_importance = {
                        k: v / total_importance 
                        for k, v in feature_importance.items()
                    }
        
        except Exception as e:
            self.logger.error(f"Error analyzing feature importance: {str(e)}")
        
        return feature_importance
    
    async def _permutation_importance(self, model: Any, 
                                    sample_data: np.ndarray,
                                    feature_names: List[str]) -> Dict[str, float]:
        """Calculate permutation importance for neural networks"""
        importance = {}
        
        try:
            # Get baseline prediction
            baseline_pred = model.predict(sample_data)
            baseline_score = np.mean(baseline_pred)
            
            # Permute each feature and measure impact
            for i, feature_name in enumerate(feature_names):
                permuted_data = sample_data.copy()
                np.random.shuffle(permuted_data[:, i])
                
                permuted_pred = model.predict(permuted_data)
                permuted_score = np.mean(permuted_pred)
                
                # Importance is the change in model output
                importance[feature_name] = abs(baseline_score - permuted_score)
        
        except Exception as e:
            self.logger.error(f"Error calculating permutation importance: {str(e)}")
        
        return importance
    
    async def generate_local_explanations(self, model: Any, 
                                        instance: np.ndarray,
                                        feature_names: List[str]) -> Dict[str, Any]:
        """Generate instance-level explanations"""
        explanation = {
            "instance_id": hashlib.md5(instance.tobytes()).hexdigest()[:8],
            "prediction": None,
            "confidence": None,
            "contributing_features": {},
            "explanation_text": ""
        }
        
        try:
            # Get prediction and confidence
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(instance.reshape(1, -1))[0]
                explanation["prediction"] = int(np.argmax(proba))
                explanation["confidence"] = float(np.max(proba))
            elif hasattr(model, 'predict'):
                pred = model.predict(instance.reshape(1, -1))[0]
                explanation["prediction"] = float(pred)
                # Calculate confidence based on prediction certainty
                # For regression models, use prediction stability as confidence measure
                predictions = []
                if len(instance) > 1:
                    for i in range(min(10, len(instance))):
                        # Add small noise to input and check prediction stability
                        noisy_input = instance + np.random.normal(0, 0.01, instance.shape)
                        noisy_pred = model.predict(noisy_input.reshape(1, -1))[0]
                        predictions.append(noisy_pred)
                    
                    if predictions:
                        pred_std = np.std(predictions)
                        # Convert to confidence score (inverse of variability)
                        confidence = max(0.1, min(0.95, 1.0 - (pred_std / (abs(pred) + 1e-8))))
                        explanation["confidence"] = float(confidence)
                    else:
                        explanation["confidence"] = 0.5  # Default for single predictions
                else:
                    explanation["confidence"] = 0.5  # Default for edge cases
            
            # Analyze feature contributions (simplified)
            feature_importance = await self.analyze_feature_importance(
                model, feature_names, instance.reshape(1, -1)
            )
            
            # Get top contributing features
            sorted_features = sorted(
                feature_importance.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            explanation["contributing_features"] = dict(sorted_features[:5])
            
            # Generate explanation text
            top_feature = sorted_features[0] if sorted_features else ("unknown", 0)
            explanation["explanation_text"] = (
                f"Prediction primarily influenced by '{top_feature[0]}' "
                f"(importance: {top_feature[1]:.3f})"
            )
        
        except Exception as e:
            self.logger.error(f"Error generating local explanations: {str(e)}")
        
        return explanation
    
    async def analyze_model_explainability(self, model_id: str, model: Any,
                                         feature_names: List[str],
                                         sample_data: np.ndarray) -> ModelExplainabilityResult:
        """Comprehensive explainability analysis"""
        result = ModelExplainabilityResult(
            model_id=model_id,
            timestamp=datetime.utcnow()
        )
        
        try:
            # Global feature importance
            result.feature_importance = await self.analyze_feature_importance(
                model, feature_names, sample_data
            )
            
            # Generate local explanations for sample instances
            sample_size = min(10, len(sample_data))
            sample_indices = np.random.choice(len(sample_data), sample_size, replace=False)
            
            for idx in sample_indices:
                local_exp = await self.generate_local_explanations(
                    model, sample_data[idx], feature_names
                )
                result.local_explanations.append(local_exp)
            
            # Calculate explanation quality metrics
            result.explanation_quality = self._calculate_explanation_quality(result)
            result.interpretability_score = self._calculate_interpretability_score(model, result)
            result.consistency_score = self._calculate_consistency_score(result)
            
            # Generate stakeholder-specific explanations
            result.technical_explanation = self._generate_technical_explanation(result)
            result.business_explanation = self._generate_business_explanation(result)
            result.regulatory_explanation = self._generate_regulatory_explanation(result)
        
        except Exception as e:
            self.logger.error(f"Error in explainability analysis: {str(e)}")
        
        return result
    
    def _calculate_explanation_quality(self, result: ModelExplainabilityResult) -> float:
        """Calculate overall explanation quality score"""
        # Based on feature importance distribution and local explanation consistency
        if not result.feature_importance:
            return 0.0
        
        # Check feature importance distribution (prefer concentrated importance)
        importances = list(result.feature_importance.values())
        entropy = -sum(p * np.log(p + 1e-10) for p in importances if p > 0)
        normalized_entropy = entropy / np.log(len(importances)) if len(importances) > 1 else 0
        
        # Quality is higher when fewer features are important (lower entropy)
        quality_score = 1 - normalized_entropy
        
        return max(0.0, min(1.0, quality_score))
    
    def _calculate_interpretability_score(self, model: Any, 
                                        result: ModelExplainabilityResult) -> float:
        """Calculate model interpretability score"""
        score = 0.5  # Base score
        
        # Linear models are more interpretable
        if hasattr(model, 'coef_'):
            score += 0.3
        
        # Tree-based models are interpretable
        elif hasattr(model, 'feature_importances_'):
            score += 0.2
        
        # Complex models (neural networks) are less interpretable
        elif HAS_TENSORFLOW and isinstance(model, tf.keras.Model):
            score -= 0.1
        
        # Bonus for good feature importance distribution
        if result.feature_importance:
            top_5_importance = sum(sorted(result.feature_importance.values(), reverse=True)[:5])
            if top_5_importance > 0.8:  # Top 5 features explain 80% of importance
                score += 0.2
        
        return max(0.0, min(1.0, score))
    
    def _calculate_consistency_score(self, result: ModelExplainabilityResult) -> float:
        """Calculate explanation consistency score"""
        if len(result.local_explanations) < 2:
            return 0.5
        
        # Check consistency of top contributing features across instances
        top_features = []
        for exp in result.local_explanations:
            contributing_features = exp.get("contributing_features", {})
            if contributing_features:
                top_feature = max(contributing_features.items(), key=lambda x: x[1])[0]
                top_features.append(top_feature)
        
        if not top_features:
            return 0.5
        
        # Calculate consistency as most common feature frequency
        from collections import Counter
        feature_counts = Counter(top_features)
        most_common_freq = feature_counts.most_common(1)[0][1] if feature_counts else 0
        consistency = most_common_freq / len(top_features)
        
        return consistency
    
    def _generate_technical_explanation(self, result: ModelExplainabilityResult) -> str:
        """Generate technical explanation for developers"""
        if not result.feature_importance:
            return "No feature importance data available for technical analysis."
        
        top_features = sorted(result.feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]
        
        explanation = f"Model {result.model_id} technical analysis:\n"
        explanation += f"- Explanation Quality: {result.explanation_quality:.3f}\n"
        explanation += f"- Interpretability Score: {result.interpretability_score:.3f}\n"
        explanation += f"- Consistency Score: {result.consistency_score:.3f}\n\n"
        explanation += "Top contributing features:\n"
        
        for feature, importance in top_features:
            explanation += f"- {feature}: {importance:.3f} importance\n"
        
        return explanation
    
    def _generate_business_explanation(self, result: ModelExplainabilityResult) -> str:
        """Generate business-friendly explanation"""
        if not result.feature_importance:
            return "Model analysis unavailable for business review."
        
        top_feature = max(result.feature_importance.items(), key=lambda x: x[1])
        
        explanation = f"Business Impact Analysis for Model {result.model_id}:\n\n"
        explanation += f"The model's decisions are primarily driven by '{top_feature[0]}', "
        explanation += f"which accounts for {top_feature[1]:.1%} of the decision-making process.\n\n"
        
        if result.explanation_quality > 0.7:
            explanation += "✅ The model provides clear, understandable decision patterns.\n"
        else:
            explanation += "⚠️ The model's decision patterns may be complex and harder to interpret.\n"
        
        explanation += f"\nOverall model interpretability: {result.interpretability_score:.1%}"
        
        return explanation
    
    def _generate_regulatory_explanation(self, result: ModelExplainabilityResult) -> str:
        """Generate regulatory compliance explanation"""
        explanation = f"Regulatory Compliance Report for Model {result.model_id}:\n\n"
        
        explanation += f"Transparency Score: {result.explanation_quality:.1%}\n"
        explanation += f"Interpretability Score: {result.interpretability_score:.1%}\n"
        explanation += f"Decision Consistency: {result.consistency_score:.1%}\n\n"
        
        if result.explanation_quality > 0.8 and result.interpretability_score > 0.6:
            explanation += "✅ Model meets explainability requirements for regulatory compliance.\n"
        else:
            explanation += "⚠️ Model may require additional documentation for regulatory compliance.\n"
        
        explanation += "\nRecommendations for compliance:\n"
        if result.explanation_quality < 0.8:
            explanation += "- Improve feature importance documentation\n"
        if result.interpretability_score < 0.6:
            explanation += "- Consider simpler model architectures\n"
        if result.consistency_score < 0.7:
            explanation += "- Validate decision consistency across use cases\n"
        
        return explanation


class AIObservabilityEngine:
    """Main AI observability engine"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.monitors: Dict[str, BaseModelMonitor] = {}
        self.explainability_analyzer = ModelExplainabilityAnalyzer()
        self.logger = logging.getLogger("ai_observability.engine")
        
        # Background monitoring
        self._monitoring_task: Optional[asyncio.Task] = None
        self._running = False
        self._monitoring_interval = self.config.get("monitoring_interval_seconds", 60)
        
        # Results storage
        self.metrics_history: deque = deque(maxlen=10000)
        self.drift_results: deque = deque(maxlen=1000)
        self.bias_results: deque = deque(maxlen=1000)
        self.explainability_results: deque = deque(maxlen=100)
        
        # Alert thresholds
        self.alert_thresholds = self.config.get("alert_thresholds", {
            "accuracy_drop": 0.05,
            "latency_increase": 2.0,
            "error_rate_increase": 0.1,
            "drift_score": 0.1,
            "bias_score": 0.2
        })
    
    def register_model(self, monitor: BaseModelMonitor):
        """Register a model monitor"""
        self.monitors[monitor.model_id] = monitor
        self.logger.info(f"Registered model monitor: {monitor.model_id}")
    
    def create_content_protection_monitor(self, model_id: str, model_name: str,
                                        endpoint_url: str = None) -> ContentProtectionModelMonitor:
        """Create and register content protection model monitor"""
        monitor = ContentProtectionModelMonitor(model_id, model_name, endpoint_url)
        self.register_model(monitor)
        return monitor
    
    def create_fingerprinting_monitor(self, model_id: str, model_name: str) -> FingerprintingModelMonitor:
        """Create and register fingerprinting model monitor"""
        monitor = FingerprintingModelMonitor(model_id, model_name)
        self.register_model(monitor)
        return monitor
    
    async def start_monitoring(self):
        """Start background monitoring of all registered models"""
        if self._running:
            return
        
        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_worker())
        self.logger.info(f"Started AI observability monitoring for {len(self.monitors)} models")
    
    async def stop_monitoring(self):
        """Stop background monitoring"""
        self._running = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Stopped AI observability monitoring")
    
    async def _monitoring_worker(self):
        """Background monitoring worker"""
        while self._running:
            try:
                await self._collect_all_metrics()
                await asyncio.sleep(self._monitoring_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring worker: {str(e)}")
                await asyncio.sleep(30)  # Wait before retry
    
    async def _collect_all_metrics(self):
        """Collect metrics from all registered models"""
        if not self.monitors:
            return
        
        # Collect metrics in parallel
        tasks = []
        for monitor in self.monitors.values():
            task = asyncio.create_task(self._collect_monitor_metrics(monitor))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                monitor_id = list(self.monitors.keys())[i]
                self.logger.error(f"Error collecting metrics from {monitor_id}: {str(result)}")
    
    async def _collect_monitor_metrics(self, monitor: BaseModelMonitor):
        """Collect metrics from a single monitor"""
        try:
            metrics = await monitor.collect_metrics()
            self.metrics_history.append(metrics)
            
            # Check for alerts
            await self._check_metrics_alerts(metrics)
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics from {monitor.model_id}: {str(e)}")
    
    async def _check_metrics_alerts(self, metrics: ModelMetrics):
        """Check metrics against alert thresholds"""
        alerts = []
        
        # Check accuracy drop
        if metrics.accuracy is not None:
            recent_accuracy = self._get_recent_metrics_values("accuracy", metrics.model_id, hours=1)
            if len(recent_accuracy) > 5:
                avg_recent = np.mean(recent_accuracy[-5:])
                avg_historical = np.mean(recent_accuracy[:-5]) if len(recent_accuracy) > 5 else avg_recent
                
                if avg_recent < avg_historical - self.alert_thresholds["accuracy_drop"]:
                    alerts.append({
                        "type": "accuracy_drop",
                        "model_id": metrics.model_id,
                        "current": avg_recent,
                        "historical": avg_historical,
                        "severity": "high"
                    })
        
        # Check latency increase
        if metrics.latency_ms > 0:
            recent_latency = self._get_recent_metrics_values("latency_ms", metrics.model_id, hours=1)
            if len(recent_latency) > 5:
                avg_recent = np.mean(recent_latency[-5:])
                avg_historical = np.mean(recent_latency[:-5]) if len(recent_latency) > 5 else avg_recent
                
                if avg_recent > avg_historical * (1 + self.alert_thresholds["latency_increase"]):
                    alerts.append({
                        "type": "latency_increase",
                        "model_id": metrics.model_id,
                        "current": avg_recent,
                        "historical": avg_historical,
                        "severity": "medium"
                    })
        
        # Log alerts
        for alert in alerts:
            self.logger.warning(f"AI Model Alert: {alert}")
    
    def _get_recent_metrics_values(self, metric_name: str, model_id: str, hours: int = 24) -> List[float]:
        """Get recent values for a specific metric"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        values = []
        
        for metrics in self.metrics_history:
            if (metrics.model_id == model_id and 
                metrics.timestamp >= cutoff_time):
                
                value = getattr(metrics, metric_name, None)
                if value is not None and isinstance(value, (int, float)):
                    values.append(value)
        
        return values
    
    async def analyze_model_drift(self, model_id: str, reference_data: np.ndarray,
                                current_data: np.ndarray) -> List[DriftDetectionResult]:
        """Analyze drift for a specific model"""
        if model_id not in self.monitors:
            raise ValueError(f"Model {model_id} not registered")
        
        monitor = self.monitors[model_id]
        results = await monitor.detect_drift(reference_data, current_data)
        
        # Store results
        for result in results:
            self.drift_results.append(result)
        
        return results
    
    async def analyze_model_bias(self, model_id: str, predictions: np.ndarray,
                               ground_truth: np.ndarray,
                               protected_attributes: np.ndarray) -> List[BiasDetectionResult]:
        """Analyze bias for a specific model"""
        if model_id not in self.monitors:
            raise ValueError(f"Model {model_id} not registered")
        
        monitor = self.monitors[model_id]
        results = await monitor.detect_bias(predictions, ground_truth, protected_attributes)
        
        # Store results
        for result in results:
            self.bias_results.append(result)
        
        return results
    
    async def analyze_model_explainability(self, model_id: str, model: Any,
                                         feature_names: List[str],
                                         sample_data: np.ndarray) -> ModelExplainabilityResult:
        """Analyze explainability for a specific model"""
        result = await self.explainability_analyzer.analyze_model_explainability(
            model_id, model, feature_names, sample_data
        )
        
        # Store result
        self.explainability_results.append(result)
        
        return result
    
    def get_model_health_summary(self, model_id: str = None) -> Dict[str, Any]:
        """Get health summary for a model or all models"""
        if model_id:
            if model_id not in self.monitors:
                return {}
            
            models_to_analyze = [model_id]
        else:
            models_to_analyze = list(self.monitors.keys())
        
        summary = {}
        
        for mid in models_to_analyze:
            model_metrics = [m for m in self.metrics_history if m.model_id == mid]
            
            if not model_metrics:
                summary[mid] = {"status": "no_data"}
                continue
            
            latest_metrics = model_metrics[-1]
            recent_metrics = model_metrics[-10:] if len(model_metrics) >= 10 else model_metrics
            
            # Calculate trends
            accuracy_trend = self._calculate_trend([m.accuracy for m in recent_metrics if m.accuracy])
            latency_trend = self._calculate_trend([m.latency_ms for m in recent_metrics if m.latency_ms > 0])
            error_trend = self._calculate_trend([m.error_rate for m in recent_metrics])
            
            # Overall health score
            health_score = latest_metrics.get_performance_score()
            
            summary[mid] = {
                "model_name": self.monitors[mid].model_name,
                "model_type": self.monitors[mid].model_type.value,
                "last_update": latest_metrics.timestamp.isoformat(),
                "health_score": health_score,
                "latest_metrics": latest_metrics.to_dict(),
                "trends": {
                    "accuracy": accuracy_trend,
                    "latency": latency_trend,
                    "error_rate": error_trend
                },
                "alerts": self._get_recent_alerts(mid),
                "status": "healthy" if health_score > 0.8 else "degraded" if health_score > 0.6 else "critical"
            }
        
        return summary
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for a list of values"""
        if len(values) < 2:
            return "stable"
        
        # Simple linear trend calculation
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        if not first_half or not second_half:
            return "stable"
        
        first_avg = np.mean(first_half)
        second_avg = np.mean(second_half)
        
        if second_avg > first_avg * 1.05:
            return "increasing"
        elif second_avg < first_avg * 0.95:
            return "decreasing"
        else:
            return "stable"
    
    def _get_recent_alerts(self, model_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts for a model"""
        # This would integrate with the alerting system
        # For now, return empty list
        return []
    
    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive AI observability statistics"""
        return {
            "registered_models": len(self.monitors),
            "monitoring_active": self._running,
            "monitoring_interval_seconds": self._monitoring_interval,
            "total_metrics_collected": len(self.metrics_history),
            "total_drift_analyses": len(self.drift_results),
            "total_bias_analyses": len(self.bias_results),
            "total_explainability_analyses": len(self.explainability_results),
            "model_types": list(set(monitor.model_type.value for monitor in self.monitors.values())),
            "recent_drift_issues": sum(1 for r in self.drift_results 
                                     if r.is_drifting and r.timestamp > datetime.utcnow() - timedelta(days=1)),
            "recent_bias_issues": sum(1 for r in self.bias_results 
                                    if r.is_biased and r.timestamp > datetime.utcnow() - timedelta(days=1)),
            "alert_thresholds": self.alert_thresholds.copy()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get basic statistics"""
        return self.get_comprehensive_statistics()


# Factory function
def create_ai_observability_engine(config: Dict[str, Any] = None) -> AIObservabilityEngine:
    """Factory function to create AI observability engine"""
    return AIObservabilityEngine(config)


# Export AI observability components
__all__ = [
    "AIObservabilityEngine",
    "BaseModelMonitor",
    "ContentProtectionModelMonitor",
    "FingerprintingModelMonitor",
    "ModelExplainabilityAnalyzer",
    "ModelMetrics",
    "DriftDetectionResult",
    "BiasDetectionResult", 
    "ModelExplainabilityResult",
    "ModelType",
    "ModelFramework",
    "ModelStatus",
    "DriftType",
    "BiasType",
    "AlertSeverity",
    "create_ai_observability_engine"
]
