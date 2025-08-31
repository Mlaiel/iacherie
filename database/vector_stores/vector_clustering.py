"""Vector Clustering Engine

This module provides advanced vector clustering capabilities for content analysis,
similarity grouping, and anomaly detection in fingerprint data.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

WARNING: This code is proprietary to Fahed Mlaiel. Any unauthorized copying, modification, 
or distribution without explicit written permission is strictly prohibited and will result 
in legal action under German and international copyright law.
"""import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.cluster import (
    KMeans, DBSCAN, AgglomerativeClustering, 
    SpectralClustering, OPTICS, MeanShift
)
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA, UMAP
from sklearn.metrics import (
    silhouette_score, calinski_harabasz_score, 
    davies_bouldin_score, adjusted_rand_score
)
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from backend.core.config import get_settings
from backend.core.database import get_db_session
from backend.models.content_fingerprints import ContentFingerprint
from backend.utils.exceptions import ClusteringError, VectorStoreError
from backend.utils.performance import measure_execution_time
from backend.utils.visualization import VisualizationManager
from backend.utils.ml_models import AnomalyDetector

logger = logging.getLogger(__name__)
settings = get_settings()


class ClusteringAlgorithm(Enum):
    """Supported clustering algorithms"""    KMEANS = "kmeans"
    DBSCAN = "dbscan"
    HIERARCHICAL = "hierarchical"
    SPECTRAL = "spectral"
    GAUSSIAN_MIXTURE = "gaussian_mixture"
    OPTICS = "optics"
    MEAN_SHIFT = "mean_shift"
    CUSTOM_ENSEMBLE = "custom_ensemble"


class DimensionalityReduction(Enum):
    """Dimensionality reduction techniques"""    PCA = "pca"
    UMAP = "umap"
    TSNE = "tsne"
    ISOMAP = "isomap"
    NONE = "none"


class ClusteringMode(Enum):
    """Clustering operation modes"""    CONTENT_ANALYSIS = "content_analysis"
    DUPLICATE_DETECTION = "duplicate_detection"
    ANOMALY_DETECTION = "anomaly_detection"
    SIMILARITY_GROUPING = "similarity_grouping"
    QUALITY_ASSESSMENT = "quality_assessment"


@dataclass
class ClusteringConfig:
    """Clustering configuration parameters"""    algorithm: ClusteringAlgorithm
    n_clusters: Optional[int] = None
    eps: float = 0.5
    min_samples: int = 5
    dimensionality_reduction: DimensionalityReduction = DimensionalityReduction.NONE
    n_components: int = 50
    normalize: bool = True
    random_state: int = 42
    mode: ClusteringMode = ClusteringMode.SIMILARITY_GROUPING
    quality_threshold: float = 0.7
    outlier_threshold: float = 2.0


@dataclass
class ClusterInfo:
    """Information about a single cluster"""    cluster_id: int
    content_type: str
    size: int
    centroid: np.ndarray
    radius: float
    density: float
    quality_score: float
    content_ids: List[str]
    representative_content: str
    metadata: Dict[str, Any]
    created_at: datetime
    silhouette_score: float


@dataclass
class ClusteringResult:
    """Complete clustering analysis result"""    clustering_id: str
    content_type: str
    algorithm_used: str
    total_vectors: int
    n_clusters: int
    clusters: List[ClusterInfo]
    outliers: List[str]
    quality_metrics: Dict[str, float]
    execution_time: float
    config: ClusteringConfig
    visualization_paths: List[str]
    insights: Dict[str, Any]


@dataclass
class AnomalyReport:
    """Anomaly detection report"""    content_id: str
    anomaly_score: float
    anomaly_type: str
    cluster_id: Optional[int]
    distance_to_nearest: float
    explanation: str
    recommendation: str
    confidence: float


class VectorClusteringEngine:
    """    Advanced vector clustering engine for content analysis and pattern discovery.
    
    Features:
    - Multiple clustering algorithms (K-means, DBSCAN, Hierarchical, etc.)
    - Dimensionality reduction for visualization
    - Anomaly and outlier detection
    - Cluster quality assessment and optimization
    - Content similarity grouping
    - Duplicate content identification
    - Interactive visualizations
    - Performance monitoring and caching
    """    
    def __init__(
        self,
        visualization_manager: VisualizationManager = None,
        anomaly_detector: AnomalyDetector = None,
        cache_enabled: bool = True,
        parallel_processing: bool = True
    ):
        """        Initialize vector clustering engine
        
        Args:
            visualization_manager: Visualization utilities
            anomaly_detector: Anomaly detection system
            cache_enabled: Enable result caching
            parallel_processing: Enable parallel processing
        """        self.visualization_manager = visualization_manager or VisualizationManager()
        self.anomaly_detector = anomaly_detector or AnomalyDetector()
        self.cache_enabled = cache_enabled
        self.parallel_processing = parallel_processing
        
        # Clustering results cache
        self.clustering_cache: Dict[str, ClusteringResult] = {}
        
        # Performance tracking
        self.clustering_stats = {
            "total_clusterings": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "avg_execution_time": 0.0,
            "total_vectors_processed": 0,
            "anomalies_detected": 0
        }
        
        # Algorithm configurations
        self.algorithm_configs = self._initialize_algorithm_configs()
        
        # Quality metrics history
        self.quality_history: List[Dict[str, Any]] = []
        
        logger.info(
            f"Initialized VectorClusteringEngine - Cache: {cache_enabled}, "
            f"Parallel: {parallel_processing}"
        )
    
    @measure_execution_time
    async def cluster_vectors(
        self,
        content_type: str,
        config: ClusteringConfig,
        vector_data: Optional[List[Tuple[str, np.ndarray]]] = None,
        clustering_id: str = None
    ) -> ClusteringResult:
        """        Perform vector clustering analysis
        
        Args:
            content_type: Content type to cluster
            config: Clustering configuration
            vector_data: Optional pre-loaded vector data
            clustering_id: Optional clustering identifier
            
        Returns:
            Comprehensive clustering result
        """        try:
            start_time = datetime.now()
            
            # Generate clustering ID
            if not clustering_id:
                clustering_id = f"cluster_{content_type}_{datetime.now().timestamp()}"
            
            # Check cache
            cache_key = self._generate_cache_key(content_type, config)
            if self.cache_enabled and cache_key in self.clustering_cache:
                self.clustering_stats["cache_hits"] += 1
                logger.info(f"Retrieved cached clustering result: {cache_key}")
                return self.clustering_cache[cache_key]
            
            self.clustering_stats["cache_misses"] += 1
            
            # Load vector data if not provided
            if vector_data is None:
                vector_data = await self._load_vector_data(content_type)
            
            if len(vector_data) < 2:
                raise ClusteringError(f"Insufficient data for clustering: {len(vector_data)} vectors")
            
            # Prepare data
            content_ids, vectors, metadata = await self._prepare_clustering_data(
                vector_data, config
            )
            
            # Apply dimensionality reduction if configured
            reduced_vectors = await self._apply_dimensionality_reduction(
                vectors, config
            )
            
            # Perform clustering
            cluster_labels, cluster_centers = await self._perform_clustering(
                reduced_vectors, config
            )
            
            # Analyze clusters
            clusters = await self._analyze_clusters(
                content_ids, vectors, cluster_labels, cluster_centers, content_type
            )
            
            # Detect outliers and anomalies
            outliers = await self._detect_outliers(
                content_ids, vectors, cluster_labels, config
            )
            
            # Calculate quality metrics
            quality_metrics = await self._calculate_clustering_quality(
                vectors, cluster_labels, config
            )
            
            # Generate insights
            insights = await self._generate_clustering_insights(
                clusters, outliers, quality_metrics, content_type
            )
            
            # Create visualizations
            visualization_paths = await self._create_visualizations(
                reduced_vectors, cluster_labels, clusters, clustering_id
            )
            
            # Create result
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = ClusteringResult(
                clustering_id=clustering_id,
                content_type=content_type,
                algorithm_used=config.algorithm.value,
                total_vectors=len(vectors),
                n_clusters=len(clusters),
                clusters=clusters,
                outliers=outliers,
                quality_metrics=quality_metrics,
                execution_time=execution_time,
                config=config,
                visualization_paths=visualization_paths,
                insights=insights
            )
            
            # Cache result
            if self.cache_enabled:
                self.clustering_cache[cache_key] = result
            
            # Update statistics
            self._update_clustering_stats(execution_time, len(vectors), len(outliers))
            
            # Store quality history
            self.quality_history.append({
                "timestamp": datetime.now().isoformat(),
                "content_type": content_type,
                "algorithm": config.algorithm.value,
                "quality_metrics": quality_metrics
            })
            
            logger.info(
                f"Clustering completed: {len(clusters)} clusters, "
                f"{len(outliers)} outliers in {execution_time:.3f}s"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Vector clustering failed: {str(e)}")
            raise ClusteringError(f"Vector clustering failed: {str(e)}")
    
    @measure_execution_time
    async def detect_duplicates(
        self,
        content_type: str,
        similarity_threshold: float = 0.95,
        clustering_config: ClusteringConfig = None
    ) -> List[List[str]]:
        """        Detect potential duplicate content using clustering
        
        Args:
            content_type: Content type to analyze
            similarity_threshold: Similarity threshold for duplicates
            clustering_config: Optional clustering configuration
            
        Returns:
            List of duplicate groups (each group is a list of content IDs)
        """        try:
            # Use DBSCAN for duplicate detection
            if clustering_config is None:
                clustering_config = ClusteringConfig(
                    algorithm=ClusteringAlgorithm.DBSCAN,
                    eps=1.0 - similarity_threshold,  # Convert similarity to distance
                    min_samples=2,
                    mode=ClusteringMode.DUPLICATE_DETECTION
                )
            
            # Perform clustering
            result = await self.cluster_vectors(content_type, clustering_config)
            
            # Extract duplicate groups
            duplicate_groups = []
            
            for cluster in result.clusters:
                if cluster.size >= 2:  # Potential duplicates
                    # Calculate internal similarities
                    vectors = await self._get_vectors_for_content_ids(cluster.content_ids)
                    
                    if vectors:
                        # Check if vectors are highly similar
                        similarities = self._calculate_pairwise_similarities(vectors)
                        avg_similarity = np.mean(similarities)
                        
                        if avg_similarity >= similarity_threshold:
                            duplicate_groups.append(cluster.content_ids)
            
            logger.info(
                f"Duplicate detection completed: {len(duplicate_groups)} groups found"
            )
            
            return duplicate_groups
            
        except Exception as e:
            logger.error(f"Duplicate detection failed: {str(e)}")
            raise ClusteringError(f"Duplicate detection failed: {str(e)}")
    
    @measure_execution_time
    async def detect_anomalies(
        self,
        content_type: str,
        anomaly_threshold: float = 2.0,
        return_detailed_report: bool = True
    ) -> Union[List[str], List[AnomalyReport]]:
        """        Detect anomalous content using clustering-based approach
        
        Args:
            content_type: Content type to analyze
            anomaly_threshold: Anomaly threshold (standard deviations)
            return_detailed_report: Return detailed anomaly reports
            
        Returns:
            List of anomalous content IDs or detailed reports
        """        try:
            # Configure for anomaly detection
            config = ClusteringConfig(
                algorithm=ClusteringAlgorithm.DBSCAN,
                eps=0.3,
                min_samples=5,
                mode=ClusteringMode.ANOMALY_DETECTION,
                outlier_threshold=anomaly_threshold
            )
            
            # Perform clustering
            result = await self.cluster_vectors(content_type, config)
            
            if not return_detailed_report:
                return result.outliers
            
            # Generate detailed anomaly reports
            anomaly_reports = []
            
            for content_id in result.outliers:
                # Get vector for this content
                vector = await self._get_vector_for_content_id(content_id)
                
                if vector is not None:
                    # Calculate anomaly score
                    anomaly_score = await self._calculate_anomaly_score(
                        vector, result.clusters
                    )
                    
                    # Find nearest cluster
                    nearest_cluster, distance = await self._find_nearest_cluster(
                        vector, result.clusters
                    )
                    
                    # Generate explanation
                    explanation = await self._generate_anomaly_explanation(
                        anomaly_score, distance, nearest_cluster
                    )
                    
                    # Generate recommendation
                    recommendation = await self._generate_anomaly_recommendation(
                        anomaly_score, content_type
                    )
                    
                    report = AnomalyReport(
                        content_id=content_id,
                        anomaly_score=anomaly_score,
                        anomaly_type="clustering_outlier",
                        cluster_id=nearest_cluster.cluster_id if nearest_cluster else None,
                        distance_to_nearest=distance,
                        explanation=explanation,
                        recommendation=recommendation,
                        confidence=min(anomaly_score / anomaly_threshold, 1.0)
                    )
                    
                    anomaly_reports.append(report)
            
            # Update anomaly statistics
            self.clustering_stats["anomalies_detected"] += len(anomaly_reports)
            
            logger.info(f"Anomaly detection completed: {len(anomaly_reports)} anomalies found")
            return anomaly_reports
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {str(e)}")
            raise ClusteringError(f"Anomaly detection failed: {str(e)}")
    
    async def optimize_clustering_parameters(
        self,
        content_type: str,
        algorithm: ClusteringAlgorithm,
        parameter_ranges: Dict[str, List[Any]],
        evaluation_metric: str = "silhouette"
    ) -> Dict[str, Any]:
        """        Optimize clustering parameters using grid search
        
        Args:
            content_type: Content type to optimize for
            algorithm: Clustering algorithm to optimize
            parameter_ranges: Parameter ranges to search
            evaluation_metric: Metric for evaluation
            
        Returns:
            Best parameters and performance metrics
        """        try:
            # Load vector data
            vector_data = await self._load_vector_data(content_type)
            
            if len(vector_data) < 10:
                raise ClusteringError("Insufficient data for parameter optimization")
            
            best_score = -np.inf
            best_params = {}
            optimization_results = []
            
            # Generate parameter combinations
            param_combinations = self._generate_parameter_combinations(parameter_ranges)
            
            logger.info(
                f"Starting parameter optimization: {len(param_combinations)} combinations"
            )
            
            for i, params in enumerate(param_combinations):
                try:
                    # Create configuration
                    config = ClusteringConfig(
                        algorithm=algorithm,
                        **params
                    )
                    
                    # Perform clustering
                    result = await self.cluster_vectors(
                        content_type, config, vector_data,
                        clustering_id=f"opt_{i}"
                    )
                    
                    # Evaluate clustering quality
                    score = result.quality_metrics.get(evaluation_metric, 0.0)
                    
                    optimization_results.append({
                        "params": params,
                        "score": score,
                        "n_clusters": result.n_clusters,
                        "execution_time": result.execution_time
                    })
                    
                    if score > best_score:
                        best_score = score
                        best_params = params
                    
                    logger.debug(
                        f"Parameter set {i+1}/{len(param_combinations)}: "
                        f"score={score:.4f}, params={params}"
                    )
                
                except Exception as e:
                    logger.warning(f"Parameter set {i} failed: {str(e)}")
                    continue
            
            # Analyze optimization results
            optimization_analysis = {
                "best_parameters": best_params,
                "best_score": best_score,
                "algorithm": algorithm.value,
                "evaluation_metric": evaluation_metric,
                "total_combinations": len(param_combinations),
                "successful_combinations": len(optimization_results),
                "results": optimization_results
            }
            
            logger.info(
                f"Parameter optimization completed: best {evaluation_metric} = {best_score:.4f}"
            )
            
            return optimization_analysis
            
        except Exception as e:
            logger.error(f"Parameter optimization failed: {str(e)}")
            raise ClusteringError(f"Parameter optimization failed: {str(e)}")
    
    async def compare_clustering_algorithms(
        self,
        content_type: str,
        algorithms: List[ClusteringAlgorithm],
        evaluation_metrics: List[str] = ["silhouette", "calinski_harabasz", "davies_bouldin"]
    ) -> Dict[str, Dict[str, float]]:
        """        Compare performance of different clustering algorithms
        
        Args:
            content_type: Content type to analyze
            algorithms: Algorithms to compare
            evaluation_metrics: Metrics for comparison
            
        Returns:
            Comparison results for each algorithm
        """        try:
            # Load vector data once
            vector_data = await self._load_vector_data(content_type)
            
            comparison_results = {}
            
            for algorithm in algorithms:
                try:
                    # Use default configuration for algorithm
                    config = self.algorithm_configs.get(
                        algorithm, 
                        ClusteringConfig(algorithm=algorithm)
                    )
                    
                    # Perform clustering
                    result = await self.cluster_vectors(
                        content_type, config, vector_data,
                        clustering_id=f"compare_{algorithm.value}"
                    )
                    
                    # Extract metrics
                    algorithm_metrics = {}
                    for metric in evaluation_metrics:
                        algorithm_metrics[metric] = result.quality_metrics.get(metric, 0.0)
                    
                    # Add additional metrics
                    algorithm_metrics["execution_time"] = result.execution_time
                    algorithm_metrics["n_clusters"] = result.n_clusters
                    algorithm_metrics["n_outliers"] = len(result.outliers)
                    
                    comparison_results[algorithm.value] = algorithm_metrics
                    
                except Exception as e:
                    logger.error(f"Algorithm {algorithm.value} failed: {str(e)}")
                    comparison_results[algorithm.value] = {
                        metric: 0.0 for metric in evaluation_metrics
                    }
            
            logger.info(f"Algorithm comparison completed for {len(algorithms)} algorithms")
            return comparison_results
            
        except Exception as e:
            logger.error(f"Algorithm comparison failed: {str(e)}")
            raise ClusteringError(f"Algorithm comparison failed: {str(e)}")
    
    async def get_clustering_history(
        self, content_type: str = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get clustering history and quality trends"""        try:
            history = self.quality_history.copy()
            
            # Filter by content type if specified
            if content_type:
                history = [h for h in history if h["content_type"] == content_type]
            
            # Sort by timestamp (newest first) and limit
            history.sort(key=lambda x: x["timestamp"], reverse=True)
            return history[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get clustering history: {str(e)}")
            return []
    
    async def get_clustering_statistics(self) -> Dict[str, Any]:
        """Get comprehensive clustering statistics"""        try:
            stats = self.clustering_stats.copy()
            
            # Add derived metrics
            total_requests = stats["cache_hits"] + stats["cache_misses"]
            stats["cache_hit_ratio"] = stats["cache_hits"] / max(total_requests, 1)
            
            if stats["total_clusterings"] > 0:
                stats["avg_vectors_per_clustering"] = (
                    stats["total_vectors_processed"] / stats["total_clusterings"]
                )
                stats["anomaly_rate"] = (
                    stats["anomalies_detected"] / stats["total_vectors_processed"]
                )
            else:
                stats["avg_vectors_per_clustering"] = 0.0
                stats["anomaly_rate"] = 0.0
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get clustering statistics: {str(e)}")
            return {}
    
    async def _load_vector_data(self, content_type: str) -> List[Tuple[str, np.ndarray]]:
        """Load vector data from database"""        try:
            vector_data = []
            
            async with get_db_session() as session:
                stmt = select(ContentFingerprint).where(
                    and_(
                        ContentFingerprint.content_type == content_type,
                        ContentFingerprint.vector_embedding.isnot(None)
                    )
                ).limit(10000)  # Limit for performance
                
                result = await session.execute(stmt)
                fingerprints = result.scalars().all()
                
                for fp in fingerprints:
                    if fp.vector_embedding:
                        vector = np.frombuffer(fp.vector_embedding, dtype=np.float32)
                        vector_data.append((fp.content_id, vector))
            
            logger.info(f"Loaded {len(vector_data)} vectors for {content_type}")
            return vector_data
            
        except Exception as e:
            logger.error(f"Failed to load vector data: {str(e)}")
            raise VectorStoreError(f"Vector data loading failed: {str(e)}")
    
    async def _prepare_clustering_data(
        self, vector_data: List[Tuple[str, np.ndarray]], config: ClusteringConfig
    ) -> Tuple[List[str], np.ndarray, List[Dict]]:
        """Prepare data for clustering"""        try:
            content_ids = [item[0] for item in vector_data]
            vectors = np.array([item[1] for item in vector_data])
            
            # Normalize vectors if configured
            if config.normalize:
                scaler = StandardScaler()
                vectors = scaler.fit_transform(vectors)
            
            # Create metadata (placeholder for future enhancements)
            metadata = [{"content_id": cid} for cid in content_ids]
            
            return content_ids, vectors, metadata
            
        except Exception as e:
            logger.error(f"Data preparation failed: {str(e)}")
            raise ClusteringError(f"Data preparation failed: {str(e)}")
    
    async def _apply_dimensionality_reduction(
        self, vectors: np.ndarray, config: ClusteringConfig
    ) -> np.ndarray:
        """Apply dimensionality reduction if configured"""        try:
            if config.dimensionality_reduction == DimensionalityReduction.NONE:
                return vectors
            
            if vectors.shape[1] <= config.n_components:
                return vectors  # No reduction needed
            
            if config.dimensionality_reduction == DimensionalityReduction.PCA:
                reducer = PCA(n_components=config.n_components, random_state=config.random_state)
                reduced_vectors = reducer.fit_transform(vectors)
                
            elif config.dimensionality_reduction == DimensionalityReduction.UMAP:
                try:
                    import umap
                    reducer = umap.UMAP(
                        n_components=config.n_components,
                        random_state=config.random_state,
                        n_neighbors=min(15, len(vectors) - 1)
                    )
                    reduced_vectors = reducer.fit_transform(vectors)
                except ImportError:
                    logger.warning("UMAP not available, using PCA instead")
                    reducer = PCA(n_components=config.n_components, random_state=config.random_state)
                    reduced_vectors = reducer.fit_transform(vectors)
            
            else:
                # Default to PCA
                reducer = PCA(n_components=config.n_components, random_state=config.random_state)
                reduced_vectors = reducer.fit_transform(vectors)
            
            logger.info(
                f"Applied {config.dimensionality_reduction.value}: "
                f"{vectors.shape[1]} -> {reduced_vectors.shape[1]} dimensions"
            )
            
            return reduced_vectors
            
        except Exception as e:
            logger.error(f"Dimensionality reduction failed: {str(e)}")
            return vectors  # Return original vectors on failure
    
    async def _perform_clustering(
        self, vectors: np.ndarray, config: ClusteringConfig
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Perform clustering using specified algorithm"""        try:
            if config.algorithm == ClusteringAlgorithm.KMEANS:
                n_clusters = config.n_clusters or self._estimate_optimal_clusters(vectors)
                clusterer = KMeans(
                    n_clusters=n_clusters,
                    random_state=config.random_state,
                    n_init=10
                )
                labels = clusterer.fit_predict(vectors)
                centers = clusterer.cluster_centers_
            
            elif config.algorithm == ClusteringAlgorithm.DBSCAN:
                clusterer = DBSCAN(
                    eps=config.eps,
                    min_samples=config.min_samples,
                    metric='euclidean'
                )
                labels = clusterer.fit_predict(vectors)
                centers = self._calculate_cluster_centers(vectors, labels)
            
            elif config.algorithm == ClusteringAlgorithm.HIERARCHICAL:
                n_clusters = config.n_clusters or self._estimate_optimal_clusters(vectors)
                clusterer = AgglomerativeClustering(
                    n_clusters=n_clusters,
                    linkage='ward'
                )
                labels = clusterer.fit_predict(vectors)
                centers = self._calculate_cluster_centers(vectors, labels)
            
            elif config.algorithm == ClusteringAlgorithm.SPECTRAL:
                n_clusters = config.n_clusters or self._estimate_optimal_clusters(vectors)
                clusterer = SpectralClustering(
                    n_clusters=n_clusters,
                    random_state=config.random_state,
                    affinity='rbf'
                )
                labels = clusterer.fit_predict(vectors)
                centers = self._calculate_cluster_centers(vectors, labels)
            
            elif config.algorithm == ClusteringAlgorithm.GAUSSIAN_MIXTURE:
                n_clusters = config.n_clusters or self._estimate_optimal_clusters(vectors)
                clusterer = GaussianMixture(
                    n_components=n_clusters,
                    random_state=config.random_state
                )
                clusterer.fit(vectors)
                labels = clusterer.predict(vectors)
                centers = clusterer.means_
            
            elif config.algorithm == ClusteringAlgorithm.OPTICS:
                clusterer = OPTICS(
                    min_samples=config.min_samples,
                    eps=config.eps if config.eps != 0.5 else None
                )
                labels = clusterer.fit_predict(vectors)
                centers = self._calculate_cluster_centers(vectors, labels)
            
            elif config.algorithm == ClusteringAlgorithm.MEAN_SHIFT:
                clusterer = MeanShift()
                labels = clusterer.fit_predict(vectors)
                centers = clusterer.cluster_centers_
            
            else:
                raise ClusteringError(f"Unsupported algorithm: {config.algorithm}")
            
            logger.info(
                f"Clustering completed: {len(np.unique(labels))} clusters found "
                f"using {config.algorithm.value}"
            )
            
            return labels, centers
            
        except Exception as e:
            logger.error(f"Clustering execution failed: {str(e)}")
            raise ClusteringError(f"Clustering execution failed: {str(e)}")
    
    async def _analyze_clusters(
        self,
        content_ids: List[str],
        vectors: np.ndarray,
        labels: np.ndarray,
        centers: Optional[np.ndarray],
        content_type: str
    ) -> List[ClusterInfo]:
        """Analyze clustering results and create cluster information"""        try:
            clusters = []
            unique_labels = np.unique(labels)
            
            for label in unique_labels:
                if label == -1:  # Skip outlier label
                    continue
                
                # Get cluster members
                cluster_mask = (labels == label)
                cluster_vectors = vectors[cluster_mask]
                cluster_content_ids = [content_ids[i] for i in range(len(content_ids)) if cluster_mask[i]]
                
                if len(cluster_vectors) == 0:
                    continue
                
                # Calculate cluster properties
                if centers is not None and label < len(centers):
                    centroid = centers[label]
                else:
                    centroid = np.mean(cluster_vectors, axis=0)
                
                # Calculate cluster radius (max distance from centroid)
                distances = np.linalg.norm(cluster_vectors - centroid, axis=1)
                radius = np.max(distances)
                
                # Calculate cluster density
                density = len(cluster_vectors) / (radius ** 2 + 1e-8)
                
                # Calculate cluster quality score
                if len(cluster_vectors) > 1:
                    intra_distances = np.linalg.norm(
                        cluster_vectors[:, np.newaxis] - cluster_vectors[np.newaxis, :],
                        axis=2
                    )
                    avg_intra_distance = np.mean(intra_distances[intra_distances > 0])
                    quality_score = 1.0 / (1.0 + avg_intra_distance)
                else:
                    quality_score = 1.0
                
                # Calculate silhouette score for this cluster
                if len(cluster_vectors) > 1 and len(unique_labels) > 1:
                    try:
                        cluster_silhouette = silhouette_score(
                            vectors, labels, sample_size=min(1000, len(vectors))
                        )
                    except:
                        cluster_silhouette = 0.0
                else:
                    cluster_silhouette = 0.0
                
                # Select representative content
                representative_content = cluster_content_ids[0] if cluster_content_ids else ""
                
                cluster_info = ClusterInfo(
                    cluster_id=int(label),
                    content_type=content_type,
                    size=len(cluster_content_ids),
                    centroid=centroid,
                    radius=radius,
                    density=density,
                    quality_score=quality_score,
                    content_ids=cluster_content_ids,
                    representative_content=representative_content,
                    metadata={
                        "avg_intra_distance": avg_intra_distance if len(cluster_vectors) > 1 else 0.0,
                        "std_distances": np.std(distances),
                        "compactness": 1.0 / (radius + 1e-8)
                    },
                    created_at=datetime.now(timezone.utc),
                    silhouette_score=cluster_silhouette
                )
                
                clusters.append(cluster_info)
            
            # Sort clusters by size (largest first)
            clusters.sort(key=lambda x: x.size, reverse=True)
            
            return clusters
            
        except Exception as e:
            logger.error(f"Cluster analysis failed: {str(e)}")
            raise ClusteringError(f"Cluster analysis failed: {str(e)}")
    
    async def _detect_outliers(
        self,
        content_ids: List[str],
        vectors: np.ndarray,
        labels: np.ndarray,
        config: ClusteringConfig
    ) -> List[str]:
        """Detect outliers in clustering results"""        try:
            outliers = []
            
            # Method 1: Labels marked as -1 (for DBSCAN, OPTICS)
            outlier_mask = (labels == -1)
            outliers.extend([content_ids[i] for i in range(len(content_ids)) if outlier_mask[i]])
            
            # Method 2: Distance-based outlier detection
            if config.outlier_threshold > 0:
                # Calculate distances to cluster centers
                unique_labels = np.unique(labels)
                cluster_centers = self._calculate_cluster_centers(vectors, labels)
                
                for i, (content_id, vector) in enumerate(zip(content_ids, vectors)):
                    label = labels[i]
                    
                    if label != -1 and label < len(cluster_centers):
                        # Distance to assigned cluster center
                        distance = np.linalg.norm(vector - cluster_centers[label])
                        
                        # Calculate threshold based on cluster statistics
                        cluster_mask = (labels == label)
                        cluster_vectors = vectors[cluster_mask]
                        
                        if len(cluster_vectors) > 1:
                            cluster_distances = np.linalg.norm(
                                cluster_vectors - cluster_centers[label], axis=1
                            )
                            mean_distance = np.mean(cluster_distances)
                            std_distance = np.std(cluster_distances)
                            
                            threshold = mean_distance + (config.outlier_threshold * std_distance)
                            
                            if distance > threshold and content_id not in outliers:
                                outliers.append(content_id)
            
            logger.info(f"Detected {len(outliers)} outliers")
            return outliers
            
        except Exception as e:
            logger.error(f"Outlier detection failed: {str(e)}")
            return []
    
    async def _calculate_clustering_quality(
        self, vectors: np.ndarray, labels: np.ndarray, config: ClusteringConfig
    ) -> Dict[str, float]:
        """Calculate clustering quality metrics"""        try:
            quality_metrics = {}
            
            # Skip if all points are outliers or single cluster
            unique_labels = np.unique(labels)
            valid_labels = unique_labels[unique_labels != -1]
            
            if len(valid_labels) < 2:
                return {
                    "silhouette": 0.0,
                    "calinski_harabasz": 0.0,
                    "davies_bouldin": 1.0,
                    "inertia": 0.0,
                    "compactness": 0.0,
                    "separation": 0.0
                }
            
            # Silhouette score
            try:
                quality_metrics["silhouette"] = silhouette_score(
                    vectors, labels, sample_size=min(1000, len(vectors))
                )
            except:
                quality_metrics["silhouette"] = 0.0
            
            # Calinski-Harabasz score
            try:
                quality_metrics["calinski_harabasz"] = calinski_harabasz_score(vectors, labels)
            except:
                quality_metrics["calinski_harabasz"] = 0.0
            
            # Davies-Bouldin score (lower is better)
            try:
                quality_metrics["davies_bouldin"] = davies_bouldin_score(vectors, labels)
            except:
                quality_metrics["davies_bouldin"] = 1.0
            
            # Custom metrics
            quality_metrics.update(self._calculate_custom_metrics(vectors, labels))
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Quality calculation failed: {str(e)}")
            return {"overall_quality": 0.0}
    
    def _calculate_custom_metrics(
        self, vectors: np.ndarray, labels: np.ndarray
    ) -> Dict[str, float]:
        """Calculate custom clustering quality metrics"""        try:
            metrics = {}
            
            unique_labels = np.unique(labels)
            valid_labels = unique_labels[unique_labels != -1]
            
            if len(valid_labels) < 2:
                return {"inertia": 0.0, "compactness": 0.0, "separation": 0.0}
            
            # Calculate cluster centers
            cluster_centers = self._calculate_cluster_centers(vectors, labels)
            
            # Inertia (within-cluster sum of squares)
            inertia = 0.0
            for label in valid_labels:
                cluster_mask = (labels == label)
                cluster_vectors = vectors[cluster_mask]
                if len(cluster_vectors) > 0:
                    center = cluster_centers[label]
                    distances_sq = np.sum((cluster_vectors - center) ** 2, axis=1)
                    inertia += np.sum(distances_sq)
            
            metrics["inertia"] = inertia
            
            # Compactness (average within-cluster distance)
            total_points = 0
            total_compactness = 0.0
            
            for label in valid_labels:
                cluster_mask = (labels == label)
                cluster_vectors = vectors[cluster_mask]
                
                if len(cluster_vectors) > 1:
                    center = cluster_centers[label]
                    distances = np.linalg.norm(cluster_vectors - center, axis=1)
                    total_compactness += np.sum(distances)
                    total_points += len(cluster_vectors)
            
            metrics["compactness"] = total_compactness / max(total_points, 1)
            
            # Separation (minimum distance between cluster centers)
            if len(cluster_centers) > 1:
                center_distances = []
                for i in range(len(cluster_centers)):
                    for j in range(i + 1, len(cluster_centers)):
                        distance = np.linalg.norm(cluster_centers[i] - cluster_centers[j])
                        center_distances.append(distance)
                
                metrics["separation"] = np.min(center_distances) if center_distances else 0.0
            else:
                metrics["separation"] = 0.0
            
            return metrics
            
        except Exception as e:
            logger.error(f"Custom metrics calculation failed: {str(e)}")
            return {}
    
    def _calculate_cluster_centers(
        self, vectors: np.ndarray, labels: np.ndarray
    ) -> np.ndarray:
        """Calculate cluster centers for given labels"""        try:
            unique_labels = np.unique(labels)
            centers = []
            
            for label in unique_labels:
                if label == -1:  # Skip outlier label
                    continue
                
                cluster_mask = (labels == label)
                cluster_vectors = vectors[cluster_mask]
                
                if len(cluster_vectors) > 0:
                    center = np.mean(cluster_vectors, axis=0)
                    centers.append(center)
            
            return np.array(centers) if centers else np.array([])
            
        except Exception as e:
            logger.error(f"Cluster center calculation failed: {str(e)}")
            return np.array([])
    
    async def _generate_clustering_insights(
        self,
        clusters: List[ClusterInfo],
        outliers: List[str],
        quality_metrics: Dict[str, float],
        content_type: str
    ) -> Dict[str, Any]:
        """Generate insights from clustering results"""        try:
            insights = {
                "summary": {},
                "quality_assessment": {},
                "recommendations": [],
                "patterns": []
            }
            
            # Summary insights
            total_content = sum(cluster.size for cluster in clusters) + len(outliers)
            
            insights["summary"] = {
                "total_content_analyzed": total_content,
                "clusters_found": len(clusters),
                "outliers_detected": len(outliers),
                "outlier_ratio": len(outliers) / max(total_content, 1),
                "largest_cluster_size": max([c.size for c in clusters]) if clusters else 0,
                "average_cluster_size": np.mean([c.size for c in clusters]) if clusters else 0,
                "cluster_quality_distribution": {
                    "high_quality": len([c for c in clusters if c.quality_score > 0.8]),
                    "medium_quality": len([c for c in clusters if 0.5 < c.quality_score <= 0.8]),
                    "low_quality": len([c for c in clusters if c.quality_score <= 0.5])
                }
            }
            
            # Quality assessment
            overall_quality = quality_metrics.get("silhouette", 0.0)
            
            if overall_quality > 0.7:
                quality_rating = "Excellent"
            elif overall_quality > 0.5:
                quality_rating = "Good"
            elif overall_quality > 0.3:
                quality_rating = "Fair"
            else:
                quality_rating = "Poor"
            
            insights["quality_assessment"] = {
                "overall_rating": quality_rating,
                "silhouette_score": overall_quality,
                "cluster_cohesion": 1.0 - quality_metrics.get("davies_bouldin", 1.0),
                "cluster_separation": quality_metrics.get("calinski_harabasz", 0.0) / 1000.0
            }
            
            # Recommendations
            recommendations = []
            
            if overall_quality < 0.5:
                recommendations.append(
                    "Consider adjusting clustering parameters or trying a different algorithm"
                )
            
            if len(outliers) / max(total_content, 1) > 0.2:
                recommendations.append(
                    "High outlier ratio detected - consider anomaly investigation"
                )
            
            if len(clusters) > total_content * 0.5:
                recommendations.append(
                    "Many small clusters detected - consider increasing cluster size constraints"
                )
            
            insights["recommendations"] = recommendations
            
            # Pattern detection
            patterns = []
            
            if clusters:
                # Size distribution pattern
                sizes = [c.size for c in clusters]
                if np.std(sizes) / np.mean(sizes) > 1.0:
                    patterns.append("Highly uneven cluster size distribution detected")
                
                # Quality pattern
                qualities = [c.quality_score for c in clusters]
                if np.mean(qualities) > 0.8:
                    patterns.append("Consistently high-quality clusters")
                elif np.std(qualities) > 0.3:
                    patterns.append("Variable cluster quality - some clusters may need refinement")
            
            insights["patterns"] = patterns
            
            return insights
            
        except Exception as e:
            logger.error(f"Insight generation failed: {str(e)}")
            return {"summary": {}, "quality_assessment": {}, "recommendations": [], "patterns": []}
    
    async def _create_visualizations(
        self,
        vectors: np.ndarray,
        labels: np.ndarray,
        clusters: List[ClusterInfo],
        clustering_id: str
    ) -> List[str]:
        """Create visualizations for clustering results"""        try:
            visualization_paths = []
            
            if self.visualization_manager is None:
                return visualization_paths
            
            # Create output directory
            viz_dir = os.path.join(settings.STORAGE_PATH, "visualizations", "clustering", clustering_id)
            os.makedirs(viz_dir, exist_ok=True)
            
            # 2D scatter plot of clusters
            if vectors.shape[1] > 2:
                # Reduce to 2D for visualization
                pca = PCA(n_components=2)
                vectors_2d = pca.fit_transform(vectors)
            else:
                vectors_2d = vectors
            
            # Cluster scatter plot
            plt.figure(figsize=(12, 8))
            unique_labels = np.unique(labels)
            colors = plt.cm.Set3(np.linspace(0, 1, len(unique_labels)))
            
            for i, label in enumerate(unique_labels):
                if label == -1:
                    # Outliers in black
                    mask = (labels == label)
                    plt.scatter(
                        vectors_2d[mask, 0], vectors_2d[mask, 1],
                        c='black', marker='x', s=50, alpha=0.6, label='Outliers'
                    )
                else:
                    mask = (labels == label)
                    plt.scatter(
                        vectors_2d[mask, 0], vectors_2d[mask, 1],
                        c=[colors[i]], s=50, alpha=0.7, label=f'Cluster {label}'
                    )
            
            plt.title(f'Clustering Results - {clustering_id}')
            plt.xlabel('Component 1')
            plt.ylabel('Component 2')
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            
            scatter_path = os.path.join(viz_dir, "cluster_scatter.png")
            plt.savefig(scatter_path, dpi=300, bbox_inches='tight')
            plt.close()
            visualization_paths.append(scatter_path)
            
            # Cluster size distribution
            if clusters:
                plt.figure(figsize=(10, 6))
                cluster_sizes = [c.size for c in clusters]
                cluster_ids = [str(c.cluster_id) for c in clusters]
                
                plt.bar(cluster_ids, cluster_sizes)
                plt.title('Cluster Size Distribution')
                plt.xlabel('Cluster ID')
                plt.ylabel('Number of Items')
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                size_dist_path = os.path.join(viz_dir, "cluster_sizes.png")
                plt.savefig(size_dist_path, dpi=300, bbox_inches='tight')
                plt.close()
                visualization_paths.append(size_dist_path)
                
                # Cluster quality heatmap
                plt.figure(figsize=(10, 6))
                quality_scores = [c.quality_score for c in clusters]
                
                plt.bar(cluster_ids, quality_scores, color='skyblue')
                plt.title('Cluster Quality Scores')
                plt.xlabel('Cluster ID')
                plt.ylabel('Quality Score')
                plt.ylim(0, 1)
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                quality_path = os.path.join(viz_dir, "cluster_quality.png")
                plt.savefig(quality_path, dpi=300, bbox_inches='tight')
                plt.close()
                visualization_paths.append(quality_path)
            
            logger.info(f"Created {len(visualization_paths)} visualizations")
            return visualization_paths
            
        except Exception as e:
            logger.error(f"Visualization creation failed: {str(e)}")
            return []
    
    def _estimate_optimal_clusters(self, vectors: np.ndarray) -> int:
        """Estimate optimal number of clusters using elbow method"""        try:
            max_clusters = min(10, len(vectors) // 2)
            
            if max_clusters < 2:
                return 2
            
            inertias = []
            k_range = range(2, max_clusters + 1)
            
            for k in k_range:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                kmeans.fit(vectors)
                inertias.append(kmeans.inertia_)
            
            # Find elbow point
            if len(inertias) > 2:
                # Calculate second derivative
                second_derivatives = []
                for i in range(1, len(inertias) - 1):
                    second_deriv = inertias[i - 1] - 2 * inertias[i] + inertias[i + 1]
                    second_derivatives.append(second_deriv)
                
                # Find maximum second derivative (elbow point)
                elbow_idx = np.argmax(second_derivatives) + 1
                optimal_k = k_range[elbow_idx]
            else:
                optimal_k = 2
            
            return min(max(optimal_k, 2), max_clusters)
            
        except Exception as e:
            logger.error(f"Optimal cluster estimation failed: {str(e)}")
            return 3  # Default fallback
    
    def _generate_parameter_combinations(
        self, parameter_ranges: Dict[str, List[Any]]
    ) -> List[Dict[str, Any]]:
        """Generate all combinations of parameters for grid search"""        try:
            import itertools
            
            param_names = list(parameter_ranges.keys())
            param_values = list(parameter_ranges.values())
            
            combinations = []
            for combination in itertools.product(*param_values):
                param_dict = dict(zip(param_names, combination))
                combinations.append(param_dict)
            
            return combinations
            
        except Exception as e:
            logger.error(f"Parameter combination generation failed: {str(e)}")
            return []
    
    def _calculate_pairwise_similarities(self, vectors: List[np.ndarray]) -> List[float]:
        """Calculate pairwise similarities between vectors"""        try:
            from sklearn.metrics.pairwise import cosine_similarity
            
            similarities = []
            
            for i in range(len(vectors)):
                for j in range(i + 1, len(vectors)):
                    similarity = cosine_similarity(
                        vectors[i].reshape(1, -1),
                        vectors[j].reshape(1, -1)
                    )[0, 0]
                    similarities.append(similarity)
            
            return similarities
            
        except Exception as e:
            logger.error(f"Pairwise similarity calculation failed: {str(e)}")
            return []
    
    async def _get_vectors_for_content_ids(self, content_ids: List[str]) -> List[np.ndarray]:
        """Get vectors for specific content IDs"""        try:
            vectors = []
            
            async with get_db_session() as session:
                for content_id in content_ids:
                    stmt = select(ContentFingerprint).where(
                        ContentFingerprint.content_id == content_id
                    )
                    result = await session.execute(stmt)
                    fingerprint = result.scalar_one_or_none()
                    
                    if fingerprint and fingerprint.vector_embedding:
                        vector = np.frombuffer(fingerprint.vector_embedding, dtype=np.float32)
                        vectors.append(vector)
            
            return vectors
            
        except Exception as e:
            logger.error(f"Vector retrieval failed: {str(e)}")
            return []
    
    async def _get_vector_for_content_id(self, content_id: str) -> Optional[np.ndarray]:
        """Get vector for specific content ID"""        try:
            async with get_db_session() as session:
                stmt = select(ContentFingerprint).where(
                    ContentFingerprint.content_id == content_id
                )
                result = await session.execute(stmt)
                fingerprint = result.scalar_one_or_none()
                
                if fingerprint and fingerprint.vector_embedding:
                    return np.frombuffer(fingerprint.vector_embedding, dtype=np.float32)
                
                return None
                
        except Exception as e:
            logger.error(f"Single vector retrieval failed: {str(e)}")
            return None
    
    async def _calculate_anomaly_score(
        self, vector: np.ndarray, clusters: List[ClusterInfo]
    ) -> float:
        """Calculate anomaly score for a vector"""        try:
            if not clusters:
                return 1.0  # Maximum anomaly if no clusters
            
            # Find minimum distance to any cluster center
            min_distance = float('inf')
            
            for cluster in clusters:
                distance = np.linalg.norm(vector - cluster.centroid)
                min_distance = min(min_distance, distance)
            
            # Normalize distance to anomaly score (0-1)
            # Higher distance = higher anomaly score
            max_possible_distance = np.sqrt(len(vector))  # Rough estimate
            anomaly_score = min(min_distance / max_possible_distance, 1.0)
            
            return anomaly_score
            
        except Exception as e:
            logger.error(f"Anomaly score calculation failed: {str(e)}")
            return 0.5  # Default medium anomaly
    
    async def _find_nearest_cluster(
        self, vector: np.ndarray, clusters: List[ClusterInfo]
    ) -> Tuple[Optional[ClusterInfo], float]:
        """Find nearest cluster to a vector"""        try:
            if not clusters:
                return None, float('inf')
            
            nearest_cluster = None
            min_distance = float('inf')
            
            for cluster in clusters:
                distance = np.linalg.norm(vector - cluster.centroid)
                if distance < min_distance:
                    min_distance = distance
                    nearest_cluster = cluster
            
            return nearest_cluster, min_distance
            
        except Exception as e:
            logger.error(f"Nearest cluster search failed: {str(e)}")
            return None, float('inf')
    
    async def _generate_anomaly_explanation(
        self, anomaly_score: float, distance: float, nearest_cluster: Optional[ClusterInfo]
    ) -> str:
        """Generate explanation for anomaly detection"""        try:
            if anomaly_score > 0.8:
                severity = "high"
            elif anomaly_score > 0.6:
                severity = "medium"
            else:
                severity = "low"
            
            if nearest_cluster:
                explanation = (
                    f"Content shows {severity} anomaly (score: {anomaly_score:.3f}). "
                    f"Distance to nearest cluster {nearest_cluster.cluster_id}: {distance:.3f}. "
                    f"Nearest cluster has {nearest_cluster.size} members with "
                    f"quality score {nearest_cluster.quality_score:.3f}."
                )
            else:
                explanation = (
                    f"Content shows {severity} anomaly (score: {anomaly_score:.3f}). "
                    f"No similar clusters found."
                )
            
            return explanation
            
        except Exception as e:
            logger.error(f"Anomaly explanation generation failed: {str(e)}")
            return "Anomaly detected but explanation generation failed."
    
    async def _generate_anomaly_recommendation(
        self, anomaly_score: float, content_type: str
    ) -> str:
        """Generate recommendation for handling anomaly"""        try:
            if anomaly_score > 0.8:
                recommendation = (
                    "High anomaly detected. Recommend manual review for potential "
                    "quality issues, corrupted data, or novel content patterns."
                )
            elif anomaly_score > 0.6:
                recommendation = (
                    "Medium anomaly detected. Consider automated quality checks "
                    "and possible inclusion in training data for model improvement."
                )
            else:
                recommendation = (
                    "Low anomaly detected. Monitor for patterns but likely "
                    "acceptable variation in content."
                )
            
            # Content type specific recommendations
            if content_type == "audio":
                recommendation += " Check audio quality, format, and duration."
            elif content_type == "image":
                recommendation += " Verify image resolution, format, and visual content."
            elif content_type == "text":
                recommendation += " Review text length, language, and semantic content."
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Anomaly recommendation generation failed: {str(e)}")
            return "Review recommended for anomalous content."
    
    def _initialize_algorithm_configs(self) -> Dict[ClusteringAlgorithm, ClusteringConfig]:
        """Initialize default configurations for clustering algorithms"""        return {
            ClusteringAlgorithm.KMEANS: ClusteringConfig(
                algorithm=ClusteringAlgorithm.KMEANS,
                n_clusters=5,
                normalize=True
            ),
            ClusteringAlgorithm.DBSCAN: ClusteringConfig(
                algorithm=ClusteringAlgorithm.DBSCAN,
                eps=0.5,
                min_samples=5,
                normalize=True
            ),
            ClusteringAlgorithm.HIERARCHICAL: ClusteringConfig(
                algorithm=ClusteringAlgorithm.HIERARCHICAL,
                n_clusters=5,
                normalize=True
            ),
            ClusteringAlgorithm.SPECTRAL: ClusteringConfig(
                algorithm=ClusteringAlgorithm.SPECTRAL,
                n_clusters=5,
                normalize=True
            ),
            ClusteringAlgorithm.GAUSSIAN_MIXTURE: ClusteringConfig(
                algorithm=ClusteringAlgorithm.GAUSSIAN_MIXTURE,
                n_clusters=5,
                normalize=True
            ),
            ClusteringAlgorithm.OPTICS: ClusteringConfig(
                algorithm=ClusteringAlgorithm.OPTICS,
                min_samples=5,
                normalize=True
            ),
            ClusteringAlgorithm.MEAN_SHIFT: ClusteringConfig(
                algorithm=ClusteringAlgorithm.MEAN_SHIFT,
                normalize=True
            )
        }
    
    def _generate_cache_key(self, content_type: str, config: ClusteringConfig) -> str:
        """Generate cache key for clustering configuration"""        import hashlib
        
        config_str = (
            f"{content_type}_{config.algorithm.value}_{config.n_clusters}_"
            f"{config.eps}_{config.min_samples}_{config.normalize}_"
            f"{config.dimensionality_reduction.value}_{config.n_components}"
        )
        
        return hashlib.md5(config_str.encode()).hexdigest()
    
    def _update_clustering_stats(
        self, execution_time: float, vector_count: int, outlier_count: int
    ) -> None:
        """Update clustering performance statistics"""        self.clustering_stats["total_clusterings"] += 1
        self.clustering_stats["total_vectors_processed"] += vector_count
        
        # Update average execution time
        total = self.clustering_stats["total_clusterings"]
        current_avg = self.clustering_stats["avg_execution_time"]
        new_avg = ((current_avg * (total - 1)) + execution_time) / total
        self.clustering_stats["avg_execution_time"] = new_avg
    
    async def close(self) -> None:
        """Close clustering engine and cleanup resources"""        try:
            # Clear cache
            self.clustering_cache.clear()
            
            # Close visualization manager
            if self.visualization_manager:
                await self.visualization_manager.close()
            
            # Close anomaly detector
            if self.anomaly_detector:
                await self.anomaly_detector.close()
            
            logger.info("Vector clustering engine closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing vector clustering engine: {str(e)}")
