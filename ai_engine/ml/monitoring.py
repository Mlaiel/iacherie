"""Monitoring Module - Model monitoring, performance tracking, and drift detection
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive monitoring capabilities for ML models including
performance tracking, data drift detection, model degradation monitoring.
"""
import logging
import time
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from collections import deque
import json
import threading

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics that can be monitored"""    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    PREDICTION_CONFIDENCE = "prediction_confidence"

class AlertSeverity(Enum):
    """Severity levels for monitoring alerts"""    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class DriftType(Enum):
    """Types of data drift"""    DATA_DRIFT = "data_drift"
    CONCEPT_DRIFT = "concept_drift"
    FEATURE_DRIFT = "feature_drift"
    PREDICTION_DRIFT = "prediction_drift"

@dataclass
class MetricPoint:
    """Single metric measurement"""    metric_type: MetricType
    value: float
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class Alert:
    """Monitoring alert"""    alert_id: str
    severity: AlertSeverity
    message: str
    metric_type: MetricType
    threshold_value: float
    actual_value: float
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class MonitoringConfig:
    """Configuration for model monitoring"""    model_name: str
    collection_interval: int = 60  # seconds
    retention_days: int = 30
    enable_drift_detection: bool = True
    enable_performance_tracking: bool = True
    alert_thresholds: Dict[MetricType, Tuple[float, float]] = None  # (min, max)

class ModelMonitor:
    """Main model monitoring system"""    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.metrics_storage: Dict[MetricType, deque] = {}
        self.alerts: List[Alert] = []
        self.is_monitoring = False
        self.monitor_thread = None
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        self._initialize_storage()
        self.logger.info("ModelMonitor initialized successfully")
    
    def _initialize_storage(self):
        """Initialize metrics storage"""        try:
            # Initialize storage for each metric type
            for metric_type in MetricType:
                self.metrics_storage[metric_type] = deque(maxlen=10000)  # Keep last 10k points
            
            # Set default thresholds if not provided
            if self.config.alert_thresholds is None:
                self.config.alert_thresholds = {
                    MetricType.ACCURACY: (0.8, 1.0),
                    MetricType.LATENCY: (0.0, 1000.0),  # milliseconds
                    MetricType.ERROR_RATE: (0.0, 0.05),  # 5%
                    MetricType.MEMORY_USAGE: (0.0, 0.9),  # 90%
                    MetricType.CPU_USAGE: (0.0, 0.9)  # 90%
                }
            
        except Exception as e:
            self.logger.error(f"Storage initialization failed: {e}")
    
    def start_monitoring(self):
        """Start continuous monitoring"""        try:
            if self.is_monitoring:
                self.logger.warning("Monitoring is already running")
                return
            
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitoring_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
            self.logger.info(f"Model monitoring started for {self.config.model_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
            self.is_monitoring = False
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""        try:
            self.is_monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5.0)
            
            self.logger.info("Model monitoring stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop monitoring: {e}")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""        while self.is_monitoring:
            try:
                # Collect current metrics
                current_metrics = self._collect_metrics()
                
                # Store metrics
                for metric_type, value in current_metrics.items():
                    if value is not None:
                        self.record_metric(metric_type, value)
                
                # Check for alerts
                self._check_alert_conditions()
                
                # Sleep until next collection
                time.sleep(self.config.collection_interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
    
    def _collect_metrics(self) -> Dict[MetricType, float]:
        """Collect current model metrics"""        # Simulate metric collection - in production this would interface with actual systems
        metrics = {}
        
        try:
            # System metrics
            metrics[MetricType.CPU_USAGE] = np.random.uniform(0.2, 0.8)
            metrics[MetricType.MEMORY_USAGE] = np.random.uniform(0.3, 0.7)
            metrics[MetricType.LATENCY] = np.random.uniform(50, 200)
            metrics[MetricType.THROUGHPUT] = np.random.uniform(100, 500)
            
            # Model performance metrics (would come from actual predictions)
            metrics[MetricType.ACCURACY] = np.random.uniform(0.85, 0.95)
            metrics[MetricType.ERROR_RATE] = np.random.uniform(0.01, 0.05)
            metrics[MetricType.PREDICTION_CONFIDENCE] = np.random.uniform(0.7, 0.95)
            
        except Exception as e:
            self.logger.error(f"Metric collection failed: {e}")
        
        return metrics
    
    def record_metric(self, metric_type: MetricType, value: float, metadata: Dict[str, Any] = None):
        """Record a metric measurement"""        try:
            if metadata is None:
                metadata = {}
            
            metric_point = MetricPoint(
                metric_type=metric_type,
                value=value,
                timestamp=datetime.utcnow(),
                metadata=metadata
            )
            
            self.metrics_storage[metric_type].append(metric_point)
            self.logger.debug(f"Recorded metric: {metric_type.value} = {value}")
            
        except Exception as e:
            self.logger.error(f"Failed to record metric: {e}")
    
    def _check_alert_conditions(self):
        """Check if any alert conditions are met"""        try:
            for metric_type, threshold in self.config.alert_thresholds.items():
                if metric_type not in self.metrics_storage:
                    continue
                
                metrics_queue = self.metrics_storage[metric_type]
                if not metrics_queue:
                    continue
                
                # Get latest metric
                latest_metric = metrics_queue[-1]
                min_threshold, max_threshold = threshold
                
                # Check threshold violations
                if latest_metric.value < min_threshold:
                    self._trigger_alert(
                        metric_type, latest_metric.value, min_threshold,
                        AlertSeverity.WARNING,
                        f"{metric_type.value} below minimum threshold"
                    )
                elif latest_metric.value > max_threshold:
                    self._trigger_alert(
                        metric_type, latest_metric.value, max_threshold,
                        AlertSeverity.ERROR,
                        f"{metric_type.value} above maximum threshold"
                    )
                
        except Exception as e:
            self.logger.error(f"Alert condition check failed: {e}")
    
    def _trigger_alert(self, metric_type: MetricType, actual_value: float, 
                      threshold_value: float, severity: AlertSeverity, message: str):
        """Trigger a monitoring alert"""        try:
            alert = Alert(
                alert_id=f"{int(time.time())}_{metric_type.value}",
                severity=severity,
                message=message,
                metric_type=metric_type,
                threshold_value=threshold_value,
                actual_value=actual_value,
                timestamp=datetime.utcnow(),
                metadata={"model_name": self.config.model_name}
            )
            
            self.alerts.append(alert)
            
            # Trigger alert callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as cb_error:
                    self.logger.error(f"Alert callback failed: {cb_error}")
            
            self.logger.warning(f"Alert triggered: {message}")
            
        except Exception as e:
            self.logger.error(f"Failed to trigger alert: {e}")
    
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Add callback function for alerts"""        self.alert_callbacks.append(callback)
    
    def get_metrics(self, metric_type: MetricType, hours: int = 24) -> List[MetricPoint]:
        """Get historical metrics for a specific type"""        try:
            if metric_type not in self.metrics_storage:
                return []
            
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            metrics_queue = self.metrics_storage[metric_type]
            
            return [
                metric for metric in metrics_queue 
                if metric.timestamp >= cutoff_time
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get metrics: {e}")
            return []
    
    def get_recent_alerts(self, hours: int = 24) -> List[Alert]:
        """Get recent alerts"""        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            return [
                alert for alert in self.alerts 
                if alert.timestamp >= cutoff_time
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get alerts: {e}")
            return []

class PerformanceTracker:
    """Track model performance over time"""    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.logger = logging.getLogger(self.__class__.__name__)
        self.performance_history: List[Dict[str, Any]] = []
        self.baseline_metrics: Dict[str, float] = {}
        self.logger.info("PerformanceTracker initialized successfully")
    
    def set_baseline(self, metrics: Dict[str, float]):
        """Set baseline performance metrics"""        try:
            self.baseline_metrics = metrics.copy()
            self.logger.info(f"Baseline set for model {self.model_name}: {metrics}")
            
        except Exception as e:
            self.logger.error(f"Failed to set baseline: {e}")
    
    def record_performance(self, metrics: Dict[str, float], metadata: Dict[str, Any] = None):
        """Record performance metrics"""        try:
            if metadata is None:
                metadata = {}
            
            performance_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": metrics,
                "metadata": metadata
            }
            
            self.performance_history.append(performance_record)
            
            # Calculate performance degradation
            degradation = self._calculate_degradation(metrics)
            if degradation:
                self.logger.warning(f"Performance degradation detected: {degradation}")
            
        except Exception as e:
            self.logger.error(f"Failed to record performance: {e}")
    
    def _calculate_degradation(self, current_metrics: Dict[str, float]) -> Optional[Dict[str, float]]:
        """Calculate performance degradation from baseline"""        if not self.baseline_metrics:
            return None
        
        degradation = {}
        for metric_name, current_value in current_metrics.items():
            if metric_name in self.baseline_metrics:
                baseline_value = self.baseline_metrics[metric_name]
                if baseline_value > 0:
                    degradation_pct = ((baseline_value - current_value) / baseline_value) * 100
                    if abs(degradation_pct) > 5:  # More than 5% change
                        degradation[metric_name] = degradation_pct
        
        return degradation if degradation else None
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the specified time period"""        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            cutoff_str = cutoff_time.isoformat()
            
            recent_records = [
                record for record in self.performance_history
                if record["timestamp"] >= cutoff_str
            ]
            
            if not recent_records:
                return {"message": "No performance data available"}
            
            # Calculate aggregated metrics
            all_metrics = {}
            for record in recent_records:
                for metric_name, value in record["metrics"].items():
                    if metric_name not in all_metrics:
                        all_metrics[metric_name] = []
                    all_metrics[metric_name].append(value)
            
            summary = {}
            for metric_name, values in all_metrics.items():
                summary[metric_name] = {
                    "avg": np.mean(values),
                    "min": np.min(values),
                    "max": np.max(values),
                    "std": np.std(values),
                    "count": len(values)
                }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get performance summary: {e}")
            return {"error": str(e)}

class DriftDetector:
    """Detect data and concept drift in models"""    
    def __init__(self, model_name: str, sensitivity: float = 0.1):
        self.model_name = model_name
        self.sensitivity = sensitivity
        self.logger = logging.getLogger(self.__class__.__name__)
        self.reference_data: Optional[np.ndarray] = None
        self.reference_predictions: Optional[np.ndarray] = None
        self.drift_history: List[Dict[str, Any]] = []
        self.logger.info("DriftDetector initialized successfully")
    
    def set_reference_data(self, data: np.ndarray, predictions: Optional[np.ndarray] = None):
        """Set reference data for drift detection"""        try:
            self.reference_data = data.copy()
            if predictions is not None:
                self.reference_predictions = predictions.copy()
            
            self.logger.info(f"Reference data set for drift detection: {data.shape}")
            
        except Exception as e:
            self.logger.error(f"Failed to set reference data: {e}")
    
    def detect_data_drift(self, current_data: np.ndarray) -> Dict[str, Any]:
        """Detect data drift using statistical methods"""        try:
            if self.reference_data is None:
                return {"error": "No reference data set"}
            
            # Simple statistical drift detection
            drift_scores = {}
            
            # Compare feature distributions
            if current_data.shape[1] == self.reference_data.shape[1]:
                for feature_idx in range(current_data.shape[1]):
                    ref_feature = self.reference_data[:, feature_idx]
                    cur_feature = current_data[:, feature_idx]
                    
                    # Calculate statistical distance (simplified KS test)
                    drift_score = self._calculate_drift_score(ref_feature, cur_feature)
                    drift_scores[f"feature_{feature_idx}"] = drift_score
            
            # Determine if drift is significant
            max_drift = max(drift_scores.values()) if drift_scores else 0
            is_drift_detected = max_drift > self.sensitivity
            
            drift_result = {
                "drift_detected": is_drift_detected,
                "drift_type": DriftType.DATA_DRIFT,
                "max_drift_score": max_drift,
                "feature_drift_scores": drift_scores,
                "timestamp": datetime.utcnow().isoformat(),
                "threshold": self.sensitivity
            }
            
            # Record drift event
            self.drift_history.append(drift_result)
            
            if is_drift_detected:
                self.logger.warning(f"Data drift detected with score: {max_drift}")
            
            return drift_result
            
        except Exception as e:
            self.logger.error(f"Data drift detection failed: {e}")
            return {"error": str(e)}
    
    def detect_prediction_drift(self, current_predictions: np.ndarray) -> Dict[str, Any]:
        """Detect prediction drift"""        try:
            if self.reference_predictions is None:
                return {"error": "No reference predictions set"}
            
            # Calculate prediction distribution drift
            drift_score = self._calculate_drift_score(
                self.reference_predictions, current_predictions
            )
            
            is_drift_detected = drift_score > self.sensitivity
            
            drift_result = {
                "drift_detected": is_drift_detected,
                "drift_type": DriftType.PREDICTION_DRIFT,
                "drift_score": drift_score,
                "timestamp": datetime.utcnow().isoformat(),
                "threshold": self.sensitivity
            }
            
            # Record drift event
            self.drift_history.append(drift_result)
            
            if is_drift_detected:
                self.logger.warning(f"Prediction drift detected with score: {drift_score}")
            
            return drift_result
            
        except Exception as e:
            self.logger.error(f"Prediction drift detection failed: {e}")
            return {"error": str(e)}
    
    def _calculate_drift_score(self, reference: np.ndarray, current: np.ndarray) -> float:
        """Calculate drift score between two datasets"""        try:
            # Simple statistical comparison (in production, use proper statistical tests)
            ref_mean = np.mean(reference)
            ref_std = np.std(reference)
            
            cur_mean = np.mean(current)
            cur_std = np.std(current)
            
            # Normalized difference in means
            mean_diff = abs(cur_mean - ref_mean) / (ref_std + 1e-8)
            
            # Normalized difference in standard deviations
            std_diff = abs(cur_std - ref_std) / (ref_std + 1e-8)
            
            # Combined drift score
            drift_score = (mean_diff + std_diff) / 2
            
            return float(drift_score)
            
        except Exception as e:
            self.logger.error(f"Drift score calculation failed: {e}")
            return 0.0
    
    def get_drift_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of drift events"""        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            cutoff_str = cutoff_time.isoformat()
            
            recent_drift = [
                event for event in self.drift_history
                if event.get("timestamp", "") >= cutoff_str
            ]
            
            # Count drift events by type
            drift_counts = {}
            for event in recent_drift:
                drift_type = event.get("drift_type", "unknown")
                if hasattr(drift_type, 'value'):
                    drift_type = drift_type.value
                drift_counts[drift_type] = drift_counts.get(drift_type, 0) + 1
            
            summary = {
                "total_drift_events": len(recent_drift),
                "drift_by_type": drift_counts,
                "time_period_hours": hours,
                "recent_events": recent_drift[-5:] if recent_drift else []  # Last 5 events
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get drift summary: {e}")
            return {"error": str(e)}

# Export classes for external use
__all__ = [
    'MetricType',
    'AlertSeverity',
    'DriftType',
    'MetricPoint',
    'Alert',
    'MonitoringConfig',
    'ModelMonitor',
    'PerformanceTracker',
    'DriftDetector'
]

logger.info("Monitoring module loaded successfully")
