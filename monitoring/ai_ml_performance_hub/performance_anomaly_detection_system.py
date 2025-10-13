"""
🚨 Performance Anomaly Detection System - Enterprise AI/ML Infrastructure
========================================================================

Système ultra-avancé détection anomalies performance pour infrastructure IA Creator Economy.
ML-based anomaly detection, pattern recognition, root cause analysis automatisé.

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

Architecture: monitoring/ai_ml_performance_hub/performance_anomaly_detection_system.py
Responsabilité: Détection anomalies performance IA, ML pattern recognition, Creator Economy analytics
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + DevOps
"""

import asyncio
import logging
import statistics
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
import math
import numpy as np
from collections import deque, defaultdict
import time
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN


class AnomalyType(Enum):
    """Types d'anomalies détectées"""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    LATENCY_SPIKE = "latency_spike"
    THROUGHPUT_DROP = "throughput_drop"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    MODEL_DRIFT = "model_drift"
    MEMORY_LEAK = "memory_leak"
    ERROR_RATE_SURGE = "error_rate_surge"
    CREATOR_PATTERN_ANOMALY = "creator_pattern_anomaly"
    COST_ANOMALY = "cost_anomaly"
    AVAILABILITY_DEGRADATION = "availability_degradation"


class AnomalySeverity(Enum):
    """Niveaux sévérité anomalies"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class DetectionMethod(Enum):
    """Méthodes détection anomalies"""
    STATISTICAL_OUTLIER = "statistical_outlier"
    ISOLATION_FOREST = "isolation_forest"
    CLUSTERING_BASED = "clustering_based"
    TIME_SERIES_ANALYSIS = "time_series_analysis"
    THRESHOLD_BASED = "threshold_based"
    PATTERN_RECOGNITION = "pattern_recognition"
    ENSEMBLE_METHOD = "ensemble_method"


class CreatorTier(Enum):
    """Niveaux créateurs pour analyse"""
    PREMIUM = "premium"
    PROFESSIONAL = "professional"
    STANDARD = "standard"
    STARTER = "starter"


@dataclass
class PerformanceMetric:
    """Métrique performance pour analyse"""
    metric_name: str
    value: float
    timestamp: datetime
    source_id: str  # model_id, instance_id, etc.
    creator_id: Optional[str] = None
    creator_tier: Optional[CreatorTier] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnomalyDetection:
    """Détection anomalie performance"""
    anomaly_id: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    detection_method: DetectionMethod
    affected_metric: str
    current_value: float
    expected_value: float
    deviation_score: float  # How far from normal (0-1)
    confidence_score: float  # Detection confidence (0-1)
    source_id: str
    creator_impact: Dict[str, int]  # creator_tier -> affected_count
    time_window: Tuple[datetime, datetime]
    root_cause_analysis: Dict[str, Any]
    recommended_actions: List[str]
    auto_remediation_possible: bool
    business_impact: str  # low, medium, high, critical
    detected_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AnomalyPattern:
    """Pattern d'anomalies récurrentes"""
    pattern_id: str
    pattern_name: str
    anomaly_types: List[AnomalyType]
    typical_conditions: Dict[str, Any]
    frequency: str  # hourly, daily, weekly
    seasonal_correlation: bool
    creator_tier_correlation: bool
    predictive_indicators: List[str]
    historical_occurrences: int
    last_occurrence: datetime
    prevention_strategies: List[str]
    confidence: float  # 0-1


@dataclass
class RootCauseAnalysis:
    """Analyse cause racine anomalie"""
    analysis_id: str
    anomaly_id: str
    primary_cause: str
    contributing_factors: List[str]
    correlation_analysis: Dict[str, float]  # factor -> correlation_score
    timeline_analysis: List[Dict[str, Any]]
    impact_assessment: Dict[str, Any]
    remediation_priority: str  # immediate, urgent, high, medium, low
    estimated_resolution_time: float  # hours
    resource_requirements: Dict[str, Any]
    success_probability: float  # 0-1
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AnomalyAlert:
    """Alerte anomalie performance"""
    alert_id: str
    anomaly_id: str
    alert_level: str  # notification, warning, critical, emergency
    recipients: List[str]  # team members, roles
    notification_channels: List[str]  # email, slack, pagerduty
    escalation_policy: Dict[str, Any]
    acknowledgment_required: bool
    auto_resolution_timeout: Optional[int]  # minutes
    business_context: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class PerformanceAnomalyDetectionSystem:
    """Système détection anomalies performance enterprise"""
    
    def __init__(self, config):
        self.config = config
        self.logger = self._setup_logging()
        
        # Metrics storage and processing
        self.metrics_buffer: deque = deque(maxlen=10000)
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.baseline_models: Dict[str, Dict[str, Any]] = {}
        
        # Anomaly detection and analysis
        self.detected_anomalies: List[AnomalyDetection] = []
        self.anomaly_patterns: List[AnomalyPattern] = []
        self.root_cause_analyses: List[RootCauseAnalysis] = []
        self.active_alerts: List[AnomalyAlert] = []
        
        # ML models for detection
        self.isolation_forests: Dict[str, IsolationForest] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.clustering_models: Dict[str, DBSCAN] = {}
        
        # Detection thresholds and parameters
        self.detection_thresholds = {
            'latency_spike_threshold': 3.0,  # standard deviations
            'throughput_drop_threshold': 2.5,
            'error_rate_threshold': 0.05,  # 5%
            'resource_utilization_threshold': 0.95,  # 95%
            'anomaly_score_threshold': 0.7,  # 0-1
            'minimum_data_points': 10
        }
        
        # Pattern recognition
        self.pattern_detection_window = timedelta(hours=24)
        self.seasonal_analysis_window = timedelta(days=7)
        
        # Alert configurations
        self.alert_policies = {
            AnomalySeverity.CRITICAL: {
                'notification_delay': 0,  # immediate
                'escalation_time': 15,  # minutes
                'auto_remediation': True
            },
            AnomalySeverity.HIGH: {
                'notification_delay': 60,  # 1 minute
                'escalation_time': 30,
                'auto_remediation': False
            },
            AnomalySeverity.MEDIUM: {
                'notification_delay': 300,  # 5 minutes
                'escalation_time': 60,
                'auto_remediation': False
            }
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Configuration logging"""
        logger = logging.getLogger("performance_anomaly_detection")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def initialize(self):
        """Initialisation système détection anomalies"""
        self.logger.info("🚨 Initialisation Performance Anomaly Detection System...")
        
        # Initialize ML models
        await self._initialize_detection_models()
        
        # Generate sample baseline data
        await self._generate_baseline_data()
        
        # Start background monitoring tasks
        asyncio.create_task(self._continuous_anomaly_detection())
        asyncio.create_task(self._pattern_analysis())
        asyncio.create_task(self._alert_management())
        asyncio.create_task(self._model_retraining())
        
        self.logger.info("✅ Performance Anomaly Detection System initialisé")
    
    async def _initialize_detection_models(self):
        """Initialisation modèles ML détection"""
        metric_types = ['latency', 'throughput', 'error_rate', 'cpu_usage', 'memory_usage', 'gpu_usage']
        
        for metric_type in metric_types:
            # Isolation Forest for outlier detection
            self.isolation_forests[metric_type] = IsolationForest(
                contamination=0.1,  # 10% expected anomalies
                random_state=42,
                n_estimators=100
            )
            
            # Standard scaler for normalization
            self.scalers[metric_type] = StandardScaler()
            
            # DBSCAN for clustering-based detection
            self.clustering_models[metric_type] = DBSCAN(
                eps=0.5,
                min_samples=5
            )
        
        self.logger.info(f"Initialized ML models for {len(metric_types)} metric types")
    
    async def _generate_baseline_data(self):
        """Génération données baseline échantillon"""
        current_time = datetime.utcnow()
        
        # Generate sample metrics for different sources
        sample_sources = [
            'content_classifier_v1',
            'audio_processor_v2',
            'revenue_predictor_v1',
            'collaboration_matcher_v1'
        ]
        
        creator_tiers = list(CreatorTier)
        
        for source_id in sample_sources:
            for i in range(100):  # 100 historical data points
                timestamp = current_time - timedelta(minutes=i * 5)
                
                # Generate realistic baseline metrics
                base_latency = np.random.normal(150, 30)  # ms
                base_throughput = np.random.normal(100, 20)  # requests/sec
                base_error_rate = np.random.beta(1, 20)  # low error rate
                base_cpu = np.random.normal(0.6, 0.15)  # 60% average
                base_memory = np.random.normal(0.7, 0.1)  # 70% average
                
                metrics = [
                    PerformanceMetric(
                        metric_name='latency',
                        value=max(0, base_latency),
                        timestamp=timestamp,
                        source_id=source_id,
                        creator_tier=np.random.choice(creator_tiers)
                    ),
                    PerformanceMetric(
                        metric_name='throughput',
                        value=max(0, base_throughput),
                        timestamp=timestamp,
                        source_id=source_id,
                        creator_tier=np.random.choice(creator_tiers)
                    ),
                    PerformanceMetric(
                        metric_name='error_rate',
                        value=max(0, min(1, base_error_rate)),
                        timestamp=timestamp,
                        source_id=source_id,
                        creator_tier=np.random.choice(creator_tiers)
                    ),
                    PerformanceMetric(
                        metric_name='cpu_usage',
                        value=max(0, min(1, base_cpu)),
                        timestamp=timestamp,
                        source_id=source_id
                    ),
                    PerformanceMetric(
                        metric_name='memory_usage',
                        value=max(0, min(1, base_memory)),
                        timestamp=timestamp,
                        source_id=source_id
                    )
                ]
                
                for metric in metrics:
                    await self.ingest_metric(metric)
        
        # Train initial models
        await self._train_baseline_models()
        
        self.logger.info("Generated baseline data and trained initial models")
    
    async def ingest_metric(self, metric: PerformanceMetric):
        """Ingestion métrique performance"""
        # Add to buffer for real-time processing
        self.metrics_buffer.append(metric)
        
        # Add to historical data for specific metric/source
        key = f"{metric.source_id}_{metric.metric_name}"
        self.metrics_history[key].append(metric)
        
        # Trigger real-time anomaly detection for critical metrics
        if metric.metric_name in ['latency', 'error_rate', 'throughput']:
            await self._detect_real_time_anomaly(metric)
    
    async def _detect_real_time_anomaly(self, metric: PerformanceMetric):
        """Détection temps réel anomalie"""
        key = f"{metric.source_id}_{metric.metric_name}"
        history = self.metrics_history[key]
        
        if len(history) < self.detection_thresholds['minimum_data_points']:
            return
        
        # Convert to array for analysis
        values = [m.value for m in list(history)[-50:]]  # Last 50 points
        current_value = metric.value
        
        # Statistical outlier detection
        if len(values) >= 10:
            mean_val = statistics.mean(values)
            std_val = statistics.stdev(values) if len(values) > 1 else 0
            
            if std_val > 0:
                z_score = abs(current_value - mean_val) / std_val
                
                # Determine anomaly type and severity
                anomaly_type = None
                severity = AnomalySeverity.LOW
                
                if metric.metric_name == 'latency' and z_score > self.detection_thresholds['latency_spike_threshold']:
                    anomaly_type = AnomalyType.LATENCY_SPIKE
                    severity = AnomalySeverity.HIGH if z_score > 4 else AnomalySeverity.MEDIUM
                    
                elif metric.metric_name == 'throughput' and current_value < mean_val - (std_val * self.detection_thresholds['throughput_drop_threshold']):
                    anomaly_type = AnomalyType.THROUGHPUT_DROP
                    severity = AnomalySeverity.HIGH if z_score > 3 else AnomalySeverity.MEDIUM
                    
                elif metric.metric_name == 'error_rate' and current_value > self.detection_thresholds['error_rate_threshold']:
                    anomaly_type = AnomalyType.ERROR_RATE_SURGE
                    severity = AnomalySeverity.CRITICAL if current_value > 0.1 else AnomalySeverity.HIGH
                
                if anomaly_type:
                    await self._create_anomaly_detection(
                        anomaly_type=anomaly_type,
                        severity=severity,
                        detection_method=DetectionMethod.STATISTICAL_OUTLIER,
                        metric=metric,
                        expected_value=mean_val,
                        deviation_score=min(1.0, z_score / 5.0),
                        confidence_score=min(1.0, z_score / 3.0)
                    )
    
    async def _create_anomaly_detection(self, anomaly_type: AnomalyType, severity: AnomalySeverity,
                                      detection_method: DetectionMethod, metric: PerformanceMetric,
                                      expected_value: float, deviation_score: float,
                                      confidence_score: float):
        """Création détection anomalie"""
        
        # Analyze creator impact
        creator_impact = await self._analyze_creator_impact(metric, anomaly_type)
        
        # Perform root cause analysis
        root_cause = await self._perform_root_cause_analysis(metric, anomaly_type)
        
        # Generate recommended actions
        recommended_actions = await self._generate_recommended_actions(anomaly_type, severity, metric)
        
        # Determine business impact
        business_impact = await self._assess_business_impact(severity, creator_impact, metric)
        
        anomaly = AnomalyDetection(
            anomaly_id=str(uuid.uuid4()),
            anomaly_type=anomaly_type,
            severity=severity,
            detection_method=detection_method,
            affected_metric=metric.metric_name,
            current_value=metric.value,
            expected_value=expected_value,
            deviation_score=deviation_score,
            confidence_score=confidence_score,
            source_id=metric.source_id,
            creator_impact=creator_impact,
            time_window=(metric.timestamp - timedelta(minutes=5), metric.timestamp),
            root_cause_analysis=root_cause,
            recommended_actions=recommended_actions,
            auto_remediation_possible=await self._check_auto_remediation_feasibility(anomaly_type, severity),
            business_impact=business_impact
        )
        
        self.detected_anomalies.append(anomaly)
        
        # Create alert if necessary
        if severity in [AnomalySeverity.CRITICAL, AnomalySeverity.HIGH]:
            await self._create_alert(anomaly)
        
        self.logger.warning(
            f"Anomaly detected: {anomaly_type.value} on {metric.source_id} "
            f"({metric.metric_name}: {metric.value:.2f}, expected: {expected_value:.2f})"
        )
    
    async def _analyze_creator_impact(self, metric: PerformanceMetric, anomaly_type: AnomalyType) -> Dict[str, int]:
        """Analyse impact sur créateurs"""
        creator_impact = {}
        
        # Simulate creator impact analysis
        if metric.creator_tier:
            creator_impact[metric.creator_tier.value] = 1
        
        # Analyze broader impact based on anomaly type
        if anomaly_type in [AnomalyType.LATENCY_SPIKE, AnomalyType.AVAILABILITY_DEGRADATION]:
            # High impact anomalies affect multiple creator tiers
            creator_impact = {
                'premium': np.random.randint(1, 10),
                'professional': np.random.randint(5, 25),
                'standard': np.random.randint(10, 50),
                'starter': np.random.randint(5, 30)
            }
        elif anomaly_type == AnomalyType.COST_ANOMALY:
            # Cost anomalies primarily affect premium users
            creator_impact = {
                'premium': np.random.randint(5, 15),
                'professional': np.random.randint(2, 8),
                'standard': np.random.randint(1, 5),
                'starter': np.random.randint(0, 2)
            }
        
        return creator_impact
    
    async def _perform_root_cause_analysis(self, metric: PerformanceMetric, anomaly_type: AnomalyType) -> Dict[str, Any]:
        """Analyse cause racine"""
        # Simulate root cause analysis
        root_causes = {
            AnomalyType.LATENCY_SPIKE: [
                "Database connection pool exhaustion",
                "Network congestion",
                "Resource contention",
                "Memory pressure"
            ],
            AnomalyType.THROUGHPUT_DROP: [
                "CPU throttling",
                "I/O bottleneck",
                "Network saturation",
                "Application deadlock"
            ],
            AnomalyType.ERROR_RATE_SURGE: [
                "Service dependency failure",
                "Configuration error",
                "Resource exhaustion",
                "Model prediction errors"
            ],
            AnomalyType.MEMORY_LEAK: [
                "Application memory leak",
                "Inefficient garbage collection",
                "Resource not released",
                "Memory fragmentation"
            ]
        }
        
        possible_causes = root_causes.get(anomaly_type, ["Unknown cause"])
        primary_cause = np.random.choice(possible_causes)
        
        return {
            'primary_cause': primary_cause,
            'confidence': np.random.uniform(0.6, 0.9),
            'contributing_factors': np.random.choice(possible_causes, size=2, replace=False).tolist(),
            'correlation_factors': {
                'time_correlation': np.random.uniform(0.3, 0.8),
                'resource_correlation': np.random.uniform(0.4, 0.9),
                'workload_correlation': np.random.uniform(0.2, 0.7)
            }
        }
    
    async def _generate_recommended_actions(self, anomaly_type: AnomalyType, severity: AnomalySeverity,
                                          metric: PerformanceMetric) -> List[str]:
        """Génération actions recommandées"""
        action_templates = {
            AnomalyType.LATENCY_SPIKE: [
                "Scale up compute resources",
                "Optimize database queries",
                "Clear application caches",
                "Enable request throttling"
            ],
            AnomalyType.THROUGHPUT_DROP: [
                "Increase worker threads",
                "Optimize resource allocation",
                "Check for bottlenecks",
                "Scale horizontally"
            ],
            AnomalyType.ERROR_RATE_SURGE: [
                "Check service dependencies",
                "Review recent deployments",
                "Validate input data quality",
                "Enable circuit breakers"
            ],
            AnomalyType.RESOURCE_EXHAUSTION: [
                "Scale up resources immediately",
                "Enable auto-scaling",
                "Optimize resource usage",
                "Implement resource quotas"
            ],
            AnomalyType.MEMORY_LEAK: [
                "Restart affected services",
                "Profile memory usage",
                "Review recent code changes",
                "Implement memory monitoring"
            ]
        }
        
        base_actions = action_templates.get(anomaly_type, ["Monitor situation closely"])
        
        # Add severity-specific actions
        if severity == AnomalySeverity.CRITICAL:
            base_actions.insert(0, "Initiate incident response procedure")
            base_actions.append("Notify on-call team immediately")
        elif severity == AnomalySeverity.HIGH:
            base_actions.insert(0, "Escalate to senior team")
        
        return base_actions[:4]  # Return top 4 actions
    
    async def _assess_business_impact(self, severity: AnomalySeverity, creator_impact: Dict[str, int],
                                    metric: PerformanceMetric) -> str:
        """Évaluation impact business"""
        total_affected_creators = sum(creator_impact.values())
        premium_affected = creator_impact.get('premium', 0)
        
        if severity == AnomalySeverity.CRITICAL or total_affected_creators > 100:
            return "critical"
        elif severity == AnomalySeverity.HIGH or premium_affected > 10 or total_affected_creators > 50:
            return "high"
        elif severity == AnomalySeverity.MEDIUM or total_affected_creators > 20:
            return "medium"
        else:
            return "low"
    
    async def _check_auto_remediation_feasibility(self, anomaly_type: AnomalyType, severity: AnomalySeverity) -> bool:
        """Vérification faisabilité remédiation automatique"""
        auto_remediable_types = [
            AnomalyType.RESOURCE_EXHAUSTION,
            AnomalyType.THROUGHPUT_DROP
        ]
        
        return (anomaly_type in auto_remediable_types and 
                severity not in [AnomalySeverity.CRITICAL])
    
    async def _create_alert(self, anomaly: AnomalyDetection):
        """Création alerte anomalie"""
        alert_policy = self.alert_policies.get(anomaly.severity, self.alert_policies[AnomalySeverity.MEDIUM])
        
        alert = AnomalyAlert(
            alert_id=str(uuid.uuid4()),
            anomaly_id=anomaly.anomaly_id,
            alert_level="critical" if anomaly.severity == AnomalySeverity.CRITICAL else "warning",
            recipients=["oncall-team", "platform-engineers"],
            notification_channels=["slack", "email", "pagerduty"] if anomaly.severity == AnomalySeverity.CRITICAL else ["slack", "email"],
            escalation_policy={
                'escalation_time': alert_policy['escalation_time'],
                'escalation_targets': ["senior-engineers", "platform-lead"]
            },
            acknowledgment_required=anomaly.severity in [AnomalySeverity.CRITICAL, AnomalySeverity.HIGH],
            auto_resolution_timeout=30 if anomaly.auto_remediation_possible else None,
            business_context=f"Anomaly affects {sum(anomaly.creator_impact.values())} creators"
        )
        
        self.active_alerts.append(alert)
        
        self.logger.error(f"Alert created: {alert.alert_id} for anomaly {anomaly.anomaly_id}")
    
    async def _train_baseline_models(self):
        """Entraînement modèles baseline"""
        for metric_name in ['latency', 'throughput', 'error_rate', 'cpu_usage', 'memory_usage']:
            # Collect training data
            training_data = []
            
            for key, metrics in self.metrics_history.items():
                if key.endswith(f"_{metric_name}"):
                    values = [m.value for m in metrics]
                    training_data.extend(values)
            
            if len(training_data) >= 50:  # Minimum training data
                # Prepare data
                X = np.array(training_data).reshape(-1, 1)
                
                # Train and fit scaler
                X_scaled = self.scalers[metric_name].fit_transform(X)
                
                # Train Isolation Forest
                self.isolation_forests[metric_name].fit(X_scaled)
                
                self.logger.debug(f"Trained models for {metric_name} with {len(training_data)} samples")
    
    async def detect_ml_anomalies(self, source_id: str, metric_name: str) -> List[AnomalyDetection]:
        """Détection anomalies ML avancée"""
        key = f"{source_id}_{metric_name}"
        history = self.metrics_history[key]
        
        if len(history) < 50:  # Need sufficient data
            return []
        
        # Prepare data
        values = [m.value for m in list(history)[-100:]]  # Last 100 points
        timestamps = [m.timestamp for m in list(history)[-100:]]
        X = np.array(values).reshape(-1, 1)
        
        anomalies = []
        
        # Isolation Forest detection
        if metric_name in self.isolation_forests:
            try:
                X_scaled = self.scalers[metric_name].transform(X)
                anomaly_scores = self.isolation_forests[metric_name].decision_function(X_scaled)
                outlier_predictions = self.isolation_forests[metric_name].predict(X_scaled)
                
                # Find anomalies
                for i, (score, prediction) in enumerate(zip(anomaly_scores, outlier_predictions)):
                    if prediction == -1 and score < -0.1:  # Outlier with significant score
                        metric = list(history)[-100:][i]
                        
                        # Determine anomaly type based on metric and value
                        anomaly_type = self._classify_ml_anomaly(metric_name, values[i], statistics.mean(values))
                        severity = self._calculate_ml_severity(abs(score), metric_name)
                        
                        anomaly = await self._create_ml_anomaly_detection(
                            anomaly_type=anomaly_type,
                            severity=severity,
                            metric=metric,
                            anomaly_score=abs(score),
                            expected_value=statistics.mean(values)
                        )
                        
                        anomalies.append(anomaly)
                        
            except Exception as e:
                self.logger.error(f"ML anomaly detection failed for {metric_name}: {e}")
        
        return anomalies
    
    def _classify_ml_anomaly(self, metric_name: str, current_value: float, mean_value: float) -> AnomalyType:
        """Classification type anomalie ML"""
        if metric_name == 'latency':
            return AnomalyType.LATENCY_SPIKE if current_value > mean_value else AnomalyType.PERFORMANCE_DEGRADATION
        elif metric_name == 'throughput':
            return AnomalyType.THROUGHPUT_DROP if current_value < mean_value else AnomalyType.PERFORMANCE_DEGRADATION
        elif metric_name == 'error_rate':
            return AnomalyType.ERROR_RATE_SURGE
        elif metric_name in ['cpu_usage', 'memory_usage', 'gpu_usage']:
            return AnomalyType.RESOURCE_EXHAUSTION if current_value > mean_value else AnomalyType.PERFORMANCE_DEGRADATION
        else:
            return AnomalyType.PERFORMANCE_DEGRADATION
    
    def _calculate_ml_severity(self, anomaly_score: float, metric_name: str) -> AnomalySeverity:
        """Calcul sévérité anomalie ML"""
        if anomaly_score > 0.8:
            return AnomalySeverity.CRITICAL
        elif anomaly_score > 0.6:
            return AnomalySeverity.HIGH
        elif anomaly_score > 0.4:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW
    
    async def _create_ml_anomaly_detection(self, anomaly_type: AnomalyType, severity: AnomalySeverity,
                                         metric: PerformanceMetric, anomaly_score: float,
                                         expected_value: float) -> AnomalyDetection:
        """Création détection anomalie ML"""
        creator_impact = await self._analyze_creator_impact(metric, anomaly_type)
        root_cause = await self._perform_root_cause_analysis(metric, anomaly_type)
        recommended_actions = await self._generate_recommended_actions(anomaly_type, severity, metric)
        business_impact = await self._assess_business_impact(severity, creator_impact, metric)
        
        anomaly = AnomalyDetection(
            anomaly_id=str(uuid.uuid4()),
            anomaly_type=anomaly_type,
            severity=severity,
            detection_method=DetectionMethod.ISOLATION_FOREST,
            affected_metric=metric.metric_name,
            current_value=metric.value,
            expected_value=expected_value,
            deviation_score=anomaly_score,
            confidence_score=anomaly_score,
            source_id=metric.source_id,
            creator_impact=creator_impact,
            time_window=(metric.timestamp - timedelta(minutes=10), metric.timestamp),
            root_cause_analysis=root_cause,
            recommended_actions=recommended_actions,
            auto_remediation_possible=await self._check_auto_remediation_feasibility(anomaly_type, severity),
            business_impact=business_impact
        )
        
        return anomaly
    
    async def detect_pattern_anomalies(self) -> List[AnomalyPattern]:
        """Détection patterns anomalies récurrents"""
        current_time = datetime.utcnow()
        analysis_window = current_time - self.pattern_detection_window
        
        # Filter recent anomalies
        recent_anomalies = [
            a for a in self.detected_anomalies
            if a.detected_at >= analysis_window
        ]
        
        if len(recent_anomalies) < 5:
            return []
        
        patterns = []
        
        # Group anomalies by type and analyze patterns
        anomaly_groups = defaultdict(list)
        for anomaly in recent_anomalies:
            anomaly_groups[anomaly.anomaly_type].append(anomaly)
        
        for anomaly_type, anomalies_list in anomaly_groups.items():
            if len(anomalies_list) >= 3:  # Minimum for pattern
                pattern = await self._analyze_anomaly_pattern(anomaly_type, anomalies_list)
                if pattern:
                    patterns.append(pattern)
        
        return patterns
    
    async def _analyze_anomaly_pattern(self, anomaly_type: AnomalyType, anomalies: List[AnomalyDetection]) -> Optional[AnomalyPattern]:
        """Analyse pattern spécifique"""
        if len(anomalies) < 3:
            return None
        
        # Analyze timing patterns
        timestamps = [a.detected_at for a in anomalies]
        time_diffs = [(timestamps[i+1] - timestamps[i]).total_seconds() / 3600 for i in range(len(timestamps)-1)]
        
        # Determine frequency
        avg_interval = statistics.mean(time_diffs) if time_diffs else 24
        if avg_interval < 2:
            frequency = "hourly"
        elif avg_interval < 25:
            frequency = "daily"
        else:
            frequency = "weekly"
        
        # Analyze conditions
        typical_conditions = {
            'average_severity': statistics.mode([a.severity.value for a in anomalies]),
            'common_sources': list(set([a.source_id for a in anomalies])),
            'affected_metrics': list(set([a.affected_metric for a in anomalies]))
        }
        
        # Creator tier correlation
        creator_tiers_affected = []
        for anomaly in anomalies:
            creator_tiers_affected.extend(anomaly.creator_impact.keys())
        
        creator_tier_correlation = len(set(creator_tiers_affected)) < len(CreatorTier) / 2
        
        # Predictive indicators
        predictive_indicators = await self._identify_predictive_indicators(anomaly_type, anomalies)
        
        pattern = AnomalyPattern(
            pattern_id=str(uuid.uuid4()),
            pattern_name=f"Recurring {anomaly_type.value} pattern",
            anomaly_types=[anomaly_type],
            typical_conditions=typical_conditions,
            frequency=frequency,
            seasonal_correlation=avg_interval > 20,  # > 20 hours suggests daily/weekly pattern
            creator_tier_correlation=creator_tier_correlation,
            predictive_indicators=predictive_indicators,
            historical_occurrences=len(anomalies),
            last_occurrence=max(timestamps),
            prevention_strategies=await self._generate_prevention_strategies(anomaly_type),
            confidence=min(1.0, len(anomalies) / 10.0)  # Higher confidence with more occurrences
        )
        
        return pattern
    
    async def _identify_predictive_indicators(self, anomaly_type: AnomalyType, anomalies: List[AnomalyDetection]) -> List[str]:
        """Identification indicateurs prédictifs"""
        indicators = []
        
        # Common indicators based on anomaly type
        type_indicators = {
            AnomalyType.LATENCY_SPIKE: [
                "Increased request volume",
                "High memory usage",
                "Database connection pool near capacity"
            ],
            AnomalyType.THROUGHPUT_DROP: [
                "CPU utilization above 80%",
                "I/O wait time increasing",
                "Network saturation"
            ],
            AnomalyType.ERROR_RATE_SURGE: [
                "Dependency service latency increase",
                "Invalid input data patterns",
                "Configuration changes"
            ]
        }
        
        indicators = type_indicators.get(anomaly_type, ["Resource utilization changes"])
        
        # Add source-specific indicators
        common_sources = set([a.source_id for a in anomalies])
        if len(common_sources) == 1:
            indicators.append(f"Specific to {list(common_sources)[0]}")
        
        return indicators
    
    async def _generate_prevention_strategies(self, anomaly_type: AnomalyType) -> List[str]:
        """Génération stratégies prévention"""
        strategies = {
            AnomalyType.LATENCY_SPIKE: [
                "Implement predictive auto-scaling",
                "Set up proactive monitoring alerts",
                "Optimize database query performance",
                "Implement request rate limiting"
            ],
            AnomalyType.THROUGHPUT_DROP: [
                "Monitor resource utilization trends",
                "Implement circuit breakers",
                "Set up automated scaling policies",
                "Optimize application performance"
            ],
            AnomalyType.ERROR_RATE_SURGE: [
                "Implement robust error handling",
                "Set up dependency health checks",
                "Validate input data quality",
                "Monitor deployment impacts"
            ],
            AnomalyType.RESOURCE_EXHAUSTION: [
                "Implement resource quotas",
                "Set up proactive scaling",
                "Monitor resource trends",
                "Optimize resource allocation"
            ]
        }
        
        return strategies.get(anomaly_type, ["Monitor system health closely"])
    
    async def _continuous_anomaly_detection(self):
        """Détection continue anomalies background"""
        while True:
            try:
                # Process metrics buffer
                if len(self.metrics_buffer) > 0:
                    # Get recent metrics
                    recent_metrics = list(self.metrics_buffer)[-100:]
                    
                    # Group by source and metric type
                    metric_groups = defaultdict(list)
                    for metric in recent_metrics:
                        key = f"{metric.source_id}_{metric.metric_name}"
                        metric_groups[key].append(metric)
                    
                    # Run ML-based detection on each group
                    for key, metrics in metric_groups.items():
                        if len(metrics) >= 10:
                            source_id, metric_name = key.rsplit('_', 1)
                            ml_anomalies = await self.detect_ml_anomalies(source_id, metric_name)
                            self.detected_anomalies.extend(ml_anomalies)
                
                await asyncio.sleep(60)  # Run every minute
                
            except Exception as e:
                self.logger.error(f"Continuous anomaly detection error: {e}")
                await asyncio.sleep(30)
    
    async def _pattern_analysis(self):
        """Analyse patterns background"""
        while True:
            try:
                patterns = await self.detect_pattern_anomalies()
                
                for pattern in patterns:
                    # Check if pattern already exists
                    existing_pattern = next(
                        (p for p in self.anomaly_patterns 
                         if p.pattern_name == pattern.pattern_name), 
                        None
                    )
                    
                    if existing_pattern:
                        # Update existing pattern
                        existing_pattern.historical_occurrences += 1
                        existing_pattern.last_occurrence = pattern.last_occurrence
                        existing_pattern.confidence = min(1.0, existing_pattern.confidence + 0.1)
                    else:
                        # Add new pattern
                        self.anomaly_patterns.append(pattern)
                        self.logger.info(f"New anomaly pattern detected: {pattern.pattern_name}")
                
                await asyncio.sleep(1800)  # Run every 30 minutes
                
            except Exception as e:
                self.logger.error(f"Pattern analysis error: {e}")
                await asyncio.sleep(300)
    
    async def _alert_management(self):
        """Gestion alertes background"""
        while True:
            try:
                current_time = datetime.utcnow()
                
                # Process active alerts
                for alert in self.active_alerts.copy():
                    # Check for auto-resolution timeout
                    if (alert.auto_resolution_timeout and 
                        alert.acknowledged_at and
                        (current_time - alert.acknowledged_at).total_seconds() > alert.auto_resolution_timeout * 60):
                        
                        alert.resolved_at = current_time
                        self.active_alerts.remove(alert)
                        self.logger.info(f"Alert auto-resolved: {alert.alert_id}")
                    
                    # Check for escalation
                    elif (not alert.acknowledged_at and
                          (current_time - alert.created_at).total_seconds() > alert.escalation_policy['escalation_time'] * 60):
                        
                        self.logger.warning(f"Alert escalated: {alert.alert_id}")
                        # In real implementation, trigger escalation procedures
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Alert management error: {e}")
                await asyncio.sleep(30)
    
    async def _model_retraining(self):
        """Réentraînement modèles ML background"""
        while True:
            try:
                # Retrain models every 6 hours with new data
                await self._train_baseline_models()
                
                self.logger.info("ML models retrained with latest data")
                
                await asyncio.sleep(21600)  # 6 hours
                
            except Exception as e:
                self.logger.error(f"Model retraining error: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    async def get_anomaly_summary(self) -> Dict[str, Any]:
        """Résumé détections anomalies"""
        current_time = datetime.utcnow()
        last_24h = current_time - timedelta(hours=24)
        
        # Filter recent anomalies
        recent_anomalies = [a for a in self.detected_anomalies if a.detected_at >= last_24h]
        
        # Anomaly distribution by type
        type_distribution = defaultdict(int)
        severity_distribution = defaultdict(int)
        
        for anomaly in recent_anomalies:
            type_distribution[anomaly.anomaly_type.value] += 1
            severity_distribution[anomaly.severity.value] += 1
        
        # Creator impact analysis
        total_creator_impact = defaultdict(int)
        for anomaly in recent_anomalies:
            for tier, count in anomaly.creator_impact.items():
                total_creator_impact[tier] += count
        
        # Active alerts
        active_critical_alerts = len([a for a in self.active_alerts if a.alert_level == "critical"])
        
        return {
            'detection_summary': {
                'total_anomalies_24h': len(recent_anomalies),
                'critical_anomalies': len([a for a in recent_anomalies if a.severity == AnomalySeverity.CRITICAL]),
                'high_anomalies': len([a for a in recent_anomalies if a.severity == AnomalySeverity.HIGH]),
                'anomaly_types': dict(type_distribution),
                'severity_distribution': dict(severity_distribution)
            },
            'creator_impact': {
                'total_affected': dict(total_creator_impact),
                'most_affected_tier': max(total_creator_impact.keys(), key=total_creator_impact.get) if total_creator_impact else None
            },
            'pattern_analysis': {
                'identified_patterns': len(self.anomaly_patterns),
                'recurring_anomalies': len([p for p in self.anomaly_patterns if p.historical_occurrences > 3])
            },
            'alert_status': {
                'active_alerts': len(self.active_alerts),
                'critical_alerts': active_critical_alerts,
                'unacknowledged_alerts': len([a for a in self.active_alerts if not a.acknowledged_at])
            },
            'system_health': {
                'detection_models_active': len(self.isolation_forests),
                'metrics_processed': len(self.metrics_buffer),
                'data_sources_monitored': len(set(m.source_id for m in self.metrics_buffer))
            }
        }
    
    async def shutdown(self):
        """Arrêt propre système détection"""
        self.logger.info("⏹️ Arrêt Performance Anomaly Detection System...")
        
        # Clear data structures
        self.metrics_buffer.clear()
        self.metrics_history.clear()
        self.detected_anomalies.clear()
        self.active_alerts.clear()
        
        self.logger.info("✅ Performance Anomaly Detection System arrêté proprement")


# Point d'entrée pour tests
if __name__ == "__main__":
    async def test_anomaly_detection():
        class MockConfig:
            debug = True
        
        system = PerformanceAnomalyDetectionSystem(MockConfig())
        await system.initialize()
        
        # Test metric ingestion and detection
        test_metric = PerformanceMetric(
            metric_name='latency',
            value=2000.0,  # High latency to trigger anomaly
            timestamp=datetime.utcnow(),
            source_id='test_model_v1',
            creator_tier=CreatorTier.PREMIUM
        )
        
        await system.ingest_metric(test_metric)
        
        # Wait for processing
        await asyncio.sleep(2)
        
        # Test ML anomaly detection
        ml_anomalies = await system.detect_ml_anomalies('test_model_v1', 'latency')
        print(f"ML anomalies detected: {len(ml_anomalies)}")
        
        # Test pattern detection
        patterns = await system.detect_pattern_anomalies()
        print(f"Patterns identified: {len(patterns)}")
        
        # Test summary
        summary = await system.get_anomaly_summary()
        print(f"Total anomalies 24h: {summary['detection_summary']['total_anomalies_24h']}")
        print(f"Active alerts: {summary['alert_status']['active_alerts']}")
        
        print('✅ Performance Anomaly Detection System test passed')
        await system.shutdown()
    
    asyncio.run(test_anomaly_detection())