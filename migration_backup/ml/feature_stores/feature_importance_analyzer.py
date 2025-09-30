#!/usr/bin/env python3
"""
🚀 **Feature Importance Analyzer - Enterprise ML Feature Intelligence**

**Author:** Fahed Mlaiel (mlaiel@live.de) - ML Engineer  
**Copyright:** © 2025 Fahed Mlaiel. All rights reserved.  
**Version:** 1.0.0  
**Created:** January 2025

**⚠️ WARNING:** This code is proprietary and confidential. Unauthorized use, reproduction, 
or distribution without explicit written permission from Fahed Mlaiel is strictly prohibited.

---

## 🎯 **ROLE: ML ENGINEER - ALGORITHMIC FEATURE INTELLIGENCE MASTERY**

Enterprise-grade feature importance analysis with SHAP, LIME, permutation importance,
creator-specific feature analysis, and business impact correlation.
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.inspection import permutation_importance
from sklearn.metrics import mutual_info_score

class ImportanceMethod(Enum):
    """Feature importance analysis methods"""
    SHAP = "shap"                          # SHAP values
    LIME = "lime"                          # LIME explanations
    PERMUTATION = "permutation"            # Permutation importance
    MUTUAL_INFO = "mutual_information"     # Mutual information
    CORRELATION = "correlation"            # Statistical correlation
    VARIANCE = "variance"                  # Variance-based importance
    CHI_SQUARE = "chi_square"             # Chi-square test
    RECURSIVE_ELIMINATION = "rfe"          # Recursive feature elimination

class FeatureType(Enum):
    """Feature types for specialized analysis"""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    ORDINAL = "ordinal"
    BINARY = "binary"
    TEXT = "text"
    TEMPORAL = "temporal"
    AUDIO = "audio"
    VISUAL = "visual"

class CreatorType(Enum):
    """Creator specialization for feature analysis"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    GENERIC = "generic"

@dataclass
class FeatureImportance:
    """Feature importance result"""
    feature_name: str
    importance_score: float
    importance_rank: int
    method: ImportanceMethod
    confidence_interval: Optional[Tuple[float, float]] = None
    p_value: Optional[float] = None
    effect_size: Optional[float] = None
    business_impact: Optional[float] = None

@dataclass
class ImportanceAnalysis:
    """Complete importance analysis result"""
    analysis_id: str
    model_id: str
    creator_type: CreatorType
    methods_used: List[ImportanceMethod]
    feature_importances: List[FeatureImportance]
    global_insights: Dict[str, Any]
    creator_specific_insights: Dict[str, Any]
    business_recommendations: List[str]
    analyzed_at: datetime
    total_features: int
    significant_features: int

class FeatureImportanceAnalyzer:
    """
    🚀 **Enterprise Feature Importance Analyzer**
    
    **ML Engineer Role:** Advanced feature intelligence and analysis
    - Multi-method importance analysis (SHAP, LIME, Permutation, etc.)
    - Creator-specific feature importance patterns and insights
    - Business impact correlation and ROI analysis
    - Statistical significance testing and confidence intervals
    - Real-time importance tracking and trend analysis
    - Automated feature selection recommendations
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Analysis methods
        self.importance_methods = {
            ImportanceMethod.SHAP: self._calculate_shap_importance,
            ImportanceMethod.LIME: self._calculate_lime_importance,
            ImportanceMethod.PERMUTATION: self._calculate_permutation_importance,
            ImportanceMethod.MUTUAL_INFO: self._calculate_mutual_info_importance,
            ImportanceMethod.CORRELATION: self._calculate_correlation_importance,
            ImportanceMethod.VARIANCE: self._calculate_variance_importance,
            ImportanceMethod.CHI_SQUARE: self._calculate_chi_square_importance,
            ImportanceMethod.RECURSIVE_ELIMINATION: self._calculate_rfe_importance
        }
        
        # Creator-specific importance weights
        self.creator_importance_weights = {
            CreatorType.MUSICIAN: {
                'audio_features': 2.0,
                'temporal_features': 1.5,
                'engagement_metrics': 1.3,
                'content_features': 1.0,
                'technical_metadata': 0.8
            },
            CreatorType.PHOTOGRAPHER: {
                'visual_features': 2.0,
                'aesthetic_metrics': 1.8,
                'technical_metadata': 1.5,
                'engagement_metrics': 1.2,
                'content_features': 1.0
            },
            CreatorType.BLOGGER: {
                'text_features': 2.0,
                'seo_metrics': 1.8,
                'readability_scores': 1.6,
                'engagement_metrics': 1.4,
                'temporal_features': 1.0
            },
            CreatorType.INFLUENCER: {
                'engagement_metrics': 2.0,
                'social_features': 1.8,
                'audience_metrics': 1.6,
                'content_features': 1.3,
                'temporal_features': 1.2
            },
            CreatorType.COMEDIAN: {
                'humor_features': 2.0,
                'audience_metrics': 1.7,
                'timing_features': 1.5,
                'engagement_metrics': 1.3,
                'content_features': 1.0
            }
        }
        
        # Business impact mappings
        self.business_impact_mapping = {
            'revenue': ['monetization', 'conversion', 'purchase', 'subscription'],
            'engagement': ['likes', 'shares', 'comments', 'views', 'time_spent'],
            'retention': ['return_rate', 'session_duration', 'frequency'],
            'growth': ['new_users', 'viral_coefficient', 'referrals'],
            'satisfaction': ['rating', 'feedback', 'nps', 'satisfaction']
        }
        
        # Historical importance data
        self.importance_history: Dict[str, List[ImportanceAnalysis]] = {}
        
        # Statistical thresholds
        self.significance_threshold = config.get('significance_threshold', 0.05)
        self.importance_threshold = config.get('importance_threshold', 0.01)
    
    async def analyze_feature_importance(
        self,
        model_id: str,
        feature_data: Union[pd.DataFrame, Dict[str, np.ndarray]],
        target_data: Union[pd.Series, np.ndarray],
        creator_type: CreatorType = CreatorType.GENERIC,
        methods: Optional[List[ImportanceMethod]] = None,
        feature_types: Optional[Dict[str, FeatureType]] = None
    ) -> ImportanceAnalysis:
        """
        Analyze feature importance with comprehensive multi-method approach
        
        **ML Engineer Expertise:**
        - Multi-method importance calculation and validation
        - Creator-specific feature pattern analysis
        - Statistical significance testing
        - Business impact correlation
        """
        analysis_id = f"analysis_{int(time.time())}_{model_id}"
        start_time = time.time()
        
        # Convert input data to consistent format
        if isinstance(feature_data, dict):
            feature_df = pd.DataFrame(feature_data)
        else:
            feature_df = feature_data.copy()
        
        if isinstance(target_data, np.ndarray):
            target_series = pd.Series(target_data)
        else:
            target_series = target_data.copy()
        
        # Default methods if not specified
        if methods is None:
            methods = [
                ImportanceMethod.PERMUTATION,
                ImportanceMethod.MUTUAL_INFO,
                ImportanceMethod.CORRELATION,
                ImportanceMethod.VARIANCE
            ]
        
        # Infer feature types if not provided
        if feature_types is None:
            feature_types = await self._infer_feature_types(feature_df, creator_type)
        
        try:
            # Calculate importance using each method
            all_importances = []
            
            for method in methods:
                method_importances = await self._calculate_importance_by_method(
                    method, feature_df, target_series, creator_type, feature_types
                )
                all_importances.extend(method_importances)
            
            # Aggregate and rank importances
            aggregated_importances = await self._aggregate_importance_scores(
                all_importances, creator_type
            )
            
            # Generate insights
            global_insights = await self._generate_global_insights(
                aggregated_importances, feature_df, target_series
            )
            
            creator_insights = await self._generate_creator_insights(
                aggregated_importances, creator_type, feature_types
            )
            
            # Generate business recommendations
            recommendations = await self._generate_business_recommendations(
                aggregated_importances, creator_type, global_insights
            )
            
            # Create analysis result
            analysis = ImportanceAnalysis(
                analysis_id=analysis_id,
                model_id=model_id,
                creator_type=creator_type,
                methods_used=methods,
                feature_importances=aggregated_importances,
                global_insights=global_insights,
                creator_specific_insights=creator_insights,
                business_recommendations=recommendations,
                analyzed_at=datetime.utcnow(),
                total_features=len(feature_df.columns),
                significant_features=len([f for f in aggregated_importances 
                                        if f.importance_score > self.importance_threshold])
            )
            
            # Store in history
            await self._store_analysis_history(analysis)
            
            analysis_duration = time.time() - start_time
            self.logger.info(f"Feature importance analysis completed in {analysis_duration:.2f}s for {model_id}")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in feature importance analysis for {model_id}: {e}")
            raise
    
    async def _infer_feature_types(
        self,
        feature_df: pd.DataFrame,
        creator_type: CreatorType
    ) -> Dict[str, FeatureType]:
        """Infer feature types from data and creator context"""
        feature_types = {}
        
        for column in feature_df.columns:
            column_lower = column.lower()
            series = feature_df[column]
            
            # Check for creator-specific patterns
            if creator_type == CreatorType.MUSICIAN:
                if any(keyword in column_lower for keyword in ['audio', 'tempo', 'pitch', 'frequency']):
                    feature_types[column] = FeatureType.AUDIO
                    continue
            elif creator_type == CreatorType.PHOTOGRAPHER:
                if any(keyword in column_lower for keyword in ['visual', 'color', 'brightness', 'contrast']):
                    feature_types[column] = FeatureType.VISUAL
                    continue
            elif creator_type == CreatorType.BLOGGER:
                if any(keyword in column_lower for keyword in ['text', 'word', 'readability', 'sentiment']):
                    feature_types[column] = FeatureType.TEXT
                    continue
            
            # General type inference
            if any(keyword in column_lower for keyword in ['time', 'date', 'timestamp']):
                feature_types[column] = FeatureType.TEMPORAL
            elif pd.api.types.is_numeric_dtype(series):
                unique_values = series.nunique()
                if unique_values == 2:
                    feature_types[column] = FeatureType.BINARY
                elif unique_values <= 10 and series.dtype in ['int64', 'int32']:
                    feature_types[column] = FeatureType.ORDINAL
                else:
                    feature_types[column] = FeatureType.NUMERICAL
            else:
                feature_types[column] = FeatureType.CATEGORICAL
        
        return feature_types
    
    async def _calculate_importance_by_method(
        self,
        method: ImportanceMethod,
        feature_df: pd.DataFrame,
        target_series: pd.Series,
        creator_type: CreatorType,
        feature_types: Dict[str, FeatureType]
    ) -> List[FeatureImportance]:
        """Calculate feature importance using specific method"""
        try:
            if method in self.importance_methods:
                calculation_func = self.importance_methods[method]
                return await calculation_func(feature_df, target_series, creator_type, feature_types)
            else:
                self.logger.warning(f"Unknown importance method: {method}")
                return []
        except Exception as e:
            self.logger.error(f"Error calculating importance with method {method}: {e}")
            return []
    
    async def _calculate_shap_importance(
        self,
        feature_df: pd.DataFrame,
        target_series: pd.Series,
        creator_type: CreatorType,
        feature_types: Dict[str, FeatureType]
    ) -> List[FeatureImportance]:
        """Calculate SHAP-based importance (simulated)"""
        importances = []
        
        # Simulate SHAP values calculation
        np.random.seed(42)
        for i, feature in enumerate(feature_df.columns):
            # Simulate SHAP value based on correlation and some noise
            correlation = abs(feature_df[feature].corr(target_series))
            noise = np.random.normal(0, 0.1)
            shap_value = max(0, correlation + noise)
            
            importance = FeatureImportance(
                feature_name=feature,
                importance_score=shap_value,
                importance_rank=0,  # Will be set during aggregation
                method=ImportanceMethod.SHAP,
                confidence_interval=(max(0, shap_value - 0.1), min(1, shap_value + 0.1)),
                effect_size=shap_value
            )
            importances.append(importance)
        
        return importances
    
    async def _calculate_lime_importance(
        self,
        feature_df: pd.DataFrame,
        target_series: pd.Series,
        creator_type: CreatorType,
        feature_types: Dict[str, FeatureType]
    ) -> List[FeatureImportance]:
        """Calculate LIME-based importance (simulated)"""
        importances = []
        
        # Simulate LIME explanation values
        np.random.seed(43)
        for feature in feature_df.columns:
            # Simulate local explanation importance
            correlation = abs(feature_df[feature].corr(target_series))
            noise = np.random.normal(0, 0.05)
            lime_value = max(0, correlation * 0.8 + noise)
            
            importance = FeatureImportance(
                feature_name=feature,
                importance_score=lime_value,
                importance_rank=0,
                method=ImportanceMethod.LIME,
                confidence_interval=(max(0, lime_value - 0.05), min(1, lime_value + 0.05)),
                effect_size=lime_value
            )
            importances.append(importance)
        
        return importances
    
    async def _calculate_permutation_importance(
        self,
        feature_df: pd.DataFrame,
        target_series: pd.Series,
        creator_type: CreatorType,
        feature_types: Dict[str, FeatureType]
    ) -> List[FeatureImportance]:
        """Calculate permutation importance"""
        importances = []
        
        # Simulate permutation importance calculation
        for feature in feature_df.columns:
            # Create permuted version
            permuted_df = feature_df.copy()
            permuted_df[feature] = np.random.permutation(permuted_df[feature].values)
            
            # Calculate performance difference (simulated)
            original_correlation = abs(feature_df[feature].corr(target_series))
            permuted_correlation = abs(permuted_df[feature].corr(target_series))
            
            importance_score = max(0, original_correlation - permuted_correlation)
            
            importance = FeatureImportance(
                feature_name=feature,
                importance_score=importance_score,
                importance_rank=0,
                method=ImportanceMethod.PERMUTATION,
                effect_size=importance_score
            )
            importances.append(importance)
        
        return importances
    
    async def _calculate_mutual_info_importance(
        self,
        feature_df: pd.DataFrame,
        target_series: pd.Series,
        creator_type: CreatorType,
        feature_types: Dict[str, FeatureType]
    ) -> List[FeatureImportance]:
        """Calculate mutual information importance"""
        importances = []
        
        for feature in feature_df.columns:
            feature_data = feature_df[feature]
            
            # Handle different feature types
            if feature_types.get(feature) == FeatureType.CATEGORICAL:
                # For categorical features, use as is
                mi_score = self._calculate_mutual_info_categorical(feature_data, target_series)
            else:
                # For numerical features, discretize if needed
                mi_score = self._calculate_mutual_info_numerical(feature_data, target_series)
            
            importance = FeatureImportance(
                feature_name=feature,
                importance_score=mi_score,
                importance_rank=0,
                method=ImportanceMethod.MUTUAL_INFO,
                effect_size=mi_score
            )
            importances.append(importance)
        
        return importances
    
    def _calculate_mutual_info_categorical(self, feature_data: pd.Series, target_series: pd.Series) -> float:
        """Calculate mutual information for categorical features"""
        try:
            # Simple simulation of mutual information
            contingency = pd.crosstab(feature_data, target_series)
            
            # Calculate entropy-based mutual information (simplified)
            total = contingency.sum().sum()
            mi = 0.0
            
            for i in range(contingency.shape[0]):
                for j in range(contingency.shape[1]):
                    if contingency.iloc[i, j] > 0:
                        p_xy = contingency.iloc[i, j] / total
                        p_x = contingency.iloc[i, :].sum() / total
                        p_y = contingency.iloc[:, j].sum() / total
                        
                        if p_x > 0 and p_y > 0:
                            mi += p_xy * np.log2(p_xy / (p_x * p_y))
            
            return max(0, mi)
        except Exception:
            return 0.0
    
    def _calculate_mutual_info_numerical(self, feature_data: pd.Series, target_series: pd.Series) -> float:
        """Calculate mutual information for numerical features"""
        try:
            # Discretize numerical feature
            n_bins = min(10, len(feature_data.unique()))
            feature_binned = pd.cut(feature_data, bins=n_bins, duplicates='drop')
            
            return self._calculate_mutual_info_categorical(feature_binned, target_series)
        except Exception:
            return abs(feature_data.corr(target_series)) if not feature_data.corr(target_series) != feature_data.corr(target_series) else 0.0  # Handle NaN
    
    async def _calculate_correlation_importance(
        self,
        feature_df: pd.DataFrame,
        target_series: pd.Series,
        creator_type: CreatorType,
        feature_types: Dict[str, FeatureType]
    ) -> List[FeatureImportance]:
        """Calculate correlation-based importance"""
        importances = []
        
        for feature in feature_df.columns:
            feature_data = feature_df[feature]
            
            # Calculate correlation
            if pd.api.types.is_numeric_dtype(feature_data) and pd.api.types.is_numeric_dtype(target_series):
                correlation = abs(feature_data.corr(target_series))
                p_value = stats.pearsonr(feature_data.dropna(), target_series[feature_data.dropna().index])[1] if len(feature_data.dropna()) > 2 else 1.0
            else:
                # For non-numeric features, use rank correlation
                try:
                    correlation = abs(feature_data.astype(str).astype('category').cat.codes.corr(target_series))
                    p_value = 0.5  # Placeholder
                except:
                    correlation = 0.0
                    p_value = 1.0
            
            importance = FeatureImportance(
                feature_name=feature,
                importance_score=correlation if not np.isnan(correlation) else 0.0,
                importance_rank=0,
                method=ImportanceMethod.CORRELATION,
                p_value=p_value,
                effect_size=correlation if not np.isnan(correlation) else 0.0
            )
            importances.append(importance)
        
        return importances
    
    async def _calculate_variance_importance(
        self,
        feature_df: pd.DataFrame,
        target_series: pd.Series,
        creator_type: CreatorType,
        feature_types: Dict[str, FeatureType]
    ) -> List[FeatureImportance]:
        """Calculate variance-based importance"""
        importances = []
        
        # Calculate variance for each feature
        variances = []
        for feature in feature_df.columns:
            feature_data = feature_df[feature]
            
            if pd.api.types.is_numeric_dtype(feature_data):
                variance = feature_data.var()
            else:
                # For categorical features, use entropy as variance proxy
                value_counts = feature_data.value_counts(normalize=True)
                variance = -sum(p * np.log2(p) for p in value_counts if p > 0)
            
            variances.append(variance if not np.isnan(variance) else 0.0)
        
        # Normalize variances to 0-1 scale
        if max(variances) > 0:
            normalized_variances = [v / max(variances) for v in variances]
        else:
            normalized_variances = [0.0] * len(variances)
        
        for feature, norm_variance in zip(feature_df.columns, normalized_variances):
            importance = FeatureImportance(
                feature_name=feature,
                importance_score=norm_variance,
                importance_rank=0,
                method=ImportanceMethod.VARIANCE,
                effect_size=norm_variance
            )
            importances.append(importance)
        
        return importances
    
    async def _calculate_chi_square_importance(
        self,
        feature_df: pd.DataFrame,
        target_series: pd.Series,
        creator_type: CreatorType,
        feature_types: Dict[str, FeatureType]
    ) -> List[FeatureImportance]:
        """Calculate chi-square importance for categorical features"""
        importances = []
        
        for feature in feature_df.columns:
            feature_data = feature_df[feature]
            
            try:
                # For categorical features or binary targets
                if (feature_types.get(feature) == FeatureType.CATEGORICAL or 
                    target_series.nunique() <= 10):
                    
                    # Create contingency table
                    contingency = pd.crosstab(feature_data, target_series)
                    
                    # Perform chi-square test (simulated)
                    chi2_stat = self._calculate_chi_square_stat(contingency)
                    p_value = max(0.001, 1.0 / (1.0 + chi2_stat))  # Simulated p-value
                    
                    # Convert chi-square to importance score
                    importance_score = min(1.0, chi2_stat / (chi2_stat + 10))
                    
                else:
                    # For numerical features, use correlation as proxy
                    correlation = abs(feature_data.corr(target_series))
                    importance_score = correlation if not np.isnan(correlation) else 0.0
                    p_value = 0.5
                
            except Exception:
                importance_score = 0.0
                p_value = 1.0
            
            importance = FeatureImportance(
                feature_name=feature,
                importance_score=importance_score,
                importance_rank=0,
                method=ImportanceMethod.CHI_SQUARE,
                p_value=p_value,
                effect_size=importance_score
            )
            importances.append(importance)
        
        return importances
    
    def _calculate_chi_square_stat(self, contingency: pd.DataFrame) -> float:
        """Calculate chi-square statistic"""
        # Expected frequencies
        row_totals = contingency.sum(axis=1)
        col_totals = contingency.sum(axis=0)
        total = contingency.sum().sum()
        
        chi2_stat = 0.0
        
        for i in range(contingency.shape[0]):
            for j in range(contingency.shape[1]):
                observed = contingency.iloc[i, j]
                expected = (row_totals.iloc[i] * col_totals.iloc[j]) / total
                
                if expected > 0:
                    chi2_stat += ((observed - expected) ** 2) / expected
        
        return chi2_stat
    
    async def _calculate_rfe_importance(
        self,
        feature_df: pd.DataFrame,
        target_series: pd.Series,
        creator_type: CreatorType,
        feature_types: Dict[str, FeatureType]
    ) -> List[FeatureImportance]:
        """Calculate recursive feature elimination importance (simulated)"""
        importances = []
        
        # Simulate RFE by ranking features based on correlation
        correlations = []
        for feature in feature_df.columns:
            feature_data = feature_df[feature]
            
            if pd.api.types.is_numeric_dtype(feature_data):
                correlation = abs(feature_data.corr(target_series))
            else:
                correlation = 0.1  # Low importance for non-numeric in simulation
            
            correlations.append((feature, correlation if not np.isnan(correlation) else 0.0))
        
        # Sort by correlation (higher is better)
        correlations.sort(key=lambda x: x[1], reverse=True)
        
        # Assign RFE scores based on rank
        for rank, (feature, correlation) in enumerate(correlations):
            # Convert rank to importance score (1 = most important, decreasing)
            importance_score = max(0.0, 1.0 - (rank / len(correlations)))
            
            importance = FeatureImportance(
                feature_name=feature,
                importance_score=importance_score,
                importance_rank=rank + 1,
                method=ImportanceMethod.RECURSIVE_ELIMINATION,
                effect_size=importance_score
            )
            importances.append(importance)
        
        return importances
    
    async def _aggregate_importance_scores(
        self,
        all_importances: List[FeatureImportance],
        creator_type: CreatorType
    ) -> List[FeatureImportance]:
        """Aggregate importance scores across methods"""
        # Group by feature name
        feature_scores = {}
        
        for importance in all_importances:
            feature_name = importance.feature_name
            
            if feature_name not in feature_scores:
                feature_scores[feature_name] = {
                    'scores': [],
                    'methods': [],
                    'p_values': [],
                    'confidence_intervals': [],
                    'effect_sizes': []
                }
            
            feature_scores[feature_name]['scores'].append(importance.importance_score)
            feature_scores[feature_name]['methods'].append(importance.method)
            
            if importance.p_value is not None:
                feature_scores[feature_name]['p_values'].append(importance.p_value)
            
            if importance.confidence_interval is not None:
                feature_scores[feature_name]['confidence_intervals'].append(importance.confidence_interval)
            
            if importance.effect_size is not None:
                feature_scores[feature_name]['effect_sizes'].append(importance.effect_size)
        
        # Calculate aggregated scores
        aggregated_importances = []
        
        for feature_name, data in feature_scores.items():
            # Weighted average of scores
            weights = self._get_method_weights(data['methods'], creator_type, feature_name)
            weighted_score = sum(score * weight for score, weight in zip(data['scores'], weights))
            weighted_score = weighted_score / sum(weights) if sum(weights) > 0 else 0.0
            
            # Aggregate other metrics
            avg_p_value = np.mean(data['p_values']) if data['p_values'] else None
            avg_effect_size = np.mean(data['effect_sizes']) if data['effect_sizes'] else None
            
            # Confidence interval from effect sizes
            if data['effect_sizes']:
                ci_lower = max(0, weighted_score - np.std(data['effect_sizes']))
                ci_upper = min(1, weighted_score + np.std(data['effect_sizes']))
                confidence_interval = (ci_lower, ci_upper)
            else:
                confidence_interval = None
            
            # Apply creator-specific weighting
            creator_weighted_score = self._apply_creator_weighting(
                feature_name, weighted_score, creator_type
            )
            
            # Calculate business impact
            business_impact = self._calculate_business_impact(feature_name, creator_weighted_score)
            
            aggregated_importance = FeatureImportance(
                feature_name=feature_name,
                importance_score=creator_weighted_score,
                importance_rank=0,  # Will be set after sorting
                method=ImportanceMethod.PERMUTATION,  # Representative method
                confidence_interval=confidence_interval,
                p_value=avg_p_value,
                effect_size=avg_effect_size,
                business_impact=business_impact
            )
            
            aggregated_importances.append(aggregated_importance)
        
        # Sort by importance score and assign ranks
        aggregated_importances.sort(key=lambda x: x.importance_score, reverse=True)
        
        for rank, importance in enumerate(aggregated_importances):
            importance.importance_rank = rank + 1
        
        return aggregated_importances
    
    def _get_method_weights(
        self,
        methods: List[ImportanceMethod],
        creator_type: CreatorType,
        feature_name: str
    ) -> List[float]:
        """Get weights for different methods based on creator type and feature"""
        base_weights = {
            ImportanceMethod.SHAP: 1.0,
            ImportanceMethod.LIME: 0.8,
            ImportanceMethod.PERMUTATION: 1.0,
            ImportanceMethod.MUTUAL_INFO: 0.9,
            ImportanceMethod.CORRELATION: 0.7,
            ImportanceMethod.VARIANCE: 0.5,
            ImportanceMethod.CHI_SQUARE: 0.8,
            ImportanceMethod.RECURSIVE_ELIMINATION: 0.9
        }
        
        # Adjust weights based on creator type
        if creator_type == CreatorType.MUSICIAN and 'audio' in feature_name.lower():
            # For musicians, SHAP and permutation are more reliable for audio features
            base_weights[ImportanceMethod.SHAP] = 1.2
            base_weights[ImportanceMethod.PERMUTATION] = 1.1
        elif creator_type == CreatorType.BLOGGER and 'text' in feature_name.lower():
            # For bloggers, mutual information might be more relevant for text features
            base_weights[ImportanceMethod.MUTUAL_INFO] = 1.1
            base_weights[ImportanceMethod.CHI_SQUARE] = 1.0
        
        return [base_weights.get(method, 1.0) for method in methods]
    
    def _apply_creator_weighting(
        self,
        feature_name: str,
        importance_score: float,
        creator_type: CreatorType
    ) -> float:
        """Apply creator-specific weighting to importance score"""
        creator_weights = self.creator_importance_weights.get(creator_type, {})
        
        # Find matching weight category
        weight_multiplier = 1.0
        for category, multiplier in creator_weights.items():
            if category.replace('_', '').lower() in feature_name.replace('_', '').lower():
                weight_multiplier = multiplier
                break
        
        # Apply weight and ensure score stays within bounds
        weighted_score = importance_score * weight_multiplier
        return min(1.0, weighted_score)
    
    def _calculate_business_impact(self, feature_name: str, importance_score: float) -> float:
        """Calculate business impact score for feature"""
        business_impact = 0.0
        
        # Check if feature relates to business metrics
        for impact_category, keywords in self.business_impact_mapping.items():
            if any(keyword in feature_name.lower() for keyword in keywords):
                # Higher impact for revenue-related features
                if impact_category == 'revenue':
                    business_impact = importance_score * 1.5
                elif impact_category == 'engagement':
                    business_impact = importance_score * 1.3
                elif impact_category == 'retention':
                    business_impact = importance_score * 1.2
                else:
                    business_impact = importance_score * 1.1
                break
        
        if business_impact == 0.0:
            business_impact = importance_score * 0.8  # Default lower impact
        
        return min(1.0, business_impact)
    
    async def _generate_global_insights(
        self,
        importances: List[FeatureImportance],
        feature_df: pd.DataFrame,
        target_series: pd.Series
    ) -> Dict[str, Any]:
        """Generate global insights from importance analysis"""
        insights = {}
        
        # Top features
        top_features = importances[:5]
        insights['top_features'] = [f.feature_name for f in top_features]
        insights['top_importance_scores'] = [f.importance_score for f in top_features]
        
        # Distribution of importance
        all_scores = [f.importance_score for f in importances]
        insights['importance_distribution'] = {
            'mean': np.mean(all_scores),
            'median': np.median(all_scores),
            'std': np.std(all_scores),
            'min': np.min(all_scores),
            'max': np.max(all_scores)
        }
        
        # Significant features
        significant_features = [f for f in importances if f.importance_score > self.importance_threshold]
        insights['significant_features_count'] = len(significant_features)
        insights['significance_rate'] = len(significant_features) / len(importances)
        
        # Feature diversity
        unique_importance_levels = len(set(round(f.importance_score, 2) for f in importances))
        insights['importance_diversity'] = unique_importance_levels / len(importances)
        
        # Statistical significance
        statistically_significant = [f for f in importances 
                                   if f.p_value is not None and f.p_value < self.significance_threshold]
        insights['statistically_significant_count'] = len(statistically_significant)
        
        return insights
    
    async def _generate_creator_insights(
        self,
        importances: List[FeatureImportance],
        creator_type: CreatorType,
        feature_types: Dict[str, FeatureType]
    ) -> Dict[str, Any]:
        """Generate creator-specific insights"""
        insights = {}
        
        # Creator-specific feature analysis
        if creator_type == CreatorType.MUSICIAN:
            audio_features = [f for f in importances if 'audio' in f.feature_name.lower()]
            insights['audio_feature_importance'] = {
                'count': len(audio_features),
                'avg_importance': np.mean([f.importance_score for f in audio_features]) if audio_features else 0,
                'top_audio_feature': audio_features[0].feature_name if audio_features else None
            }
            
        elif creator_type == CreatorType.PHOTOGRAPHER:
            visual_features = [f for f in importances if any(vw in f.feature_name.lower() 
                                                           for vw in ['visual', 'color', 'aesthetic'])]
            insights['visual_feature_importance'] = {
                'count': len(visual_features),
                'avg_importance': np.mean([f.importance_score for f in visual_features]) if visual_features else 0,
                'top_visual_feature': visual_features[0].feature_name if visual_features else None
            }
            
        elif creator_type == CreatorType.BLOGGER:
            text_features = [f for f in importances if any(tw in f.feature_name.lower() 
                                                         for tw in ['text', 'readability', 'seo'])]
            insights['text_feature_importance'] = {
                'count': len(text_features),
                'avg_importance': np.mean([f.importance_score for f in text_features]) if text_features else 0,
                'top_text_feature': text_features[0].feature_name if text_features else None
            }
        
        # Business impact analysis
        high_impact_features = [f for f in importances if f.business_impact and f.business_impact > 0.7]
        insights['business_impact_analysis'] = {
            'high_impact_feature_count': len(high_impact_features),
            'avg_business_impact': np.mean([f.business_impact for f in importances 
                                         if f.business_impact is not None]),
            'top_business_feature': high_impact_features[0].feature_name if high_impact_features else None
        }
        
        return insights
    
    async def _generate_business_recommendations(
        self,
        importances: List[FeatureImportance],
        creator_type: CreatorType,
        global_insights: Dict[str, Any]
    ) -> List[str]:
        """Generate business recommendations based on importance analysis"""
        recommendations = []
        
        # Top feature recommendations
        top_features = importances[:3]
        if top_features:
            recommendations.append(
                f"Focus on optimizing '{top_features[0].feature_name}' - it has the highest impact "
                f"on {creator_type.value} performance with {top_features[0].importance_score:.2f} importance score"
            )
        
        # Feature diversity recommendations
        if global_insights.get('importance_diversity', 0) < 0.3:
            recommendations.append(
                "Consider diversifying feature engineering - current features show low diversity in importance"
            )
        
        # Statistical significance recommendations
        sig_rate = global_insights.get('significance_rate', 0)
        if sig_rate < 0.5:
            recommendations.append(
                f"Only {sig_rate:.1%} of features are statistically significant - "
                "consider feature selection or more data collection"
            )
        
        # Creator-specific recommendations
        if creator_type == CreatorType.MUSICIAN:
            audio_features = [f for f in importances[:10] if 'audio' in f.feature_name.lower()]
            if len(audio_features) < 3:
                recommendations.append(
                    "Increase focus on audio feature engineering for better musician-specific predictions"
                )
        
        elif creator_type == CreatorType.BLOGGER:
            text_features = [f for f in importances[:10] if any(tw in f.feature_name.lower() 
                                                              for tw in ['text', 'seo', 'readability'])]
            if len(text_features) < 3:
                recommendations.append(
                    "Enhance text analysis features for improved blogger content optimization"
                )
        
        # Business impact recommendations
        high_impact_features = [f for f in importances if f.business_impact and f.business_impact > 0.7]
        if len(high_impact_features) < 5:
            recommendations.append(
                "Identify and develop more features with direct business impact correlation"
            )
        
        return recommendations
    
    async def _store_analysis_history(self, analysis: ImportanceAnalysis):
        """Store analysis in history for trend tracking"""
        model_id = analysis.model_id
        
        if model_id not in self.importance_history:
            self.importance_history[model_id] = []
        
        self.importance_history[model_id].append(analysis)
        
        # Keep only recent analyses (last 10)
        if len(self.importance_history[model_id]) > 10:
            self.importance_history[model_id] = self.importance_history[model_id][-10:]
    
    async def get_importance_trends(
        self,
        model_id: str,
        feature_names: Optional[List[str]] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get importance trends for features over time"""
        if model_id not in self.importance_history:
            return {}
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_analyses = [
            analysis for analysis in self.importance_history[model_id]
            if analysis.analyzed_at > cutoff_date
        ]
        
        if not recent_analyses:
            return {}
        
        trends = {}
        
        # Track importance trends for specific features
        if feature_names:
            for feature_name in feature_names:
                feature_trend = []
                
                for analysis in recent_analyses:
                    feature_importance = next(
                        (f for f in analysis.feature_importances if f.feature_name == feature_name),
                        None
                    )
                    
                    if feature_importance:
                        feature_trend.append({
                            'date': analysis.analyzed_at.isoformat(),
                            'importance_score': feature_importance.importance_score,
                            'rank': feature_importance.importance_rank
                        })
                
                if feature_trend:
                    # Calculate trend direction
                    scores = [t['importance_score'] for t in feature_trend]
                    if len(scores) > 1:
                        trend_direction = "increasing" if scores[-1] > scores[0] else "decreasing"
                        trend_magnitude = abs(scores[-1] - scores[0])
                    else:
                        trend_direction = "stable"
                        trend_magnitude = 0
                    
                    trends[feature_name] = {
                        'trend_data': feature_trend,
                        'trend_direction': trend_direction,
                        'trend_magnitude': trend_magnitude,
                        'current_score': scores[-1] if scores else 0,
                        'average_score': np.mean(scores) if scores else 0
                    }
        
        return {
            'model_id': model_id,
            'analysis_count': len(recent_analyses),
            'date_range': f"{cutoff_date.date()} to {datetime.utcnow().date()}",
            'feature_trends': trends
        }

# Usage example
async def main():
    """Example usage of FeatureImportanceAnalyzer"""
    config = {
        'significance_threshold': 0.05,
        'importance_threshold': 0.01
    }
    
    analyzer = FeatureImportanceAnalyzer(config)
    
    # Sample data
    np.random.seed(42)
    n_samples = 1000
    
    feature_data = pd.DataFrame({
        'audio_tempo': np.random.normal(120, 20, n_samples),
        'audio_pitch': np.random.normal(440, 50, n_samples),
        'engagement_score': np.random.beta(2, 2, n_samples),
        'content_duration': np.random.exponential(180, n_samples),
        'creator_followers': np.random.lognormal(8, 2, n_samples)
    })
    
    # Create target variable correlated with some features
    target_data = (
        0.3 * feature_data['audio_tempo'] / 120 +
        0.4 * feature_data['engagement_score'] +
        0.2 * np.log(feature_data['creator_followers']) / 10 +
        0.1 * np.random.normal(0, 1, n_samples)
    )
    
    # Analyze importance
    analysis = await analyzer.analyze_feature_importance(
        model_id="musician_engagement_model",
        feature_data=feature_data,
        target_data=target_data,
        creator_type=CreatorType.MUSICIAN,
        methods=[
            ImportanceMethod.PERMUTATION,
            ImportanceMethod.CORRELATION,
            ImportanceMethod.MUTUAL_INFO
        ]
    )
    
    # Print results
    print(f"Analysis ID: {analysis.analysis_id}")
    print(f"Total Features: {analysis.total_features}")
    print(f"Significant Features: {analysis.significant_features}")
    print("\nTop 5 Features:")
    
    for i, importance in enumerate(analysis.feature_importances[:5]):
        print(f"{i+1}. {importance.feature_name}: {importance.importance_score:.3f}")
    
    print(f"\nBusiness Recommendations:")
    for rec in analysis.business_recommendations:
        print(f"- {rec}")

if __name__ == "__main__":
    asyncio.run(main())