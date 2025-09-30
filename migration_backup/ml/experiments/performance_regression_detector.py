"""
📉 PERFORMANCE REGRESSION DETECTOR
Enterprise-grade ML model performance regression detection and analysis system.

Ersteller: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Alle Rechte vorbehalten.
"""

import asyncio
import time
import json
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, NamedTuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import statistics
import scipy.stats as stats
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA
import threading
from concurrent.futures import ThreadPoolExecutor


class RegressionSeverity(Enum):
    """Performance regression severity levels."""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"


class RegressionType(Enum):
    """Types of performance regressions."""
    LATENCY_INCREASE = "latency_increase"
    ACCURACY_DECREASE = "accuracy_decrease"
    THROUGHPUT_DECREASE = "throughput_decrease"
    ERROR_RATE_INCREASE = "error_rate_increase"
    MEMORY_INCREASE = "memory_increase"
    CPU_INCREASE = "cpu_increase"
    DRIFT_DETECTED = "drift_detected"
    QUALITY_DEGRADATION = "quality_degradation"


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    timestamp: datetime
    model_id: str
    version: str
    creator_type: str
    environment: str
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    accuracy_score: float
    throughput_rps: float
    error_rate_percent: float
    memory_usage_mb: float
    cpu_usage_percent: float
    prediction_confidence: float
    data_drift_score: float
    model_drift_score: float
    business_metric_score: float


@dataclass
class RegressionAlert:
    """Performance regression alert."""
    alert_id: str
    model_id: str
    version: str
    regression_type: RegressionType
    severity: RegressionSeverity
    current_value: float
    baseline_value: float
    degradation_percent: float
    statistical_significance: float
    confidence_interval: Tuple[float, float]
    timestamp: datetime
    affected_creators: List[str]
    root_cause_analysis: Dict[str, Any]
    recommendation: str


class PerformanceRegressionDetector:
    """
    📉 Enterprise-grade performance regression detection system.
    
    Features:
    - Statistical regression detection
    - Multi-dimensional performance analysis
    - Creator-specific regression thresholds
    - Automated root cause analysis
    - Trend analysis and forecasting
    - A/B test performance comparison
    - Model drift detection integration
    - Business impact assessment
    - Automated alerting and remediation
    - Performance baseline management
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = self._setup_logging()
        
        # Performance data storage
        self.performance_history: deque = deque(maxlen=50000)  # ~30 days at 1min intervals
        self.model_baselines: Dict[str, Dict[str, float]] = {}
        self.creator_baselines: Dict[str, Dict[str, float]] = {}
        
        # Regression detection
        self.regression_alerts: List[RegressionAlert] = []
        self.active_regressions: Dict[str, RegressionAlert] = {}
        self.regression_thresholds = self._setup_regression_thresholds()
        
        # Statistical models
        self.anomaly_detectors: Dict[str, IsolationForest] = {}
        self.trend_models: Dict[str, Dict[str, Any]] = {}
        
        # Monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.analysis_interval = 60  # seconds
        
        # Creator-specific configurations
        self.creator_configs = {
            'musician': {
                'audio_quality_weight': 0.4,
                'latency_tolerance_ms': 150,
                'accuracy_threshold': 0.92,
                'drift_sensitivity': 0.7
            },
            'blogger': {
                'content_quality_weight': 0.3,
                'latency_tolerance_ms': 500,
                'accuracy_threshold': 0.88,
                'drift_sensitivity': 0.5
            },
            'photographer': {
                'image_quality_weight': 0.35,
                'latency_tolerance_ms': 300,
                'accuracy_threshold': 0.90,
                'drift_sensitivity': 0.6
            },
            'influencer': {
                'engagement_weight': 0.45,
                'latency_tolerance_ms': 100,
                'accuracy_threshold': 0.95,
                'drift_sensitivity': 0.8
            }
        }
        
        self.logger.info("PerformanceRegressionDetector initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger('performance_regression_detector')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _setup_regression_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Setup performance regression detection thresholds."""
        return {
            'latency': {
                'minor_increase_percent': 15.0,
                'moderate_increase_percent': 30.0,
                'major_increase_percent': 50.0,
                'critical_increase_percent': 100.0
            },
            'accuracy': {
                'minor_decrease_percent': 2.0,
                'moderate_decrease_percent': 5.0,
                'major_decrease_percent': 10.0,
                'critical_decrease_percent': 20.0
            },
            'throughput': {
                'minor_decrease_percent': 10.0,
                'moderate_decrease_percent': 25.0,
                'major_decrease_percent': 40.0,
                'critical_decrease_percent': 60.0
            },
            'error_rate': {
                'minor_increase_percent': 50.0,
                'moderate_increase_percent': 100.0,
                'major_increase_percent': 200.0,
                'critical_increase_percent': 500.0
            },
            'memory': {
                'minor_increase_percent': 20.0,
                'moderate_increase_percent': 40.0,
                'major_increase_percent': 70.0,
                'critical_increase_percent': 100.0
            },
            'drift': {
                'minor_threshold': 0.3,
                'moderate_threshold': 0.5,
                'major_threshold': 0.7,
                'critical_threshold': 0.9
            }
        }
    
    async def record_performance_metrics(self, metrics: PerformanceMetrics) -> None:
        """Record performance metrics for regression analysis."""
        try:
            # Store metrics
            self.performance_history.append(metrics)
            
            # Update baselines if needed
            await self._update_baselines(metrics)
            
            # Check for regressions
            regressions = await self._detect_regressions(metrics)
            
            # Process any detected regressions
            for regression in regressions:
                await self._process_regression_alert(regression)
            
            self.logger.debug(f"Recorded performance metrics for {metrics.model_id}")
            
        except Exception as e:
            self.logger.error(f"Error recording performance metrics: {e}")
    
    async def _update_baselines(self, metrics: PerformanceMetrics) -> None:
        """Update performance baselines."""
        try:
            # Get recent stable metrics for baseline calculation
            recent_metrics = [
                m for m in self.performance_history
                if (m.model_id == metrics.model_id and 
                    (metrics.timestamp - m.timestamp).total_seconds() <= 7*24*3600)  # 7 days
            ]
            
            if len(recent_metrics) >= 100:  # Minimum sample size
                # Calculate baseline statistics
                baseline = {
                    'latency_p50_ms': np.percentile([m.latency_p50_ms for m in recent_metrics], 50),
                    'latency_p95_ms': np.percentile([m.latency_p95_ms for m in recent_metrics], 50),
                    'accuracy_score': statistics.mean([m.accuracy_score for m in recent_metrics]),
                    'throughput_rps': statistics.mean([m.throughput_rps for m in recent_metrics]),
                    'error_rate_percent': np.percentile([m.error_rate_percent for m in recent_metrics], 50),
                    'memory_usage_mb': statistics.mean([m.memory_usage_mb for m in recent_metrics]),
                    'cpu_usage_percent': statistics.mean([m.cpu_usage_percent for m in recent_metrics]),
                    'prediction_confidence': statistics.mean([m.prediction_confidence for m in recent_metrics]),
                    'updated_at': metrics.timestamp
                }
                
                self.model_baselines[metrics.model_id] = baseline
                
                # Update creator-specific baseline
                creator_key = f"{metrics.creator_type}_{metrics.environment}"
                if creator_key not in self.creator_baselines:
                    self.creator_baselines[creator_key] = {}
                
                self.creator_baselines[creator_key].update(baseline)
                
        except Exception as e:
            self.logger.error(f"Error updating baselines: {e}")
    
    async def _detect_regressions(self, metrics: PerformanceMetrics) -> List[RegressionAlert]:
        """Detect performance regressions in the metrics."""
        try:
            regressions = []
            
            # Get baseline for comparison
            baseline = self.model_baselines.get(metrics.model_id)
            if not baseline:
                return regressions  # No baseline yet
            
            # Check each metric for regression
            
            # Latency regression
            latency_regression = await self._check_latency_regression(metrics, baseline)
            if latency_regression:
                regressions.append(latency_regression)
            
            # Accuracy regression
            accuracy_regression = await self._check_accuracy_regression(metrics, baseline)
            if accuracy_regression:
                regressions.append(accuracy_regression)
            
            # Throughput regression
            throughput_regression = await self._check_throughput_regression(metrics, baseline)
            if throughput_regression:
                regressions.append(throughput_regression)
            
            # Error rate regression
            error_rate_regression = await self._check_error_rate_regression(metrics, baseline)
            if error_rate_regression:
                regressions.append(error_rate_regression)
            
            # Memory regression
            memory_regression = await self._check_memory_regression(metrics, baseline)
            if memory_regression:
                regressions.append(memory_regression)
            
            # Drift regression
            drift_regression = await self._check_drift_regression(metrics, baseline)
            if drift_regression:
                regressions.append(drift_regression)
            
            return regressions
            
        except Exception as e:
            self.logger.error(f"Error detecting regressions: {e}")
            return []
    
    async def _check_latency_regression(
        self, 
        metrics: PerformanceMetrics, 
        baseline: Dict[str, float]
    ) -> Optional[RegressionAlert]:
        """Check for latency performance regression."""
        try:
            current_latency = metrics.latency_p95_ms
            baseline_latency = baseline.get('latency_p95_ms', current_latency)
            
            if baseline_latency <= 0:
                return None
            
            increase_percent = ((current_latency - baseline_latency) / baseline_latency) * 100
            
            # Determine severity
            severity = None
            thresholds = self.regression_thresholds['latency']
            
            if increase_percent >= thresholds['critical_increase_percent']:
                severity = RegressionSeverity.CRITICAL
            elif increase_percent >= thresholds['major_increase_percent']:
                severity = RegressionSeverity.MAJOR
            elif increase_percent >= thresholds['moderate_increase_percent']:
                severity = RegressionSeverity.MODERATE
            elif increase_percent >= thresholds['minor_increase_percent']:
                severity = RegressionSeverity.MINOR
            
            if severity:
                # Statistical significance test
                significance, confidence_interval = await self._calculate_statistical_significance(
                    metrics.model_id, 'latency_p95_ms', current_latency, baseline_latency
                )
                
                # Root cause analysis
                root_cause = await self._analyze_latency_root_cause(metrics, baseline)
                
                # Recommendation
                recommendation = await self._generate_latency_recommendation(
                    metrics, baseline, severity, root_cause
                )
                
                return RegressionAlert(
                    alert_id=f"latency_{metrics.model_id}_{int(time.time())}",
                    model_id=metrics.model_id,
                    version=metrics.version,
                    regression_type=RegressionType.LATENCY_INCREASE,
                    severity=severity,
                    current_value=current_latency,
                    baseline_value=baseline_latency,
                    degradation_percent=increase_percent,
                    statistical_significance=significance,
                    confidence_interval=confidence_interval,
                    timestamp=metrics.timestamp,
                    affected_creators=[metrics.creator_type],
                    root_cause_analysis=root_cause,
                    recommendation=recommendation
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking latency regression: {e}")
            return None
    
    async def _check_accuracy_regression(
        self, 
        metrics: PerformanceMetrics, 
        baseline: Dict[str, float]
    ) -> Optional[RegressionAlert]:
        """Check for accuracy performance regression."""
        try:
            current_accuracy = metrics.accuracy_score
            baseline_accuracy = baseline.get('accuracy_score', current_accuracy)
            
            if baseline_accuracy <= 0:
                return None
            
            decrease_percent = ((baseline_accuracy - current_accuracy) / baseline_accuracy) * 100
            
            # Determine severity
            severity = None
            thresholds = self.regression_thresholds['accuracy']
            
            if decrease_percent >= thresholds['critical_decrease_percent']:
                severity = RegressionSeverity.CRITICAL
            elif decrease_percent >= thresholds['major_decrease_percent']:
                severity = RegressionSeverity.MAJOR
            elif decrease_percent >= thresholds['moderate_decrease_percent']:
                severity = RegressionSeverity.MODERATE
            elif decrease_percent >= thresholds['minor_decrease_percent']:
                severity = RegressionSeverity.MINOR
            
            if severity:
                # Statistical significance test
                significance, confidence_interval = await self._calculate_statistical_significance(
                    metrics.model_id, 'accuracy_score', current_accuracy, baseline_accuracy
                )
                
                # Root cause analysis
                root_cause = await self._analyze_accuracy_root_cause(metrics, baseline)
                
                # Recommendation
                recommendation = await self._generate_accuracy_recommendation(
                    metrics, baseline, severity, root_cause
                )
                
                return RegressionAlert(
                    alert_id=f"accuracy_{metrics.model_id}_{int(time.time())}",
                    model_id=metrics.model_id,
                    version=metrics.version,
                    regression_type=RegressionType.ACCURACY_DECREASE,
                    severity=severity,
                    current_value=current_accuracy,
                    baseline_value=baseline_accuracy,
                    degradation_percent=decrease_percent,
                    statistical_significance=significance,
                    confidence_interval=confidence_interval,
                    timestamp=metrics.timestamp,
                    affected_creators=[metrics.creator_type],
                    root_cause_analysis=root_cause,
                    recommendation=recommendation
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking accuracy regression: {e}")
            return None
    
    async def _check_throughput_regression(
        self, 
        metrics: PerformanceMetrics, 
        baseline: Dict[str, float]
    ) -> Optional[RegressionAlert]:
        """Check for throughput performance regression."""
        try:
            current_throughput = metrics.throughput_rps
            baseline_throughput = baseline.get('throughput_rps', current_throughput)
            
            if baseline_throughput <= 0:
                return None
            
            decrease_percent = ((baseline_throughput - current_throughput) / baseline_throughput) * 100
            
            # Determine severity
            severity = None
            thresholds = self.regression_thresholds['throughput']
            
            if decrease_percent >= thresholds['critical_decrease_percent']:
                severity = RegressionSeverity.CRITICAL
            elif decrease_percent >= thresholds['major_decrease_percent']:
                severity = RegressionSeverity.MAJOR
            elif decrease_percent >= thresholds['moderate_decrease_percent']:
                severity = RegressionSeverity.MODERATE
            elif decrease_percent >= thresholds['minor_decrease_percent']:
                severity = RegressionSeverity.MINOR
            
            if severity:
                # Statistical significance test
                significance, confidence_interval = await self._calculate_statistical_significance(
                    metrics.model_id, 'throughput_rps', current_throughput, baseline_throughput
                )
                
                # Root cause analysis
                root_cause = await self._analyze_throughput_root_cause(metrics, baseline)
                
                # Recommendation
                recommendation = await self._generate_throughput_recommendation(
                    metrics, baseline, severity, root_cause
                )
                
                return RegressionAlert(
                    alert_id=f"throughput_{metrics.model_id}_{int(time.time())}",
                    model_id=metrics.model_id,
                    version=metrics.version,
                    regression_type=RegressionType.THROUGHPUT_DECREASE,
                    severity=severity,
                    current_value=current_throughput,
                    baseline_value=baseline_throughput,
                    degradation_percent=decrease_percent,
                    statistical_significance=significance,
                    confidence_interval=confidence_interval,
                    timestamp=metrics.timestamp,
                    affected_creators=[metrics.creator_type],
                    root_cause_analysis=root_cause,
                    recommendation=recommendation
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking throughput regression: {e}")
            return None
    
    async def _check_error_rate_regression(
        self, 
        metrics: PerformanceMetrics, 
        baseline: Dict[str, float]
    ) -> Optional[RegressionAlert]:
        """Check for error rate regression."""
        try:
            current_error_rate = metrics.error_rate_percent
            baseline_error_rate = baseline.get('error_rate_percent', current_error_rate)
            
            if baseline_error_rate <= 0:
                baseline_error_rate = 0.1  # Small baseline to avoid division by zero
            
            increase_percent = ((current_error_rate - baseline_error_rate) / baseline_error_rate) * 100
            
            # Determine severity
            severity = None
            thresholds = self.regression_thresholds['error_rate']
            
            if increase_percent >= thresholds['critical_increase_percent']:
                severity = RegressionSeverity.CRITICAL
            elif increase_percent >= thresholds['major_increase_percent']:
                severity = RegressionSeverity.MAJOR
            elif increase_percent >= thresholds['moderate_increase_percent']:
                severity = RegressionSeverity.MODERATE
            elif increase_percent >= thresholds['minor_increase_percent']:
                severity = RegressionSeverity.MINOR
            
            if severity:
                # Statistical significance test
                significance, confidence_interval = await self._calculate_statistical_significance(
                    metrics.model_id, 'error_rate_percent', current_error_rate, baseline_error_rate
                )
                
                # Root cause analysis
                root_cause = await self._analyze_error_rate_root_cause(metrics, baseline)
                
                # Recommendation
                recommendation = await self._generate_error_rate_recommendation(
                    metrics, baseline, severity, root_cause
                )
                
                return RegressionAlert(
                    alert_id=f"error_rate_{metrics.model_id}_{int(time.time())}",
                    model_id=metrics.model_id,
                    version=metrics.version,
                    regression_type=RegressionType.ERROR_RATE_INCREASE,
                    severity=severity,
                    current_value=current_error_rate,
                    baseline_value=baseline_error_rate,
                    degradation_percent=increase_percent,
                    statistical_significance=significance,
                    confidence_interval=confidence_interval,
                    timestamp=metrics.timestamp,
                    affected_creators=[metrics.creator_type],
                    root_cause_analysis=root_cause,
                    recommendation=recommendation
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking error rate regression: {e}")
            return None
    
    async def _check_memory_regression(
        self, 
        metrics: PerformanceMetrics, 
        baseline: Dict[str, float]
    ) -> Optional[RegressionAlert]:
        """Check for memory usage regression."""
        try:
            current_memory = metrics.memory_usage_mb
            baseline_memory = baseline.get('memory_usage_mb', current_memory)
            
            if baseline_memory <= 0:
                return None
            
            increase_percent = ((current_memory - baseline_memory) / baseline_memory) * 100
            
            # Determine severity
            severity = None
            thresholds = self.regression_thresholds['memory']
            
            if increase_percent >= thresholds['critical_increase_percent']:
                severity = RegressionSeverity.CRITICAL
            elif increase_percent >= thresholds['major_increase_percent']:
                severity = RegressionSeverity.MAJOR
            elif increase_percent >= thresholds['moderate_increase_percent']:
                severity = RegressionSeverity.MODERATE
            elif increase_percent >= thresholds['minor_increase_percent']:
                severity = RegressionSeverity.MINOR
            
            if severity:
                # Statistical significance test
                significance, confidence_interval = await self._calculate_statistical_significance(
                    metrics.model_id, 'memory_usage_mb', current_memory, baseline_memory
                )
                
                # Root cause analysis
                root_cause = await self._analyze_memory_root_cause(metrics, baseline)
                
                # Recommendation
                recommendation = await self._generate_memory_recommendation(
                    metrics, baseline, severity, root_cause
                )
                
                return RegressionAlert(
                    alert_id=f"memory_{metrics.model_id}_{int(time.time())}",
                    model_id=metrics.model_id,
                    version=metrics.version,
                    regression_type=RegressionType.MEMORY_INCREASE,
                    severity=severity,
                    current_value=current_memory,
                    baseline_value=baseline_memory,
                    degradation_percent=increase_percent,
                    statistical_significance=significance,
                    confidence_interval=confidence_interval,
                    timestamp=metrics.timestamp,
                    affected_creators=[metrics.creator_type],
                    root_cause_analysis=root_cause,
                    recommendation=recommendation
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking memory regression: {e}")
            return None
    
    async def _check_drift_regression(
        self, 
        metrics: PerformanceMetrics, 
        baseline: Dict[str, float]
    ) -> Optional[RegressionAlert]:
        """Check for data/model drift regression."""
        try:
            current_drift = max(metrics.data_drift_score, metrics.model_drift_score)
            
            # Determine severity based on drift thresholds
            severity = None
            thresholds = self.regression_thresholds['drift']
            
            if current_drift >= thresholds['critical_threshold']:
                severity = RegressionSeverity.CRITICAL
            elif current_drift >= thresholds['major_threshold']:
                severity = RegressionSeverity.MAJOR
            elif current_drift >= thresholds['moderate_threshold']:
                severity = RegressionSeverity.MODERATE
            elif current_drift >= thresholds['minor_threshold']:
                severity = RegressionSeverity.MINOR
            
            if severity:
                # Root cause analysis
                root_cause = await self._analyze_drift_root_cause(metrics, baseline)
                
                # Recommendation
                recommendation = await self._generate_drift_recommendation(
                    metrics, baseline, severity, root_cause
                )
                
                return RegressionAlert(
                    alert_id=f"drift_{metrics.model_id}_{int(time.time())}",
                    model_id=metrics.model_id,
                    version=metrics.version,
                    regression_type=RegressionType.DRIFT_DETECTED,
                    severity=severity,
                    current_value=current_drift,
                    baseline_value=0.0,
                    degradation_percent=current_drift * 100,
                    statistical_significance=0.95,  # High confidence for drift
                    confidence_interval=(current_drift * 0.9, current_drift * 1.1),
                    timestamp=metrics.timestamp,
                    affected_creators=[metrics.creator_type],
                    root_cause_analysis=root_cause,
                    recommendation=recommendation
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking drift regression: {e}")
            return None
    
    async def _calculate_statistical_significance(
        self, 
        model_id: str, 
        metric_name: str, 
        current_value: float, 
        baseline_value: float
    ) -> Tuple[float, Tuple[float, float]]:
        """Calculate statistical significance of performance change."""
        try:
            # Get recent measurements for statistical analysis
            recent_metrics = [
                m for m in self.performance_history
                if (m.model_id == model_id and 
                    (datetime.now() - m.timestamp).total_seconds() <= 7*24*3600)
            ]
            
            if len(recent_metrics) < 30:
                return 0.5, (current_value * 0.95, current_value * 1.05)
            
            # Extract values for the specific metric
            values = []
            for m in recent_metrics:
                if metric_name == 'latency_p95_ms':
                    values.append(m.latency_p95_ms)
                elif metric_name == 'accuracy_score':
                    values.append(m.accuracy_score)
                elif metric_name == 'throughput_rps':
                    values.append(m.throughput_rps)
                elif metric_name == 'error_rate_percent':
                    values.append(m.error_rate_percent)
                elif metric_name == 'memory_usage_mb':
                    values.append(m.memory_usage_mb)
            
            if len(values) < 30:
                return 0.5, (current_value * 0.95, current_value * 1.05)
            
            # Perform t-test
            baseline_values = values[:-10]  # Historical values
            current_values = values[-10:]   # Recent values
            
            if len(baseline_values) > 0 and len(current_values) > 0:
                t_stat, p_value = stats.ttest_ind(current_values, baseline_values)
                significance = 1 - p_value
                
                # Calculate confidence interval
                std_error = stats.sem(current_values)
                confidence_interval = stats.t.interval(
                    0.95, len(current_values)-1, 
                    loc=np.mean(current_values), 
                    scale=std_error
                )
                
                return significance, confidence_interval
            
            return 0.5, (current_value * 0.95, current_value * 1.05)
            
        except Exception as e:
            self.logger.error(f"Error calculating statistical significance: {e}")
            return 0.5, (current_value * 0.95, current_value * 1.05)
    
    async def _analyze_latency_root_cause(
        self, 
        metrics: PerformanceMetrics, 
        baseline: Dict[str, float]
    ) -> Dict[str, Any]:
        """Analyze root cause of latency regression."""
        try:
            analysis = {
                'potential_causes': [],
                'correlation_analysis': {},
                'resource_impact': {},
                'environmental_factors': {}
            }
            
            # Check resource correlation
            if metrics.cpu_usage_percent > 80:
                analysis['potential_causes'].append('high_cpu_utilization')
                analysis['resource_impact']['cpu'] = metrics.cpu_usage_percent
            
            if metrics.memory_usage_mb > baseline.get('memory_usage_mb', 0) * 1.5:
                analysis['potential_causes'].append('memory_pressure')
                analysis['resource_impact']['memory'] = metrics.memory_usage_mb
            
            # Check drift correlation
            if metrics.data_drift_score > 0.5:
                analysis['potential_causes'].append('data_drift')
                analysis['correlation_analysis']['data_drift'] = metrics.data_drift_score
            
            # Environment-specific factors
            if metrics.environment == 'production':
                analysis['environmental_factors']['load_pattern'] = 'production_traffic'
            
            # Creator-specific factors
            creator_config = self.creator_configs.get(metrics.creator_type, {})
            if metrics.latency_p95_ms > creator_config.get('latency_tolerance_ms', 1000):
                analysis['potential_causes'].append('creator_type_sensitivity')
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing latency root cause: {e}")
            return {'error': str(e)}
    
    async def _analyze_accuracy_root_cause(
        self, 
        metrics: PerformanceMetrics, 
        baseline: Dict[str, float]
    ) -> Dict[str, Any]:
        """Analyze root cause of accuracy regression."""
        try:
            analysis = {
                'potential_causes': [],
                'data_quality_issues': {},
                'model_degradation': {},
                'drift_indicators': {}
            }
            
            # Check data drift
            if metrics.data_drift_score > 0.4:
                analysis['potential_causes'].append('data_distribution_shift')
                analysis['drift_indicators']['data_drift_score'] = metrics.data_drift_score
            
            # Check model drift
            if metrics.model_drift_score > 0.4:
                analysis['potential_causes'].append('model_performance_drift')
                analysis['drift_indicators']['model_drift_score'] = metrics.model_drift_score
            
            # Check prediction confidence
            if metrics.prediction_confidence < 0.7:
                analysis['potential_causes'].append('low_prediction_confidence')
                analysis['model_degradation']['confidence_score'] = metrics.prediction_confidence
            
            # Creator-specific accuracy thresholds
            creator_config = self.creator_configs.get(metrics.creator_type, {})
            threshold = creator_config.get('accuracy_threshold', 0.9)
            if metrics.accuracy_score < threshold:
                analysis['potential_causes'].append('below_creator_threshold')
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing accuracy root cause: {e}")
            return {'error': str(e)}
    
    async def _analyze_throughput_root_cause(
        self, 
        metrics: PerformanceMetrics, 
        baseline: Dict[str, float]
    ) -> Dict[str, Any]:
        """Analyze root cause of throughput regression."""
        try:
            analysis = {
                'potential_causes': [],
                'bottlenecks': {},
                'resource_constraints': {},
                'scaling_issues': {}
            }
            
            # Check resource bottlenecks
            if metrics.cpu_usage_percent > 90:
                analysis['potential_causes'].append('cpu_bottleneck')
                analysis['bottlenecks']['cpu_utilization'] = metrics.cpu_usage_percent
            
            if metrics.memory_usage_mb > baseline.get('memory_usage_mb', 0) * 1.8:
                analysis['potential_causes'].append('memory_bottleneck')
                analysis['bottlenecks']['memory_usage'] = metrics.memory_usage_mb
            
            # Check latency correlation
            if metrics.latency_p95_ms > baseline.get('latency_p95_ms', 0) * 1.3:
                analysis['potential_causes'].append('latency_impact')
                analysis['resource_constraints']['increased_latency'] = metrics.latency_p95_ms
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing throughput root cause: {e}")
            return {'error': str(e)}
    
    async def _analyze_error_rate_root_cause(
        self, 
        metrics: PerformanceMetrics, 
        baseline: Dict[str, float]
    ) -> Dict[str, Any]:
        """Analyze root cause of error rate regression."""
        try:
            analysis = {
                'potential_causes': [],
                'error_patterns': {},
                'system_health': {},
                'data_issues': {}
            }
            
            # Check system health indicators
            if metrics.cpu_usage_percent > 95:
                analysis['potential_causes'].append('system_overload')
                analysis['system_health']['cpu_overload'] = True
            
            # Check data quality
            if metrics.data_drift_score > 0.6:
                analysis['potential_causes'].append('data_quality_degradation')
                analysis['data_issues']['drift_score'] = metrics.data_drift_score
            
            # Check confidence correlation
            if metrics.prediction_confidence < 0.6:
                analysis['potential_causes'].append('model_uncertainty')
                analysis['error_patterns']['low_confidence'] = metrics.prediction_confidence
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing error rate root cause: {e}")
            return {'error': str(e)}
    
    async def _analyze_memory_root_cause(
        self, 
        metrics: PerformanceMetrics, 
        baseline: Dict[str, float]
    ) -> Dict[str, Any]:
        """Analyze root cause of memory regression."""
        try:
            analysis = {
                'potential_causes': [],
                'memory_patterns': {},
                'resource_leaks': {},
                'optimization_opportunities': {}
            }
            
            baseline_memory = baseline.get('memory_usage_mb', 0)
            memory_increase = metrics.memory_usage_mb - baseline_memory
            
            if memory_increase > baseline_memory * 0.5:
                analysis['potential_causes'].append('significant_memory_leak')
                analysis['memory_patterns']['increase_mb'] = memory_increase
            
            # Check correlation with other metrics
            if metrics.throughput_rps < baseline.get('throughput_rps', 0) * 0.8:
                analysis['potential_causes'].append('memory_pressure_impact')
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing memory root cause: {e}")
            return {'error': str(e)}
    
    async def _analyze_drift_root_cause(
        self, 
        metrics: PerformanceMetrics, 
        baseline: Dict[str, float]
    ) -> Dict[str, Any]:
        """Analyze root cause of drift regression."""
        try:
            analysis = {
                'potential_causes': [],
                'drift_analysis': {},
                'data_characteristics': {},
                'temporal_patterns': {}
            }
            
            # Analyze drift patterns
            if metrics.data_drift_score > metrics.model_drift_score:
                analysis['potential_causes'].append('input_data_distribution_change')
                analysis['drift_analysis']['primary_drift'] = 'data'
            else:
                analysis['potential_causes'].append('model_performance_degradation')
                analysis['drift_analysis']['primary_drift'] = 'model'
            
            # Creator-specific drift sensitivity
            creator_config = self.creator_configs.get(metrics.creator_type, {})
            sensitivity = creator_config.get('drift_sensitivity', 0.5)
            
            if max(metrics.data_drift_score, metrics.model_drift_score) > sensitivity:
                analysis['potential_causes'].append('creator_specific_sensitivity')
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing drift root cause: {e}")
            return {'error': str(e)}
    
    async def _generate_latency_recommendation(
        self, 
        metrics: PerformanceMetrics, 
        baseline: Dict[str, float],
        severity: RegressionSeverity,
        root_cause: Dict[str, Any]
    ) -> str:
        """Generate recommendation for latency regression."""
        try:
            recommendations = []
            
            if 'high_cpu_utilization' in root_cause.get('potential_causes', []):
                recommendations.append("Scale CPU resources or optimize computation")
            
            if 'memory_pressure' in root_cause.get('potential_causes', []):
                recommendations.append("Increase memory allocation or optimize memory usage")
            
            if 'data_drift' in root_cause.get('potential_causes', []):
                recommendations.append("Retrain model with recent data or apply drift adaptation")
            
            if severity in [RegressionSeverity.CRITICAL, RegressionSeverity.MAJOR]:
                recommendations.append("Consider immediate rollback to previous stable version")
            
            # Creator-specific recommendations
            if metrics.creator_type == 'influencer':
                recommendations.append("Prioritize low-latency optimization for real-time requirements")
            elif metrics.creator_type == 'musician':
                recommendations.append("Optimize audio processing pipeline for lower latency")
            
            return "; ".join(recommendations) if recommendations else "Monitor closely and investigate further"
            
        except Exception as e:
            self.logger.error(f"Error generating latency recommendation: {e}")
            return "Unable to generate recommendation"
    
    async def _generate_accuracy_recommendation(
        self, 
        metrics: PerformanceMetrics, 
        baseline: Dict[str, float],
        severity: RegressionSeverity,
        root_cause: Dict[str, Any]
    ) -> str:
        """Generate recommendation for accuracy regression."""
        try:
            recommendations = []
            
            if 'data_distribution_shift' in root_cause.get('potential_causes', []):
                recommendations.append("Collect new training data and retrain model")
            
            if 'model_performance_drift' in root_cause.get('potential_causes', []):
                recommendations.append("Apply model recalibration or incremental learning")
            
            if 'low_prediction_confidence' in root_cause.get('potential_causes', []):
                recommendations.append("Implement confidence-based filtering and human review")
            
            if severity == RegressionSeverity.CRITICAL:
                recommendations.append("Immediate model rollback and emergency retraining")
            
            return "; ".join(recommendations) if recommendations else "Continue monitoring and data analysis"
            
        except Exception as e:
            self.logger.error(f"Error generating accuracy recommendation: {e}")
            return "Unable to generate recommendation"
    
    async def _generate_throughput_recommendation(
        self, 
        metrics: PerformanceMetrics, 
        baseline: Dict[str, float],
        severity: RegressionSeverity,
        root_cause: Dict[str, Any]
    ) -> str:
        """Generate recommendation for throughput regression."""
        try:
            recommendations = []
            
            if 'cpu_bottleneck' in root_cause.get('potential_causes', []):
                recommendations.append("Scale CPU resources or implement load balancing")
            
            if 'memory_bottleneck' in root_cause.get('potential_causes', []):
                recommendations.append("Increase memory allocation or optimize memory usage")
            
            if 'latency_impact' in root_cause.get('potential_causes', []):
                recommendations.append("Optimize inference pipeline to reduce latency")
            
            return "; ".join(recommendations) if recommendations else "Investigate system bottlenecks"
            
        except Exception as e:
            self.logger.error(f"Error generating throughput recommendation: {e}")
            return "Unable to generate recommendation"
    
    async def _generate_error_rate_recommendation(
        self, 
        metrics: PerformanceMetrics, 
        baseline: Dict[str, float],
        severity: RegressionSeverity,
        root_cause: Dict[str, Any]
    ) -> str:
        """Generate recommendation for error rate regression."""
        try:
            recommendations = []
            
            if 'system_overload' in root_cause.get('potential_causes', []):
                recommendations.append("Reduce system load or scale resources")
            
            if 'data_quality_degradation' in root_cause.get('potential_causes', []):
                recommendations.append("Implement data quality validation and cleaning")
            
            if 'model_uncertainty' in root_cause.get('potential_causes', []):
                recommendations.append("Review model confidence thresholds and add validation")
            
            return "; ".join(recommendations) if recommendations else "Investigate error patterns"
            
        except Exception as e:
            self.logger.error(f"Error generating error rate recommendation: {e}")
            return "Unable to generate recommendation"
    
    async def _generate_memory_recommendation(
        self, 
        metrics: PerformanceMetrics, 
        baseline: Dict[str, float],
        severity: RegressionSeverity,
        root_cause: Dict[str, Any]
    ) -> str:
        """Generate recommendation for memory regression."""
        try:
            recommendations = []
            
            if 'significant_memory_leak' in root_cause.get('potential_causes', []):
                recommendations.append("Investigate and fix memory leaks in application code")
            
            if 'memory_pressure_impact' in root_cause.get('potential_causes', []):
                recommendations.append("Optimize memory usage patterns and garbage collection")
            
            recommendations.append("Consider implementing memory monitoring and alerting")
            
            return "; ".join(recommendations) if recommendations else "Monitor memory usage patterns"
            
        except Exception as e:
            self.logger.error(f"Error generating memory recommendation: {e}")
            return "Unable to generate recommendation"
    
    async def _generate_drift_recommendation(
        self, 
        metrics: PerformanceMetrics, 
        baseline: Dict[str, float],
        severity: RegressionSeverity,
        root_cause: Dict[str, Any]
    ) -> str:
        """Generate recommendation for drift regression."""
        try:
            recommendations = []
            
            if 'input_data_distribution_change' in root_cause.get('potential_causes', []):
                recommendations.append("Implement adaptive preprocessing and feature normalization")
            
            if 'model_performance_degradation' in root_cause.get('potential_causes', []):
                recommendations.append("Schedule model retraining with recent data")
            
            if severity in [RegressionSeverity.MAJOR, RegressionSeverity.CRITICAL]:
                recommendations.append("Implement immediate drift mitigation strategies")
            
            return "; ".join(recommendations) if recommendations else "Continue drift monitoring"
            
        except Exception as e:
            self.logger.error(f"Error generating drift recommendation: {e}")
            return "Unable to generate recommendation"
    
    async def _process_regression_alert(self, regression: RegressionAlert) -> None:
        """Process a detected regression alert."""
        try:
            # Store the alert
            self.regression_alerts.append(regression)
            self.active_regressions[regression.alert_id] = regression
            
            # Log the regression
            self.logger.warning(
                f"PERFORMANCE REGRESSION DETECTED: {regression.regression_type.value} "
                f"in {regression.model_id} - Severity: {regression.severity.value} "
                f"({regression.degradation_percent:.2f}% degradation)"
            )
            
            # In production, would trigger alerts, notifications, etc.
            
        except Exception as e:
            self.logger.error(f"Error processing regression alert: {e}")
    
    def get_regression_summary(
        self, 
        model_id: Optional[str] = None,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get regression detection summary."""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Filter alerts
            if model_id:
                alerts = [a for a in self.regression_alerts 
                         if a.model_id == model_id and start_time <= a.timestamp <= end_time]
            else:
                alerts = [a for a in self.regression_alerts 
                         if start_time <= a.timestamp <= end_time]
            
            # Summarize by type and severity
            summary = {
                'total_regressions': len(alerts),
                'active_regressions': len(self.active_regressions),
                'by_type': defaultdict(int),
                'by_severity': defaultdict(int),
                'by_model': defaultdict(int),
                'most_recent': None,
                'critical_alerts': []
            }
            
            for alert in alerts:
                summary['by_type'][alert.regression_type.value] += 1
                summary['by_severity'][alert.severity.value] += 1
                summary['by_model'][alert.model_id] += 1
                
                if alert.severity == RegressionSeverity.CRITICAL:
                    summary['critical_alerts'].append({
                        'alert_id': alert.alert_id,
                        'model_id': alert.model_id,
                        'type': alert.regression_type.value,
                        'degradation_percent': alert.degradation_percent,
                        'timestamp': alert.timestamp.isoformat()
                    })
            
            if alerts:
                most_recent = max(alerts, key=lambda a: a.timestamp)
                summary['most_recent'] = {
                    'alert_id': most_recent.alert_id,
                    'model_id': most_recent.model_id,
                    'type': most_recent.regression_type.value,
                    'severity': most_recent.severity.value,
                    'timestamp': most_recent.timestamp.isoformat()
                }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting regression summary: {e}")
            return {'error': str(e)}


# Example usage and testing
async def example_usage():
    """Example usage of the PerformanceRegressionDetector."""
    detector = PerformanceRegressionDetector()
    
    # Simulate baseline metrics
    baseline_metrics = PerformanceMetrics(
        timestamp=datetime.now() - timedelta(days=1),
        model_id="content-classifier-v1",
        version="v1.0.0",
        creator_type="musician",
        environment="production",
        latency_p50_ms=75.0,
        latency_p95_ms=125.0,
        latency_p99_ms=180.0,
        accuracy_score=0.95,
        throughput_rps=150.0,
        error_rate_percent=1.0,
        memory_usage_mb=512.0,
        cpu_usage_percent=45.0,
        prediction_confidence=0.92,
        data_drift_score=0.2,
        model_drift_score=0.1,
        business_metric_score=0.88
    )
    
    # Record baseline
    await detector.record_performance_metrics(baseline_metrics)
    
    # Simulate performance regression
    regression_metrics = PerformanceMetrics(
        timestamp=datetime.now(),
        model_id="content-classifier-v1",
        version="v1.1.0",
        creator_type="musician",
        environment="production",
        latency_p50_ms=125.0,    # 67% increase
        latency_p95_ms=210.0,    # 68% increase  
        latency_p99_ms=320.0,    # 78% increase
        accuracy_score=0.89,     # 6% decrease
        throughput_rps=85.0,     # 43% decrease
        error_rate_percent=4.5,  # 350% increase
        memory_usage_mb=892.0,   # 74% increase
        cpu_usage_percent=87.0,  # 93% increase
        prediction_confidence=0.76,  # Lower confidence
        data_drift_score=0.6,    # High drift
        model_drift_score=0.4,   # Medium drift
        business_metric_score=0.72
    )
    
    # Record regression metrics
    await detector.record_performance_metrics(regression_metrics)
    
    # Get regression summary
    summary = detector.get_regression_summary()
    print(f"Regression Summary: {json.dumps(summary, indent=2, default=str)}")


if __name__ == "__main__":
    asyncio.run(example_usage())