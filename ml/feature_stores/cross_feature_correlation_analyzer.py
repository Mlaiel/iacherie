"""🔗 Cross Feature Correlation Analyzer - Enterprise ML Infrastructure
=======================================================================
Module: ml/feature_stores/cross_feature_correlation_analyzer.py
Author: Fahed Mlaiel (mlaiel@live.de)
=======================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 FEATURE CORRELATION ANALYSIS & REDUNDANCY ELIMINATION
Feature correlation analysis and redundancy elimination for optimal model performance
- Multi-method correlation analysis
- Creator-specific correlation patterns
- Automated redundancy detection
- Feature interaction analysis
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, kendalltau
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif
from sklearn.metrics import adjusted_mutual_info_score
import seaborn as sns
import matplotlib.pyplot as plt
import networkx as nx

logger = logging.getLogger(__name__)


class CorrelationMethod(Enum):
    """Correlation analysis methods"""
    PEARSON = "pearson"
    SPEARMAN = "spearman"
    KENDALL = "kendall"
    MUTUAL_INFO = "mutual_info"
    DISTANCE_CORRELATION = "distance_correlation"
    MAXIMAL_INFO_COEFFICIENT = "mic"
    CREATOR_SPECIFIC = "creator_specific"


class FeatureType(Enum):
    """Feature types for analysis"""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    ORDINAL = "ordinal"
    BINARY = "binary"
    TEXT = "text"
    TEMPORAL = "temporal"
    CREATOR_SPECIFIC = "creator_specific"


class RedundancyLevel(Enum):
    """Redundancy levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


@dataclass
class CorrelationPair:
    """Feature correlation pair"""
    feature_1: str
    feature_2: str
    correlation_value: float
    correlation_method: CorrelationMethod
    p_value: Optional[float] = None
    confidence_interval: Optional[Tuple[float, float]] = None
    sample_size: int = 0
    feature_types: Tuple[FeatureType, FeatureType] = (FeatureType.NUMERICAL, FeatureType.NUMERICAL)


@dataclass
class RedundancyGroup:
    """Group of redundant features"""
    group_id: str
    features: List[str]
    redundancy_level: RedundancyLevel
    correlation_matrix: Dict[str, Dict[str, float]]
    recommended_action: str
    representative_feature: Optional[str] = None
    elimination_candidates: List[str] = field(default_factory=list)


@dataclass
class CorrelationAnalysis:
    """Complete correlation analysis result"""
    analysis_id: str
    dataset_info: Dict[str, Any]
    correlation_matrix: pd.DataFrame
    correlation_pairs: List[CorrelationPair]
    redundancy_groups: List[RedundancyGroup]
    feature_importance_scores: Dict[str, float]
    recommendations: List[str]
    analysis_time: float
    creator_specific_insights: Dict[str, Any] = field(default_factory=dict)


class CrossFeatureCorrelationAnalyzer:
    """Enterprise Cross Feature Correlation Analyzer"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        
        # Configuration
        self.correlation_threshold = self.config.get('correlation_threshold', 0.8)
        self.p_value_threshold = self.config.get('p_value_threshold', 0.05)
        self.min_sample_size = self.config.get('min_sample_size', 100)
        self.enable_visualization = self.config.get('enable_visualization', True)
        
        # Creator-specific thresholds
        self.creator_thresholds = {
            'musician': 0.75,
            'blogger': 0.8,
            'photographer': 0.85,
            'influencer': 0.7,
            'comedian': 0.8
        }
        
        # Analysis history
        self.analysis_history: List[CorrelationAnalysis] = []
        self.feature_patterns: Dict[str, List[float]] = {}
        
        # Performance metrics
        self.analysis_metrics = {
            'total_analyses': 0,
            'features_analyzed': 0,
            'redundancies_found': 0,
            'correlations_computed': 0,
            'average_analysis_time': 0.0
        }
        
        logger.info("🔗 Cross Feature Correlation Analyzer initialized")
    
    async def analyze_correlations(
        self,
        data: pd.DataFrame,
        target_column: Optional[str] = None,
        creator_type: Optional[str] = None,
        methods: Optional[List[CorrelationMethod]] = None,
        feature_types: Optional[Dict[str, FeatureType]] = None
    ) -> CorrelationAnalysis:
        """Comprehensive correlation analysis"""
        try:
            start_time = time.time()
            analysis_id = str(uuid.uuid4())
            
            # Default methods
            if methods is None:
                methods = [CorrelationMethod.PEARSON, CorrelationMethod.SPEARMAN, CorrelationMethod.MUTUAL_INFO]
            
            # Infer feature types if not provided
            if feature_types is None:
                feature_types = await self._infer_feature_types(data)
            
            logger.info(f"🔍 Starting correlation analysis: {analysis_id}")
            
            # Dataset information
            dataset_info = {
                'num_features': len(data.columns),
                'num_samples': len(data),
                'feature_types': {col: ftype.value for col, ftype in feature_types.items()},
                'missing_values': data.isnull().sum().to_dict(),
                'creator_type': creator_type
            }
            
            # Compute correlation matrix for each method
            correlation_matrices = {}
            all_correlation_pairs = []
            
            for method in methods:
                matrix = await self._compute_correlation_matrix(data, method, feature_types)
                correlation_matrices[method] = matrix
                
                # Extract correlation pairs
                pairs = await self._extract_correlation_pairs(matrix, method, feature_types)
                all_correlation_pairs.extend(pairs)
            
            # Use primary method for main matrix
            primary_method = methods[0]
            main_correlation_matrix = correlation_matrices[primary_method]
            
            # Detect redundancy groups
            redundancy_groups = await self._detect_redundancy_groups(
                main_correlation_matrix, creator_type
            )
            
            # Calculate feature importance if target provided
            feature_importance = {}
            if target_column and target_column in data.columns:
                feature_importance = await self._calculate_feature_importance(
                    data, target_column, feature_types
                )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                redundancy_groups, feature_importance, creator_type
            )
            
            # Creator-specific insights
            creator_insights = await self._analyze_creator_patterns(
                data, correlation_matrices, creator_type
            )
            
            analysis_time = time.time() - start_time
            
            # Create analysis result
            analysis = CorrelationAnalysis(
                analysis_id=analysis_id,
                dataset_info=dataset_info,
                correlation_matrix=main_correlation_matrix,
                correlation_pairs=all_correlation_pairs,
                redundancy_groups=redundancy_groups,
                feature_importance_scores=feature_importance,
                recommendations=recommendations,
                analysis_time=analysis_time,
                creator_specific_insights=creator_insights
            )
            
            # Store in history
            self.analysis_history.append(analysis)
            if len(self.analysis_history) > 100:
                self.analysis_history = self.analysis_history[-100:]
            
            # Update metrics
            await self._update_metrics(analysis)
            
            logger.info(f"✅ Correlation analysis completed: {analysis_id} ({analysis_time:.2f}s)")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error in correlation analysis: {e}")
            raise
    
    async def find_feature_interactions(
        self,
        data: pd.DataFrame,
        target_column: str,
        max_interaction_degree: int = 2
    ) -> Dict[str, Any]:
        """Find feature interactions"""
        try:
            interactions = {
                'pairwise_interactions': [],
                'higher_order_interactions': [],
                'interaction_strength': {}
            }
            
            features = [col for col in data.columns if col != target_column]
            
            # Pairwise interactions
            for i, feat1 in enumerate(features):
                for feat2 in features[i+1:]:
                    interaction_strength = await self._calculate_interaction_strength(
                        data, feat1, feat2, target_column
                    )
                    
                    if interaction_strength > 0.1:  # Threshold for significance
                        interactions['pairwise_interactions'].append({
                            'feature_1': feat1,
                            'feature_2': feat2,
                            'strength': interaction_strength
                        })
            
            # Sort by interaction strength
            interactions['pairwise_interactions'].sort(
                key=lambda x: x['strength'], reverse=True
            )
            
            return interactions
            
        except Exception as e:
            logger.error(f"❌ Error finding feature interactions: {e}")
            return {}
    
    async def eliminate_redundant_features(
        self,
        data: pd.DataFrame,
        analysis: CorrelationAnalysis,
        strategy: str = "keep_most_important"
    ) -> Tuple[pd.DataFrame, List[str]]:
        """Eliminate redundant features from dataset"""
        try:
            eliminated_features = []
            
            for group in analysis.redundancy_groups:
                if group.redundancy_level in [RedundancyLevel.HIGH, RedundancyLevel.EXTREME]:
                    if strategy == "keep_most_important":
                        # Keep feature with highest importance score
                        if analysis.feature_importance_scores:
                            importance_scores = {
                                feat: analysis.feature_importance_scores.get(feat, 0)
                                for feat in group.features
                            }
                            keep_feature = max(importance_scores, key=importance_scores.get)
                        else:
                            # Keep first feature
                            keep_feature = group.features[0]
                        
                        # Eliminate others
                        for feat in group.features:
                            if feat != keep_feature:
                                eliminated_features.append(feat)
                    
                    elif strategy == "keep_representative":
                        # Keep representative feature
                        if group.representative_feature:
                            for feat in group.features:
                                if feat != group.representative_feature:
                                    eliminated_features.append(feat)
                        else:
                            # Keep first feature as fallback
                            for feat in group.features[1:]:
                                eliminated_features.append(feat)
                    
                    elif strategy == "eliminate_candidates":
                        # Eliminate pre-identified candidates
                        eliminated_features.extend(group.elimination_candidates)
            
            # Remove duplicates
            eliminated_features = list(set(eliminated_features))
            
            # Create new dataset
            remaining_features = [col for col in data.columns if col not in eliminated_features]
            reduced_data = data[remaining_features].copy()
            
            logger.info(f"✅ Eliminated {len(eliminated_features)} redundant features")
            return reduced_data, eliminated_features
            
        except Exception as e:
            logger.error(f"❌ Error eliminating redundant features: {e}")
            return data, []
    
    async def visualize_correlations(
        self,
        analysis: CorrelationAnalysis,
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Create correlation visualization"""
        try:
            if not self.enable_visualization:
                return None
            
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            # Set up the matplotlib figure
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Feature Correlation Analysis', fontsize=16)
            
            # 1. Correlation heatmap
            ax1 = axes[0, 0]
            mask = np.triu(np.ones_like(analysis.correlation_matrix, dtype=bool))
            sns.heatmap(analysis.correlation_matrix, mask=mask, annot=True, 
                       cmap='coolwarm', center=0, ax=ax1)
            ax1.set_title('Correlation Heatmap')
            
            # 2. Correlation distribution
            ax2 = axes[0, 1]
            correlations = analysis.correlation_matrix.values[np.triu_indices_from(analysis.correlation_matrix.values, k=1)]
            ax2.hist(correlations, bins=30, alpha=0.7, edgecolor='black')
            ax2.set_title('Correlation Distribution')
            ax2.set_xlabel('Correlation Coefficient')
            ax2.set_ylabel('Frequency')
            
            # 3. High correlation pairs
            ax3 = axes[1, 0]
            high_corr_pairs = [
                pair for pair in analysis.correlation_pairs
                if abs(pair.correlation_value) > self.correlation_threshold
            ]
            
            if high_corr_pairs:
                pair_names = [f"{pair.feature_1[:10]}...{pair.feature_2[:10]}" 
                             for pair in high_corr_pairs[:10]]
                correlations = [pair.correlation_value for pair in high_corr_pairs[:10]]
                
                bars = ax3.bar(range(len(pair_names)), correlations)
                ax3.set_xticks(range(len(pair_names)))
                ax3.set_xticklabels(pair_names, rotation=45, ha='right')
                ax3.set_title('Top High Correlations')
                ax3.set_ylabel('Correlation')
                
                # Color bars by correlation strength
                for bar, corr in zip(bars, correlations):
                    bar.set_color('red' if abs(corr) > 0.9 else 'orange' if abs(corr) > 0.8 else 'yellow')
            
            # 4. Redundancy groups
            ax4 = axes[1, 1]
            redundancy_levels = [group.redundancy_level.value for group in analysis.redundancy_groups]
            if redundancy_levels:
                level_counts = pd.Series(redundancy_levels).value_counts()
                ax4.pie(level_counts.values, labels=level_counts.index, autopct='%1.1f%%')
                ax4.set_title('Redundancy Levels Distribution')
            else:
                ax4.text(0.5, 0.5, 'No Redundancy Groups Found', 
                        ha='center', va='center', transform=ax4.transAxes)
                ax4.set_title('Redundancy Groups')
            
            plt.tight_layout()
            
            # Save if path provided
            if output_path:
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                logger.info(f"📊 Visualization saved: {output_path}")
                plt.close()
                return output_path
            
            return "visualization_created"
            
        except Exception as e:
            logger.error(f"❌ Error creating visualization: {e}")
            return None
    
    async def _infer_feature_types(self, data: pd.DataFrame) -> Dict[str, FeatureType]:
        """Infer feature types from data"""
        try:
            feature_types = {}
            
            for column in data.columns:
                if data[column].dtype in ['int64', 'float64']:
                    # Check if binary
                    unique_values = data[column].unique()
                    if len(unique_values) == 2 and set(unique_values).issubset({0, 1, True, False}):
                        feature_types[column] = FeatureType.BINARY
                    else:
                        feature_types[column] = FeatureType.NUMERICAL
                elif data[column].dtype == 'object':
                    # Check if ordinal (has ordering)
                    unique_count = data[column].nunique()
                    if unique_count <= 10:  # Arbitrary threshold
                        feature_types[column] = FeatureType.CATEGORICAL
                    else:
                        feature_types[column] = FeatureType.TEXT
                elif data[column].dtype == 'datetime64[ns]':
                    feature_types[column] = FeatureType.TEMPORAL
                else:
                    feature_types[column] = FeatureType.CATEGORICAL
            
            return feature_types
            
        except Exception as e:
            logger.error(f"❌ Error inferring feature types: {e}")
            return {}
    
    async def _compute_correlation_matrix(
        self,
        data: pd.DataFrame,
        method: CorrelationMethod,
        feature_types: Dict[str, FeatureType]
    ) -> pd.DataFrame:
        """Compute correlation matrix using specified method"""
        try:
            # Filter to numerical features for most methods
            if method in [CorrelationMethod.PEARSON, CorrelationMethod.SPEARMAN, CorrelationMethod.KENDALL]:
                numerical_features = [
                    col for col, ftype in feature_types.items()
                    if ftype in [FeatureType.NUMERICAL, FeatureType.BINARY]
                ]
                subset_data = data[numerical_features]
                
                if method == CorrelationMethod.PEARSON:
                    corr_matrix = subset_data.corr(method='pearson')
                elif method == CorrelationMethod.SPEARMAN:
                    corr_matrix = subset_data.corr(method='spearman')
                elif method == CorrelationMethod.KENDALL:
                    corr_matrix = subset_data.corr(method='kendall')
                
            elif method == CorrelationMethod.MUTUAL_INFO:
                # Mutual information for all feature types
                features = list(data.columns)
                n_features = len(features)
                
                # Initialize matrix
                mi_matrix = np.zeros((n_features, n_features))
                
                for i, feat1 in enumerate(features):
                    for j, feat2 in enumerate(features):
                        if i == j:
                            mi_matrix[i, j] = 1.0
                        elif i < j:
                            # Calculate mutual information
                            mi_score = await self._calculate_mutual_info(
                                data[feat1], data[feat2]
                            )
                            mi_matrix[i, j] = mi_score
                            mi_matrix[j, i] = mi_score
                
                corr_matrix = pd.DataFrame(mi_matrix, index=features, columns=features)
            
            else:
                # Default to Pearson
                corr_matrix = data.corr(method='pearson')
            
            return corr_matrix.fillna(0)
            
        except Exception as e:
            logger.error(f"❌ Error computing correlation matrix: {e}")
            # Return identity matrix as fallback
            features = list(data.columns)
            return pd.DataFrame(np.eye(len(features)), index=features, columns=features)
    
    async def _calculate_mutual_info(self, x: pd.Series, y: pd.Series) -> float:
        """Calculate mutual information between two features"""
        try:
            # Handle missing values
            mask = ~(x.isna() | y.isna())
            x_clean = x[mask]
            y_clean = y[mask]
            
            if len(x_clean) < 2:
                return 0.0
            
            # Convert to numerical if needed
            if x_clean.dtype == 'object':
                x_encoded = pd.Categorical(x_clean).codes
            else:
                x_encoded = x_clean.values
            
            if y_clean.dtype == 'object':
                y_encoded = pd.Categorical(y_clean).codes
            else:
                y_encoded = y_clean.values
            
            # Calculate mutual information
            x_reshaped = x_encoded.reshape(-1, 1)
            mi_score = mutual_info_regression(x_reshaped, y_encoded)[0]
            
            # Normalize to [0, 1]
            return min(mi_score, 1.0)
            
        except Exception as e:
            logger.error(f"❌ Error calculating mutual info: {e}")
            return 0.0
    
    async def _extract_correlation_pairs(
        self,
        correlation_matrix: pd.DataFrame,
        method: CorrelationMethod,
        feature_types: Dict[str, FeatureType]
    ) -> List[CorrelationPair]:
        """Extract correlation pairs from matrix"""
        try:
            pairs = []
            features = correlation_matrix.columns
            
            for i, feat1 in enumerate(features):
                for feat2 in features[i+1:]:
                    correlation_value = correlation_matrix.loc[feat1, feat2]
                    
                    if not np.isnan(correlation_value):
                        pair = CorrelationPair(
                            feature_1=feat1,
                            feature_2=feat2,
                            correlation_value=correlation_value,
                            correlation_method=method,
                            feature_types=(
                                feature_types.get(feat1, FeatureType.NUMERICAL),
                                feature_types.get(feat2, FeatureType.NUMERICAL)
                            )
                        )
                        pairs.append(pair)
            
            return pairs
            
        except Exception as e:
            logger.error(f"❌ Error extracting correlation pairs: {e}")
            return []
    
    async def _detect_redundancy_groups(
        self,
        correlation_matrix: pd.DataFrame,
        creator_type: Optional[str]
    ) -> List[RedundancyGroup]:
        """Detect groups of redundant features"""
        try:
            redundancy_groups = []
            
            # Get correlation threshold for creator type
            threshold = self.creator_thresholds.get(creator_type, self.correlation_threshold)
            
            # Create adjacency matrix for highly correlated features
            features = correlation_matrix.columns
            adj_matrix = (np.abs(correlation_matrix.values) > threshold) & (correlation_matrix.values != 1.0)
            
            # Use networkx to find connected components
            G = nx.from_numpy_array(adj_matrix)
            node_mapping = {i: features[i] for i in range(len(features))}
            G = nx.relabel_nodes(G, node_mapping)
            
            # Find connected components (redundancy groups)
            connected_components = list(nx.connected_components(G))
            
            for i, component in enumerate(connected_components):
                if len(component) > 1:  # Only groups with multiple features
                    component_features = list(component)
                    
                    # Calculate redundancy level
                    group_correlations = []
                    correlation_dict = {}
                    
                    for feat1 in component_features:
                        correlation_dict[feat1] = {}
                        for feat2 in component_features:
                            if feat1 != feat2:
                                corr_val = correlation_matrix.loc[feat1, feat2]
                                correlation_dict[feat1][feat2] = corr_val
                                group_correlations.append(abs(corr_val))
                    
                    avg_correlation = np.mean(group_correlations) if group_correlations else 0
                    redundancy_level = self._classify_redundancy_level(avg_correlation)
                    
                    # Select representative feature (highest average correlation)
                    feature_avg_corrs = {}
                    for feat in component_features:
                        other_corrs = [
                            abs(correlation_matrix.loc[feat, other])
                            for other in component_features if other != feat
                        ]
                        feature_avg_corrs[feat] = np.mean(other_corrs) if other_corrs else 0
                    
                    representative_feature = max(feature_avg_corrs, key=feature_avg_corrs.get)
                    
                    # Identify elimination candidates (all except representative)
                    elimination_candidates = [f for f in component_features if f != representative_feature]
                    
                    group = RedundancyGroup(
                        group_id=f"redundancy_group_{i}",
                        features=component_features,
                        redundancy_level=redundancy_level,
                        correlation_matrix=correlation_dict,
                        recommended_action=f"Keep {representative_feature}, eliminate others",
                        representative_feature=representative_feature,
                        elimination_candidates=elimination_candidates
                    )
                    
                    redundancy_groups.append(group)
            
            return redundancy_groups
            
        except Exception as e:
            logger.error(f"❌ Error detecting redundancy groups: {e}")
            return []
    
    def _classify_redundancy_level(self, avg_correlation: float) -> RedundancyLevel:
        """Classify redundancy level based on correlation"""
        if avg_correlation >= 0.95:
            return RedundancyLevel.EXTREME
        elif avg_correlation >= 0.85:
            return RedundancyLevel.HIGH
        elif avg_correlation >= 0.7:
            return RedundancyLevel.MEDIUM
        elif avg_correlation >= 0.5:
            return RedundancyLevel.LOW
        else:
            return RedundancyLevel.NONE
    
    async def _calculate_feature_importance(
        self,
        data: pd.DataFrame,
        target_column: str,
        feature_types: Dict[str, FeatureType]
    ) -> Dict[str, float]:
        """Calculate feature importance scores"""
        try:
            importance_scores = {}
            features = [col for col in data.columns if col != target_column]
            
            X = data[features]
            y = data[target_column]
            
            # Simple correlation-based importance for numerical features
            for feature in features:
                if feature_types.get(feature) in [FeatureType.NUMERICAL, FeatureType.BINARY]:
                    try:
                        correlation = np.corrcoef(X[feature].fillna(0), y.fillna(0))[0, 1]
                        importance_scores[feature] = abs(correlation) if not np.isnan(correlation) else 0
                    except:
                        importance_scores[feature] = 0
                else:
                    # For categorical features, use mutual information
                    try:
                        mi_score = await self._calculate_mutual_info(X[feature], y)
                        importance_scores[feature] = mi_score
                    except:
                        importance_scores[feature] = 0
            
            return importance_scores
            
        except Exception as e:
            logger.error(f"❌ Error calculating feature importance: {e}")
            return {}
    
    async def _calculate_interaction_strength(
        self,
        data: pd.DataFrame,
        feat1: str,
        feat2: str,
        target: str
    ) -> float:
        """Calculate interaction strength between two features"""
        try:
            # Simple interaction: correlation of product with target
            x1 = data[feat1].fillna(0)
            x2 = data[feat2].fillna(0)
            y = data[target].fillna(0)
            
            # Create interaction term
            interaction = x1 * x2
            
            # Calculate correlation with target
            interaction_corr = np.corrcoef(interaction, y)[0, 1]
            
            # Calculate individual correlations
            corr1 = np.corrcoef(x1, y)[0, 1]
            corr2 = np.corrcoef(x2, y)[0, 1]
            
            # Interaction strength is additional predictive power
            if not (np.isnan(interaction_corr) or np.isnan(corr1) or np.isnan(corr2)):
                return max(0, abs(interaction_corr) - max(abs(corr1), abs(corr2)))
            else:
                return 0
            
        except Exception as e:
            logger.error(f"❌ Error calculating interaction strength: {e}")
            return 0
    
    async def _generate_recommendations(
        self,
        redundancy_groups: List[RedundancyGroup],
        feature_importance: Dict[str, float],
        creator_type: Optional[str]
    ) -> List[str]:
        """Generate recommendations based on analysis"""
        try:
            recommendations = []
            
            # Redundancy recommendations
            high_redundancy_groups = [
                group for group in redundancy_groups
                if group.redundancy_level in [RedundancyLevel.HIGH, RedundancyLevel.EXTREME]
            ]
            
            if high_redundancy_groups:
                recommendations.append(
                    f"Found {len(high_redundancy_groups)} high-redundancy feature groups. "
                    "Consider feature elimination to reduce dimensionality."
                )
                
                for group in high_redundancy_groups[:3]:  # Top 3 groups
                    recommendations.append(
                        f"Group {group.group_id}: Keep '{group.representative_feature}', "
                        f"eliminate {len(group.elimination_candidates)} redundant features."
                    )
            
            # Feature importance recommendations
            if feature_importance:
                low_importance_features = [
                    feat for feat, score in feature_importance.items()
                    if score < 0.1
                ]
                
                if low_importance_features:
                    recommendations.append(
                        f"Consider removing {len(low_importance_features)} low-importance features "
                        "to reduce noise and improve model performance."
                    )
            
            # Creator-specific recommendations
            if creator_type:
                if creator_type == 'musician':
                    recommendations.append(
                        "For music content, focus on temporal and spectral features. "
                        "Audio correlation patterns may indicate genre-specific characteristics."
                    )
                elif creator_type == 'blogger':
                    recommendations.append(
                        "For blog content, text-based features may show high correlation. "
                        "Consider topic modeling to reduce text feature redundancy."
                    )
                elif creator_type == 'photographer':
                    recommendations.append(
                        "For visual content, color and composition features may correlate. "
                        "Consider principal component analysis for image features."
                    )
            
            if not recommendations:
                recommendations.append("No significant redundancies found. Feature set appears well-balanced.")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error generating recommendations: {e}")
            return ["Analysis completed with errors. Manual review recommended."]
    
    async def _analyze_creator_patterns(
        self,
        data: pd.DataFrame,
        correlation_matrices: Dict[CorrelationMethod, pd.DataFrame],
        creator_type: Optional[str]
    ) -> Dict[str, Any]:
        """Analyze creator-specific correlation patterns"""
        try:
            insights = {}
            
            if not creator_type:
                return insights
            
            # Creator-specific feature patterns
            creator_features = [col for col in data.columns if creator_type in col.lower()]
            
            if creator_features:
                insights['creator_specific_features'] = len(creator_features)
                
                # Analyze correlations among creator features
                if len(creator_features) > 1:
                    creator_corr_matrix = data[creator_features].corr()
                    high_corr_pairs = []
                    
                    for i, feat1 in enumerate(creator_features):
                        for feat2 in creator_features[i+1:]:
                            corr_val = creator_corr_matrix.loc[feat1, feat2]
                            if abs(corr_val) > 0.7:
                                high_corr_pairs.append((feat1, feat2, corr_val))
                    
                    insights['high_correlation_creator_pairs'] = len(high_corr_pairs)
            
            # Creator-specific correlation threshold analysis
            threshold = self.creator_thresholds.get(creator_type, self.correlation_threshold)
            main_matrix = list(correlation_matrices.values())[0]
            
            high_corr_count = np.sum(np.abs(main_matrix.values) > threshold) - len(main_matrix)
            total_pairs = (len(main_matrix) * (len(main_matrix) - 1)) // 2
            
            insights['high_correlation_ratio'] = high_corr_count / total_pairs if total_pairs > 0 else 0
            insights['creator_threshold_used'] = threshold
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error analyzing creator patterns: {e}")
            return {}
    
    async def _update_metrics(self, analysis -> None: CorrelationAnalysis) -> None:
        """Update analysis metrics"""
        try:
            self.analysis_metrics['total_analyses'] += 1
            self.analysis_metrics['features_analyzed'] += analysis.dataset_info['num_features']
            self.analysis_metrics['redundancies_found'] += len(analysis.redundancy_groups)
            self.analysis_metrics['correlations_computed'] += len(analysis.correlation_pairs)
            
            # Update average analysis time
            total = self.analysis_metrics['total_analyses']
            current_avg = self.analysis_metrics['average_analysis_time']
            new_avg = (current_avg * (total - 1) + analysis.analysis_time) / total
            self.analysis_metrics['average_analysis_time'] = new_avg
            
        except Exception as e:
            logger.error(f"❌ Error updating metrics: {e}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get analyzer metrics"""
        return {
            **self.analysis_metrics,
            'analysis_history_size': len(self.analysis_history),
            'creator_thresholds': self.creator_thresholds
        }


# Global instance
correlation_analyzer = CrossFeatureCorrelationAnalyzer()


async def main() -> None:
    """Test the Cross Feature Correlation Analyzer"""
    analyzer = CrossFeatureCorrelationAnalyzer()
    
    print("🔗 Testing Cross Feature Correlation Analyzer...")
    
    # Create sample data with correlations
    np.random.seed(42)
    n_samples = 1000
    
    # Create correlated features
    x1 = np.random.normal(0, 1, n_samples)
    x2 = x1 + np.random.normal(0, 0.1, n_samples)  # Highly correlated with x1
    x3 = np.random.normal(0, 1, n_samples)  # Independent
    x4 = x1 * 0.8 + np.random.normal(0, 0.2, n_samples)  # Moderately correlated with x1
    target = x1 + x3 + np.random.normal(0, 0.1, n_samples)
    
    data = pd.DataFrame({
        'feature_1': x1,
        'feature_2': x2,  # Redundant with feature_1
        'feature_3': x3,
        'feature_4': x4,  # Correlated with feature_1
        'target': target
    })
    
    # Perform correlation analysis
    analysis = await analyzer.analyze_correlations(
        data,
        target_column='target',
        creator_type='musician',
        methods=[CorrelationMethod.PEARSON, CorrelationMethod.SPEARMAN]
    )
    
    print(f"Analysis ID: {analysis.analysis_id}")
    print(f"Features analyzed: {analysis.dataset_info['num_features']}")
    print(f"Redundancy groups found: {len(analysis.redundancy_groups)}")
    print(f"High correlation pairs: {len([p for p in analysis.correlation_pairs if abs(p.correlation_value) > 0.8])}")
    
    # Print redundancy groups
    for group in analysis.redundancy_groups:
        print(f"\nRedundancy Group: {group.group_id}")
        print(f"  Features: {group.features}")
        print(f"  Level: {group.redundancy_level.value}")
        print(f"  Representative: {group.representative_feature}")
    
    # Print recommendations
    print("\nRecommendations:")
    for rec in analysis.recommendations:
        print(f"  - {rec}")
    
    # Test feature elimination
    reduced_data, eliminated = await analyzer.eliminate_redundant_features(
        data, analysis, strategy="keep_most_important"
    )
    print(f"\nEliminated features: {eliminated}")
    print(f"Original shape: {data.shape}, Reduced shape: {reduced_data.shape}")
    
    # Get metrics
    metrics = await analyzer.get_metrics()
    print(f"\nMetrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(main())