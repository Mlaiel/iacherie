"""
Vector Quality Assessment Engine

This module provides comprehensive quality assessment for vector embeddings,
including dimensionality analysis, clustering validation, and embedding quality metrics.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

WARNING: This code is proprietary to Fahed Mlaiel. Any unauthorized copying, modification, 
or distribution without explicit written permission is strictly prohibited and will result 
in legal action under German and international copyright law.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.decomposition import PCA, TruncatedSVD, FastICA
from sklearn.manifold import TSNE, UMAP
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.neighbors import NearestNeighbors
from scipy import stats
from scipy.spatial.distance import pdist, squareform
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from backend.core.config import get_settings
from backend.core.database import get_db_session
from backend.models.content_fingerprints import ContentFingerprint
from backend.utils.exceptions import QualityAssessmentError, VectorStoreError
from backend.utils.performance import measure_execution_time
from backend.utils.monitoring import MetricsCollector
from backend.utils.visualization import VectorVisualizer

logger = logging.getLogger(__name__)
settings = get_settings()


class QualityMetric(Enum):
    """Vector quality assessment metrics"""
    INTRINSIC_DIMENSIONALITY = "intrinsic_dimensionality"
    CLUSTERING_QUALITY = "clustering_quality"
    SEPARABILITY = "separability"
    UNIFORMITY = "uniformity"
    STABILITY = "stability"
    SEMANTIC_COHERENCE = "semantic_coherence"
    OUTLIER_DETECTION = "outlier_detection"
    REDUNDANCY_ANALYSIS = "redundancy_analysis"


class DimensionalityMethod(Enum):
    """Dimensionality reduction methods"""
    PCA = "pca"
    TSNE = "tsne"
    UMAP = "umap"
    ICA = "ica"
    SVD = "svd"


@dataclass
class QualityAssessmentConfig:
    """Configuration for quality assessment"""
    metrics_to_compute: List[QualityMetric]
    sample_size: int = 10000
    clustering_algorithms: List[str] = field(default_factory=lambda: ["kmeans", "dbscan"])
    dimensionality_methods: List[DimensionalityMethod] = field(default_factory=lambda: [DimensionalityMethod.PCA, DimensionalityMethod.UMAP])
    n_clusters_range: Tuple[int, int] = (2, 20)
    outlier_threshold: float = 0.05
    similarity_threshold: float = 0.95
    enable_visualization: bool = True
    output_dir: str = "quality_reports"


@dataclass
class DimensionalityAnalysis:
    """Results of dimensionality analysis"""
    original_dimension: int
    intrinsic_dimension: int
    explained_variance_ratio: List[float]
    cumulative_variance: List[float]
    elbow_point: int
    reduction_methods: Dict[str, Dict[str, Any]]
    optimal_dimensions: Dict[str, int]


@dataclass
class ClusteringAnalysis:
    """Results of clustering analysis"""
    algorithm: str
    n_clusters: int
    silhouette_score: float
    calinski_harabasz_score: float
    davies_bouldin_score: float
    cluster_labels: np.ndarray
    cluster_centers: Optional[np.ndarray]
    cluster_sizes: List[int]
    inertia: Optional[float]


@dataclass
class SeparabilityAnalysis:
    """Results of separability analysis"""
    inter_cluster_distance: float
    intra_cluster_distance: float
    separability_index: float
    nearest_neighbor_distances: np.ndarray
    density_distribution: Dict[str, float]
    overlap_coefficient: float


@dataclass
class OutlierAnalysis:
    """Results of outlier analysis"""
    outlier_indices: List[int]
    outlier_scores: np.ndarray
    isolation_scores: np.ndarray
    local_outlier_factors: np.ndarray
    threshold_used: float
    outlier_percentage: float


@dataclass
class QualityReport:
    """Comprehensive quality assessment report"""
    content_type: str
    total_vectors: int
    assessment_timestamp: datetime
    
    # Core analyses
    dimensionality_analysis: DimensionalityAnalysis
    clustering_analyses: List[ClusteringAnalysis]
    separability_analysis: SeparabilityAnalysis
    outlier_analysis: OutlierAnalysis
    
    # Quality metrics
    overall_quality_score: float
    quality_breakdown: Dict[str, float]
    recommendations: List[str]
    
    # Visualizations
    visualization_paths: Dict[str, str]


class VectorQualityAssessment:
    """
    Comprehensive vector quality assessment engine.
    
    Features:
    - Intrinsic dimensionality analysis
    - Clustering quality evaluation
    - Vector space separability analysis
    - Outlier and anomaly detection
    - Embedding stability assessment
    - Semantic coherence validation
    - Quality scoring and recommendations
    - Interactive visualizations
    """
    
    def __init__(self):
        """Initialize quality assessment engine"""
        self.metrics_collector = MetricsCollector()
        self.visualizer = VectorVisualizer()
        
        # Analysis cache
        self.analysis_cache: Dict[str, QualityReport] = {}
        self.vector_cache: Dict[str, np.ndarray] = {}
        
        # Quality thresholds
        self.quality_thresholds = {
            "excellent": 0.9,
            "good": 0.7,
            "fair": 0.5,
            "poor": 0.3
        }
        
        logger.info("Initialized VectorQualityAssessment engine")
    
    async def initialize(self) -> None:
        """Initialize quality assessment system"""



        try:
            await self.visualizer.initialize()
            logger.info("Vector quality assessment system initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize quality assessment: {str(e)}")
            raise QualityAssessmentError(f"Initialization failed: {str(e)}")
    
    @measure_execution_time
    async def assess_vector_quality(
        self,
        content_type: str,
        config: QualityAssessmentConfig,
        vectors: Optional[np.ndarray] = None
    ) -> QualityReport:
        """
        Perform comprehensive quality assessment
        
        Args:
            content_type: Content type to assess
            config: Assessment configuration
            vectors: Optional vectors array (if not provided, loads from DB)
            
        Returns:
            Comprehensive quality report
        """



        try:
            logger.info(f"Starting quality assessment for {content_type}")
            
            # Load vectors if not provided
            if vectors is None:
                vectors = await self._load_vectors(content_type, config.sample_size)
            
            if len(vectors) == 0:
                raise QualityAssessmentError(f"No vectors found for {content_type}")
            
            # Prepare output directory
            output_dir = os.path.join(config.output_dir, content_type, datetime.now().strftime("%Y%m%d_%H%M%S"))
            os.makedirs(output_dir, exist_ok=True)
            
            # Perform analyses
            analyses = {}
            visualization_paths = {}
            
            # Dimensionality analysis
            if QualityMetric.INTRINSIC_DIMENSIONALITY in config.metrics_to_compute:
                analyses["dimensionality"] = await self._analyze_dimensionality(
                    vectors, config, output_dir
                )
                if config.enable_visualization:
                    viz_path = await self._visualize_dimensionality(vectors, output_dir)
                    visualization_paths["dimensionality"] = viz_path
            
            # Clustering analysis
            if QualityMetric.CLUSTERING_QUALITY in config.metrics_to_compute:
                analyses["clustering"] = await self._analyze_clustering(
                    vectors, config, output_dir
                )
                if config.enable_visualization:
                    viz_path = await self._visualize_clustering(vectors, analyses["clustering"], output_dir)
                    visualization_paths["clustering"] = viz_path
            
            # Separability analysis
            if QualityMetric.SEPARABILITY in config.metrics_to_compute:
                analyses["separability"] = await self._analyze_separability(
                    vectors, config, output_dir
                )
                if config.enable_visualization:
                    viz_path = await self._visualize_separability(vectors, analyses["separability"], output_dir)
                    visualization_paths["separability"] = viz_path
            
            # Outlier analysis
            if QualityMetric.OUTLIER_DETECTION in config.metrics_to_compute:
                analyses["outliers"] = await self._analyze_outliers(
                    vectors, config, output_dir
                )
                if config.enable_visualization:
                    viz_path = await self._visualize_outliers(vectors, analyses["outliers"], output_dir)
                    visualization_paths["outliers"] = viz_path
            
            # Calculate overall quality score
            quality_breakdown = self._calculate_quality_metrics(analyses)
            overall_score = self._calculate_overall_quality(quality_breakdown)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(analyses, quality_breakdown)
            
            # Create comprehensive report
            report = QualityReport(
                content_type=content_type,
                total_vectors=len(vectors),
                assessment_timestamp=datetime.now(timezone.utc),
                dimensionality_analysis=analyses.get("dimensionality"),
                clustering_analyses=analyses.get("clustering", []),
                separability_analysis=analyses.get("separability"),
                outlier_analysis=analyses.get("outliers"),
                overall_quality_score=overall_score,
                quality_breakdown=quality_breakdown,
                recommendations=recommendations,
                visualization_paths=visualization_paths
            )
            
            # Cache the report
            self.analysis_cache[content_type] = report
            
            # Save report to file
            await self._save_report(report, output_dir)
            
            logger.info(f"Quality assessment completed for {content_type}. Overall score: {overall_score:.3f}")
            
            return report
            
        except Exception as e:
            logger.error(f"Quality assessment failed for {content_type}: {str(e)}")
            raise QualityAssessmentError(f"Assessment failed: {str(e)}")
    
    async def _analyze_dimensionality(
        self,
        vectors: np.ndarray,
        config: QualityAssessmentConfig,
        output_dir: str
    ) -> DimensionalityAnalysis:
        """Analyze vector dimensionality and intrinsic dimensions"""



        try:
            original_dim = vectors.shape[1]
            
            # PCA analysis for explained variance
            pca = PCA()
            pca.fit(vectors)
            
            explained_variance = pca.explained_variance_ratio_
            cumulative_variance = np.cumsum(explained_variance)
            
            # Find elbow point (95% variance)
            elbow_point = np.argmax(cumulative_variance >= 0.95) + 1
            
            # Intrinsic dimensionality estimation using PCA
            intrinsic_dim = np.sum(explained_variance > explained_variance.mean())
            
            # Test different dimensionality reduction methods
            reduction_methods = {}
            optimal_dimensions = {}
            
            for method in config.dimensionality_methods:
                try:
                    if method == DimensionalityMethod.PCA:
                        reducer = PCA(n_components=min(50, original_dim))
                        reduced_vectors = reducer.fit_transform(vectors)
                        
                        reduction_methods["pca"] = {
                            "explained_variance_ratio": reducer.explained_variance_ratio_.tolist(),
                            "components": reducer.components_.shape,
                            "reconstruction_error": self._calculate_reconstruction_error(vectors, reducer)
                        }
                        optimal_dimensions["pca"] = elbow_point
                    
                    elif method == DimensionalityMethod.UMAP:
                        import umap
                        reducer = umap.UMAP(n_components=min(50, original_dim), random_state=42)
                        reduced_vectors = reducer.fit_transform(vectors)
                        
                        reduction_methods["umap"] = {
                            "n_components": reducer.n_components,
                            "embedding_shape": reduced_vectors.shape,
                            "trustworthiness": self._calculate_trustworthiness(vectors, reduced_vectors)
                        }
                        optimal_dimensions["umap"] = reducer.n_components
                    
                    elif method == DimensionalityMethod.TSNE:
                        from sklearn.manifold import TSNE
                        reducer = TSNE(n_components=min(3, original_dim), random_state=42)
                        reduced_vectors = reducer.fit_transform(vectors[:5000])  # TSNE is expensive
                        
                        reduction_methods["tsne"] = {
                            "n_components": reducer.n_components,
                            "embedding_shape": reduced_vectors.shape,
                            "kl_divergence": reducer.kl_divergence_
                        }
                        optimal_dimensions["tsne"] = reducer.n_components
                    
                    elif method == DimensionalityMethod.ICA:
                        from sklearn.decomposition import FastICA
                        reducer = FastICA(n_components=min(50, original_dim), random_state=42)
                        reduced_vectors = reducer.fit_transform(vectors)
                        
                        reduction_methods["ica"] = {
                            "n_components": reducer.n_components,
                            "components_shape": reducer.components_.shape,
                            "independence_score": self._calculate_independence_score(reduced_vectors)
                        }
                        optimal_dimensions["ica"] = reducer.n_components
                    
                    elif method == DimensionalityMethod.SVD:
                        reducer = TruncatedSVD(n_components=min(50, original_dim))
                        reduced_vectors = reducer.fit_transform(vectors)
                        
                        reduction_methods["svd"] = {
                            "explained_variance_ratio": reducer.explained_variance_ratio_.tolist(),
                            "components_shape": reducer.components_.shape,
                            "singular_values": reducer.singular_values_.tolist()
                        }
                        optimal_dimensions["svd"] = np.argmax(np.cumsum(reducer.explained_variance_ratio_) >= 0.95) + 1
                
                except Exception as e:
                    logger.warning(f"Failed to apply {method.value}: {str(e)}")
                    continue
            
            return DimensionalityAnalysis(
                original_dimension=original_dim,
                intrinsic_dimension=intrinsic_dim,
                explained_variance_ratio=explained_variance.tolist(),
                cumulative_variance=cumulative_variance.tolist(),
                elbow_point=elbow_point,
                reduction_methods=reduction_methods,
                optimal_dimensions=optimal_dimensions
            )
            
        except Exception as e:
            logger.error(f"Dimensionality analysis failed: {str(e)}")
            raise QualityAssessmentError(f"Dimensionality analysis failed: {str(e)}")
    
    async def _analyze_clustering(
        self,
        vectors: np.ndarray,
        config: QualityAssessmentConfig,
        output_dir: str
    ) -> List[ClusteringAnalysis]:
        """Analyze clustering quality with multiple algorithms"""



        try:
            clustering_results = []
            
            for algorithm in config.clustering_algorithms:
                if algorithm == "kmeans":
                    # Test different numbers of clusters
                    best_kmeans = None
                    best_score = -1
                    
                    for n_clusters in range(config.n_clusters_range[0], config.n_clusters_range[1] + 1):
                        try:
                            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                            labels = kmeans.fit_predict(vectors)
                            
                            if len(set(labels)) > 1:  # Need at least 2 clusters for silhouette
                                silhouette = silhouette_score(vectors, labels)
                                
                                if silhouette > best_score:
                                    best_score = silhouette
                                    best_kmeans = kmeans
                        except:
                            continue
                    
                    if best_kmeans is not None:
                        labels = best_kmeans.labels_
                        cluster_analysis = ClusteringAnalysis(
                            algorithm="kmeans",
                            n_clusters=best_kmeans.n_clusters,
                            silhouette_score=silhouette_score(vectors, labels),
                            calinski_harabasz_score=calinski_harabasz_score(vectors, labels),
                            davies_bouldin_score=davies_bouldin_score(vectors, labels),
                            cluster_labels=labels,
                            cluster_centers=best_kmeans.cluster_centers_,
                            cluster_sizes=[np.sum(labels == i) for i in range(best_kmeans.n_clusters)],
                            inertia=best_kmeans.inertia_
                        )
                        clustering_results.append(cluster_analysis)
                
                elif algorithm == "dbscan":
                    # Test different epsilon values
                    best_dbscan = None
                    best_score = -1
                    
                    # Estimate epsilon using k-distance
                    k_distances = self._calculate_k_distances(vectors, k=4)
                    eps_candidates = np.percentile(k_distances, [25, 50, 75, 90])
                    
                    for eps in eps_candidates:
                        try:
                            dbscan = DBSCAN(eps=eps, min_samples=5)
                            labels = dbscan.fit_predict(vectors)
                            
                            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
                            if n_clusters > 1:
                                silhouette = silhouette_score(vectors, labels)
                                
                                if silhouette > best_score:
                                    best_score = silhouette
                                    best_dbscan = dbscan
                        except:
                            continue
                    
                    if best_dbscan is not None:
                        labels = best_dbscan.labels_
                        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
                        cluster_sizes = [np.sum(labels == i) for i in set(labels) if i != -1]
                        
                        cluster_analysis = ClusteringAnalysis(
                            algorithm="dbscan",
                            n_clusters=n_clusters,
                            silhouette_score=silhouette_score(vectors, labels),
                            calinski_harabasz_score=calinski_harabasz_score(vectors, labels),
                            davies_bouldin_score=davies_bouldin_score(vectors, labels),
                            cluster_labels=labels,
                            cluster_centers=None,
                            cluster_sizes=cluster_sizes,
                            inertia=None
                        )
                        clustering_results.append(cluster_analysis)
            
            return clustering_results
            
        except Exception as e:
            logger.error(f"Clustering analysis failed: {str(e)}")
            raise QualityAssessmentError(f"Clustering analysis failed: {str(e)}")
    
    async def _analyze_separability(
        self,
        vectors: np.ndarray,
        config: QualityAssessmentConfig,
        output_dir: str
    ) -> SeparabilityAnalysis:
        """Analyze vector space separability"""



        try:
            # Calculate pairwise distances
            distances = pdist(vectors, metric='cosine')
            distance_matrix = squareform(distances)
            
            # Nearest neighbor analysis
            nn = NearestNeighbors(n_neighbors=5, metric='cosine')
            nn.fit(vectors)
            nn_distances, nn_indices = nn.kneighbors(vectors)
            
            # Inter vs intra cluster distances (using k-means for reference)
            kmeans = KMeans(n_clusters=min(10, len(vectors) // 100), random_state=42)
            cluster_labels = kmeans.fit_predict(vectors)
            
            inter_distances = []
            intra_distances = []
            
            for i in range(len(vectors)):
                for j in range(i + 1, len(vectors)):
                    dist = distance_matrix[i, j]
                    if cluster_labels[i] == cluster_labels[j]:
                        intra_distances.append(dist)
                    else:
                        inter_distances.append(dist)
            
            inter_cluster_distance = np.mean(inter_distances) if inter_distances else 0
            intra_cluster_distance = np.mean(intra_distances) if intra_distances else 0
            
            # Separability index
            separability_index = inter_cluster_distance / (intra_cluster_distance + 1e-8)
            
            # Density distribution analysis
            density_scores = []
            for i in range(len(vectors)):
                # Local density based on k-nearest neighbors
                local_density = 1.0 / (np.mean(nn_distances[i][1:]) + 1e-8)
                density_scores.append(local_density)
            
            density_distribution = {
                "mean": np.mean(density_scores),
                "std": np.std(density_scores),
                "min": np.min(density_scores),
                "max": np.max(density_scores),
                "median": np.median(density_scores)
            }
            
            # Overlap coefficient (simplified)
            overlap_coefficient = self._calculate_overlap_coefficient(vectors, cluster_labels)
            
            return SeparabilityAnalysis(
                inter_cluster_distance=inter_cluster_distance,
                intra_cluster_distance=intra_cluster_distance,
                separability_index=separability_index,
                nearest_neighbor_distances=nn_distances[:, 1],  # Distance to nearest neighbor
                density_distribution=density_distribution,
                overlap_coefficient=overlap_coefficient
            )
            
        except Exception as e:
            logger.error(f"Separability analysis failed: {str(e)}")
            raise QualityAssessmentError(f"Separability analysis failed: {str(e)}")
    
    async def _analyze_outliers(
        self,
        vectors: np.ndarray,
        config: QualityAssessmentConfig,
        output_dir: str
    ) -> OutlierAnalysis:
        """Analyze outliers and anomalies in vector space"""



        try:
            from sklearn.ensemble import IsolationForest
            from sklearn.neighbors import LocalOutlierFactor
            
            # Isolation Forest
            iso_forest = IsolationForest(contamination=config.outlier_threshold, random_state=42)
            isolation_scores = iso_forest.fit_predict(vectors)
            
            # Local Outlier Factor
            lof = LocalOutlierFactor(n_neighbors=20, contamination=config.outlier_threshold)
            lof_scores = lof.fit_predict(vectors)
            
            # Statistical outliers (using Mahalanobis distance)
            mean_vector = np.mean(vectors, axis=0)
            cov_matrix = np.cov(vectors.T)
            
            try:
                inv_cov = np.linalg.pinv(cov_matrix)
                mahalanobis_distances = []
                for vector in vectors:
                    diff = vector - mean_vector
                    m_dist = np.sqrt(diff.T @ inv_cov @ diff)
                    mahalanobis_distances.append(m_dist)
                
                mahalanobis_distances = np.array(mahalanobis_distances)
                threshold = np.percentile(mahalanobis_distances, (1 - config.outlier_threshold) * 100)
                statistical_outliers = mahalanobis_distances > threshold
            except:
                # Fallback to z-score if covariance matrix is singular
                z_scores = np.abs(stats.zscore(vectors, axis=0))
                statistical_outliers = np.any(z_scores > 3, axis=1)
                mahalanobis_distances = np.max(z_scores, axis=1)
                threshold = 3.0
            
            # Combine outlier detection methods
            outlier_votes = (isolation_scores == -1).astype(int) + \
                           (lof_scores == -1).astype(int) + \
                           statistical_outliers.astype(int)
            
            # Consensus outliers (detected by at least 2 methods)
            consensus_outliers = outlier_votes >= 2
            outlier_indices = np.where(consensus_outliers)[0].tolist()
            
            outlier_percentage = len(outlier_indices) / len(vectors) * 100
            
            return OutlierAnalysis(
                outlier_indices=outlier_indices,
                outlier_scores=outlier_votes,
                isolation_scores=isolation_scores,
                local_outlier_factors=lof_scores,
                threshold_used=threshold,
                outlier_percentage=outlier_percentage
            )
            
        except Exception as e:
            logger.error(f"Outlier analysis failed: {str(e)}")
            raise QualityAssessmentError(f"Outlier analysis failed: {str(e)}")
    
    def _calculate_quality_metrics(self, analyses: Dict[str, Any]) -> Dict[str, float]:
        """Calculate quality metrics from analyses"""
        quality_breakdown = {}
        
        try:
            # Dimensionality quality
            if "dimensionality" in analyses:
                dim_analysis = analyses["dimensionality"]
                
                # Quality based on explained variance and intrinsic dimensionality
                variance_ratio = dim_analysis.cumulative_variance[dim_analysis.elbow_point - 1] if dim_analysis.elbow_point > 0 else 0
                dimension_efficiency = dim_analysis.intrinsic_dimension / dim_analysis.original_dimension
                
                quality_breakdown["dimensionality"] = (variance_ratio + dimension_efficiency) / 2
            
            # Clustering quality
            if "clustering" in analyses:
                clustering_analyses = analyses["clustering"]
                if clustering_analyses:
                    # Take best silhouette score
                    best_silhouette = max(analysis.silhouette_score for analysis in clustering_analyses)
                    quality_breakdown["clustering"] = (best_silhouette + 1) / 2  # Normalize to [0, 1]
            
            # Separability quality
            if "separability" in analyses:
                sep_analysis = analyses["separability"]
                
                # Quality based on separability index and density uniformity
                separability_score = min(sep_analysis.separability_index / 2.0, 1.0)  # Cap at 1.0
                density_uniformity = 1.0 / (1.0 + sep_analysis.density_distribution["std"])
                overlap_score = 1.0 - sep_analysis.overlap_coefficient
                
                quality_breakdown["separability"] = (separability_score + density_uniformity + overlap_score) / 3
            
            # Outlier quality (fewer outliers = better quality)
            if "outliers" in analyses:
                outlier_analysis = analyses["outliers"]
                outlier_score = 1.0 - (outlier_analysis.outlier_percentage / 100.0)
                quality_breakdown["outliers"] = max(outlier_score, 0.0)
            
            return quality_breakdown
            
        except Exception as e:
            logger.error(f"Failed to calculate quality metrics: {str(e)}")
            return {}
    
    def _calculate_overall_quality(self, quality_breakdown: Dict[str, float]) -> float:
        """Calculate overall quality score"""
        if not quality_breakdown:
            return 0.0
        
        # Weighted average of quality metrics
        weights = {
            "dimensionality": 0.25,
            "clustering": 0.30,
            "separability": 0.30,
            "outliers": 0.15
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for metric, score in quality_breakdown.items():
            weight = weights.get(metric, 0.25)
            weighted_score += score * weight
            total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _generate_recommendations(
        self,
        analyses: Dict[str, Any],
        quality_breakdown: Dict[str, float]
    ) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        try:
            # Dimensionality recommendations
            if "dimensionality" in analyses:
                dim_analysis = analyses["dimensionality"]
                
                if dim_analysis.intrinsic_dimension < dim_analysis.original_dimension * 0.5:
                    recommendations.append(
                        f"Consider dimensionality reduction: intrinsic dimension ({dim_analysis.intrinsic_dimension}) "
                        f"is much lower than original ({dim_analysis.original_dimension})"
                    )
                
                if dim_analysis.elbow_point < 10:
                    recommendations.append(
                        "Low effective dimensionality detected. Consider using higher-capacity models."
                    )
            
            # Clustering recommendations
            if "clustering" in analyses:
                clustering_analyses = analyses["clustering"]
                if clustering_analyses:
                    best_analysis = max(clustering_analyses, key=lambda x: x.silhouette_score)
                    
                    if best_analysis.silhouette_score < 0.3:
                        recommendations.append(
                            "Poor clustering structure detected. Consider improving embedding model or data quality."
                        )
                    
                    if best_analysis.n_clusters > 20:
                        recommendations.append(
                            "High number of clusters detected. Data might be too fragmented."
                        )
            
            # Separability recommendations
            if "separability" in analyses:
                sep_analysis = analyses["separability"]
                
                if sep_analysis.separability_index < 1.0:
                    recommendations.append(
                        "Low separability between clusters. Consider contrastive learning or margin-based losses."
                    )
                
                if sep_analysis.overlap_coefficient > 0.5:
                    recommendations.append(
                        "High overlap between clusters detected. Improve model discriminative power."
                    )
            
            # Outlier recommendations
            if "outliers" in analyses:
                outlier_analysis = analyses["outliers"]
                
                if outlier_analysis.outlier_percentage > 10:
                    recommendations.append(
                        f"High outlier percentage ({outlier_analysis.outlier_percentage:.1f}%). "
                        "Consider data cleaning or robustness improvements."
                    )
            
            # Overall quality recommendations
            overall_score = self._calculate_overall_quality(quality_breakdown)
            
            if overall_score < self.quality_thresholds["poor"]:
                recommendations.append(
                    "Overall vector quality is poor. Consider retraining embedding models with better data."
                )
            elif overall_score < self.quality_thresholds["fair"]:
                recommendations.append(
                    "Vector quality needs improvement. Focus on data quality and model architecture."
                )
            elif overall_score < self.quality_thresholds["good"]:
                recommendations.append(
                    "Vector quality is fair. Fine-tuning and optimization can provide improvements."
                )
            
            if not recommendations:
                recommendations.append("Vector quality is excellent. No immediate improvements needed.")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {str(e)}")
            return ["Error generating recommendations"]
    
    async def _load_vectors(self, content_type: str, sample_size: int) -> np.ndarray:
        """Load vectors from database"""



        try:
            async with get_db_session() as session:
                stmt = select(ContentFingerprint.vector_embedding).where(
                    and_(
                        ContentFingerprint.content_type == content_type,
                        ContentFingerprint.vector_embedding.isnot(None)
                    )
                ).limit(sample_size)
                
                result = await session.execute(stmt)
                embeddings = result.scalars().all()
                
                if not embeddings:
                    return np.array([])
                
                # Convert binary embeddings to numpy arrays
                vectors = []
                for embedding in embeddings:
                    vector = np.frombuffer(embedding, dtype=np.float32)
                    vectors.append(vector)
                
                return np.array(vectors)
                
        except Exception as e:
            logger.error(f"Failed to load vectors for {content_type}: {str(e)}")
            return np.array([])
    
    async def _visualize_dimensionality(self, vectors: np.ndarray, output_dir: str) -> str:
        """Create dimensionality visualization"""



        try:
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            
            # PCA explained variance
            pca = PCA()
            pca.fit(vectors)
            
            axes[0, 0].plot(range(1, min(51, len(pca.explained_variance_ratio_) + 1)), 
                           pca.explained_variance_ratio_[:50])
            axes[0, 0].set_title('PCA Explained Variance Ratio')
            axes[0, 0].set_xlabel('Component')
            axes[0, 0].set_ylabel('Explained Variance Ratio')
            
            # Cumulative variance
            cumsum = np.cumsum(pca.explained_variance_ratio_)
            axes[0, 1].plot(range(1, min(51, len(cumsum) + 1)), cumsum[:50])
            axes[0, 1].axhline(y=0.95, color='r', linestyle='--', label='95% variance')
            axes[0, 1].set_title('Cumulative Explained Variance')
            axes[0, 1].set_xlabel('Component')
            axes[0, 1].set_ylabel('Cumulative Variance')
            axes[0, 1].legend()
            
            # 2D PCA projection
            pca_2d = PCA(n_components=2)
            vectors_2d = pca_2d.fit_transform(vectors)
            axes[1, 0].scatter(vectors_2d[:, 0], vectors_2d[:, 1], alpha=0.6)
            axes[1, 0].set_title('2D PCA Projection')
            axes[1, 0].set_xlabel('PC1')
            axes[1, 0].set_ylabel('PC2')
            
            # Distribution of first principal component
            axes[1, 1].hist(vectors_2d[:, 0], bins=50, alpha=0.7)
            axes[1, 1].set_title('Distribution of First Principal Component')
            axes[1, 1].set_xlabel('PC1 Value')
            axes[1, 1].set_ylabel('Frequency')
            
            plt.tight_layout()
            viz_path = os.path.join(output_dir, 'dimensionality_analysis.png')
            plt.savefig(viz_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return viz_path
            
        except Exception as e:
            logger.error(f"Failed to create dimensionality visualization: {str(e)}")
            return ""
    
    async def _visualize_clustering(
        self, 
        vectors: np.ndarray, 
        clustering_analyses: List[ClusteringAnalysis], 
        output_dir: str
    ) -> str:
        """Create clustering visualization"""



        try:
            if not clustering_analyses:
                return ""
            
            best_analysis = max(clustering_analyses, key=lambda x: x.silhouette_score)
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            
            # 2D visualization of clusters
            pca_2d = PCA(n_components=2)
            vectors_2d = pca_2d.fit_transform(vectors)
            
            scatter = axes[0, 0].scatter(vectors_2d[:, 0], vectors_2d[:, 1], 
                                       c=best_analysis.cluster_labels, 
                                       cmap='tab10', alpha=0.6)
            axes[0, 0].set_title(f'Clusters ({best_analysis.algorithm.upper()})')
            axes[0, 0].set_xlabel('PC1')
            axes[0, 0].set_ylabel('PC2')
            plt.colorbar(scatter, ax=axes[0, 0])
            
            # Cluster sizes
            cluster_sizes = best_analysis.cluster_sizes
            axes[0, 1].bar(range(len(cluster_sizes)), cluster_sizes)
            axes[0, 1].set_title('Cluster Sizes')
            axes[0, 1].set_xlabel('Cluster ID')
            axes[0, 1].set_ylabel('Number of Points')
            
            # Silhouette scores comparison
            algorithms = [analysis.algorithm for analysis in clustering_analyses]
            silhouette_scores = [analysis.silhouette_score for analysis in clustering_analyses]
            
            axes[1, 0].bar(algorithms, silhouette_scores)
            axes[1, 0].set_title('Silhouette Scores by Algorithm')
            axes[1, 0].set_xlabel('Algorithm')
            axes[1, 0].set_ylabel('Silhouette Score')
            axes[1, 0].tick_params(axis='x', rotation=45)
            
            # Quality metrics comparison
            metrics_names = ['Silhouette', 'Calinski-Harabasz', 'Davies-Bouldin']
            best_metrics = [
                best_analysis.silhouette_score,
                best_analysis.calinski_harabasz_score / 1000,  # Scale down
                1.0 / best_analysis.davies_bouldin_score  # Invert (lower is better)
            ]
            
            axes[1, 1].bar(metrics_names, best_metrics)
            axes[1, 1].set_title('Clustering Quality Metrics')
            axes[1, 1].set_xlabel('Metric')
            axes[1, 1].set_ylabel('Score')
            axes[1, 1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            viz_path = os.path.join(output_dir, 'clustering_analysis.png')
            plt.savefig(viz_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return viz_path
            
        except Exception as e:
            logger.error(f"Failed to create clustering visualization: {str(e)}")
            return ""
    
    async def _visualize_separability(
        self, 
        vectors: np.ndarray, 
        separability_analysis: SeparabilityAnalysis, 
        output_dir: str
    ) -> str:
        """Create separability visualization"""



        try:
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            
            # Nearest neighbor distances distribution
            nn_distances = separability_analysis.nearest_neighbor_distances
            axes[0, 0].hist(nn_distances, bins=50, alpha=0.7)
            axes[0, 0].set_title('Nearest Neighbor Distances')
            axes[0, 0].set_xlabel('Distance')
            axes[0, 0].set_ylabel('Frequency')
            
            # Density distribution
            density_dist = separability_analysis.density_distribution
            density_stats = [density_dist['min'], density_dist['median'], density_dist['max']]
            density_labels = ['Min', 'Median', 'Max']
            
            axes[0, 1].bar(density_labels, density_stats)
            axes[0, 1].set_title('Density Distribution Statistics')
            axes[0, 1].set_ylabel('Density Score')
            
            # Separability metrics
            metrics = [
                'Inter-cluster Distance',
                'Intra-cluster Distance',
                'Separability Index',
                'Overlap Coefficient'
            ]
            values = [
                separability_analysis.inter_cluster_distance,
                separability_analysis.intra_cluster_distance,
                separability_analysis.separability_index,
                separability_analysis.overlap_coefficient
            ]
            
            axes[1, 0].bar(metrics, values)
            axes[1, 0].set_title('Separability Metrics')
            axes[1, 0].tick_params(axis='x', rotation=45)
            axes[1, 0].set_ylabel('Value')
            
            # 2D projection with density coloring
            pca_2d = PCA(n_components=2)
            vectors_2d = pca_2d.fit_transform(vectors)
            
            # Calculate local density for coloring
            nn = NearestNeighbors(n_neighbors=10)
            nn.fit(vectors_2d)
            distances, _ = nn.kneighbors(vectors_2d)
            local_density = 1.0 / (np.mean(distances[:, 1:], axis=1) + 1e-8)
            
            scatter = axes[1, 1].scatter(vectors_2d[:, 0], vectors_2d[:, 1], 
                                       c=local_density, cmap='viridis', alpha=0.6)
            axes[1, 1].set_title('Vector Space Density')
            axes[1, 1].set_xlabel('PC1')
            axes[1, 1].set_ylabel('PC2')
            plt.colorbar(scatter, ax=axes[1, 1])
            
            plt.tight_layout()
            viz_path = os.path.join(output_dir, 'separability_analysis.png')
            plt.savefig(viz_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return viz_path
            
        except Exception as e:
            logger.error(f"Failed to create separability visualization: {str(e)}")
            return ""
    
    async def _visualize_outliers(
        self, 
        vectors: np.ndarray, 
        outlier_analysis: OutlierAnalysis, 
        output_dir: str
    ) -> str:
        """Create outlier visualization"""



        try:
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            
            # 2D visualization of outliers
            pca_2d = PCA(n_components=2)
            vectors_2d = pca_2d.fit_transform(vectors)
            
            outlier_mask = np.zeros(len(vectors), dtype=bool)
            outlier_mask[outlier_analysis.outlier_indices] = True
            
            # Plot normal points
            normal_points = vectors_2d[~outlier_mask]
            outlier_points = vectors_2d[outlier_mask]
            
            axes[0, 0].scatter(normal_points[:, 0], normal_points[:, 1], 
                             alpha=0.6, label='Normal', color='blue')
            axes[0, 0].scatter(outlier_points[:, 0], outlier_points[:, 1], 
                             alpha=0.8, label='Outliers', color='red', s=100)
            axes[0, 0].set_title('Outlier Detection')
            axes[0, 0].set_xlabel('PC1')
            axes[0, 0].set_ylabel('PC2')
            axes[0, 0].legend()
            
            # Outlier scores distribution
            axes[0, 1].hist(outlier_analysis.outlier_scores, bins=20, alpha=0.7)
            axes[0, 1].set_title('Outlier Scores Distribution')
            axes[0, 1].set_xlabel('Outlier Score (Consensus Votes)')
            axes[0, 1].set_ylabel('Frequency')
            
            # Outlier percentage by method
            isolation_outliers = np.sum(outlier_analysis.isolation_scores == -1) / len(vectors) * 100
            lof_outliers = np.sum(outlier_analysis.local_outlier_factors == -1) / len(vectors) * 100
            
            methods = ['Isolation Forest', 'Local Outlier Factor', 'Consensus']
            percentages = [isolation_outliers, lof_outliers, outlier_analysis.outlier_percentage]
            
            axes[1, 0].bar(methods, percentages)
            axes[1, 0].set_title('Outlier Percentage by Method')
            axes[1, 0].set_ylabel('Percentage (%)')
            axes[1, 0].tick_params(axis='x', rotation=45)
            
            # Outlier score vs distance from center
            center = np.mean(vectors, axis=0)
            distances_from_center = np.linalg.norm(vectors - center, axis=1)
            
            axes[1, 1].scatter(distances_from_center, outlier_analysis.outlier_scores, alpha=0.6)
            axes[1, 1].set_title('Outlier Score vs Distance from Center')
            axes[1, 1].set_xlabel('Distance from Center')
            axes[1, 1].set_ylabel('Outlier Score')
            
            plt.tight_layout()
            viz_path = os.path.join(output_dir, 'outlier_analysis.png')
            plt.savefig(viz_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return viz_path
            
        except Exception as e:
            logger.error(f"Failed to create outlier visualization: {str(e)}")
            return ""
    
    async def _save_report(self, report: QualityReport, output_dir: str) -> None:
        """Save quality assessment report"""



        try:
            report_path = os.path.join(output_dir, 'quality_report.json')
            
            # Convert report to JSON-serializable format
            report_dict = asdict(report)
            
            # Handle numpy arrays
            def convert_numpy(obj):
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                return obj
            
            # Recursively convert numpy arrays
            def recursive_convert(data):
                if isinstance(data, dict):
                    return {k: recursive_convert(v) for k, v in data.items()}
                elif isinstance(data, list):
                    return [recursive_convert(item) for item in data]
                else:
                    return convert_numpy(data)
            
            report_dict = recursive_convert(report_dict)
            
            with open(report_path, 'w') as f:
                json.dump(report_dict, f, indent=2, default=str)
            
            logger.info(f"Quality report saved to {report_path}")
            
        except Exception as e:
            logger.error(f"Failed to save quality report: {str(e)}")
    
    # Helper methods
    def _calculate_reconstruction_error(self, original: np.ndarray, reducer) -> float:
        """Calculate reconstruction error for dimensionality reduction"""



        try:
            reduced = reducer.transform(original)
            reconstructed = reducer.inverse_transform(reduced)
            error = np.mean(np.square(original - reconstructed))
            return float(error)
        except:
            return 0.0
    
    def _calculate_trustworthiness(self, original: np.ndarray, reduced: np.ndarray) -> float:
        """Calculate trustworthiness of dimensionality reduction"""



        try:
            from sklearn.manifold import trustworthiness
            return trustworthiness(original, reduced)
        except:
            return 0.0
    
    def _calculate_independence_score(self, components: np.ndarray) -> float:
        """Calculate independence score for ICA components"""



        try:
            # Measure statistical independence using mutual information
            correlations = np.corrcoef(components.T)
            off_diagonal = correlations[np.triu_indices_from(correlations, k=1)]
            independence = 1.0 - np.mean(np.abs(off_diagonal))
            return float(independence)
        except:
            return 0.0
    
    def _calculate_k_distances(self, vectors: np.ndarray, k: int = 4) -> np.ndarray:
        """Calculate k-distances for DBSCAN epsilon estimation"""



        try:
            nn = NearestNeighbors(n_neighbors=k + 1)
            nn.fit(vectors)
            distances, _ = nn.kneighbors(vectors)
            return distances[:, -1]  # k-th nearest neighbor distance
        except:
            return np.array([])
    
    def _calculate_overlap_coefficient(self, vectors: np.ndarray, labels: np.ndarray) -> float:
        """Calculate overlap coefficient between clusters"""



        try:
            unique_labels = np.unique(labels)
            if len(unique_labels) < 2:
                return 0.0
            
            total_overlap = 0.0
            comparisons = 0
            
            for i in range(len(unique_labels)):
                for j in range(i + 1, len(unique_labels)):
                    cluster_i = vectors[labels == unique_labels[i]]
                    cluster_j = vectors[labels == unique_labels[j]]
                    
                    if len(cluster_i) > 0 and len(cluster_j) > 0:
                        # Calculate overlap using convex hull or distance-based metric
                        min_distance = np.min(euclidean_distances(cluster_i, cluster_j))
                        max_intra_distance = max(
                            np.max(pdist(cluster_i)) if len(cluster_i) > 1 else 0,
                            np.max(pdist(cluster_j)) if len(cluster_j) > 1 else 0
                        )
                        
                        overlap = max(0, 1 - min_distance / (max_intra_distance + 1e-8))
                        total_overlap += overlap
                        comparisons += 1
            
            return total_overlap / comparisons if comparisons > 0 else 0.0
        except:
            return 0.0
    
    async def close(self) -> None:
        """Close quality assessment system"""



        try:
            # Clear caches
            self.analysis_cache.clear()
            self.vector_cache.clear()
            
            logger.info("Vector quality assessment system closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing quality assessment system: {str(e)}")
