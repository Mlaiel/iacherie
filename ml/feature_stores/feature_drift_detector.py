#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 ML Module - Feature Drift Detector
Feature drift detection and adaptation strategies

Ersteller: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Alle Rechte vorbehalten.
Version: 1.0.0
Letztes Update: Januar 2025

⚠️ WARNUNG: Dieser Code ist urheberrechtlich geschützt und vertraulich.
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from enum import Enum
import json
import time
from datetime import datetime, timedelta
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import jensen_shannon_distance
import warnings
from collections import defaultdict, deque
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DriftDetectionMethod(Enum):
    """Methods for detecting feature drift."""
    KOLMOGOROV_SMIRNOV = "kolmogorov_smirnov"
    JENSEN_SHANNON = "jensen_shannon"
    POPULATION_STABILITY_INDEX = "psi"
    WASSERSTEIN_DISTANCE = "wasserstein"
    CHI_SQUARE = "chi_square"
    STATISTICAL_DISTANCE = "statistical_distance"
    DISTRIBUTION_COMPARISON = "distribution_comparison"
    ADAPTIVE_WINDOWING = "adaptive_windowing"

class DriftSeverity(Enum):
    """Severity levels of detected drift."""
    NO_DRIFT = "no_drift"
    LOW_DRIFT = "low_drift"
    MODERATE_DRIFT = "moderate_drift"
    HIGH_DRIFT = "high_drift"
    CRITICAL_DRIFT = "critical_drift"

class CreatorType(Enum):
    """Creator types for specialized drift analysis."""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"

class AdaptationStrategy(Enum):
    """Strategies for adapting to detected drift."""
    RETRAIN_MODEL = "retrain_model"
    UPDATE_FEATURES = "update_features"
    ADJUST_THRESHOLDS = "adjust_thresholds"
    ENSEMBLE_WEIGHTING = "ensemble_weighting"
    INCREMENTAL_LEARNING = "incremental_learning"
    FEATURE_SELECTION = "feature_selection"
    NO_ACTION = "no_action"

@dataclass
class FeatureSnapshot:
    """Snapshot of feature data at a specific time."""
    timestamp: datetime
    feature_name: str
    feature_values: np.ndarray
    statistics: Dict[str, float]
    creator_type: Optional[CreatorType] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DriftDetectionResult:
    """Result of drift detection analysis."""
    feature_name: str
    drift_detected: bool
    drift_severity: DriftSeverity
    drift_score: float
    detection_method: DriftDetectionMethod
    p_value: Optional[float]
    confidence_interval: Optional[Tuple[float, float]]
    timestamp: datetime
    adaptation_strategy: AdaptationStrategy
    creator_type: Optional[CreatorType] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DriftDetectionConfig:
    """Configuration for drift detection."""
    detection_method: DriftDetectionMethod
    sensitivity_threshold: float = 0.05
    critical_threshold: float = 0.01
    window_size: int = 1000
    min_samples: int = 100
    adaptation_enabled: bool = True
    creator_specific: bool = True

class FeatureDriftDetector:
    """
    🔬 ML ENGINEER - Advanced Feature Drift Detection System
    
    Sophisticated feature drift detection with multiple statistical methods,
    creator-specific thresholds, and automated adaptation strategies.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize feature drift detector."""
        self.config = config or {}
        self.reference_snapshots: Dict[str, FeatureSnapshot] = {}
        self.current_snapshots: Dict[str, FeatureSnapshot] = {}
        self.drift_history: List[DriftDetectionResult] = []
        self.feature_windows: Dict[str, deque] = defaultdict(lambda: deque())
        self.adaptation_history: List[Dict[str, Any]] = []
        
        # Detection configurations
        self.detection_configs: Dict[str, DriftDetectionConfig] = {}
        self.creator_thresholds: Dict[CreatorType, Dict[str, float]] = {}
        
        # Performance tracking
        self.detection_performance: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        # Initialize logging
        logger.info("🔬 FeatureDriftDetector initialized - ML Engineer expertise")
        
        # Initialize creator-specific thresholds
        self._initialize_creator_thresholds()
        
        # Setup default detection configurations
        self._initialize_default_configs()
    
    def _initialize_creator_thresholds(self):
        """Initialize creator-specific drift detection thresholds."""
        self.creator_thresholds = {
            CreatorType.MUSICIAN: {
                "sensitivity_threshold": 0.03,  # More sensitive for audio features
                "critical_threshold": 0.008,
                "temporal_weight": 1.2,         # Higher weight for temporal patterns
                "engagement_weight": 1.5,       # Music engagement is critical
                "seasonal_adjustment": 1.1      # Account for music seasonality
            },
            CreatorType.BLOGGER: {
                "sensitivity_threshold": 0.05,  # Standard sensitivity for text
                "critical_threshold": 0.01,
                "temporal_weight": 1.0,
                "engagement_weight": 1.3,       # Text engagement varies more
                "seasonal_adjustment": 1.0
            },
            CreatorType.PHOTOGRAPHER: {
                "sensitivity_threshold": 0.04,  # Visual content changes faster
                "critical_threshold": 0.01,
                "temporal_weight": 1.1,
                "engagement_weight": 1.4,       # Visual engagement is volatile
                "seasonal_adjustment": 1.3      # Strong seasonal effects
            },
            CreatorType.INFLUENCER: {
                "sensitivity_threshold": 0.02,  # Very sensitive to trends
                "critical_threshold": 0.005,
                "temporal_weight": 1.4,         # Trend sensitivity
                "engagement_weight": 1.6,       # Engagement is everything
                "seasonal_adjustment": 1.2
            },
            CreatorType.COMEDIAN: {
                "sensitivity_threshold": 0.04,  # Comedy trends change
                "critical_threshold": 0.01,
                "temporal_weight": 1.1,
                "engagement_weight": 1.4,       # Humor engagement varies
                "seasonal_adjustment": 1.0
            }
        }
    
    def _initialize_default_configs(self):
        """Initialize default drift detection configurations."""
        default_methods = [
            DriftDetectionMethod.KOLMOGOROV_SMIRNOV,
            DriftDetectionMethod.JENSEN_SHANNON,
            DriftDetectionMethod.POPULATION_STABILITY_INDEX
        ]
        
        for method in default_methods:
            self.detection_configs[method.value] = DriftDetectionConfig(
                detection_method=method,
                sensitivity_threshold=0.05,
                critical_threshold=0.01,
                window_size=1000,
                min_samples=100,
                adaptation_enabled=True,
                creator_specific=True
            )
    
    async def add_reference_snapshot(
        self,
        feature_name: str,
        feature_values: np.ndarray,
        creator_type: Optional[CreatorType] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add reference snapshot for drift detection baseline.
        
        Args:
            feature_name: Name of the feature
            feature_values: Reference feature values
            creator_type: Creator type for specialized thresholds
            metadata: Additional metadata
        """
        if len(feature_values) == 0:
            logger.warning(f"⚠️ Empty feature values for {feature_name}")
            return
        
        # Calculate statistics
        statistics = self._calculate_feature_statistics(feature_values)
        
        # Create snapshot
        snapshot = FeatureSnapshot(
            timestamp=datetime.now(),
            feature_name=feature_name,
            feature_values=feature_values.copy(),
            statistics=statistics,
            creator_type=creator_type,
            metadata=metadata or {}
        )
        
        self.reference_snapshots[feature_name] = snapshot
        
        logger.info(f"📊 Reference snapshot added for feature: {feature_name}")
    
    async def detect_drift(
        self,
        feature_name: str,
        current_values: np.ndarray,
        detection_method: DriftDetectionMethod = DriftDetectionMethod.KOLMOGOROV_SMIRNOV,
        creator_type: Optional[CreatorType] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DriftDetectionResult:
        """
        Detect drift in feature values compared to reference.
        
        Args:
            feature_name: Name of the feature to analyze
            current_values: Current feature values
            detection_method: Method to use for drift detection
            creator_type: Creator type for specialized analysis
            metadata: Additional metadata
            
        Returns:
            Drift detection result
        """
        logger.info(f"🔍 Detecting drift for feature: {feature_name}")
        
        # Check if reference snapshot exists
        if feature_name not in self.reference_snapshots:
            logger.warning(f"⚠️ No reference snapshot for feature {feature_name}")
            return self._create_no_drift_result(feature_name, detection_method, creator_type)
        
        reference_snapshot = self.reference_snapshots[feature_name]
        reference_values = reference_snapshot.feature_values
        
        if len(current_values) == 0:
            logger.warning(f"⚠️ Empty current values for {feature_name}")
            return self._create_no_drift_result(feature_name, detection_method, creator_type)
        
        # Create current snapshot
        current_statistics = self._calculate_feature_statistics(current_values)
        current_snapshot = FeatureSnapshot(
            timestamp=datetime.now(),
            feature_name=feature_name,
            feature_values=current_values.copy(),
            statistics=current_statistics,
            creator_type=creator_type,
            metadata=metadata or {}
        )
        
        self.current_snapshots[feature_name] = current_snapshot
        
        # Perform drift detection based on method
        if detection_method == DriftDetectionMethod.KOLMOGOROV_SMIRNOV:
            result = await self._detect_drift_ks(feature_name, reference_values, current_values, creator_type)
        elif detection_method == DriftDetectionMethod.JENSEN_SHANNON:
            result = await self._detect_drift_js(feature_name, reference_values, current_values, creator_type)
        elif detection_method == DriftDetectionMethod.POPULATION_STABILITY_INDEX:
            result = await self._detect_drift_psi(feature_name, reference_values, current_values, creator_type)
        elif detection_method == DriftDetectionMethod.WASSERSTEIN_DISTANCE:
            result = await self._detect_drift_wasserstein(feature_name, reference_values, current_values, creator_type)
        elif detection_method == DriftDetectionMethod.CHI_SQUARE:
            result = await self._detect_drift_chi_square(feature_name, reference_values, current_values, creator_type)
        elif detection_method == DriftDetectionMethod.STATISTICAL_DISTANCE:
            result = await self._detect_drift_statistical(feature_name, reference_values, current_values, creator_type)
        else:
            logger.warning(f"⚠️ Unsupported detection method: {detection_method.value}")
            return self._create_no_drift_result(feature_name, detection_method, creator_type)
        
        # Store result in history
        self.drift_history.append(result)
        
        # Update feature window
        self.feature_windows[feature_name].append(current_values)
        config = self.detection_configs.get(detection_method.value)
        if config and len(self.feature_windows[feature_name]) > config.window_size:
            self.feature_windows[feature_name].popleft()
        
        # Apply adaptation strategy if needed
        if result.drift_detected and config and config.adaptation_enabled:
            await self._apply_adaptation_strategy(result)
        
        logger.info(f"✅ Drift detection completed: {result.drift_severity.value}")
        return result
    
    def _calculate_feature_statistics(self, values: np.ndarray) -> Dict[str, float]:
        """Calculate comprehensive statistics for feature values."""
        if len(values) == 0:
            return {}
        
        return {
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "median": float(np.median(values)),
            "q25": float(np.percentile(values, 25)),
            "q75": float(np.percentile(values, 75)),
            "skewness": float(stats.skew(values)),
            "kurtosis": float(stats.kurtosis(values)),
            "variance": float(np.var(values)),
            "count": len(values)
        }
    
    async def _detect_drift_ks(
        self,
        feature_name: str,
        reference_values: np.ndarray,
        current_values: np.ndarray,
        creator_type: Optional[CreatorType]
    ) -> DriftDetectionResult:
        """Detect drift using Kolmogorov-Smirnov test."""
        try:
            # Perform KS test
            ks_statistic, p_value = stats.ks_2samp(reference_values, current_values)
            
            # Get creator-specific thresholds
            thresholds = self._get_creator_thresholds(creator_type)
            sensitivity_threshold = thresholds["sensitivity_threshold"]
            critical_threshold = thresholds["critical_threshold"]
            
            # Determine drift severity
            drift_detected = p_value < sensitivity_threshold
            
            if p_value < critical_threshold:
                severity = DriftSeverity.CRITICAL_DRIFT
                strategy = AdaptationStrategy.RETRAIN_MODEL
            elif p_value < critical_threshold * 2:
                severity = DriftSeverity.HIGH_DRIFT
                strategy = AdaptationStrategy.UPDATE_FEATURES
            elif p_value < sensitivity_threshold:
                severity = DriftSeverity.MODERATE_DRIFT
                strategy = AdaptationStrategy.ADJUST_THRESHOLDS
            elif p_value < sensitivity_threshold * 2:
                severity = DriftSeverity.LOW_DRIFT
                strategy = AdaptationStrategy.INCREMENTAL_LEARNING
            else:
                severity = DriftSeverity.NO_DRIFT
                strategy = AdaptationStrategy.NO_ACTION
            
            return DriftDetectionResult(
                feature_name=feature_name,
                drift_detected=drift_detected,
                drift_severity=severity,
                drift_score=ks_statistic,
                detection_method=DriftDetectionMethod.KOLMOGOROV_SMIRNOV,
                p_value=p_value,
                confidence_interval=(
                    max(0, ks_statistic - 1.96 * np.sqrt((len(reference_values) + len(current_values)) / (len(reference_values) * len(current_values)))),
                    ks_statistic + 1.96 * np.sqrt((len(reference_values) + len(current_values)) / (len(reference_values) * len(current_values)))
                ),
                timestamp=datetime.now(),
                adaptation_strategy=strategy,
                creator_type=creator_type,
                metadata={
                    "ks_statistic": ks_statistic,
                    "reference_size": len(reference_values),
                    "current_size": len(current_values)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in KS drift detection: {e}")
            return self._create_no_drift_result(feature_name, DriftDetectionMethod.KOLMOGOROV_SMIRNOV, creator_type)
    
    async def _detect_drift_js(
        self,
        feature_name: str,
        reference_values: np.ndarray,
        current_values: np.ndarray,
        creator_type: Optional[CreatorType]
    ) -> DriftDetectionResult:
        """Detect drift using Jensen-Shannon divergence."""
        try:
            # Create histograms
            min_val = min(np.min(reference_values), np.min(current_values))
            max_val = max(np.max(reference_values), np.max(current_values))
            
            # Use appropriate number of bins
            n_bins = min(50, int(np.sqrt(min(len(reference_values), len(current_values)))))
            bins = np.linspace(min_val, max_val, n_bins + 1)
            
            ref_hist, _ = np.histogram(reference_values, bins=bins, density=True)
            cur_hist, _ = np.histogram(current_values, bins=bins, density=True)
            
            # Normalize to probabilities
            ref_hist = ref_hist / (np.sum(ref_hist) + 1e-10)
            cur_hist = cur_hist / (np.sum(cur_hist) + 1e-10)
            
            # Add small epsilon to avoid log(0)
            epsilon = 1e-10
            ref_hist = ref_hist + epsilon
            cur_hist = cur_hist + epsilon
            
            # Renormalize
            ref_hist = ref_hist / np.sum(ref_hist)
            cur_hist = cur_hist / np.sum(cur_hist)
            
            # Calculate Jensen-Shannon divergence
            m = 0.5 * (ref_hist + cur_hist)
            js_div = 0.5 * stats.entropy(ref_hist, m) + 0.5 * stats.entropy(cur_hist, m)
            js_distance = np.sqrt(js_div)
            
            # Get thresholds
            thresholds = self._get_creator_thresholds(creator_type)
            
            # Map JS distance to drift severity (JS distance is between 0 and 1)
            if js_distance > 0.3:
                severity = DriftSeverity.CRITICAL_DRIFT
                strategy = AdaptationStrategy.RETRAIN_MODEL
            elif js_distance > 0.2:
                severity = DriftSeverity.HIGH_DRIFT
                strategy = AdaptationStrategy.UPDATE_FEATURES
            elif js_distance > 0.1:
                severity = DriftSeverity.MODERATE_DRIFT
                strategy = AdaptationStrategy.ADJUST_THRESHOLDS
            elif js_distance > 0.05:
                severity = DriftSeverity.LOW_DRIFT
                strategy = AdaptationStrategy.INCREMENTAL_LEARNING
            else:
                severity = DriftSeverity.NO_DRIFT
                strategy = AdaptationStrategy.NO_ACTION
            
            drift_detected = js_distance > 0.05
            
            return DriftDetectionResult(
                feature_name=feature_name,
                drift_detected=drift_detected,
                drift_severity=severity,
                drift_score=js_distance,
                detection_method=DriftDetectionMethod.JENSEN_SHANNON,
                p_value=None,  # JS doesn't provide p-value
                confidence_interval=None,
                timestamp=datetime.now(),
                adaptation_strategy=strategy,
                creator_type=creator_type,
                metadata={
                    "js_divergence": js_div,
                    "js_distance": js_distance,
                    "n_bins": n_bins
                }
            )
            
        except Exception as e:
            logger.error(f"Error in JS drift detection: {e}")
            return self._create_no_drift_result(feature_name, DriftDetectionMethod.JENSEN_SHANNON, creator_type)
    
    async def _detect_drift_psi(
        self,
        feature_name: str,
        reference_values: np.ndarray,
        current_values: np.ndarray,
        creator_type: Optional[CreatorType]
    ) -> DriftDetectionResult:
        """Detect drift using Population Stability Index (PSI)."""
        try:
            # Create decile-based bins from reference data
            percentiles = np.percentile(reference_values, np.arange(0, 101, 10))
            percentiles = np.unique(percentiles)  # Remove duplicates
            
            if len(percentiles) < 2:
                logger.warning(f"⚠️ Insufficient unique values for PSI calculation: {feature_name}")
                return self._create_no_drift_result(feature_name, DriftDetectionMethod.POPULATION_STABILITY_INDEX, creator_type)
            
            # Bin the data
            ref_counts, _ = np.histogram(reference_values, bins=percentiles)
            cur_counts, _ = np.histogram(current_values, bins=percentiles)
            
            # Convert to proportions
            ref_props = ref_counts / len(reference_values)
            cur_props = cur_counts / len(current_values)
            
            # Calculate PSI
            epsilon = 1e-10  # Small value to avoid log(0)
            ref_props = np.where(ref_props == 0, epsilon, ref_props)
            cur_props = np.where(cur_props == 0, epsilon, cur_props)
            
            psi = np.sum((cur_props - ref_props) * np.log(cur_props / ref_props))
            
            # Determine drift severity based on PSI thresholds
            if psi > 0.25:
                severity = DriftSeverity.CRITICAL_DRIFT
                strategy = AdaptationStrategy.RETRAIN_MODEL
            elif psi > 0.1:
                severity = DriftSeverity.HIGH_DRIFT
                strategy = AdaptationStrategy.UPDATE_FEATURES
            elif psi > 0.05:
                severity = DriftSeverity.MODERATE_DRIFT
                strategy = AdaptationStrategy.ADJUST_THRESHOLDS
            elif psi > 0.02:
                severity = DriftSeverity.LOW_DRIFT
                strategy = AdaptationStrategy.INCREMENTAL_LEARNING
            else:
                severity = DriftSeverity.NO_DRIFT
                strategy = AdaptationStrategy.NO_ACTION
            
            drift_detected = psi > 0.02
            
            return DriftDetectionResult(
                feature_name=feature_name,
                drift_detected=drift_detected,
                drift_severity=severity,
                drift_score=psi,
                detection_method=DriftDetectionMethod.POPULATION_STABILITY_INDEX,
                p_value=None,
                confidence_interval=None,
                timestamp=datetime.now(),
                adaptation_strategy=strategy,
                creator_type=creator_type,
                metadata={
                    "psi_value": psi,
                    "n_bins": len(percentiles) - 1,
                    "reference_proportions": ref_props.tolist(),
                    "current_proportions": cur_props.tolist()
                }
            )
            
        except Exception as e:
            logger.error(f"Error in PSI drift detection: {e}")
            return self._create_no_drift_result(feature_name, DriftDetectionMethod.POPULATION_STABILITY_INDEX, creator_type)
    
    async def _detect_drift_wasserstein(
        self,
        feature_name: str,
        reference_values: np.ndarray,
        current_values: np.ndarray,
        creator_type: Optional[CreatorType]
    ) -> DriftDetectionResult:
        """Detect drift using Wasserstein distance."""
        try:
            # Calculate Wasserstein distance (Earth Mover's Distance)
            wasserstein_dist = stats.wasserstein_distance(reference_values, current_values)
            
            # Normalize by the range of values
            value_range = max(np.max(reference_values), np.max(current_values)) - min(np.min(reference_values), np.min(current_values))
            normalized_distance = wasserstein_dist / (value_range + 1e-10)
            
            # Determine drift severity
            if normalized_distance > 0.2:
                severity = DriftSeverity.CRITICAL_DRIFT
                strategy = AdaptationStrategy.RETRAIN_MODEL
            elif normalized_distance > 0.1:
                severity = DriftSeverity.HIGH_DRIFT
                strategy = AdaptationStrategy.UPDATE_FEATURES
            elif normalized_distance > 0.05:
                severity = DriftSeverity.MODERATE_DRIFT
                strategy = AdaptationStrategy.ADJUST_THRESHOLDS
            elif normalized_distance > 0.02:
                severity = DriftSeverity.LOW_DRIFT
                strategy = AdaptationStrategy.INCREMENTAL_LEARNING
            else:
                severity = DriftSeverity.NO_DRIFT
                strategy = AdaptationStrategy.NO_ACTION
            
            drift_detected = normalized_distance > 0.02
            
            return DriftDetectionResult(
                feature_name=feature_name,
                drift_detected=drift_detected,
                drift_severity=severity,
                drift_score=normalized_distance,
                detection_method=DriftDetectionMethod.WASSERSTEIN_DISTANCE,
                p_value=None,
                confidence_interval=None,
                timestamp=datetime.now(),
                adaptation_strategy=strategy,
                creator_type=creator_type,
                metadata={
                    "wasserstein_distance": wasserstein_dist,
                    "normalized_distance": normalized_distance,
                    "value_range": value_range
                }
            )
            
        except Exception as e:
            logger.error(f"Error in Wasserstein drift detection: {e}")
            return self._create_no_drift_result(feature_name, DriftDetectionMethod.WASSERSTEIN_DISTANCE, creator_type)
    
    async def _detect_drift_chi_square(
        self,
        feature_name: str,
        reference_values: np.ndarray,
        current_values: np.ndarray,
        creator_type: Optional[CreatorType]
    ) -> DriftDetectionResult:
        """Detect drift using Chi-square test."""
        try:
            # Create bins for categorical comparison
            min_val = min(np.min(reference_values), np.min(current_values))
            max_val = max(np.max(reference_values), np.max(current_values))
            
            n_bins = min(20, int(np.sqrt(min(len(reference_values), len(current_values)))))
            bins = np.linspace(min_val, max_val, n_bins + 1)
            
            # Get observed frequencies
            ref_freq, _ = np.histogram(reference_values, bins=bins)
            cur_freq, _ = np.histogram(current_values, bins=bins)
            
            # Expected frequencies (proportional to reference)
            total_ref = np.sum(ref_freq)
            total_cur = np.sum(cur_freq)
            
            if total_ref == 0 or total_cur == 0:
                return self._create_no_drift_result(feature_name, DriftDetectionMethod.CHI_SQUARE, creator_type)
            
            expected_freq = ref_freq * (total_cur / total_ref)
            
            # Avoid division by zero
            mask = expected_freq > 0
            if np.sum(mask) < 2:
                return self._create_no_drift_result(feature_name, DriftDetectionMethod.CHI_SQUARE, creator_type)
            
            # Calculate chi-square statistic
            chi2_stat = np.sum((cur_freq[mask] - expected_freq[mask]) ** 2 / expected_freq[mask])
            degrees_of_freedom = np.sum(mask) - 1
            
            if degrees_of_freedom <= 0:
                return self._create_no_drift_result(feature_name, DriftDetectionMethod.CHI_SQUARE, creator_type)
            
            p_value = 1 - stats.chi2.cdf(chi2_stat, degrees_of_freedom)
            
            # Get thresholds
            thresholds = self._get_creator_thresholds(creator_type)
            sensitivity_threshold = thresholds["sensitivity_threshold"]
            critical_threshold = thresholds["critical_threshold"]
            
            # Determine drift severity
            drift_detected = p_value < sensitivity_threshold
            
            if p_value < critical_threshold:
                severity = DriftSeverity.CRITICAL_DRIFT
                strategy = AdaptationStrategy.RETRAIN_MODEL
            elif p_value < critical_threshold * 2:
                severity = DriftSeverity.HIGH_DRIFT
                strategy = AdaptationStrategy.UPDATE_FEATURES
            elif p_value < sensitivity_threshold:
                severity = DriftSeverity.MODERATE_DRIFT
                strategy = AdaptationStrategy.ADJUST_THRESHOLDS
            elif p_value < sensitivity_threshold * 2:
                severity = DriftSeverity.LOW_DRIFT
                strategy = AdaptationStrategy.INCREMENTAL_LEARNING
            else:
                severity = DriftSeverity.NO_DRIFT
                strategy = AdaptationStrategy.NO_ACTION
            
            return DriftDetectionResult(
                feature_name=feature_name,
                drift_detected=drift_detected,
                drift_severity=severity,
                drift_score=chi2_stat,
                detection_method=DriftDetectionMethod.CHI_SQUARE,
                p_value=p_value,
                confidence_interval=None,
                timestamp=datetime.now(),
                adaptation_strategy=strategy,
                creator_type=creator_type,
                metadata={
                    "chi2_statistic": chi2_stat,
                    "degrees_of_freedom": degrees_of_freedom,
                    "n_bins": n_bins
                }
            )
            
        except Exception as e:
            logger.error(f"Error in Chi-square drift detection: {e}")
            return self._create_no_drift_result(feature_name, DriftDetectionMethod.CHI_SQUARE, creator_type)
    
    async def _detect_drift_statistical(
        self,
        feature_name: str,
        reference_values: np.ndarray,
        current_values: np.ndarray,
        creator_type: Optional[CreatorType]
    ) -> DriftDetectionResult:
        """Detect drift using comprehensive statistical distance."""
        try:
            # Calculate multiple statistical measures
            ref_stats = self._calculate_feature_statistics(reference_values)
            cur_stats = self._calculate_feature_statistics(current_values)
            
            # Calculate normalized differences for key statistics
            statistical_distances = {}
            
            for stat_name in ['mean', 'std', 'median', 'skewness', 'kurtosis']:
                if stat_name in ref_stats and stat_name in cur_stats:
                    ref_val = ref_stats[stat_name]
                    cur_val = cur_stats[stat_name]
                    
                    # Normalize by reference value (with protection against division by zero)
                    if abs(ref_val) > 1e-10:
                        normalized_diff = abs(cur_val - ref_val) / abs(ref_val)
                    else:
                        normalized_diff = abs(cur_val - ref_val)
                    
                    statistical_distances[stat_name] = normalized_diff
            
            # Weight different statistics based on importance
            weights = {
                'mean': 0.3,
                'std': 0.25,
                'median': 0.2,
                'skewness': 0.15,
                'kurtosis': 0.1
            }
            
            # Calculate weighted statistical distance
            weighted_distance = sum(
                weights.get(stat, 0.1) * dist 
                for stat, dist in statistical_distances.items()
            )
            
            # Get creator-specific adjustments
            thresholds = self._get_creator_thresholds(creator_type)
            adjustment = thresholds.get("temporal_weight", 1.0)
            adjusted_distance = weighted_distance * adjustment
            
            # Determine drift severity
            if adjusted_distance > 0.5:
                severity = DriftSeverity.CRITICAL_DRIFT
                strategy = AdaptationStrategy.RETRAIN_MODEL
            elif adjusted_distance > 0.3:
                severity = DriftSeverity.HIGH_DRIFT
                strategy = AdaptationStrategy.UPDATE_FEATURES
            elif adjusted_distance > 0.15:
                severity = DriftSeverity.MODERATE_DRIFT
                strategy = AdaptationStrategy.ADJUST_THRESHOLDS
            elif adjusted_distance > 0.05:
                severity = DriftSeverity.LOW_DRIFT
                strategy = AdaptationStrategy.INCREMENTAL_LEARNING
            else:
                severity = DriftSeverity.NO_DRIFT
                strategy = AdaptationStrategy.NO_ACTION
            
            drift_detected = adjusted_distance > 0.05
            
            return DriftDetectionResult(
                feature_name=feature_name,
                drift_detected=drift_detected,
                drift_severity=severity,
                drift_score=adjusted_distance,
                detection_method=DriftDetectionMethod.STATISTICAL_DISTANCE,
                p_value=None,
                confidence_interval=None,
                timestamp=datetime.now(),
                adaptation_strategy=strategy,
                creator_type=creator_type,
                metadata={
                    "statistical_distances": statistical_distances,
                    "weighted_distance": weighted_distance,
                    "adjustment_factor": adjustment,
                    "reference_statistics": ref_stats,
                    "current_statistics": cur_stats
                }
            )
            
        except Exception as e:
            logger.error(f"Error in statistical drift detection: {e}")
            return self._create_no_drift_result(feature_name, DriftDetectionMethod.STATISTICAL_DISTANCE, creator_type)
    
    def _get_creator_thresholds(self, creator_type: Optional[CreatorType]) -> Dict[str, float]:
        """Get creator-specific thresholds or default values."""
        if creator_type and creator_type in self.creator_thresholds:
            return self.creator_thresholds[creator_type]
        else:
            return {
                "sensitivity_threshold": 0.05,
                "critical_threshold": 0.01,
                "temporal_weight": 1.0,
                "engagement_weight": 1.0,
                "seasonal_adjustment": 1.0
            }
    
    def _create_no_drift_result(
        self,
        feature_name: str,
        detection_method: DriftDetectionMethod,
        creator_type: Optional[CreatorType]
    ) -> DriftDetectionResult:
        """Create a no-drift result for error cases."""
        return DriftDetectionResult(
            feature_name=feature_name,
            drift_detected=False,
            drift_severity=DriftSeverity.NO_DRIFT,
            drift_score=0.0,
            detection_method=detection_method,
            p_value=1.0,
            confidence_interval=None,
            timestamp=datetime.now(),
            adaptation_strategy=AdaptationStrategy.NO_ACTION,
            creator_type=creator_type,
            metadata={"error": "Insufficient data or calculation error"}
        )
    
    async def _apply_adaptation_strategy(self, drift_result: DriftDetectionResult):
        """Apply the recommended adaptation strategy."""
        logger.info(f"🔧 Applying adaptation strategy: {drift_result.adaptation_strategy.value}")
        
        adaptation_action = {
            "timestamp": datetime.now(),
            "feature_name": drift_result.feature_name,
            "drift_severity": drift_result.drift_severity.value,
            "strategy": drift_result.adaptation_strategy.value,
            "creator_type": drift_result.creator_type.value if drift_result.creator_type else None,
            "actions_taken": []
        }
        
        if drift_result.adaptation_strategy == AdaptationStrategy.RETRAIN_MODEL:
            # Signal for model retraining
            adaptation_action["actions_taken"].append("Model retraining triggered")
            await self._trigger_model_retraining(drift_result)
            
        elif drift_result.adaptation_strategy == AdaptationStrategy.UPDATE_FEATURES:
            # Update feature preprocessing or selection
            adaptation_action["actions_taken"].append("Feature update initiated")
            await self._update_feature_processing(drift_result)
            
        elif drift_result.adaptation_strategy == AdaptationStrategy.ADJUST_THRESHOLDS:
            # Adjust detection thresholds
            adaptation_action["actions_taken"].append("Thresholds adjusted")
            await self._adjust_detection_thresholds(drift_result)
            
        elif drift_result.adaptation_strategy == AdaptationStrategy.INCREMENTAL_LEARNING:
            # Trigger incremental model update
            adaptation_action["actions_taken"].append("Incremental learning initiated")
            await self._trigger_incremental_learning(drift_result)
            
        elif drift_result.adaptation_strategy == AdaptationStrategy.FEATURE_SELECTION:
            # Re-evaluate feature importance
            adaptation_action["actions_taken"].append("Feature selection review")
            await self._review_feature_selection(drift_result)
        
        # Store adaptation history
        self.adaptation_history.append(adaptation_action)
        
        logger.info(f"✅ Adaptation strategy applied: {len(adaptation_action['actions_taken'])} actions taken")
    
    async def _trigger_model_retraining(self, drift_result: DriftDetectionResult):
        """Trigger model retraining process."""
        # In a real implementation, this would interface with the training pipeline
        logger.info(f"🔄 Model retraining triggered for feature: {drift_result.feature_name}")
        
        # Update reference snapshot with current data
        if drift_result.feature_name in self.current_snapshots:
            self.reference_snapshots[drift_result.feature_name] = self.current_snapshots[drift_result.feature_name]
    
    async def _update_feature_processing(self, drift_result: DriftDetectionResult):
        """Update feature processing pipeline."""
        logger.info(f"🔧 Feature processing update for: {drift_result.feature_name}")
        
        # This could involve updating normalization parameters, feature transformations, etc.
        pass
    
    async def _adjust_detection_thresholds(self, drift_result: DriftDetectionResult):
        """Adjust drift detection thresholds based on observed patterns."""
        logger.info(f"⚙️ Adjusting detection thresholds for: {drift_result.feature_name}")
        
        # Analyze recent drift history for this feature
        recent_results = [
            r for r in self.drift_history[-50:]  # Last 50 results
            if r.feature_name == drift_result.feature_name
        ]
        
        if len(recent_results) >= 5:
            # Calculate adjustment based on false positive rate
            false_positives = sum(1 for r in recent_results if r.drift_detected and r.drift_severity == DriftSeverity.LOW_DRIFT)
            false_positive_rate = false_positives / len(recent_results)
            
            # Adjust thresholds if too many false positives
            if false_positive_rate > 0.3 and drift_result.creator_type:
                creator_threshold = self.creator_thresholds.get(drift_result.creator_type, {})
                creator_threshold["sensitivity_threshold"] *= 1.1  # Make less sensitive
                logger.info(f"📈 Increased sensitivity threshold due to high false positive rate")
    
    async def _trigger_incremental_learning(self, drift_result: DriftDetectionResult):
        """Trigger incremental learning process."""
        logger.info(f"📚 Incremental learning triggered for: {drift_result.feature_name}")
        
        # This would interface with online learning algorithms
        pass
    
    async def _review_feature_selection(self, drift_result: DriftDetectionResult):
        """Review and potentially update feature selection."""
        logger.info(f"🔍 Feature selection review for: {drift_result.feature_name}")
        
        # Analyze feature importance and stability
        pass
    
    async def detect_multi_feature_drift(
        self,
        feature_data: Dict[str, np.ndarray],
        detection_method: DriftDetectionMethod = DriftDetectionMethod.KOLMOGOROV_SMIRNOV,
        creator_type: Optional[CreatorType] = None
    ) -> List[DriftDetectionResult]:
        """
        Detect drift across multiple features simultaneously.
        
        Args:
            feature_data: Dictionary mapping feature names to current values
            detection_method: Method to use for drift detection
            creator_type: Creator type for specialized analysis
            
        Returns:
            List of drift detection results for all features
        """
        logger.info(f"🔍 Multi-feature drift detection for {len(feature_data)} features")
        
        # Create detection tasks
        tasks = []
        for feature_name, feature_values in feature_data.items():
            tasks.append(
                self.detect_drift(feature_name, feature_values, detection_method, creator_type)
            )
        
        # Execute detection in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and compile results
        valid_results = []
        for result in results:
            if isinstance(result, DriftDetectionResult):
                valid_results.append(result)
            else:
                logger.error(f"Error in multi-feature drift detection: {result}")
        
        # Analyze overall drift pattern
        await self._analyze_multi_feature_drift_pattern(valid_results, creator_type)
        
        logger.info(f"✅ Multi-feature drift detection completed: {len(valid_results)} features analyzed")
        return valid_results
    
    async def _analyze_multi_feature_drift_pattern(
        self,
        drift_results: List[DriftDetectionResult],
        creator_type: Optional[CreatorType]
    ):
        """Analyze patterns across multiple feature drift results."""
        if not drift_results:
            return
        
        # Count drift by severity
        severity_counts = defaultdict(int)
        for result in drift_results:
            severity_counts[result.drift_severity] += 1
        
        # Check for systemic drift
        total_features = len(drift_results)
        drifted_features = sum(1 for r in drift_results if r.drift_detected)
        drift_rate = drifted_features / total_features
        
        if drift_rate > 0.5:
            logger.warning(f"🚨 Systemic drift detected: {drift_rate:.1%} of features showing drift")
            
            # This could trigger more aggressive adaptation strategies
            if creator_type:
                await self._handle_systemic_drift(creator_type, drift_results)
        
        logger.info(f"📊 Multi-feature drift analysis: {drift_rate:.1%} drift rate")
    
    async def _handle_systemic_drift(
        self,
        creator_type: CreatorType,
        drift_results: List[DriftDetectionResult]
    ):
        """Handle systemic drift across multiple features."""
        logger.info(f"🔧 Handling systemic drift for {creator_type.value}")
        
        # This could trigger comprehensive model updates, data pipeline reviews, etc.
        systemic_adaptation = {
            "timestamp": datetime.now(),
            "creator_type": creator_type.value,
            "affected_features": [r.feature_name for r in drift_results if r.drift_detected],
            "drift_rate": sum(1 for r in drift_results if r.drift_detected) / len(drift_results),
            "recommended_actions": [
                "Review data collection pipeline",
                "Consider model architecture updates", 
                "Evaluate feature engineering process",
                "Implement enhanced monitoring"
            ]
        }
        
        self.adaptation_history.append(systemic_adaptation)
    
    async def generate_drift_report(
        self,
        time_window_hours: int = 24,
        creator_type: Optional[CreatorType] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive drift detection report.
        
        Args:
            time_window_hours: Time window for analysis
            creator_type: Filter by specific creator type
            
        Returns:
            Comprehensive drift report
        """
        logger.info("📊 Generating drift detection report")
        
        # Filter results by time window
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        recent_results = [
            r for r in self.drift_history
            if r.timestamp >= cutoff_time
        ]
        
        # Filter by creator type if specified
        if creator_type:
            recent_results = [
                r for r in recent_results
                if r.creator_type == creator_type
            ]
        
        if not recent_results:
            return {
                "error": "No drift detection results found for specified criteria",
                "time_window_hours": time_window_hours,
                "creator_type": creator_type.value if creator_type else None
            }
        
        # Analyze drift patterns
        drift_summary = self._analyze_drift_patterns(recent_results)
        
        # Analyze adaptation effectiveness
        adaptation_analysis = self._analyze_adaptation_effectiveness()
        
        # Generate recommendations
        recommendations = await self._generate_drift_recommendations(recent_results, creator_type)
        
        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "time_window_hours": time_window_hours,
                "creator_type": creator_type.value if creator_type else None,
                "total_detections": len(recent_results),
                "unique_features": len(set(r.feature_name for r in recent_results))
            },
            "drift_summary": drift_summary,
            "adaptation_analysis": adaptation_analysis,
            "feature_analysis": self._analyze_feature_drift_patterns(recent_results),
            "performance_metrics": self._calculate_detection_performance(recent_results),
            "recommendations": recommendations,
            "detailed_results": [
                {
                    "feature_name": r.feature_name,
                    "drift_detected": r.drift_detected,
                    "drift_severity": r.drift_severity.value,
                    "drift_score": r.drift_score,
                    "detection_method": r.detection_method.value,
                    "adaptation_strategy": r.adaptation_strategy.value,
                    "timestamp": r.timestamp.isoformat(),
                    "p_value": r.p_value
                }
                for r in recent_results[-50:]  # Last 50 results
            ]
        }
        
        logger.info(f"✅ Drift report generated: {len(recent_results)} detections analyzed")
        return report
    
    def _analyze_drift_patterns(self, results: List[DriftDetectionResult]) -> Dict[str, Any]:
        """Analyze patterns in drift detection results."""
        if not results:
            return {}
        
        # Count by severity
        severity_counts = defaultdict(int)
        method_counts = defaultdict(int)
        strategy_counts = defaultdict(int)
        
        for result in results:
            severity_counts[result.drift_severity.value] += 1
            method_counts[result.detection_method.value] += 1
            strategy_counts[result.adaptation_strategy.value] += 1
        
        # Calculate rates
        total_results = len(results)
        drift_rate = sum(1 for r in results if r.drift_detected) / total_results
        
        return {
            "overall_drift_rate": drift_rate,
            "severity_distribution": dict(severity_counts),
            "method_usage": dict(method_counts),
            "strategy_distribution": dict(strategy_counts),
            "average_drift_score": np.mean([r.drift_score for r in results]),
            "max_drift_score": max(r.drift_score for r in results),
            "min_drift_score": min(r.drift_score for r in results)
        }
    
    def _analyze_adaptation_effectiveness(self) -> Dict[str, Any]:
        """Analyze effectiveness of adaptation strategies."""
        if not self.adaptation_history:
            return {"message": "No adaptation history available"}
        
        recent_adaptations = self.adaptation_history[-20:]  # Last 20 adaptations
        
        strategy_counts = defaultdict(int)
        for adaptation in recent_adaptations:
            strategy = adaptation.get("strategy", "unknown")
            strategy_counts[strategy] += 1
        
        return {
            "total_adaptations": len(recent_adaptations),
            "strategy_usage": dict(strategy_counts),
            "adaptation_frequency": len(recent_adaptations) / max(1, len(self.drift_history[-100:])),
            "most_common_strategy": max(strategy_counts.items(), key=lambda x: x[1])[0] if strategy_counts else "none"
        }
    
    def _analyze_feature_drift_patterns(self, results: List[DriftDetectionResult]) -> Dict[str, Any]:
        """Analyze drift patterns by feature."""
        feature_analysis = defaultdict(lambda: {
            "detection_count": 0,
            "drift_count": 0,
            "avg_drift_score": 0.0,
            "max_severity": "no_drift",
            "most_common_method": "unknown"
        })
        
        for result in results:
            feature_name = result.feature_name
            analysis = feature_analysis[feature_name]
            
            analysis["detection_count"] += 1
            if result.drift_detected:
                analysis["drift_count"] += 1
            
            # Update average drift score
            current_avg = analysis["avg_drift_score"]
            current_count = analysis["detection_count"]
            analysis["avg_drift_score"] = (current_avg * (current_count - 1) + result.drift_score) / current_count
            
            # Update max severity
            severity_order = {
                "no_drift": 0,
                "low_drift": 1,
                "moderate_drift": 2,
                "high_drift": 3,
                "critical_drift": 4
            }
            
            current_severity_level = severity_order.get(analysis["max_severity"], 0)
            new_severity_level = severity_order.get(result.drift_severity.value, 0)
            
            if new_severity_level > current_severity_level:
                analysis["max_severity"] = result.drift_severity.value
        
        return dict(feature_analysis)
    
    def _calculate_detection_performance(self, results: List[DriftDetectionResult]) -> Dict[str, Any]:
        """Calculate performance metrics for drift detection."""
        if not results:
            return {}
        
        # Calculate basic performance metrics
        total_detections = len(results)
        positive_detections = sum(1 for r in results if r.drift_detected)
        
        # Method performance
        method_performance = defaultdict(lambda: {"total": 0, "detected": 0})
        
        for result in results:
            method = result.detection_method.value
            method_performance[method]["total"] += 1
            if result.drift_detected:
                method_performance[method]["detected"] += 1
        
        # Calculate detection rates by method
        method_rates = {}
        for method, stats in method_performance.items():
            if stats["total"] > 0:
                method_rates[method] = stats["detected"] / stats["total"]
        
        return {
            "total_detections": total_detections,
            "positive_detection_rate": positive_detections / total_detections,
            "method_performance": dict(method_performance),
            "method_detection_rates": method_rates,
            "avg_response_time": "immediate",  # Since detection is real-time
            "false_positive_estimate": self._estimate_false_positive_rate(results)
        }
    
    def _estimate_false_positive_rate(self, results: List[DriftDetectionResult]) -> float:
        """Estimate false positive rate based on drift patterns."""
        # This is a simplified estimation
        # In practice, would require ground truth data
        
        if not results:
            return 0.0
        
        # Assume low-severity drifts that don't lead to adaptations might be false positives
        potential_false_positives = sum(
            1 for r in results 
            if r.drift_detected 
            and r.drift_severity == DriftSeverity.LOW_DRIFT
            and r.adaptation_strategy == AdaptationStrategy.NO_ACTION
        )
        
        total_positive_detections = sum(1 for r in results if r.drift_detected)
        
        if total_positive_detections == 0:
            return 0.0
        
        return potential_false_positives / total_positive_detections
    
    async def _generate_drift_recommendations(
        self,
        results: List[DriftDetectionResult],
        creator_type: Optional[CreatorType]
    ) -> List[str]:
        """Generate actionable recommendations based on drift analysis."""
        recommendations = []
        
        if not results:
            return ["No drift detections to analyze"]
        
        # Analyze drift frequency
        drift_rate = sum(1 for r in results if r.drift_detected) / len(results)
        
        if drift_rate > 0.3:
            recommendations.append("🚨 High drift rate detected - review data collection pipeline")
        elif drift_rate > 0.1:
            recommendations.append("⚠️ Moderate drift rate - consider more frequent model updates")
        
        # Analyze severity distribution
        critical_drifts = sum(1 for r in results if r.drift_severity == DriftSeverity.CRITICAL_DRIFT)
        if critical_drifts > 0:
            recommendations.append(f"🔴 {critical_drifts} critical drift(s) detected - immediate model retraining recommended")
        
        # Feature-specific recommendations
        feature_drift_counts = defaultdict(int)
        for result in results:
            if result.drift_detected:
                feature_drift_counts[result.feature_name] += 1
        
        problematic_features = [f for f, count in feature_drift_counts.items() if count >= 3]
        if problematic_features:
            recommendations.append(f"🔧 Problematic features detected: {', '.join(problematic_features[:3])} - consider feature engineering review")
        
        # Creator-specific recommendations
        if creator_type:
            creator_name = creator_type.value
            
            if creator_type == CreatorType.INFLUENCER and drift_rate > 0.2:
                recommendations.append(f"📱 {creator_name.title()} content shows high drift - consider trend-adaptive features")
            elif creator_type == CreatorType.MUSICIAN and drift_rate > 0.15:
                recommendations.append(f"🎵 {creator_name.title()} audio features drifting - review audio processing pipeline")
            elif creator_type == CreatorType.PHOTOGRAPHER and drift_rate > 0.25:
                recommendations.append(f"📸 {creator_name.title()} visual features unstable - consider seasonal adjustments")
        
        # Method effectiveness recommendations
        method_counts = defaultdict(int)
        for result in results:
            method_counts[result.detection_method.value] += 1
        
        if len(method_counts) == 1:
            recommendations.append("🔄 Consider using multiple detection methods for better coverage")
        
        # Adaptation recommendations
        adaptations_needed = sum(1 for r in results if r.adaptation_strategy != AdaptationStrategy.NO_ACTION)
        if adaptations_needed > len(results) * 0.2:
            recommendations.append("⚙️ High adaptation frequency - review detection thresholds")
        
        return recommendations

# Export main class
__all__ = ['FeatureDriftDetector', 'DriftDetectionMethod', 'DriftSeverity', 'CreatorType', 'AdaptationStrategy', 'FeatureSnapshot', 'DriftDetectionResult', 'DriftDetectionConfig']

if __name__ == "__main__":
    # Test the feature drift detector
    async def test_feature_drift_detector():
        detector = FeatureDriftDetector()
        
        # Create reference data
        np.random.seed(42)
        reference_data = np.random.normal(0, 1, 1000)
        
        # Add reference snapshot
        await detector.add_reference_snapshot(
            feature_name="test_feature",
            feature_values=reference_data,
            creator_type=CreatorType.MUSICIAN
        )
        
        # Test different types of drift
        test_scenarios = [
            ("no_drift", np.random.normal(0, 1, 500)),
            ("location_drift", np.random.normal(0.5, 1, 500)),
            ("scale_drift", np.random.normal(0, 1.5, 500)),
            ("distribution_drift", np.random.exponential(1, 500))
        ]
        
        print("🔍 Testing Feature Drift Detection:")
        print("-" * 50)
        
        for scenario_name, current_data in test_scenarios:
            print(f"\n📊 Scenario: {scenario_name}")
            
            # Test multiple detection methods
            methods = [
                DriftDetectionMethod.KOLMOGOROV_SMIRNOV,
                DriftDetectionMethod.JENSEN_SHANNON,
                DriftDetectionMethod.POPULATION_STABILITY_INDEX
            ]
            
            for method in methods:
                result = await detector.detect_drift(
                    feature_name="test_feature",
                    current_values=current_data,
                    detection_method=method,
                    creator_type=CreatorType.MUSICIAN
                )
                
                print(f"  {method.value}:")
                print(f"    Drift detected: {result.drift_detected}")
                print(f"    Severity: {result.drift_severity.value}")
                print(f"    Score: {result.drift_score:.4f}")
                print(f"    Strategy: {result.adaptation_strategy.value}")
        
        # Test multi-feature drift detection
        print(f"\n🔍 Multi-feature drift detection:")
        
        feature_data = {
            "feature_1": np.random.normal(0, 1, 500),
            "feature_2": np.random.normal(0.3, 1.2, 500),  # Slight drift
            "feature_3": np.random.exponential(1, 500)      # Strong drift
        }
        
        # Add reference snapshots for all features
        for feature_name in feature_data.keys():
            ref_data = np.random.normal(0, 1, 1000)
            await detector.add_reference_snapshot(feature_name, ref_data, CreatorType.MUSICIAN)
        
        multi_results = await detector.detect_multi_feature_drift(
            feature_data=feature_data,
            creator_type=CreatorType.MUSICIAN
        )
        
        for result in multi_results:
            print(f"  {result.feature_name}: {result.drift_severity.value} ({result.drift_score:.4f})")
        
        # Generate comprehensive report
        print(f"\n📊 Generating drift report...")
        report = await detector.generate_drift_report(
            time_window_hours=24,
            creator_type=CreatorType.MUSICIAN
        )
        
        print(f"Report summary:")
        print(f"  Total detections: {report['report_metadata']['total_detections']}")
        print(f"  Unique features: {report['report_metadata']['unique_features']}")
        print(f"  Overall drift rate: {report['drift_summary']['overall_drift_rate']:.2%}")
        print(f"  Recommendations: {len(report['recommendations'])}")
        
        print("\n✅ FeatureDriftDetector test completed successfully!")
    
    # Run test
    asyncio.run(test_feature_drift_detector())