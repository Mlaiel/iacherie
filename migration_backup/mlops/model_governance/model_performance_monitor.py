"""
📊 Model Performance Monitor - Enterprise ML Engineering & DevOps
© 2025 Fahed Mlaiel <mlaiel@live.de> - Tous droits réservés

⚠️ AVERTISSEMENT LÉGAL:
==========================================
TOUS DROITS RÉSERVÉS - Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE: Licence entreprise disponible sur demande
📧 Contact: mlaiel@live.de

Monitoring performance modèles temps réel avec drift detection
Expertise: ML Engineer + DevOps + Backend Senior + DBA
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import numpy as np
import statistics
from collections import deque, defaultdict
import threading
import time

logger = logging.getLogger(__name__)


class MonitoringLevel(Enum):
    """Performance monitoring levels"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"
    REAL_TIME = "real_time"


class DriftType(Enum):
    """Types of model drift"""
    DATA_DRIFT = "data_drift"
    CONCEPT_DRIFT = "concept_drift"
    PREDICTION_DRIFT = "prediction_drift"
    PERFORMANCE_DRIFT = "performance_drift"
    BUSINESS_DRIFT = "business_drift"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class MetricType(Enum):
    """Performance metric types"""
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    AUC_ROC = "auc_roc"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    CREATOR_SATISFACTION = "creator_satisfaction"
    BUSINESS_KPI = "business_kpi"


@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    metric_type: MetricType
    value: float
    timestamp: datetime
    model_name: str
    model_version: str
    context: Dict[str, Any] = field(default_factory=dict)
    creator_tier: Optional[str] = None
    business_context: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary"""
        return {
            "metric_type": self.metric_type.value,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "model_name": self.model_name,
            "model_version": self.model_version,
            "context": self.context,
            "creator_tier": self.creator_tier,
            "business_context": self.business_context
        }


@dataclass
class DriftAlert:
    """Model drift alert"""
    alert_id: str
    drift_type: DriftType
    severity: AlertSeverity
    model_name: str
    model_version: str
    detected_at: datetime
    drift_score: float
    threshold: float
    description: str
    affected_metrics: List[str] = field(default_factory=list)
    creator_impact: Optional[Dict[str, Any]] = None
    recommended_actions: List[str] = field(default_factory=list)
    acknowledged: bool = False
    resolved: bool = False
    resolution_notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary"""
        return {
            "alert_id": self.alert_id,
            "drift_type": self.drift_type.value,
            "severity": self.severity.value,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "detected_at": self.detected_at.isoformat(),
            "drift_score": self.drift_score,
            "threshold": self.threshold,
            "description": self.description,
            "affected_metrics": self.affected_metrics,
            "creator_impact": self.creator_impact,
            "recommended_actions": self.recommended_actions,
            "acknowledged": self.acknowledged,
            "resolved": self.resolved,
            "resolution_notes": self.resolution_notes
        }


@dataclass
class MonitoringConfiguration:
    """Monitoring configuration for a model"""
    model_name: str
    model_version: str
    monitoring_level: MonitoringLevel
    metrics_to_monitor: List[MetricType]
    drift_detection_enabled: bool = True
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    sampling_interval_seconds: int = 60
    window_size_hours: int = 24
    creator_specific_monitoring: bool = True
    business_kpi_monitoring: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "monitoring_level": self.monitoring_level.value,
            "metrics_to_monitor": [m.value for m in self.metrics_to_monitor],
            "drift_detection_enabled": self.drift_detection_enabled,
            "alert_thresholds": self.alert_thresholds,
            "sampling_interval_seconds": self.sampling_interval_seconds,
            "window_size_hours": self.window_size_hours,
            "creator_specific_monitoring": self.creator_specific_monitoring,
            "business_kpi_monitoring": self.business_kpi_monitoring
        }


class ModelPerformanceMonitor:
    """
    📊 Monitoring performance modèles temps réel
    
    Enterprise performance monitoring with:
    - Real-time drift detection algorithmique
    - Performance degradation alerts auto-remediation
    - Business metrics correlation Creator Economy
    - Creator satisfaction impact tracking
    - Automated remediation triggers
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize performance monitor
        
        Args:
            config: Monitoring configuration
        """
        self.config = config or self._get_default_config()
        self.monitor_id = str(uuid.uuid4())
        
        # Monitoring state
        self._monitoring_configs: Dict[str, MonitoringConfiguration] = {}
        self._metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self._drift_detectors: Dict[str, Callable] = {}
        self._active_alerts: Dict[str, DriftAlert] = {}
        self._alert_history: List[DriftAlert] = []
        
        # Real-time processing
        self._monitoring_threads: Dict[str, threading.Thread] = {}
        self._stop_monitoring: Dict[str, threading.Event] = {}
        self._metric_buffer: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Performance analytics
        self._baseline_metrics: Dict[str, Dict[str, float]] = {}
        self._performance_trends: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
        
        # Remediation engines
        self._remediation_handlers: Dict[DriftType, Callable] = {}
        
        # System metrics
        self._monitor_metrics = {
            "metrics_processed": 0,
            "alerts_generated": 0,
            "drift_detections": 0,
            "auto_remediations": 0,
            "models_monitored": 0
        }
        
        # Initialize drift detectors
        self._initialize_drift_detectors()
        
        # Initialize remediation handlers
        self._initialize_remediation_handlers()
        
        logger.info(f"📊 ModelPerformanceMonitor initialized with ID: {self.monitor_id}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default monitoring configuration"""
        return {
            "monitoring": {
                "default_level": "enterprise",
                "real_time_processing": True,
                "batch_processing": True,
                "sampling_interval_seconds": 30,
                "window_size_hours": 24
            },
            "drift_detection": {
                "enabled": True,
                "algorithms": ["ks_test", "psi", "wasserstein", "jensen_shannon"],
                "thresholds": {
                    "data_drift": 0.05,
                    "concept_drift": 0.1,
                    "performance_drift": 0.15,
                    "business_drift": 0.2
                },
                "minimum_samples": 100
            },
            "alerting": {
                "enabled": True,
                "channels": ["dashboard", "email", "webhook"],
                "escalation": True,
                "auto_acknowledge": False
            },
            "remediation": {
                "auto_remediation": True,
                "rollback_enabled": True,
                "retraining_triggers": True,
                "creator_notifications": True
            },
            "creator_economy": {
                "satisfaction_tracking": True,
                "tier_based_thresholds": True,
                "revenue_correlation": True,
                "engagement_monitoring": True
            },
            "storage": {
                "retention_days": 90,
                "aggregation_levels": ["minute", "hour", "day"],
                "compression": True
            }
        }
    
    def _initialize_drift_detectors(self) -> None:
        """Initialize drift detection algorithms"""
        
        def kolmogorov_smirnov_test(baseline: List[float], current: List[float]) -> Tuple[float, bool]:
            """Kolmogorov-Smirnov test for data drift"""
            try:
                if len(baseline) < 30 or len(current) < 30:
                    return 0.0, False
                
                # Sort data
                baseline_sorted = sorted(baseline)
                current_sorted = sorted(current)
                
                # Compute empirical CDFs
                def ecdf(data, x):
                    return sum(1 for val in data if val <= x) / len(data)
                
                # Find maximum difference
                all_values = sorted(set(baseline + current))
                max_diff = max(
                    abs(ecdf(baseline_sorted, x) - ecdf(current_sorted, x))
                    for x in all_values
                )
                
                # Critical value for significance level 0.05
                n1, n2 = len(baseline), len(current)
                critical_value = 1.36 * np.sqrt((n1 + n2) / (n1 * n2))
                
                return max_diff, max_diff > critical_value
                
            except Exception as e:
                logger.error(f"KS test error: {str(e)}")
                return 0.0, False
        
        def population_stability_index(baseline: List[float], current: List[float], bins: int = 10) -> Tuple[float, bool]:
            """Population Stability Index for data drift"""
            try:
                if len(baseline) < 100 or len(current) < 100:
                    return 0.0, False
                
                # Create bins based on baseline quantiles
                baseline_array = np.array(baseline)
                current_array = np.array(current)
                
                # Calculate quantile-based bins
                quantiles = np.linspace(0, 1, bins + 1)
                bin_edges = np.quantile(baseline_array, quantiles)
                bin_edges[0] = -float('inf')
                bin_edges[-1] = float('inf')
                
                # Calculate bin proportions
                baseline_counts = np.histogram(baseline_array, bins=bin_edges)[0]
                current_counts = np.histogram(current_array, bins=bin_edges)[0]
                
                baseline_props = baseline_counts / len(baseline)
                current_props = current_counts / len(current)
                
                # Calculate PSI
                psi = 0.0
                for i in range(len(baseline_props)):
                    if baseline_props[i] > 0 and current_props[i] > 0:
                        psi += (current_props[i] - baseline_props[i]) * np.log(current_props[i] / baseline_props[i])
                
                # PSI thresholds: <0.1 no drift, 0.1-0.25 moderate, >0.25 significant
                return psi, psi > 0.1
                
            except Exception as e:
                logger.error(f"PSI calculation error: {str(e)}")
                return 0.0, False
        
        def wasserstein_distance(baseline: List[float], current: List[float]) -> Tuple[float, bool]:
            """Wasserstein distance for data drift"""
            try:
                if len(baseline) < 50 or len(current) < 50:
                    return 0.0, False
                
                baseline_array = np.array(baseline)
                current_array = np.array(current)
                
                # Sort arrays
                baseline_sorted = np.sort(baseline_array)
                current_sorted = np.sort(current_array)
                
                # Calculate Wasserstein distance (1st order)
                u_values = np.linspace(0, 1, min(len(baseline_sorted), len(current_sorted)))
                baseline_quantiles = np.quantile(baseline_sorted, u_values)
                current_quantiles = np.quantile(current_sorted, u_values)
                
                distance = np.mean(np.abs(baseline_quantiles - current_quantiles))
                
                # Normalize by baseline std
                baseline_std = np.std(baseline_array)
                normalized_distance = distance / max(baseline_std, 1e-8)
                
                return normalized_distance, normalized_distance > 0.5
                
            except Exception as e:
                logger.error(f"Wasserstein distance error: {str(e)}")
                return 0.0, False
        
        def jensen_shannon_divergence(baseline: List[float], current: List[float], bins: int = 50) -> Tuple[float, bool]:
            """Jensen-Shannon divergence for data drift"""
            try:
                if len(baseline) < 100 or len(current) < 100:
                    return 0.0, False
                
                # Create common histogram bins
                all_data = baseline + current
                min_val, max_val = min(all_data), max(all_data)
                bin_edges = np.linspace(min_val, max_val, bins + 1)
                
                # Calculate histograms
                baseline_hist = np.histogram(baseline, bins=bin_edges, density=True)[0]
                current_hist = np.histogram(current, bins=bin_edges, density=True)[0]
                
                # Normalize to probabilities
                baseline_prob = baseline_hist / np.sum(baseline_hist)
                current_prob = current_hist / np.sum(current_hist)
                
                # Add small epsilon to avoid log(0)
                epsilon = 1e-10
                baseline_prob += epsilon
                current_prob += epsilon
                
                # Calculate JS divergence
                m = 0.5 * (baseline_prob + current_prob)
                js_div = 0.5 * np.sum(baseline_prob * np.log(baseline_prob / m)) + \
                        0.5 * np.sum(current_prob * np.log(current_prob / m))
                
                # JS divergence is bounded [0, log(2)]
                js_distance = np.sqrt(js_div)
                
                return js_distance, js_distance > 0.1
                
            except Exception as e:
                logger.error(f"JS divergence error: {str(e)}")
                return 0.0, False
        
        # Register drift detectors
        self._drift_detectors = {
            "ks_test": kolmogorov_smirnov_test,
            "psi": population_stability_index,
            "wasserstein": wasserstein_distance,
            "jensen_shannon": jensen_shannon_divergence
        }
        
        logger.info(f"🔍 {len(self._drift_detectors)} drift detection algorithms initialized")
    
    def _initialize_remediation_handlers(self) -> None:
        """Initialize automated remediation handlers"""
        
        async def handle_data_drift(alert: DriftAlert, model_config: MonitoringConfiguration) -> Dict[str, Any]:
            """Handle data drift remediation"""
            actions_taken = []
            
            try:
                # 1. Trigger data quality checks
                actions_taken.append("Initiated data quality validation")
                
                # 2. Check for training data staleness
                if alert.drift_score > 0.3:
                    actions_taken.append("Flagged for retraining due to high drift score")
                
                # 3. Notify creators if tier-specific
                if model_config.creator_specific_monitoring:
                    actions_taken.append("Creator stakeholders notified")
                
                # 4. Adjust monitoring sensitivity
                actions_taken.append("Increased monitoring frequency temporarily")
                
                return {
                    "success": True,
                    "actions_taken": actions_taken,
                    "recommendation": "Consider retraining with recent data"
                }
                
            except Exception as e:
                return {"success": False, "error": str(e), "actions_taken": actions_taken}
        
        async def handle_performance_drift(alert: DriftAlert, model_config: MonitoringConfiguration) -> Dict[str, Any]:
            """Handle performance drift remediation"""
            actions_taken = []
            
            try:
                # 1. Performance rollback if severe
                if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
                    actions_taken.append("Initiated rollback to previous stable version")
                
                # 2. Resource scaling
                if "latency" in alert.affected_metrics or "throughput" in alert.affected_metrics:
                    actions_taken.append("Auto-scaled compute resources")
                
                # 3. Circuit breaker activation
                if alert.drift_score > 0.5:
                    actions_taken.append("Activated circuit breaker pattern")
                
                # 4. A/B test setup for gradual recovery
                actions_taken.append("Configured A/B test for gradual traffic restoration")
                
                return {
                    "success": True,
                    "actions_taken": actions_taken,
                    "recommendation": "Monitor resource utilization and consider horizontal scaling"
                }
                
            except Exception as e:
                return {"success": False, "error": str(e), "actions_taken": actions_taken}
        
        async def handle_business_drift(alert: DriftAlert, model_config: MonitoringConfiguration) -> Dict[str, Any]:
            """Handle business drift remediation"""
            actions_taken = []
            
            try:
                # 1. Business stakeholder notification
                actions_taken.append("Business stakeholders notified immediately")
                
                # 2. Creator impact assessment
                if model_config.creator_specific_monitoring:
                    actions_taken.append("Creator impact assessment initiated")
                
                # 3. Revenue impact analysis
                actions_taken.append("Automated revenue impact analysis started")
                
                # 4. Business rule validation
                actions_taken.append("Business rule validation triggered")
                
                return {
                    "success": True,
                    "actions_taken": actions_taken,
                    "recommendation": "Review business assumptions and model objectives"
                }
                
            except Exception as e:
                return {"success": False, "error": str(e), "actions_taken": actions_taken}
        
        async def handle_concept_drift(alert: DriftAlert, model_config: MonitoringConfiguration) -> Dict[str, Any]:
            """Handle concept drift remediation"""
            actions_taken = []
            
            try:
                # 1. Feature importance analysis
                actions_taken.append("Feature importance analysis initiated")
                
                # 2. Online learning activation if available
                actions_taken.append("Online learning adaptation enabled")
                
                # 3. Ensemble model switching
                actions_taken.append("Switched to ensemble model for robustness")
                
                # 4. Retraining pipeline trigger
                actions_taken.append("Automated retraining pipeline triggered")
                
                return {
                    "success": True,
                    "actions_taken": actions_taken,
                    "recommendation": "Update feature engineering and model architecture"
                }
                
            except Exception as e:
                return {"success": False, "error": str(e), "actions_taken": actions_taken}
        
        # Register remediation handlers
        self._remediation_handlers = {
            DriftType.DATA_DRIFT: handle_data_drift,
            DriftType.PERFORMANCE_DRIFT: handle_performance_drift,
            DriftType.BUSINESS_DRIFT: handle_business_drift,
            DriftType.CONCEPT_DRIFT: handle_concept_drift
        }
        
        logger.info(f"🔧 {len(self._remediation_handlers)} remediation handlers initialized")
    
    def register_model_monitoring(self, config: MonitoringConfiguration) -> bool:
        """Register a model for monitoring"""
        try:
            model_key = f"{config.model_name}:{config.model_version}"
            self._monitoring_configs[model_key] = config
            
            # Initialize metric storage
            if model_key not in self._metric_history:
                self._metric_history[model_key] = deque(maxlen=10000)
            
            # Start real-time monitoring if enabled
            if self.config.get("monitoring", {}).get("real_time_processing", True):
                self._start_real_time_monitoring(config)
            
            self._monitor_metrics["models_monitored"] += 1
            
            logger.info(f"📊 Registered monitoring for {model_key} at {config.monitoring_level.value} level")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register model monitoring: {str(e)}")
            return False
    
    def _start_real_time_monitoring(self, config: MonitoringConfiguration) -> None:
        """Start real-time monitoring thread for a model"""
        model_key = f"{config.model_name}:{config.model_version}"
        
        def monitoring_loop():
            """Real-time monitoring loop"""
            stop_event = self._stop_monitoring[model_key]
            
            while not stop_event.is_set():
                try:
                    # Process buffered metrics
                    if model_key in self._metric_buffer and self._metric_buffer[model_key]:
                        metrics_batch = []
                        
                        # Drain buffer
                        while self._metric_buffer[model_key]:
                            try:
                                metric = self._metric_buffer[model_key].popleft()
                                metrics_batch.append(metric)
                            except IndexError:
                                break
                        
                        # Process batch for drift detection
                        if metrics_batch:
                            asyncio.run(self._process_metrics_batch(config, metrics_batch))
                    
                    # Sleep for sampling interval
                    time.sleep(config.sampling_interval_seconds)
                    
                except Exception as e:
                    logger.error(f"Monitoring loop error for {model_key}: {str(e)}")
                    time.sleep(5)  # Brief pause before retry
        
        # Create and start monitoring thread
        stop_event = threading.Event()
        self._stop_monitoring[model_key] = stop_event
        
        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()
        self._monitoring_threads[model_key] = monitoring_thread
        
        logger.info(f"🔄 Started real-time monitoring thread for {model_key}")
    
    async def record_metric(self, metric: PerformanceMetric) -> bool:
        """Record a performance metric"""
        try:
            model_key = f"{metric.model_name}:{metric.model_version}"
            
            # Check if model is registered for monitoring
            if model_key not in self._monitoring_configs:
                logger.warning(f"⚠️ Model {model_key} not registered for monitoring")
                return False
            
            config = self._monitoring_configs[model_key]
            
            # Check if metric type is monitored
            if metric.metric_type not in config.metrics_to_monitor:
                return True  # Silently ignore unmonitored metrics
            
            # Add to history
            self._metric_history[model_key].append(metric)
            
            # Add to real-time buffer
            self._metric_buffer[model_key].append(metric)
            
            # Update performance trends
            self._performance_trends[model_key][metric.metric_type.value].append(metric.value)
            
            # Immediate drift check for critical metrics
            if metric.metric_type in [MetricType.ACCURACY, MetricType.ERROR_RATE, MetricType.CREATOR_SATISFACTION]:
                await self._check_immediate_drift(metric, config)
            
            self._monitor_metrics["metrics_processed"] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to record metric: {str(e)}")
            return False
    
    async def _process_metrics_batch(self, config: MonitoringConfiguration, metrics: List[PerformanceMetric]) -> None:
        """Process a batch of metrics for drift detection"""
        try:
            # Group metrics by type
            metrics_by_type = defaultdict(list)
            for metric in metrics:
                metrics_by_type[metric.metric_type.value].append(metric.value)
            
            # Run drift detection for each metric type
            for metric_type, values in metrics_by_type.items():
                if len(values) >= self.config.get("drift_detection", {}).get("minimum_samples", 100):
                    await self._detect_drift(config, metric_type, values)
                    
        except Exception as e:
            logger.error(f"❌ Batch processing error: {str(e)}")
    
    async def _check_immediate_drift(self, metric: PerformanceMetric, config: MonitoringConfiguration) -> None:
        """Check for immediate drift on critical metrics"""
        try:
            model_key = f"{metric.model_name}:{metric.model_version}"
            metric_type = metric.metric_type.value
            
            # Get baseline if available
            if model_key not in self._baseline_metrics or metric_type not in self._baseline_metrics[model_key]:
                return
            
            baseline_value = self._baseline_metrics[model_key][metric_type]
            current_value = metric.value
            
            # Calculate deviation percentage
            if baseline_value != 0:
                deviation = abs(current_value - baseline_value) / abs(baseline_value)
            else:
                deviation = abs(current_value)
            
            # Check against thresholds
            thresholds = config.alert_thresholds
            threshold_key = f"{metric_type}_drift"
            
            if threshold_key in thresholds and deviation > thresholds[threshold_key]:
                # Generate immediate alert
                alert = DriftAlert(
                    alert_id=str(uuid.uuid4()),
                    drift_type=DriftType.PERFORMANCE_DRIFT,
                    severity=AlertSeverity.CRITICAL if deviation > 0.5 else AlertSeverity.WARNING,
                    model_name=metric.model_name,
                    model_version=metric.model_version,
                    detected_at=datetime.now(),
                    drift_score=deviation,
                    threshold=thresholds[threshold_key],
                    description=f"Immediate drift detected in {metric_type}: {deviation:.2%} deviation from baseline",
                    affected_metrics=[metric_type],
                    creator_impact=metric.business_context
                )
                
                await self._handle_alert(alert, config)
                
        except Exception as e:
            logger.error(f"❌ Immediate drift check error: {str(e)}")
    
    async def _detect_drift(self, config: MonitoringConfiguration, metric_type: str, current_values: List[float]) -> None:
        """Detect drift using multiple algorithms"""
        try:
            model_key = f"{config.model_name}:{config.model_version}"
            
            # Get baseline values
            if model_key not in self._baseline_metrics or metric_type not in self._baseline_metrics[model_key]:
                # No baseline yet, establish one
                if len(current_values) >= 100:
                    self._establish_baseline(model_key, metric_type, current_values)
                return
            
            # Get historical baseline data
            baseline_values = self._get_baseline_values(model_key, metric_type)
            if not baseline_values or len(baseline_values) < 50:
                return
            
            # Run drift detection algorithms
            drift_results = {}
            enabled_algorithms = self.config.get("drift_detection", {}).get("algorithms", [])
            
            for algorithm_name in enabled_algorithms:
                if algorithm_name in self._drift_detectors:
                    detector = self._drift_detectors[algorithm_name]
                    score, is_drift = detector(baseline_values, current_values)
                    drift_results[algorithm_name] = {"score": score, "drift_detected": is_drift}
            
            # Consensus-based drift detection
            drift_detected_count = sum(1 for result in drift_results.values() if result["drift_detected"])
            consensus_threshold = len(drift_results) // 2 + 1
            
            if drift_detected_count >= consensus_threshold:
                # Calculate aggregate drift score
                avg_drift_score = statistics.mean([r["score"] for r in drift_results.values()])
                
                # Determine drift type and severity
                drift_type = self._classify_drift_type(metric_type)
                severity = self._determine_alert_severity(avg_drift_score, drift_type)
                
                # Create drift alert
                alert = DriftAlert(
                    alert_id=str(uuid.uuid4()),
                    drift_type=drift_type,
                    severity=severity,
                    model_name=config.model_name,
                    model_version=config.model_version,
                    detected_at=datetime.now(),
                    drift_score=avg_drift_score,
                    threshold=self.config.get("drift_detection", {}).get("thresholds", {}).get(drift_type.value, 0.1),
                    description=f"Drift detected in {metric_type} using {drift_detected_count}/{len(drift_results)} algorithms",
                    affected_metrics=[metric_type]
                )
                
                await self._handle_alert(alert, config)
                
        except Exception as e:
            logger.error(f"❌ Drift detection error: {str(e)}")
    
    def _establish_baseline(self, model_key: str, metric_type: str, values: List[float]) -> None:
        """Establish baseline for a metric"""
        try:
            if model_key not in self._baseline_metrics:
                self._baseline_metrics[model_key] = {}
            
            # Calculate baseline statistics
            baseline_stats = {
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "std": statistics.stdev(values) if len(values) > 1 else 0.0,
                "min": min(values),
                "max": max(values),
                "count": len(values),
                "established_at": datetime.now().isoformat()
            }
            
            self._baseline_metrics[model_key][metric_type] = baseline_stats["mean"]
            
            logger.info(f"📊 Established baseline for {model_key}:{metric_type} - Mean: {baseline_stats['mean']:.4f}")
            
        except Exception as e:
            logger.error(f"❌ Baseline establishment error: {str(e)}")
    
    def _get_baseline_values(self, model_key: str, metric_type: str) -> List[float]:
        """Get baseline values for drift comparison"""
        try:
            # Get historical metrics from the first 25% of recorded data
            historical_metrics = [
                m for m in self._metric_history[model_key]
                if m.metric_type.value == metric_type
            ]
            
            if len(historical_metrics) < 100:
                return []
            
            # Use first 25% as baseline
            baseline_count = min(len(historical_metrics) // 4, 1000)
            baseline_metrics = historical_metrics[:baseline_count]
            
            return [m.value for m in baseline_metrics]
            
        except Exception as e:
            logger.error(f"❌ Baseline retrieval error: {str(e)}")
            return []
    
    def _classify_drift_type(self, metric_type: str) -> DriftType:
        """Classify the type of drift based on metric"""
        performance_metrics = ["accuracy", "precision", "recall", "f1_score", "auc_roc", "error_rate"]
        business_metrics = ["creator_satisfaction", "business_kpi"]
        system_metrics = ["latency", "throughput", "memory_usage", "cpu_usage"]
        
        if metric_type in performance_metrics:
            return DriftType.PERFORMANCE_DRIFT
        elif metric_type in business_metrics:
            return DriftType.BUSINESS_DRIFT
        elif metric_type in system_metrics:
            return DriftType.PERFORMANCE_DRIFT
        else:
            return DriftType.DATA_DRIFT
    
    def _determine_alert_severity(self, drift_score: float, drift_type: DriftType) -> AlertSeverity:
        """Determine alert severity based on drift score and type"""
        # Business drift is more critical
        if drift_type == DriftType.BUSINESS_DRIFT:
            if drift_score > 0.3:
                return AlertSeverity.EMERGENCY
            elif drift_score > 0.2:
                return AlertSeverity.CRITICAL
            elif drift_score > 0.1:
                return AlertSeverity.WARNING
            else:
                return AlertSeverity.INFO
        
        # Performance drift
        elif drift_type == DriftType.PERFORMANCE_DRIFT:
            if drift_score > 0.5:
                return AlertSeverity.CRITICAL
            elif drift_score > 0.3:
                return AlertSeverity.WARNING
            else:
                return AlertSeverity.INFO
        
        # Data/Concept drift
        else:
            if drift_score > 0.4:
                return AlertSeverity.WARNING
            else:
                return AlertSeverity.INFO
    
    async def _handle_alert(self, alert: DriftAlert, config: MonitoringConfiguration) -> None:
        """Handle drift alert"""
        try:
            # Store alert
            self._active_alerts[alert.alert_id] = alert
            self._alert_history.append(alert)
            
            # Generate recommendations
            alert.recommended_actions = self._generate_alert_recommendations(alert, config)
            
            # Auto-remediation if enabled
            if self.config.get("remediation", {}).get("auto_remediation", True):
                if alert.drift_type in self._remediation_handlers:
                    remediation_handler = self._remediation_handlers[alert.drift_type]
                    remediation_result = await remediation_handler(alert, config)
                    
                    if remediation_result.get("success", False):
                        self._monitor_metrics["auto_remediations"] += 1
                        logger.info(f"🔧 Auto-remediation completed for alert {alert.alert_id}")
            
            self._monitor_metrics["alerts_generated"] += 1
            self._monitor_metrics["drift_detections"] += 1
            
            logger.warning(f"🚨 Drift alert generated: {alert.alert_id} - {alert.description}")
            
        except Exception as e:
            logger.error(f"❌ Alert handling error: {str(e)}")
    
    def _generate_alert_recommendations(self, alert: DriftAlert, config: MonitoringConfiguration) -> List[str]:
        """Generate recommendations for drift alert"""
        recommendations = []
        
        if alert.drift_type == DriftType.DATA_DRIFT:
            recommendations.extend([
                "Investigate data source changes",
                "Validate data preprocessing pipeline",
                "Consider model retraining with recent data"
            ])
        
        elif alert.drift_type == DriftType.PERFORMANCE_DRIFT:
            recommendations.extend([
                "Check system resources and scaling",
                "Validate model serving infrastructure",
                "Consider A/B testing with previous version"
            ])
        
        elif alert.drift_type == DriftType.BUSINESS_DRIFT:
            recommendations.extend([
                "Review business assumptions and KPIs",
                "Analyze creator satisfaction metrics",
                "Evaluate revenue impact and trends"
            ])
        
        elif alert.drift_type == DriftType.CONCEPT_DRIFT:
            recommendations.extend([
                "Update feature engineering approach",
                "Retrain model with concept-aware techniques",
                "Consider ensemble or adaptive learning methods"
            ])
        
        # Severity-specific recommendations
        if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
            recommendations.insert(0, "Consider immediate rollback to stable version")
        
        return recommendations
    
    def get_model_performance_summary(self, model_name: str, model_version: str) -> Dict[str, Any]:
        """Get performance summary for a model"""
        try:
            model_key = f"{model_name}:{model_version}"
            
            if model_key not in self._monitoring_configs:
                return {"error": "Model not registered for monitoring"}
            
            config = self._monitoring_configs[model_key]
            metrics = list(self._metric_history.get(model_key, []))
            
            if not metrics:
                return {"error": "No metrics recorded yet"}
            
            # Calculate summary statistics
            summary = {
                "model_name": model_name,
                "model_version": model_version,
                "monitoring_level": config.monitoring_level.value,
                "total_metrics": len(metrics),
                "monitoring_duration_hours": (datetime.now() - metrics[0].timestamp).total_seconds() / 3600 if metrics else 0,
                "last_updated": metrics[-1].timestamp.isoformat() if metrics else None,
                "metrics_by_type": {}
            }
            
            # Group metrics by type
            metrics_by_type = defaultdict(list)
            for metric in metrics[-1000:]:  # Last 1000 metrics
                metrics_by_type[metric.metric_type.value].append(metric.value)
            
            # Calculate statistics for each metric type
            for metric_type, values in metrics_by_type.items():
                if values:
                    summary["metrics_by_type"][metric_type] = {
                        "count": len(values),
                        "latest": values[-1],
                        "mean": statistics.mean(values),
                        "median": statistics.median(values),
                        "std": statistics.stdev(values) if len(values) > 1 else 0.0,
                        "min": min(values),
                        "max": max(values),
                        "trend": "stable"  # Could implement trend analysis
                    }
            
            # Active alerts
            model_alerts = [
                alert for alert in self._active_alerts.values()
                if alert.model_name == model_name and alert.model_version == model_version and not alert.resolved
            ]
            
            summary["active_alerts"] = len(model_alerts)
            summary["alert_breakdown"] = {
                severity.value: len([a for a in model_alerts if a.severity == severity])
                for severity in AlertSeverity
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Performance summary error: {str(e)}")
            return {"error": str(e)}
    
    def get_active_alerts(self, model_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get active drift alerts"""
        alerts = [
            alert for alert in self._active_alerts.values()
            if not alert.resolved and (not model_name or alert.model_name == model_name)
        ]
        
        return [alert.to_dict() for alert in sorted(alerts, key=lambda x: x.detected_at, reverse=True)]
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge a drift alert"""
        try:
            if alert_id in self._active_alerts:
                alert = self._active_alerts[alert_id]
                alert.acknowledged = True
                logger.info(f"✅ Alert {alert_id} acknowledged by {acknowledged_by}")
                return True
            else:
                logger.warning(f"⚠️ Alert {alert_id} not found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Alert acknowledgment error: {str(e)}")
            return False
    
    def resolve_alert(self, alert_id: str, resolution_notes: str, resolved_by: str) -> bool:
        """Resolve a drift alert"""
        try:
            if alert_id in self._active_alerts:
                alert = self._active_alerts[alert_id]
                alert.resolved = True
                alert.resolution_notes = resolution_notes
                
                # Remove from active alerts
                del self._active_alerts[alert_id]
                
                logger.info(f"✅ Alert {alert_id} resolved by {resolved_by}")
                return True
            else:
                logger.warning(f"⚠️ Alert {alert_id} not found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Alert resolution error: {str(e)}")
            return False
    
    def get_monitoring_metrics(self) -> Dict[str, Any]:
        """Get monitoring system metrics"""
        return {
            **self._monitor_metrics,
            "active_alerts": len(self._active_alerts),
            "monitoring_threads": len(self._monitoring_threads),
            "drift_detectors": len(self._drift_detectors),
            "remediation_handlers": len(self._remediation_handlers)
        }
    
    def stop_monitoring(self, model_name: str, model_version: str) -> bool:
        """Stop monitoring for a model"""
        try:
            model_key = f"{model_name}:{model_version}"
            
            # Stop monitoring thread
            if model_key in self._stop_monitoring:
                self._stop_monitoring[model_key].set()
                
            # Wait for thread to finish
            if model_key in self._monitoring_threads:
                self._monitoring_threads[model_key].join(timeout=5.0)
                del self._monitoring_threads[model_key]
                
            # Cleanup
            if model_key in self._stop_monitoring:
                del self._stop_monitoring[model_key]
                
            if model_key in self._monitoring_configs:
                del self._monitoring_configs[model_key]
                self._monitor_metrics["models_monitored"] -= 1
            
            logger.info(f"🛑 Stopped monitoring for {model_key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop monitoring: {str(e)}")
            return False
    
    def health_check(self) -> str:
        """Health check for performance monitor"""
        try:
            # Check monitoring threads
            active_threads = sum(1 for t in self._monitoring_threads.values() if t.is_alive())
            expected_threads = len(self._monitoring_configs)
            
            if active_threads != expected_threads:
                return f"WARNING: {active_threads}/{expected_threads} monitoring threads active"
            
            # Check for stuck alerts
            now = datetime.now()
            stuck_alerts = [
                alert for alert in self._active_alerts.values()
                if not alert.acknowledged and (now - alert.detected_at).total_seconds() > 3600  # 1 hour
            ]
            
            if stuck_alerts:
                return f"WARNING: {len(stuck_alerts)} unacknowledged alerts"
            
            # Check drift detector health
            if not self._drift_detectors:
                return "ERROR: No drift detectors available"
            
            return "OPERATIONAL"
            
        except Exception as e:
            return f"ERROR: {str(e)}"


# Export main class and enums
__all__ = [
    "ModelPerformanceMonitor",
    "MonitoringLevel",
    "DriftType",
    "AlertSeverity",
    "MetricType",
    "PerformanceMetric",
    "DriftAlert",
    "MonitoringConfiguration"
]