"""
Advanced Data Drift Detection for MLOps
Lead Dev IA implementation with enterprise-grade drift detection algorithms
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import warnings
from abc import ABC, abstractmethod

# Statistical libraries for advanced drift detection
try:
    from scipy import stats
    from scipy.spatial.distance import jensenshannon
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    warnings.warn("scipy not available. Some drift detection methods will be limited.")

try:
    from sklearn.metrics import accuracy_score, classification_report
    from sklearn.ensemble import IsolationForest
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    warnings.warn("scikit-learn not available. Some drift detection methods will be limited.")

logger = logging.getLogger(__name__)


class DriftDetectionMethod(Enum):
    """Available drift detection methods"""
    KOLMOGOROV_SMIRNOV = "kolmogorov_smirnov"
    JENSEN_SHANNON_DIVERGENCE = "jensen_shannon_divergence"
    POPULATION_STABILITY_INDEX = "population_stability_index"
    CHI_SQUARE = "chi_square"
    WASSERSTEIN_DISTANCE = "wasserstein_distance"
    HELLINGER_DISTANCE = "hellinger_distance"
    MAXIMUM_MEAN_DISCREPANCY = "maximum_mean_discrepancy"
    DOMAIN_CLASSIFIER = "domain_classifier"


class DriftSeverity(Enum):
    """Severity levels for detected drift"""
    NO_DRIFT = "no_drift"
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class FeatureType(Enum):
    """Types of features for appropriate drift detection"""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    BOOLEAN = "boolean"
    TEXT = "text"
    TEMPORAL = "temporal"


@dataclass
class DriftDetectionResult:
    """Results of drift detection analysis"""
    feature_name: str
    drift_detected: bool
    drift_score: float
    p_value: Optional[float]
    severity: DriftSeverity
    method_used: DriftDetectionMethod
    threshold: float
    reference_period: str
    current_period: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DriftAlert:
    """Alert for detected drift"""
    alert_id: str
    feature_name: str
    model_id: str
    drift_result: DriftDetectionResult
    alert_level: str
    message: str
    recommended_actions: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


class DataDriftDetector:
    """
    Enterprise-grade data drift detection system
    Lead Dev IA implementation with advanced statistical methods
    """
    
    def __init__(
        self,
        model_id: str,
        default_method: DriftDetectionMethod = DriftDetectionMethod.KOLMOGOROV_SMIRNOV,
        sensitivity_threshold: float = 0.05,
        enable_alerting: bool = True,
        alert_webhook_url: Optional[str] = None
    ):
        """Initialize drift detector
        
        Args:
            model_id: Unique identifier for the model
            default_method: Default drift detection method
            sensitivity_threshold: Threshold for drift detection (p-value)
            enable_alerting: Whether to enable automatic alerting
            alert_webhook_url: Webhook URL for sending alerts
        """
        self.model_id = model_id
        self.default_method = default_method
        self.sensitivity_threshold = sensitivity_threshold
        self.enable_alerting = enable_alerting
        self.alert_webhook_url = alert_webhook_url
        
        # Storage for reference distributions
        self.reference_distributions: Dict[str, Dict] = {}
        self.feature_types: Dict[str, FeatureType] = {}
        self.drift_history: List[DriftDetectionResult] = []
        self.alerts_history: List[DriftAlert] = []
        
        # Configuration for different detection methods
        self.method_config = {
            DriftDetectionMethod.KOLMOGOROV_SMIRNOV: {"threshold": 0.05},
            DriftDetectionMethod.JENSEN_SHANNON_DIVERGENCE: {"threshold": 0.1},
            DriftDetectionMethod.POPULATION_STABILITY_INDEX: {"threshold": 0.25},
            DriftDetectionMethod.CHI_SQUARE: {"threshold": 0.05},
            DriftDetectionMethod.WASSERSTEIN_DISTANCE: {"threshold": 0.1},
            DriftDetectionMethod.HELLINGER_DISTANCE: {"threshold": 0.1},
            DriftDetectionMethod.DOMAIN_CLASSIFIER: {"threshold": 0.7}
        }
        
        logger.info(f"Initialized DataDriftDetector for model {model_id}")

    def set_reference_distribution(
        self,
        reference_data: pd.DataFrame,
        feature_types: Optional[Dict[str, FeatureType]] = None
    ) -> None:
        """Set reference distribution for drift detection
        
        Args:
            reference_data: Reference dataset (training data)
            feature_types: Optional mapping of feature names to types
        """
        if not isinstance(reference_data, pd.DataFrame):
            raise ValueError("Reference data must be a pandas DataFrame")
            
        logger.info(f"Setting reference distribution with {len(reference_data)} samples")
        
        # Auto-detect feature types if not provided
        if feature_types is None:
            feature_types = self._auto_detect_feature_types(reference_data)
        
        self.feature_types = feature_types
        
        # Calculate reference statistics for each feature
        for column in reference_data.columns:
            feature_type = self.feature_types.get(column, FeatureType.NUMERICAL)
            
            self.reference_distributions[column] = {
                'type': feature_type,
                'timestamp': datetime.now(),
                'sample_size': len(reference_data),
                'statistics': self._calculate_feature_statistics(
                    reference_data[column], feature_type
                )
            }
        
        logger.info(f"Reference distribution set for {len(self.reference_distributions)} features")

    def detect_drift(
        self,
        current_data: pd.DataFrame,
        methods: Optional[List[DriftDetectionMethod]] = None,
        features: Optional[List[str]] = None
    ) -> Dict[str, DriftDetectionResult]:
        """Detect drift in current data compared to reference
        
        Args:
            current_data: Current dataset to check for drift
            methods: List of detection methods to use
            features: Specific features to check (default: all)
            
        Returns:
            Dictionary mapping feature names to drift detection results
        """
        if not self.reference_distributions:
            raise ValueError("Reference distribution not set. Call set_reference_distribution first.")
        
        if methods is None:
            methods = [self.default_method]
        
        if features is None:
            features = list(self.reference_distributions.keys())
        
        logger.info(f"Detecting drift for {len(features)} features using {len(methods)} methods")
        
        results = {}
        
        for feature in features:
            if feature not in current_data.columns:
                logger.warning(f"Feature {feature} not found in current data")
                continue
                
            if feature not in self.reference_distributions:
                logger.warning(f"No reference distribution for feature {feature}")
                continue
            
            # Use the best method for this feature type
            feature_type = self.reference_distributions[feature]['type']
            best_method = self._select_best_method(feature_type, methods)
            
            drift_result = self._detect_feature_drift(
                feature_name=feature,
                reference_stats=self.reference_distributions[feature],
                current_data=current_data[feature],
                method=best_method
            )
            
            results[feature] = drift_result
            self.drift_history.append(drift_result)
            
            # Generate alert if drift detected
            if drift_result.drift_detected and self.enable_alerting:
                alert = self._generate_drift_alert(drift_result)
                self.alerts_history.append(alert)
                self._send_alert(alert)
        
        logger.info(f"Drift detection completed. Found drift in {sum(1 for r in results.values() if r.drift_detected)} features")
        return results

    def _auto_detect_feature_types(self, data: pd.DataFrame) -> Dict[str, FeatureType]:
        """Automatically detect feature types"""
        feature_types = {}
        
        for column in data.columns:
            if data[column].dtype == 'bool':
                feature_types[column] = FeatureType.BOOLEAN
            elif pd.api.types.is_numeric_dtype(data[column]):
                feature_types[column] = FeatureType.NUMERICAL
            elif pd.api.types.is_datetime64_any_dtype(data[column]):
                feature_types[column] = FeatureType.TEMPORAL
            elif data[column].dtype == 'object':
                # Check if it's text or categorical
                unique_ratio = data[column].nunique() / len(data[column])
                if unique_ratio > 0.5:  # High cardinality suggests text
                    feature_types[column] = FeatureType.TEXT
                else:
                    feature_types[column] = FeatureType.CATEGORICAL
            else:
                feature_types[column] = FeatureType.CATEGORICAL
                
        return feature_types

    def _calculate_feature_statistics(self, series: pd.Series, feature_type: FeatureType) -> Dict:
        """Calculate appropriate statistics for feature type"""
        stats = {}
        
        if feature_type == FeatureType.NUMERICAL:
            stats.update({
                'mean': float(series.mean()),
                'std': float(series.std()),
                'min': float(series.min()),
                'max': float(series.max()),
                'quantiles': {
                    '25': float(series.quantile(0.25)),
                    '50': float(series.quantile(0.5)),
                    '75': float(series.quantile(0.75))
                },
                'histogram': self._create_histogram(series)
            })
        elif feature_type in [FeatureType.CATEGORICAL, FeatureType.BOOLEAN]:
            value_counts = series.value_counts(normalize=True)
            stats.update({
                'distribution': value_counts.to_dict(),
                'unique_values': series.nunique(),
                'most_frequent': series.mode().iloc[0] if len(series.mode()) > 0 else None
            })
        elif feature_type == FeatureType.TEMPORAL:
            stats.update({
                'min_date': series.min(),
                'max_date': series.max(),
                'frequency_pattern': self._analyze_temporal_pattern(series)
            })
        
        return stats

    def _create_histogram(self, series: pd.Series, bins: int = 50) -> Dict:
        """Create histogram for numerical features"""
        if not SCIPY_AVAILABLE:
            return {}
            
        hist, bin_edges = np.histogram(series.dropna(), bins=bins)
        return {
            'counts': hist.tolist(),
            'bin_edges': bin_edges.tolist()
        }

    def _analyze_temporal_pattern(self, series: pd.Series) -> Dict:
        """Analyze temporal patterns in datetime features"""
        if series.empty:
            return {}
            
        return {
            'daily_pattern': series.dt.hour.value_counts().to_dict(),
            'weekly_pattern': series.dt.dayofweek.value_counts().to_dict(),
            'monthly_pattern': series.dt.month.value_counts().to_dict()
        }

    def _select_best_method(self, feature_type: FeatureType, available_methods: List[DriftDetectionMethod]) -> DriftDetectionMethod:
        """Select the best drift detection method for feature type"""
        # Method recommendations by feature type
        recommendations = {
            FeatureType.NUMERICAL: [
                DriftDetectionMethod.KOLMOGOROV_SMIRNOV,
                DriftDetectionMethod.WASSERSTEIN_DISTANCE,
                DriftDetectionMethod.JENSEN_SHANNON_DIVERGENCE
            ],
            FeatureType.CATEGORICAL: [
                DriftDetectionMethod.CHI_SQUARE,
                DriftDetectionMethod.JENSEN_SHANNON_DIVERGENCE,
                DriftDetectionMethod.POPULATION_STABILITY_INDEX
            ],
            FeatureType.BOOLEAN: [
                DriftDetectionMethod.CHI_SQUARE,
                DriftDetectionMethod.JENSEN_SHANNON_DIVERGENCE
            ],
            FeatureType.TEXT: [
                DriftDetectionMethod.DOMAIN_CLASSIFIER,
                DriftDetectionMethod.JENSEN_SHANNON_DIVERGENCE
            ],
            FeatureType.TEMPORAL: [
                DriftDetectionMethod.KOLMOGOROV_SMIRNOV,
                DriftDetectionMethod.CHI_SQUARE
            ]
        }
        
        recommended = recommendations.get(feature_type, [self.default_method])
        
        # Return first available recommended method
        for method in recommended:
            if method in available_methods:
                return method
                
        return available_methods[0] if available_methods else self.default_method

    def _detect_feature_drift(
        self,
        feature_name: str,
        reference_stats: Dict,
        current_data: pd.Series,
        method: DriftDetectionMethod
    ) -> DriftDetectionResult:
        """Detect drift for a single feature"""
        
        current_stats = self._calculate_feature_statistics(
            current_data, reference_stats['type']
        )
        
        # Apply the specified detection method
        if method == DriftDetectionMethod.KOLMOGOROV_SMIRNOV:
            drift_score, p_value = self._kolmogorov_smirnov_test(
                reference_stats['statistics'], current_stats
            )
        elif method == DriftDetectionMethod.JENSEN_SHANNON_DIVERGENCE:
            drift_score, p_value = self._jensen_shannon_divergence(
                reference_stats['statistics'], current_stats
            )
        elif method == DriftDetectionMethod.POPULATION_STABILITY_INDEX:
            drift_score, p_value = self._population_stability_index(
                reference_stats['statistics'], current_stats
            )
        elif method == DriftDetectionMethod.CHI_SQUARE:
            drift_score, p_value = self._chi_square_test(
                reference_stats['statistics'], current_stats
            )
        elif method == DriftDetectionMethod.WASSERSTEIN_DISTANCE:
            drift_score, p_value = self._wasserstein_distance(
                reference_stats['statistics'], current_stats
            )
        else:
            # Fallback to simple statistical comparison
            drift_score, p_value = self._simple_drift_test(
                reference_stats['statistics'], current_stats
            )
        
        # Determine if drift is detected
        threshold = self.method_config[method]['threshold']
        drift_detected = drift_score > threshold or (p_value is not None and p_value < self.sensitivity_threshold)
        
        # Calculate severity
        severity = self._calculate_drift_severity(drift_score, p_value)
        
        return DriftDetectionResult(
            feature_name=feature_name,
            drift_detected=drift_detected,
            drift_score=drift_score,
            p_value=p_value,
            severity=severity,
            method_used=method,
            threshold=threshold,
            reference_period=reference_stats['timestamp'].isoformat(),
            current_period=datetime.now().isoformat(),
            metadata={
                'reference_sample_size': reference_stats['sample_size'],
                'current_sample_size': len(current_data),
                'feature_type': reference_stats['type'].value
            }
        )

    def _kolmogorov_smirnov_test(self, ref_stats: Dict, current_stats: Dict) -> Tuple[float, Optional[float]]:
        """Kolmogorov-Smirnov test for numerical features"""
        if not SCIPY_AVAILABLE:
            return 0.0, None
            
        try:
            # Reconstruct distributions from histograms
            ref_hist = ref_stats.get('histogram', {})
            curr_hist = current_stats.get('histogram', {})
            
            if not ref_hist or not curr_hist:
                return 0.0, None
                
            # Use means and stds for normal approximation if histograms unavailable
            ref_mean = ref_stats.get('mean', 0)
            ref_std = ref_stats.get('std', 1)
            curr_mean = current_stats.get('mean', 0)
            curr_std = current_stats.get('std', 1)
            
            # Simple KS statistic approximation
            ks_statistic = abs(ref_mean - curr_mean) / max(ref_std, curr_std, 0.01)
            p_value = 2 * (1 - stats.norm.cdf(ks_statistic))
            
            return ks_statistic, p_value
            
        except Exception as e:
            logger.warning(f"KS test failed: {e}")
            return 0.0, None

    def _jensen_shannon_divergence(self, ref_stats: Dict, current_stats: Dict) -> Tuple[float, Optional[float]]:
        """Jensen-Shannon divergence for categorical features"""
        if not SCIPY_AVAILABLE:
            return 0.0, None
            
        try:
            ref_dist = ref_stats.get('distribution', {})
            curr_dist = current_stats.get('distribution', {})
            
            if not ref_dist or not curr_dist:
                return 0.0, None
            
            # Align distributions
            all_values = set(ref_dist.keys()) | set(curr_dist.keys())
            ref_probs = np.array([ref_dist.get(v, 0) for v in all_values])
            curr_probs = np.array([curr_dist.get(v, 0) for v in all_values])
            
            # Add small epsilon to avoid log(0)
            epsilon = 1e-10
            ref_probs = ref_probs + epsilon
            curr_probs = curr_probs + epsilon
            
            # Normalize
            ref_probs = ref_probs / ref_probs.sum()
            curr_probs = curr_probs / curr_probs.sum()
            
            js_divergence = jensenshannon(ref_probs, curr_probs)
            
            return float(js_divergence), None
            
        except Exception as e:
            logger.warning(f"JS divergence calculation failed: {e}")
            return 0.0, None

    def _population_stability_index(self, ref_stats: Dict, current_stats: Dict) -> Tuple[float, Optional[float]]:
        """Population Stability Index calculation"""
        try:
            ref_dist = ref_stats.get('distribution', {})
            curr_dist = current_stats.get('distribution', {})
            
            if not ref_dist or not curr_dist:
                return 0.0, None
            
            psi = 0.0
            for category in ref_dist.keys():
                ref_pct = ref_dist[category]
                curr_pct = curr_dist.get(category, 0.001)  # Small value for missing categories
                
                if ref_pct > 0 and curr_pct > 0:
                    psi += (curr_pct - ref_pct) * np.log(curr_pct / ref_pct)
            
            return float(abs(psi)), None
            
        except Exception as e:
            logger.warning(f"PSI calculation failed: {e}")
            return 0.0, None

    def _chi_square_test(self, ref_stats: Dict, current_stats: Dict) -> Tuple[float, Optional[float]]:
        """Chi-square test for categorical features"""
        if not SCIPY_AVAILABLE:
            return 0.0, None
            
        try:
            ref_dist = ref_stats.get('distribution', {})
            curr_dist = current_stats.get('distribution', {})
            
            if not ref_dist or not curr_dist:
                return 0.0, None
                
            all_categories = set(ref_dist.keys()) | set(curr_dist.keys())
            
            observed = []
            expected = []
            
            for category in all_categories:
                curr_count = curr_dist.get(category, 0)
                ref_count = ref_dist.get(category, 0)
                
                observed.append(curr_count * 1000)  # Scale for chi-square
                expected.append(ref_count * 1000)
            
            # Add small value to avoid zero expected frequencies
            expected = [max(e, 0.1) for e in expected]
            
            chi2_stat, p_value = stats.chisquare(observed, expected)
            
            return float(chi2_stat), float(p_value)
            
        except Exception as e:
            logger.warning(f"Chi-square test failed: {e}")
            return 0.0, None

    def _wasserstein_distance(self, ref_stats: Dict, current_stats: Dict) -> Tuple[float, Optional[float]]:
        """Wasserstein distance for numerical features"""
        if not SCIPY_AVAILABLE:
            return 0.0, None
            
        try:
            ref_mean = ref_stats.get('mean', 0)
            curr_mean = current_stats.get('mean', 0)
            ref_std = ref_stats.get('std', 1)
            curr_std = current_stats.get('std', 1)
            
            # Simplified Wasserstein distance for normal distributions
            wasserstein_dist = abs(ref_mean - curr_mean) + abs(ref_std - curr_std)
            
            return float(wasserstein_dist), None
            
        except Exception as e:
            logger.warning(f"Wasserstein distance calculation failed: {e}")
            return 0.0, None

    def _simple_drift_test(self, ref_stats: Dict, current_stats: Dict) -> Tuple[float, Optional[float]]:
        """Simple drift test fallback"""
        try:
            # Compare means for numerical features
            if 'mean' in ref_stats and 'mean' in current_stats:
                ref_mean = ref_stats['mean']
                curr_mean = current_stats['mean']
                ref_std = ref_stats.get('std', 1)
                
                drift_score = abs(ref_mean - curr_mean) / max(ref_std, 0.01)
                return float(drift_score), None
            
            # Compare distributions for categorical features
            elif 'distribution' in ref_stats and 'distribution' in current_stats:
                ref_dist = ref_stats['distribution']
                curr_dist = current_stats['distribution']
                
                # Simple distribution difference
                total_diff = 0.0
                all_keys = set(ref_dist.keys()) | set(curr_dist.keys())
                
                for key in all_keys:
                    ref_val = ref_dist.get(key, 0)
                    curr_val = curr_dist.get(key, 0)
                    total_diff += abs(ref_val - curr_val)
                
                return float(total_diff), None
            
            return 0.0, None
            
        except Exception as e:
            logger.warning(f"Simple drift test failed: {e}")
            return 0.0, None

    def _calculate_drift_severity(self, drift_score: float, p_value: Optional[float]) -> DriftSeverity:
        """Calculate severity of detected drift"""
        if p_value is not None:
            if p_value >= 0.05:
                return DriftSeverity.NO_DRIFT
            elif p_value >= 0.01:
                return DriftSeverity.MINOR
            elif p_value >= 0.001:
                return DriftSeverity.MODERATE
            elif p_value >= 0.0001:
                return DriftSeverity.SEVERE
            else:
                return DriftSeverity.CRITICAL
        else:
            # Use drift score for severity
            if drift_score < 0.1:
                return DriftSeverity.NO_DRIFT
            elif drift_score < 0.3:
                return DriftSeverity.MINOR
            elif drift_score < 0.6:
                return DriftSeverity.MODERATE
            elif drift_score < 1.0:
                return DriftSeverity.SEVERE
            else:
                return DriftSeverity.CRITICAL

    def _generate_drift_alert(self, drift_result: DriftDetectionResult) -> DriftAlert:
        """Generate alert for detected drift"""
        alert_id = f"drift_alert_{self.model_id}_{drift_result.feature_name}_{int(datetime.now().timestamp())}"
        
        severity_actions = {
            DriftSeverity.MINOR: [
                "Monitor feature distribution trends",
                "Schedule data quality review"
            ],
            DriftSeverity.MODERATE: [
                "Review data collection process",
                "Consider feature transformation",
                "Evaluate model performance impact"
            ],
            DriftSeverity.SEVERE: [
                "Immediate investigation required",
                "Consider model retraining",
                "Review data pipeline for issues"
            ],
            DriftSeverity.CRITICAL: [
                "Stop model serving if possible",
                "Emergency investigation required",
                "Immediate retraining needed",
                "Review entire data pipeline"
            ]
        }
        
        recommended_actions = severity_actions.get(drift_result.severity, [])
        
        message = (
            f"Data drift detected in feature '{drift_result.feature_name}' "
            f"for model {self.model_id}. "
            f"Drift score: {drift_result.drift_score:.4f}, "
            f"Severity: {drift_result.severity.value}"
        )
        
        return DriftAlert(
            alert_id=alert_id,
            feature_name=drift_result.feature_name,
            model_id=self.model_id,
            drift_result=drift_result,
            alert_level=drift_result.severity.value,
            message=message,
            recommended_actions=recommended_actions
        )

    def _send_alert(self, alert: DriftAlert) -> None:
        """Send drift alert to configured channels"""
        try:
            logger.warning(f"DRIFT ALERT: {alert.message}")
            
            # Here you would integrate with your alerting system
            # E.g., Slack, email, webhook, etc.
            if self.alert_webhook_url:
                # Implementation for webhook notification
                pass
                
        except Exception as e:
            logger.error(f"Failed to send drift alert: {e}")

    def get_drift_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get summary of drift detection results"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_results = [r for r in self.drift_history if r.timestamp > cutoff_date]
        
        if not recent_results:
            return {
                'period_days': days,
                'total_checks': 0,
                'drift_detected': 0,
                'features_with_drift': [],
                'average_drift_score': 0.0,
                'most_severe_drift': None
            }
        
        drift_detected_count = sum(1 for r in recent_results if r.drift_detected)
        features_with_drift = list(set(r.feature_name for r in recent_results if r.drift_detected))
        avg_drift_score = np.mean([r.drift_score for r in recent_results])
        
        # Find most severe drift
        most_severe = max(recent_results, key=lambda r: r.drift_score) if recent_results else None
        
        return {
            'period_days': days,
            'total_checks': len(recent_results),
            'drift_detected': drift_detected_count,
            'drift_rate': drift_detected_count / len(recent_results),
            'features_with_drift': features_with_drift,
            'average_drift_score': float(avg_drift_score),
            'most_severe_drift': {
                'feature': most_severe.feature_name,
                'score': most_severe.drift_score,
                'severity': most_severe.severity.value,
                'method': most_severe.method_used.value
            } if most_severe else None,
            'severity_distribution': {
                severity.value: sum(1 for r in recent_results if r.severity == severity)
                for severity in DriftSeverity
            }
        }

    def export_results(self, filepath: str) -> None:
        """Export drift detection results to file"""
        export_data = {
            'model_id': self.model_id,
            'export_timestamp': datetime.now().isoformat(),
            'configuration': {
                'default_method': self.default_method.value,
                'sensitivity_threshold': self.sensitivity_threshold,
                'method_config': {k.value: v for k, v in self.method_config.items()}
            },
            'drift_history': [
                {
                    'feature_name': r.feature_name,
                    'drift_detected': r.drift_detected,
                    'drift_score': r.drift_score,
                    'p_value': r.p_value,
                    'severity': r.severity.value,
                    'method_used': r.method_used.value,
                    'threshold': r.threshold,
                    'timestamp': r.timestamp.isoformat(),
                    'metadata': r.metadata
                }
                for r in self.drift_history
            ],
            'summary': self.get_drift_summary()
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
            
        logger.info(f"Drift detection results exported to {filepath}")


# Enterprise Creator-Specific Drift Detection Extensions
class CreatorSpecificDriftDetector(DataDriftDetector):
    """
    Creator-specific drift detection for Ainflue platform
    Specialized for musician, blogger, photographer, influencer, comedian use cases
    """
    
    def __init__(self, creator_type: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.creator_type = creator_type.lower()
        
        # Creator-specific drift thresholds and methods
        self.creator_configs = {
            'musician': {
                'audio_features': {
                    'method': DriftDetectionMethod.WASSERSTEIN_DISTANCE,
                    'threshold': 0.15,
                    'critical_features': ['tempo', 'energy', 'valence', 'danceability']
                }
            },
            'blogger': {
                'text_features': {
                    'method': DriftDetectionMethod.JENSEN_SHANNON_DIVERGENCE,
                    'threshold': 0.2,
                    'critical_features': ['sentiment', 'readability', 'topic_distribution']
                }
            },
            'photographer': {
                'image_features': {
                    'method': DriftDetectionMethod.KOLMOGOROV_SMIRNOV,
                    'threshold': 0.1,
                    'critical_features': ['brightness', 'contrast', 'color_distribution', 'composition_score']
                }
            },
            'influencer': {
                'engagement_features': {
                    'method': DriftDetectionMethod.POPULATION_STABILITY_INDEX,
                    'threshold': 0.25,
                    'critical_features': ['engagement_rate', 'reach', 'sentiment', 'platform_distribution']
                }
            },
            'comedian': {
                'performance_features': {
                    'method': DriftDetectionMethod.CHI_SQUARE,
                    'threshold': 0.05,
                    'critical_features': ['humor_type', 'timing_patterns', 'audience_reaction', 'delivery_style']
                }
            }
        }
        
        # Apply creator-specific configuration
        creator_config = self.creator_configs.get(self.creator_type, {})
        if creator_config:
            self._apply_creator_config(creator_config)

    def _apply_creator_config(self, config: Dict) -> None:
        """Apply creator-specific configuration"""
        for feature_group, settings in config.items():
            method = settings.get('method')
            threshold = settings.get('threshold')
            
            if method and threshold:
                self.method_config[method] = {'threshold': threshold}
                
        logger.info(f"Applied {self.creator_type} specific drift detection configuration")

    def detect_creator_specific_drift(
        self,
        current_data: pd.DataFrame,
        content_metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Enhanced drift detection with creator-specific insights"""
        
        # Standard drift detection
        drift_results = self.detect_drift(current_data)
        
        # Creator-specific analysis
        creator_insights = self._analyze_creator_specific_patterns(
            current_data, drift_results, content_metadata
        )
        
        return {
            'standard_drift_results': drift_results,
            'creator_specific_insights': creator_insights,
            'recommendations': self._generate_creator_recommendations(drift_results, creator_insights)
        }

    def _analyze_creator_specific_patterns(
        self,
        current_data: pd.DataFrame,
        drift_results: Dict[str, DriftDetectionResult],
        content_metadata: Optional[Dict]
    ) -> Dict[str, Any]:
        """Analyze creator-specific drift patterns"""
        
        insights = {
            'creator_type': self.creator_type,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # Get critical features for this creator type
        creator_config = self.creator_configs.get(self.creator_type, {})
        critical_features = []
        
        for feature_group in creator_config.values():
            critical_features.extend(feature_group.get('critical_features', []))
        
        # Analyze drift in critical features
        critical_drift = {
            feature: result for feature, result in drift_results.items()
            if feature in critical_features and result.drift_detected
        }
        
        insights['critical_features_with_drift'] = list(critical_drift.keys())
        insights['critical_drift_severity'] = {
            feature: result.severity.value for feature, result in critical_drift.items()
        }
        
        # Creator-specific pattern analysis
        if self.creator_type == 'musician':
            insights.update(self._analyze_musician_patterns(current_data, drift_results))
        elif self.creator_type == 'blogger':
            insights.update(self._analyze_blogger_patterns(current_data, drift_results))
        elif self.creator_type == 'photographer':
            insights.update(self._analyze_photographer_patterns(current_data, drift_results))
        elif self.creator_type == 'influencer':
            insights.update(self._analyze_influencer_patterns(current_data, drift_results))
        elif self.creator_type == 'comedian':
            insights.update(self._analyze_comedian_patterns(current_data, drift_results))
        
        return insights

    def _analyze_musician_patterns(self, data: pd.DataFrame, drift_results: Dict) -> Dict:
        """Musician-specific drift pattern analysis"""
        patterns = {}
        
        # Audio feature correlations
        audio_features = ['tempo', 'energy', 'valence', 'danceability', 'acousticness']
        present_features = [f for f in audio_features if f in data.columns]
        
        if present_features:
            patterns['audio_feature_drift_correlation'] = {
                'drifted_features': [f for f in present_features if f in drift_results and drift_results[f].drift_detected],
                'potential_genre_shift': self._detect_genre_shift_indicators(data, present_features)
            }
        
        return patterns

    def _analyze_blogger_patterns(self, data: pd.DataFrame, drift_results: Dict) -> Dict:
        """Blogger-specific drift pattern analysis"""
        patterns = {}
        
        text_features = ['sentiment', 'readability', 'topic_distribution', 'engagement_rate']
        present_features = [f for f in text_features if f in data.columns]
        
        if present_features:
            patterns['content_strategy_shift'] = {
                'drifted_text_features': [f for f in present_features if f in drift_results and drift_results[f].drift_detected],
                'potential_audience_change': self._detect_audience_shift_indicators(data, present_features)
            }
        
        return patterns

    def _analyze_photographer_patterns(self, data: pd.DataFrame, drift_results: Dict) -> Dict:
        """Photographer-specific drift pattern analysis"""
        patterns = {}
        
        visual_features = ['brightness', 'contrast', 'color_distribution', 'composition_score']
        present_features = [f for f in visual_features if f in data.columns]
        
        if present_features:
            patterns['visual_style_evolution'] = {
                'drifted_visual_features': [f for f in present_features if f in drift_results and drift_results[f].drift_detected],
                'potential_style_shift': self._detect_style_shift_indicators(data, present_features)
            }
        
        return patterns

    def _analyze_influencer_patterns(self, data: pd.DataFrame, drift_results: Dict) -> Dict:
        """Influencer-specific drift pattern analysis"""
        patterns = {}
        
        engagement_features = ['engagement_rate', 'reach', 'sentiment', 'platform_distribution']
        present_features = [f for f in engagement_features if f in data.columns]
        
        if present_features:
            patterns['audience_engagement_shift'] = {
                'drifted_engagement_features': [f for f in present_features if f in drift_results and drift_results[f].drift_detected],
                'potential_algorithm_change': self._detect_algorithm_change_indicators(data, present_features)
            }
        
        return patterns

    def _analyze_comedian_patterns(self, data: pd.DataFrame, drift_results: Dict) -> Dict:
        """Comedian-specific drift pattern analysis"""
        patterns = {}
        
        performance_features = ['humor_type', 'timing_patterns', 'audience_reaction', 'delivery_style']
        present_features = [f for f in performance_features if f in data.columns]
        
        if present_features:
            patterns['comedic_style_evolution'] = {
                'drifted_performance_features': [f for f in present_features if f in drift_results and drift_results[f].drift_detected],
                'potential_audience_preference_shift': self._detect_humor_preference_shift(data, present_features)
            }
        
        return patterns

    def _detect_genre_shift_indicators(self, data: pd.DataFrame, features: List[str]) -> bool:
        """Detect potential genre shift in music"""
        # Simplified logic - in practice would use more sophisticated analysis
        return len([f for f in features if f in data.columns and data[f].std() > data[f].mean() * 0.5]) > 2

    def _detect_audience_shift_indicators(self, data: pd.DataFrame, features: List[str]) -> bool:
        """Detect potential audience shift for bloggers"""
        return 'engagement_rate' in data.columns and data['engagement_rate'].std() > 0.3

    def _detect_style_shift_indicators(self, data: pd.DataFrame, features: List[str]) -> bool:
        """Detect potential style shift for photographers"""
        return len([f for f in features if f in data.columns and data[f].nunique() > len(data) * 0.8]) > 1

    def _detect_algorithm_change_indicators(self, data: pd.DataFrame, features: List[str]) -> bool:
        """Detect potential platform algorithm changes"""
        return 'reach' in data.columns and data['reach'].std() > data['reach'].mean() * 0.7

    def _detect_humor_preference_shift(self, data: pd.DataFrame, features: List[str]) -> bool:
        """Detect humor preference shifts for comedians"""
        return 'audience_reaction' in data.columns and data['audience_reaction'].std() > 0.4

    def _generate_creator_recommendations(
        self,
        drift_results: Dict[str, DriftDetectionResult],
        creator_insights: Dict[str, Any]
    ) -> List[str]:
        """Generate creator-specific recommendations based on drift analysis"""
        
        recommendations = []
        
        # General recommendations based on drift severity
        severe_drifts = [name for name, result in drift_results.items() 
                        if result.severity in [DriftSeverity.SEVERE, DriftSeverity.CRITICAL]]
        
        if severe_drifts:
            recommendations.append(
                f"Critical attention needed: Severe drift detected in {', '.join(severe_drifts)}"
            )
        
        # Creator-specific recommendations
        creator_type = creator_insights.get('creator_type')
        
        if creator_type == 'musician':
            if creator_insights.get('audio_feature_drift_correlation', {}).get('potential_genre_shift'):
                recommendations.append(
                    "Consider reviewing your musical style evolution - significant audio feature changes detected"
                )
                recommendations.append(
                    "Update model training data to include recent musical style changes"
                )
        
        elif creator_type == 'blogger':
            if creator_insights.get('content_strategy_shift', {}).get('potential_audience_change'):
                recommendations.append(
                    "Potential audience shift detected - consider segmenting your audience analysis"
                )
                recommendations.append(
                    "Review content strategy and ensure consistent messaging"
                )
        
        elif creator_type == 'photographer':
            if creator_insights.get('visual_style_evolution', {}).get('potential_style_shift'):
                recommendations.append(
                    "Visual style evolution detected - update portfolio recommendation models"
                )
                recommendations.append(
                    "Consider A/B testing new vs. traditional photography styles"
                )
        
        elif creator_type == 'influencer':
            if creator_insights.get('audience_engagement_shift', {}).get('potential_algorithm_change'):
                recommendations.append(
                    "Platform algorithm changes may be affecting engagement - adjust content strategy"
                )
                recommendations.append(
                    "Monitor cross-platform performance for algorithm impact assessment"
                )
        
        elif creator_type == 'comedian':
            if creator_insights.get('comedic_style_evolution', {}).get('potential_audience_preference_shift'):
                recommendations.append(
                    "Audience humor preferences may be shifting - test new material gradually"
                )
                recommendations.append(
                    "Consider timing and venue-specific performance adaptations"
                )
        
        # Add model-specific recommendations
        if any(result.drift_detected for result in drift_results.values()):
            recommendations.extend([
                "Schedule model retraining with recent data",
                "Review data collection and preprocessing pipelines",
                "Consider implementing gradual model updates",
                "Monitor business metrics for impact assessment"
            ])
        
        return recommendations