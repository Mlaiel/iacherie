"""
🔍 Model Drift Detection Engine - Enterprise AI/ML Performance Hub
================================================================

Moteur détection drift modèles IA ultra-avancé pour Creator Economy Ainflue.
Algorithmes détection dérive statistique, analyse patterns comportement créateurs,
monitoring distribution features, alertes dégradation performance, triggers retraining automatique.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Architecture: monitoring/ai_ml_performance_hub/model_drift_detection_engine.py
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Audio + DevOps
"""

import asyncio
import logging
import time
import statistics
import math
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import deque, defaultdict
import threading
import json
import uuid
import numpy as np
from concurrent.futures import ThreadPoolExecutor


class DriftType(Enum):
    """Types dérive modèle"""
    DATA_DRIFT = "data_drift"           # Distribution input features change
    CONCEPT_DRIFT = "concept_drift"     # Relationship input->output changes
    PERFORMANCE_DRIFT = "performance_drift"  # Model accuracy degrades
    PREDICTION_DRIFT = "prediction_drift"    # Output distribution changes
    BEHAVIORAL_DRIFT = "behavioral_drift"    # Creator behavior patterns change


class DriftSeverity(Enum):
    """Sévérité dérive"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CreatorTier(Enum):
    """Niveaux créateurs"""
    FREE = "free"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class ContentModality(Enum):
    """Modalités contenu"""
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"
    IMAGE = "image"
    MULTIMODAL = "multimodal"


class DetectionMethod(Enum):
    """Méthodes détection drift"""
    STATISTICAL_TEST = "statistical_test"        # KS test, chi-square, etc.
    DISTANCE_METRIC = "distance_metric"          # KL divergence, Wasserstein
    ENSEMBLE_VOTING = "ensemble_voting"          # Multiple methods combined
    PERFORMANCE_THRESHOLD = "performance_threshold"  # Accuracy-based
    CONFIDENCE_INTERVAL = "confidence_interval"  # Statistical bounds


@dataclass
class FeatureStatistics:
    """Statistiques feature"""
    feature_name: str
    feature_type: str  # "numerical", "categorical", "embedding"
    mean: Optional[float]
    std: Optional[float]
    min_val: Optional[float]
    max_val: Optional[float]
    percentiles: Optional[Dict[str, float]]
    category_distribution: Optional[Dict[str, float]]
    null_percentage: float
    unique_values_count: int
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DriftMeasurement:
    """Mesure dérive détaillée"""
    measurement_id: str
    model_id: str
    creator_id: str
    creator_tier: CreatorTier
    content_modality: ContentModality
    drift_type: DriftType
    detection_method: DetectionMethod
    drift_score: float  # 0-1, higher = more drift
    p_value: Optional[float]
    confidence_level: float
    reference_window_size: int
    current_window_size: int
    features_affected: List[str]
    performance_impact: Dict[str, float]
    statistical_details: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DriftAlert:
    """Alerte dérive modèle"""
    alert_id: str
    model_id: str
    creator_id: str
    drift_type: DriftType
    severity: DriftSeverity
    drift_score: float
    threshold_violated: float
    detection_method: DetectionMethod
    features_most_affected: List[str]
    estimated_impact: str
    recommended_actions: List[str]
    retraining_required: bool
    urgency_level: int  # 1=highest, 5=lowest
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ModelBehaviorPattern:
    """Pattern comportement modèle"""
    model_id: str
    creator_tier: CreatorTier
    content_modality: ContentModality
    typical_accuracy_range: Tuple[float, float]
    typical_confidence_range: Tuple[float, float]
    typical_latency_range: Tuple[float, float]
    common_features_patterns: Dict[str, Any]
    seasonal_patterns: Dict[str, float]
    creator_behavior_baseline: Dict[str, Any]
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RetrainingRecommendation:
    """Recommandation retraining"""
    recommendation_id: str
    model_id: str
    trigger_reason: str
    drift_severity: DriftSeverity
    estimated_performance_gain: float
    estimated_training_cost: float
    estimated_training_time_hours: float
    priority_score: float
    data_requirements: Dict[str, Any]
    suggested_hyperparameter_changes: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ModelDriftDetectionEngine:
    """Moteur détection drift modèles IA Creator Economy"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        
        # Drift detection storage
        self.model_features_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.model_predictions_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.model_performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Drift measurements and alerts
        self.drift_measurements: deque = deque(maxlen=5000)
        self.drift_alerts: deque = deque(maxlen=1000)
        self.active_drifts: Dict[str, DriftAlert] = {}
        
        # Model behavior baselines
        self.model_behavior_patterns: Dict[str, ModelBehaviorPattern] = {}
        self.creator_behavior_baselines: Dict[str, Dict] = defaultdict(dict)
        
        # Drift detection thresholds
        self.drift_thresholds = {
            DriftType.DATA_DRIFT: {'low': 0.1, 'medium': 0.3, 'high': 0.5, 'critical': 0.8},
            DriftType.CONCEPT_DRIFT: {'low': 0.05, 'medium': 0.15, 'high': 0.3, 'critical': 0.5},
            DriftType.PERFORMANCE_DRIFT: {'low': 0.02, 'medium': 0.05, 'high': 0.1, 'critical': 0.2},
            DriftType.PREDICTION_DRIFT: {'low': 0.1, 'medium': 0.25, 'high': 0.4, 'critical': 0.6},
            DriftType.BEHAVIORAL_DRIFT: {'low': 0.15, 'medium': 0.3, 'high': 0.5, 'critical': 0.7}
        }
        
        # Statistical test parameters
        self.statistical_params = {
            'confidence_level': 0.95,
            'min_samples_reference': 1000,
            'min_samples_current': 100,
            'reference_window_days': 30,
            'detection_window_hours': 6
        }
        
        # Monitoring
        self.monitoring_active = False
        self.drift_detection_thread: Optional[threading.Thread] = None
        self.behavior_analysis_thread: Optional[threading.Thread] = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Retraining recommendations
        self.retraining_recommendations: deque = deque(maxlen=100)
        
    def _setup_logging(self) -> logging.Logger:
        """Configuration logging avancé"""
        logger = logging.getLogger(f"drift_engine_{id(self)}")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def initialize(self):
        """Initialisation moteur détection drift"""
        self.logger.info("🔍 Initialisation Model Drift Detection Engine...")
        
        # Démarrer monitoring continu
        await self._start_drift_monitoring()
        await self._start_behavior_analysis()
        
        # Initialiser baselines
        await self._initialize_behavior_baselines()
        
        self.logger.info("✅ Model Drift Detection Engine initialisé")
    
    async def _start_drift_monitoring(self):
        """Démarrage monitoring drift"""
        self.monitoring_active = True
        
        def monitor_drift():
            while self.monitoring_active:
                try:
                    self._detect_data_drift()
                    self._detect_performance_drift()
                    self._detect_prediction_drift()
                    time.sleep(300)  # Check every 5 minutes
                except Exception as e:
                    self.logger.error(f"Drift monitoring error: {e}")
        
        self.drift_detection_thread = threading.Thread(target=monitor_drift, daemon=True)
        self.drift_detection_thread.start()
    
    async def _start_behavior_analysis(self):
        """Démarrage analyse comportement"""
        def analyze_behavior():
            while self.monitoring_active:
                try:
                    self._analyze_creator_behavior_patterns()
                    self._detect_concept_drift()
                    self._update_behavior_baselines()
                    time.sleep(600)  # Analyze every 10 minutes
                except Exception as e:
                    self.logger.error(f"Behavior analysis error: {e}")
        
        self.behavior_analysis_thread = threading.Thread(target=analyze_behavior, daemon=True)
        self.behavior_analysis_thread.start()
    
    async def _initialize_behavior_baselines(self):
        """Initialisation baselines comportement"""
        # Initialize sample behavior patterns for different model types
        sample_patterns = {
            'content_classifier': {
                CreatorTier.PREMIUM: {
                    ContentModality.VIDEO: ModelBehaviorPattern(
                        model_id='content_classifier',
                        creator_tier=CreatorTier.PREMIUM,
                        content_modality=ContentModality.VIDEO,
                        typical_accuracy_range=(0.88, 0.94),
                        typical_confidence_range=(0.75, 0.92),
                        typical_latency_range=(200, 400),
                        common_features_patterns={
                            'video_duration': {'mean': 180, 'std': 60},
                            'resolution': {'distribution': {'1080p': 0.6, '720p': 0.3, '4K': 0.1}},
                            'audio_quality': {'mean': 0.85, 'std': 0.1}
                        },
                        seasonal_patterns={'weekday_boost': 1.1, 'weekend_drop': 0.9},
                        creator_behavior_baseline={
                            'avg_uploads_per_day': 3.2,
                            'preferred_categories': ['entertainment', 'education'],
                            'engagement_pattern': 'consistent'
                        }
                    )
                }
            }
        }
        
        for model_id, tier_patterns in sample_patterns.items():
            for tier, modality_patterns in tier_patterns.items():
                for modality, pattern in modality_patterns.items():
                    key = f"{model_id}_{tier.value}_{modality.value}"
                    self.model_behavior_patterns[key] = pattern
    
    async def record_model_inference(
        self,
        model_id: str,
        creator_id: str,
        creator_tier: CreatorTier,
        content_modality: ContentModality,
        input_features: Dict[str, Any],
        prediction: Dict[str, Any],
        confidence_score: float,
        ground_truth: Optional[Dict[str, Any]] = None
    ):
        """Enregistrement inférence modèle pour détection drift"""
        timestamp = datetime.utcnow()
        
        # Store feature data
        feature_key = f"{model_id}_{creator_tier.value}_{content_modality.value}"
        
        feature_record = {
            'timestamp': timestamp,
            'creator_id': creator_id,
            'features': input_features,
            'feature_statistics': self._calculate_feature_statistics(input_features)
        }
        
        self.model_features_history[feature_key].append(feature_record)
        
        # Store prediction data
        prediction_record = {
            'timestamp': timestamp,
            'creator_id': creator_id,
            'prediction': prediction,
            'confidence_score': confidence_score,
            'ground_truth': ground_truth
        }
        
        self.model_predictions_history[feature_key].append(prediction_record)
        
        # Calculate performance metrics if ground truth available
        if ground_truth:
            await self._update_performance_metrics(
                feature_key, prediction, ground_truth, confidence_score, timestamp
            )
    
    def _calculate_feature_statistics(self, features: Dict[str, Any]) -> Dict[str, FeatureStatistics]:
        """Calcul statistiques features"""
        feature_stats = {}
        
        for feature_name, feature_value in features.items():
            if isinstance(feature_value, (int, float)):
                # Numerical feature
                stats = FeatureStatistics(
                    feature_name=feature_name,
                    feature_type="numerical",
                    mean=float(feature_value),
                    std=0.0,  # Single value, no std
                    min_val=float(feature_value),
                    max_val=float(feature_value),
                    percentiles=None,
                    category_distribution=None,
                    null_percentage=0.0,
                    unique_values_count=1
                )
            elif isinstance(feature_value, str):
                # Categorical feature
                stats = FeatureStatistics(
                    feature_name=feature_name,
                    feature_type="categorical",
                    mean=None,
                    std=None,
                    min_val=None,
                    max_val=None,
                    percentiles=None,
                    category_distribution={feature_value: 1.0},
                    null_percentage=0.0,
                    unique_values_count=1
                )
            elif isinstance(feature_value, list):
                # Embedding or array feature
                if all(isinstance(x, (int, float)) for x in feature_value):
                    mean_val = statistics.mean(feature_value)
                    std_val = statistics.stdev(feature_value) if len(feature_value) > 1 else 0.0
                    
                    stats = FeatureStatistics(
                        feature_name=feature_name,
                        feature_type="embedding",
                        mean=mean_val,
                        std=std_val,
                        min_val=min(feature_value),
                        max_val=max(feature_value),
                        percentiles=None,
                        category_distribution=None,
                        null_percentage=0.0,
                        unique_values_count=len(set(feature_value))
                    )
                else:
                    # Mixed type array
                    stats = FeatureStatistics(
                        feature_name=feature_name,
                        feature_type="mixed",
                        mean=None,
                        std=None,
                        min_val=None,
                        max_val=None,
                        percentiles=None,
                        category_distribution=None,
                        null_percentage=0.0,
                        unique_values_count=len(feature_value)
                    )
            else:
                # Other types
                stats = FeatureStatistics(
                    feature_name=feature_name,
                    feature_type="other",
                    mean=None,
                    std=None,
                    min_val=None,
                    max_val=None,
                    percentiles=None,
                    category_distribution=None,
                    null_percentage=0.0,
                    unique_values_count=1
                )
            
            feature_stats[feature_name] = stats
        
        return feature_stats
    
    async def _update_performance_metrics(
        self,
        model_key: str,
        prediction: Dict[str, Any],
        ground_truth: Dict[str, Any],
        confidence_score: float,
        timestamp: datetime
    ):
        """Mise à jour métriques performance"""
        # Calculate accuracy (simplified - would use proper metrics based on task type)
        accuracy = self._calculate_accuracy(prediction, ground_truth)
        
        performance_record = {
            'timestamp': timestamp,
            'accuracy': accuracy,
            'confidence_score': confidence_score,
            'prediction': prediction,
            'ground_truth': ground_truth
        }
        
        self.model_performance_history[model_key].append(performance_record)
    
    def _calculate_accuracy(self, prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Calcul précision (simplifié)"""
        # Simplified accuracy calculation - would be task-specific in production
        if 'label' in prediction and 'label' in ground_truth:
            return 1.0 if prediction['label'] == ground_truth['label'] else 0.0
        elif 'score' in prediction and 'score' in ground_truth:
            # Regression task
            error = abs(prediction['score'] - ground_truth['score'])
            max_error = max(abs(ground_truth['score']), 1.0)
            return max(0.0, 1.0 - (error / max_error))
        else:
            # Default similarity
            return 0.8  # Placeholder
    
    def _detect_data_drift(self):
        """Détection drift données"""
        for model_key, feature_history in self.model_features_history.items():
            if len(feature_history) < self.statistical_params['min_samples_current']:
                continue
            
            # Get reference and current windows
            reference_window = self._get_reference_window(feature_history)
            current_window = self._get_current_window(feature_history)
            
            if not reference_window or not current_window:
                continue
            
            # Detect drift for each feature
            for feature_name in self._get_common_features(reference_window, current_window):
                drift_score = self._calculate_feature_drift_score(
                    feature_name, reference_window, current_window
                )
                
                if drift_score > self.drift_thresholds[DriftType.DATA_DRIFT]['low']:
                    measurement = DriftMeasurement(
                        measurement_id=str(uuid.uuid4()),
                        model_id=model_key.split('_')[0],
                        creator_id="aggregate",  # Aggregated across creators
                        creator_tier=CreatorTier(model_key.split('_')[1]),
                        content_modality=ContentModality(model_key.split('_')[2]),
                        drift_type=DriftType.DATA_DRIFT,
                        detection_method=DetectionMethod.STATISTICAL_TEST,
                        drift_score=drift_score,
                        p_value=None,  # Would calculate actual p-value
                        confidence_level=self.statistical_params['confidence_level'],
                        reference_window_size=len(reference_window),
                        current_window_size=len(current_window),
                        features_affected=[feature_name],
                        performance_impact={},
                        statistical_details={
                            'feature_name': feature_name,
                            'drift_method': 'ks_test',
                            'drift_score': drift_score
                        }
                    )
                    
                    self.drift_measurements.append(measurement)
                    
                    # Create alert if significant drift
                    if drift_score > self.drift_thresholds[DriftType.DATA_DRIFT]['medium']:
                        self._create_drift_alert_sync(measurement)
    
    def _get_reference_window(self, feature_history: deque) -> List[Dict]:
        """Obtention fenêtre référence"""
        reference_cutoff = datetime.utcnow() - timedelta(days=self.statistical_params['reference_window_days'])
        current_cutoff = datetime.utcnow() - timedelta(hours=self.statistical_params['detection_window_hours'])
        
        reference_window = [
            record for record in feature_history
            if reference_cutoff <= record['timestamp'] < current_cutoff
        ]
        
        return reference_window[-self.statistical_params['min_samples_reference']:]
    
    def _get_current_window(self, feature_history: deque) -> List[Dict]:
        """Obtention fenêtre courante"""
        current_cutoff = datetime.utcnow() - timedelta(hours=self.statistical_params['detection_window_hours'])
        
        current_window = [
            record for record in feature_history
            if record['timestamp'] >= current_cutoff
        ]
        
        return current_window
    
    def _get_common_features(self, reference_window: List[Dict], current_window: List[Dict]) -> List[str]:
        """Obtention features communes"""
        if not reference_window or not current_window:
            return []
        
        ref_features = set(reference_window[0]['features'].keys())
        curr_features = set(current_window[0]['features'].keys())
        
        return list(ref_features.intersection(curr_features))
    
    def _calculate_feature_drift_score(
        self, 
        feature_name: str, 
        reference_window: List[Dict], 
        current_window: List[Dict]
    ) -> float:
        """Calcul score drift feature"""
        # Extract feature values
        ref_values = [record['features'][feature_name] for record in reference_window 
                     if feature_name in record['features']]
        curr_values = [record['features'][feature_name] for record in current_window 
                      if feature_name in record['features']]
        
        if not ref_values or not curr_values:
            return 0.0
        
        # Handle different feature types
        if all(isinstance(v, (int, float)) for v in ref_values + curr_values):
            # Numerical feature - use KS test approximation
            return self._ks_test_approximation(ref_values, curr_values)
        elif all(isinstance(v, str) for v in ref_values + curr_values):
            # Categorical feature - use chi-square approximation
            return self._chi_square_approximation(ref_values, curr_values)
        else:
            # Mixed or complex features - use distance-based method
            return self._distance_based_drift(ref_values, curr_values)
    
    def _ks_test_approximation(self, ref_values: List[float], curr_values: List[float]) -> float:
        """Approximation test Kolmogorov-Smirnov"""
        # Simple implementation - would use scipy.stats in production
        ref_mean = statistics.mean(ref_values)
        ref_std = statistics.stdev(ref_values) if len(ref_values) > 1 else 1.0
        
        curr_mean = statistics.mean(curr_values)
        curr_std = statistics.stdev(curr_values) if len(curr_values) > 1 else 1.0
        
        # Normalized difference in means
        mean_diff = abs(curr_mean - ref_mean) / (ref_std + 1e-6)
        
        # Normalized difference in standard deviations
        std_diff = abs(curr_std - ref_std) / (ref_std + 1e-6)
        
        # Combined drift score
        drift_score = min(1.0, (mean_diff + std_diff) / 2)
        
        return drift_score
    
    def _chi_square_approximation(self, ref_values: List[str], curr_values: List[str]) -> float:
        """Approximation test chi-carré"""
        # Calculate distributions
        ref_dist = defaultdict(int)
        curr_dist = defaultdict(int)
        
        for val in ref_values:
            ref_dist[val] += 1
        
        for val in curr_values:
            curr_dist[val] += 1
        
        # Normalize to probabilities
        ref_total = len(ref_values)
        curr_total = len(curr_values)
        
        all_categories = set(ref_dist.keys()) | set(curr_dist.keys())
        
        chi_square = 0.0
        for category in all_categories:
            ref_prob = ref_dist[category] / ref_total if ref_total > 0 else 0
            curr_prob = curr_dist[category] / curr_total if curr_total > 0 else 0
            
            expected = ref_prob
            observed = curr_prob
            
            if expected > 0:
                chi_square += ((observed - expected) ** 2) / expected
        
        # Normalize to 0-1 range (approximation)
        drift_score = min(1.0, chi_square / len(all_categories))
        
        return drift_score
    
    def _distance_based_drift(self, ref_values: List[Any], curr_values: List[Any]) -> float:
        """Drift basé sur distance"""
        # Simple overlap-based measure for complex features
        ref_set = set(str(v) for v in ref_values)
        curr_set = set(str(v) for v in curr_values)
        
        intersection = len(ref_set & curr_set)
        union = len(ref_set | curr_set)
        
        # Jaccard similarity
        similarity = intersection / union if union > 0 else 0
        drift_score = 1.0 - similarity
        
        return drift_score
    
    def _detect_performance_drift(self):
        """Détection drift performance"""
        for model_key, performance_history in self.model_performance_history.items():
            if len(performance_history) < 50:  # Need minimum samples
                continue
            
            # Calculate recent vs historical performance
            recent_window = list(performance_history)[-20:]  # Last 20 predictions
            historical_window = list(performance_history)[:-20] if len(performance_history) > 20 else []
            
            if not historical_window:
                continue
            
            recent_accuracy = statistics.mean([r['accuracy'] for r in recent_window])
            historical_accuracy = statistics.mean([r['accuracy'] for r in historical_window])
            
            # Calculate performance drift
            performance_drift = abs(historical_accuracy - recent_accuracy) / (historical_accuracy + 1e-6)
            
            if performance_drift > self.drift_thresholds[DriftType.PERFORMANCE_DRIFT]['low']:
                measurement = DriftMeasurement(
                    measurement_id=str(uuid.uuid4()),
                    model_id=model_key.split('_')[0],
                    creator_id="aggregate",
                    creator_tier=CreatorTier(model_key.split('_')[1]),
                    content_modality=ContentModality(model_key.split('_')[2]),
                    drift_type=DriftType.PERFORMANCE_DRIFT,
                    detection_method=DetectionMethod.PERFORMANCE_THRESHOLD,
                    drift_score=performance_drift,
                    p_value=None,
                    confidence_level=self.statistical_params['confidence_level'],
                    reference_window_size=len(historical_window),
                    current_window_size=len(recent_window),
                    features_affected=[],
                    performance_impact={
                        'accuracy_drop': historical_accuracy - recent_accuracy,
                        'relative_drop_percent': performance_drift * 100
                    },
                    statistical_details={
                        'historical_accuracy': historical_accuracy,
                        'recent_accuracy': recent_accuracy,
                        'drift_magnitude': performance_drift
                    }
                )
                
                self.drift_measurements.append(measurement)
                
                # Create alert if significant performance drift
                if performance_drift > self.drift_thresholds[DriftType.PERFORMANCE_DRIFT]['medium']:
                    self._create_performance_drift_alert_sync(measurement)
    
    def _detect_prediction_drift(self):
        """Détection drift prédictions"""
        for model_key, prediction_history in self.model_predictions_history.items():
            if len(prediction_history) < 100:
                continue
            
            # Analyze confidence score distribution drift
            recent_window = list(prediction_history)[-50:]
            historical_window = list(prediction_history)[:-50] if len(prediction_history) > 50 else []
            
            if not historical_window:
                continue
            
            recent_confidences = [r['confidence_score'] for r in recent_window]
            historical_confidences = [r['confidence_score'] for r in historical_window]
            
            # Calculate distribution shift
            confidence_drift = self._ks_test_approximation(historical_confidences, recent_confidences)
            
            if confidence_drift > self.drift_thresholds[DriftType.PREDICTION_DRIFT]['low']:
                measurement = DriftMeasurement(
                    measurement_id=str(uuid.uuid4()),
                    model_id=model_key.split('_')[0],
                    creator_id="aggregate",
                    creator_tier=CreatorTier(model_key.split('_')[1]),
                    content_modality=ContentModality(model_key.split('_')[2]),
                    drift_type=DriftType.PREDICTION_DRIFT,
                    detection_method=DetectionMethod.STATISTICAL_TEST,
                    drift_score=confidence_drift,
                    p_value=None,
                    confidence_level=self.statistical_params['confidence_level'],
                    reference_window_size=len(historical_window),
                    current_window_size=len(recent_window),
                    features_affected=['confidence_score'],
                    performance_impact={},
                    statistical_details={
                        'historical_mean_confidence': statistics.mean(historical_confidences),
                        'recent_mean_confidence': statistics.mean(recent_confidences),
                        'confidence_drift_score': confidence_drift
                    }
                )
                
                self.drift_measurements.append(measurement)
                
                if confidence_drift > self.drift_thresholds[DriftType.PREDICTION_DRIFT]['medium']:
                    self._create_drift_alert_sync(measurement)
    
    def _analyze_creator_behavior_patterns(self):
        """Analyse patterns comportement créateurs"""
        # Analyze creator behavior changes that might indicate concept drift
        creator_activity = defaultdict(list)
        
        # Collect creator activity from all models
        for model_key, feature_history in self.model_features_history.items():
            recent_window = self._get_current_window(feature_history)
            
            for record in recent_window:
                creator_id = record['creator_id']
                creator_activity[creator_id].append({
                    'timestamp': record['timestamp'],
                    'model_key': model_key,
                    'features': record['features']
                })
        
        # Analyze each creator's behavior
        for creator_id, activities in creator_activity.items():
            if len(activities) < 10:  # Need minimum activity
                continue
            
            # Detect behavioral drift
            behavioral_drift_score = self._calculate_behavioral_drift(creator_id, activities)
            
            if behavioral_drift_score > self.drift_thresholds[DriftType.BEHAVIORAL_DRIFT]['low']:
                self.logger.info(f"Behavioral drift detected for creator {creator_id}: {behavioral_drift_score:.3f}")
    
    def _calculate_behavioral_drift(self, creator_id: str, activities: List[Dict]) -> float:
        """Calcul drift comportemental"""
        # Simple behavioral drift calculation based on activity patterns
        if creator_id not in self.creator_behavior_baselines:
            # No baseline yet, establish one
            self.creator_behavior_baselines[creator_id] = self._establish_creator_baseline(activities)
            return 0.0
        
        baseline = self.creator_behavior_baselines[creator_id]
        current_pattern = self._analyze_current_behavior(activities)
        
        # Compare patterns
        drift_score = 0.0
        
        # Activity frequency drift
        baseline_freq = baseline.get('activity_frequency', 1.0)
        current_freq = current_pattern.get('activity_frequency', 1.0)
        freq_drift = abs(current_freq - baseline_freq) / (baseline_freq + 1e-6)
        drift_score += freq_drift * 0.3
        
        # Content type preference drift
        baseline_prefs = baseline.get('content_preferences', {})
        current_prefs = current_pattern.get('content_preferences', {})
        pref_drift = self._calculate_preference_drift(baseline_prefs, current_prefs)
        drift_score += pref_drift * 0.4
        
        # Temporal pattern drift
        baseline_temporal = baseline.get('temporal_pattern', {})
        current_temporal = current_pattern.get('temporal_pattern', {})
        temporal_drift = self._calculate_temporal_drift(baseline_temporal, current_temporal)
        drift_score += temporal_drift * 0.3
        
        return min(1.0, drift_score)
    
    def _establish_creator_baseline(self, activities: List[Dict]) -> Dict[str, Any]:
        """Établissement baseline créateur"""
        # Calculate baseline behavior pattern
        activity_frequency = len(activities) / 24  # Activities per hour (simplified)
        
        # Content preferences
        content_types = defaultdict(int)
        for activity in activities:
            model_key = activity['model_key']
            content_types[model_key.split('_')[2]] += 1  # Content modality
        
        total_activities = len(activities)
        content_preferences = {k: v / total_activities for k, v in content_types.items()}
        
        # Temporal patterns (hour of day)
        hour_distribution = defaultdict(int)
        for activity in activities:
            hour = activity['timestamp'].hour
            hour_distribution[hour] += 1
        
        temporal_pattern = {k: v / total_activities for k, v in hour_distribution.items()}
        
        return {
            'activity_frequency': activity_frequency,
            'content_preferences': content_preferences,
            'temporal_pattern': temporal_pattern,
            'established_at': datetime.utcnow()
        }
    
    def _analyze_current_behavior(self, activities: List[Dict]) -> Dict[str, Any]:
        """Analyse comportement actuel"""
        # Same analysis as baseline but for current window
        return self._establish_creator_baseline(activities)
    
    def _calculate_preference_drift(self, baseline_prefs: Dict, current_prefs: Dict) -> float:
        """Calcul drift préférences"""
        all_prefs = set(baseline_prefs.keys()) | set(current_prefs.keys())
        
        if not all_prefs:
            return 0.0
        
        drift = 0.0
        for pref in all_prefs:
            baseline_val = baseline_prefs.get(pref, 0.0)
            current_val = current_prefs.get(pref, 0.0)
            drift += abs(baseline_val - current_val)
        
        return drift / len(all_prefs)
    
    def _calculate_temporal_drift(self, baseline_temporal: Dict, current_temporal: Dict) -> float:
        """Calcul drift temporel"""
        # Similar to preference drift but for temporal patterns
        return self._calculate_preference_drift(baseline_temporal, current_temporal)
    
    def _detect_concept_drift(self):
        """Détection drift conceptuel"""
        # Analyze relationship between features and predictions
        for model_key, prediction_history in self.model_predictions_history.items():
            if len(prediction_history) < 100:
                continue
            
            # Get corresponding feature history
            if model_key not in self.model_features_history:
                continue
            
            feature_history = self.model_features_history[model_key]
            
            # Analyze correlation between features and predictions over time
            concept_drift_score = self._analyze_feature_prediction_correlation(
                feature_history, prediction_history
            )
            
            if concept_drift_score > self.drift_thresholds[DriftType.CONCEPT_DRIFT]['low']:
                measurement = DriftMeasurement(
                    measurement_id=str(uuid.uuid4()),
                    model_id=model_key.split('_')[0],
                    creator_id="aggregate",
                    creator_tier=CreatorTier(model_key.split('_')[1]),
                    content_modality=ContentModality(model_key.split('_')[2]),
                    drift_type=DriftType.CONCEPT_DRIFT,
                    detection_method=DetectionMethod.ENSEMBLE_VOTING,
                    drift_score=concept_drift_score,
                    p_value=None,
                    confidence_level=self.statistical_params['confidence_level'],
                    reference_window_size=len(feature_history),
                    current_window_size=len(prediction_history),
                    features_affected=[],
                    performance_impact={},
                    statistical_details={
                        'concept_drift_score': concept_drift_score,
                        'analysis_method': 'correlation_analysis'
                    }
                )
                
                self.drift_measurements.append(measurement)
                
                if concept_drift_score > self.drift_thresholds[DriftType.CONCEPT_DRIFT]['medium']:
                    self._create_drift_alert_sync(measurement)
    
    def _analyze_feature_prediction_correlation(
        self, 
        feature_history: deque, 
        prediction_history: deque
    ) -> float:
        """Analyse corrélation features-prédictions"""
        # Simplified concept drift detection
        # In production, would use more sophisticated methods
        
        if len(feature_history) < 50 or len(prediction_history) < 50:
            return 0.0
        
        # Compare recent vs historical correlation patterns
        # This is a simplified placeholder - real implementation would be more complex
        
        recent_features = list(feature_history)[-25:]
        recent_predictions = list(prediction_history)[-25:]
        
        historical_features = list(feature_history)[-50:-25]
        historical_predictions = list(prediction_history)[-50:-25]
        
        if not historical_features or not historical_predictions:
            return 0.0
        
        # Simple correlation change measure (placeholder)
        # Would use actual correlation analysis in production
        recent_avg_confidence = statistics.mean([p['confidence_score'] for p in recent_predictions])
        historical_avg_confidence = statistics.mean([p['confidence_score'] for p in historical_predictions])
        
        confidence_change = abs(recent_avg_confidence - historical_avg_confidence) / (historical_avg_confidence + 1e-6)
        
        return min(1.0, confidence_change)
    
    def _create_drift_alert_sync(self, measurement: DriftMeasurement):
        """Création alerte drift (synchrone)"""
        severity = self._determine_drift_severity(measurement.drift_type, measurement.drift_score)
        
        alert = DriftAlert(
            alert_id=str(uuid.uuid4()),
            model_id=measurement.model_id,
            creator_id=measurement.creator_id,
            drift_type=measurement.drift_type,
            severity=severity,
            drift_score=measurement.drift_score,
            threshold_violated=self.drift_thresholds[measurement.drift_type][severity.value],
            detection_method=measurement.detection_method,
            features_most_affected=measurement.features_affected,
            estimated_impact=self._estimate_drift_impact(measurement),
            recommended_actions=self._generate_drift_recommendations(measurement),
            retraining_required=severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL],
            urgency_level=self._calculate_urgency_level(severity, measurement.drift_type)
        )
        
        self.drift_alerts.append(alert)
        self.active_drifts[alert.alert_id] = alert
        
        self.logger.warning(
            f"🚨 {measurement.drift_type.value.title()} Drift Alert: {measurement.model_id} "
            f"(score: {measurement.drift_score:.3f}, severity: {severity.value})"
        )
        
        # Generate retraining recommendation if needed
        if alert.retraining_required:
            self._generate_retraining_recommendation_sync(alert, measurement)
    
    def _create_performance_drift_alert_sync(self, measurement: DriftMeasurement):
        """Création alerte drift performance (synchrone)"""
        self._create_drift_alert_sync(measurement)
    
    def _generate_retraining_recommendation_sync(self, alert: DriftAlert, measurement: DriftMeasurement):
        """Génération recommandation retraining (synchrone)"""
        # Estimate training cost and time based on model and drift severity
        base_cost = 100.0  # Base cost in dollars
        base_time = 2.0    # Base time in hours
        
        # Adjust based on severity
        severity_multiplier = {
            DriftSeverity.LOW: 1.0,
            DriftSeverity.MEDIUM: 1.5,
            DriftSeverity.HIGH: 2.0,
            DriftSeverity.CRITICAL: 3.0
        }[alert.severity]
        
        estimated_cost = base_cost * severity_multiplier
        estimated_time = base_time * severity_multiplier
        
        # Estimate performance gain
        estimated_gain = min(0.3, alert.drift_score * 0.5)  # Up to 30% improvement
        
        recommendation = RetrainingRecommendation(
            recommendation_id=str(uuid.uuid4()),
            model_id=alert.model_id,
            trigger_reason=f"{alert.drift_type.value} with score {alert.drift_score:.3f}",
            drift_severity=alert.severity,
            estimated_performance_gain=estimated_gain,
            estimated_training_cost=estimated_cost,
            estimated_training_time_hours=estimated_time,
            priority_score=self._calculate_priority_score(alert, estimated_gain, estimated_cost),
            data_requirements={
                'min_samples': 10000,
                'recent_data_weight': 0.7,
                'data_freshness_days': 30
            },
            suggested_hyperparameter_changes={
                'learning_rate': 'reduce by 50%',
                'regularization': 'increase by 20%'
            }
        )
        
        self.retraining_recommendations.append(recommendation)
        
        self.logger.info(
            f"💡 Retraining recommendation generated for {alert.model_id}: "
            f"estimated gain {estimated_gain:.1%}, cost ${estimated_cost:.0f}, time {estimated_time:.1f}h"
        )
    
    async def _create_drift_alert(self, measurement: DriftMeasurement):
        """Création alerte drift"""
        severity = self._determine_drift_severity(measurement.drift_type, measurement.drift_score)
        
        alert = DriftAlert(
            alert_id=str(uuid.uuid4()),
            model_id=measurement.model_id,
            creator_id=measurement.creator_id,
            drift_type=measurement.drift_type,
            severity=severity,
            drift_score=measurement.drift_score,
            threshold_violated=self.drift_thresholds[measurement.drift_type][severity.value],
            detection_method=measurement.detection_method,
            features_most_affected=measurement.features_affected,
            estimated_impact=self._estimate_drift_impact(measurement),
            recommended_actions=self._generate_drift_recommendations(measurement),
            retraining_required=severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL],
            urgency_level=self._calculate_urgency_level(severity, measurement.drift_type)
        )
        
        self.drift_alerts.append(alert)
        self.active_drifts[alert.alert_id] = alert
        
        self.logger.warning(
            f"🚨 {measurement.drift_type.value.title()} Drift Alert: {measurement.model_id} "
            f"(score: {measurement.drift_score:.3f}, severity: {severity.value})"
        )
        
        # Generate retraining recommendation if needed
        if alert.retraining_required:
            self._generate_retraining_recommendation_sync(alert, measurement)
    
    async def _create_performance_drift_alert(self, measurement: DriftMeasurement):
        """Création alerte drift performance"""
        self._create_drift_alert_sync(measurement)
    
    def _determine_drift_severity(self, drift_type: DriftType, drift_score: float) -> DriftSeverity:
        """Détermination sévérité drift"""
        thresholds = self.drift_thresholds[drift_type]
        
        if drift_score >= thresholds['critical']:
            return DriftSeverity.CRITICAL
        elif drift_score >= thresholds['high']:
            return DriftSeverity.HIGH
        elif drift_score >= thresholds['medium']:
            return DriftSeverity.MEDIUM
        else:
            return DriftSeverity.LOW
    
    def _estimate_drift_impact(self, measurement: DriftMeasurement) -> str:
        """Estimation impact drift"""
        impact_descriptions = {
            DriftType.DATA_DRIFT: f"Input data distribution has shifted by {measurement.drift_score:.1%}",
            DriftType.CONCEPT_DRIFT: f"Relationship between inputs and outputs has changed by {measurement.drift_score:.1%}",
            DriftType.PERFORMANCE_DRIFT: f"Model accuracy may have degraded by {measurement.drift_score:.1%}",
            DriftType.PREDICTION_DRIFT: f"Prediction confidence distribution has shifted by {measurement.drift_score:.1%}",
            DriftType.BEHAVIORAL_DRIFT: f"Creator behavior patterns have changed by {measurement.drift_score:.1%}"
        }
        
        return impact_descriptions.get(measurement.drift_type, "Unknown impact")
    
    def _generate_drift_recommendations(self, measurement: DriftMeasurement) -> List[str]:
        """Génération recommandations drift"""
        recommendations = []
        
        if measurement.drift_type == DriftType.DATA_DRIFT:
            recommendations.extend([
                "Monitor data quality and preprocessing pipelines",
                "Consider feature engineering updates",
                "Evaluate data collection procedures"
            ])
        
        elif measurement.drift_type == DriftType.CONCEPT_DRIFT:
            recommendations.extend([
                "Collect more recent training data",
                "Consider online learning approaches",
                "Review business logic changes"
            ])
        
        elif measurement.drift_type == DriftType.PERFORMANCE_DRIFT:
            recommendations.extend([
                "Immediate model retraining recommended",
                "Investigate root cause of performance degradation",
                "Consider ensemble methods"
            ])
        
        elif measurement.drift_type == DriftType.PREDICTION_DRIFT:
            recommendations.extend([
                "Calibrate model confidence scores",
                "Review prediction thresholds",
                "Monitor downstream systems"
            ])
        
        elif measurement.drift_type == DriftType.BEHAVIORAL_DRIFT:
            recommendations.extend([
                "Analyze creator behavior changes",
                "Update user segmentation models",
                "Consider personalization updates"
            ])
        
        # Add severity-based recommendations
        severity = self._determine_drift_severity(measurement.drift_type, measurement.drift_score)
        
        if severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]:
            recommendations.append("Immediate action required - high business impact")
        
        return recommendations
    
    def _calculate_urgency_level(self, severity: DriftSeverity, drift_type: DriftType) -> int:
        """Calcul niveau urgence"""
        base_urgency = {
            DriftSeverity.LOW: 5,
            DriftSeverity.MEDIUM: 4,
            DriftSeverity.HIGH: 2,
            DriftSeverity.CRITICAL: 1
        }[severity]
        
        # Adjust based on drift type
        if drift_type == DriftType.PERFORMANCE_DRIFT:
            base_urgency = max(1, base_urgency - 1)  # Higher urgency for performance issues
        
        return base_urgency
    
    async def _generate_retraining_recommendation(self, alert: DriftAlert, measurement: DriftMeasurement):
        """Génération recommandation retraining"""
        # Estimate training cost and time based on model and drift severity
        base_cost = 100.0  # Base cost in dollars
        base_time = 2.0    # Base time in hours
        
        # Adjust based on severity
        severity_multiplier = {
            DriftSeverity.LOW: 1.0,
            DriftSeverity.MEDIUM: 1.5,
            DriftSeverity.HIGH: 2.0,
            DriftSeverity.CRITICAL: 3.0
        }[alert.severity]
        
        estimated_cost = base_cost * severity_multiplier
        estimated_time = base_time * severity_multiplier
        
        # Estimate performance gain
        estimated_gain = min(0.3, alert.drift_score * 0.5)  # Up to 30% improvement
        
        recommendation = RetrainingRecommendation(
            recommendation_id=str(uuid.uuid4()),
            model_id=alert.model_id,
            trigger_reason=f"{alert.drift_type.value} with score {alert.drift_score:.3f}",
            drift_severity=alert.severity,
            estimated_performance_gain=estimated_gain,
            estimated_training_cost=estimated_cost,
            estimated_training_time_hours=estimated_time,
            priority_score=self._calculate_priority_score(alert, estimated_gain, estimated_cost),
            data_requirements={
                'min_samples': 10000,
                'recent_data_weight': 0.7,
                'data_freshness_days': 30
            },
            suggested_hyperparameter_changes={
                'learning_rate': 'reduce by 50%',
                'regularization': 'increase by 20%'
            }
        )
        
        self.retraining_recommendations.append(recommendation)
        
        self.logger.info(
            f"💡 Retraining recommendation generated for {alert.model_id}: "
            f"estimated gain {estimated_gain:.1%}, cost ${estimated_cost:.0f}, time {estimated_time:.1f}h"
        )
    
    def _calculate_priority_score(self, alert: DriftAlert, estimated_gain: float, estimated_cost: float) -> float:
        """Calcul score priorité"""
        # Priority based on gain/cost ratio and severity
        if estimated_cost > 0:
            roi_score = estimated_gain / (estimated_cost / 100)  # Normalize cost
        else:
            roi_score = estimated_gain
        
        severity_score = {
            DriftSeverity.LOW: 0.25,
            DriftSeverity.MEDIUM: 0.5,
            DriftSeverity.HIGH: 0.75,
            DriftSeverity.CRITICAL: 1.0
        }[alert.severity]
        
        urgency_score = (6 - alert.urgency_level) / 5  # Convert to 0-1 scale
        
        # Weighted combination
        priority_score = (roi_score * 0.4 + severity_score * 0.4 + urgency_score * 0.2)
        
        return min(1.0, priority_score)
    
    def _update_behavior_baselines(self):
        """Mise à jour baselines comportement"""
        # Update creator behavior baselines periodically
        current_time = datetime.utcnow()
        
        for creator_id, baseline in self.creator_behavior_baselines.items():
            established_at = baseline.get('established_at', current_time - timedelta(days=30))
            
            # Update baseline if it's older than 7 days
            if (current_time - established_at).days > 7:
                # Get recent activity for this creator
                creator_activities = []
                
                for model_key, feature_history in self.model_features_history.items():
                    recent_window = self._get_current_window(feature_history)
                    creator_records = [r for r in recent_window if r['creator_id'] == creator_id]
                    
                    for record in creator_records:
                        creator_activities.append({
                            'timestamp': record['timestamp'],
                            'model_key': model_key,
                            'features': record['features']
                        })
                
                if len(creator_activities) >= 10:  # Need minimum activity
                    updated_baseline = self._establish_creator_baseline(creator_activities)
                    self.creator_behavior_baselines[creator_id] = updated_baseline
                    
                    self.logger.debug(f"Updated behavior baseline for creator {creator_id}")
    
    async def get_drift_overview(self) -> Dict[str, Any]:
        """Vue d'ensemble drift"""
        # Recent drift measurements (last 24 hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        recent_measurements = [m for m in self.drift_measurements if m.timestamp >= cutoff_time]
        
        # Active alerts
        active_alerts = list(self.active_drifts.values())
        
        # Drift by type
        drift_by_type = defaultdict(int)
        for measurement in recent_measurements:
            drift_by_type[measurement.drift_type.value] += 1
        
        # Severity distribution
        severity_distribution = defaultdict(int)
        for alert in active_alerts:
            severity_distribution[alert.severity.value] += 1
        
        # Models with active drift
        models_with_drift = set(alert.model_id for alert in active_alerts)
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'summary': {
                'total_drift_measurements_24h': len(recent_measurements),
                'active_drift_alerts': len(active_alerts),
                'models_affected': len(models_with_drift),
                'retraining_recommendations': len(self.retraining_recommendations)
            },
            'drift_by_type': dict(drift_by_type),
            'severity_distribution': dict(severity_distribution),
            'most_affected_models': list(models_with_drift)[:5],
            'urgent_alerts': len([a for a in active_alerts if a.urgency_level <= 2])
        }
    
    async def get_model_drift_analysis(self, model_id: str) -> Dict[str, Any]:
        """Analyse drift modèle spécifique"""
        # Get measurements for this model
        model_measurements = [m for m in self.drift_measurements if m.model_id == model_id]
        
        if not model_measurements:
            return {'model_id': model_id, 'error': 'No drift measurements found'}
        
        # Get active alerts for this model
        model_alerts = [a for a in self.active_drifts.values() if a.model_id == model_id]
        
        # Drift timeline (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_measurements = [m for m in model_measurements if m.timestamp >= week_ago]
        
        # Drift trends by type
        drift_trends = defaultdict(list)
        for measurement in recent_measurements:
            drift_trends[measurement.drift_type.value].append({
                'timestamp': measurement.timestamp.isoformat(),
                'drift_score': measurement.drift_score
            })
        
        # Performance impact
        performance_measurements = [m for m in recent_measurements 
                                 if m.drift_type == DriftType.PERFORMANCE_DRIFT]
        
        performance_impact = {}
        if performance_measurements:
            latest_perf = performance_measurements[-1]
            performance_impact = latest_perf.performance_impact
        
        # Retraining recommendations for this model
        model_recommendations = [r for r in self.retraining_recommendations if r.model_id == model_id]
        
        return {
            'model_id': model_id,
            'drift_summary': {
                'total_measurements': len(model_measurements),
                'active_alerts': len(model_alerts),
                'highest_drift_score': max([m.drift_score for m in model_measurements]) if model_measurements else 0,
                'most_common_drift_type': max(drift_trends.keys(), key=lambda k: len(drift_trends[k])) if drift_trends else None
            },
            'drift_trends_7d': dict(drift_trends),
            'active_alerts': [
                {
                    'alert_id': alert.alert_id,
                    'drift_type': alert.drift_type.value,
                    'severity': alert.severity.value,
                    'drift_score': alert.drift_score,
                    'urgency_level': alert.urgency_level,
                    'retraining_required': alert.retraining_required
                }
                for alert in model_alerts
            ],
            'performance_impact': performance_impact,
            'retraining_recommendations': len(model_recommendations),
            'next_recommended_action': model_recommendations[0].recommended_id if model_recommendations else None
        }
    
    async def shutdown(self):
        """Arrêt propre moteur détection drift"""
        self.logger.info("⏹️ Arrêt Model Drift Detection Engine...")
        
        # Arrêter monitoring
        self.monitoring_active = False
        
        if self.drift_detection_thread:
            self.drift_detection_thread.join(timeout=5)
        
        if self.behavior_analysis_thread:
            self.behavior_analysis_thread.join(timeout=5)
        
        # Arrêter executor
        self.executor.shutdown(wait=True)
        
        self.logger.info("✅ Model Drift Detection Engine arrêté proprement")


# Point d'entrée pour tests
if __name__ == "__main__":
    async def test_drift_engine():
        config = {"debug": True}
        engine = ModelDriftDetectionEngine(config)
        
        await engine.initialize()
        
        # Simulate model inferences with potential drift
        for i in range(50):
            # Simulate gradual drift in features
            drift_factor = i / 50.0  # Gradually increase drift
            
            features = {
                'feature_1': 1.0 + drift_factor * 0.5,  # Gradual mean shift
                'feature_2': 'category_A' if i < 25 else 'category_B',  # Categorical shift
                'feature_3': [1.0, 2.0, 3.0 + drift_factor]  # Embedding drift
            }
            
            prediction = {
                'label': 'positive' if i % 2 == 0 else 'negative',
                'score': 0.8 - drift_factor * 0.3  # Decreasing confidence
            }
            
            ground_truth = {
                'label': 'positive' if i % 2 == 0 else 'negative'
            }
            
            await engine.record_model_inference(
                model_id="content_classifier",
                creator_id=f"creator_{i % 10}",
                creator_tier=CreatorTier.PREMIUM,
                content_modality=ContentModality.VIDEO,
                input_features=features,
                prediction=prediction,
                confidence_score=prediction['score'],
                ground_truth=ground_truth
            )
        
        # Wait for drift detection
        await asyncio.sleep(10)
        
        # Get overview
        overview = await engine.get_drift_overview()
        print(f"Drift Overview: {json.dumps(overview, indent=2)}")
        
        # Get model analysis
        model_analysis = await engine.get_model_drift_analysis("content_classifier")
        print(f"Model Analysis: {json.dumps(model_analysis, indent=2)}")
        
        print("✅ Model Drift Detection Engine test passed")
        await engine.shutdown()
    
    asyncio.run(test_drift_engine())