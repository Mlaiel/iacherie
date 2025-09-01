"""Advanced Anomaly Detection Module

Enterprise-grade ML-based anomaly detection for IA Influencer Agent platform.
Uses statistical analysis and machine learning to detect performance and business anomalies.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
"""
import asyncio
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import deque, defaultdict
from enum import Enum
import logging
import json
import statistics
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import scipy.stats as stats

from ..core.metrics import MetricsCollector, MetricEntry, MetricType, MetricPriority
from ..core.exceptions import AnomalyDetectionError
from .real_time_alerts import AlertSeverity, AlertCategory

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Types of anomalies that can be detected"""
    STATISTICAL = "statistical"
    TREND = "trend"
    SEASONAL = "seasonal"
    PATTERN = "pattern"
    THRESHOLD = "threshold"
    CLUSTER = "cluster"
    BEHAVIORAL = "behavioral"
    PERFORMANCE = "performance"
    BUSINESS = "business"
    SECURITY = "security"


class AnomalySeverity(Enum):
    """Severity levels for detected anomalies"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DetectionMethod(Enum):
    """Anomaly detection methods"""
    Z_SCORE = "z_score"
    IQR = "iqr"
    ISOLATION_FOREST = "isolation_forest"
    DBSCAN = "dbscan"
    MOVING_AVERAGE = "moving_average"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    SEASONAL_DECOMPOSITION = "seasonal_decomposition"
    CHANGE_POINT = "change_point"
    CUSTOM_THRESHOLD = "custom_threshold"


@dataclass
class AnomalyPoint:
    """Represents a detected anomaly"""
    timestamp: datetime
    metric_name: str
    value: float
    expected_value: float
    deviation: float
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    detection_method: DetectionMethod
    confidence_score: float
    context: Dict[str, Any] = field(default_factory=dict)
    related_metrics: List[str] = field(default_factory=list)
    description: str = ""
    suggested_actions: List[str] = field(default_factory=list)


@dataclass
class AnomalyPattern:
    """Represents a pattern of anomalies"""
    pattern_id: str
    pattern_name: str
    anomaly_points: List[AnomalyPoint]
    start_time: datetime
    end_time: datetime
    frequency: float  # anomalies per hour
    affected_metrics: List[str]
    pattern_confidence: float
    root_cause_candidates: List[str] = field(default_factory=list)


@dataclass
class DetectionModel:
    """Configuration for an anomaly detection model"""
    model_id: str
    metric_name: str
    detection_method: DetectionMethod
    parameters: Dict[str, Any]
    enabled: bool = True
    sensitivity: float = 0.8
    min_samples: int = 50
    window_size: int = 100
    update_frequency: timedelta = timedelta(minutes=5)
    last_trained: Optional[datetime] = None


class AnomalyDetection:
    """
    Advanced Anomaly Detection System
    
    Provides ML-based anomaly detection for performance metrics, business KPIs,
    and user behavior patterns in the IA Influencer Agent platform.
    """
    
    def __init__(
        self,
        metrics_collector: Optional[MetricsCollector] = None,
        sensitivity: float = 0.8,
        min_confidence: float = 0.7
    ):
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.sensitivity = sensitivity
        self.min_confidence = min_confidence
        
        # Detection models and data
        self.detection_models: Dict[str, DetectionModel] = {}
        self.metric_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.detected_anomalies: deque = deque(maxlen=1000)
        self.anomaly_patterns: Dict[str, AnomalyPattern] = {}
        
        # Statistical baselines
        self.baselines: Dict[str, Dict[str, float]] = {}
        self.seasonal_patterns: Dict[str, Dict[str, float]] = {}
        self.trend_models: Dict[str, Any] = {}
        
        # ML models
        self.isolation_forests: Dict[str, IsolationForest] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.clustering_models: Dict[str, DBSCAN] = {}
        
        # Detection state
        self.is_detecting = False
        self._detection_task: Optional[asyncio.Task] = None
        
        # Callbacks for anomaly notifications
        self.anomaly_callbacks: List[Callable[[AnomalyPoint], None]] = []
        
        # Initialize default detection models
        self._initialize_default_models()
        
    async def start_detection(self) -> None:
        """Start anomaly detection monitoring"""
        if self.is_detecting:
            logger.warning("Anomaly detection is already running")
            return
            
        self.is_detecting = True
        self._detection_task = asyncio.create_task(self._detection_loop())
        
        logger.info("Anomaly detection started successfully")
        
    async def stop_detection(self) -> None:
        """Stop anomaly detection monitoring"""
        if not self.is_detecting:
            return
            
        self.is_detecting = False
        
        if self._detection_task:
            self._detection_task.cancel()
            try:
                await self._detection_task
            except asyncio.CancelledError:
                pass
                
        logger.info("Anomaly detection stopped")
        
    def add_detection_model(self, model: DetectionModel) -> None:
        """Add a new anomaly detection model"""
        self.detection_models[model.model_id] = model
        logger.info(f"Added anomaly detection model: {model.model_id}")
        
    def remove_detection_model(self, model_id: str) -> bool:
        """Remove an anomaly detection model"""
        if model_id in self.detection_models:
            del self.detection_models[model_id]
            logger.info(f"Removed anomaly detection model: {model_id}")
            return True
        return False
        
    async def add_metric_data(
        self,
        metric_name: str,
        value: float,
        timestamp: Optional[datetime] = None
    ) -> None:
        """Add new metric data point for anomaly detection"""
        if timestamp is None:
            timestamp = datetime.utcnow()
            
        data_point = {
            "timestamp": timestamp,
            "value": value
        }
        
        self.metric_data[metric_name].append(data_point)
        
        # Check for real-time anomalies
        await self._check_realtime_anomalies(metric_name, value, timestamp)
        
    async def detect_anomalies(
        self,
        metric_name: str,
        detection_method: Optional[DetectionMethod] = None
    ) -> List[AnomalyPoint]:
        """Detect anomalies in a specific metric"""
        if metric_name not in self.metric_data:
            return []
            
        data = list(self.metric_data[metric_name])
        if len(data) < 10:  # Need minimum data points
            return []
            
        values = [point["value"] for point in data]
        timestamps = [point["timestamp"] for point in data]
        
        anomalies = []
        
        # Use specified method or try multiple methods
        methods = [detection_method] if detection_method else [
            DetectionMethod.Z_SCORE,
            DetectionMethod.IQR,
            DetectionMethod.ISOLATION_FOREST
        ]
        
        for method in methods:
            try:
                method_anomalies = await self._detect_with_method(
                    metric_name, values, timestamps, method
                )
                anomalies.extend(method_anomalies)
            except Exception as e:
                logger.error(f"Anomaly detection failed for {metric_name} with {method}: {e}")
                
        # Remove duplicates and sort by timestamp
        unique_anomalies = self._deduplicate_anomalies(anomalies)
        return sorted(unique_anomalies, key=lambda x: x.timestamp)
        
    async def detect_patterns(
        self,
        time_window: timedelta = timedelta(hours=24)
    ) -> List[AnomalyPattern]:
        """Detect patterns in anomalies"""
        cutoff_time = datetime.utcnow() - time_window
        
        # Get recent anomalies
        recent_anomalies = [
            anomaly for anomaly in self.detected_anomalies
            if anomaly.timestamp >= cutoff_time
        ]
        
        if len(recent_anomalies) < 3:
            return []
            
        patterns = []
        
        # Group anomalies by metric
        metric_anomalies = defaultdict(list)
        for anomaly in recent_anomalies:
            metric_anomalies[anomaly.metric_name].append(anomaly)
            
        # Detect temporal patterns
        for metric_name, anomalies in metric_anomalies.items():
            if len(anomalies) >= 3:
                temporal_patterns = self._detect_temporal_patterns(metric_name, anomalies)
                patterns.extend(temporal_patterns)
                
        # Detect cross-metric patterns
        cross_patterns = self._detect_cross_metric_patterns(recent_anomalies)
        patterns.extend(cross_patterns)
        
        return patterns
        
    async def get_anomaly_summary(
        self,
        time_window: timedelta = timedelta(hours=24)
    ) -> Dict[str, Any]:
        """Get summary of detected anomalies"""
        cutoff_time = datetime.utcnow() - time_window
        
        recent_anomalies = [
            anomaly for anomaly in self.detected_anomalies
            if anomaly.timestamp >= cutoff_time
        ]
        
        if not recent_anomalies:
            return {
                "time_window": str(time_window),
                "total_anomalies": 0,
                "message": "No anomalies detected in the specified time window"
            }
            
        # Categorize anomalies
        by_severity = defaultdict(int)
        by_type = defaultdict(int)
        by_metric = defaultdict(int)
        by_method = defaultdict(int)
        
        for anomaly in recent_anomalies:
            by_severity[anomaly.severity.value] += 1
            by_type[anomaly.anomaly_type.value] += 1
            by_metric[anomaly.metric_name] += 1
            by_method[anomaly.detection_method.value] += 1
            
        # Calculate statistics
        confidence_scores = [a.confidence_score for a in recent_anomalies]
        deviations = [abs(a.deviation) for a in recent_anomalies]
        
        return {
            "time_window": str(time_window),
            "total_anomalies": len(recent_anomalies),
            "summary": {
                "by_severity": dict(by_severity),
                "by_type": dict(by_type),
                "by_metric": dict(by_metric),
                "by_detection_method": dict(by_method)
            },
            "statistics": {
                "average_confidence": statistics.mean(confidence_scores),
                "average_deviation": statistics.mean(deviations),
                "max_deviation": max(deviations) if deviations else 0,
                "anomaly_rate": len(recent_anomalies) / time_window.total_seconds() * 3600  # per hour
            },
            "top_affected_metrics": [
                {"metric": metric, "count": count}
                for metric, count in sorted(by_metric.items(), key=lambda x: x[1], reverse=True)[:5]
            ]
        }
        
    async def predict_anomalies(
        self,
        metric_name: str,
        forecast_horizon: timedelta = timedelta(hours=1)
    ) -> List[Dict[str, Any]]:
        """Predict potential future anomalies"""
        if metric_name not in self.metric_data:
            return []
            
        data = list(self.metric_data[metric_name])
        if len(data) < 50:  # Need sufficient historical data
            return []
            
        try:
            # Extract values and timestamps
            values = np.array([point["value"] for point in data[-100:]])  # Last 100 points
            timestamps = [point["timestamp"] for point in data[-100:]]
            
            # Simple trend-based prediction
            predictions = []
            
            # Calculate trend
            x = np.arange(len(values))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
            
            # Calculate prediction intervals
            current_time = datetime.utcnow()
            steps = int(forecast_horizon.total_seconds() / 300)  # 5-minute intervals
            
            for i in range(1, steps + 1):
                future_time = current_time + timedelta(minutes=5 * i)
                predicted_value = slope * (len(values) + i) + intercept
                
                # Calculate prediction uncertainty
                uncertainty = std_err * np.sqrt(1 + 1/len(values) + (i**2) / np.var(x))
                
                # Check if predicted value would be anomalous
                baseline_mean = np.mean(values)
                baseline_std = np.std(values)
                
                z_score = abs(predicted_value - baseline_mean) / baseline_std
                
                if z_score > 2.0:  # Potential anomaly
                    predictions.append({
                        "timestamp": future_time.isoformat(),
                        "predicted_value": predicted_value,
                        "baseline_mean": baseline_mean,
                        "uncertainty": uncertainty,
                        "anomaly_probability": min(z_score / 3.0, 1.0),
                        "severity": "high" if z_score > 3.0 else "medium"
                    })
                    
            return predictions
            
        except Exception as e:
            logger.error(f"Anomaly prediction failed for {metric_name}: {e}")
            return []
            
    def add_anomaly_callback(self, callback: Callable[[AnomalyPoint], None]) -> None:
        """Add callback function for anomaly notifications"""
        self.anomaly_callbacks.append(callback)
        
    def _initialize_default_models(self) -> None:
        """Initialize default detection models for common metrics"""
        default_models = [
            # AI Performance Anomalies
            DetectionModel(
                model_id="ai_inference_time_zscore",
                metric_name="ai_inference_time",
                detection_method=DetectionMethod.Z_SCORE,
                parameters={"threshold": 2.5},
                sensitivity=0.8
            ),
            
            DetectionModel(
                model_id="ai_accuracy_isolation",
                metric_name="ai_accuracy",
                detection_method=DetectionMethod.ISOLATION_FOREST,
                parameters={"contamination": 0.1, "n_estimators": 100},
                sensitivity=0.9
            ),
            
            # Business Metrics Anomalies
            DetectionModel(
                model_id="revenue_trend",
                metric_name="revenue",
                detection_method=DetectionMethod.MOVING_AVERAGE,
                parameters={"window_size": 24, "threshold": 2.0},
                sensitivity=0.9
            ),
            
            DetectionModel(
                model_id="user_engagement_iqr",
                metric_name="user_engagement",
                detection_method=DetectionMethod.IQR,
                parameters={"iqr_factor": 1.5},
                sensitivity=0.7
            ),
            
            # System Metrics Anomalies
            DetectionModel(
                model_id="cpu_usage_threshold",
                metric_name="cpu_usage",
                detection_method=DetectionMethod.CUSTOM_THRESHOLD,
                parameters={"threshold": 0.9, "direction": "above"},
                sensitivity=1.0
            ),
            
            DetectionModel(
                model_id="memory_usage_zscore",
                metric_name="memory_usage",
                detection_method=DetectionMethod.Z_SCORE,
                parameters={"threshold": 2.0},
                sensitivity=0.8
            )
        ]
        
        for model in default_models:
            self.detection_models[model.model_id] = model
            
        logger.info(f"Initialized {len(default_models)} default detection models")
        
    async def _detect_with_method(
        self,
        metric_name: str,
        values: List[float],
        timestamps: List[datetime],
        method: DetectionMethod
    ) -> List[AnomalyPoint]:
        """Detect anomalies using a specific method"""
        anomalies = []
        
        if method == DetectionMethod.Z_SCORE:
            anomalies = self._detect_zscore_anomalies(metric_name, values, timestamps)
        elif method == DetectionMethod.IQR:
            anomalies = self._detect_iqr_anomalies(metric_name, values, timestamps)
        elif method == DetectionMethod.ISOLATION_FOREST:
            anomalies = await self._detect_isolation_forest_anomalies(metric_name, values, timestamps)
        elif method == DetectionMethod.MOVING_AVERAGE:
            anomalies = self._detect_moving_average_anomalies(metric_name, values, timestamps)
        elif method == DetectionMethod.CUSTOM_THRESHOLD:
            anomalies = self._detect_threshold_anomalies(metric_name, values, timestamps)
            
        return anomalies
        
    def _detect_zscore_anomalies(
        self,
        metric_name: str,
        values: List[float],
        timestamps: List[datetime]
    ) -> List[AnomalyPoint]:
        """Detect anomalies using Z-score method"""
        if len(values) < 10:
            return []
            
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values)
        
        if std_val == 0:
            return []
            
        anomalies = []
        threshold = 2.5  # Default threshold
        
        # Get threshold from model if available
        for model in self.detection_models.values():
            if (model.metric_name == metric_name and 
                model.detection_method == DetectionMethod.Z_SCORE):
                threshold = model.parameters.get("threshold", 2.5)
                break
                
        for i, (value, timestamp) in enumerate(zip(values, timestamps)):
            z_score = abs(value - mean_val) / std_val
            
            if z_score > threshold:
                severity = self._calculate_severity(z_score, threshold)
                
                anomaly = AnomalyPoint(
                    timestamp=timestamp,
                    metric_name=metric_name,
                    value=value,
                    expected_value=mean_val,
                    deviation=value - mean_val,
                    anomaly_type=AnomalyType.STATISTICAL,
                    severity=severity,
                    detection_method=DetectionMethod.Z_SCORE,
                    confidence_score=min(z_score / (threshold * 2), 1.0),
                    description=f"Z-score anomaly: value {value:.2f} (z-score: {z_score:.2f})"
                )
                
                anomalies.append(anomaly)
                
        return anomalies
        
    def _detect_iqr_anomalies(
        self,
        metric_name: str,
        values: List[float],
        timestamps: List[datetime]
    ) -> List[AnomalyPoint]:
        """Detect anomalies using IQR method"""
        if len(values) < 10:
            return []
            
        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)
        iqr = q3 - q1
        
        iqr_factor = 1.5  # Default factor
        
        # Get factor from model if available
        for model in self.detection_models.values():
            if (model.metric_name == metric_name and 
                model.detection_method == DetectionMethod.IQR):
                iqr_factor = model.parameters.get("iqr_factor", 1.5)
                break
                
        lower_bound = q1 - iqr_factor * iqr
        upper_bound = q3 + iqr_factor * iqr
        
        anomalies = []
        
        for value, timestamp in zip(values, timestamps):
            if value < lower_bound or value > upper_bound:
                deviation = min(abs(value - lower_bound), abs(value - upper_bound))
                severity = self._calculate_severity_iqr(deviation, iqr)
                
                anomaly = AnomalyPoint(
                    timestamp=timestamp,
                    metric_name=metric_name,
                    value=value,
                    expected_value=(q1 + q3) / 2,
                    deviation=deviation,
                    anomaly_type=AnomalyType.STATISTICAL,
                    severity=severity,
                    detection_method=DetectionMethod.IQR,
                    confidence_score=min(deviation / (iqr * 2), 1.0),
                    description=f"IQR anomaly: value {value:.2f} outside bounds [{lower_bound:.2f}, {upper_bound:.2f}]"
                )
                
                anomalies.append(anomaly)
                
        return anomalies
        
    async def _detect_isolation_forest_anomalies(
        self,
        metric_name: str,
        values: List[float],
        timestamps: List[datetime]
    ) -> List[AnomalyPoint]:
        """Detect anomalies using Isolation Forest"""
        if len(values) < 50:  # Need more data for ML methods
            return []
            
        try:
            # Prepare data
            X = np.array(values).reshape(-1, 1)
            
            # Get or create Isolation Forest model
            if metric_name not in self.isolation_forests:
                contamination = 0.1  # Default contamination
                n_estimators = 100
                
                # Get parameters from model if available
                for model in self.detection_models.values():
                    if (model.metric_name == metric_name and 
                        model.detection_method == DetectionMethod.ISOLATION_FOREST):
                        contamination = model.parameters.get("contamination", 0.1)
                        n_estimators = model.parameters.get("n_estimators", 100)
                        break
                        
                self.isolation_forests[metric_name] = IsolationForest(
                    contamination=contamination,
                    n_estimators=n_estimators,
                    random_state=42
                )
                
            # Fit and predict
            model = self.isolation_forests[metric_name]
            model.fit(X)
            predictions = model.predict(X)
            scores = model.decision_function(X)
            
            anomalies = []
            
            for i, (prediction, score, value, timestamp) in enumerate(
                zip(predictions, scores, values, timestamps)
            ):
                if prediction == -1:  # Anomaly detected
                    severity = self._calculate_severity_isolation(score)
                    confidence = abs(score)
                    
                    anomaly = AnomalyPoint(
                        timestamp=timestamp,
                        metric_name=metric_name,
                        value=value,
                        expected_value=statistics.mean(values),
                        deviation=abs(value - statistics.mean(values)),
                        anomaly_type=AnomalyType.PATTERN,
                        severity=severity,
                        detection_method=DetectionMethod.ISOLATION_FOREST,
                        confidence_score=min(confidence, 1.0),
                        description=f"Isolation Forest anomaly: value {value:.2f} (score: {score:.3f})"
                    )
                    
                    anomalies.append(anomaly)
                    
            return anomalies
            
        except Exception as e:
            logger.error(f"Isolation Forest detection failed for {metric_name}: {e}")
            return []
            
    def _detect_moving_average_anomalies(
        self,
        metric_name: str,
        values: List[float],
        timestamps: List[datetime]
    ) -> List[AnomalyPoint]:
        """Detect anomalies using moving average"""
        window_size = 10  # Default window
        threshold = 2.0
        
        # Get parameters from model if available
        for model in self.detection_models.values():
            if (model.metric_name == metric_name and 
                model.detection_method == DetectionMethod.MOVING_AVERAGE):
                window_size = model.parameters.get("window_size", 10)
                threshold = model.parameters.get("threshold", 2.0)
                break
                
        if len(values) < window_size:
            return []
            
        anomalies = []
        
        for i in range(window_size, len(values)):
            window = values[i-window_size:i]
            moving_avg = statistics.mean(window)
            moving_std = statistics.stdev(window) if len(window) > 1 else 0
            
            if moving_std > 0:
                z_score = abs(values[i] - moving_avg) / moving_std
                
                if z_score > threshold:
                    severity = self._calculate_severity(z_score, threshold)
                    
                    anomaly = AnomalyPoint(
                        timestamp=timestamps[i],
                        metric_name=metric_name,
                        value=values[i],
                        expected_value=moving_avg,
                        deviation=values[i] - moving_avg,
                        anomaly_type=AnomalyType.TREND,
                        severity=severity,
                        detection_method=DetectionMethod.MOVING_AVERAGE,
                        confidence_score=min(z_score / (threshold * 2), 1.0),
                        description=f"Moving average anomaly: value {values[i]:.2f} vs MA {moving_avg:.2f}"
                    )
                    
                    anomalies.append(anomaly)
                    
        return anomalies
        
    def _detect_threshold_anomalies(
        self,
        metric_name: str,
        values: List[float],
        timestamps: List[datetime]
    ) -> List[AnomalyPoint]:
        """Detect anomalies using custom thresholds"""
        threshold = 0.0
        direction = "above"
        
        # Get parameters from model if available
        for model in self.detection_models.values():
            if (model.metric_name == metric_name and 
                model.detection_method == DetectionMethod.CUSTOM_THRESHOLD):
                threshold = model.parameters.get("threshold", 0.0)
                direction = model.parameters.get("direction", "above")
                break
                
        anomalies = []
        
        for value, timestamp in zip(values, timestamps):
            is_anomaly = False
            
            if direction == "above" and value > threshold:
                is_anomaly = True
            elif direction == "below" and value < threshold:
                is_anomaly = True
            elif direction == "outside" and (value < threshold or value > threshold):
                is_anomaly = True
                
            if is_anomaly:
                deviation = abs(value - threshold)
                severity = AnomalySeverity.HIGH if deviation > threshold * 0.5 else AnomalySeverity.MEDIUM
                
                anomaly = AnomalyPoint(
                    timestamp=timestamp,
                    metric_name=metric_name,
                    value=value,
                    expected_value=threshold,
                    deviation=deviation,
                    anomaly_type=AnomalyType.THRESHOLD,
                    severity=severity,
                    detection_method=DetectionMethod.CUSTOM_THRESHOLD,
                    confidence_score=1.0,
                    description=f"Threshold anomaly: value {value:.2f} {direction} threshold {threshold:.2f}"
                )
                
                anomalies.append(anomaly)
                
        return anomalies
        
    def _calculate_severity(self, z_score: float, threshold: float) -> AnomalySeverity:
        """Calculate anomaly severity based on Z-score"""
        if z_score > threshold * 2:
            return AnomalySeverity.CRITICAL
        elif z_score > threshold * 1.5:
            return AnomalySeverity.HIGH
        elif z_score > threshold:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW
            
    def _calculate_severity_iqr(self, deviation: float, iqr: float) -> AnomalySeverity:
        """Calculate anomaly severity based on IQR deviation"""
        if deviation > iqr * 3:
            return AnomalySeverity.CRITICAL
        elif deviation > iqr * 2:
            return AnomalySeverity.HIGH
        elif deviation > iqr:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW
            
    def _calculate_severity_isolation(self, score: float) -> AnomalySeverity:
        """Calculate anomaly severity based on isolation forest score"""
        abs_score = abs(score)
        if abs_score > 0.7:
            return AnomalySeverity.CRITICAL
        elif abs_score > 0.5:
            return AnomalySeverity.HIGH
        elif abs_score > 0.3:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW
            
    def _deduplicate_anomalies(self, anomalies: List[AnomalyPoint]) -> List[AnomalyPoint]:
        """Remove duplicate anomalies from different detection methods"""
        if not anomalies:
            return []
            
        # Group by timestamp and metric
        grouped = defaultdict(list)
        for anomaly in anomalies:
            key = (anomaly.timestamp, anomaly.metric_name)
            grouped[key].append(anomaly)
            
        # Keep the highest confidence anomaly for each group
        deduplicated = []
        for group in grouped.values():
            best_anomaly = max(group, key=lambda x: x.confidence_score)
            deduplicated.append(best_anomaly)
            
        return deduplicated
        
    def _detect_temporal_patterns(
        self,
        metric_name: str,
        anomalies: List[AnomalyPoint]
    ) -> List[AnomalyPattern]:
        """Detect temporal patterns in anomalies for a specific metric"""
        if len(anomalies) < 3:
            return []
            
        patterns = []
        
        # Sort by timestamp
        sorted_anomalies = sorted(anomalies, key=lambda x: x.timestamp)
        
        # Look for periodic patterns
        time_diffs = []
        for i in range(1, len(sorted_anomalies)):
            diff = (sorted_anomalies[i].timestamp - sorted_anomalies[i-1].timestamp).total_seconds()
            time_diffs.append(diff)
            
        if time_diffs:
            # Check for regular intervals
            avg_interval = statistics.mean(time_diffs)
            std_interval = statistics.stdev(time_diffs) if len(time_diffs) > 1 else 0
            
            # If intervals are relatively consistent, it's a pattern
            if std_interval < avg_interval * 0.3:  # Low variance
                pattern = AnomalyPattern(
                    pattern_id=f"temporal_{metric_name}_{int(time.time())}",
                    pattern_name=f"Periodic anomalies in {metric_name}",
                    anomaly_points=sorted_anomalies,
                    start_time=sorted_anomalies[0].timestamp,
                    end_time=sorted_anomalies[-1].timestamp,
                    frequency=3600 / avg_interval if avg_interval > 0 else 0,  # per hour
                    affected_metrics=[metric_name],
                    pattern_confidence=1.0 - (std_interval / avg_interval) if avg_interval > 0 else 0,
                    root_cause_candidates=[
                        "Periodic system load",
                        "Scheduled processes",
                        "External service patterns"
                    ]
                )
                patterns.append(pattern)
                
        return patterns
        
    def _detect_cross_metric_patterns(
        self,
        anomalies: List[AnomalyPoint]
    ) -> List[AnomalyPattern]:
        """Detect patterns across multiple metrics"""
        if len(anomalies) < 5:
            return []
            
        patterns = []
        
        # Group anomalies by time windows
        time_windows = defaultdict(list)
        window_size = timedelta(minutes=5)
        
        for anomaly in anomalies:
            window_start = anomaly.timestamp.replace(second=0, microsecond=0)
            window_start = window_start.replace(minute=(window_start.minute // 5) * 5)
            time_windows[window_start].append(anomaly)
            
        # Look for windows with multiple metrics affected
        for window_start, window_anomalies in time_windows.items():
            if len(window_anomalies) >= 3:  # Multiple anomalies in same window
                affected_metrics = list(set(a.metric_name for a in window_anomalies))
                
                if len(affected_metrics) >= 2:  # Multiple metrics affected
                    pattern = AnomalyPattern(
                        pattern_id=f"cross_metric_{int(window_start.timestamp())}",
                        pattern_name=f"Cross-metric anomalies at {window_start}",
                        anomaly_points=window_anomalies,
                        start_time=min(a.timestamp for a in window_anomalies),
                        end_time=max(a.timestamp for a in window_anomalies),
                        frequency=len(window_anomalies) / window_size.total_seconds() * 3600,
                        affected_metrics=affected_metrics,
                        pattern_confidence=len(affected_metrics) / 10.0,  # More metrics = higher confidence
                        root_cause_candidates=[
                            "System-wide issue",
                            "Infrastructure problem",
                            "External dependency failure",
                            "Configuration change"
                        ]
                    )
                    patterns.append(pattern)
                    
        return patterns
        
    async def _check_realtime_anomalies(
        self,
        metric_name: str,
        value: float,
        timestamp: datetime
    ) -> None:
        """Check for real-time anomalies as data comes in"""
        # Get recent data for comparison
        recent_data = list(self.metric_data[metric_name])[-50:]  # Last 50 points
        
        if len(recent_data) < 10:
            return
            
        recent_values = [point["value"] for point in recent_data[:-1]]  # Exclude current value
        
        # Quick Z-score check
        if recent_values:
            mean_val = statistics.mean(recent_values)
            std_val = statistics.stdev(recent_values) if len(recent_values) > 1 else 0
            
            if std_val > 0:
                z_score = abs(value - mean_val) / std_val
                
                if z_score > 3.0:  # High threshold for real-time alerts
                    anomaly = AnomalyPoint(
                        timestamp=timestamp,
                        metric_name=metric_name,
                        value=value,
                        expected_value=mean_val,
                        deviation=value - mean_val,
                        anomaly_type=AnomalyType.STATISTICAL,
                        severity=self._calculate_severity(z_score, 3.0),
                        detection_method=DetectionMethod.Z_SCORE,
                        confidence_score=min(z_score / 6.0, 1.0),
                        description=f"Real-time anomaly detected: {value:.2f} (z-score: {z_score:.2f})"
                    )
                    
                    # Store anomaly
                    self.detected_anomalies.append(anomaly)
                    
                    # Collect metrics
                    await self.metrics_collector.collect_metric(
                        MetricEntry(
                            name="anomaly_detected",
                            value=1,
                            metric_type=MetricType.COUNTER,
                            tags={
                                "metric_name": metric_name,
                                "severity": anomaly.severity.value,
                                "detection_method": anomaly.detection_method.value
                            },
                            priority=MetricPriority.HIGH
                        )
                    )
                    
                    # Trigger callbacks
                    for callback in self.anomaly_callbacks:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(anomaly)
                            else:
                                callback(anomaly)
                        except Exception as e:
                            logger.error(f"Anomaly callback failed: {e}")
                            
                    logger.warning(f"Real-time anomaly detected: {anomaly.description}")
                    
    async def _detection_loop(self) -> None:
        """Main detection loop for continuous anomaly monitoring"""
        while self.is_detecting:
            try:
                # Run detection on all metrics with sufficient data
                for metric_name in self.metric_data.keys():
                    if len(self.metric_data[metric_name]) >= 50:
                        anomalies = await self.detect_anomalies(metric_name)
                        
                        # Store new anomalies
                        for anomaly in anomalies:
                            if anomaly.confidence_score >= self.min_confidence:
                                self.detected_anomalies.append(anomaly)
                                
                # Detect patterns
                await self.detect_patterns()
                
                # Update models if needed
                await self._update_models()
                
                # Wait before next detection cycle
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Error in anomaly detection loop: {e}")
                await asyncio.sleep(600)  # Wait longer on error
                
    async def _update_models(self) -> None:
        """Update detection models with new data"""
        current_time = datetime.utcnow()
        
        for model in self.detection_models.values():
            if not model.enabled:
                continue
                
            # Check if model needs updating
            if (model.last_trained is None or 
                current_time - model.last_trained > model.update_frequency):
                
                try:
                    await self._retrain_model(model)
                    model.last_trained = current_time
                except Exception as e:
                    logger.error(f"Failed to update model {model.model_id}: {e}")
                    
    async def _retrain_model(self, model: DetectionModel) -> None:
        """Retrain a specific detection model"""
        metric_name = model.metric_name
        
        if metric_name not in self.metric_data:
            return
            
        data = list(self.metric_data[metric_name])
        if len(data) < model.min_samples:
            return
            
        values = [point["value"] for point in data]
        
        # Update model-specific parameters based on recent data
        if model.detection_method == DetectionMethod.Z_SCORE:
            # Update baseline statistics
            self.baselines[metric_name] = {
                "mean": statistics.mean(values),
                "std": statistics.stdev(values) if len(values) > 1 else 0
            }
            
        elif model.detection_method == DetectionMethod.ISOLATION_FOREST:
            # Retrain Isolation Forest
            X = np.array(values).reshape(-1, 1)
            
            if metric_name in self.isolation_forests:
                self.isolation_forests[metric_name].fit(X)
                
        logger.debug(f"Retrained model {model.model_id}")


# Global anomaly detection instance
anomaly_detection = AnomalyDetection()
