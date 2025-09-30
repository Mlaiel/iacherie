"""
✅ Feature Validation Framework - Data Quality & Feature Engineering Module

Comprehensive feature validation system with statistical tests, drift detection,
and quality assurance for machine learning features on the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Version: 1.0.0
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import hashlib
from pathlib import Path
import scipy.stats as stats
from scipy.stats import ks_2samp, chi2_contingency, mannwhitneyu
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif
from sklearn.model_selection import train_test_split
import redis
import concurrent.futures
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

@dataclass
class FeatureValidationConfig:
    """Configuration for feature validation"""
    statistical_significance_level: float = 0.05
    drift_detection_threshold: float = 0.1
    missing_value_threshold: float = 0.3
    outlier_detection_method: str = 'iqr'  # 'iqr', 'zscore', 'isolation_forest'
    correlation_threshold: float = 0.95
    information_gain_threshold: float = 0.01
    validate_distributions: bool = True
    validate_relationships: bool = True
    validate_temporal_stability: bool = True

@dataclass
class ValidationResult:
    """Results of feature validation"""
    feature_name: str
    validation_status: str  # 'passed', 'warning', 'failed'
    quality_score: float
    issues_detected: List[str]
    statistical_tests: Dict[str, Any]
    recommendations: List[str]
    metadata: Dict[str, Any]

@dataclass
class FeatureQualityReport:
    """Comprehensive feature quality assessment"""
    overall_score: float
    total_features: int
    passed_features: int
    warning_features: int
    failed_features: int
    validation_results: List[ValidationResult]
    drift_analysis: Dict[str, Any]
    correlation_analysis: Dict[str, Any]
    feature_importance: Dict[str, float]
    recommendations: List[str]

class FeatureValidationFramework:
    """
    ✅ Comprehensive Feature Validation & Quality Assurance Framework
    
    Provides statistical validation, drift detection, and quality assessment
    for machine learning features across all creator types.
    """
    
    def __init__(self,
                 redis_host: str = "localhost",
                 redis_port: int = 6379,
                 validation_cache_ttl: int = 3600):
        self.logger = logging.getLogger(__name__)
        
        # Initialize Redis for caching
        try:
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            self.redis_client.ping()
        except:
            self.logger.warning("Redis not available, using memory cache")
            self.redis_client = None
        
        self.cache_ttl = validation_cache_ttl
        
        # Statistical test configurations
        self.statistical_tests = {
            'normality': {
                'shapiro': stats.shapiro,
                'anderson': stats.anderson,
                'kstest': lambda x: stats.kstest(x, 'norm')
            },
            'stationarity': {
                'adf': self._adf_test,
                'kpss': self._kpss_test
            },
            'independence': {
                'ljungbox': self._ljung_box_test,
                'runs': self._runs_test
            }
        }
        
        # Feature type detection patterns
        self.feature_patterns = {
            'creator_metrics': ['likes', 'shares', 'comments', 'followers', 'engagement'],
            'content_features': ['duration', 'size', 'format', 'quality_score'],
            'temporal_features': ['hour', 'day', 'month', 'season', 'trend'],
            'behavioral_features': ['session_length', 'click_rate', 'bounce_rate'],
            'demographic_features': ['age', 'gender', 'location', 'device_type']
        }
        
        # Performance tracking
        self.validation_metrics = {
            'total_validations': 0,
            'avg_validation_time': 0.0,
            'feature_quality_trends': defaultdict(list),
            'drift_detection_rate': 0.0
        }
    
    async def validate_feature_set(self,
                                 features_df: pd.DataFrame,
                                 target_column: Optional[str] = None,
                                 reference_df: Optional[pd.DataFrame] = None,
                                 config: Optional[FeatureValidationConfig] = None) -> FeatureQualityReport:
        """
        🔍 Comprehensive feature set validation
        
        Args:
            features_df: DataFrame with features to validate
            target_column: Optional target column for supervised validation
            reference_df: Reference data for drift detection
            config: Validation configuration
            
        Returns:
            Comprehensive feature quality report
        """
        start_time = datetime.now()
        config = config or FeatureValidationConfig()
        
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(features_df, config)
            
            # Check cache
            if self.redis_client:
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    return FeatureQualityReport(**json.loads(cached_result))
            
            # Parallel validation tasks
            validation_tasks = []
            feature_columns = [col for col in features_df.columns if col != target_column]
            
            # Validate each feature
            for feature_name in feature_columns:
                task = self._validate_single_feature(
                    features_df[feature_name],
                    feature_name,
                    features_df,
                    target_column,
                    reference_df[feature_name] if reference_df is not None else None,
                    config
                )
                validation_tasks.append(task)
            
            # Execute validations in parallel
            validation_results = await asyncio.gather(*validation_tasks)
            
            # Analyze feature relationships
            correlation_analysis = await self._analyze_feature_correlations(features_df, config)
            
            # Detect feature drift
            drift_analysis = await self._analyze_feature_drift(
                features_df, reference_df, config
            ) if reference_df is not None else {}
            
            # Calculate feature importance
            feature_importance = await self._calculate_feature_importance(
                features_df, target_column
            ) if target_column is not None else {}
            
            # Generate overall assessment
            quality_report = await self._generate_quality_report(
                validation_results,
                correlation_analysis,
                drift_analysis,
                feature_importance,
                config
            )
            
            # Cache results
            if self.redis_client:
                self.redis_client.setex(
                    cache_key,
                    self.cache_ttl,
                    json.dumps(asdict(quality_report), default=str)
                )
            
            # Update metrics
            self._update_validation_metrics(quality_report, start_time)
            
            return quality_report
            
        except Exception as e:
            self.logger.error(f"❌ Feature validation failed: {e}")
            raise
    
    async def _validate_single_feature(self,
                                     feature_series: pd.Series,
                                     feature_name: str,
                                     full_df: pd.DataFrame,
                                     target_column: Optional[str],
                                     reference_series: Optional[pd.Series],
                                     config: FeatureValidationConfig) -> ValidationResult:
        """Validate a single feature comprehensively"""
        
        issues_detected = []
        statistical_tests = {}
        recommendations = []
        quality_factors = []
        
        # Basic data quality checks
        missing_ratio = feature_series.isnull().sum() / len(feature_series)
        if missing_ratio > config.missing_value_threshold:
            issues_detected.append(f"High missing value ratio: {missing_ratio:.2%}")
            quality_factors.append(0.3)
        else:
            quality_factors.append(1.0 - missing_ratio)
        
        # Data type validation
        if pd.api.types.is_numeric_dtype(feature_series):
            numeric_validation = await self._validate_numeric_feature(
                feature_series, feature_name, config
            )
            statistical_tests.update(numeric_validation['tests'])
            issues_detected.extend(numeric_validation['issues'])
            recommendations.extend(numeric_validation['recommendations'])
            quality_factors.append(numeric_validation['quality_score'])
            
        elif pd.api.types.is_categorical_dtype(feature_series) or feature_series.dtype == 'object':
            categorical_validation = await self._validate_categorical_feature(
                feature_series, feature_name, config
            )
            statistical_tests.update(categorical_validation['tests'])
            issues_detected.extend(categorical_validation['issues'])
            recommendations.extend(categorical_validation['recommendations'])
            quality_factors.append(categorical_validation['quality_score'])
        
        # Temporal validation if applicable
        if self._is_temporal_feature(feature_name):
            temporal_validation = await self._validate_temporal_feature(
                feature_series, feature_name, config
            )
            statistical_tests.update(temporal_validation['tests'])
            issues_detected.extend(temporal_validation['issues'])
            quality_factors.append(temporal_validation['quality_score'])
        
        # Drift detection
        if reference_series is not None:
            drift_result = await self._detect_feature_drift(
                feature_series, reference_series, feature_name, config
            )
            statistical_tests['drift_test'] = drift_result
            if drift_result['drift_detected']:
                issues_detected.append(f"Feature drift detected: {drift_result['drift_score']:.3f}")
                quality_factors.append(0.5)
            else:
                quality_factors.append(1.0)
        
        # Target relationship validation
        if target_column is not None and target_column in full_df.columns:
            relationship_validation = await self._validate_target_relationship(
                feature_series, full_df[target_column], feature_name, config
            )
            statistical_tests.update(relationship_validation['tests'])
            if relationship_validation['weak_relationship']:
                issues_detected.append("Weak relationship with target variable")
                quality_factors.append(0.6)
            else:
                quality_factors.append(1.0)
        
        # Calculate overall quality score
        quality_score = np.mean(quality_factors) if quality_factors else 0.0
        
        # Determine validation status
        if quality_score >= 0.8:
            status = 'passed'
        elif quality_score >= 0.6:
            status = 'warning'
        else:
            status = 'failed'
        
        # Generate recommendations based on issues
        if missing_ratio > 0.1:
            recommendations.append("Consider imputation strategies for missing values")
        if quality_score < 0.7:
            recommendations.append("Feature may need preprocessing or transformation")
        
        return ValidationResult(
            feature_name=feature_name,
            validation_status=status,
            quality_score=quality_score,
            issues_detected=issues_detected,
            statistical_tests=statistical_tests,
            recommendations=recommendations,
            metadata={
                'missing_ratio': missing_ratio,
                'data_type': str(feature_series.dtype),
                'unique_values': feature_series.nunique(),
                'feature_category': self._categorize_feature(feature_name)
            }
        )
    
    async def _validate_numeric_feature(self,
                                      feature_series: pd.Series,
                                      feature_name: str,
                                      config: FeatureValidationConfig) -> Dict[str, Any]:
        """Validate numeric feature"""
        
        issues = []
        tests = {}
        recommendations = []
        quality_factors = []
        
        # Remove missing values for statistical tests
        clean_series = feature_series.dropna()
        
        if len(clean_series) == 0:
            return {
                'tests': {},
                'issues': ['All values are missing'],
                'recommendations': ['Remove feature or use advanced imputation'],
                'quality_score': 0.0
            }
        
        # Outlier detection
        if config.outlier_detection_method == 'iqr':
            outlier_ratio = self._detect_outliers_iqr(clean_series)
        elif config.outlier_detection_method == 'zscore':
            outlier_ratio = self._detect_outliers_zscore(clean_series)
        else:
            outlier_ratio = 0.0
        
        tests['outlier_ratio'] = outlier_ratio
        if outlier_ratio > 0.1:
            issues.append(f"High outlier ratio: {outlier_ratio:.2%}")
            quality_factors.append(0.7)
            recommendations.append("Consider outlier treatment or robust scaling")
        else:
            quality_factors.append(1.0)
        
        # Distribution tests
        if config.validate_distributions and len(clean_series) > 20:
            # Normality test
            if len(clean_series) <= 5000:
                shapiro_stat, shapiro_p = stats.shapiro(clean_series)
                tests['shapiro_normality'] = {'statistic': shapiro_stat, 'p_value': shapiro_p}
                
                if shapiro_p < config.statistical_significance_level:
                    issues.append("Non-normal distribution detected")
                    quality_factors.append(0.8)
                else:
                    quality_factors.append(1.0)
        
        # Variance check
        variance = clean_series.var()
        tests['variance'] = variance
        if variance < 1e-6:
            issues.append("Very low variance - feature may be constant")
            quality_factors.append(0.3)
            recommendations.append("Consider removing low-variance feature")
        else:
            quality_factors.append(1.0)
        
        # Range validation
        feature_range = clean_series.max() - clean_series.min()
        tests['range'] = feature_range
        if feature_range == 0:
            issues.append("Feature has zero range - all values identical")
            quality_factors.append(0.0)
        else:
            quality_factors.append(1.0)
        
        return {
            'tests': tests,
            'issues': issues,
            'recommendations': recommendations,
            'quality_score': np.mean(quality_factors) if quality_factors else 0.0
        }
    
    async def _validate_categorical_feature(self,
                                          feature_series: pd.Series,
                                          feature_name: str,
                                          config: FeatureValidationConfig) -> Dict[str, Any]:
        """Validate categorical feature"""
        
        issues = []
        tests = {}
        recommendations = []
        quality_factors = []
        
        # Remove missing values
        clean_series = feature_series.dropna()
        
        if len(clean_series) == 0:
            return {
                'tests': {},
                'issues': ['All values are missing'],
                'recommendations': ['Remove feature or use mode imputation'],
                'quality_score': 0.0
            }
        
        # Cardinality check
        unique_count = clean_series.nunique()
        cardinality_ratio = unique_count / len(clean_series)
        
        tests['cardinality'] = {
            'unique_count': unique_count,
            'cardinality_ratio': cardinality_ratio
        }
        
        if cardinality_ratio > 0.9:
            issues.append(f"Very high cardinality: {unique_count} unique values")
            quality_factors.append(0.5)
            recommendations.append("Consider grouping rare categories or feature engineering")
        elif cardinality_ratio < 0.01:
            issues.append("Very low cardinality - feature may not be informative")
            quality_factors.append(0.6)
        else:
            quality_factors.append(1.0)
        
        # Category distribution
        value_counts = clean_series.value_counts()
        tests['distribution'] = value_counts.to_dict()
        
        # Check for dominant category
        dominant_ratio = value_counts.iloc[0] / len(clean_series)
        if dominant_ratio > 0.95:
            issues.append(f"Dominant category: {dominant_ratio:.2%} of values")
            quality_factors.append(0.4)
            recommendations.append("Consider removing or combining with other features")
        else:
            quality_factors.append(1.0)
        
        # Check for rare categories
        rare_categories = value_counts[value_counts < len(clean_series) * 0.01]
        if len(rare_categories) > 0:
            issues.append(f"{len(rare_categories)} rare categories detected")
            quality_factors.append(0.8)
            recommendations.append("Consider grouping rare categories")
        else:
            quality_factors.append(1.0)
        
        return {
            'tests': tests,
            'issues': issues,
            'recommendations': recommendations,
            'quality_score': np.mean(quality_factors) if quality_factors else 0.0
        }
    
    async def _detect_feature_drift(self,
                                  current_series: pd.Series,
                                  reference_series: pd.Series,
                                  feature_name: str,
                                  config: FeatureValidationConfig) -> Dict[str, Any]:
        """Detect statistical drift between current and reference data"""
        
        # Remove missing values
        current_clean = current_series.dropna()
        reference_clean = reference_series.dropna()
        
        if len(current_clean) == 0 or len(reference_clean) == 0:
            return {
                'drift_detected': False,
                'drift_score': 0.0,
                'test_method': 'insufficient_data',
                'p_value': 1.0
            }
        
        # Choose appropriate test based on data type
        if pd.api.types.is_numeric_dtype(current_series):
            # Kolmogorov-Smirnov test for numeric data
            ks_stat, p_value = ks_2samp(reference_clean, current_clean)
            drift_score = ks_stat
            test_method = 'kolmogorov_smirnov'
        else:
            # Chi-square test for categorical data
            try:
                # Align categories
                all_categories = set(current_clean.unique()) | set(reference_clean.unique())
                current_counts = current_clean.value_counts().reindex(all_categories, fill_value=0)
                reference_counts = reference_clean.value_counts().reindex(all_categories, fill_value=0)
                
                # Perform chi-square test
                chi2_stat, p_value, _, _ = chi2_contingency([reference_counts, current_counts])
                drift_score = chi2_stat / (len(all_categories) - 1)  # Normalized
                test_method = 'chi_square'
            except:
                return {
                    'drift_detected': False,
                    'drift_score': 0.0,
                    'test_method': 'test_failed',
                    'p_value': 1.0
                }
        
        drift_detected = (p_value < config.statistical_significance_level or 
                         drift_score > config.drift_detection_threshold)
        
        return {
            'drift_detected': drift_detected,
            'drift_score': drift_score,
            'test_method': test_method,
            'p_value': p_value,
            'recommendation': 'Retrain model' if drift_detected else 'No action needed'
        }
    
    async def _analyze_feature_correlations(self,
                                          features_df: pd.DataFrame,
                                          config: FeatureValidationConfig) -> Dict[str, Any]:
        """Analyze feature correlations and multicollinearity"""
        
        # Select only numeric features for correlation analysis
        numeric_features = features_df.select_dtypes(include=[np.number])
        
        if numeric_features.empty:
            return {'high_correlations': [], 'correlation_matrix': {}}
        
        # Calculate correlation matrix
        correlation_matrix = numeric_features.corr()
        
        # Find high correlations
        high_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = abs(correlation_matrix.iloc[i, j])
                if corr_value > config.correlation_threshold:
                    high_correlations.append({
                        'feature_1': correlation_matrix.columns[i],
                        'feature_2': correlation_matrix.columns[j],
                        'correlation': correlation_matrix.iloc[i, j],
                        'recommendation': 'Consider removing one of the features'
                    })
        
        return {
            'high_correlations': high_correlations,
            'correlation_matrix': correlation_matrix.to_dict(),
            'multicollinearity_detected': len(high_correlations) > 0
        }
    
    def _detect_outliers_iqr(self, series: pd.Series) -> float:
        """Detect outliers using IQR method"""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = series[(series < lower_bound) | (series > upper_bound)]
        return len(outliers) / len(series)
    
    def _detect_outliers_zscore(self, series: pd.Series, threshold: float = 3.0) -> float:
        """Detect outliers using Z-score method"""
        z_scores = np.abs(stats.zscore(series))
        outliers = series[z_scores > threshold]
        return len(outliers) / len(series)
    
    def _is_temporal_feature(self, feature_name: str) -> bool:
        """Check if feature is temporal"""
        temporal_keywords = ['time', 'date', 'hour', 'day', 'month', 'year', 'timestamp']
        return any(keyword in feature_name.lower() for keyword in temporal_keywords)
    
    def _categorize_feature(self, feature_name: str) -> str:
        """Categorize feature based on name patterns"""
        for category, patterns in self.feature_patterns.items():
            if any(pattern in feature_name.lower() for pattern in patterns):
                return category
        return 'unknown'
    
    def _generate_cache_key(self, features_df: pd.DataFrame, config: FeatureValidationConfig) -> str:
        """Generate cache key for validation results"""
        # Create hash of dataframe structure and config
        df_hash = hashlib.md5(
            str(features_df.columns.tolist() + features_df.dtypes.tolist()).encode()
        ).hexdigest()
        config_hash = hashlib.md5(json.dumps(asdict(config), sort_keys=True).encode()).hexdigest()
        
        return f"feature_validation:{df_hash}:{config_hash}"
    
    def _update_validation_metrics(self, report: FeatureQualityReport, start_time: datetime):
        """Update validation performance metrics"""
        self.validation_metrics['total_validations'] += 1
        
        processing_time = (datetime.now() - start_time).total_seconds()
        total = self.validation_metrics['total_validations']
        self.validation_metrics['avg_validation_time'] = (
            (self.validation_metrics['avg_validation_time'] * (total - 1) + processing_time) / total
        )
        
        # Track quality trends
        self.validation_metrics['feature_quality_trends']['overall'].append(report.overall_score)
    
    async def get_validation_metrics(self) -> Dict[str, Any]:
        """Get validation performance metrics"""
        return {
            **self.validation_metrics,
            'supported_tests': list(self.statistical_tests.keys()),
            'feature_categories': list(self.feature_patterns.keys()),
            'cache_status': 'active' if self.redis_client else 'disabled'
        }

# Example usage and integration
if __name__ == "__main__":
    async def main():
        # Initialize framework
        validator = FeatureValidationFramework()
        
        print("✅ Feature Validation Framework - Ready for Quality Assessment")
        
        # Example validation
        try:
            # Create sample data
            np.random.seed(42)
            sample_data = pd.DataFrame({
                'likes_count': np.random.poisson(100, 1000),
                'engagement_rate': np.random.beta(2, 5, 1000),
                'follower_count': np.random.lognormal(10, 1, 1000),
                'content_category': np.random.choice(['music', 'blog', 'photo'], 1000),
                'posting_hour': np.random.randint(0, 24, 1000),
                'target_metric': np.random.uniform(0, 1, 1000)
            })
            
            # Validate features
            report = await validator.validate_feature_set(
                sample_data,
                target_column='target_metric'
            )
            
            print(f"📊 Validation completed - Overall Score: {report.overall_score:.2f}")
            print(f"✅ Passed: {report.passed_features}, ⚠️ Warnings: {report.warning_features}, ❌ Failed: {report.failed_features}")
            
            # Show issues
            for result in report.validation_results:
                if result.issues_detected:
                    print(f"🔍 {result.feature_name}: {result.issues_detected}")
            
        except Exception as e:
            print(f"❌ Validation failed: {e}")
        
        # Get metrics
        metrics = await validator.get_validation_metrics()
        print(f"📈 Framework Metrics: {metrics}")

    if __name__ == "__main__":
        asyncio.run(main())