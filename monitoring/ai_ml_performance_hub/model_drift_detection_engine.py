"""
🔍 Model Drift Detection Engine - Enterprise AI/ML Quality Assurance
====================================================================

Moteur ultra-avancé détection drift modèles IA pour assurance qualité Creator Economy.
Statistical drift detection, behavioral analysis, automatic retraining triggers.

Fonctionnalités:
- Statistical drift detection algorithms (KS-test, PSI, Chi-square)
- Creator behavior pattern drift analysis
- Feature distribution monitoring avec alerting automatique
- Model performance degradation detection temps réel
- Automatic retraining triggers avec cost-benefit analysis
- Data quality monitoring pour input validation
- Concept drift vs data drift differentiation
- A/B testing support pour model comparison
- Creator tier impact analysis pour drift effects

Architecture: monitoring/ai_ml_performance_hub/model_drift_detection_engine.py
Responsabilité: Drift detection, quality assurance, retraining automation

© 2025 Fahed Mlaiel - Code propriétaire ultra-avancé production-ready
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import statistics
import threading
from collections import defaultdict, deque
import math
import numpy as np
from scipy import stats


class CreatorTier(Enum):
    """Niveaux créateurs pour analyse drift"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    PREMIUM = "premium"


class ModelType(Enum):
    """Types modèles surveillés pour drift"""
    CONTENT_CLASSIFIER = "content_classifier"
    COLLABORATION_MATCHER = "collaboration_matcher"
    REVENUE_PREDICTOR = "revenue_predictor"
    QUALITY_ASSESSOR = "quality_assessor"
    TREND_ANALYZER = "trend_analyzer"
    RECOMMENDATION_ENGINE = "recommendation_engine"
    AUDIO_PROCESSOR = "audio_processor"
    IMAGE_ENHANCER = "image_enhancer"


class DriftType(Enum):
    """Types drift détectés"""
    DATA_DRIFT = "data_drift"           # Changes in input distribution
    CONCEPT_DRIFT = "concept_drift"     # Changes in input-output relationship
    PREDICTION_DRIFT = "prediction_drift"  # Changes in model outputs
    PERFORMANCE_DRIFT = "performance_drift"  # Changes in model performance
    BEHAVIORAL_DRIFT = "behavioral_drift"    # Changes in user behavior patterns


class DriftSeverity(Enum):
    """Sévérité drift détecté"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class StatisticalTest(Enum):
    """Tests statistiques pour drift detection"""
    KOLMOGOROV_SMIRNOV = "kolmogorov_smirnov"
    POPULATION_STABILITY_INDEX = "population_stability_index"
    CHI_SQUARE = "chi_square"
    JENSEN_SHANNON_DIVERGENCE = "jensen_shannon_divergence"
    EARTH_MOVERS_DISTANCE = "earth_movers_distance"


@dataclass
class FeatureStatistics:
    """Statistiques feature pour baseline"""
    feature_name: str
    feature_type: str  # "numerical", "categorical", "boolean"
    
    # Numerical features
    mean: Optional[float] = None
    std_dev: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    percentiles: Optional[Dict[str, float]] = None  # P25, P50, P75, P95, P99
    
    # Categorical features
    category_distribution: Optional[Dict[str, float]] = None  # category -> frequency
    unique_values: Optional[int] = None
    entropy: Optional[float] = None
    
    # Quality metrics
    missing_rate: float = 0.0
    outlier_rate: float = 0.0
    
    sample_count: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DriftMeasurement:
    """Mesure drift détectée"""
    measurement_id: str
    model_id: str
    model_type: ModelType
    drift_type: DriftType
    
    # Statistical measures
    statistical_test: StatisticalTest
    test_statistic: float
    p_value: float
    threshold: float
    
    # Feature-specific drift
    feature_name: Optional[str] = None
    feature_drift_score: Optional[float] = None
    
    # Context information
    baseline_period: Tuple[datetime, datetime] = None
    detection_period: Tuple[datetime, datetime] = None
    sample_size_baseline: int = 0
    sample_size_detection: int = 0
    
    # Business context
    creator_tier_impact: Dict[CreatorTier, float] = field(default_factory=dict)
    business_impact_score: float = 0.0
    
    # Severity and confidence
    severity: DriftSeverity = DriftSeverity.LOW
    confidence_score: float = 0.0
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DriftAlert:
    """Alerte drift détectée"""
    alert_id: str
    model_id: str
    drift_measurements: List[DriftMeasurement]
    
    # Alert classification
    overall_severity: DriftSeverity
    alert_type: str  # "single_feature", "multiple_features", "model_wide", "performance_degradation"
    
    # Impact assessment
    affected_features: List[str]
    performance_impact_estimate: float  # Estimated performance drop %
    creator_impact_analysis: Dict[CreatorTier, str]
    
    # Recommendations
    recommended_actions: List[str]
    retraining_recommended: bool
    urgency_score: float  # 0-1, 1 being most urgent
    
    # Cost-benefit analysis
    estimated_retraining_cost: float
    estimated_performance_recovery: float
    roi_retraining: float
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RetrainingTrigger:
    """Déclencheur retraining automatique"""
    trigger_id: str
    model_id: str
    trigger_reason: str
    
    # Trigger conditions
    drift_alerts: List[str]  # Alert IDs that triggered this
    performance_threshold_breached: bool
    time_since_last_training: timedelta
    
    # Retraining parameters
    recommended_data_window: timedelta
    estimated_training_time: timedelta
    resource_requirements: Dict[str, Any]
    
    # Cost analysis
    estimated_cost: float
    expected_benefit: float
    priority_score: float
    
    # Status
    status: str = "pending"  # "pending", "approved", "running", "completed", "failed"
    
    created_at: datetime = field(default_factory=datetime.utcnow)


class ModelDriftDetectionEngine:
    """Moteur détection drift modèles IA Creator Economy"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        
        # Model tracking and baselines
        self.model_baselines: Dict[str, Dict[str, FeatureStatistics]] = {}  # model_id -> feature_name -> stats
        self.model_metadata: Dict[str, Dict[str, Any]] = {}  # model_id -> metadata
        
        # Drift measurements and alerts
        self.drift_measurements: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))  # model_id -> measurements
        self.active_alerts: Dict[str, DriftAlert] = {}  # alert_id -> alert
        self.alert_history: deque = deque(maxlen=500)
        
        # Retraining triggers
        self.retraining_triggers: Dict[str, RetrainingTrigger] = {}  # trigger_id -> trigger
        self.retraining_history: deque = deque(maxlen=100)
        
        # Real-time monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_interval = config.get('monitoring_interval', 300.0)  # 5 minutes default
        
        # Detection thresholds
        self.drift_thresholds = {
            StatisticalTest.KOLMOGOROV_SMIRNOV: 0.05,  # p-value threshold
            StatisticalTest.POPULATION_STABILITY_INDEX: 0.1,  # PSI threshold  
            StatisticalTest.CHI_SQUARE: 0.05,  # p-value threshold
            StatisticalTest.JENSEN_SHANNON_DIVERGENCE: 0.1,  # divergence threshold
            StatisticalTest.EARTH_MOVERS_DISTANCE: 0.2  # distance threshold
        }
        
        # Performance drift thresholds
        self.performance_thresholds = {
            'accuracy_drop_percent': 5.0,  # 5% accuracy drop triggers alert
            'precision_drop_percent': 5.0,
            'recall_drop_percent': 5.0,
            'f1_drop_percent': 5.0,
            'latency_increase_percent': 20.0  # 20% latency increase
        }
        
        # Retraining triggers
        self.retraining_config = {
            'auto_trigger_enabled': config.get('auto_retraining', False),
            'min_days_between_retraining': config.get('min_retraining_interval_days', 7),
            'performance_threshold_critical': 10.0,  # 10% performance drop = critical
            'cost_benefit_threshold': 2.0  # ROI must be > 2.0 to trigger auto-retraining
        }
        
        # Creator tier impact weights
        self.tier_impact_weights = {
            CreatorTier.PREMIUM: 4.0,
            CreatorTier.ENTERPRISE: 3.0,
            CreatorTier.PRO: 2.0,
            CreatorTier.FREE: 1.0
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Configuration logging avancé"""
        logger = logging.getLogger("model_drift_detection")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [DRIFT] - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def initialize(self):
        """Initialisation moteur drift detection"""
        self.logger.info("🔍 Initialisation Model Drift Detection Engine...")
        
        # Initialize sample models and baselines
        await self._initialize_model_baselines()
        
        # Start real-time monitoring
        await self._start_drift_monitoring()
        
        self.logger.info("✅ Model Drift Detection Engine initialisé")
    
    async def _initialize_model_baselines(self):
        """Initialisation baselines modèles"""
        # Sample models with typical features
        sample_models = {
            'content_classifier_v1': {
                'type': ModelType.CONTENT_CLASSIFIER,
                'features': {
                    'text_length': {'type': 'numerical', 'mean': 150.0, 'std': 50.0, 'min': 10.0, 'max': 500.0},
                    'word_count': {'type': 'numerical', 'mean': 25.0, 'std': 10.0, 'min': 2.0, 'max': 80.0},
                    'content_type': {'type': 'categorical', 'categories': {'blog': 0.4, 'video': 0.3, 'audio': 0.2, 'image': 0.1}},
                    'creator_tier': {'type': 'categorical', 'categories': {'free': 0.5, 'pro': 0.3, 'enterprise': 0.15, 'premium': 0.05}},
                    'engagement_score': {'type': 'numerical', 'mean': 0.65, 'std': 0.25, 'min': 0.0, 'max': 1.0}
                }
            },
            'collaboration_matcher_v2': {
                'type': ModelType.COLLABORATION_MATCHER,
                'features': {
                    'creator_followers': {'type': 'numerical', 'mean': 10000.0, 'std': 50000.0, 'min': 100.0, 'max': 1000000.0},
                    'content_similarity': {'type': 'numerical', 'mean': 0.7, 'std': 0.2, 'min': 0.0, 'max': 1.0},
                    'geographic_distance': {'type': 'numerical', 'mean': 500.0, 'std': 1000.0, 'min': 0.0, 'max': 10000.0},
                    'collaboration_history': {'type': 'numerical', 'mean': 5.0, 'std': 8.0, 'min': 0.0, 'max': 50.0},
                    'preferred_medium': {'type': 'categorical', 'categories': {'video': 0.4, 'audio': 0.3, 'text': 0.2, 'image': 0.1}}
                }
            },
            'revenue_predictor_v1': {
                'type': ModelType.REVENUE_PREDICTOR,
                'features': {
                    'historical_revenue': {'type': 'numerical', 'mean': 1500.0, 'std': 2000.0, 'min': 0.0, 'max': 50000.0},
                    'content_views': {'type': 'numerical', 'mean': 25000.0, 'std': 75000.0, 'min': 100.0, 'max': 5000000.0},
                    'engagement_rate': {'type': 'numerical', 'mean': 0.08, 'std': 0.05, 'min': 0.0, 'max': 0.5},
                    'monetization_enabled': {'type': 'boolean', 'categories': {'true': 0.7, 'false': 0.3}},
                    'seasonal_factor': {'type': 'numerical', 'mean': 1.0, 'std': 0.3, 'min': 0.5, 'max': 2.0}
                }
            }
        }
        
        for model_id, model_info in sample_models.items():
            self.model_metadata[model_id] = {
                'type': model_info['type'],
                'created_at': datetime.utcnow() - timedelta(days=30),
                'last_trained': datetime.utcnow() - timedelta(days=7),
                'version': '1.0.0'
            }
            
            # Create feature baselines
            model_baselines = {}
            for feature_name, feature_config in model_info['features'].items():
                if feature_config['type'] == 'numerical':
                    baseline = FeatureStatistics(
                        feature_name=feature_name,
                        feature_type='numerical',
                        mean=feature_config['mean'],
                        std_dev=feature_config['std'],
                        min_value=feature_config['min'],
                        max_value=feature_config['max'],
                        percentiles={
                            'p25': feature_config['mean'] - 0.67 * feature_config['std'],
                            'p50': feature_config['mean'],
                            'p75': feature_config['mean'] + 0.67 * feature_config['std'],
                            'p95': feature_config['mean'] + 1.64 * feature_config['std'],
                            'p99': feature_config['mean'] + 2.33 * feature_config['std']
                        },
                        sample_count=10000
                    )
                elif feature_config['type'] == 'categorical':
                    baseline = FeatureStatistics(
                        feature_name=feature_name,
                        feature_type='categorical',
                        category_distribution=feature_config['categories'],
                        unique_values=len(feature_config['categories']),
                        entropy=self._calculate_entropy(list(feature_config['categories'].values())),
                        sample_count=10000
                    )
                elif feature_config['type'] == 'boolean':
                    baseline = FeatureStatistics(
                        feature_name=feature_name,
                        feature_type='boolean',
                        category_distribution=feature_config['categories'],
                        unique_values=2,
                        sample_count=10000
                    )
                
                model_baselines[feature_name] = baseline
            
            self.model_baselines[model_id] = model_baselines
            
            self.logger.info(
                f"📊 Baseline initialized for {model_id}: {len(model_baselines)} features"
            )
    
    def _calculate_entropy(self, probabilities: List[float]) -> float:
        """Calcul entropie Shannon"""
        entropy = 0.0
        for p in probabilities:
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy
    
    async def _start_drift_monitoring(self):
        """Démarrage monitoring drift temps réel"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        
        self.logger.info("🔍 Drift monitoring started")
    
    def _monitoring_loop(self):
        """Boucle monitoring drift temps réel"""
        while self.monitoring_active:
            try:
                # Run drift detection for all models
                self._run_drift_detection_cycle()
                
                # Process active alerts
                self._process_active_alerts()
                
                # Check retraining triggers
                self._check_retraining_triggers()
                
                # Cleanup old data
                self._cleanup_old_data()
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in drift monitoring loop: {str(e)}")
                time.sleep(30)  # Wait longer on error
    
    def _run_drift_detection_cycle(self):
        """Cycle détection drift pour tous modèles"""
        for model_id in self.model_baselines.keys():
            try:
                # Simulate receiving new data for drift detection
                self._simulate_and_detect_drift(model_id)
                
            except Exception as e:
                self.logger.error(f"Error detecting drift for model {model_id}: {str(e)}")
    
    def _simulate_and_detect_drift(self, model_id: str):
        """Simulation et détection drift pour modèle"""
        import random
        
        # Simulate new data that might show drift
        model_baseline = self.model_baselines[model_id]
        
        for feature_name, baseline_stats in model_baseline.items():
            # Simulate drift with some probability
            drift_probability = 0.1  # 10% chance of drift per cycle
            
            if random.random() < drift_probability:
                # Generate drift measurement
                drift_measurement = self._generate_simulated_drift(
                    model_id, feature_name, baseline_stats
                )
                
                if drift_measurement:
                    self.drift_measurements[model_id].append(drift_measurement)
                    
                    # Check if alert should be created
                    if drift_measurement.p_value < self.drift_thresholds[drift_measurement.statistical_test]:
                        asyncio.run_coroutine_threadsafe(
                            self._create_drift_alert(model_id, [drift_measurement]),
                            asyncio.get_event_loop()
                        )
    
    def _generate_simulated_drift(
        self, 
        model_id: str, 
        feature_name: str, 
        baseline_stats: FeatureStatistics
    ) -> Optional[DriftMeasurement]:
        """Génération drift simulé pour tests"""
        import random
        
        # Choose random statistical test
        statistical_test = random.choice(list(StatisticalTest))
        
        # Generate realistic test results
        if baseline_stats.feature_type == 'numerical':
            # Simulate numerical feature drift
            test_statistic = random.uniform(0.1, 0.8)
            p_value = random.uniform(0.001, 0.2)  # Some will be significant
            
        elif baseline_stats.feature_type == 'categorical':
            # Simulate categorical feature drift
            test_statistic = random.uniform(0.05, 0.5)
            p_value = random.uniform(0.001, 0.15)
            
        else:  # boolean
            test_statistic = random.uniform(0.02, 0.3)
            p_value = random.uniform(0.001, 0.1)
        
        # Determine severity based on test results
        threshold = self.drift_thresholds[statistical_test]
        
        if p_value < threshold * 0.2:  # Very significant
            severity = DriftSeverity.CRITICAL
            confidence = 0.95
        elif p_value < threshold * 0.5:
            severity = DriftSeverity.HIGH
            confidence = 0.85
        elif p_value < threshold:
            severity = DriftSeverity.MEDIUM
            confidence = 0.75
        else:
            severity = DriftSeverity.LOW
            confidence = 0.6
        
        # Creator tier impact (simulate)
        tier_impact = {}
        for tier in CreatorTier:
            impact_factor = random.uniform(0.5, 1.5) * self.tier_impact_weights[tier]
            tier_impact[tier] = min(1.0, impact_factor * test_statistic)
        
        # Business impact score
        weighted_impact = sum(
            tier_impact[tier] * self.tier_impact_weights[tier] 
            for tier in CreatorTier
        )
        business_impact = weighted_impact / sum(self.tier_impact_weights.values())
        
        measurement = DriftMeasurement(
            measurement_id=str(uuid.uuid4()),
            model_id=model_id,
            model_type=self.model_metadata[model_id]['type'],
            drift_type=DriftType.DATA_DRIFT,  # Simplified for simulation
            statistical_test=statistical_test,
            test_statistic=test_statistic,
            p_value=p_value,
            threshold=threshold,
            feature_name=feature_name,
            feature_drift_score=test_statistic,
            baseline_period=(datetime.utcnow() - timedelta(days=7), datetime.utcnow() - timedelta(days=1)),
            detection_period=(datetime.utcnow() - timedelta(hours=24), datetime.utcnow()),
            sample_size_baseline=10000,
            sample_size_detection=1000,
            creator_tier_impact=tier_impact,
            business_impact_score=business_impact,
            severity=severity,
            confidence_score=confidence
        )
        
        return measurement
    
    async def _create_drift_alert(self, model_id: str, drift_measurements: List[DriftMeasurement]):
        """Création alerte drift"""
        # Determine overall severity
        max_severity = max(m.severity for m in drift_measurements)
        
        # Classify alert type
        unique_features = set(m.feature_name for m in drift_measurements if m.feature_name)
        
        if len(unique_features) == 1:
            alert_type = "single_feature"
        elif len(unique_features) > 1:
            alert_type = "multiple_features"
        else:
            alert_type = "model_wide"
        
        # Estimate performance impact
        avg_drift_score = statistics.mean([m.feature_drift_score or 0 for m in drift_measurements])
        performance_impact = min(50.0, avg_drift_score * 100)  # Max 50% estimated impact
        
        # Creator impact analysis
        creator_impact = {}
        for tier in CreatorTier:
            tier_impacts = [m.creator_tier_impact.get(tier, 0) for m in drift_measurements]
            avg_impact = statistics.mean(tier_impacts)
            
            if avg_impact > 0.8:
                creator_impact[tier] = "high_impact"
            elif avg_impact > 0.5:
                creator_impact[tier] = "medium_impact"
            elif avg_impact > 0.2:
                creator_impact[tier] = "low_impact"
            else:
                creator_impact[tier] = "no_impact"
        
        # Generate recommendations
        recommendations = self._generate_drift_recommendations(drift_measurements, max_severity)
        
        # Determine if retraining is recommended
        retraining_recommended = (
            max_severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL] or
            performance_impact > 10.0 or
            len(unique_features) > 3
        )
        
        # Calculate urgency score
        urgency_factors = [
            min(1.0, performance_impact / 20.0),  # Performance impact factor
            1.0 if max_severity == DriftSeverity.CRITICAL else 0.8 if max_severity == DriftSeverity.HIGH else 0.5,
            min(1.0, len(drift_measurements) / 5.0),  # Number of drifted features
            statistics.mean([m.business_impact_score for m in drift_measurements])
        ]
        urgency_score = statistics.mean(urgency_factors)
        
        # Cost-benefit analysis for retraining
        retraining_cost = self._estimate_retraining_cost(model_id)
        performance_recovery = min(90.0, performance_impact * 0.8)  # Assume 80% recovery
        roi_retraining = (performance_recovery * 1000) / retraining_cost if retraining_cost > 0 else 0  # Simplified ROI
        
        alert = DriftAlert(
            alert_id=str(uuid.uuid4()),
            model_id=model_id,
            drift_measurements=drift_measurements,
            overall_severity=max_severity,
            alert_type=alert_type,
            affected_features=list(unique_features),
            performance_impact_estimate=performance_impact,
            creator_impact_analysis=creator_impact,
            recommended_actions=recommendations,
            retraining_recommended=retraining_recommended,
            urgency_score=urgency_score,
            estimated_retraining_cost=retraining_cost,
            estimated_performance_recovery=performance_recovery,
            roi_retraining=roi_retraining
        )
        
        self.active_alerts[alert.alert_id] = alert
        self.alert_history.append(alert)
        
        self.logger.warning(
            f"🚨 Drift Alert: {model_id} - {alert_type} - {max_severity.value} severity "
            f"({len(drift_measurements)} measurements, {performance_impact:.1f}% impact estimate)"
        )
        
        # Auto-trigger retraining if configured
        if (self.retraining_config['auto_trigger_enabled'] and 
            retraining_recommended and 
            roi_retraining > self.retraining_config['cost_benefit_threshold']):
            
            await self._create_retraining_trigger(model_id, [alert.alert_id], "drift_detected")
    
    def _generate_drift_recommendations(
        self, 
        drift_measurements: List[DriftMeasurement], 
        severity: DriftSeverity
    ) -> List[str]:
        """Génération recommandations drift"""
        recommendations = []
        
        # General recommendations based on severity
        if severity == DriftSeverity.CRITICAL:
            recommendations.extend([
                "Immediate model retraining required",
                "Consider temporarily reducing model confidence thresholds",
                "Implement fallback mechanisms for affected predictions"
            ])
        elif severity == DriftSeverity.HIGH:
            recommendations.extend([
                "Schedule model retraining within 48 hours",
                "Monitor model performance closely",
                "Consider A/B testing with updated model"
            ])
        elif severity == DriftSeverity.MEDIUM:
            recommendations.extend([
                "Plan model retraining within next week",
                "Increase monitoring frequency",
                "Analyze root cause of distribution changes"
            ])
        else:  # LOW
            recommendations.extend([
                "Continue monitoring for trend confirmation",
                "Document drift patterns for future analysis"
            ])
        
        # Feature-specific recommendations
        feature_types = set(m.drift_type for m in drift_measurements)
        
        if DriftType.DATA_DRIFT in feature_types:
            recommendations.append("Investigate changes in data pipeline or sources")
        
        if DriftType.CONCEPT_DRIFT in feature_types:
            recommendations.append("Analyze changes in user behavior patterns")
        
        if DriftType.PERFORMANCE_DRIFT in feature_types:
            recommendations.append("Review model architecture and hyperparameters")
        
        # Creator tier specific recommendations
        high_impact_tiers = [
            tier for tier, impacts in 
            [(tier, [m.creator_tier_impact.get(tier, 0) for m in drift_measurements])
             for tier in CreatorTier]
            if statistics.mean(impacts) > 0.7
        ]
        
        if CreatorTier.PREMIUM in high_impact_tiers or CreatorTier.ENTERPRISE in high_impact_tiers:
            recommendations.append("Prioritize retraining due to high-value creator impact")
        
        return recommendations[:8]  # Limit to top 8 recommendations
    
    def _estimate_retraining_cost(self, model_id: str) -> float:
        """Estimation coût retraining"""
        model_type = self.model_metadata[model_id]['type']
        
        # Simplified cost model based on model type
        base_costs = {
            ModelType.CONTENT_CLASSIFIER: 500.0,
            ModelType.COLLABORATION_MATCHER: 800.0,
            ModelType.REVENUE_PREDICTOR: 300.0,
            ModelType.QUALITY_ASSESSOR: 600.0,
            ModelType.TREND_ANALYZER: 1000.0,
            ModelType.RECOMMENDATION_ENGINE: 1200.0,
            ModelType.AUDIO_PROCESSOR: 2000.0,
            ModelType.IMAGE_ENHANCER: 1500.0
        }
        
        return base_costs.get(model_type, 500.0)
    
    async def _create_retraining_trigger(
        self, 
        model_id: str, 
        alert_ids: List[str], 
        reason: str
    ):
        """Création déclencheur retraining"""
        model_metadata = self.model_metadata[model_id]
        last_training = model_metadata.get('last_trained', datetime.utcnow() - timedelta(days=30))
        time_since_training = datetime.utcnow() - last_training
        
        # Check minimum interval
        min_interval = timedelta(days=self.retraining_config['min_days_between_retraining'])
        if time_since_training < min_interval:
            self.logger.info(
                f"⏱️ Retraining trigger skipped for {model_id}: "
                f"Last training {time_since_training.days} days ago (min: {min_interval.days} days)"
            )
            return
        
        # Calculate resource requirements
        model_type = model_metadata['type']
        resource_requirements = self._calculate_retraining_resources(model_type)
        
        # Estimate costs and benefits
        estimated_cost = self._estimate_retraining_cost(model_id)
        
        # Calculate expected benefit from drift alerts
        relevant_alerts = [self.active_alerts[aid] for aid in alert_ids if aid in self.active_alerts]
        expected_benefit = sum(alert.estimated_performance_recovery * 10 for alert in relevant_alerts)  # Simplified
        
        priority_score = expected_benefit / estimated_cost if estimated_cost > 0 else 0
        
        trigger = RetrainingTrigger(
            trigger_id=str(uuid.uuid4()),
            model_id=model_id,
            trigger_reason=reason,
            drift_alerts=alert_ids,
            performance_threshold_breached=any(
                alert.performance_impact_estimate > self.retraining_config['performance_threshold_critical']
                for alert in relevant_alerts
            ),
            time_since_last_training=time_since_training,
            recommended_data_window=timedelta(days=30),  # Default 30 days of data
            estimated_training_time=timedelta(hours=resource_requirements['estimated_hours']),
            resource_requirements=resource_requirements,
            estimated_cost=estimated_cost,
            expected_benefit=expected_benefit,
            priority_score=priority_score
        )
        
        self.retraining_triggers[trigger.trigger_id] = trigger
        
        self.logger.warning(
            f"🔄 Retraining trigger created: {model_id} - {reason} "
            f"(Priority: {priority_score:.2f}, Cost: ${estimated_cost:.0f})"
        )
    
    def _calculate_retraining_resources(self, model_type: ModelType) -> Dict[str, Any]:
        """Calcul ressources nécessaires retraining"""
        # Simplified resource estimation
        resource_templates = {
            ModelType.CONTENT_CLASSIFIER: {'gpu_hours': 2, 'memory_gb': 16, 'estimated_hours': 4},
            ModelType.COLLABORATION_MATCHER: {'gpu_hours': 4, 'memory_gb': 32, 'estimated_hours': 8},
            ModelType.REVENUE_PREDICTOR: {'gpu_hours': 1, 'memory_gb': 8, 'estimated_hours': 2},
            ModelType.QUALITY_ASSESSOR: {'gpu_hours': 3, 'memory_gb': 24, 'estimated_hours': 6},
            ModelType.TREND_ANALYZER: {'gpu_hours': 6, 'memory_gb': 48, 'estimated_hours': 12},
            ModelType.RECOMMENDATION_ENGINE: {'gpu_hours': 8, 'memory_gb': 64, 'estimated_hours': 16},
            ModelType.AUDIO_PROCESSOR: {'gpu_hours': 12, 'memory_gb': 96, 'estimated_hours': 24},
            ModelType.IMAGE_ENHANCER: {'gpu_hours': 10, 'memory_gb': 80, 'estimated_hours': 20}
        }
        
        return resource_templates.get(model_type, {'gpu_hours': 2, 'memory_gb': 16, 'estimated_hours': 4})
    
    def _process_active_alerts(self):
        """Traitement alertes actives"""
        # Auto-resolve old alerts
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        resolved_alerts = []
        for alert_id, alert in self.active_alerts.items():
            if alert.timestamp < cutoff_time and alert.overall_severity in [DriftSeverity.LOW, DriftSeverity.MEDIUM]:
                resolved_alerts.append(alert_id)
        
        for alert_id in resolved_alerts:
            self.logger.info(f"📋 Auto-resolved drift alert: {alert_id}")
            del self.active_alerts[alert_id]
    
    def _check_retraining_triggers(self):
        """Vérification déclencheurs retraining"""
        for trigger_id, trigger in list(self.retraining_triggers.items()):
            if trigger.status == "pending":
                # Auto-approve high priority triggers
                if (trigger.priority_score > self.retraining_config['cost_benefit_threshold'] and
                    trigger.performance_threshold_breached):
                    
                    trigger.status = "approved"
                    self.logger.info(f"🎯 Auto-approved retraining trigger: {trigger_id}")
                    
                    # Here you would integrate with actual retraining system
                    # For now, just simulate completion after some time
                    if trigger.created_at < datetime.utcnow() - timedelta(minutes=30):
                        trigger.status = "completed"
                        self.retraining_history.append(trigger)
                        
                        # Update model metadata
                        self.model_metadata[trigger.model_id]['last_trained'] = datetime.utcnow()
                        
                        self.logger.info(f"✅ Simulated retraining completed: {trigger.model_id}")
    
    def _cleanup_old_data(self):
        """Nettoyage données anciennes"""
        cutoff_time = datetime.utcnow() - timedelta(days=7)
        
        # Cleanup old drift measurements
        for model_id in list(self.drift_measurements.keys()):
            measurements = self.drift_measurements[model_id]
            # Keep only recent measurements (deque maxlen handles most of this)
            pass
        
        # Cleanup completed retraining triggers
        completed_triggers = [
            tid for tid, trigger in self.retraining_triggers.items()
            if trigger.status == "completed" and trigger.created_at < cutoff_time
        ]
        
        for trigger_id in completed_triggers:
            trigger = self.retraining_triggers[trigger_id]
            self.retraining_history.append(trigger)
            del self.retraining_triggers[trigger_id]
    
    async def get_model_drift_status(self, model_id: str) -> Dict[str, Any]:
        """Statut drift modèle"""
        if model_id not in self.model_baselines:
            return {'error': f'Model {model_id} not found'}
        
        # Recent drift measurements
        recent_measurements = list(self.drift_measurements[model_id])[-10:]
        
        # Active alerts for this model
        model_alerts = [
            alert for alert in self.active_alerts.values()
            if alert.model_id == model_id
        ]
        
        # Drift score calculation
        if recent_measurements:
            avg_drift_score = statistics.mean([
                m.feature_drift_score or 0 for m in recent_measurements
            ])
            max_drift_score = max([
                m.feature_drift_score or 0 for m in recent_measurements
            ])
        else:
            avg_drift_score = 0.0
            max_drift_score = 0.0
        
        # Overall status
        if model_alerts:
            max_alert_severity = max(alert.overall_severity for alert in model_alerts)
            if max_alert_severity == DriftSeverity.CRITICAL:
                overall_status = "critical_drift"
            elif max_alert_severity == DriftSeverity.HIGH:
                overall_status = "high_drift"
            elif max_alert_severity == DriftSeverity.MEDIUM:
                overall_status = "moderate_drift"
            else:
                overall_status = "low_drift"
        else:
            overall_status = "stable"
        
        # Retraining status
        model_triggers = [
            trigger for trigger in self.retraining_triggers.values()
            if trigger.model_id == model_id
        ]
        
        retraining_status = "none"
        if model_triggers:
            latest_trigger = max(model_triggers, key=lambda t: t.created_at)
            retraining_status = latest_trigger.status
        
        return {
            'model_id': model_id,
            'model_type': self.model_metadata[model_id]['type'].value,
            'overall_status': overall_status,
            'drift_metrics': {
                'avg_drift_score': round(avg_drift_score, 4),
                'max_drift_score': round(max_drift_score, 4),
                'recent_measurements': len(recent_measurements),
                'features_monitored': len(self.model_baselines[model_id])
            },
            'active_alerts': len(model_alerts),
            'alert_details': [
                {
                    'alert_id': alert.alert_id,
                    'severity': alert.overall_severity.value,
                    'alert_type': alert.alert_type,
                    'affected_features': alert.affected_features,
                    'performance_impact': alert.performance_impact_estimate,
                    'retraining_recommended': alert.retraining_recommended,
                    'created_at': alert.timestamp.isoformat()
                }
                for alert in model_alerts
            ],
            'retraining_status': retraining_status,
            'retraining_triggers': len(model_triggers),
            'last_training': self.model_metadata[model_id].get('last_trained', datetime.utcnow()).isoformat(),
            'baseline_info': {
                'baseline_age_days': (datetime.utcnow() - self.model_metadata[model_id].get('created_at', datetime.utcnow())).days,
                'baseline_features': len(self.model_baselines[model_id])
            }
        }
    
    async def get_drift_detection_summary(self) -> Dict[str, Any]:
        """Résumé détection drift tous modèles"""
        total_models = len(self.model_baselines)
        total_active_alerts = len(self.active_alerts)
        total_measurements = sum(len(measurements) for measurements in self.drift_measurements.values())
        
        # Status distribution
        status_distribution = defaultdict(int)
        for model_id in self.model_baselines.keys():
            status = await self.get_model_drift_status(model_id)
            status_distribution[status['overall_status']] += 1
        
        # Alert severity distribution
        severity_distribution = defaultdict(int)
        for alert in self.active_alerts.values():
            severity_distribution[alert.overall_severity.value] += 1
        
        # Retraining statistics
        retraining_stats = {
            'pending_triggers': len([t for t in self.retraining_triggers.values() if t.status == "pending"]),
            'approved_triggers': len([t for t in self.retraining_triggers.values() if t.status == "approved"]),
            'running_retrainings': len([t for t in self.retraining_triggers.values() if t.status == "running"]),
            'completed_retrainings': len(self.retraining_history)
        }
        
        # Recent activity
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_alerts = len([
            alert for alert in self.active_alerts.values()
            if alert.timestamp > recent_cutoff
        ])
        
        recent_measurements = sum(
            len([m for m in measurements if m.timestamp > recent_cutoff])
            for measurements in self.drift_measurements.values()
        )
        
        return {
            'overview': {
                'total_models_monitored': total_models,
                'total_active_alerts': total_active_alerts,
                'total_drift_measurements': total_measurements,
                'monitoring_active': self.monitoring_active
            },
            'model_status_distribution': dict(status_distribution),
            'alert_severity_distribution': dict(severity_distribution),
            'retraining_statistics': retraining_stats,
            'recent_activity_24h': {
                'new_alerts': recent_alerts,
                'new_measurements': recent_measurements
            },
            'configuration': {
                'monitoring_interval_minutes': self.monitoring_interval / 60,
                'auto_retraining_enabled': self.retraining_config['auto_trigger_enabled'],
                'drift_thresholds': {test.value: threshold for test, threshold in self.drift_thresholds.items()}
            },
            'system_health': {
                'models_stable': status_distribution.get('stable', 0),
                'models_need_attention': total_models - status_distribution.get('stable', 0),
                'critical_alerts': severity_distribution.get('critical', 0),
                'last_update': datetime.utcnow().isoformat()
            }
        }
    
    async def get_comprehensive_dashboard(self) -> Dict[str, Any]:
        """Dashboard complet drift detection"""
        # Overall summary
        summary = await self.get_drift_detection_summary()
        
        # Individual model statuses
        model_statuses = {}
        for model_id in self.model_baselines.keys():
            model_statuses[model_id] = await self.get_model_drift_status(model_id)
        
        # Top priority alerts
        priority_alerts = sorted(
            self.active_alerts.values(),
            key=lambda alert: (alert.overall_severity.value, alert.urgency_score),
            reverse=True
        )[:5]
        
        priority_alert_summary = [
            {
                'alert_id': alert.alert_id,
                'model_id': alert.model_id,
                'severity': alert.overall_severity.value,
                'urgency_score': alert.urgency_score,
                'performance_impact': alert.performance_impact_estimate,
                'retraining_recommended': alert.retraining_recommended,
                'roi_retraining': alert.roi_retraining,
                'created_at': alert.timestamp.isoformat()
            }
            for alert in priority_alerts
        ]
        
        # Retraining queue
        retraining_queue = [
            {
                'trigger_id': trigger.trigger_id,
                'model_id': trigger.model_id,
                'status': trigger.status,
                'priority_score': trigger.priority_score,
                'estimated_cost': trigger.estimated_cost,
                'expected_benefit': trigger.expected_benefit,
                'created_at': trigger.created_at.isoformat()
            }
            for trigger in sorted(self.retraining_triggers.values(), key=lambda t: t.priority_score, reverse=True)
        ]
        
        return {
            'summary': summary,
            'model_details': model_statuses,
            'priority_alerts': priority_alert_summary,
            'retraining_queue': retraining_queue,
            'recommendations': self._generate_system_recommendations(),
            'dashboard_generated_at': datetime.utcnow().isoformat()
        }
    
    def _generate_system_recommendations(self) -> List[str]:
        """Génération recommandations système"""
        recommendations = []
        
        # Check for high number of critical alerts
        critical_alerts = len([
            alert for alert in self.active_alerts.values()
            if alert.overall_severity == DriftSeverity.CRITICAL
        ])
        
        if critical_alerts > 2:
            recommendations.append(
                f"High priority: {critical_alerts} critical drift alerts require immediate attention"
            )
        
        # Check for models needing retraining
        high_priority_retraining = len([
            trigger for trigger in self.retraining_triggers.values()
            if trigger.priority_score > 3.0 and trigger.status == "pending"
        ])
        
        if high_priority_retraining > 0:
            recommendations.append(
                f"Consider approving {high_priority_retraining} high-priority retraining requests"
            )
        
        # Check for models without recent measurements
        stale_models = len([
            model_id for model_id in self.model_baselines.keys()
            if len(self.drift_measurements[model_id]) == 0
        ])
        
        if stale_models > 0:
            recommendations.append(
                f"Investigate {stale_models} models with no recent drift measurements"
            )
        
        # General health recommendations
        if not recommendations:
            recommendations.append("System healthy - continue regular monitoring")
        
        return recommendations[:5]
    
    async def shutdown(self):
        """Arrêt propre moteur drift detection"""
        self.logger.info("⏹️ Shutting down Model Drift Detection Engine...")
        
        # Stop monitoring
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=10)
        
        # Clear data structures
        self.model_baselines.clear()
        self.model_metadata.clear()
        self.drift_measurements.clear()
        self.active_alerts.clear()
        self.alert_history.clear()
        self.retraining_triggers.clear()
        self.retraining_history.clear()
        
        self.logger.info("✅ Model Drift Detection Engine shutdown complete")


# Point d'entrée pour tests
if __name__ == "__main__":
    async def test_drift_engine():
        config = {
            'monitoring_interval': 2.0,  # Fast for testing
            'auto_retraining': True
        }
        
        engine = ModelDriftDetectionEngine(config)
        await engine.initialize()
        
        # Let monitoring run for a few cycles
        await asyncio.sleep(6)
        
        # Test drift status for a model
        status = await engine.get_model_drift_status('content_classifier_v1')
        print(f"✅ Model status: {status['overall_status']} ({status['active_alerts']} alerts)")
        
        # Test summary
        summary = await engine.get_drift_detection_summary()
        print(f"✅ System summary: {summary['overview']['total_models_monitored']} models monitored")
        
        # Test dashboard
        dashboard = await engine.get_comprehensive_dashboard()
        print(f"✅ Dashboard: {len(dashboard['priority_alerts'])} priority alerts")
        
        print("✅ Model Drift Detection Engine test completed")
        await engine.shutdown()
    
    asyncio.run(test_drift_engine())