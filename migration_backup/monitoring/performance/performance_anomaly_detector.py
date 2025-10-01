"""
⚠️ CONFIDENTIEL - IA Chéries Creator Platform ⚠️

Performance Anomaly Detector Enterprise
Advanced ML-powered performance anomaly detection for Creator Economy platform

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import asyncio
import time
import json
import logging
import statistics
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from collections import deque, defaultdict, Counter
import threading
from concurrent.futures import ThreadPoolExecutor
import pickle
import hashlib
from enum import Enum

# ML and anomaly detection imports
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from sklearn.cluster import DBSCAN
    import pandas as pd
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from scipy import stats
    import scipy.signal
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

# Prometheus metrics
from prometheus_client import Gauge, Counter, Histogram

logger = logging.getLogger(__name__)

class AnomalyType(Enum):
    PERFORMANCE_DEGRADATION = "performance_degradation"
    RESOURCE_SPIKE = "resource_spike"
    ERROR_RATE_INCREASE = "error_rate_increase"
    LATENCY_ANOMALY = "latency_anomaly"
    THROUGHPUT_DROP = "throughput_drop"
    MEMORY_LEAK = "memory_leak"
    CPU_SATURATION = "cpu_saturation"
    NETWORK_ANOMALY = "network_anomaly"
    DATABASE_SLOWDOWN = "database_slowdown"
    QUEUE_BACKLOG = "queue_backlog"

class SeverityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PerformanceAnomaly:
    """Performance anomaly detection result"""
    anomaly_id: str
    anomaly_type: AnomalyType
    severity: SeverityLevel
    confidence_score: float  # 0.0 to 1.0
    detected_at: datetime
    metric_name: str
    metric_value: float
    expected_value: Optional[float]
    deviation_percentage: float
    affected_components: List[str]
    root_cause_analysis: Optional[str]
    recommended_actions: List[str]
    historical_context: Dict[str, Any]
    creator_impact: Optional[str] = None
    business_impact: Optional[str] = None

@dataclass
class AnomalyDetectionModel:
    """Anomaly detection model configuration"""
    model_name: str
    model_type: str  # isolation_forest, statistical, time_series, clustering
    metric_patterns: List[str]
    sensitivity: float  # 0.0 to 1.0
    training_window_hours: int
    detection_threshold: float
    model_data: Optional[bytes] = None
    last_trained: Optional[datetime] = None
    accuracy_score: Optional[float] = None

@dataclass
class MetricDataPoint:
    """Time series data point for anomaly detection"""
    timestamp: datetime
    metric_name: str
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class PerformanceAnomalyDetector:
    """
    Enterprise Performance Anomaly Detector
    Advanced ML-powered anomaly detection for Creator Economy platform
    Uses multiple detection algorithms for comprehensive monitoring
    """
    
    def __init__(self,
                 enable_ml_detection: bool = True,
                 enable_statistical_detection: bool = True,
                 enable_time_series_detection: bool = True,
                 detection_interval: int = 60,  # seconds
                 training_interval: int = 3600,  # seconds (1 hour)
                 max_history_points: int = 50000):
        
        self.enable_ml_detection = enable_ml_detection and SKLEARN_AVAILABLE
        self.enable_statistical_detection = enable_statistical_detection and SCIPY_AVAILABLE
        self.enable_time_series_detection = enable_time_series_detection and PROPHET_AVAILABLE
        self.detection_interval = detection_interval
        self.training_interval = training_interval
        self.max_history_points = max_history_points
        
        # Data storage
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history_points))
        self.detected_anomalies: deque = deque(maxlen=10000)
        self.active_anomalies: Dict[str, PerformanceAnomaly] = {}
        
        # Models
        self.anomaly_models: Dict[str, AnomalyDetectionModel] = {}
        self.trained_models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        
        # Detection state
        self.detection_active = False
        self.detection_thread: Optional[threading.Thread] = None
        self.training_thread: Optional[threading.Thread] = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Pattern analysis
        self.metric_patterns: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.seasonal_patterns: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.correlation_matrix: Optional[np.ndarray] = None
        
        # Thresholds and sensitivity
        self.default_sensitivity = 0.8
        self.anomaly_thresholds = {
            AnomalyType.PERFORMANCE_DEGRADATION: 0.7,
            AnomalyType.RESOURCE_SPIKE: 0.8,
            AnomalyType.ERROR_RATE_INCREASE: 0.9,
            AnomalyType.LATENCY_ANOMALY: 0.75,
            AnomalyType.THROUGHPUT_DROP: 0.8,
            AnomalyType.MEMORY_LEAK: 0.85,
            AnomalyType.CPU_SATURATION: 0.9,
        }
        
        # Initialize Prometheus metrics
        self._init_prometheus_metrics()
        
        # Initialize detection models
        self._init_detection_models()
        
        logger.info("PerformanceAnomalyDetector initialized")
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.anomalies_detected_total = Counter(
            'performance_anomalies_detected_total',
            'Total performance anomalies detected',
            ['anomaly_type', 'severity', 'metric_name']
        )
        
        self.anomaly_confidence_score = Histogram(
            'performance_anomaly_confidence_score',
            'Anomaly detection confidence score',
            ['anomaly_type', 'metric_name']
        )
        
        self.active_anomalies_count = Gauge(
            'performance_active_anomalies_count',
            'Number of active performance anomalies',
            ['severity']
        )
        
        self.detection_model_accuracy = Gauge(
            'performance_anomaly_model_accuracy',
            'Anomaly detection model accuracy',
            ['model_name', 'metric_pattern']
        )
        
        self.metric_deviation_percentage = Histogram(
            'performance_metric_deviation_percentage',
            'Metric deviation from expected value',
            ['metric_name']
        )
    
    def _init_detection_models(self):
        """Initialize anomaly detection models"""
        # Performance metrics patterns
        performance_patterns = [
            'api_response_time',
            'database_query_time',
            'content_processing_time',
            'background_job_duration'
        ]
        
        # Resource patterns
        resource_patterns = [
            'cpu_usage_percent',
            'memory_usage_percent',
            'disk_usage_percent',
            'network_bytes_per_second'
        ]
        
        # Error patterns
        error_patterns = [
            'error_rate_percent',
            'failed_requests_per_minute',
            'timeout_count',
            'exception_count'
        ]
        
        # Initialize models for each pattern group
        self._create_model_for_patterns('performance_isolation_forest', 'isolation_forest', 
                                      performance_patterns, sensitivity=0.8)
        self._create_model_for_patterns('resource_isolation_forest', 'isolation_forest', 
                                      resource_patterns, sensitivity=0.85)
        self._create_model_for_patterns('error_statistical', 'statistical', 
                                      error_patterns, sensitivity=0.9)
        
        if self.enable_time_series_detection:
            self._create_model_for_patterns('performance_time_series', 'time_series', 
                                          performance_patterns, sensitivity=0.75)
    
    def _create_model_for_patterns(self, model_name: str, model_type: str, 
                                 patterns: List[str], sensitivity: float):
        """Create anomaly detection model for metric patterns"""
        model = AnomalyDetectionModel(
            model_name=model_name,
            model_type=model_type,
            metric_patterns=patterns,
            sensitivity=sensitivity,
            training_window_hours=24,
            detection_threshold=self._calculate_threshold(sensitivity),
            last_trained=None,
            accuracy_score=None
        )
        
        self.anomaly_models[model_name] = model
    
    def _calculate_threshold(self, sensitivity: float) -> float:
        """Calculate detection threshold based on sensitivity"""
        # Higher sensitivity = lower threshold = more anomalies detected
        return 1.0 - sensitivity
    
    async def start_detection(self):
        """Start anomaly detection"""
        if self.detection_active:
            logger.warning("Anomaly detection already active")
            return
        
        self.detection_active = True
        
        # Start detection thread
        self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.detection_thread.start()
        
        # Start training thread
        self.training_thread = threading.Thread(target=self._training_loop, daemon=True)
        self.training_thread.start()
        
        logger.info("Performance anomaly detection started")
    
    async def stop_detection(self):
        """Stop anomaly detection"""
        self.detection_active = False
        
        if self.detection_thread:
            self.detection_thread.join(timeout=30)
        
        if self.training_thread:
            self.training_thread.join(timeout=30)
        
        logger.info("Performance anomaly detection stopped")
    
    def _detection_loop(self):
        """Main anomaly detection loop"""
        while self.detection_active:
            try:
                # Run anomaly detection
                self._run_anomaly_detection()
                
                # Clean up resolved anomalies
                self._cleanup_resolved_anomalies()
                
                # Update Prometheus metrics
                self._update_prometheus_metrics()
                
                time.sleep(self.detection_interval)
                
            except Exception as e:
                logger.error(f"Error in anomaly detection loop: {e}")
                time.sleep(self.detection_interval)
    
    def _training_loop(self):
        """Model training loop"""
        while self.detection_active:
            try:
                # Retrain models periodically
                self._retrain_models()
                
                time.sleep(self.training_interval)
                
            except Exception as e:
                logger.error(f"Error in model training loop: {e}")
                time.sleep(self.training_interval)
    
    def ingest_metric(self, metric_name: str, value: float, metadata: Optional[Dict[str, Any]] = None):
        """Ingest metric data point for anomaly detection"""
        data_point = MetricDataPoint(
            timestamp=datetime.utcnow(),
            metric_name=metric_name,
            value=value,
            metadata=metadata or {}
        )
        
        self.metric_history[metric_name].append(data_point)
        
        # Update metric patterns
        self._update_metric_patterns(metric_name, value)
    
    def _update_metric_patterns(self, metric_name: str, value: float):
        """Update statistical patterns for metric"""
        history = [dp.value for dp in self.metric_history[metric_name]]
        
        if len(history) >= 10:
            self.metric_patterns[metric_name] = {
                'mean': statistics.mean(history),
                'std': statistics.stdev(history) if len(history) > 1 else 0,
                'min': min(history),
                'max': max(history),
                'median': statistics.median(history),
                'recent_trend': self._calculate_trend(history[-20:]) if len(history) >= 20 else 0
            }
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend slope for recent values"""
        if len(values) < 2:
            return 0
        
        x = list(range(len(values)))
        if SCIPY_AVAILABLE:
            slope, _, _, _, _ = stats.linregress(x, values)
            return slope
        else:
            # Simple trend calculation
            return (values[-1] - values[0]) / len(values)
    
    def _run_anomaly_detection(self):
        """Run all anomaly detection algorithms"""
        current_time = datetime.utcnow()
        
        # ML-based detection
        if self.enable_ml_detection:
            self._run_ml_detection(current_time)
        
        # Statistical detection
        if self.enable_statistical_detection:
            self._run_statistical_detection(current_time)
        
        # Time series detection
        if self.enable_time_series_detection:
            self._run_time_series_detection(current_time)
        
        # Cross-metric correlation detection
        self._run_correlation_detection(current_time)
    
    def _run_ml_detection(self, current_time: datetime):
        """Run ML-based anomaly detection"""
        for model_name, model_config in self.anomaly_models.items():
            if model_config.model_type != 'isolation_forest':
                continue
            
            try:
                # Get recent data for model patterns
                recent_data = []
                feature_names = []
                
                for pattern in model_config.metric_patterns:
                    matching_metrics = [name for name in self.metric_history.keys() if pattern in name]
                    
                    for metric_name in matching_metrics:
                        if len(self.metric_history[metric_name]) < 10:
                            continue
                        
                        recent_values = [dp.value for dp in list(self.metric_history[metric_name])[-100:]]
                        if recent_values:
                            recent_data.append(recent_values[-1])  # Latest value
                            feature_names.append(metric_name)
                
                if len(recent_data) < 2:
                    continue
                
                # Prepare data
                X = np.array(recent_data).reshape(1, -1)
                
                # Get or train model
                if model_name not in self.trained_models:
                    self._train_isolation_forest(model_name, feature_names)
                
                if model_name in self.trained_models:
                    model = self.trained_models[model_name]
                    scaler = self.scalers.get(model_name)
                    
                    # Scale data
                    if scaler:
                        X_scaled = scaler.transform(X)
                    else:
                        X_scaled = X
                    
                    # Predict anomaly
                    anomaly_score = model.decision_function(X_scaled)[0]
                    is_anomaly = model.predict(X_scaled)[0] == -1
                    
                    if is_anomaly:
                        confidence = abs(anomaly_score)
                        self._create_anomaly(
                            anomaly_type=AnomalyType.PERFORMANCE_DEGRADATION,
                            metric_name=f"ml_model_{model_name}",
                            metric_value=anomaly_score,
                            confidence_score=min(confidence, 1.0),
                            affected_components=feature_names,
                            detection_method="isolation_forest"
                        )
            
            except Exception as e:
                logger.error(f"Error in ML detection for {model_name}: {e}")
    
    def _train_isolation_forest(self, model_name: str, feature_names: List[str]):
        """Train Isolation Forest model"""
        if not SKLEARN_AVAILABLE:
            return
        
        try:
            # Collect training data
            training_data = []
            min_samples = float('inf')
            
            for metric_name in feature_names:
                metric_values = [dp.value for dp in self.metric_history[metric_name]]
                if len(metric_values) < 100:  # Need sufficient data
                    continue
                training_data.append(metric_values[-1000:])  # Last 1000 points
                min_samples = min(min_samples, len(metric_values))
            
            if len(training_data) < 2 or min_samples < 100:
                return
            
            # Prepare training matrix
            X = np.array(training_data).T[:min_samples]
            
            # Scale data
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Train Isolation Forest
            model = IsolationForest(
                contamination=0.1,  # Expect 10% anomalies
                random_state=42,
                n_estimators=100
            )
            model.fit(X_scaled)
            
            # Store model and scaler
            self.trained_models[model_name] = model
            self.scalers[model_name] = scaler
            
            # Update model metadata
            self.anomaly_models[model_name].last_trained = datetime.utcnow()
            
            logger.info(f"Trained Isolation Forest model: {model_name}")
        
        except Exception as e:
            logger.error(f"Error training Isolation Forest {model_name}: {e}")
    
    def _run_statistical_detection(self, current_time: datetime):
        """Run statistical anomaly detection"""
        for metric_name, history in self.metric_history.items():
            if len(history) < 30:  # Need sufficient history
                continue
            
            try:
                values = [dp.value for dp in history]
                recent_value = values[-1]
                
                # Z-score based detection
                if len(values) > 10:
                    mean_val = statistics.mean(values[:-1])  # Exclude current value
                    std_val = statistics.stdev(values[:-1]) if len(values) > 2 else 0
                    
                    if std_val > 0:
                        z_score = abs((recent_value - mean_val) / std_val)
                        
                        # Detect anomaly if z-score > threshold
                        if z_score > 3.0:  # 3-sigma rule
                            confidence = min(z_score / 5.0, 1.0)  # Normalize to 0-1
                            deviation_pct = abs((recent_value - mean_val) / mean_val) * 100
                            
                            anomaly_type = self._classify_statistical_anomaly(metric_name, recent_value, mean_val)
                            
                            self._create_anomaly(
                                anomaly_type=anomaly_type,
                                metric_name=metric_name,
                                metric_value=recent_value,
                                expected_value=mean_val,
                                confidence_score=confidence,
                                deviation_percentage=deviation_pct,
                                detection_method="statistical_zscore"
                            )
                
                # Trend-based detection
                if len(values) >= 20:
                    recent_trend = self._calculate_trend(values[-20:])
                    long_term_trend = self._calculate_trend(values[-100:]) if len(values) >= 100 else 0
                    
                    # Detect sudden trend changes
                    if abs(recent_trend - long_term_trend) > statistics.stdev(values) * 0.1:
                        self._create_anomaly(
                            anomaly_type=AnomalyType.PERFORMANCE_DEGRADATION,
                            metric_name=metric_name,
                            metric_value=recent_trend,
                            confidence_score=0.6,
                            detection_method="trend_analysis"
                        )
            
            except Exception as e:
                logger.error(f"Error in statistical detection for {metric_name}: {e}")
    
    def _classify_statistical_anomaly(self, metric_name: str, value: float, expected: float) -> AnomalyType:
        """Classify anomaly type based on metric name and deviation"""
        metric_lower = metric_name.lower()
        
        if 'cpu' in metric_lower and value > expected:
            return AnomalyType.CPU_SATURATION
        elif 'memory' in metric_lower and value > expected:
            return AnomalyType.MEMORY_LEAK
        elif 'response_time' in metric_lower or 'latency' in metric_lower:
            return AnomalyType.LATENCY_ANOMALY
        elif 'error' in metric_lower or 'fail' in metric_lower:
            return AnomalyType.ERROR_RATE_INCREASE
        elif 'throughput' in metric_lower and value < expected:
            return AnomalyType.THROUGHPUT_DROP
        elif 'network' in metric_lower:
            return AnomalyType.NETWORK_ANOMALY
        elif 'database' in metric_lower or 'db' in metric_lower:
            return AnomalyType.DATABASE_SLOWDOWN
        else:
            return AnomalyType.PERFORMANCE_DEGRADATION
    
    def _run_time_series_detection(self, current_time: datetime):
        """Run time series based anomaly detection using Prophet"""
        if not PROPHET_AVAILABLE:
            return
        
        # Implementation would use Prophet for time series forecasting
        # This is a simplified version focusing on seasonal patterns
        for metric_name, history in self.metric_history.items():
            if len(history) < 100:  # Need sufficient history for time series
                continue
            
            try:
                # Detect seasonal anomalies (simplified approach)
                values = [dp.value for dp in history]
                timestamps = [dp.timestamp for dp in history]
                
                # Look for weekly/daily patterns
                if len(values) >= 168:  # At least 1 week of hourly data
                    recent_hour = current_time.hour
                    same_hour_values = []
                    
                    for i, ts in enumerate(timestamps):
                        if ts.hour == recent_hour and i < len(values) - 1:
                            same_hour_values.append(values[i])
                    
                    if len(same_hour_values) >= 7:  # At least a week of same-hour data
                        expected = statistics.median(same_hour_values)
                        current_value = values[-1]
                        
                        if abs(current_value - expected) > statistics.stdev(same_hour_values) * 2:
                            deviation_pct = abs((current_value - expected) / expected) * 100
                            
                            self._create_anomaly(
                                anomaly_type=AnomalyType.PERFORMANCE_DEGRADATION,
                                metric_name=metric_name,
                                metric_value=current_value,
                                expected_value=expected,
                                confidence_score=0.7,
                                deviation_percentage=deviation_pct,
                                detection_method="seasonal_pattern"
                            )
            
            except Exception as e:
                logger.error(f"Error in time series detection for {metric_name}: {e}")
    
    def _run_correlation_detection(self, current_time: datetime):
        """Run cross-metric correlation anomaly detection"""
        try:
            # Build correlation matrix for recent data
            metric_names = list(self.metric_history.keys())
            if len(metric_names) < 2:
                return
            
            # Get recent values for all metrics
            recent_data = {}
            min_length = float('inf')
            
            for metric_name in metric_names:
                values = [dp.value for dp in list(self.metric_history[metric_name])[-100:]]
                if len(values) >= 10:
                    recent_data[metric_name] = values
                    min_length = min(min_length, len(values))
            
            if len(recent_data) < 2 or min_length < 10:
                return
            
            # Create correlation matrix
            data_matrix = []
            for metric_name in recent_data.keys():
                data_matrix.append(recent_data[metric_name][:min_length])
            
            if SKLEARN_AVAILABLE and len(data_matrix) >= 2:
                correlation_matrix = np.corrcoef(data_matrix)
                
                # Detect correlation anomalies
                for i, metric1 in enumerate(recent_data.keys()):
                    for j, metric2 in enumerate(recent_data.keys()):
                        if i >= j:
                            continue
                        
                        correlation = correlation_matrix[i][j]
                        
                        # Strong correlation expected but broken
                        if abs(correlation) < 0.3 and self._should_be_correlated(metric1, metric2):
                            self._create_anomaly(
                                anomaly_type=AnomalyType.PERFORMANCE_DEGRADATION,
                                metric_name=f"correlation_{metric1}_{metric2}",
                                metric_value=correlation,
                                confidence_score=0.6,
                                affected_components=[metric1, metric2],
                                detection_method="correlation_analysis"
                            )
        
        except Exception as e:
            logger.error(f"Error in correlation detection: {e}")
    
    def _should_be_correlated(self, metric1: str, metric2: str) -> bool:
        """Determine if two metrics should be correlated"""
        # Define expected correlations between metrics
        correlations = [
            ('cpu_usage', 'response_time'),
            ('memory_usage', 'gc_time'),
            ('database_connections', 'database_query_time'),
            ('queue_size', 'processing_time'),
            ('error_rate', 'response_time')
        ]
        
        for m1, m2 in correlations:
            if (m1 in metric1.lower() and m2 in metric2.lower()) or \
               (m2 in metric1.lower() and m1 in metric2.lower()):
                return True
        
        return False
    
    def _create_anomaly(self,
                       anomaly_type: AnomalyType,
                       metric_name: str,
                       metric_value: float,
                       confidence_score: float,
                       expected_value: Optional[float] = None,
                       deviation_percentage: Optional[float] = None,
                       affected_components: Optional[List[str]] = None,
                       detection_method: str = "unknown"):
        """Create and register a performance anomaly"""
        
        # Generate unique anomaly ID
        anomaly_data = f"{anomaly_type.value}_{metric_name}_{metric_value}_{datetime.utcnow().isoformat()}"
        anomaly_id = hashlib.md5(anomaly_data.encode()).hexdigest()[:12]
        
        # Determine severity
        severity = self._calculate_severity(anomaly_type, confidence_score, deviation_percentage)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(anomaly_type, metric_name, metric_value, expected_value)
        
        # Create anomaly object
        anomaly = PerformanceAnomaly(
            anomaly_id=anomaly_id,
            anomaly_type=anomaly_type,
            severity=severity,
            confidence_score=confidence_score,
            detected_at=datetime.utcnow(),
            metric_name=metric_name,
            metric_value=metric_value,
            expected_value=expected_value,
            deviation_percentage=deviation_percentage or 0,
            affected_components=affected_components or [metric_name],
            root_cause_analysis=self._analyze_root_cause(anomaly_type, metric_name, metric_value),
            recommended_actions=recommendations,
            historical_context=self._get_historical_context(metric_name),
            creator_impact=self._assess_creator_impact(anomaly_type, metric_name),
            business_impact=self._assess_business_impact(anomaly_type, severity)
        )
        
        # Store anomaly
        self.detected_anomalies.append(anomaly)
        self.active_anomalies[anomaly_id] = anomaly
        
        # Update Prometheus metrics
        self.anomalies_detected_total.labels(
            anomaly_type=anomaly_type.value,
            severity=severity.value,
            metric_name=metric_name
        ).inc()
        
        self.anomaly_confidence_score.labels(
            anomaly_type=anomaly_type.value,
            metric_name=metric_name
        ).observe(confidence_score)
        
        if deviation_percentage:
            self.metric_deviation_percentage.labels(
                metric_name=metric_name
            ).observe(deviation_percentage)
        
        logger.warning(f"Anomaly detected: {anomaly_type.value} in {metric_name} "
                      f"(confidence: {confidence_score:.2f}, severity: {severity.value})")
    
    def _calculate_severity(self, 
                          anomaly_type: AnomalyType, 
                          confidence_score: float, 
                          deviation_percentage: Optional[float]) -> SeverityLevel:
        """Calculate anomaly severity level"""
        # Base severity on confidence and deviation
        base_score = confidence_score
        
        if deviation_percentage:
            # Higher deviation increases severity
            deviation_factor = min(deviation_percentage / 100, 1.0)
            base_score = min(base_score + deviation_factor * 0.3, 1.0)
        
        # Adjust based on anomaly type
        critical_types = [AnomalyType.CPU_SATURATION, AnomalyType.MEMORY_LEAK, AnomalyType.ERROR_RATE_INCREASE]
        if anomaly_type in critical_types:
            base_score = min(base_score + 0.2, 1.0)
        
        if base_score >= 0.9:
            return SeverityLevel.CRITICAL
        elif base_score >= 0.7:
            return SeverityLevel.HIGH
        elif base_score >= 0.5:
            return SeverityLevel.MEDIUM
        else:
            return SeverityLevel.LOW
    
    def _generate_recommendations(self,
                                anomaly_type: AnomalyType,
                                metric_name: str,
                                metric_value: float,
                                expected_value: Optional[float]) -> List[str]:
        """Generate actionable recommendations for anomaly"""
        recommendations = []
        
        if anomaly_type == AnomalyType.CPU_SATURATION:
            recommendations.extend([
                "Check for CPU-intensive processes",
                "Consider horizontal scaling",
                "Review algorithm efficiency",
                "Implement CPU throttling if necessary"
            ])
        elif anomaly_type == AnomalyType.MEMORY_LEAK:
            recommendations.extend([
                "Investigate memory usage patterns",
                "Check for memory leaks in application code",
                "Review garbage collection settings",
                "Consider memory profiling"
            ])
        elif anomaly_type == AnomalyType.LATENCY_ANOMALY:
            recommendations.extend([
                "Check network connectivity",
                "Review database query performance",
                "Investigate external service dependencies",
                "Consider caching strategies"
            ])
        elif anomaly_type == AnomalyType.ERROR_RATE_INCREASE:
            recommendations.extend([
                "Review recent deployments",
                "Check error logs for patterns",
                "Investigate external dependencies",
                "Consider implementing circuit breakers"
            ])
        elif anomaly_type == AnomalyType.THROUGHPUT_DROP:
            recommendations.extend([
                "Check resource utilization",
                "Review queue processing",
                "Investigate bottlenecks",
                "Consider scaling resources"
            ])
        else:
            recommendations.extend([
                "Monitor trend continuation",
                "Review recent changes",
                "Check system health",
                "Consider preventive scaling"
            ])
        
        return recommendations
    
    def _analyze_root_cause(self, anomaly_type: AnomalyType, metric_name: str, metric_value: float) -> str:
        """Perform basic root cause analysis"""
        analysis = f"Anomaly detected in {metric_name} with value {metric_value}. "
        
        # Add context based on metric patterns
        if metric_name in self.metric_patterns:
            patterns = self.metric_patterns[metric_name]
            
            if metric_value > patterns.get('max', 0):
                analysis += "Value exceeds historical maximum. "
            
            trend = patterns.get('recent_trend', 0)
            if trend > 0:
                analysis += "Recent upward trend detected. "
            elif trend < 0:
                analysis += "Recent downward trend detected. "
        
        return analysis
    
    def _get_historical_context(self, metric_name: str) -> Dict[str, Any]:
        """Get historical context for the metric"""
        if metric_name not in self.metric_patterns:
            return {}
        
        return self.metric_patterns[metric_name].copy()
    
    def _assess_creator_impact(self, anomaly_type: AnomalyType, metric_name: str) -> str:
        """Assess impact on Creator Economy workflows"""
        if 'content_processing' in metric_name or 'upload' in metric_name:
            return "Content creation workflows may be affected"
        elif 'api_response' in metric_name:
            return "Creator dashboard responsiveness may be impacted"
        elif 'database' in metric_name:
            return "Creator data operations may be slower"
        elif 'background_job' in metric_name:
            return "Background content processing may be delayed"
        else:
            return "General platform performance may affect creator experience"
    
    def _assess_business_impact(self, anomaly_type: AnomalyType, severity: SeverityLevel) -> str:
        """Assess business impact of the anomaly"""
        if severity == SeverityLevel.CRITICAL:
            return "High business impact - immediate attention required"
        elif severity == SeverityLevel.HIGH:
            return "Moderate business impact - should be addressed promptly"
        elif severity == SeverityLevel.MEDIUM:
            return "Low to moderate business impact - monitor closely"
        else:
            return "Minimal business impact - informational"
    
    def _cleanup_resolved_anomalies(self):
        """Clean up anomalies that have been resolved"""
        current_time = datetime.utcnow()
        resolved_anomalies = []
        
        for anomaly_id, anomaly in self.active_anomalies.items():
            # Check if anomaly has been resolved (simplified logic)
            if current_time - anomaly.detected_at > timedelta(hours=1):
                # Check if metric has returned to normal
                if anomaly.metric_name in self.metric_history:
                    recent_values = [dp.value for dp in list(self.metric_history[anomaly.metric_name])[-10:]]
                    if recent_values and anomaly.expected_value:
                        recent_avg = statistics.mean(recent_values)
                        if abs(recent_avg - anomaly.expected_value) / anomaly.expected_value < 0.1:  # Within 10%
                            resolved_anomalies.append(anomaly_id)
        
        # Remove resolved anomalies
        for anomaly_id in resolved_anomalies:
            del self.active_anomalies[anomaly_id]
            logger.info(f"Anomaly {anomaly_id} has been resolved")
    
    def _update_prometheus_metrics(self):
        """Update Prometheus metrics"""
        # Update active anomalies count by severity
        severity_counts = Counter(anomaly.severity for anomaly in self.active_anomalies.values())
        
        for severity in SeverityLevel:
            self.active_anomalies_count.labels(severity=severity.value).set(
                severity_counts.get(severity, 0)
            )
    
    def _retrain_models(self):
        """Retrain anomaly detection models periodically"""
        for model_name, model_config in self.anomaly_models.items():
            if model_config.model_type == 'isolation_forest':
                # Find metrics matching the model patterns
                matching_metrics = []
                for pattern in model_config.metric_patterns:
                    matching_metrics.extend([
                        name for name in self.metric_history.keys() 
                        if pattern in name and len(self.metric_history[name]) >= 100
                    ])
                
                if matching_metrics:
                    self._train_isolation_forest(model_name, matching_metrics)
    
    async def get_anomaly_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get anomaly detection summary"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_anomalies = [a for a in self.detected_anomalies if a.detected_at >= cutoff_time]
        
        # Group by type and severity
        anomaly_by_type = Counter(a.anomaly_type for a in recent_anomalies)
        anomaly_by_severity = Counter(a.severity for a in recent_anomalies)
        
        # Top affected metrics
        affected_metrics = Counter(a.metric_name for a in recent_anomalies)
        
        return {
            'time_window_hours': hours,
            'summary_timestamp': datetime.utcnow().isoformat(),
            'total_anomalies': len(recent_anomalies),
            'active_anomalies': len(self.active_anomalies),
            'anomalies_by_type': {t.value: count for t, count in anomaly_by_type.items()},
            'anomalies_by_severity': {s.value: count for s, count in anomaly_by_severity.items()},
            'top_affected_metrics': dict(affected_metrics.most_common(10)),
            'recent_critical_anomalies': [
                {
                    'anomaly_id': a.anomaly_id,
                    'type': a.anomaly_type.value,
                    'metric': a.metric_name,
                    'confidence': a.confidence_score,
                    'detected_at': a.detected_at.isoformat()
                }
                for a in recent_anomalies 
                if a.severity == SeverityLevel.CRITICAL
            ][:5],
            'model_status': {
                name: {
                    'last_trained': model.last_trained.isoformat() if model.last_trained else None,
                    'accuracy': model.accuracy_score
                }
                for name, model in self.anomaly_models.items()
            }
        }
    
    async def get_anomaly_details(self, anomaly_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific anomaly"""
        if anomaly_id in self.active_anomalies:
            anomaly = self.active_anomalies[anomaly_id]
            return asdict(anomaly)
        
        # Search in historical anomalies
        for anomaly in self.detected_anomalies:
            if anomaly.anomaly_id == anomaly_id:
                return asdict(anomaly)
        
        return None