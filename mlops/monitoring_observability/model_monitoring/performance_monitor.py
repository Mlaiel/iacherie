"""
Model Performance Monitoring and Drift Detection
Comprehensive monitoring for model performance and data drift
"""

import warnings
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import json
import logging
from enum import Enum

# Optional dependencies
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    warnings.warn("numpy not available. Some monitoring features will be limited.")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    warnings.warn("pandas not available. Some monitoring features will be limited.")

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    warnings.warn("scipy not available. Statistical analysis will be limited.")

try:
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    warnings.warn("sklearn not available. Some metrics will be limited.")

# Define conditional types and mock implementations based on availability
if NUMPY_AVAILABLE:
    NDArray = np.ndarray
else:
    from typing import Any
    NDArray = Any  # Fallback when numpy not available
    # Create mock numpy for basic compatibility
    class MockNumpy:
        @staticmethod
        def histogram(*args, **kwargs):
            return [], []
        @staticmethod
        def concatenate(*args, **kwargs):
            return []
        @staticmethod
        def sum(*args, **kwargs):
            return 0
        @staticmethod
        def where(*args, **kwargs):
            return []
        @staticmethod
        def log(*args, **kwargs):
            return 0
        @staticmethod
        def unique(*args, **kwargs):
            return []
        @staticmethod
        def arange(*args, **kwargs):
            return []
    np = MockNumpy()

if PANDAS_AVAILABLE:
    from pandas import DataFrame
else:
    from typing import Any
    DataFrame = Any  # Fallback when pandas not available
    # Create mock pandas for basic compatibility
    class MockPandas:
        DataFrame = Any
        @staticmethod
        def DataFrame(*args, **kwargs):
            return {}
    pd = MockPandas()

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DriftType(Enum):
    """Types of drift detection"""
    DATA_DRIFT = "data_drift"
    CONCEPT_DRIFT = "concept_drift"
    PREDICTION_DRIFT = "prediction_drift"


@dataclass
class MonitoringMetric:
    """Monitoring metric configuration"""
    name: str
    description: str
    threshold: float
    comparison_type: str  # 'greater', 'less', 'absolute_change', 'relative_change'
    window_size: int = 100
    alert_severity: AlertSeverity = AlertSeverity.MEDIUM


@dataclass
class DriftAlert:
    """Drift detection alert"""
    alert_id: str
    drift_type: DriftType
    metric_name: str
    current_value: float
    baseline_value: float
    threshold: float
    severity: AlertSeverity
    timestamp: datetime
    description: str
    recommendations: List[str] = field(default_factory=list)


class DriftDetector(ABC):
    """Abstract base class for drift detectors"""
    
    @abstractmethod
    def detect_drift(self, baseline_data: NDArray, current_data: NDArray) -> Tuple[bool, float, Dict]:
        try:
            logger.info(f"Executing detect_drift")
            
            # Implementation for detect_drift
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"detect_drift completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"detect_drift failed: {e}")
            raise
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
class KolmogorovSmirnovDriftDetector(DriftDetector):
    """Kolmogorov-Smirnov test for drift detection"""
    
    def __init__(self, significance_level: float = 0.05):
        self.significance_level = significance_level
    
    def detect_drift(self, baseline_data: NDArray, current_data: NDArray) -> Tuple[bool, float, Dict]:
        """Detect drift using KS test"""
        try:
            ks_statistic, p_value = stats.ks_2samp(baseline_data, current_data)
            
            drift_detected = p_value < self.significance_level
            
            details = {
                "test": "kolmogorov_smirnov",
                "ks_statistic": ks_statistic,
                "p_value": p_value,
                "significance_level": self.significance_level,
                "baseline_samples": len(baseline_data),
                "current_samples": len(current_data)
            }
            
            return drift_detected, ks_statistic, details
            
        except Exception as e:
            logger.error(f"Error in KS drift detection: {str(e)}")
            return False, 0.0, {"error": str(e)}


class PSIDriftDetector(DriftDetector):
    """Population Stability Index (PSI) for drift detection"""
    
    def __init__(self, bins: int = 10, threshold: float = 0.1):
        self.bins = bins
        self.threshold = threshold
    
    def detect_drift(self, baseline_data: NDArray, current_data: NDArray) -> Tuple[bool, float, Dict]:
        """Detect drift using PSI"""
        try:
            # Create bins based on baseline data
            _, bin_edges = np.histogram(baseline_data, bins=self.bins)
            
            # Calculate distributions
            baseline_dist, _ = np.histogram(baseline_data, bins=bin_edges, density=True)
            current_dist, _ = np.histogram(current_data, bins=bin_edges, density=True)
            
            # Normalize to probabilities
            baseline_dist = baseline_dist / np.sum(baseline_dist)
            current_dist = current_dist / np.sum(current_dist)
            
            # Avoid division by zero
            baseline_dist = np.where(baseline_dist == 0, 1e-8, baseline_dist)
            current_dist = np.where(current_dist == 0, 1e-8, current_dist)
            
            # Calculate PSI
            psi = np.sum((current_dist - baseline_dist) * np.log(current_dist / baseline_dist))
            
            drift_detected = psi > self.threshold
            
            details = {
                "test": "population_stability_index",
                "psi_value": psi,
                "threshold": self.threshold,
                "bins": self.bins,
                "baseline_distribution": baseline_dist.tolist(),
                "current_distribution": current_dist.tolist()
            }
            
            return drift_detected, psi, details
            
        except Exception as e:
            logger.error(f"Error in PSI drift detection: {str(e)}")
            return False, 0.0, {"error": str(e)}


class JensenShannonDriftDetector(DriftDetector):
    """Jensen-Shannon divergence for drift detection"""
    
    def __init__(self, bins: int = 10, threshold: float = 0.1):
        self.bins = bins
        self.threshold = threshold
    
    def detect_drift(self, baseline_data: NDArray, current_data: NDArray) -> Tuple[bool, float, Dict]:
        """Detect drift using Jensen-Shannon divergence"""
        try:
            # Create bins
            all_data = np.concatenate([baseline_data, current_data])
            _, bin_edges = np.histogram(all_data, bins=self.bins)
            
            # Calculate distributions
            baseline_dist, _ = np.histogram(baseline_data, bins=bin_edges, density=True)
            current_dist, _ = np.histogram(current_data, bins=bin_edges, density=True)
            
            # Normalize
            baseline_dist = baseline_dist / np.sum(baseline_dist)
            current_dist = current_dist / np.sum(current_dist)
            
            # Avoid zeros
            baseline_dist = np.where(baseline_dist == 0, 1e-8, baseline_dist)
            current_dist = np.where(current_dist == 0, 1e-8, current_dist)
            
            # Calculate JS divergence
            m = 0.5 * (baseline_dist + current_dist)
            js_divergence = 0.5 * stats.entropy(baseline_dist, m) + 0.5 * stats.entropy(current_dist, m)
            
            drift_detected = js_divergence > self.threshold
            
            details = {
                "test": "jensen_shannon_divergence",
                "js_divergence": js_divergence,
                "threshold": self.threshold,
                "bins": self.bins
            }
            
            return drift_detected, js_divergence, details
            
        except Exception as e:
            logger.error(f"Error in JS drift detection: {str(e)}")
            return False, 0.0, {"error": str(e)}


class ModelPerformanceMonitor:
    """Monitor model performance metrics"""
    
    def __init__(self, model_name: str, model_version: str):
        self.model_name = model_name
        self.model_version = model_version
        self.metrics_history: List[Dict] = []
        self.baseline_metrics: Optional[Dict] = None
        self.monitoring_metrics: List[MonitoringMetric] = []
        
    def set_baseline_metrics(self, metrics: Dict[str, float]):
        """Set baseline performance metrics"""
        self.baseline_metrics = metrics.copy()
        self.baseline_metrics["timestamp"] = datetime.now()
        logger.info(f"Set baseline metrics for {self.model_name} v{self.model_version}: {metrics}")
    
    def add_monitoring_metric(self, metric: MonitoringMetric):
        """Add a metric to monitor"""
        self.monitoring_metrics.append(metric)
        logger.info(f"Added monitoring metric: {metric.name}")
    
    def record_performance(self, y_true: NDArray, y_pred: NDArray, y_pred_proba: Optional[NDArray] = None) -> Dict[str, float]:
        """Record model performance metrics"""
        try:
            metrics = {}
            
            # Calculate standard metrics
            metrics["accuracy"] = accuracy_score(y_true, y_pred)
            metrics["precision"] = precision_score(y_true, y_pred, average="weighted", zero_division=0)
            metrics["recall"] = recall_score(y_true, y_pred, average="weighted", zero_division=0)
            metrics["f1_score"] = f1_score(y_true, y_pred, average="weighted", zero_division=0)
            
            # Calculate AUC if probabilities are provided
            if y_pred_proba is not None:
                try:
                    if len(np.unique(y_true)) == 2:  # Binary classification
                        metrics["auc_roc"] = roc_auc_score(y_true, y_pred_proba[:, 1] if y_pred_proba.ndim > 1 else y_pred_proba)
                    else:  # Multi-class
                        metrics["auc_roc"] = roc_auc_score(y_true, y_pred_proba, multi_class="ovr", average="weighted")
                except Exception as e:
                    logger.warning(f"Could not calculate AUC: {str(e)}")
            
            # Add metadata
            metrics["timestamp"] = datetime.now()
            metrics["sample_size"] = len(y_true)
            
            # Store in history
            self.metrics_history.append(metrics)
            
            # Check for alerts
            alerts = self._check_performance_alerts(metrics)
            
            logger.info(f"Recorded performance metrics for {self.model_name}: {metrics}")
            
            if alerts:
                logger.warning(f"Performance alerts triggered: {len(alerts)} alerts")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error recording performance metrics: {str(e)}")
            raise
    
    def get_performance_trends(self, window_size: int = 10) -> Dict[str, Any]:
        """Get performance trends over time"""
        if len(self.metrics_history) < 2:
            return {"error": "Insufficient data for trend analysis"}
        
        recent_metrics = self.metrics_history[-window_size:]
        
        trends = {}
        metric_names = ["accuracy", "precision", "recall", "f1_score", "auc_roc"]
        
        for metric_name in metric_names:
            values = [m.get(metric_name) for m in recent_metrics if m.get(metric_name) is not None]
            
            if len(values) >= 2:
                # Calculate trend
                x = np.arange(len(values))
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
                
                trends[metric_name] = {
                    "current_value": values[-1],
                    "slope": slope,
                    "r_squared": r_value ** 2,
                    "p_value": p_value,
                    "trend_direction": "improving" if slope > 0 else "declining" if slope < 0 else "stable",
                    "values": values,
                    "timestamps": [m["timestamp"].isoformat() for m in recent_metrics[-len(values):]]
                }
        
        return trends
    
    def _check_performance_alerts(self, current_metrics: Dict[str, float]) -> List[DriftAlert]:
        """Check if current metrics trigger any alerts"""
        alerts = []
        
        if not self.baseline_metrics:
            return alerts
        
        for monitoring_metric in self.monitoring_metrics:
            metric_name = monitoring_metric.name
            
            if metric_name not in current_metrics or metric_name not in self.baseline_metrics:
                continue
            
            current_value = current_metrics[metric_name]
            baseline_value = self.baseline_metrics[metric_name]
            threshold = monitoring_metric.threshold
            
            alert_triggered = False
            description = ""
            
            if monitoring_metric.comparison_type == "greater":
                if current_value > threshold:
                    alert_triggered = True
                    description = f"{metric_name} ({current_value:.4f}) exceeds threshold ({threshold})"
            
            elif monitoring_metric.comparison_type == "less":
                if current_value < threshold:
                    alert_triggered = True
                    description = f"{metric_name} ({current_value:.4f}) below threshold ({threshold})"
            
            elif monitoring_metric.comparison_type == "absolute_change":
                change = abs(current_value - baseline_value)
                if change > threshold:
                    alert_triggered = True
                    description = f"{metric_name} absolute change ({change:.4f}) exceeds threshold ({threshold})"
            
            elif monitoring_metric.comparison_type == "relative_change":
                if baseline_value != 0:
                    relative_change = abs((current_value - baseline_value) / baseline_value)
                    if relative_change > threshold:
                        alert_triggered = True
                        description = f"{metric_name} relative change ({relative_change:.4f}) exceeds threshold ({threshold})"
            
            if alert_triggered:
                alert = DriftAlert(
                    alert_id=f"{self.model_name}_{metric_name}_{datetime.now().timestamp()}",
                    drift_type=DriftType.CONCEPT_DRIFT,
                    metric_name=metric_name,
                    current_value=current_value,
                    baseline_value=baseline_value,
                    threshold=threshold,
                    severity=monitoring_metric.alert_severity,
                    timestamp=datetime.now(),
                    description=description,
                    recommendations=[
                        "Investigate data quality issues",
                        "Check for changes in input distribution",
                        "Consider model retraining",
                        "Review feature engineering pipeline"
                    ]
                )
                alerts.append(alert)
        
        return alerts


class DataDriftMonitor:
    """Monitor data drift for model inputs"""
    
    def __init__(self, model_name: str, feature_names: List[str]):
        self.model_name = model_name
        self.feature_names = feature_names
        self.baseline_data: Optional[DataFrame] = None
        self.drift_detectors: Dict[str, DriftDetector] = {}
        self.drift_history: List[Dict] = []
        
        # Initialize default drift detectors
        self.drift_detectors["ks_test"] = KolmogorovSmirnovDriftDetector()
        self.drift_detectors["psi"] = PSIDriftDetector()
        self.drift_detectors["js_divergence"] = JensenShannonDriftDetector()
    
    def set_baseline_data(self, data: DataFrame):
        """Set baseline data for drift detection"""
        self.baseline_data = data[self.feature_names].copy()
        logger.info(f"Set baseline data for {self.model_name}: {self.baseline_data.shape}")
    
    def add_drift_detector(self, name: str, detector: DriftDetector):
        """Add a custom drift detector"""
        self.drift_detectors[name] = detector
        logger.info(f"Added drift detector: {name}")
    
    def detect_drift(self, current_data: DataFrame) -> Dict[str, Any]:
        """Detect drift in current data compared to baseline"""
        if self.baseline_data is None:
            raise ValueError("Baseline data not set. Call set_baseline_data() first.")
        
        current_data_subset = current_data[self.feature_names]
        drift_results = {
            "timestamp": datetime.now(),
            "overall_drift_detected": False,
            "feature_drift": {},
            "detector_results": {}
        }
        
        # Check drift for each feature
        for feature in self.feature_names:
            baseline_feature = self.baseline_data[feature].dropna().values
            current_feature = current_data_subset[feature].dropna().values
            
            if len(baseline_feature) == 0 or len(current_feature) == 0:
                continue
            
            feature_drift_results = {}
            feature_drift_detected = False
            
            # Run all drift detectors for this feature
            for detector_name, detector in self.drift_detectors.items():
                try:
                    drift_detected, drift_score, details = detector.detect_drift(baseline_feature, current_feature)
                    
                    feature_drift_results[detector_name] = {
                        "drift_detected": drift_detected,
                        "drift_score": drift_score,
                        "details": details
                    }
                    
                    if drift_detected:
                        feature_drift_detected = True
                        
                except Exception as e:
                    logger.error(f"Error in drift detection for {feature} with {detector_name}: {str(e)}")
                    feature_drift_results[detector_name] = {"error": str(e)}
            
            drift_results["feature_drift"][feature] = {
                "drift_detected": feature_drift_detected,
                "detector_results": feature_drift_results
            }
            
            if feature_drift_detected:
                drift_results["overall_drift_detected"] = True
        
        # Store results
        self.drift_history.append(drift_results)
        
        # Generate alerts if drift detected
        if drift_results["overall_drift_detected"]:
            alerts = self._generate_drift_alerts(drift_results)
            drift_results["alerts"] = alerts
        
        logger.info(f"Drift detection completed for {self.model_name}. Overall drift: {drift_results['overall_drift_detected']}")
        
        return drift_results
    
    def get_drift_summary(self, days_back: int = 7) -> Dict[str, Any]:
        """Get drift summary for the past N days"""
        cutoff_time = datetime.now() - timedelta(days=days_back)
        recent_results = [r for r in self.drift_history if r["timestamp"] > cutoff_time]
        
        if not recent_results:
            return {"error": "No drift detection results in the specified period"}
        
        summary = {
            "period_days": days_back,
            "total_checks": len(recent_results),
            "drift_detected_count": sum(1 for r in recent_results if r["overall_drift_detected"]),
            "feature_drift_frequency": {},
            "drift_trend": "stable"
        }
        
        # Calculate drift frequency by feature
        for feature in self.feature_names:
            drift_count = sum(1 for r in recent_results 
                            if r["feature_drift"].get(feature, {}).get("drift_detected", False))
            summary["feature_drift_frequency"][feature] = drift_count / len(recent_results)
        
        # Determine trend
        if len(recent_results) >= 2:
            recent_drift_rate = summary["drift_detected_count"] / len(recent_results)
            if recent_drift_rate > 0.5:
                summary["drift_trend"] = "increasing"
            elif recent_drift_rate < 0.1:
                summary["drift_trend"] = "stable"
            else:
                summary["drift_trend"] = "moderate"
        
        return summary
    
    def _generate_drift_alerts(self, drift_results: Dict) -> List[DriftAlert]:
        """Generate alerts for detected drift"""
        alerts = []
        
        for feature, feature_results in drift_results["feature_drift"].items():
            if feature_results["drift_detected"]:
                # Find the strongest drift signal
                max_drift_score = 0
                best_detector = None
                
                for detector_name, detector_results in feature_results["detector_results"].items():
                    if detector_results.get("drift_detected", False):
                        drift_score = detector_results.get("drift_score", 0)
                        if drift_score > max_drift_score:
                            max_drift_score = drift_score
                            best_detector = detector_name
                
                if best_detector:
                    severity = AlertSeverity.HIGH if max_drift_score > 0.5 else AlertSeverity.MEDIUM
                    
                    alert = DriftAlert(
                        alert_id=f"{self.model_name}_{feature}_drift_{datetime.now().timestamp()}",
                        drift_type=DriftType.DATA_DRIFT,
                        metric_name=feature,
                        current_value=max_drift_score,
                        baseline_value=0.0,
                        threshold=0.1,  # Default threshold
                        severity=severity,
                        timestamp=datetime.now(),
                        description=f"Data drift detected in feature '{feature}' using {best_detector} (score: {max_drift_score:.4f})",
                        recommendations=[
                            f"Investigate changes in feature '{feature}' distribution",
                            "Check data collection and preprocessing pipeline",
                            "Consider retraining model with recent data",
                            "Review feature engineering for this variable"
                        ]
                    )
                    alerts.append(alert)
        
        return alerts


class ComprehensiveModelMonitor:
    """Comprehensive monitoring combining performance and drift detection"""
    
    def __init__(self, model_name: str, model_version: str, feature_names: List[str]):
        self.model_name = model_name
        self.model_version = model_version
        self.performance_monitor = ModelPerformanceMonitor(model_name, model_version)
        self.data_drift_monitor = DataDriftMonitor(model_name, feature_names)
        self.alerts: List[DriftAlert] = []
        
    def setup_monitoring(
        self,
        baseline_data: DataFrame,
        baseline_metrics: Dict[str, float],
        monitoring_metrics: List[MonitoringMetric]
    ):
        """Setup comprehensive monitoring"""
        # Setup data drift monitoring
        self.data_drift_monitor.set_baseline_data(baseline_data)
        
        # Setup performance monitoring
        self.performance_monitor.set_baseline_metrics(baseline_metrics)
        for metric in monitoring_metrics:
            self.performance_monitor.add_monitoring_metric(metric)
        
        logger.info(f"Comprehensive monitoring setup completed for {self.model_name}")
    
    def monitor_prediction_batch(
        self,
        input_data: DataFrame,
        y_true: NDArray,
        y_pred: NDArray,
        y_pred_proba: Optional[NDArray] = None
    ) -> Dict[str, Any]:
        """Monitor a batch of predictions"""
        monitoring_results = {
            "timestamp": datetime.now(),
            "model_name": self.model_name,
            "model_version": self.model_version,
            "batch_size": len(input_data)
        }
        
        # Performance monitoring
        try:
            performance_metrics = self.performance_monitor.record_performance(y_true, y_pred, y_pred_proba)
            monitoring_results["performance_metrics"] = performance_metrics
        except Exception as e:
            logger.error(f"Error in performance monitoring: {str(e)}")
            monitoring_results["performance_error"] = str(e)
        
        # Data drift monitoring
        try:
            drift_results = self.data_drift_monitor.detect_drift(input_data)
            monitoring_results["drift_detection"] = drift_results
        except Exception as e:
            logger.error(f"Error in drift monitoring: {str(e)}")
            monitoring_results["drift_error"] = str(e)
        
        # Collect all alerts
        all_alerts = []
        if "drift_detection" in monitoring_results and "alerts" in monitoring_results["drift_detection"]:
            all_alerts.extend(monitoring_results["drift_detection"]["alerts"])
        
        monitoring_results["alerts"] = all_alerts
        self.alerts.extend(all_alerts)
        
        # Generate recommendations
        monitoring_results["recommendations"] = self._generate_monitoring_recommendations(monitoring_results)
        
        return monitoring_results
    
    def get_monitoring_dashboard_data(self) -> Dict[str, Any]:
        """Get data for monitoring dashboard"""
        dashboard_data = {
            "model_info": {
                "name": self.model_name,
                "version": self.model_version,
                "last_updated": datetime.now()
            },
            "performance_trends": self.performance_monitor.get_performance_trends(),
            "drift_summary": self.data_drift_monitor.get_drift_summary(),
            "recent_alerts": [alert.__dict__ for alert in self.alerts[-10:]],  # Last 10 alerts
            "alert_counts": {
                severity.value: len([a for a in self.alerts if a.severity == severity])
                for severity in AlertSeverity
            }
        }
        
        return dashboard_data
    
    def _generate_monitoring_recommendations(self, monitoring_results: Dict) -> List[str]:
        """Generate monitoring recommendations based on results"""
        recommendations = []
        
        # Check for performance degradation
        performance_metrics = monitoring_results.get("performance_metrics", {})
        if self.performance_monitor.baseline_metrics:
            for metric_name in ["accuracy", "f1_score"]:
                if metric_name in performance_metrics and metric_name in self.performance_monitor.baseline_metrics:
                    current = performance_metrics[metric_name]
                    baseline = self.performance_monitor.baseline_metrics[metric_name]
                    degradation = (baseline - current) / baseline
                    
                    if degradation > 0.05:  # 5% degradation
                        recommendations.append(f"Performance degradation detected in {metric_name} ({degradation:.2%}). Consider model retraining.")
        
        # Check for drift
        drift_results = monitoring_results.get("drift_detection", {})
        if drift_results.get("overall_drift_detected", False):
            drifted_features = [
                feature for feature, results in drift_results.get("feature_drift", {}).items()
                if results.get("drift_detected", False)
            ]
            recommendations.append(f"Data drift detected in features: {', '.join(drifted_features)}. Investigate data pipeline.")
        
        # Check alert patterns
        recent_alerts = [a for a in self.alerts if (datetime.now() - a.timestamp).days <= 1]
        if len(recent_alerts) > 5:
            recommendations.append("Multiple alerts in the past 24 hours. Consider immediate investigation.")
        
        if not recommendations:
            recommendations.append("Model monitoring shows stable performance. Continue regular monitoring.")
        
        return recommendations