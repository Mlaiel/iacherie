"""Enhanced Data Drift Detection - Advanced drift monitoring with alerting

Comprehensive data drift detection system with statistical tests, automatic alerting,
and integration with the existing performance monitoring infrastructure.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import statistics
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import math
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class DriftType(Enum):
    """Types of drift"""
    FEATURE_DRIFT = "feature_drift"
    PREDICTION_DRIFT = "prediction_drift"
    CONCEPT_DRIFT = "concept_drift"
    COVARIATE_DRIFT = "covariate_drift"
    LABEL_DRIFT = "label_drift"


class DriftSeverity(Enum):
    """Drift severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class StatisticalTest(Enum):
    """Statistical tests for drift detection"""
    KOLMOGOROV_SMIRNOV = "kolmogorov_smirnov"
    CHI_SQUARE = "chi_square"
    JENSEN_SHANNON = "jensen_shannon"
    POPULATION_STABILITY_INDEX = "psi"
    HELLINGER_DISTANCE = "hellinger"
    WASSERSTEIN = "wasserstein"


@dataclass
class DriftAlert:
    """Data drift alert"""
    alert_id: str
    model_id: str
    drift_type: DriftType
    severity: DriftSeverity
    drift_score: float
    threshold: float
    statistical_test: StatisticalTest
    feature_name: Optional[str] = None
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False


@dataclass
class DriftDetectionConfig:
    """Configuration for drift detection"""
    detection_window_size: int = 1000
    reference_window_size: int = 5000
    drift_threshold: float = 0.1
    alert_threshold: float = 0.15
    critical_threshold: float = 0.3
    min_samples: int = 100
    check_interval_minutes: int = 15
    statistical_tests: List[StatisticalTest] = field(default_factory=lambda: [
        StatisticalTest.KOLMOGOROV_SMIRNOV,
        StatisticalTest.JENSEN_SHANNON,
        StatisticalTest.POPULATION_STABILITY_INDEX
    ])


@dataclass
class DriftAnalysisResult:
    """Result of drift analysis"""
    drift_type: DriftType
    drift_detected: bool
    drift_score: float
    statistical_test: StatisticalTest
    p_value: Optional[float] = None
    feature_name: Optional[str] = None
    severity: DriftSeverity = DriftSeverity.LOW
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class EnhancedDataDriftDetector:
    """Advanced data drift detection with automatic alerting"""
    
    def __init__(self, config: DriftDetectionConfig = None):
        self.config = config or DriftDetectionConfig()
        
        # Data storage
        self.reference_data: Dict[str, Dict[str, List[Any]]] = {}  # model_id -> feature_name -> data
        self.current_data: Dict[str, Dict[str, deque]] = {}  # model_id -> feature_name -> data
        self.prediction_history: Dict[str, deque] = {}  # model_id -> predictions
        self.label_history: Dict[str, deque] = {}  # model_id -> labels
        
        # Drift tracking
        self.drift_history: Dict[str, List[DriftAnalysisResult]] = {}
        self.active_alerts: Dict[str, List[DriftAlert]] = {}
        self.alert_callbacks: List[Callable] = []
        
        # Statistical test implementations
        self.test_implementations = {
            StatisticalTest.KOLMOGOROV_SMIRNOV: self._ks_test,
            StatisticalTest.CHI_SQUARE: self._chi_square_test,
            StatisticalTest.JENSEN_SHANNON: self._jensen_shannon_test,
            StatisticalTest.POPULATION_STABILITY_INDEX: self._psi_test,
            StatisticalTest.HELLINGER_DISTANCE: self._hellinger_test,
            StatisticalTest.WASSERSTEIN: self._wasserstein_test
        }
        
        # Monitoring state
        self.monitoring_active = False
        self.last_check: Dict[str, datetime] = {}
        
        logger.info("Enhanced data drift detector initialized")
    
    
    async def register_model(self, model_id: str, reference_data: Dict[str, List[Any]]) -> bool:
        """Register a model with reference data for drift detection"""
        try:
            self.reference_data[model_id] = reference_data
            self.current_data[model_id] = {
                feature: deque(maxlen=self.config.detection_window_size)
                for feature in reference_data.keys()
            }
            self.prediction_history[model_id] = deque(maxlen=self.config.detection_window_size)
            self.label_history[model_id] = deque(maxlen=self.config.detection_window_size)
            self.drift_history[model_id] = []
            self.active_alerts[model_id] = []
            
            logger.info(f"Model registered for drift detection: {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Model registration failed: {e}")
            return False
    
    
    async def update_data(self, model_id: str, feature_data: Dict[str, Any], 
                          prediction: Any = None, label: Any = None) -> bool:
        """Update current data for a model"""
        try:
            if model_id not in self.current_data:
                logger.warning(f"Model not registered: {model_id}")
                return False
            
            # Update feature data
            for feature_name, value in feature_data.items():
                if feature_name in self.current_data[model_id]:
                    self.current_data[model_id][feature_name].append(value)
            
            # Update predictions and labels
            if prediction is not None:
                self.prediction_history[model_id].append(prediction)
            
            if label is not None:
                self.label_history[model_id].append(label)
            
            return True
            
        except Exception as e:
            logger.error(f"Data update failed: {e}")
            return False
    
    
    async def detect_drift(self, model_id: str) -> List[DriftAnalysisResult]:
        """Perform comprehensive drift detection for a model"""
        try:
            if model_id not in self.current_data:
                return []
            
            results = []
            
            # Feature drift detection
            for feature_name in self.current_data[model_id].keys():
                feature_results = await self._detect_feature_drift(model_id, feature_name)
                results.extend(feature_results)
            
            # Prediction drift detection
            prediction_results = await self._detect_prediction_drift(model_id)
            results.extend(prediction_results)
            
            # Concept drift detection (if labels available)
            if self.label_history[model_id]:
                concept_results = await self._detect_concept_drift(model_id)
                results.extend(concept_results)
            
            # Store results
            self.drift_history[model_id].extend(results)
            
            # Generate alerts for significant drift
            await self._process_drift_results(model_id, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Drift detection failed: {e}")
            return []
    
    
    async def start_monitoring(self, model_ids: List[str] = None) -> bool:
        """Start continuous drift monitoring"""
        try:
            if self.monitoring_active:
                return True
            
            self.monitoring_active = True
            
            # Start monitoring task
            asyncio.create_task(self._monitoring_loop(model_ids))
            
            logger.info("Drift monitoring started")
            return True
            
        except Exception as e:
            logger.error(f"Monitoring start failed: {e}")
            return False
    
    
    async def stop_monitoring(self):
        """Stop drift monitoring"""
        self.monitoring_active = False
        logger.info("Drift monitoring stopped")
    
    
    async def get_drift_report(self, model_id: str = None, days_back: int = 7) -> Dict[str, Any]:
        """Generate a comprehensive drift report"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            if model_id:
                model_ids = [model_id] if model_id in self.drift_history else []
            else:
                model_ids = list(self.drift_history.keys())
            
            report = {
                "summary": {
                    "models_monitored": len(model_ids),
                    "total_drift_events": 0,
                    "active_alerts": 0,
                    "critical_alerts": 0
                },
                "models": {},
                "generated_at": datetime.now().isoformat()
            }
            
            for mid in model_ids:
                # Filter recent drift events
                recent_drifts = [
                    d for d in self.drift_history[mid] 
                    if d.timestamp >= cutoff_date
                ]
                
                # Count active alerts
                active_alerts = [a for a in self.active_alerts[mid] if not a.acknowledged]
                critical_alerts = [a for a in active_alerts if a.severity == DriftSeverity.CRITICAL]
                
                # Feature-wise breakdown
                feature_breakdown = {}
                for drift in recent_drifts:
                    if drift.feature_name:
                        if drift.feature_name not in feature_breakdown:
                            feature_breakdown[drift.feature_name] = {
                                "total_events": 0,
                                "detected_events": 0,
                                "max_drift_score": 0.0
                            }
                        
                        feature_breakdown[drift.feature_name]["total_events"] += 1
                        if drift.drift_detected:
                            feature_breakdown[drift.feature_name]["detected_events"] += 1
                        feature_breakdown[drift.feature_name]["max_drift_score"] = max(
                            feature_breakdown[drift.feature_name]["max_drift_score"],
                            drift.drift_score
                        )
                
                report["models"][mid] = {
                    "drift_events": len(recent_drifts),
                    "detected_drifts": len([d for d in recent_drifts if d.drift_detected]),
                    "active_alerts": len(active_alerts),
                    "critical_alerts": len(critical_alerts),
                    "feature_breakdown": feature_breakdown,
                    "last_check": self.last_check.get(mid, "Never").isoformat() if isinstance(self.last_check.get(mid), datetime) else "Never"
                }
                
                # Update summary
                report["summary"]["total_drift_events"] += len(recent_drifts)
                report["summary"]["active_alerts"] += len(active_alerts)
                report["summary"]["critical_alerts"] += len(critical_alerts)
            
            return report
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return {"error": str(e)}
    
    
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge a drift alert"""
        try:
            for model_id, alerts in self.active_alerts.items():
                for alert in alerts:
                    if alert.alert_id == alert_id:
                        alert.acknowledged = True
                        logger.info(f"Alert acknowledged: {alert_id}")
                        return True
            
            logger.warning(f"Alert not found: {alert_id}")
            return False
            
        except Exception as e:
            logger.error(f"Alert acknowledgment failed: {e}")
            return False
    
    
    async def add_alert_callback(self, callback: Callable):
        """Add a callback function for drift alerts"""
        self.alert_callbacks.append(callback)
    
    
    async def _detect_feature_drift(self, model_id: str, feature_name: str) -> List[DriftAnalysisResult]:
        """Detect drift for a specific feature"""
        try:
            results = []
            
            reference_data = self.reference_data[model_id].get(feature_name, [])
            current_data = list(self.current_data[model_id][feature_name])
            
            if len(current_data) < self.config.min_samples or not reference_data:
                return results
            
            # Apply multiple statistical tests
            for test_type in self.config.statistical_tests:
                if test_type in self.test_implementations:
                    try:
                        drift_score, p_value, details = await self.test_implementations[test_type](
                            reference_data, current_data
                        )
                        
                        drift_detected = drift_score > self.config.drift_threshold
                        severity = self._calculate_severity(drift_score)
                        
                        result = DriftAnalysisResult(
                            drift_type=DriftType.FEATURE_DRIFT,
                            drift_detected=drift_detected,
                            drift_score=drift_score,
                            statistical_test=test_type,
                            p_value=p_value,
                            feature_name=feature_name,
                            severity=severity,
                            details=details
                        )
                        
                        results.append(result)
                        
                    except Exception as e:
                        logger.error(f"Statistical test {test_type} failed: {e}")
            
            return results
            
        except Exception as e:
            logger.error(f"Feature drift detection failed: {e}")
            return []
    
    
    async def _detect_prediction_drift(self, model_id: str) -> List[DriftAnalysisResult]:
        """Detect prediction drift"""
        try:
            results = []
            current_predictions = list(self.prediction_history[model_id])
            
            if len(current_predictions) < self.config.min_samples:
                return results
            
            # Split into reference and current windows
            split_point = len(current_predictions) // 2
            reference_predictions = current_predictions[:split_point]
            recent_predictions = current_predictions[split_point:]
            
            if len(reference_predictions) < self.config.min_samples // 2:
                return results
            
            # Apply statistical tests
            for test_type in self.config.statistical_tests:
                if test_type in self.test_implementations:
                    try:
                        drift_score, p_value, details = await self.test_implementations[test_type](
                            reference_predictions, recent_predictions
                        )
                        
                        drift_detected = drift_score > self.config.drift_threshold
                        severity = self._calculate_severity(drift_score)
                        
                        result = DriftAnalysisResult(
                            drift_type=DriftType.PREDICTION_DRIFT,
                            drift_detected=drift_detected,
                            drift_score=drift_score,
                            statistical_test=test_type,
                            p_value=p_value,
                            severity=severity,
                            details=details
                        )
                        
                        results.append(result)
                        
                    except Exception as e:
                        logger.error(f"Prediction drift test {test_type} failed: {e}")
            
            return results
            
        except Exception as e:
            logger.error(f"Prediction drift detection failed: {e}")
            return []
    
    
    async def _detect_concept_drift(self, model_id: str) -> List[DriftAnalysisResult]:
        """Detect concept drift using predictions and labels"""
        try:
            results = []
            predictions = list(self.prediction_history[model_id])
            labels = list(self.label_history[model_id])
            
            # Align predictions and labels
            min_length = min(len(predictions), len(labels))
            if min_length < self.config.min_samples:
                return results
            
            predictions = predictions[-min_length:]
            labels = labels[-min_length:]
            
            # Calculate prediction accuracy over time windows
            window_size = min_length // 4
            accuracy_scores = []
            
            for i in range(0, min_length - window_size, window_size // 2):
                window_predictions = predictions[i:i + window_size]
                window_labels = labels[i:i + window_size]
                
                # Simple accuracy calculation (assumes binary classification)
                correct = sum(1 for p, l in zip(window_predictions, window_labels) if abs(p - l) < 0.5)
                accuracy = correct / len(window_predictions)
                accuracy_scores.append(accuracy)
            
            if len(accuracy_scores) < 2:
                return results
            
            # Detect trend in accuracy
            trend = self._calculate_trend(accuracy_scores)
            drift_score = abs(trend)
            
            drift_detected = drift_score > self.config.drift_threshold
            severity = self._calculate_severity(drift_score)
            
            result = DriftAnalysisResult(
                drift_type=DriftType.CONCEPT_DRIFT,
                drift_detected=drift_detected,
                drift_score=drift_score,
                statistical_test=StatisticalTest.KOLMOGOROV_SMIRNOV,  # Placeholder
                severity=severity,
                details={
                    "accuracy_trend": trend,
                    "accuracy_scores": accuracy_scores,
                    "window_count": len(accuracy_scores)
                }
            )
            
            results.append(result)
            return results
            
        except Exception as e:
            logger.error(f"Concept drift detection failed: {e}")
            return []
    
    
    async def _process_drift_results(self, model_id: str, results: List[DriftAnalysisResult]):
        """Process drift results and generate alerts"""
        try:
            for result in results:
                if result.drift_detected and result.drift_score >= self.config.alert_threshold:
                    # Create alert
                    alert = DriftAlert(
                        alert_id=str(uuid.uuid4()),
                        model_id=model_id,
                        drift_type=result.drift_type,
                        severity=result.severity,
                        drift_score=result.drift_score,
                        threshold=self.config.drift_threshold,
                        statistical_test=result.statistical_test,
                        feature_name=result.feature_name,
                        message=self._generate_alert_message(result),
                        details=result.details
                    )
                    
                    self.active_alerts[model_id].append(alert)
                    
                    # Trigger callbacks
                    for callback in self.alert_callbacks:
                        try:
                            await callback(alert)
                        except Exception as e:
                            logger.error(f"Alert callback failed: {e}")
                    
                    logger.warning(f"Drift alert generated: {alert.alert_id} for model {model_id}")
            
        except Exception as e:
            logger.error(f"Alert processing failed: {e}")
    
    
    def _calculate_severity(self, drift_score: float) -> DriftSeverity:
        """Calculate severity based on drift score"""
        if drift_score >= self.config.critical_threshold:
            return DriftSeverity.CRITICAL
        elif drift_score >= self.config.alert_threshold:
            return DriftSeverity.HIGH
        elif drift_score >= self.config.drift_threshold:
            return DriftSeverity.MEDIUM
        else:
            return DriftSeverity.LOW
    
    
    def _generate_alert_message(self, result: DriftAnalysisResult) -> str:
        """Generate human-readable alert message"""
        feature_part = f" in feature '{result.feature_name}'" if result.feature_name else ""
        
        return (f"{result.drift_type.value.replace('_', ' ').title()} detected{feature_part} "
                f"(score: {result.drift_score:.3f}, test: {result.statistical_test.value})")
    
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend using simple linear regression slope"""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x_values = list(range(n))
        
        # Calculate slope using least squares
        x_mean = sum(x_values) / n
        y_mean = sum(values) / n
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    
    async def _monitoring_loop(self, model_ids: List[str] = None):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                target_models = model_ids if model_ids else list(self.current_data.keys())
                
                for model_id in target_models:
                    # Check if enough time has passed since last check
                    last_check = self.last_check.get(model_id)
                    if last_check:
                        next_check = last_check + timedelta(minutes=self.config.check_interval_minutes)
                        if datetime.now() < next_check:
                            continue
                    
                    # Perform drift detection
                    await self.detect_drift(model_id)
                    self.last_check[model_id] = datetime.now()
                
                # Sleep until next check
                await asyncio.sleep(60)  # Check every minute for scheduling
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    
    # Statistical test implementations
    
    async def _ks_test(self, reference: List[Any], current: List[Any]) -> Tuple[float, Optional[float], Dict]:
        """Kolmogorov-Smirnov test for distribution comparison"""
        try:
            # Convert to numeric if possible
            ref_numeric = self._to_numeric(reference)
            cur_numeric = self._to_numeric(current)
            
            if ref_numeric is None or cur_numeric is None:
                return 0.0, None, {"error": "Non-numeric data"}
            
            # Sort data
            ref_sorted = sorted(ref_numeric)
            cur_sorted = sorted(cur_numeric)
            
            # Calculate empirical CDFs and KS statistic
            max_diff = 0.0
            all_values = sorted(set(ref_sorted + cur_sorted))
            
            for value in all_values:
                ref_cdf = sum(1 for x in ref_sorted if x <= value) / len(ref_sorted)
                cur_cdf = sum(1 for x in cur_sorted if x <= value) / len(cur_sorted)
                max_diff = max(max_diff, abs(ref_cdf - cur_cdf))
            
            # Simple p-value approximation
            n1, n2 = len(ref_sorted), len(cur_sorted)
            effective_n = (n1 * n2) / (n1 + n2)
            p_value = 2 * math.exp(-2 * effective_n * max_diff ** 2) if effective_n > 0 else 1.0
            
            return max_diff, p_value, {
                "ks_statistic": max_diff,
                "reference_size": n1,
                "current_size": n2
            }
            
        except Exception as e:
            logger.error(f"KS test failed: {e}")
            return 0.0, None, {"error": str(e)}
    
    
    async def _jensen_shannon_test(self, reference: List[Any], current: List[Any]) -> Tuple[float, Optional[float], Dict]:
        """Jensen-Shannon divergence test"""
        try:
            # Create histograms
            ref_hist, cur_hist = self._create_histograms(reference, current)
            
            if not ref_hist or not cur_hist:
                return 0.0, None, {"error": "Cannot create histograms"}
            
            # Calculate JS divergence
            js_div = self._js_divergence(ref_hist, cur_hist)
            
            return js_div, None, {
                "js_divergence": js_div,
                "reference_bins": len(ref_hist),
                "current_bins": len(cur_hist)
            }
            
        except Exception as e:
            logger.error(f"JS test failed: {e}")
            return 0.0, None, {"error": str(e)}
    
    
    async def _psi_test(self, reference: List[Any], current: List[Any]) -> Tuple[float, Optional[float], Dict]:
        """Population Stability Index test"""
        try:
            # Create histograms with same bins
            ref_hist, cur_hist = self._create_aligned_histograms(reference, current)
            
            if not ref_hist or not cur_hist:
                return 0.0, None, {"error": "Cannot create aligned histograms"}
            
            # Calculate PSI
            psi_score = 0.0
            for ref_prop, cur_prop in zip(ref_hist, cur_hist):
                if ref_prop > 0 and cur_prop > 0:
                    psi_score += (cur_prop - ref_prop) * math.log(cur_prop / ref_prop)
            
            return psi_score, None, {
                "psi_score": psi_score,
                "bin_count": len(ref_hist)
            }
            
        except Exception as e:
            logger.error(f"PSI test failed: {e}")
            return 0.0, None, {"error": str(e)}
    
    
    async def _chi_square_test(self, reference: List[Any], current: List[Any]) -> Tuple[float, Optional[float], Dict]:
        """Chi-square test for categorical data"""
        try:
            # Create frequency distributions
            ref_freq = self._create_frequency_dist(reference)
            cur_freq = self._create_frequency_dist(current)
            
            # Align categories
            all_categories = set(ref_freq.keys()) | set(cur_freq.keys())
            
            chi_square = 0.0
            for category in all_categories:
                expected = ref_freq.get(category, 0)
                observed = cur_freq.get(category, 0)
                
                if expected > 0:
                    chi_square += ((observed - expected) ** 2) / expected
            
            # Normalize by degrees of freedom
            df = len(all_categories) - 1
            normalized_chi_square = chi_square / df if df > 0 else 0.0
            
            return normalized_chi_square, None, {
                "chi_square": chi_square,
                "degrees_of_freedom": df,
                "categories": len(all_categories)
            }
            
        except Exception as e:
            logger.error(f"Chi-square test failed: {e}")
            return 0.0, None, {"error": str(e)}
    
    
    async def _hellinger_test(self, reference: List[Any], current: List[Any]) -> Tuple[float, Optional[float], Dict]:
        """Hellinger distance test"""
        try:
            ref_hist, cur_hist = self._create_aligned_histograms(reference, current)
            
            if not ref_hist or not cur_hist:
                return 0.0, None, {"error": "Cannot create histograms"}
            
            # Calculate Hellinger distance
            hellinger_dist = 0.0
            for p, q in zip(ref_hist, cur_hist):
                hellinger_dist += (math.sqrt(p) - math.sqrt(q)) ** 2
            
            hellinger_dist = math.sqrt(hellinger_dist) / math.sqrt(2)
            
            return hellinger_dist, None, {
                "hellinger_distance": hellinger_dist,
                "bin_count": len(ref_hist)
            }
            
        except Exception as e:
            logger.error(f"Hellinger test failed: {e}")
            return 0.0, None, {"error": str(e)}
    
    
    async def _wasserstein_test(self, reference: List[Any], current: List[Any]) -> Tuple[float, Optional[float], Dict]:
        """Wasserstein (Earth Mover's) distance test"""
        try:
            ref_numeric = self._to_numeric(reference)
            cur_numeric = self._to_numeric(current)
            
            if ref_numeric is None or cur_numeric is None:
                return 0.0, None, {"error": "Non-numeric data"}
            
            # Sort both distributions
            ref_sorted = sorted(ref_numeric)
            cur_sorted = sorted(cur_numeric)
            
            # Calculate Wasserstein distance (simplified 1D version)
            wasserstein_dist = 0.0
            all_values = sorted(set(ref_sorted + cur_sorted))
            
            for i, value in enumerate(all_values):
                ref_cdf = sum(1 for x in ref_sorted if x <= value) / len(ref_sorted)
                cur_cdf = sum(1 for x in cur_sorted if x <= value) / len(cur_sorted)
                
                if i > 0:
                    prev_value = all_values[i - 1]
                    wasserstein_dist += abs(ref_cdf - cur_cdf) * (value - prev_value)
            
            # Normalize by data range
            data_range = max(all_values) - min(all_values) if all_values else 1.0
            normalized_dist = wasserstein_dist / data_range if data_range > 0 else 0.0
            
            return normalized_dist, None, {
                "wasserstein_distance": wasserstein_dist,
                "normalized_distance": normalized_dist,
                "data_range": data_range
            }
            
        except Exception as e:
            logger.error(f"Wasserstein test failed: {e}")
            return 0.0, None, {"error": str(e)}
    
    
    # Helper methods
    
    def _to_numeric(self, data: List[Any]) -> Optional[List[float]]:
        """Convert data to numeric if possible"""
        try:
            numeric_data = []
            for item in data:
                if isinstance(item, (int, float)):
                    numeric_data.append(float(item))
                elif isinstance(item, str):
                    try:
                        numeric_data.append(float(item))
                    except ValueError:
                        return None
                else:
                    return None
            return numeric_data
        except:
            return None
    
    
    def _create_histograms(self, ref_data: List[Any], cur_data: List[Any], bins: int = 10) -> Tuple[List[float], List[float]]:
        """Create normalized histograms for both datasets"""
        try:
            ref_numeric = self._to_numeric(ref_data)
            cur_numeric = self._to_numeric(cur_data)
            
            if ref_numeric is None or cur_numeric is None:
                return [], []
            
            # Determine common range
            all_data = ref_numeric + cur_numeric
            min_val, max_val = min(all_data), max(all_data)
            
            if min_val == max_val:
                return [1.0], [1.0]
            
            # Create bins
            bin_width = (max_val - min_val) / bins
            bin_edges = [min_val + i * bin_width for i in range(bins + 1)]
            
            # Create histograms
            ref_hist = [0] * bins
            cur_hist = [0] * bins
            
            for value in ref_numeric:
                bin_idx = min(int((value - min_val) / bin_width), bins - 1)
                ref_hist[bin_idx] += 1
            
            for value in cur_numeric:
                bin_idx = min(int((value - min_val) / bin_width), bins - 1)
                cur_hist[bin_idx] += 1
            
            # Normalize
            ref_total = sum(ref_hist)
            cur_total = sum(cur_hist)
            
            if ref_total > 0:
                ref_hist = [count / ref_total for count in ref_hist]
            if cur_total > 0:
                cur_hist = [count / cur_total for count in cur_hist]
            
            return ref_hist, cur_hist
            
        except Exception as e:
            logger.error(f"Histogram creation failed: {e}")
            return [], []
    
    
    def _create_aligned_histograms(self, ref_data: List[Any], cur_data: List[Any]) -> Tuple[List[float], List[float]]:
        """Create aligned histograms with consistent binning"""
        return self._create_histograms(ref_data, cur_data)
    
    
    def _create_frequency_dist(self, data: List[Any]) -> Dict[Any, int]:
        """Create frequency distribution for categorical data"""
        freq_dist = {}
        for item in data:
            freq_dist[item] = freq_dist.get(item, 0) + 1
        return freq_dist
    
    
    def _js_divergence(self, p: List[float], q: List[float]) -> float:
        """Calculate Jensen-Shannon divergence"""
        try:
            # Ensure same length
            min_len = min(len(p), len(q))
            p = p[:min_len]
            q = q[:min_len]
            
            # Calculate M = (P + Q) / 2
            m = [(pi + qi) / 2 for pi, qi in zip(p, q)]
            
            # Calculate KL divergences
            kl_pm = sum(pi * math.log(pi / mi) if pi > 0 and mi > 0 else 0 for pi, mi in zip(p, m))
            kl_qm = sum(qi * math.log(qi / mi) if qi > 0 and mi > 0 else 0 for qi, mi in zip(q, m))
            
            # JS divergence
            js_div = (kl_pm + kl_qm) / 2
            
            return js_div
            
        except Exception as e:
            logger.error(f"JS divergence calculation failed: {e}")
            return 0.0