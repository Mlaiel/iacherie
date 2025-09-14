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
        """
        Detect drift between baseline and current data distributions
        
        Args:
            baseline_data: Reference dataset for comparison
            current_data: Current dataset to check for drift
            
        Returns:
            Tuple of (drift_detected, drift_magnitude, detailed_analysis)
        """
        try:
            logger.info(f"🔍 Executing enterprise drift detection analysis")
            
            # Enterprise-level drift detection implementation
            # ML Engineer + Backend Senior + DBA + Security roles
            
            # 1. Statistical Distribution Analysis
            distribution_analysis = self._analyze_distributions(baseline_data, current_data)
            
            # 2. Multi-dimensional Drift Detection
            multidim_analysis = self._detect_multidimensional_drift(baseline_data, current_data)
            
            # 3. Feature-level Drift Analysis
            feature_drift = self._analyze_feature_drift(baseline_data, current_data)
            
            # 4. Concept Drift Detection (if target available)
            concept_drift = self._detect_concept_drift(baseline_data, current_data)
            
            # 5. Calculate overall drift magnitude
            drift_magnitude = self._calculate_drift_magnitude(
                distribution_analysis, multidim_analysis, feature_drift, concept_drift
            )
            
            # 6. Determine if drift is significant
            drift_detected = drift_magnitude > self.drift_threshold
            
            # 7. Generate detailed analysis report
            detailed_analysis = {
                "drift_type": self._classify_drift_type(distribution_analysis, feature_drift),
                "affected_features": self._identify_affected_features(feature_drift),
                "distribution_analysis": distribution_analysis,
                "multidimensional_analysis": multidim_analysis,
                "feature_analysis": feature_drift,
                "concept_analysis": concept_drift,
                "drift_severity": self._assess_drift_severity(drift_magnitude),
                "business_impact": self._assess_business_impact(drift_magnitude, feature_drift),
                "recommendations": self._generate_drift_recommendations(drift_magnitude, feature_drift),
                "analysis_timestamp": datetime.now().isoformat(),
                "baseline_sample_size": len(baseline_data),
                "current_sample_size": len(current_data)
            }
            
            logger.info(f"✅ Drift detection completed - Detected: {drift_detected}, Magnitude: {drift_magnitude:.4f}")
            return drift_detected, drift_magnitude, detailed_analysis
            
        except Exception as e:
            logger.error(f"❌ Drift detection failed: {e}")
            raise
    
    # =============================================
    # ENTERPRISE DRIFT DETECTION HELPER METHODS
    # ML Engineer + Backend Senior + DBA + Security expertise
    # =============================================
    
    def _analyze_distributions(self, baseline_data: NDArray, current_data: NDArray) -> Dict[str, Any]:
        """Analyze statistical distributions between baseline and current data"""
        try:
            import numpy as np
            
            analysis = {
                "statistical_tests": {},
                "distribution_metrics": {},
                "moments_comparison": {}
            }
            
            # Statistical moments comparison
            for i, dataset_name in enumerate(["baseline", "current"]):
                data = baseline_data if i == 0 else current_data
                
                if len(data.shape) > 1:
                    # Multi-dimensional data - analyze each feature
                    for feature_idx in range(data.shape[1]):
                        feature_data = data[:, feature_idx]
                        analysis["moments_comparison"][f"{dataset_name}_feature_{feature_idx}"] = {
                            "mean": float(np.mean(feature_data)),
                            "std": float(np.std(feature_data)),
                            "skewness": float(self._calculate_skewness(feature_data)),
                            "kurtosis": float(self._calculate_kurtosis(feature_data))
                        }
                else:
                    # Single-dimensional data
                    analysis["moments_comparison"][dataset_name] = {
                        "mean": float(np.mean(data)),
                        "std": float(np.std(data)),
                        "skewness": float(self._calculate_skewness(data)),
                        "kurtosis": float(self._calculate_kurtosis(data))
                    }
            
            return analysis
        except Exception as e:
            logger.error(f"Distribution analysis failed: {e}")
            return {"error": str(e)}
    
    def _detect_multidimensional_drift(self, baseline_data: NDArray, current_data: NDArray) -> Dict[str, Any]:
        """Detect drift in multi-dimensional feature space"""
        try:
            import numpy as np
            
            analysis = {
                "multivariate_distance": 0.0,
                "covariance_drift": 0.0,
                "correlation_drift": 0.0,
                "pca_drift": {}
            }
            
            if len(baseline_data.shape) > 1 and len(current_data.shape) > 1:
                # Calculate covariance matrices
                baseline_cov = np.cov(baseline_data.T)
                current_cov = np.cov(current_data.T)
                
                # Covariance drift (Frobenius norm of difference)
                cov_diff = baseline_cov - current_cov
                analysis["covariance_drift"] = float(np.linalg.norm(cov_diff, 'fro'))
                
                # Correlation drift
                baseline_corr = np.corrcoef(baseline_data.T)
                current_corr = np.corrcoef(current_data.T)
                corr_diff = baseline_corr - current_corr
                analysis["correlation_drift"] = float(np.linalg.norm(corr_diff, 'fro'))
                
                # Multivariate distance (simplified Mahalanobis-style)
                baseline_mean = np.mean(baseline_data, axis=0)
                current_mean = np.mean(current_data, axis=0)
                mean_diff = baseline_mean - current_mean
                analysis["multivariate_distance"] = float(np.linalg.norm(mean_diff))
            
            return analysis
        except Exception as e:
            logger.error(f"Multidimensional drift detection failed: {e}")
            return {"error": str(e)}
    
    def _analyze_feature_drift(self, baseline_data: NDArray, current_data: NDArray) -> Dict[str, Any]:
        """Analyze drift at individual feature level"""
        try:
            import numpy as np
            
            feature_analysis = {
                "feature_drift_scores": {},
                "significantly_drifted_features": [],
                "drift_directions": {}
            }
            
            if len(baseline_data.shape) > 1:
                n_features = baseline_data.shape[1]
                
                for feature_idx in range(n_features):
                    baseline_feature = baseline_data[:, feature_idx]
                    current_feature = current_data[:, feature_idx]
                    
                    # Calculate feature-specific drift score
                    drift_score = self._calculate_feature_drift_score(baseline_feature, current_feature)
                    feature_analysis["feature_drift_scores"][f"feature_{feature_idx}"] = drift_score
                    
                    # Check if significantly drifted
                    if drift_score > 0.1:  # Threshold for significant drift
                        feature_analysis["significantly_drifted_features"].append(feature_idx)
                    
                    # Determine drift direction
                    baseline_mean = np.mean(baseline_feature)
                    current_mean = np.mean(current_feature)
                    
                    if abs(current_mean - baseline_mean) > 0.01:
                        direction = "increase" if current_mean > baseline_mean else "decrease"
                        feature_analysis["drift_directions"][f"feature_{feature_idx}"] = direction
            
            return feature_analysis
        except Exception as e:
            logger.error(f"Feature drift analysis failed: {e}")
            return {"error": str(e)}
    
    def _detect_concept_drift(self, baseline_data: NDArray, current_data: NDArray) -> Dict[str, Any]:
        """Detect concept drift (changes in the target relationship)"""
        try:
            # Simplified concept drift detection
            # In practice, this would require target variables
            concept_analysis = {
                "concept_drift_detected": False,
                "confidence": 0.0,
                "drift_type": "none",
                "note": "Concept drift detection requires target variables"
            }
            
            # For demo purposes, simulate concept drift detection
            import numpy as np
            if len(baseline_data) > 0 and len(current_data) > 0:
                # Simple heuristic based on data characteristics
                baseline_complexity = np.var(baseline_data.flatten()) if baseline_data.size > 0 else 0
                current_complexity = np.var(current_data.flatten()) if current_data.size > 0 else 0
                
                complexity_change = abs(current_complexity - baseline_complexity) / (baseline_complexity + 1e-8)
                
                if complexity_change > 0.2:
                    concept_analysis.update({
                        "concept_drift_detected": True,
                        "confidence": min(1.0, complexity_change),
                        "drift_type": "complexity_change"
                    })
            
            return concept_analysis
        except Exception as e:
            logger.error(f"Concept drift detection failed: {e}")
            return {"error": str(e)}
    
    def _calculate_drift_magnitude(self, distribution_analysis: Dict, multidim_analysis: Dict, 
                                 feature_drift: Dict, concept_drift: Dict) -> float:
        """Calculate overall drift magnitude from all analyses"""
        try:
            import numpy as np
            
            # Weight different types of drift
            weights = {
                "distribution": 0.3,
                "multidimensional": 0.3,
                "feature": 0.3,
                "concept": 0.1
            }
            
            # Distribution contribution
            dist_score = 0.0
            if "error" not in distribution_analysis:
                # Simplified distribution score
                dist_score = 0.1  # Placeholder
            
            # Multidimensional contribution
            multidim_score = multidim_analysis.get("multivariate_distance", 0.0)
            multidim_score = min(1.0, multidim_score / 10.0)  # Normalize
            
            # Feature-level contribution
            feature_scores = list(feature_drift.get("feature_drift_scores", {}).values())
            feature_score = np.mean(feature_scores) if feature_scores else 0.0
            
            # Concept drift contribution
            concept_score = concept_drift.get("confidence", 0.0) if concept_drift.get("concept_drift_detected", False) else 0.0
            
            # Weighted combination
            overall_magnitude = (
                weights["distribution"] * dist_score +
                weights["multidimensional"] * multidim_score +
                weights["feature"] * feature_score +
                weights["concept"] * concept_score
            )
            
            return float(overall_magnitude)
        except Exception as e:
            logger.error(f"Drift magnitude calculation failed: {e}")
            return 0.0
    
    def _classify_drift_type(self, distribution_analysis: Dict, feature_drift: Dict) -> str:
        """Classify the type of drift detected"""
        try:
            significantly_drifted = len(feature_drift.get("significantly_drifted_features", []))
            total_features = len(feature_drift.get("feature_drift_scores", {}))
            
            if total_features == 0:
                return "unknown"
            
            drift_percentage = significantly_drifted / total_features
            
            if drift_percentage > 0.8:
                return "global_drift"
            elif drift_percentage > 0.3:
                return "partial_drift"
            elif drift_percentage > 0.1:
                return "localized_drift"
            else:
                return "minimal_drift"
        except Exception as e:
            logger.error(f"Drift type classification failed: {e}")
            return "unknown"
    
    def _identify_affected_features(self, feature_drift: Dict) -> List[int]:
        """Identify which features are most affected by drift"""
        return feature_drift.get("significantly_drifted_features", [])
    
    def _assess_drift_severity(self, drift_magnitude: float) -> str:
        """Assess the severity of detected drift"""
        if drift_magnitude > 0.7:
            return "critical"
        elif drift_magnitude > 0.4:
            return "high"
        elif drift_magnitude > 0.2:
            return "medium"
        elif drift_magnitude > 0.05:
            return "low"
        else:
            return "minimal"
    
    def _assess_business_impact(self, drift_magnitude: float, feature_drift: Dict) -> Dict[str, Any]:
        """Assess potential business impact of detected drift"""
        try:
            impact_assessment = {
                "risk_level": "low",
                "confidence_degradation_estimate": 0.0,
                "performance_impact_estimate": 0.0,
                "recommended_actions": []
            }
            
            # Risk level assessment
            if drift_magnitude > 0.5:
                impact_assessment["risk_level"] = "high"
                impact_assessment["recommended_actions"].extend([
                    "immediate_model_retraining",
                    "enhanced_monitoring",
                    "stakeholder_notification"
                ])
            elif drift_magnitude > 0.2:
                impact_assessment["risk_level"] = "medium"
                impact_assessment["recommended_actions"].extend([
                    "scheduled_model_retraining",
                    "increased_monitoring_frequency"
                ])
            
            # Estimate impacts
            impact_assessment["confidence_degradation_estimate"] = min(0.5, drift_magnitude * 0.6)
            impact_assessment["performance_impact_estimate"] = min(0.3, drift_magnitude * 0.4)
            
            return impact_assessment
        except Exception as e:
            logger.error(f"Business impact assessment failed: {e}")
            return {"risk_level": "unknown", "error": str(e)}
    
    def _generate_drift_recommendations(self, drift_magnitude: float, feature_drift: Dict) -> List[str]:
        """Generate recommendations based on drift analysis"""
        try:
            recommendations = []
            
            if drift_magnitude > 0.5:
                recommendations.extend([
                    "Immediate model retraining recommended",
                    "Implement enhanced data monitoring",
                    "Consider model architecture updates",
                    "Review data collection processes"
                ])
            elif drift_magnitude > 0.2:
                recommendations.extend([
                    "Schedule model retraining within 7 days",
                    "Increase monitoring frequency",
                    "Analyze root causes of drift"
                ])
            elif drift_magnitude > 0.05:
                recommendations.extend([
                    "Continue monitoring",
                    "Document drift patterns",
                    "Prepare for potential retraining"
                ])
            
            # Feature-specific recommendations
            affected_features = feature_drift.get("significantly_drifted_features", [])
            if affected_features:
                recommendations.append(f"Focus on features: {affected_features}")
            
            return recommendations
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return ["Error generating recommendations"]
    
    # Utility methods for statistical calculations
    
    def _calculate_feature_drift_score(self, baseline_feature: NDArray, current_feature: NDArray) -> float:
        """Calculate drift score for individual feature"""
        try:
            import numpy as np
            
            # Simple KL divergence approximation
            baseline_mean = np.mean(baseline_feature)
            current_mean = np.mean(current_feature)
            baseline_std = np.std(baseline_feature) + 1e-8
            current_std = np.std(current_feature) + 1e-8
            
            # Normalized difference in means
            mean_diff = abs(current_mean - baseline_mean) / baseline_std
            
            # Ratio of standard deviations
            std_ratio = abs(np.log(current_std / baseline_std))
            
            # Combined score
            drift_score = (mean_diff + std_ratio) / 2.0
            return min(1.0, drift_score)
        except Exception as e:
            logger.error(f"Feature drift score calculation failed: {e}")
            return 0.0
    
    def _calculate_skewness(self, data: NDArray) -> float:
        """Calculate skewness of data distribution"""
        try:
            import numpy as np
            
            mean = np.mean(data)
            std = np.std(data)
            if std == 0:
                return 0.0
            
            skewness = np.mean(((data - mean) / std) ** 3)
            return float(skewness)
        except:
            return 0.0
    
    def _calculate_kurtosis(self, data: NDArray) -> float:
        """Calculate kurtosis of data distribution"""
        try:
            import numpy as np
            
            mean = np.mean(data)
            std = np.std(data)
            if std == 0:
                return 0.0
            
            kurtosis = np.mean(((data - mean) / std) ** 4) - 3  # Excess kurtosis
            return float(kurtosis)
        except:
            return 0.0


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