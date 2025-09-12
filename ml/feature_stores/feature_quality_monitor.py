#!/usr/bin/env python3
"""
🚀 **Feature Quality Monitor - Enterprise ML Feature Validation**

**Author:** Fahed Mlaiel (mlaiel@live.de) - ML Engineer  
**Copyright:** © 2025 Fahed Mlaiel. All rights reserved.  
**Version:** 1.0.0  
**Created:** January 2025

**⚠️ WARNING:** This code is proprietary and confidential. Unauthorized use, reproduction, 
or distribution without explicit written permission from Fahed Mlaiel is strictly prohibited.

---

## 🎯 **ROLE: ML ENGINEER - ALGORITHMIC EXCELLENCE MASTERY**

Enterprise-grade feature quality monitoring with real-time validation,
statistical analysis, drift detection, and creator-specific quality metrics.
"""

import asyncio
import json
import time
import warnings
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import mutual_info_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib

from prometheus_client import Counter, Histogram, Gauge

# Monitoring metrics
feature_quality_score = Gauge('feature_quality_score', 'Feature quality score', ['feature_name', 'creator_type'])
feature_drift_detected = Counter('feature_drift_detected_total', 'Feature drift detections', ['feature_name', 'drift_type'])
feature_anomalies = Counter('feature_anomalies_total', 'Feature anomalies detected', ['feature_name', 'anomaly_type'])

class QualityMetric(Enum):
    """Feature quality metrics"""
    COMPLETENESS = "completeness"
    VALIDITY = "validity"
    CONSISTENCY = "consistency"
    ACCURACY = "accuracy"
    UNIQUENESS = "uniqueness"
    STABILITY = "stability"
    DISTRIBUTION = "distribution"
    CORRELATION = "correlation"

class FeatureType(Enum):
    """Feature data types"""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    BOOLEAN = "boolean"
    TEXT = "text"
    DATETIME = "datetime"
    BINARY = "binary"
    ORDINAL = "ordinal"

class CreatorType(Enum):
    """Creator specialization for feature monitoring"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    GENERIC = "generic"

@dataclass
class QualityThreshold:
    """Quality thresholds for feature validation"""
    metric: QualityMetric
    min_score: float
    max_score: float = 1.0
    critical_threshold: float = 0.5
    warning_threshold: float = 0.7

@dataclass
class FeatureProfile:
    """Statistical profile of a feature"""
    feature_name: str
    feature_type: FeatureType
    statistics: Dict[str, Any]
    quality_scores: Dict[QualityMetric, float]
    thresholds: List[QualityThreshold]
    created_at: datetime
    updated_at: datetime
    sample_count: int

@dataclass
class QualityReport:
    """Feature quality assessment report"""
    feature_name: str
    overall_score: float
    metric_scores: Dict[QualityMetric, float]
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    severity: str  # 'critical', 'warning', 'info'
    timestamp: datetime
    creator_type: CreatorType

class FeatureQualityMonitor:
    """
    🚀 **Enterprise Feature Quality Monitor**
    
    **ML Engineer Role:** Advanced feature validation and monitoring
    - Real-time feature quality assessment with statistical analysis
    - Multi-dimensional quality metrics (completeness, validity, consistency)
    - Creator-specific quality thresholds and validation rules
    - Automated anomaly detection and drift monitoring
    - Actionable quality reports and recommendations
    - Integration with feature stores and ML pipelines
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Feature profiles storage
        self.feature_profiles: Dict[str, FeatureProfile] = {}
        
        # Quality thresholds by creator type
        self.creator_thresholds = {
            CreatorType.MUSICIAN: {
                QualityMetric.COMPLETENESS: QualityThreshold(QualityMetric.COMPLETENESS, 0.95),
                QualityMetric.VALIDITY: QualityThreshold(QualityMetric.VALIDITY, 0.98),
                QualityMetric.STABILITY: QualityThreshold(QualityMetric.STABILITY, 0.90),
                QualityMetric.CORRELATION: QualityThreshold(QualityMetric.CORRELATION, 0.80)
            },
            CreatorType.PHOTOGRAPHER: {
                QualityMetric.COMPLETENESS: QualityThreshold(QualityMetric.COMPLETENESS, 0.98),
                QualityMetric.VALIDITY: QualityThreshold(QualityMetric.VALIDITY, 0.99),
                QualityMetric.CONSISTENCY: QualityThreshold(QualityMetric.CONSISTENCY, 0.95),
                QualityMetric.DISTRIBUTION: QualityThreshold(QualityMetric.DISTRIBUTION, 0.85)
            },
            CreatorType.BLOGGER: {
                QualityMetric.COMPLETENESS: QualityThreshold(QualityMetric.COMPLETENESS, 0.92),
                QualityMetric.VALIDITY: QualityThreshold(QualityMetric.VALIDITY, 0.96),
                QualityMetric.UNIQUENESS: QualityThreshold(QualityMetric.UNIQUENESS, 0.85),
                QualityMetric.ACCURACY: QualityThreshold(QualityMetric.ACCURACY, 0.90)
            }
        }
        
        # Statistical tests configuration
        self.statistical_tests = {
            'normality': ['shapiro', 'kolmogorov_smirnov', 'anderson'],
            'stationarity': ['adf', 'kpss'],
            'independence': ['ljung_box', 'durbin_watson'],
            'outliers': ['zscore', 'iqr', 'isolation_forest']
        }
        
        # Alert thresholds
        self.alert_config = config.get('alerts', {
            'quality_degradation_threshold': 0.1,
            'drift_significance_level': 0.05,
            'anomaly_detection_sensitivity': 0.95
        })
        
        # History storage for trend analysis
        self.quality_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Creator-specific feature importance weights
        self.creator_feature_weights = {
            CreatorType.MUSICIAN: {
                'audio_features': 1.5,
                'engagement_metrics': 1.2,
                'temporal_patterns': 1.3,
                'content_features': 1.0
            },
            CreatorType.PHOTOGRAPHER: {
                'visual_features': 1.5,
                'aesthetic_scores': 1.4,
                'technical_metadata': 1.2,
                'engagement_metrics': 1.1
            },
            CreatorType.BLOGGER: {
                'text_features': 1.5,
                'seo_metrics': 1.4,
                'readability_scores': 1.3,
                'engagement_metrics': 1.2
            }
        }
    
    async def monitor_features(
        self,
        features: Dict[str, Any],
        creator_type: CreatorType = CreatorType.GENERIC,
        feature_types: Optional[Dict[str, FeatureType]] = None,
        custom_thresholds: Optional[Dict[str, QualityThreshold]] = None
    ) -> List[QualityReport]:
        """
        Monitor feature quality with comprehensive validation
        
        **ML Engineer Expertise:**
        - Multi-dimensional quality assessment
        - Statistical validation and testing
        - Creator-specific quality standards
        - Real-time monitoring and alerting
        """
        quality_reports = []
        
        for feature_name, feature_data in features.items():
            try:
                # Determine feature type
                feature_type = self._infer_feature_type(feature_data, feature_types, feature_name)
                
                # Get quality thresholds
                thresholds = self._get_quality_thresholds(feature_name, creator_type, custom_thresholds)
                
                # Calculate quality metrics
                quality_scores = await self._calculate_quality_metrics(
                    feature_name, feature_data, feature_type, creator_type
                )
                
                # Generate quality report
                report = self._generate_quality_report(
                    feature_name, quality_scores, thresholds, creator_type
                )
                
                quality_reports.append(report)
                
                # Update feature profile
                await self._update_feature_profile(
                    feature_name, feature_type, feature_data, quality_scores, thresholds
                )
                
                # Update metrics
                feature_quality_score.labels(
                    feature_name=feature_name,
                    creator_type=creator_type.value
                ).set(report.overall_score)
                
            except Exception as e:
                self.logger.error(f"Error monitoring feature {feature_name}: {e}")
                
                # Create error report
                error_report = QualityReport(
                    feature_name=feature_name,
                    overall_score=0.0,
                    metric_scores={},
                    issues=[{
                        'type': 'processing_error',
                        'message': str(e),
                        'severity': 'critical'
                    }],
                    recommendations=[f"Check feature data format for {feature_name}"],
                    severity='critical',
                    timestamp=datetime.utcnow(),
                    creator_type=creator_type
                )
                quality_reports.append(error_report)
        
        return quality_reports
    
    def _infer_feature_type(
        self,
        feature_data: Any,
        feature_types: Optional[Dict[str, FeatureType]],
        feature_name: str
    ) -> FeatureType:
        """Infer feature type from data"""
        if feature_types and feature_name in feature_types:
            return feature_types[feature_name]
        
        # Convert to pandas Series for analysis
        if not isinstance(feature_data, (pd.Series, np.ndarray, list)):
            feature_data = [feature_data]
        
        series = pd.Series(feature_data)
        
        # Check for datetime
        if series.dtype == 'datetime64[ns]' or feature_name.lower() in ['timestamp', 'date', 'time']:
            return FeatureType.DATETIME
        
        # Check for boolean
        if series.dtype == 'bool' or set(series.dropna().unique()).issubset({True, False, 1, 0}):
            return FeatureType.BOOLEAN
        
        # Check for numerical
        if pd.api.types.is_numeric_dtype(series):
            # Check if binary (0/1 or small integer range)
            unique_values = series.dropna().unique()
            if len(unique_values) == 2 and set(unique_values).issubset({0, 1}):
                return FeatureType.BINARY
            elif len(unique_values) <= 10 and all(isinstance(x, int) for x in unique_values):
                return FeatureType.ORDINAL
            else:
                return FeatureType.NUMERICAL
        
        # Check for text
        if series.dtype == 'object':
            # Sample some values to check if they're text
            sample_values = series.dropna().head(100)
            avg_length = sample_values.astype(str).str.len().mean()
            
            if avg_length > 50:  # Likely text content
                return FeatureType.TEXT
            else:
                return FeatureType.CATEGORICAL
        
        return FeatureType.CATEGORICAL  # Default
    
    def _get_quality_thresholds(
        self,
        feature_name: str,
        creator_type: CreatorType,
        custom_thresholds: Optional[Dict[str, QualityThreshold]]
    ) -> List[QualityThreshold]:
        """Get quality thresholds for feature"""
        thresholds = []
        
        # Use custom thresholds if provided
        if custom_thresholds and feature_name in custom_thresholds:
            thresholds.append(custom_thresholds[feature_name])
        
        # Use creator-specific thresholds
        creator_thresholds = self.creator_thresholds.get(creator_type, {})
        thresholds.extend(creator_thresholds.values())
        
        # Default thresholds if none specified
        if not thresholds:
            default_thresholds = [
                QualityThreshold(QualityMetric.COMPLETENESS, 0.90),
                QualityThreshold(QualityMetric.VALIDITY, 0.95),
                QualityThreshold(QualityMetric.CONSISTENCY, 0.85)
            ]
            thresholds.extend(default_thresholds)
        
        return thresholds
    
    async def _calculate_quality_metrics(
        self,
        feature_name: str,
        feature_data: Any,
        feature_type: FeatureType,
        creator_type: CreatorType
    ) -> Dict[QualityMetric, float]:
        """
        Calculate comprehensive quality metrics
        
        **ML Engineer Excellence:** Advanced statistical analysis
        """
        # Convert to pandas Series
        series = pd.Series(feature_data) if not isinstance(feature_data, pd.Series) else feature_data
        
        quality_scores = {}
        
        # Completeness: ratio of non-null values
        quality_scores[QualityMetric.COMPLETENESS] = 1.0 - (series.isnull().sum() / len(series))
        
        # Validity: depends on feature type
        quality_scores[QualityMetric.VALIDITY] = await self._calculate_validity_score(series, feature_type)
        
        # Consistency: measure of data consistency
        quality_scores[QualityMetric.CONSISTENCY] = await self._calculate_consistency_score(series, feature_type)
        
        # Uniqueness: ratio of unique values
        if len(series) > 0:
            quality_scores[QualityMetric.UNIQUENESS] = len(series.dropna().unique()) / len(series.dropna())
        else:
            quality_scores[QualityMetric.UNIQUENESS] = 0.0
        
        # Stability: measure of temporal stability
        quality_scores[QualityMetric.STABILITY] = await self._calculate_stability_score(
            feature_name, series, feature_type
        )
        
        # Distribution quality: statistical distribution assessment
        quality_scores[QualityMetric.DISTRIBUTION] = await self._calculate_distribution_score(
            series, feature_type
        )
        
        # Accuracy: compared to historical baseline
        quality_scores[QualityMetric.ACCURACY] = await self._calculate_accuracy_score(
            feature_name, series, creator_type
        )
        
        # Correlation: relationship with other features
        quality_scores[QualityMetric.CORRELATION] = await self._calculate_correlation_score(
            feature_name, series, creator_type
        )
        
        return quality_scores
    
    async def _calculate_validity_score(self, series: pd.Series, feature_type: FeatureType) -> float:
        """Calculate validity score based on feature type"""
        if len(series) == 0:
            return 0.0
        
        non_null_series = series.dropna()
        if len(non_null_series) == 0:
            return 0.0
        
        valid_count = 0
        total_count = len(non_null_series)
        
        try:
            if feature_type == FeatureType.NUMERICAL:
                # Check for finite numerical values
                valid_count = np.isfinite(pd.to_numeric(non_null_series, errors='coerce')).sum()
                
            elif feature_type == FeatureType.CATEGORICAL:
                # Check for non-empty strings
                valid_count = non_null_series.astype(str).str.strip().ne('').sum()
                
            elif feature_type == FeatureType.BOOLEAN:
                # Check for valid boolean values
                valid_values = {True, False, 1, 0, '1', '0', 'true', 'false', 'True', 'False'}
                valid_count = non_null_series.isin(valid_values).sum()
                
            elif feature_type == FeatureType.DATETIME:
                # Check for valid datetime values
                try:
                    pd.to_datetime(non_null_series)
                    valid_count = total_count
                except:
                    valid_count = 0
                    
            elif feature_type == FeatureType.TEXT:
                # Check for non-empty text
                valid_count = non_null_series.astype(str).str.len().gt(0).sum()
                
            else:
                # Default: assume all non-null values are valid
                valid_count = total_count
                
        except Exception as e:
            self.logger.warning(f"Error calculating validity score: {e}")
            return 0.5  # Default score on error
        
        return valid_count / total_count if total_count > 0 else 0.0
    
    async def _calculate_consistency_score(self, series: pd.Series, feature_type: FeatureType) -> float:
        """Calculate consistency score"""
        if len(series) == 0:
            return 0.0
        
        non_null_series = series.dropna()
        if len(non_null_series) <= 1:
            return 1.0
        
        try:
            if feature_type == FeatureType.NUMERICAL:
                # Use coefficient of variation (inverse)
                std_dev = non_null_series.std()
                mean_val = non_null_series.mean()
                if mean_val != 0:
                    cv = std_dev / abs(mean_val)
                    # Convert to 0-1 score (lower CV = higher consistency)
                    return max(0, 1 - min(cv, 1))
                else:
                    return 1.0 if std_dev == 0 else 0.0
                    
            elif feature_type in [FeatureType.CATEGORICAL, FeatureType.TEXT]:
                # Check format consistency (e.g., similar string patterns)
                str_series = non_null_series.astype(str)
                
                # Check length consistency
                lengths = str_series.str.len()
                length_cv = lengths.std() / lengths.mean() if lengths.mean() > 0 else 0
                
                # Check pattern consistency (basic)
                patterns = str_series.str.contains(r'^[A-Za-z]+$').sum() / len(str_series)
                
                return max(0, 1 - min(length_cv, 1)) * patterns
                
            elif feature_type == FeatureType.DATETIME:
                # Check for consistent datetime format/range
                dt_series = pd.to_datetime(non_null_series, errors='coerce')
                valid_dates = dt_series.dropna()
                
                if len(valid_dates) == 0:
                    return 0.0
                
                # Check if dates are within reasonable range
                date_range = valid_dates.max() - valid_dates.min()
                reasonable_range = timedelta(days=365 * 10)  # 10 years
                
                return min(1.0, reasonable_range.total_seconds() / date_range.total_seconds()) if date_range.total_seconds() > 0 else 1.0
                
            else:
                # For other types, check value distribution
                value_counts = non_null_series.value_counts()
                entropy = stats.entropy(value_counts)
                max_entropy = np.log(len(value_counts))
                
                # Normalize entropy (higher entropy = less consistency)
                if max_entropy > 0:
                    normalized_entropy = entropy / max_entropy
                    return max(0, 1 - normalized_entropy)
                else:
                    return 1.0
                    
        except Exception as e:
            self.logger.warning(f"Error calculating consistency score: {e}")
            return 0.5
    
    async def _calculate_stability_score(
        self,
        feature_name: str,
        series: pd.Series,
        feature_type: FeatureType
    ) -> float:
        """Calculate temporal stability score"""
        # Check if we have historical data
        if feature_name not in self.feature_profiles:
            return 1.0  # No baseline for comparison
        
        historical_profile = self.feature_profiles[feature_name]
        historical_stats = historical_profile.statistics
        
        try:
            current_stats = self._calculate_basic_statistics(series, feature_type)
            
            # Compare key statistics
            stability_scores = []
            
            if feature_type == FeatureType.NUMERICAL:
                # Compare mean, std, median
                for stat in ['mean', 'std', 'median']:
                    if stat in historical_stats and stat in current_stats:
                        hist_val = historical_stats[stat]
                        curr_val = current_stats[stat]
                        
                        if hist_val != 0:
                            relative_change = abs(curr_val - hist_val) / abs(hist_val)
                            stability_score = max(0, 1 - relative_change)
                            stability_scores.append(stability_score)
            
            elif feature_type == FeatureType.CATEGORICAL:
                # Compare value distribution
                hist_dist = historical_stats.get('value_distribution', {})
                curr_dist = current_stats.get('value_distribution', {})
                
                # Calculate KL divergence
                if hist_dist and curr_dist:
                    all_values = set(hist_dist.keys()) | set(curr_dist.keys())
                    hist_probs = [hist_dist.get(v, 0) for v in all_values]
                    curr_probs = [curr_dist.get(v, 0) for v in all_values]
                    
                    # Normalize
                    hist_probs = np.array(hist_probs) / sum(hist_probs) if sum(hist_probs) > 0 else np.array(hist_probs)
                    curr_probs = np.array(curr_probs) / sum(curr_probs) if sum(curr_probs) > 0 else np.array(curr_probs)
                    
                    # Add small epsilon to avoid log(0)
                    epsilon = 1e-8
                    hist_probs = hist_probs + epsilon
                    curr_probs = curr_probs + epsilon
                    
                    kl_div = stats.entropy(curr_probs, hist_probs)
                    stability_score = max(0, 1 - min(kl_div, 1))
                    stability_scores.append(stability_score)
            
            return np.mean(stability_scores) if stability_scores else 1.0
            
        except Exception as e:
            self.logger.warning(f"Error calculating stability score: {e}")
            return 0.5
    
    async def _calculate_distribution_score(self, series: pd.Series, feature_type: FeatureType) -> float:
        """Calculate distribution quality score"""
        if len(series) == 0:
            return 0.0
        
        non_null_series = series.dropna()
        if len(non_null_series) <= 1:
            return 1.0
        
        try:
            if feature_type == FeatureType.NUMERICAL:
                # Test for normality and other distribution properties
                scores = []
                
                # Normality test (if applicable)
                if len(non_null_series) >= 3:
                    try:
                        # Shapiro-Wilk test
                        stat, p_value = stats.shapiro(non_null_series)
                        normality_score = min(p_value * 2, 1.0)  # Scale p-value
                        scores.append(normality_score)
                    except:
                        pass
                
                # Outlier detection
                if len(non_null_series) >= 4:
                    Q1 = non_null_series.quantile(0.25)
                    Q3 = non_null_series.quantile(0.75)
                    IQR = Q3 - Q1
                    
                    if IQR > 0:
                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR
                        outliers = ((non_null_series < lower_bound) | (non_null_series > upper_bound)).sum()
                        outlier_ratio = outliers / len(non_null_series)
                        outlier_score = max(0, 1 - outlier_ratio * 2)  # Penalize outliers
                        scores.append(outlier_score)
                
                # Skewness check
                skewness = abs(stats.skew(non_null_series))
                skewness_score = max(0, 1 - min(skewness / 2, 1))
                scores.append(skewness_score)
                
                return np.mean(scores) if scores else 0.5
                
            elif feature_type == FeatureType.CATEGORICAL:
                # Check for balanced distribution
                value_counts = non_null_series.value_counts()
                
                # Calculate entropy (higher entropy = more balanced)
                entropy = stats.entropy(value_counts)
                max_entropy = np.log(len(value_counts))
                
                if max_entropy > 0:
                    normalized_entropy = entropy / max_entropy
                    return normalized_entropy
                else:
                    return 1.0
                    
            else:
                # For other types, return neutral score
                return 0.8
                
        except Exception as e:
            self.logger.warning(f"Error calculating distribution score: {e}")
            return 0.5
    
    async def _calculate_accuracy_score(
        self,
        feature_name: str,
        series: pd.Series,
        creator_type: CreatorType
    ) -> float:
        """Calculate accuracy score based on expected values"""
        # This would typically compare against ground truth or expected ranges
        # For now, implement basic range validation
        
        if len(series) == 0:
            return 0.0
        
        non_null_series = series.dropna()
        if len(non_null_series) == 0:
            return 0.0
        
        try:
            # Creator-specific accuracy checks
            if creator_type == CreatorType.MUSICIAN:
                if 'tempo' in feature_name.lower():
                    # Tempo should be between 60-200 BPM typically
                    valid_range = (60, 200)
                    in_range = ((non_null_series >= valid_range[0]) & 
                               (non_null_series <= valid_range[1])).sum()
                    return in_range / len(non_null_series)
                elif 'duration' in feature_name.lower():
                    # Audio duration should be positive and reasonable
                    valid = (non_null_series > 0) & (non_null_series < 3600)  # < 1 hour
                    return valid.sum() / len(non_null_series)
                    
            elif creator_type == CreatorType.PHOTOGRAPHER:
                if 'resolution' in feature_name.lower() or 'width' in feature_name.lower() or 'height' in feature_name.lower():
                    # Image dimensions should be positive and reasonable
                    valid = (non_null_series > 0) & (non_null_series < 10000)
                    return valid.sum() / len(non_null_series)
                elif 'quality' in feature_name.lower() or 'score' in feature_name.lower():
                    # Quality scores typically 0-1 or 0-100
                    if non_null_series.max() <= 1:
                        valid = (non_null_series >= 0) & (non_null_series <= 1)
                    else:
                        valid = (non_null_series >= 0) & (non_null_series <= 100)
                    return valid.sum() / len(non_null_series)
                    
            elif creator_type == CreatorType.BLOGGER:
                if 'word_count' in feature_name.lower():
                    # Word count should be positive and reasonable
                    valid = (non_null_series > 0) & (non_null_series < 50000)
                    return valid.sum() / len(non_null_series)
                elif 'readability' in feature_name.lower():
                    # Readability scores typically have known ranges
                    valid = (non_null_series >= 0) & (non_null_series <= 100)
                    return valid.sum() / len(non_null_series)
            
            # Default: check for reasonable numerical ranges
            if pd.api.types.is_numeric_dtype(non_null_series):
                # Check for extreme values (beyond 5 standard deviations)
                if len(non_null_series) > 1:
                    z_scores = np.abs(stats.zscore(non_null_series))
                    reasonable = (z_scores <= 5).sum()
                    return reasonable / len(non_null_series)
            
            # Default high score if no specific checks apply
            return 0.9
            
        except Exception as e:
            self.logger.warning(f"Error calculating accuracy score: {e}")
            return 0.5
    
    async def _calculate_correlation_score(
        self,
        feature_name: str,
        series: pd.Series,
        creator_type: CreatorType
    ) -> float:
        """Calculate correlation quality score"""
        # This would typically analyze correlation with other features
        # For now, return a neutral score
        # TODO: Implement actual correlation analysis with feature store
        return 0.8
    
    def _calculate_basic_statistics(self, series: pd.Series, feature_type: FeatureType) -> Dict[str, Any]:
        """Calculate basic statistics for a feature"""
        stats_dict = {}
        
        try:
            non_null_series = series.dropna()
            
            if len(non_null_series) == 0:
                return stats_dict
            
            # Common statistics
            stats_dict['count'] = len(non_null_series)
            stats_dict['null_count'] = series.isnull().sum()
            stats_dict['unique_count'] = len(non_null_series.unique())
            
            if feature_type == FeatureType.NUMERICAL:
                stats_dict['mean'] = float(non_null_series.mean())
                stats_dict['std'] = float(non_null_series.std())
                stats_dict['median'] = float(non_null_series.median())
                stats_dict['min'] = float(non_null_series.min())
                stats_dict['max'] = float(non_null_series.max())
                stats_dict['skewness'] = float(stats.skew(non_null_series))
                stats_dict['kurtosis'] = float(stats.kurtosis(non_null_series))
                
            elif feature_type == FeatureType.CATEGORICAL:
                value_counts = non_null_series.value_counts()
                stats_dict['value_distribution'] = value_counts.to_dict()
                stats_dict['mode'] = value_counts.index[0] if len(value_counts) > 0 else None
                stats_dict['entropy'] = float(stats.entropy(value_counts))
                
            elif feature_type == FeatureType.TEXT:
                str_series = non_null_series.astype(str)
                stats_dict['avg_length'] = float(str_series.str.len().mean())
                stats_dict['max_length'] = int(str_series.str.len().max())
                stats_dict['min_length'] = int(str_series.str.len().min())
                
        except Exception as e:
            self.logger.warning(f"Error calculating basic statistics: {e}")
        
        return stats_dict
    
    def _generate_quality_report(
        self,
        feature_name: str,
        quality_scores: Dict[QualityMetric, float],
        thresholds: List[QualityThreshold],
        creator_type: CreatorType
    ) -> QualityReport:
        """Generate comprehensive quality report"""
        
        # Calculate overall score (weighted average)
        weights = self._get_metric_weights(feature_name, creator_type)
        weighted_scores = []
        
        for metric, score in quality_scores.items():
            weight = weights.get(metric, 1.0)
            weighted_scores.append(score * weight)
        
        overall_score = np.mean(weighted_scores) if weighted_scores else 0.0
        
        # Identify issues and recommendations
        issues = []
        recommendations = []
        
        for threshold in thresholds:
            metric = threshold.metric
            if metric in quality_scores:
                score = quality_scores[metric]
                
                if score < threshold.critical_threshold:
                    issues.append({
                        'type': f'critical_{metric.value}',
                        'message': f"{metric.value.title()} score ({score:.3f}) below critical threshold ({threshold.critical_threshold})",
                        'severity': 'critical',
                        'score': score,
                        'threshold': threshold.critical_threshold
                    })
                    recommendations.append(f"Urgent: Improve {metric.value} for {feature_name}")
                    
                elif score < threshold.warning_threshold:
                    issues.append({
                        'type': f'warning_{metric.value}',
                        'message': f"{metric.value.title()} score ({score:.3f}) below warning threshold ({threshold.warning_threshold})",
                        'severity': 'warning',
                        'score': score,
                        'threshold': threshold.warning_threshold
                    })
                    recommendations.append(f"Consider improving {metric.value} for {feature_name}")
        
        # Determine overall severity
        severity = 'info'
        if any(issue['severity'] == 'critical' for issue in issues):
            severity = 'critical'
        elif any(issue['severity'] == 'warning' for issue in issues):
            severity = 'warning'
        
        # Add general recommendations based on scores
        if quality_scores.get(QualityMetric.COMPLETENESS, 1.0) < 0.9:
            recommendations.append(f"Investigate missing data sources for {feature_name}")
        
        if quality_scores.get(QualityMetric.VALIDITY, 1.0) < 0.95:
            recommendations.append(f"Implement data validation rules for {feature_name}")
        
        if quality_scores.get(QualityMetric.STABILITY, 1.0) < 0.8:
            recommendations.append(f"Monitor {feature_name} for unexpected changes")
        
        return QualityReport(
            feature_name=feature_name,
            overall_score=overall_score,
            metric_scores=quality_scores,
            issues=issues,
            recommendations=list(set(recommendations)),  # Remove duplicates
            severity=severity,
            timestamp=datetime.utcnow(),
            creator_type=creator_type
        )
    
    def _get_metric_weights(self, feature_name: str, creator_type: CreatorType) -> Dict[QualityMetric, float]:
        """Get weights for different quality metrics"""
        # Default weights
        weights = {
            QualityMetric.COMPLETENESS: 1.5,  # Critical for ML
            QualityMetric.VALIDITY: 1.4,      # Very important
            QualityMetric.CONSISTENCY: 1.2,   # Important
            QualityMetric.ACCURACY: 1.3,      # Important
            QualityMetric.STABILITY: 1.1,     # Moderately important
            QualityMetric.DISTRIBUTION: 1.0,  # Standard
            QualityMetric.UNIQUENESS: 0.8,    # Less critical
            QualityMetric.CORRELATION: 0.9    # Context dependent
        }
        
        # Adjust weights based on creator type and feature name
        creator_feature_weights = self.creator_feature_weights.get(creator_type, {})
        
        for feature_category, weight_multiplier in creator_feature_weights.items():
            if feature_category.lower() in feature_name.lower():
                # Apply multiplier to all weights
                weights = {metric: weight * weight_multiplier for metric, weight in weights.items()}
                break
        
        return weights
    
    async def _update_feature_profile(
        self,
        feature_name: str,
        feature_type: FeatureType,
        feature_data: Any,
        quality_scores: Dict[QualityMetric, float],
        thresholds: List[QualityThreshold]
    ):
        """Update feature profile with latest data"""
        series = pd.Series(feature_data) if not isinstance(feature_data, pd.Series) else feature_data
        statistics = self._calculate_basic_statistics(series, feature_type)
        
        # Create or update profile
        if feature_name in self.feature_profiles:
            profile = self.feature_profiles[feature_name]
            profile.statistics = statistics
            profile.quality_scores = quality_scores
            profile.updated_at = datetime.utcnow()
            profile.sample_count += len(series)
        else:
            profile = FeatureProfile(
                feature_name=feature_name,
                feature_type=feature_type,
                statistics=statistics,
                quality_scores=quality_scores,
                thresholds=thresholds,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                sample_count=len(series)
            )
        
        self.feature_profiles[feature_name] = profile
        
        # Update quality history for trend analysis
        if feature_name not in self.quality_history:
            self.quality_history[feature_name] = []
        
        history_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'quality_scores': quality_scores,
            'sample_count': len(series)
        }
        
        self.quality_history[feature_name].append(history_entry)
        
        # Keep only recent history (last 100 entries)
        if len(self.quality_history[feature_name]) > 100:
            self.quality_history[feature_name] = self.quality_history[feature_name][-100:]
    
    async def get_feature_quality_trends(
        self,
        feature_name: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get quality trends for a feature"""
        if feature_name not in self.quality_history:
            return {}
        
        history = self.quality_history[feature_name]
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Filter recent history
        recent_history = [
            entry for entry in history
            if datetime.fromisoformat(entry['timestamp']) > cutoff_date
        ]
        
        if not recent_history:
            return {}
        
        # Calculate trends
        trends = {}
        for metric in QualityMetric:
            scores = [entry['quality_scores'].get(metric, 0) for entry in recent_history]
            if len(scores) > 1:
                # Calculate trend (positive = improving, negative = degrading)
                trend = np.polyfit(range(len(scores)), scores, 1)[0]
                trends[metric.value] = {
                    'trend': float(trend),
                    'current_score': scores[-1],
                    'average_score': np.mean(scores),
                    'score_history': scores
                }
        
        return {
            'feature_name': feature_name,
            'trends': trends,
            'data_points': len(recent_history),
            'period_days': days
        }

# Usage example
async def main():
    """Example usage of FeatureQualityMonitor"""
    config = {
        'alerts': {
            'quality_degradation_threshold': 0.1,
            'drift_significance_level': 0.05
        }
    }
    
    monitor = FeatureQualityMonitor(config)
    
    # Sample feature data
    features = {
        'audio_tempo': np.random.normal(120, 20, 1000),  # BPM
        'engagement_score': np.random.beta(2, 2, 1000),  # 0-1 score
        'content_category': np.random.choice(['rock', 'pop', 'jazz', 'classical'], 1000),
        'upload_timestamp': pd.date_range('2024-01-01', periods=1000, freq='H')
    }
    
    # Monitor features
    reports = await monitor.monitor_features(
        features=features,
        creator_type=CreatorType.MUSICIAN
    )
    
    # Print reports
    for report in reports:
        print(f"\nFeature: {report.feature_name}")
        print(f"Overall Score: {report.overall_score:.3f}")
        print(f"Severity: {report.severity}")
        if report.issues:
            print("Issues:")
            for issue in report.issues:
                print(f"  - {issue['message']}")
        if report.recommendations:
            print("Recommendations:")
            for rec in report.recommendations:
                print(f"  - {rec}")

if __name__ == "__main__":
    asyncio.run(main())