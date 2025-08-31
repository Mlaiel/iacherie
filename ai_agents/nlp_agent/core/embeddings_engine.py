"""Embeddings Engine - Advanced Text Embeddings and Vector Operations
==================================================================

Advanced text embeddings engine for generating, managing, and performing operations
on high-quality semantic embeddings using state-of-the-art models.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""import logging
import asyncio
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import pickle
import os
from collections import defaultdict

try:
    from transformers import AutoTokenizer, AutoModel, pipeline
    import torch
    import torch.nn.functional as F
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers library not available. Using fallback embeddings.")

try:
    from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
    from sklearn.cluster import KMeans
    from sklearn.neighbors import NearestNeighbors
    import scipy.spatial.distance as distance
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available. Limited embedding operations.")

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("Faiss not available. Using basic similarity search.")

from .config import NLPAgentConfig, default_config

# Setup logging
logger = logging.getLogger(__name__)

class EmbeddingModel(Enum):
    """Available embedding models"""    SENTENCE_TRANSFORMERS = "sentence-transformers/all-MiniLM-L6-v2"
    MPNET = "sentence-transformers/all-mpnet-base-v2"
    DISTILBERT = "sentence-transformers/all-distilroberta-v1"
    BERT_BASE = "bert-base-uncased"
    ROBERTA_BASE = "roberta-base"
    CUSTOM = "custom"

class SimilarityMetric(Enum):
    """Similarity metrics for embeddings"""    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"
    MANHATTAN = "manhattan"
    MINKOWSKI = "minkowski"

class DimensionalityReduction(Enum):
    """Dimensionality reduction techniques"""    PCA = "pca"
    TSNE = "tsne"
    UMAP = "umap"
    NONE = "none"

@dataclass
class TextEmbedding:
    """Text embedding with metadata"""    text_id: str
    text: str
    embedding: np.ndarray
    model_name: str
    embedding_dim: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class SimilarityResult:
    """Result of similarity search"""    query_id: str
    similar_items: List[Tuple[str, float]] = field(default_factory=list)  # (text_id, similarity_score)
    search_time: float = 0.0
    total_comparisons: int = 0
    similarity_metric: str = "cosine"

@dataclass
class ClusterResult:
    """Result of embedding clustering"""    clusters: List[List[str]] = field(default_factory=list)  # Lists of text_ids
    cluster_centers: List[np.ndarray] = field(default_factory=list)
    cluster_labels: List[int] = field(default_factory=list)
    inertia: float = 0.0
    silhouette_score: float = 0.0
    num_clusters: int = 0

@dataclass
class EmbeddingSpaceAnalysis:
    """Analysis of embedding space"""    total_embeddings: int
    embedding_dimension: int
    average_similarity: float
    similarity_distribution: Dict[str, float] = field(default_factory=dict)
    outliers: List[str] = field(default_factory=list)
    clusters_detected: int = 0
    space_coverage: float = 0.0
    density_metrics: Dict[str, float] = field(default_factory=dict)

class EmbeddingsEngine:
    """    Advanced text embeddings engine for generating, managing, and performing
    operations on high-quality semantic embeddings.
    """    
    def __init__(self, config: Optional[NLPAgentConfig] = None):
        """Initialize Embeddings Engine"""        self.config = config or default_config
        self.models = {}
        self.tokenizers = {}
        self.pipelines = {}
        self.embeddings_cache = {}
        self.faiss_index = None
        self.embedding_store = {}
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize embedding models"""        try:
            if TRANSFORMERS_AVAILABLE:
                # Initialize sentence transformers pipeline
                try:
                    self.pipelines["sentence_transformers"] = pipeline(
                        "feature-extraction",
                        model=EmbeddingModel.SENTENCE_TRANSFORMERS.value,
                        device=self._get_device()
                    )
                    logger.info("Sentence transformers initialized")
                except Exception as e:
                    logger.warning(f"Failed to load sentence transformers: {e}")
                
                # Initialize BERT model
                try:
                    model_name = EmbeddingModel.BERT_BASE.value
                    self.tokenizers["bert"] = AutoTokenizer.from_pretrained(model_name)
                    self.models["bert"] = AutoModel.from_pretrained(model_name)
                    
                    if self._get_device() >= 0 and torch.cuda.is_available():
                        self.models["bert"].to(f"cuda:{self._get_device()}")
                    
                    logger.info("BERT model initialized")
                except Exception as e:
                    logger.warning(f"Failed to load BERT model: {e}")
            
            # Initialize FAISS index if available
            if FAISS_AVAILABLE:
                self._initialize_faiss()
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding models: {e}")
            self._setup_fallback_methods()
    
    def _setup_fallback_methods(self):
        """Setup fallback methods for embeddings"""        logger.info("Setting up embedding fallback methods")
        self.fallback_mode = True
    
    def _get_device(self) -> int:
        """Get optimal device for model execution"""        if self.config.performance.enable_gpu and TRANSFORMERS_AVAILABLE:
            try:
                if torch.cuda.is_available():
                    return 0  # Use first GPU
            except:
                pass
        return -1  # Use CPU
    
    def _initialize_faiss(self):
        """Initialize FAISS index for fast similarity search"""        if FAISS_AVAILABLE:
            # Will be initialized when first embeddings are added
            self.faiss_index = None
            logger.info("FAISS indexing will be initialized on demand")
    
    async def generate_embeddings(
        self,
        texts: Union[str, List[str]],
        model: EmbeddingModel = EmbeddingModel.SENTENCE_TRANSFORMERS,
        text_ids: Optional[Union[str, List[str]]] = None,
        batch_size: int = 32
    ) -> Union[TextEmbedding, List[TextEmbedding]]:
        """        Generate embeddings for text(s)
        
        Args:
            texts: Text or list of texts to embed
            model: Embedding model to use
            text_ids: Optional IDs for the texts
            batch_size: Batch size for processing
        
        Returns:
            TextEmbedding or list of TextEmbeddings
        """        # Handle single text input
        is_single = isinstance(texts, str)
        if is_single:
            texts = [texts]
            if text_ids:
                text_ids = [text_ids]
        
        # Generate text IDs if not provided
        if not text_ids:
            text_ids = [f"text_{i}_{hash(text) % 10000}" for i, text in enumerate(texts)]
        
        if len(text_ids) != len(texts):
            raise ValueError("Number of text_ids must match number of texts")
        
        embeddings = []
        
        try:
            # Process in batches
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_ids = text_ids[i:i + batch_size]
                
                batch_embeddings = await self._generate_batch_embeddings(
                    batch_texts, model, batch_ids
                )
                embeddings.extend(batch_embeddings)
            
            # Store embeddings in cache and store
            for embedding in embeddings:
                self.embeddings_cache[embedding.text_id] = embedding
                self.embedding_store[embedding.text_id] = embedding
            
            # Update FAISS index if available
            if FAISS_AVAILABLE and embeddings:
                await self._update_faiss_index(embeddings)
            
            return embeddings[0] if is_single else embeddings
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise
    
    async def _generate_batch_embeddings(
        self,
        texts: List[str],
        model: EmbeddingModel,
        text_ids: List[str]
    ) -> List[TextEmbedding]:
        """Generate embeddings for a batch of texts"""        embeddings = []
        
        try:
            if model == EmbeddingModel.SENTENCE_TRANSFORMERS and "sentence_transformers" in self.pipelines:
                # Use sentence transformers pipeline
                raw_embeddings = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.pipelines["sentence_transformers"](texts)
                )
                
                for i, (text, text_id, raw_embedding) in enumerate(zip(texts, text_ids, raw_embeddings)):
                    # Average pooling for sentence embeddings
                    embedding_vector = np.mean(raw_embedding, axis=0)
                    
                    text_embedding = TextEmbedding(
                        text_id=text_id,
                        text=text,
                        embedding=embedding_vector,
                        model_name=model.value,
                        embedding_dim=len(embedding_vector),
                        metadata={
                            "batch_index": i,
                            "processing_method": "sentence_transformers"
                        }
                    )
                    
                    embeddings.append(text_embedding)
            
            elif model == EmbeddingModel.BERT_BASE and "bert" in self.models:
                # Use BERT model
                embeddings = await self._generate_bert_embeddings(texts, text_ids)
            
            else:
                # Fallback method
                embeddings = await self._generate_fallback_embeddings(texts, text_ids)
            
        except Exception as e:
            logger.error(f"Batch embedding generation failed: {e}")
            # Try fallback
            embeddings = await self._generate_fallback_embeddings(texts, text_ids)
        
        return embeddings
    
    async def _generate_bert_embeddings(
        self,
        texts: List[str],
        text_ids: List[str]
    ) -> List[TextEmbedding]:
        """Generate embeddings using BERT model"""        embeddings = []
        
        try:
            tokenizer = self.tokenizers["bert"]
            model = self.models["bert"]
            
            for text, text_id in zip(texts, text_ids):
                # Tokenize
                inputs = tokenizer(
                    text,
                    return_tensors="pt",
                    truncation=True,
                    padding=True,
                    max_length=512
                )
                
                # Move to GPU if available
                if self._get_device() >= 0 and torch.cuda.is_available():
                    inputs = {k: v.to(f"cuda:{self._get_device()}") for k, v in inputs.items()}
                
                # Generate embeddings
                with torch.no_grad():
                    outputs = model(**inputs)
                    # Use [CLS] token embedding or mean pooling
                    last_hidden_states = outputs.last_hidden_state
                    # Mean pooling
                    embedding_vector = torch.mean(last_hidden_states, dim=1).squeeze().cpu().numpy()
                
                text_embedding = TextEmbedding(
                    text_id=text_id,
                    text=text,
                    embedding=embedding_vector,
                    model_name="bert-base-uncased",
                    embedding_dim=len(embedding_vector),
                    metadata={
                        "processing_method": "bert",
                        "sequence_length": inputs["input_ids"].shape[1]
                    }
                )
                
                embeddings.append(text_embedding)
        
        except Exception as e:
            logger.error(f"BERT embedding generation failed: {e}")
            raise
        
        return embeddings
    
    async def _generate_fallback_embeddings(
        self,
        texts: List[str],
        text_ids: List[str]
    ) -> List[TextEmbedding]:
        """Generate fallback embeddings using simple methods"""        embeddings = []
        
        try:
            # Simple TF-IDF based embeddings
            if SKLEARN_AVAILABLE:
                from sklearn.feature_extraction.text import TfidfVectorizer
                
                vectorizer = TfidfVectorizer(
                    max_features=384,  # Standard embedding size
                    stop_words='english'
                )
                
                tfidf_matrix = vectorizer.fit_transform(texts)
                
                for i, (text, text_id) in enumerate(zip(texts, text_ids)):
                    embedding_vector = tfidf_matrix[i].toarray().flatten()
                    
                    text_embedding = TextEmbedding(
                        text_id=text_id,
                        text=text,
                        embedding=embedding_vector,
                        model_name="tfidf_fallback",
                        embedding_dim=len(embedding_vector),
                        metadata={
                            "processing_method": "tfidf_fallback",
                            "vocab_size": len(vectorizer.vocabulary_)
                        }
                    )
                    
                    embeddings.append(text_embedding)
            
            else:
                # Most basic fallback - character frequency vectors
                for text, text_id in zip(texts, text_ids):
                    # Create simple character frequency vector
                    char_freq = np.zeros(256)  # ASCII characters
                    for char in text.lower():
                        if ord(char) < 256:
                            char_freq[ord(char)] += 1
                    
                    # Normalize
                    char_freq = char_freq / (len(text) + 1)
                    
                    text_embedding = TextEmbedding(
                        text_id=text_id,
                        text=text,
                        embedding=char_freq,
                        model_name="char_freq_fallback",
                        embedding_dim=len(char_freq),
                        metadata={
                            "processing_method": "char_frequency",
                            "text_length": len(text)
                        }
                    )
                    
                    embeddings.append(text_embedding)
        
        except Exception as e:
            logger.error(f"Fallback embedding generation failed: {e}")
            raise
        
        return embeddings
    
    async def _update_faiss_index(self, new_embeddings: List[TextEmbedding]):
        """Update FAISS index with new embeddings"""        if not FAISS_AVAILABLE:
            return
        
        try:
            if not new_embeddings:
                return
            
            # Get embedding dimension
            embedding_dim = new_embeddings[0].embedding_dim
            
            # Initialize index if needed
            if self.faiss_index is None:
                self.faiss_index = faiss.IndexFlatIP(embedding_dim)  # Inner Product (cosine similarity)
                logger.info(f"Initialized FAISS index with dimension {embedding_dim}")
            
            # Add embeddings to index
            embedding_matrix = np.array([emb.embedding for emb in new_embeddings]).astype(np.float32)
            
            # Normalize for cosine similarity
            faiss.normalize_L2(embedding_matrix)
            
            self.faiss_index.add(embedding_matrix)
            
            logger.info(f"Added {len(new_embeddings)} embeddings to FAISS index")
            
        except Exception as e:
            logger.error(f"FAISS index update failed: {e}")
    
    async def find_similar(
        self,
        query: Union[str, TextEmbedding],
        top_k: int = 10,
        similarity_metric: SimilarityMetric = SimilarityMetric.COSINE,
        min_similarity: float = 0.0
    ) -> SimilarityResult:
        """        Find most similar texts to query
        
        Args:
            query: Query text or embedding
            top_k: Number of similar items to return
            similarity_metric: Similarity metric to use
            min_similarity: Minimum similarity threshold
        
        Returns:
            SimilarityResult with similar items
        """        start_time = asyncio.get_event_loop().time()
        
        # Generate query embedding if needed
        if isinstance(query, str):
            query_embedding = await self.generate_embeddings(query)
            query_id = query_embedding.text_id
            query_vector = query_embedding.embedding
        else:
            query_embedding = query
            query_id = query.text_id
            query_vector = query.embedding
        
        result = SimilarityResult(
            query_id=query_id,
            similarity_metric=similarity_metric.value
        )
        
        try:
            # Use FAISS for fast similarity search if available
            if FAISS_AVAILABLE and self.faiss_index is not None:
                similar_items = await self._faiss_similarity_search(
                    query_vector, top_k, min_similarity
                )
            else:
                # Use brute force similarity search
                similar_items = await self._brute_force_similarity_search(
                    query_vector, top_k, similarity_metric, min_similarity
                )
            
            result.similar_items = similar_items
            result.total_comparisons = len(self.embedding_store)
            result.search_time = asyncio.get_event_loop().time() - start_time
            
            return result
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            result.search_time = asyncio.get_event_loop().time() - start_time
            return result
    
    async def _faiss_similarity_search(
        self,
        query_vector: np.ndarray,
        top_k: int,
        min_similarity: float
    ) -> List[Tuple[str, float]]:
        """Perform similarity search using FAISS"""        if self.faiss_index is None or self.faiss_index.ntotal == 0:
            return []
        
        try:
            # Normalize query vector
            query_normalized = query_vector.astype(np.float32).reshape(1, -1)
            faiss.normalize_L2(query_normalized)
            
            # Search
            k = min(top_k, self.faiss_index.ntotal)
            similarities, indices = self.faiss_index.search(query_normalized, k)
            
            # Convert to results
            similar_items = []
            text_ids = list(self.embedding_store.keys())
            
            for idx, similarity in zip(indices[0], similarities[0]):
                if idx < len(text_ids) and similarity >= min_similarity:
                    text_id = text_ids[idx]
                    similar_items.append((text_id, float(similarity)))
            
            return similar_items
            
        except Exception as e:
            logger.error(f"FAISS similarity search failed: {e}")
            return []
    
    async def _brute_force_similarity_search(
        self,
        query_vector: np.ndarray,
        top_k: int,
        similarity_metric: SimilarityMetric,
        min_similarity: float
    ) -> List[Tuple[str, float]]:
        """Perform brute force similarity search"""        similarities = []
        
        try:
            for text_id, embedding in self.embedding_store.items():
                similarity = self._calculate_similarity(
                    query_vector,
                    embedding.embedding,
                    similarity_metric
                )
                
                if similarity >= min_similarity:
                    similarities.append((text_id, similarity))
            
            # Sort by similarity and return top k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Brute force similarity search failed: {e}")
            return []
    
    def _calculate_similarity(
        self,
        vector1: np.ndarray,
        vector2: np.ndarray,
        metric: SimilarityMetric
    ) -> float:
        """Calculate similarity between two vectors"""        try:
            if metric == SimilarityMetric.COSINE:
                # Cosine similarity
                dot_product = np.dot(vector1, vector2)
                norm_product = np.linalg.norm(vector1) * np.linalg.norm(vector2)
                return dot_product / norm_product if norm_product > 0 else 0.0
            
            elif metric == SimilarityMetric.EUCLIDEAN:
                # Convert Euclidean distance to similarity
                distance = np.linalg.norm(vector1 - vector2)
                max_distance = np.linalg.norm(vector1) + np.linalg.norm(vector2)
                return 1.0 - (distance / max_distance) if max_distance > 0 else 0.0
            
            elif metric == SimilarityMetric.DOT_PRODUCT:
                return np.dot(vector1, vector2)
            
            elif metric == SimilarityMetric.MANHATTAN:
                # Convert Manhattan distance to similarity
                distance = np.sum(np.abs(vector1 - vector2))
                max_distance = np.sum(np.abs(vector1)) + np.sum(np.abs(vector2))
                return 1.0 - (distance / max_distance) if max_distance > 0 else 0.0
            
            else:
                # Default to cosine
                return self._calculate_similarity(vector1, vector2, SimilarityMetric.COSINE)
        
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0
    
    async def cluster_embeddings(
        self,
        embedding_ids: Optional[List[str]] = None,
        n_clusters: int = 5,
        algorithm: str = "kmeans"
    ) -> ClusterResult:
        """        Cluster embeddings using specified algorithm
        
        Args:
            embedding_ids: Specific embeddings to cluster (None for all)
            n_clusters: Number of clusters
            algorithm: Clustering algorithm
        
        Returns:
            ClusterResult with cluster assignments
        """        if not SKLEARN_AVAILABLE:
            logger.error("Clustering requires scikit-learn")
            return ClusterResult()
        
        # Select embeddings to cluster
        if embedding_ids:
            embeddings_to_cluster = [
                self.embedding_store[eid] for eid in embedding_ids
                if eid in self.embedding_store
            ]
        else:
            embeddings_to_cluster = list(self.embedding_store.values())
        
        if len(embeddings_to_cluster) < n_clusters:
            logger.warning(f"Not enough embeddings ({len(embeddings_to_cluster)}) for {n_clusters} clusters")
            return ClusterResult()
        
        result = ClusterResult(num_clusters=n_clusters)
        
        try:
            # Create embedding matrix
            embedding_matrix = np.array([emb.embedding for emb in embeddings_to_cluster])
            
            # Perform clustering
            if algorithm.lower() == "kmeans":
                clusterer = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                cluster_labels = clusterer.fit_predict(embedding_matrix)
                
                result.cluster_centers = clusterer.cluster_centers_.tolist()
                result.inertia = clusterer.inertia_
            
            result.cluster_labels = cluster_labels.tolist()
            
            # Organize clusters
            clusters = [[] for _ in range(n_clusters)]
            for i, label in enumerate(cluster_labels):
                clusters[label].append(embeddings_to_cluster[i].text_id)
            
            result.clusters = clusters
            
            # Calculate silhouette score
            try:
                from sklearn.metrics import silhouette_score
                result.silhouette_score = silhouette_score(embedding_matrix, cluster_labels)
            except:
                pass
            
            return result
            
        except Exception as e:
            logger.error(f"Clustering failed: {e}")
            return result
    
    async def reduce_dimensionality(
        self,
        embedding_ids: Optional[List[str]] = None,
        method: DimensionalityReduction = DimensionalityReduction.PCA,
        n_components: int = 2
    ) -> Dict[str, np.ndarray]:
        """        Reduce dimensionality of embeddings for visualization
        
        Args:
            embedding_ids: Specific embeddings to reduce (None for all)
            method: Dimensionality reduction method
            n_components: Number of output components
        
        Returns:
            Dictionary mapping text_ids to reduced embeddings
        """        if not SKLEARN_AVAILABLE:
            logger.error("Dimensionality reduction requires scikit-learn")
            return {}
        
        # Select embeddings
        if embedding_ids:
            embeddings_to_reduce = [
                (eid, self.embedding_store[eid]) for eid in embedding_ids
                if eid in self.embedding_store
            ]
        else:
            embeddings_to_reduce = list(self.embedding_store.items())
        
        if not embeddings_to_reduce:
            return {}
        
        try:
            # Create embedding matrix
            text_ids, embeddings = zip(*embeddings_to_reduce)
            embedding_matrix = np.array([emb.embedding for emb in embeddings])
            
            # Apply dimensionality reduction
            if method == DimensionalityReduction.PCA:
                reducer = PCA(n_components=n_components, random_state=42)
            elif method == DimensionalityReduction.TSNE:
                reducer = TSNE(n_components=n_components, random_state=42)
            else:
                # Default to PCA
                reducer = PCA(n_components=n_components, random_state=42)
            
            reduced_embeddings = reducer.fit_transform(embedding_matrix)
            
            # Return as dictionary
            result = {}
            for text_id, reduced_embedding in zip(text_ids, reduced_embeddings):
                result[text_id] = reduced_embedding
            
            return result
            
        except Exception as e:
            logger.error(f"Dimensionality reduction failed: {e}")
            return {}
    
    async def analyze_embedding_space(self) -> EmbeddingSpaceAnalysis:
        """Analyze the current embedding space"""        if not self.embedding_store:
            return EmbeddingSpaceAnalysis(
                total_embeddings=0,
                embedding_dimension=0,
                average_similarity=0.0
            )
        
        embeddings = list(self.embedding_store.values())
        
        analysis = EmbeddingSpaceAnalysis(
            total_embeddings=len(embeddings),
            embedding_dimension=embeddings[0].embedding_dim if embeddings else 0,
            average_similarity=0.0
        )
        
        try:
            if len(embeddings) > 1:
                # Calculate pairwise similarities
                similarities = []
                embedding_matrix = np.array([emb.embedding for emb in embeddings])
                
                if SKLEARN_AVAILABLE:
                    similarity_matrix = cosine_similarity(embedding_matrix)
                    # Get upper triangle (excluding diagonal)
                    similarities = similarity_matrix[np.triu_indices_from(similarity_matrix, k=1)]
                else:
                    # Manual calculation for small sets
                    for i in range(len(embeddings)):
                        for j in range(i + 1, len(embeddings)):
                            sim = self._calculate_similarity(
                                embeddings[i].embedding,
                                embeddings[j].embedding,
                                SimilarityMetric.COSINE
                            )
                            similarities.append(sim)
                
                # Calculate statistics
                analysis.average_similarity = np.mean(similarities)
                analysis.similarity_distribution = {
                    "min": float(np.min(similarities)),
                    "max": float(np.max(similarities)),
                    "std": float(np.std(similarities)),
                    "median": float(np.median(similarities))
                }
                
                # Detect outliers (embeddings with very low average similarity)
                if SKLEARN_AVAILABLE and len(embeddings) > 5:
                    avg_similarities = np.mean(cosine_similarity(embedding_matrix), axis=1)
                    threshold = np.mean(avg_similarities) - 2 * np.std(avg_similarities)
                    outlier_indices = np.where(avg_similarities < threshold)[0]
                    analysis.outliers = [embeddings[i].text_id for i in outlier_indices]
                
                # Estimate space coverage and density
                analysis.space_coverage = self._calculate_space_coverage(embedding_matrix)
                analysis.density_metrics = self._calculate_density_metrics(embedding_matrix)
        
        except Exception as e:
            logger.error(f"Embedding space analysis failed: {e}")
        
        return analysis
    
    def _calculate_space_coverage(self, embedding_matrix: np.ndarray) -> float:
        """Calculate how well the embeddings cover the vector space"""        try:
            if len(embedding_matrix) < 2:
                return 0.0
            
            # Use PCA to estimate effective dimensionality
            if SKLEARN_AVAILABLE:
                pca = PCA()
                pca.fit(embedding_matrix)
                
                # Calculate cumulative explained variance
                cumvar = np.cumsum(pca.explained_variance_ratio_)
                
                # Find effective dimensionality (95% of variance)
                effective_dim = np.argmax(cumvar >= 0.95) + 1
                total_dim = len(pca.explained_variance_ratio_)
                
                return effective_dim / total_dim
            
            return 0.5  # Default estimate
        
        except Exception as e:
            logger.error(f"Space coverage calculation failed: {e}")
            return 0.0
    
    def _calculate_density_metrics(self, embedding_matrix: np.ndarray) -> Dict[str, float]:
        """Calculate density metrics for the embedding space"""        metrics = {}
        
        try:
            if SKLEARN_AVAILABLE and len(embedding_matrix) > 1:
                # Average distance to nearest neighbor
                nbrs = NearestNeighbors(n_neighbors=2, metric='cosine').fit(embedding_matrix)
                distances, indices = nbrs.kneighbors(embedding_matrix)
                
                # First column is self (distance 0), second is nearest neighbor
                nearest_distances = distances[:, 1]
                
                metrics["avg_nearest_distance"] = float(np.mean(nearest_distances))
                metrics["std_nearest_distance"] = float(np.std(nearest_distances))
                metrics["min_nearest_distance"] = float(np.min(nearest_distances))
                metrics["max_nearest_distance"] = float(np.max(nearest_distances))
        
        except Exception as e:
            logger.error(f"Density metrics calculation failed: {e}")
        
        return metrics
    
    def save_embeddings(self, filepath: str) -> bool:
        """Save embeddings to file"""        try:
            # Convert to serializable format
            data = {
                "embeddings": [],
                "metadata": {
                    "total_count": len(self.embedding_store),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            for text_id, embedding in self.embedding_store.items():
                emb_data = {
                    "text_id": embedding.text_id,
                    "text": embedding.text,
                    "embedding": embedding.embedding.tolist(),
                    "model_name": embedding.model_name,
                    "embedding_dim": embedding.embedding_dim,
                    "metadata": embedding.metadata,
                    "timestamp": embedding.timestamp
                }
                data["embeddings"].append(emb_data)
            
            # Save as pickle for efficiency
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
            
            logger.info(f"Saved {len(self.embedding_store)} embeddings to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save embeddings: {e}")
            return False
    
    def load_embeddings(self, filepath: str) -> bool:
        """Load embeddings from file"""        try:
            if not os.path.exists(filepath):
                logger.error(f"File not found: {filepath}")
                return False
            
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            # Restore embeddings
            loaded_embeddings = []
            for emb_data in data["embeddings"]:
                embedding = TextEmbedding(
                    text_id=emb_data["text_id"],
                    text=emb_data["text"],
                    embedding=np.array(emb_data["embedding"]),
                    model_name=emb_data["model_name"],
                    embedding_dim=emb_data["embedding_dim"],
                    metadata=emb_data["metadata"],
                    timestamp=emb_data["timestamp"]
                )
                
                self.embedding_store[embedding.text_id] = embedding
                self.embeddings_cache[embedding.text_id] = embedding
                loaded_embeddings.append(embedding)
            
            # Update FAISS index
            if FAISS_AVAILABLE and loaded_embeddings:
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: asyncio.run(self._update_faiss_index(loaded_embeddings))
                )
            
            logger.info(f"Loaded {len(loaded_embeddings)} embeddings from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load embeddings: {e}")
            return False
    
    def get_embedding(self, text_id: str) -> Optional[TextEmbedding]:
        """Get specific embedding by ID"""        return self.embedding_store.get(text_id)
    
    def remove_embedding(self, text_id: str) -> bool:
        """Remove embedding by ID"""        if text_id in self.embedding_store:
            del self.embedding_store[text_id]
            if text_id in self.embeddings_cache:
                del self.embeddings_cache[text_id]
            
            # Note: FAISS index would need to be rebuilt for removals
            # This is a limitation of the current FAISS implementation
            
            return True
        
        return False
    
    def clear_cache(self):
        """Clear embedding caches"""        self.embeddings_cache.clear()
        logger.info("Embedding cache cleared")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""        status = {
            "status": "healthy",
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "sklearn_available": SKLEARN_AVAILABLE,
            "faiss_available": FAISS_AVAILABLE,
            "models_loaded": len(self.models),
            "pipelines_loaded": len(self.pipelines),
            "embeddings_stored": len(self.embedding_store),
            "cache_size": len(self.embeddings_cache),
            "faiss_index_size": self.faiss_index.ntotal if self.faiss_index else 0
        }
        
        # Test basic functionality
        try:
            test_result = asyncio.run(
                self.generate_embeddings("This is a test text for embedding.")
            )
            status["test_result"] = "passed"
            status["test_embedding_dim"] = test_result.embedding_dim
        except Exception as e:
            status["status"] = "degraded"
            status["error"] = str(e)
        
        return status
    
    def shutdown(self):
        """Shutdown the embeddings engine"""        logger.info("Shutting down Embeddings Engine")
        
        # Clear caches and stores
        self.clear_cache()
        self.embedding_store.clear()
        
        # Clear models
        self.models.clear()
        self.tokenizers.clear()
        self.pipelines.clear()
        
        # Clear FAISS index
        if self.faiss_index:
            self.faiss_index.reset()
            self.faiss_index = None
        
        # Clear GPU memory if using CUDA
        if TRANSFORMERS_AVAILABLE and torch.cuda.is_available():
            torch.cuda.empty_cache()

# Utility functions
def calculate_centroid(embeddings: List[np.ndarray]) -> np.ndarray:
    """Calculate centroid of embeddings"""    if not embeddings:
        return np.array([])
    
    return np.mean(embeddings, axis=0)

def normalize_embedding(embedding: np.ndarray) -> np.ndarray:
    """Normalize embedding to unit vector"""    norm = np.linalg.norm(embedding)
    return embedding / norm if norm > 0 else embedding

def batch_cosine_similarity(matrix1: np.ndarray, matrix2: np.ndarray) -> np.ndarray:
    """Calculate cosine similarity between two embedding matrices"""    if SKLEARN_AVAILABLE:
        return cosine_similarity(matrix1, matrix2)
    
    # Manual implementation
    matrix1_norm = matrix1 / np.linalg.norm(matrix1, axis=1, keepdims=True)
    matrix2_norm = matrix2 / np.linalg.norm(matrix2, axis=1, keepdims=True)
    
    return np.dot(matrix1_norm, matrix2_norm.T)
