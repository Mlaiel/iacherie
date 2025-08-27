"""
Vector Operations - Advanced Vector Database and Similarity Engine

Provides comprehensive vector operations for content similarity matching,
embedding storage and retrieval, and high-performance similarity search.
Integrates with FAISS and other vector databases for scalable operations.

Features:
- High-performance vector similarity search
- Multi-modal embedding storage
- Batch vector operations
- Real-time similarity matching
- Vector clustering and analysis
- Dimensionality reduction and optimization

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import numpy as np
from datetime import datetime
import json
import pickle

# Vector processing libraries
import faiss
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
import scipy.spatial.distance as distance

# Core Dependencies
from ..adapters.vector_adapter import VectorAdapter
from ..processors.embedding_processor import EmbeddingProcessor
from ..engines.similarity_engine import SimilarityEngine
from ..storage.vector_storage import VectorStorage


class VectorType(Enum):
    """Types of vectors supported"""
    CONTENT_EMBEDDING = "content_embedding"
    AUDIO_EMBEDDING = "audio_embedding"
    VIDEO_EMBEDDING = "video_embedding"
    IMAGE_EMBEDDING = "image_embedding"
    TEXT_EMBEDDING = "text_embedding"
    USER_PROFILE = "user_profile"
    HYBRID_EMBEDDING = "hybrid_embedding"


class SimilarityMetric(Enum):
    """Similarity metrics available"""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    MANHATTAN = "manhattan"
    DOT_PRODUCT = "dot_product"
    JACCARD = "jaccard"
    HAMMING = "hamming"


class IndexType(Enum):
    """Vector index types"""
    FLAT = "flat"
    IVF = "ivf"
    HNSW = "hnsw"
    LSH = "lsh"
    PRODUCT_QUANTIZATION = "pq"


@dataclass
class VectorDocument:
    """Vector document with metadata"""
    vector_id: str
    embedding: np.ndarray
    vector_type: VectorType
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    source_id: Optional[str] = None
    confidence: Optional[float] = None


@dataclass
class SimilarityMatch:
    """Similarity search result"""
    document: VectorDocument
    similarity_score: float
    distance: float
    rank: int
    metadata_match: Optional[Dict[str, Any]] = None


@dataclass
class ClusterResult:
    """Clustering analysis result"""
    cluster_id: int
    cluster_center: np.ndarray
    cluster_size: int
    documents: List[VectorDocument]
    coherence_score: float
    representative_documents: List[VectorDocument]


@dataclass
class VectorAnalysis:
    """Vector space analysis result"""
    total_vectors: int
    dimensions: int
    density_metrics: Dict[str, float]
    cluster_analysis: List[ClusterResult]
    outliers: List[VectorDocument]
    dimensionality_recommendation: Dict[str, Any]


class VectorOperations:
    """
    Advanced vector operations engine for high-performance similarity matching
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize vector operations engine
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self._initialize_indexes()
        self._initialize_processors()
        self._initialize_storage()
        
        # Vector storage and tracking
        self.vector_documents = {}
        self.type_indexes = {}
        self.performance_metrics = {
            "total_vectors": 0,
            "search_operations": 0,
            "average_search_time": 0.0,
            "index_update_count": 0
        }
    
    def _initialize_indexes(self) -> None:
        """Initialize vector indexes for different types"""
        try:
            # Default dimensions for different vector types
            self.vector_dimensions = {
                VectorType.CONTENT_EMBEDDING: 512,
                VectorType.AUDIO_EMBEDDING: 128,
                VectorType.VIDEO_EMBEDDING: 512,
                VectorType.IMAGE_EMBEDDING: 512,
                VectorType.TEXT_EMBEDDING: 384,
                VectorType.USER_PROFILE: 256,
                VectorType.HYBRID_EMBEDDING: 768
            }
            
            # Initialize FAISS indexes for each vector type
            self.faiss_indexes = {}
            self.index_configurations = {}
            
            for vector_type, dimension in self.vector_dimensions.items():
                # Create flat index for exact search (can be changed to IVF for large datasets)
                index = faiss.IndexFlatIP(dimension)  # Inner Product (cosine similarity)
                self.faiss_indexes[vector_type] = index
                
                # Track index configuration
                self.index_configurations[vector_type] = {
                    "type": "flat",
                    "dimension": dimension,
                    "metric": "inner_product",
                    "trained": True
                }
            
            # Initialize clustering models
            self.clustering_models = {
                "kmeans": KMeans(n_clusters=10, random_state=42),
                "dbscan": DBSCAN(eps=0.5, min_samples=5)
            }
            
            # Initialize dimensionality reduction models
            self.reduction_models = {
                "pca": PCA(n_components=0.95),  # Keep 95% of variance
                "tsne": TSNE(n_components=2, random_state=42)
            }
            
            self.logger.info("Vector indexes initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize vector indexes: {e}")
            raise
    
    def _initialize_processors(self) -> None:
        """Initialize vector processors"""
        self.vector_adapter = VectorAdapter(self.config)
        self.embedding_processor = EmbeddingProcessor(self.config)
        self.similarity_engine = SimilarityEngine(self.config)
    
    def _initialize_storage(self) -> None:
        """Initialize vector storage"""
        self.vector_storage = VectorStorage(self.config)
    
    async def add_vector(
        self,
        vector_id: str,
        embedding: np.ndarray,
        vector_type: VectorType,
        metadata: Dict[str, Any],
        source_id: Optional[str] = None,
        confidence: Optional[float] = None
    ) -> bool:
        """
        Add a vector to the appropriate index
        
        Args:
            vector_id: Unique identifier for the vector
            embedding: Vector embedding
            vector_type: Type of vector
            metadata: Associated metadata
            source_id: Source content ID
            confidence: Confidence score for the embedding
            
        Returns:
            bool: Success status
        """
        try:
            # Validate embedding dimensions
            expected_dim = self.vector_dimensions[vector_type]
            if embedding.shape[0] != expected_dim:
                # Resize or pad embedding if needed
                embedding = self._resize_embedding(embedding, expected_dim)
            
            # Normalize embedding for cosine similarity
            embedding_normalized = embedding / np.linalg.norm(embedding)
            
            # Create vector document
            document = VectorDocument(
                vector_id=vector_id,
                embedding=embedding_normalized,
                vector_type=vector_type,
                metadata=metadata,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                source_id=source_id,
                confidence=confidence
            )
            
            # Add to appropriate FAISS index
            faiss_index = self.faiss_indexes[vector_type]
            faiss_index.add(embedding_normalized.reshape(1, -1))
            
            # Store document
            self.vector_documents[vector_id] = document
            
            # Update type-specific tracking
            if vector_type not in self.type_indexes:
                self.type_indexes[vector_type] = []
            self.type_indexes[vector_type].append(vector_id)
            
            # Update performance metrics
            self.performance_metrics["total_vectors"] += 1
            self.performance_metrics["index_update_count"] += 1
            
            self.logger.debug(f"Added vector {vector_id} of type {vector_type.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add vector {vector_id}: {e}")
            return False
    
    def _resize_embedding(self, embedding: np.ndarray, target_dim: int) -> np.ndarray:
        """Resize embedding to target dimension"""
        current_dim = embedding.shape[0]
        
        if current_dim > target_dim:
            # Truncate
            return embedding[:target_dim]
        elif current_dim < target_dim:
            # Pad with zeros
            padding = np.zeros(target_dim - current_dim)
            return np.concatenate([embedding, padding])
        else:
            return embedding
    
    async def search_similar(
        self,
        query_embedding: np.ndarray,
        vector_type: VectorType,
        top_k: int = 10,
        similarity_threshold: float = 0.0,
        metadata_filters: Optional[Dict[str, Any]] = None
    ) -> List[SimilarityMatch]:
        """
        Search for similar vectors
        
        Args:
            query_embedding: Query vector
            vector_type: Type of vectors to search
            top_k: Number of top results
            similarity_threshold: Minimum similarity threshold
            metadata_filters: Optional metadata filters
            
        Returns:
            List[SimilarityMatch]: Similar vectors with scores
        """
        start_time = datetime.now()
        
        try:
            # Validate and normalize query embedding
            expected_dim = self.vector_dimensions[vector_type]
            if query_embedding.shape[0] != expected_dim:
                query_embedding = self._resize_embedding(query_embedding, expected_dim)
            
            query_normalized = query_embedding / np.linalg.norm(query_embedding)
            
            # Get appropriate FAISS index
            faiss_index = self.faiss_indexes[vector_type]
            
            if faiss_index.ntotal == 0:
                return []
            
            # Perform similarity search
            search_k = min(top_k * 2, faiss_index.ntotal)  # Search more to allow for filtering
            similarities, indices = faiss_index.search(
                query_normalized.reshape(1, -1), 
                search_k
            )
            
            # Get vector IDs for this type
            type_vector_ids = self.type_indexes.get(vector_type, [])
            
            # Process results
            matches = []
            for i, (similarity, index) in enumerate(zip(similarities[0], indices[0])):
                if index >= len(type_vector_ids):
                    continue
                
                vector_id = type_vector_ids[index]
                document = self.vector_documents.get(vector_id)
                
                if document is None:
                    continue
                
                # Check similarity threshold
                if similarity < similarity_threshold:
                    continue
                
                # Apply metadata filters
                if metadata_filters and not self._matches_metadata_filters(document.metadata, metadata_filters):
                    continue
                
                # Calculate distance
                distance_value = 1.0 - similarity  # Convert similarity to distance
                
                match = SimilarityMatch(
                    document=document,
                    similarity_score=float(similarity),
                    distance=float(distance_value),
                    rank=len(matches) + 1
                )
                
                matches.append(match)
                
                if len(matches) >= top_k:
                    break
            
            # Update performance metrics
            search_time = (datetime.now() - start_time).total_seconds()
            self._update_search_metrics(search_time)
            
            self.logger.debug(f"Found {len(matches)} similar vectors in {search_time:.3f}s")
            return matches
            
        except Exception as e:
            self.logger.error(f"Vector similarity search failed: {e}")
            return []
    
    def _matches_metadata_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if metadata matches filters"""
        for key, value in filters.items():
            if key not in metadata:
                return False
            
            metadata_value = metadata[key]
            
            # Handle different filter types
            if isinstance(value, list):
                if metadata_value not in value:
                    return False
            elif isinstance(value, dict):
                # Range filters
                if 'min' in value and metadata_value < value['min']:
                    return False
                if 'max' in value and metadata_value > value['max']:
                    return False
            else:
                if metadata_value != value:
                    return False
        
        return True
    
    async def batch_search(
        self,
        query_embeddings: List[np.ndarray],
        vector_type: VectorType,
        top_k: int = 10
    ) -> List[List[SimilarityMatch]]:
        """Perform batch similarity search"""
        results = []
        
        for query_embedding in query_embeddings:
            matches = await self.search_similar(query_embedding, vector_type, top_k)
            results.append(matches)
        
        return results
    
    async def cluster_vectors(
        self,
        vector_type: VectorType,
        algorithm: str = "kmeans",
        n_clusters: Optional[int] = None
    ) -> List[ClusterResult]:
        """
        Cluster vectors of a specific type
        
        Args:
            vector_type: Type of vectors to cluster
            algorithm: Clustering algorithm ("kmeans", "dbscan")
            n_clusters: Number of clusters (for kmeans)
            
        Returns:
            List[ClusterResult]: Clustering results
        """
        try:
            # Get vectors of specified type
            vector_ids = self.type_indexes.get(vector_type, [])
            if len(vector_ids) < 2:
                return []
            
            documents = [self.vector_documents[vid] for vid in vector_ids]
            embeddings = np.array([doc.embedding for doc in documents])
            
            # Perform clustering
            if algorithm == "kmeans":
                if n_clusters is None:
                    n_clusters = min(10, max(2, len(embeddings) // 10))
                
                clustering_model = KMeans(n_clusters=n_clusters, random_state=42)
                cluster_labels = clustering_model.fit_predict(embeddings)
                cluster_centers = clustering_model.cluster_centers_
                
            elif algorithm == "dbscan":
                clustering_model = DBSCAN(eps=0.5, min_samples=5)
                cluster_labels = clustering_model.fit_predict(embeddings)
                
                # Calculate cluster centers for DBSCAN
                unique_labels = set(cluster_labels)
                cluster_centers = []
                for label in unique_labels:
                    if label != -1:  # Ignore noise points
                        cluster_mask = cluster_labels == label
                        center = embeddings[cluster_mask].mean(axis=0)
                        cluster_centers.append(center)
                    else:
                        cluster_centers.append(np.zeros(embeddings.shape[1]))
                
                cluster_centers = np.array(cluster_centers)
            
            else:
                raise ValueError(f"Unsupported clustering algorithm: {algorithm}")
            
            # Process clustering results
            cluster_results = []
            unique_labels = set(cluster_labels)
            
            for i, label in enumerate(sorted(unique_labels)):
                if label == -1:  # Skip noise for DBSCAN
                    continue
                
                # Get documents in this cluster
                cluster_mask = cluster_labels == label
                cluster_documents = [doc for j, doc in enumerate(documents) if cluster_mask[j]]
                
                # Calculate coherence score
                cluster_embeddings = embeddings[cluster_mask]
                coherence_score = self._calculate_coherence(cluster_embeddings)
                
                # Find representative documents
                if len(cluster_centers) > i:
                    cluster_center = cluster_centers[i]
                    representative_docs = self._find_representative_documents(
                        cluster_documents, cluster_center, top_k=3
                    )
                else:
                    representative_docs = cluster_documents[:3]
                
                cluster_result = ClusterResult(
                    cluster_id=label,
                    cluster_center=cluster_centers[i] if len(cluster_centers) > i else np.zeros(embeddings.shape[1]),
                    cluster_size=len(cluster_documents),
                    documents=cluster_documents,
                    coherence_score=coherence_score,
                    representative_documents=representative_docs
                )
                
                cluster_results.append(cluster_result)
            
            self.logger.info(f"Clustered {len(embeddings)} vectors into {len(cluster_results)} clusters")
            return cluster_results
            
        except Exception as e:
            self.logger.error(f"Vector clustering failed: {e}")
            return []
    
    def _calculate_coherence(self, embeddings: np.ndarray) -> float:
        """Calculate cluster coherence score"""
        if len(embeddings) <= 1:
            return 1.0
        
        # Calculate pairwise cosine similarities
        similarities = cosine_similarity(embeddings)
        
        # Average similarity excluding diagonal
        mask = np.ones_like(similarities, dtype=bool)
        np.fill_diagonal(mask, False)
        
        return float(similarities[mask].mean())
    
    def _find_representative_documents(
        self,
        documents: List[VectorDocument],
        cluster_center: np.ndarray,
        top_k: int = 3
    ) -> List[VectorDocument]:
        """Find most representative documents for a cluster"""
        if not documents:
            return []
        
        # Calculate distances to cluster center
        distances = []
        for doc in documents:
            distance = np.linalg.norm(doc.embedding - cluster_center)
            distances.append((doc, distance))
        
        # Sort by distance and return closest
        distances.sort(key=lambda x: x[1])
        return [doc for doc, _ in distances[:top_k]]
    
    async def analyze_vector_space(
        self,
        vector_type: VectorType,
        sample_size: Optional[int] = None
    ) -> VectorAnalysis:
        """
        Analyze vector space characteristics
        
        Args:
            vector_type: Type of vectors to analyze
            sample_size: Sample size for analysis (None for all)
            
        Returns:
            VectorAnalysis: Comprehensive vector space analysis
        """
        try:
            # Get vectors of specified type
            vector_ids = self.type_indexes.get(vector_type, [])
            if not vector_ids:
                return VectorAnalysis(
                    total_vectors=0,
                    dimensions=0,
                    density_metrics={},
                    cluster_analysis=[],
                    outliers=[],
                    dimensionality_recommendation={}
                )
            
            documents = [self.vector_documents[vid] for vid in vector_ids]
            
            # Sample if requested
            if sample_size and len(documents) > sample_size:
                import random
                documents = random.sample(documents, sample_size)
            
            embeddings = np.array([doc.embedding for doc in documents])
            
            # Calculate density metrics
            density_metrics = self._calculate_density_metrics(embeddings)
            
            # Perform clustering analysis
            cluster_analysis = await self.cluster_vectors(vector_type)
            
            # Find outliers
            outliers = self._find_outliers(documents, embeddings)
            
            # Dimensionality recommendation
            dimensionality_recommendation = self._analyze_dimensionality(embeddings)
            
            return VectorAnalysis(
                total_vectors=len(embeddings),
                dimensions=embeddings.shape[1],
                density_metrics=density_metrics,
                cluster_analysis=cluster_analysis,
                outliers=outliers,
                dimensionality_recommendation=dimensionality_recommendation
            )
            
        except Exception as e:
            self.logger.error(f"Vector space analysis failed: {e}")
            return VectorAnalysis(
                total_vectors=0,
                dimensions=0,
                density_metrics={},
                cluster_analysis=[],
                outliers=[],
                dimensionality_recommendation={}
            )
    
    def _calculate_density_metrics(self, embeddings: np.ndarray) -> Dict[str, float]:
        """Calculate vector space density metrics"""
        if len(embeddings) < 2:
            return {}
        
        # Calculate pairwise distances
        distances = euclidean_distances(embeddings)
        
        # Remove diagonal (self-distances)
        mask = np.ones_like(distances, dtype=bool)
        np.fill_diagonal(mask, False)
        distances_flat = distances[mask]
        
        # Calculate metrics
        return {
            "mean_distance": float(np.mean(distances_flat)),
            "std_distance": float(np.std(distances_flat)),
            "min_distance": float(np.min(distances_flat)),
            "max_distance": float(np.max(distances_flat)),
            "density_ratio": float(1.0 / (1.0 + np.mean(distances_flat))),
            "variance_explained": float(np.var(embeddings, axis=0).sum())
        }
    
    def _find_outliers(
        self,
        documents: List[VectorDocument],
        embeddings: np.ndarray,
        threshold: float = 2.0
    ) -> List[VectorDocument]:
        """Find outlier vectors using statistical methods"""
        if len(embeddings) < 3:
            return []
        
        # Calculate mean and standard deviation
        mean_embedding = np.mean(embeddings, axis=0)
        distances = [np.linalg.norm(emb - mean_embedding) for emb in embeddings]
        
        # Find outliers using z-score
        mean_distance = np.mean(distances)
        std_distance = np.std(distances)
        
        outliers = []
        for i, distance in enumerate(distances):
            z_score = abs(distance - mean_distance) / std_distance if std_distance > 0 else 0
            if z_score > threshold:
                outliers.append(documents[i])
        
        return outliers
    
    def _analyze_dimensionality(self, embeddings: np.ndarray) -> Dict[str, Any]:
        """Analyze optimal dimensionality for embeddings"""
        if len(embeddings) < 2:
            return {}
        
        try:
            # Perform PCA to analyze variance
            pca = PCA()
            pca.fit(embeddings)
            
            # Calculate cumulative variance ratio
            cumvar = np.cumsum(pca.explained_variance_ratio_)
            
            # Find dimensions for different variance levels
            dims_80 = np.argmax(cumvar >= 0.8) + 1
            dims_90 = np.argmax(cumvar >= 0.9) + 1
            dims_95 = np.argmax(cumvar >= 0.95) + 1
            
            return {
                "current_dimensions": embeddings.shape[1],
                "intrinsic_dimensions": {
                    "80_percent_variance": int(dims_80),
                    "90_percent_variance": int(dims_90),
                    "95_percent_variance": int(dims_95)
                },
                "variance_ratio": pca.explained_variance_ratio_.tolist()[:10],
                "recommendation": {
                    "reduce_dimensions": dims_95 < embeddings.shape[1] * 0.8,
                    "suggested_dimensions": int(dims_95) if dims_95 < embeddings.shape[1] * 0.8 else embeddings.shape[1]
                }
            }
            
        except Exception as e:
            self.logger.warning(f"Dimensionality analysis failed: {e}")
            return {}
    
    async def reduce_dimensionality(
        self,
        vector_type: VectorType,
        method: str = "pca",
        target_dimensions: Optional[int] = None
    ) -> bool:
        """
        Reduce dimensionality of vectors
        
        Args:
            vector_type: Type of vectors to reduce
            method: Reduction method ("pca", "tsne")
            target_dimensions: Target number of dimensions
            
        Returns:
            bool: Success status
        """
        try:
            # Get vectors of specified type
            vector_ids = self.type_indexes.get(vector_type, [])
            if not vector_ids:
                return False
            
            documents = [self.vector_documents[vid] for vid in vector_ids]
            embeddings = np.array([doc.embedding for doc in documents])
            
            # Determine target dimensions
            if target_dimensions is None:
                if method == "pca":
                    target_dimensions = min(128, embeddings.shape[1] // 2)
                else:  # tsne
                    target_dimensions = 2
            
            # Apply dimensionality reduction
            if method == "pca":
                reducer = PCA(n_components=target_dimensions)
                reduced_embeddings = reducer.fit_transform(embeddings)
            elif method == "tsne":
                reducer = TSNE(n_components=target_dimensions, random_state=42)
                reduced_embeddings = reducer.fit_transform(embeddings)
            else:
                raise ValueError(f"Unsupported reduction method: {method}")
            
            # Update vector documents with reduced embeddings
            for i, vector_id in enumerate(vector_ids):
                self.vector_documents[vector_id].embedding = reduced_embeddings[i]
                self.vector_documents[vector_id].updated_at = datetime.now()
            
            # Update vector dimensions configuration
            self.vector_dimensions[vector_type] = target_dimensions
            
            # Rebuild FAISS index
            await self._rebuild_index(vector_type)
            
            self.logger.info(f"Reduced {vector_type.value} vectors to {target_dimensions} dimensions")
            return True
            
        except Exception as e:
            self.logger.error(f"Dimensionality reduction failed: {e}")
            return False
    
    async def _rebuild_index(self, vector_type: VectorType) -> None:
        """Rebuild FAISS index for a vector type"""
        try:
            # Get new dimension
            new_dimension = self.vector_dimensions[vector_type]
            
            # Create new index
            new_index = faiss.IndexFlatIP(new_dimension)
            
            # Add all vectors to new index
            vector_ids = self.type_indexes.get(vector_type, [])
            if vector_ids:
                embeddings = []
                for vector_id in vector_ids:
                    doc = self.vector_documents[vector_id]
                    embeddings.append(doc.embedding)
                
                embeddings_array = np.array(embeddings)
                new_index.add(embeddings_array)
            
            # Replace old index
            self.faiss_indexes[vector_type] = new_index
            self.index_configurations[vector_type]["dimension"] = new_dimension
            
            self.logger.info(f"Rebuilt index for {vector_type.value}")
            
        except Exception as e:
            self.logger.error(f"Index rebuild failed for {vector_type.value}: {e}")
    
    async def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector from storage"""
        try:
            if vector_id not in self.vector_documents:
                return False
            
            document = self.vector_documents[vector_id]
            vector_type = document.vector_type
            
            # Remove from tracking
            if vector_type in self.type_indexes and vector_id in self.type_indexes[vector_type]:
                self.type_indexes[vector_type].remove(vector_id)
            
            # Remove document
            del self.vector_documents[vector_id]
            
            # Note: FAISS doesn't support individual deletion, so we'd need to rebuild
            # For production, consider using a more advanced vector DB that supports deletion
            
            # Update metrics
            self.performance_metrics["total_vectors"] -= 1
            
            self.logger.debug(f"Deleted vector {vector_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete vector {vector_id}: {e}")
            return False
    
    def _update_search_metrics(self, search_time: float) -> None:
        """Update search performance metrics"""
        self.performance_metrics["search_operations"] += 1
        total_searches = self.performance_metrics["search_operations"]
        current_avg = self.performance_metrics["average_search_time"]
        
        # Update running average
        self.performance_metrics["average_search_time"] = (
            (current_avg * (total_searches - 1) + search_time) / total_searches
        )
    
    async def get_vector_info(self, vector_id: str) -> Optional[VectorDocument]:
        """Get information about a specific vector"""
        return self.vector_documents.get(vector_id)
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get vector operations performance metrics"""
        metrics = self.performance_metrics.copy()
        
        # Add index information
        metrics["indexes"] = {}
        for vector_type, index in self.faiss_indexes.items():
            metrics["indexes"][vector_type.value] = {
                "total_vectors": index.ntotal,
                "dimension": self.vector_dimensions[vector_type],
                "is_trained": index.is_trained
            }
        
        return metrics
    
    async def backup_vectors(self, vector_type: Optional[VectorType] = None) -> Dict[str, Any]:
        """Backup vectors to storage"""
        try:
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "vectors": {},
                "indexes": {}
            }
            
            # Backup specific type or all types
            types_to_backup = [vector_type] if vector_type else list(VectorType)
            
            for vtype in types_to_backup:
                if vtype in self.type_indexes:
                    vector_ids = self.type_indexes[vtype]
                    backup_data["vectors"][vtype.value] = []
                    
                    for vid in vector_ids:
                        doc = self.vector_documents[vid]
                        doc_data = {
                            "vector_id": doc.vector_id,
                            "embedding": doc.embedding.tolist(),
                            "metadata": doc.metadata,
                            "source_id": doc.source_id,
                            "confidence": doc.confidence,
                            "created_at": doc.created_at.isoformat(),
                            "updated_at": doc.updated_at.isoformat()
                        }
                        backup_data["vectors"][vtype.value].append(doc_data)
                    
                    # Backup index configuration
                    backup_data["indexes"][vtype.value] = self.index_configurations[vtype]
            
            return backup_data
            
        except Exception as e:
            self.logger.error(f"Vector backup failed: {e}")
            return {}
    
    async def restore_vectors(self, backup_data: Dict[str, Any]) -> bool:
        """Restore vectors from backup"""
        try:
            for type_name, vectors_data in backup_data.get("vectors", {}).items():
                vector_type = VectorType(type_name)
                
                for vector_data in vectors_data:
                    embedding = np.array(vector_data["embedding"])
                    
                    await self.add_vector(
                        vector_id=vector_data["vector_id"],
                        embedding=embedding,
                        vector_type=vector_type,
                        metadata=vector_data["metadata"],
                        source_id=vector_data.get("source_id"),
                        confidence=vector_data.get("confidence")
                    )
            
            self.logger.info("Vector restore completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Vector restore failed: {e}")
            return False
    
    async def clear_vectors(self, vector_type: Optional[VectorType] = None) -> None:
        """Clear vectors of specified type or all vectors"""
        if vector_type:
            # Clear specific type
            if vector_type in self.type_indexes:
                vector_ids = self.type_indexes[vector_type].copy()
                for vid in vector_ids:
                    await self.delete_vector(vid)
                
                # Reset index
                dimension = self.vector_dimensions[vector_type]
                self.faiss_indexes[vector_type] = faiss.IndexFlatIP(dimension)
        else:
            # Clear all vectors
            self.vector_documents.clear()
            self.type_indexes.clear()
            
            # Reset all indexes
            for vector_type, dimension in self.vector_dimensions.items():
                self.faiss_indexes[vector_type] = faiss.IndexFlatIP(dimension)
            
            # Reset metrics
            self.performance_metrics["total_vectors"] = 0
        
        self.logger.info(f"Cleared vectors: {vector_type.value if vector_type else 'all'}")
