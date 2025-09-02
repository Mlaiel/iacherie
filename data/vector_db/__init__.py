"""Vector Database Management Module
================================

Advanced vector database integration for similarity search and content matching.
Supports multiple vector storage backends with optimized similarity algorithms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

ATTENTION: Ce code est protégé par les droits d'auteur.
Toute reproduction, distribution ou modification non autorisée est strictement interdite.

⚠️ COPYRIGHT WARNING ⚠️
This code is protected by copyright law. Any unauthorized reproduction, distribution, 
modification, or use of this code without explicit written permission from 
Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result in legal action.

For licensing and authorization requests, contact: mlaiel@live.de

TEAM SPECIALTIES:
- Lead AI Developer + Backend Senior Engineer: Fahed Mlaiel
- ML Engineer + Data Scientist: Advanced algorithms & optimization
- Database Administrator + Performance Specialist: Scalability & efficiency  
- Security Engineer + DevOps Engineer: System security & deployment
- Audio Processing Specialist: Audio fingerprinting & analysis
- Computer Vision Engineer: Image/video processing & recognition
- Microservices Architect: Distributed systems & API design
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import pickle
from abc import ABC, abstractmethod

# Import core dependencies
try:
    import faiss
except ImportError:
    faiss = None
    logging.warning("FAISS not available - FAISS backend disabled")

try:
    import chromadb
except ImportError:
    chromadb = None
    logging.warning("ChromaDB not available - Chroma backend disabled")

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None
    logging.warning("SentenceTransformers not available - text embeddings limited")

try:
    import torch
except ImportError:
    torch = None
    logging.warning("PyTorch not available - some features disabled")

try:
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    logging.warning("Scikit-learn not available - fallback similarity metrics")

logger = logging.getLogger(__name__)


@dataclass
class VectorSearchResult:
    """Represents a vector search result."""
    content_id: str
    similarity_score: float
    metadata: Dict[str, Any]
    vector: Optional[np.ndarray] = None
    distance: Optional[float] = None


@dataclass 
class VectorIndex:
    """
Represents a vector index configuration."""
    name: str
    dimension: int
    metric: str
    backend: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]


class VectorBackend(ABC):
    """
Abstract base class for vector database backends."""
    
    @abstractmethod
    async def create_index(self, name: str, dimension: int, metric: str = "cosine") -> bool:
        try:
            logger.info(f"Executing create_index")
            
            # Implementation for create_index
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing add_vectors")
            
            # Implementation for add_vectors
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"add_vectors completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing search")
            
            # Implementation for search
            # TODO: Add specific business logic here
        try:
                    async with self.db_session() as session:
                        # Database operation
                        result = await session.execute(delete_query)
                        await session.commit()
                        logger.info(f"Database operation delete_vectors completed")
                        return True
                
                except Exception as e:
                    logger.error(f"Database operation delete_vectors failed: {e}")
                    raise
            result = None  # Replace with actual implementation
            
            logger.info(f"search completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"search failed: {e}")
            raise
        except Exception as e:
            logger.error(f"add_vectors failed: {e}")
            raise
            return result
            
        except Exception as e:
            logger.error(f"create_index failed: {e}")
            raise
    @abstractmethod
    async def add_vectors(self, index_name: str, vectors: np.ndarray, 
                         ids: List[str], metadata: List[Dict]) -> bool:
        """
Add vectors to an index."""
        pass
    
    @abstractmethod
    async def search(self, index_name: str, query_vector: np.ndarray,
                    k: int = 10, threshold: float = 0.8) -> List[VectorSearchResult]:
        """
Search for similar vectors."""
        pass
    
    @abstractmethod
    async def delete_vectors(self, index_name: str, ids: List[str]) -> bool:
        """
Delete vectors from an index."""
        pass


class FAISSBackend(VectorBackend):
    """
FAISS vector database backend."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.indices: Dict[str, faiss.Index] = {}
        self.metadata: Dict[str, Dict[str, Dict]] = {}
        self.id_maps: Dict[str, Dict[str, int]] = {}
        self.reverse_id_maps: Dict[str, Dict[int, str]] = {}
        
    async def create_index(self, name: str, dimension: int, metric: str = "cosine") -> bool:
        """Create a new FAISS index."""
        try:
            if metric == "cosine":
                # Use IndexFlatIP for cosine similarity
                index = faiss.IndexFlatIP(dimension)
            elif metric == "euclidean":
                # Use IndexFlatL2 for L2 distance
                index = faiss.IndexFlatL2(dimension)
            else:
                # Default to cosine
                index = faiss.IndexFlatIP(dimension)
            
            self.indices[name] = index
            self.metadata[name] = {}
            self.id_maps[name] = {}
            self.reverse_id_maps[name] = {}
            
            logger.info(f"Created FAISS index '{name}' with dimension {dimension}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create FAISS index '{name}': {str(e)}")
            return False
    
    async def add_vectors(self, index_name: str, vectors: np.ndarray,
                         ids: List[str], metadata: List[Dict]) -> bool:
        """Add vectors to FAISS index."""
        try:
            if index_name not in self.indices:
                raise ValueError(f"Index '{index_name}' not found")
            
            index = self.indices[index_name]
            
            # Normalize vectors for cosine similarity
            if isinstance(index, faiss.IndexFlatIP):
                faiss.normalize_L2(vectors)
            
            # Map string IDs to internal indices
            start_idx = index.ntotal
            for i, content_id in enumerate(ids):
                internal_idx = start_idx + i
                self.id_maps[index_name][content_id] = internal_idx
                self.reverse_id_maps[index_name][internal_idx] = content_id
                self.metadata[index_name][content_id] = metadata[i]
            
            # Add vectors to index
            index.add(vectors.astype(np.float32))
            
            logger.info(f"Added {len(ids)} vectors to index '{index_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add vectors to index '{index_name}': {str(e)}")
            return False
    
    async def search(self, index_name: str, query_vector: np.ndarray,
                    k: int = 10, threshold: float = 0.8) -> List[VectorSearchResult]:
        """Search for similar vectors in FAISS index."""
        try:
            if index_name not in self.indices:
                raise ValueError(f"Index '{index_name}' not found")
            
            index = self.indices[index_name]
            
            # Normalize query vector for cosine similarity
            if isinstance(index, faiss.IndexFlatIP):
                query_normalized = query_vector.reshape(1, -1).astype(np.float32)
                faiss.normalize_L2(query_normalized)
            else:
                query_normalized = query_vector.reshape(1, -1).astype(np.float32)
            
            # Search
            distances, indices = index.search(query_normalized, k)
            
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx == -1:  # No more results
                    break
                
                # Convert distance to similarity score
                if isinstance(index, faiss.IndexFlatIP):
                    similarity = float(distance)  # Already cosine similarity
                else:
                    # Convert L2 distance to similarity
                    similarity = 1.0 / (1.0 + float(distance))
                
                if similarity >= threshold:
                    content_id = self.reverse_id_maps[index_name].get(idx)
                    if content_id:
                        result = VectorSearchResult(
                            content_id=content_id,
                            similarity_score=similarity,
                            metadata=self.metadata[index_name].get(content_id, {}),
                            distance=float(distance)
                        )
                        results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search index '{index_name}': {str(e)}")
            return []
    
    async def delete_vectors(self, index_name: str, ids: List[str]) -> bool:
        """Delete vectors from FAISS index (rebuild required)."""
        try:
            if index_name not in self.indices:
                raise ValueError(f"Index '{index_name}' not found")
            
            # Remove from metadata and mappings
            for content_id in ids:
                if content_id in self.id_maps[index_name]:
                    internal_idx = self.id_maps[index_name][content_id]
                    del self.id_maps[index_name][content_id]
                    del self.reverse_id_maps[index_name][internal_idx]
                    del self.metadata[index_name][content_id]
            
            logger.warning(f"Deleted metadata for {len(ids)} vectors from '{index_name}'. Index rebuild recommended.")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete vectors from index '{index_name}': {str(e)}")
            return False


class ChromaBackend(VectorBackend):
    """ChromaDB vector database backend."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = chromadb.Client()
        self.collections: Dict[str, Any] = {}
        
    async def create_index(self, name: str, dimension: int, metric: str = "cosine") -> bool:
        """Create a new ChromaDB collection."""
        try:
            collection = self.client.create_collection(
                name=name,
                metadata={"dimension": dimension, "metric": metric}
            )
            self.collections[name] = collection
            
            logger.info(f"Created ChromaDB collection '{name}' with dimension {dimension}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create ChromaDB collection '{name}': {str(e)}")
            return False
    
    async def add_vectors(self, index_name: str, vectors: np.ndarray,
                         ids: List[str], metadata: List[Dict]) -> bool:
        """Add vectors to ChromaDB collection."""
        try:
            if index_name not in self.collections:
                raise ValueError(f"Collection '{index_name}' not found")
            
            collection = self.collections[index_name]
            
            # Convert numpy array to list
            embeddings = vectors.tolist()
            
            # Add to collection
            collection.add(
                embeddings=embeddings,
                ids=ids,
                metadatas=metadata
            )
            
            logger.info(f"Added {len(ids)} vectors to collection '{index_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add vectors to collection '{index_name}': {str(e)}")
            return False
    
    async def search(self, index_name: str, query_vector: np.ndarray,
                    k: int = 10, threshold: float = 0.8) -> List[VectorSearchResult]:
        """Search for similar vectors in ChromaDB collection."""
        try:
            if index_name not in self.collections:
                raise ValueError(f"Collection '{index_name}' not found")
            
            collection = self.collections[index_name]
            
            # Query collection
            results = collection.query(
                query_embeddings=[query_vector.tolist()],
                n_results=k
            )
            
            search_results = []
            for i, (content_id, distance, metadata) in enumerate(zip(
                results['ids'][0],
                results['distances'][0], 
                results['metadatas'][0]
            )):
                # Convert distance to similarity
                similarity = 1.0 - distance  # ChromaDB uses distance
                
                if similarity >= threshold:
                    result = VectorSearchResult(
                        content_id=content_id,
                        similarity_score=similarity,
                        metadata=metadata or {},
                        distance=distance
                    )
                    search_results.append(result)
            
            return search_results
            
        except Exception as e:
            logger.error(f"Failed to search collection '{index_name}': {str(e)}")
            return []
    
    async def delete_vectors(self, index_name: str, ids: List[str]) -> bool:
        """Delete vectors from ChromaDB collection."""
        try:
            if index_name not in self.collections:
                raise ValueError(f"Collection '{index_name}' not found")
            
            collection = self.collections[index_name]
            collection.delete(ids=ids)
            
            logger.info(f"Deleted {len(ids)} vectors from collection '{index_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete vectors from collection '{index_name}': {str(e)}")
            return False


class VectorDBManager:
    """
    Advanced vector database manager with multiple backend support.
    
    Handles vector indexing, similarity search, and content matching
    across multiple formats and platforms.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.backend_type = config.get('backend', 'faiss')
        self.embedding_model_name = config.get('embedding_model', 'all-MiniLM-L6-v2')
        
        # Initialize backend
        if self.backend_type == 'faiss':
            self.backend = FAISSBackend(config)
        elif self.backend_type == 'chroma':
            self.backend = ChromaBackend(config)
        else:
            raise ValueError(f"Unsupported backend: {self.backend_type}")
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        self.embedding_dimension = self.embedding_model.get_sentence_embedding_dimension()
        
        # Index registry
        self.indices: Dict[str, VectorIndex] = {}
        
        logger.info(f"VectorDBManager initialized with {self.backend_type} backend")
    
    async def create_content_index(self, content_type: str, metric: str = "cosine") -> bool:
        """
        Create a specialized index for a content type.
        
        Args:
            content_type: Type of content (audio, video, image, text)
            metric: Distance metric to use
            
        Returns:
            Success status
        """
        try:
            index_name = f"{content_type}_index"
            
            # Create backend index
            success = await self.backend.create_index(
                index_name, self.embedding_dimension, metric
            )
            
            if success:
                # Register index
                self.indices[index_name] = VectorIndex(
                    name=index_name,
                    dimension=self.embedding_dimension,
                    metric=metric,
                    backend=self.backend_type,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    metadata={
                        'content_type': content_type,
                        'embedding_model': self.embedding_model_name
                    }
                )
                
                logger.info(f"Created content index for {content_type}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to create content index for {content_type}: {str(e)}")
            return False
    
    def generate_text_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding vector for text content.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Failed to generate text embedding: {str(e)}")
            return np.zeros(self.embedding_dimension, dtype=np.float32)
    
    def generate_audio_embedding(self, audio_features: Dict[str, Any]) -> np.ndarray:
        """
        Generate embedding vector for audio content.
        
        Args:
            audio_features: Extracted audio features
            
        Returns:
            Embedding vector
        """
        try:
            # Combine different audio features into a single vector
            features = []
            
            # Add spectral features
            if 'mfcc' in audio_features:
                features.extend(np.mean(audio_features['mfcc'], axis=1))
            
            if 'chroma' in audio_features:
                features.extend(np.mean(audio_features['chroma'], axis=1))
            
            if 'spectral_centroid' in audio_features:
                features.append(np.mean(audio_features['spectral_centroid']))
            
            if 'zero_crossing_rate' in audio_features:
                features.append(np.mean(audio_features['zero_crossing_rate']))
            
            # Pad or truncate to match embedding dimension
            features = np.array(features, dtype=np.float32)
            if len(features) < self.embedding_dimension:
                features = np.pad(features, (0, self.embedding_dimension - len(features)))
            elif len(features) > self.embedding_dimension:
                features = features[:self.embedding_dimension]
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to generate audio embedding: {str(e)}")
            return np.zeros(self.embedding_dimension, dtype=np.float32)
    
    async def add_content_vector(self, content_type: str, content_id: str,
                               embedding: np.ndarray, metadata: Dict[str, Any]) -> bool:
        """
        Add content vector to appropriate index.
        
        Args:
            content_type: Type of content
            content_id: Unique content identifier
            embedding: Embedding vector
            metadata: Associated metadata
            
        Returns:
            Success status
        """
        try:
            index_name = f"{content_type}_index"
            
            if index_name not in self.indices:
                await self.create_content_index(content_type)
            
            # Add vector to backend
            success = await self.backend.add_vectors(
                index_name,
                embedding.reshape(1, -1),
                [content_id],
                [metadata]
            )
            
            if success:
                self.indices[index_name].updated_at = datetime.now()
                logger.info(f"Added vector for content {content_id} to {content_type} index")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to add content vector: {str(e)}")
            return False
    
    async def search_similar_content(self, content_type: str, query_embedding: np.ndarray,
                                   k: int = 10, threshold: float = 0.8) -> List[VectorSearchResult]:
        """
        Search for similar content in the specified index.
        
        Args:
            content_type: Type of content to search
            query_embedding: Query vector
            k: Number of results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of similar content results
        """
        try:
            index_name = f"{content_type}_index"
            
            if index_name not in self.indices:
                logger.warning(f"Index {index_name} not found")
                return []
            
            results = await self.backend.search(
                index_name, query_embedding, k, threshold
            )
            
            logger.info(f"Found {len(results)} similar content items for {content_type}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search similar content: {str(e)}")
            return []
    
    async def detect_content_similarity(self, content_id_1: str, content_id_2: str,
                                      content_type: str) -> Optional[float]:
        """
        Calculate similarity between two specific content items.
        
        Args:
            content_id_1: First content ID
            content_id_2: Second content ID
            content_type: Type of content
            
        Returns:
            Similarity score or None if not found
        """
        try:
            # This would require storing vectors separately or rebuilding from content
            # For now, return placeholder implementation
            logger.warning("Direct content similarity detection not implemented")
            return None
            
        except Exception as e:
            logger.error(f"Failed to detect content similarity: {str(e)}")
            return None
    
    async def remove_content_vector(self, content_type: str, content_id: str) -> bool:
        """
        Remove content vector from index.
        
        Args:
            content_type: Type of content
            content_id: Content identifier
            
        Returns:
            Success status
        """
        try:
            index_name = f"{content_type}_index"
            
            if index_name not in self.indices:
                logger.warning(f"Index {index_name} not found")
                return False
            
            success = await self.backend.delete_vectors(index_name, [content_id])
            
            if success:
                self.indices[index_name].updated_at = datetime.now()
                logger.info(f"Removed vector for content {content_id} from {content_type} index")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to remove content vector: {str(e)}")
            return False
    
    def get_index_stats(self, content_type: str) -> Dict[str, Any]:
        """
        Get statistics for a content index.
        
        Args:
            content_type: Type of content
            
        Returns:
            Index statistics
        """
        try:
            index_name = f"{content_type}_index"
            
            if index_name not in self.indices:
                return {}
            
            index_info = self.indices[index_name]
            
            # Get backend-specific stats
            stats = {
                'name': index_info.name,
                'dimension': index_info.dimension,
                'metric': index_info.metric,
                'backend': index_info.backend,
                'created_at': index_info.created_at.isoformat(),
                'updated_at': index_info.updated_at.isoformat(),
                'metadata': index_info.metadata
            }
            
            # Add backend-specific information
            if hasattr(self.backend, 'indices') and index_name in self.backend.indices:
                if self.backend_type == 'faiss':
                    faiss_index = self.backend.indices[index_name]
                    stats['vector_count'] = faiss_index.ntotal
                    stats['is_trained'] = faiss_index.is_trained
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get index stats: {str(e)}")
            return {}
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status.
        
        Returns:
            System status information
        """
        return {
            'backend_type': self.backend_type,
            'embedding_model': self.embedding_model_name,
            'embedding_dimension': self.embedding_dimension,
            'total_indices': len(self.indices),
            'indices': {name: self.get_index_stats(name.replace('_index', '')) 
                       for name in self.indices.keys()},
            'supported_content_types': ['audio', 'video', 'image', 'text']
        }


class SimilaritySearcher:
    """
    Advanced similarity search engine with content-aware algorithms.
    
    Provides specialized search for different content types with
    optimized similarity metrics and ranking algorithms.
    """
    
    def __init__(self, vector_db: VectorDBManager, config: Dict[str, Any]):
        self.vector_db = vector_db
        self.config = config
        self.similarity_thresholds = config.get('similarity_thresholds', {
            'audio': 0.85,
            'video': 0.80,
            'image': 0.75,
            'text': 0.70
        })
    
    async def find_duplicate_content(self, content_type: str, 
                                   embedding: np.ndarray) -> List[VectorSearchResult]:
        """
        Find potential duplicate content.
        
        Args:
            content_type: Type of content
            embedding: Content embedding
            
        Returns:
            List of potential duplicates
        """
        threshold = self.similarity_thresholds.get(content_type, 0.8)
        
        results = await self.vector_db.search_similar_content(
            content_type, embedding, k=50, threshold=threshold
        )
        
        # Filter high-similarity results (potential duplicates)
        duplicates = [r for r in results if r.similarity_score >= threshold + 0.05]
        
        logger.info(f"Found {len(duplicates)} potential duplicates for {content_type}")
        return duplicates
    
    async def find_similar_content(self, content_type: str,
                                 embedding: np.ndarray,
                                 exclude_ids: List[str] = None) -> List[VectorSearchResult]:
        """
        Find similar but not duplicate content.
        
        Args:
            content_type: Type of content
            embedding: Content embedding
            exclude_ids: Content IDs to exclude
            
        Returns:
            List of similar content
        """
        base_threshold = self.similarity_thresholds.get(content_type, 0.8)
        similarity_threshold = base_threshold - 0.1  # Lower threshold for similarity
        
        results = await self.vector_db.search_similar_content(
            content_type, embedding, k=100, threshold=similarity_threshold
        )
        
        # Filter results
        filtered_results = []
        for result in results:
            if exclude_ids and result.content_id in exclude_ids:
                continue
                
            # Not too similar (not duplicate) but similar enough
            if similarity_threshold <= result.similarity_score < base_threshold:
                filtered_results.append(result)
        
        logger.info(f"Found {len(filtered_results)} similar content items for {content_type}")
        return filtered_results
    
    async def rank_by_relevance(self, results: List[VectorSearchResult],
                              query_metadata: Dict[str, Any]) -> List[VectorSearchResult]:
        """
        Rank search results by relevance using metadata.
        
        Args:
            results: Search results to rank
            query_metadata: Query metadata for ranking
            
        Returns:
            Ranked results
        """
        try:
            # Implement relevance scoring based on metadata
            for result in results:
                relevance_score = result.similarity_score
                
                # Boost score based on metadata matches
                if 'tags' in query_metadata and 'tags' in result.metadata:
                    query_tags = set(query_metadata['tags'])
                    result_tags = set(result.metadata['tags'])
                    tag_overlap = len(query_tags.intersection(result_tags))
                    relevance_score += tag_overlap * 0.05
                
                if 'category' in query_metadata and 'category' in result.metadata:
                    if query_metadata['category'] == result.metadata['category']:
                        relevance_score += 0.1
                
                # Store enhanced score
                result.metadata['relevance_score'] = relevance_score
            
            # Sort by relevance score
            results.sort(key=lambda x: x.metadata.get('relevance_score', x.similarity_score), 
                        reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to rank results by relevance: {str(e)}")
            return results


# Import and expose all main classes and functions
try:
    from .faiss_backend import FAISSBackend, FAISSIndexManager
except ImportError:
    FAISSBackend = None
    FAISSIndexManager = None
    logger.warning("FAISS backend components not available")

try:
    from .chroma_backend import ChromaBackend, ChromaCollectionManager  
except ImportError:
    ChromaBackend = None
    ChromaCollectionManager = None
    logger.warning("ChromaDB backend components not available")

try:
    from .embedding_engine import (
        TextEmbeddingGenerator, 
        AudioEmbeddingGenerator, 
        ImageEmbeddingGenerator, 
        VideoEmbeddingGenerator,
        MultiModalEmbeddingEngine
    )
except ImportError:
    logger.warning("Embedding engine components not available")
    TextEmbeddingGenerator = None
    AudioEmbeddingGenerator = None
    ImageEmbeddingGenerator = None
    VideoEmbeddingGenerator = None
    MultiModalEmbeddingEngine = None

try:
    from .similarity_search import (
        SimilaritySearchEngine, 
        DuplicateDetectionEngine, 
        CollaborationMatchingEngine,
        AdvancedSimilaritySearch
    )
except ImportError:
    logger.warning("Similarity search components not available")
    SimilaritySearchEngine = None
    DuplicateDetectionEngine = None
    CollaborationMatchingEngine = None
    AdvancedSimilaritySearch = None

try:
    from .operations import VectorDBOperations, VectorDBMonitor
except ImportError:
    logger.warning("Operations components not available")
    VectorDBOperations = None
    VectorDBMonitor = None

try:
    from .index import VectorDatabaseManager
except ImportError:
    logger.warning("Index manager component not available")
    VectorDatabaseManager = None

# Module exports
__all__ = [
    # Core management classes
    'VectorDBManager',
    'SimilaritySearcher', 
    'VectorSearchResult',
    'VectorIndex',
    'VectorBackend',
    'VectorDatabaseManager',
    
    # Backend implementations
    'FAISSBackend',
    'FAISSIndexManager', 
    'ChromaBackend',
    'ChromaCollectionManager',
    
    # Embedding engines
    'TextEmbeddingGenerator',
    'AudioEmbeddingGenerator', 
    'ImageEmbeddingGenerator',
    'VideoEmbeddingGenerator',
    'MultiModalEmbeddingEngine',
    
    # Similarity search engines
    'SimilaritySearchEngine',
    'DuplicateDetectionEngine',
    'CollaborationMatchingEngine', 
    'AdvancedSimilaritySearch',
    
    # Operations and monitoring
    'VectorDBOperations',
    'VectorDBMonitor',
    
    # Configuration classes
    'VectorBackendConfig'
]

# Module version and metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary - All Rights Reserved"
__copyright__ = "(c) 2025 Fahed Mlaiel"

# Initialize logging for the module
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger.info(f"Vector DB Module v{__version__} initialized successfully")
logger.info(f"Available backends: FAISS={faiss is not None}, ChromaDB={chromadb is not None}")
logger.info(f"PyTorch available: {torch is not None}")
logger.info(f"SentenceTransformers available: {SentenceTransformer is not None}")
