"""Vector Search Service - FAISS Integration for Content Similarity

Advanced vector database implementation using FAISS for high-performance
similarity search across multi-format content fingerprints.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.

Project Team Specialties:
- Lead AI Developer & Senior Backend Engineer: Fahed Mlaiel
- ML Engineer: Vector embeddings and similarity algorithms
- Database Administrator: FAISS performance optimization
- Search Engineer: High-performance vector retrieval systems
- DevOps Engineer: Scalable vector database infrastructure

Contact: mlaiel@live.de

LEGAL WARNING: This software and all associated intellectual property
belong exclusively to Fahed Mlaiel. Any unauthorized copying, redistribution,
reverse engineering, or commercial use without explicit written permission
will result in immediate legal action under international copyright laws.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import pickle
import json
import hashlib
import uuid

# FAISS imports
try:
    import faiss
except ImportError:
    faiss = None
    logging.warning("FAISS not installed. Vector search functionality will be limited.")

# Elasticsearch imports
try:
    from elasticsearch import AsyncElasticsearch
    from elasticsearch.helpers import async_bulk
except ImportError:
    AsyncElasticsearch = None
    logging.warning("Elasticsearch not installed. Text search functionality will be limited.")

# Redis for caching
try:
    import redis.asyncio as redis
except ImportError:
    redis = None
    logging.warning("Redis not installed. Caching functionality will be limited.")

from ..core.exceptions import VectorSearchException, DatabaseException
from ..core.models import BaseModel
from ..core.config import get_settings


class VectorType(Enum):
    """Types of content vectors."""

    AUDIO_FINGERPRINT = "audio_fingerprint"
    VIDEO_FINGERPRINT = "video_fingerprint"
    IMAGE_FINGERPRINT = "image_fingerprint"
    TEXT_EMBEDDING = "text_embedding"
    COMBINED_MULTIMODAL = "combined_multimodal"


class SimilarityMetric(Enum):
    """Similarity metrics for vector comparison."""

    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    MANHATTAN = "manhattan"
    DOT_PRODUCT = "dot_product"


@dataclass
class VectorRecord:
    """Vector database record."""
    vector_id: str
    content_id: str
    vector_type: VectorType
    embedding: np.ndarray
    metadata: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary."""
        return {
            "vector_id": self.vector_id,
            "content_id": self.content_id,
            "vector_type": self.vector_type.value,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "embedding_shape": self.embedding.shape,
            "embedding_dtype": str(self.embedding.dtype)
        }


@dataclass
class SimilarityResult:
    """Similarity search result."""
    content_id: str
    vector_id: str
    similarity_score: float
    vector_type: VectorType
    metadata: Dict[str, Any]
    distance: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary."""
        return {
            "content_id": self.content_id,
            "vector_id": self.vector_id,
            "similarity_score": self.similarity_score,
            "vector_type": self.vector_type.value,
            "metadata": self.metadata,
            "distance": self.distance
        }


class FAISSIndexManager:
    """FAISS index management for efficient vector operations."""
    
    def __init__(self, dimension: int, metric: SimilarityMetric = SimilarityMetric.COSINE):
        if faiss is None:
            raise VectorSearchException("FAISS not installed. Please install faiss-cpu or faiss-gpu.")
            
        self.dimension = dimension
        self.metric = metric
        self.index = self._create_index()
        self.id_to_metadata: Dict[int, Dict[str, Any]] = {}
        self.vector_id_to_faiss_id: Dict[str, int] = {}
        self.next_faiss_id = 0
        
    def _create_index(self) -> faiss.Index:
        """Create FAISS index based on metric."""
        if self.metric == SimilarityMetric.COSINE:
            # Use Inner Product for cosine similarity (normalize vectors)
            index = faiss.IndexFlatIP(self.dimension)
        elif self.metric == SimilarityMetric.EUCLIDEAN:
            index = faiss.IndexFlatL2(self.dimension)
        else:
            # Default to L2 (Euclidean)
            index = faiss.IndexFlatL2(self.dimension)
            
        return index
        
    def add_vector(self, vector_id: str, embedding: np.ndarray, metadata: Dict[str, Any]):
        """
Add vector to FAISS index."""
        if embedding.shape[0] != self.dimension:
            raise VectorSearchException(f"Vector dimension {embedding.shape[0]} doesn't match index dimension {self.dimension}")
            
        # Normalize for cosine similarity
        if self.metric == SimilarityMetric.COSINE:
            embedding = embedding / np.linalg.norm(embedding)
            
        # Add to FAISS index
        embedding_2d = embedding.reshape(1, -1).astype('float32')
        self.index.add(embedding_2d)
        
        # Store metadata
        faiss_id = self.next_faiss_id
        self.id_to_metadata[faiss_id] = metadata
        self.vector_id_to_faiss_id[vector_id] = faiss_id
        self.next_faiss_id += 1
        
    def search_similar(self, query_vector: np.ndarray, k: int = 10, threshold: float = 0.0) -> List[Tuple[float, Dict[str, Any]]]:
        """Search for similar vectors."""
        if query_vector.shape[0] != self.dimension:
            raise VectorSearchException(f"Query vector dimension {query_vector.shape[0]} doesn't match index dimension {self.dimension}")
            
        # Normalize for cosine similarity
        if self.metric == SimilarityMetric.COSINE:
            query_vector = query_vector / np.linalg.norm(query_vector)
            
        # Search in FAISS
        query_2d = query_vector.reshape(1, -1).astype('float32')
        distances, indices = self.index.search(query_2d, k)
        
        # Convert distances to similarities and filter by threshold
        results = []
        for distance, faiss_id in zip(distances[0], indices[0]):
            if faiss_id == -1:  # No more results
                break
                
            # Convert distance to similarity score
            if self.metric == SimilarityMetric.COSINE:
                similarity = float(distance)  # Inner product is already similarity
            else:
                similarity = 1.0 / (1.0 + float(distance))  # Convert distance to similarity
                
            if similarity >= threshold:
                metadata = self.id_to_metadata.get(faiss_id, {})
                results.append((similarity, metadata))
                
        return results
        
    def remove_vector(self, vector_id: str) -> bool:
        """Remove vector from index (FAISS doesn't support direct removal)."""
        # Note: FAISS doesn't support direct removal. In production, use IndexIDMap
        if vector_id in self.vector_id_to_faiss_id:
            faiss_id = self.vector_id_to_faiss_id[vector_id]
            del self.vector_id_to_faiss_id[vector_id]
            del self.id_to_metadata[faiss_id]
            return True
        return False
        
    def get_total_vectors(self) -> int:
        """
Get total number of vectors in index."""
        return self.index.ntotal
        
    def save_index(self, filepath: Path):
        """
Save FAISS index to disk."""
        faiss.write_index(self.index, str(filepath))
        
        # Save metadata separately
        metadata_file = filepath.with_suffix('.metadata.pkl')
        with open(metadata_file, 'wb') as f:
            pickle.dump({
                'id_to_metadata': self.id_to_metadata,
                'vector_id_to_faiss_id': self.vector_id_to_faiss_id,
                'next_faiss_id': self.next_faiss_id
            }, f)
            
    def load_index(self, filepath: Path):
        """
Load FAISS index from disk."""
        self.index = faiss.read_index(str(filepath))
        
        # Load metadata
        metadata_file = filepath.with_suffix('.metadata.pkl')
        if metadata_file.exists():
            with open(metadata_file, 'rb') as f:
                metadata_dict = pickle.load(f)
                self.id_to_metadata = metadata_dict['id_to_metadata']
                self.vector_id_to_faiss_id = metadata_dict['vector_id_to_faiss_id']
                self.next_faiss_id = metadata_dict['next_faiss_id']


class VectorSearchService:
    """
Professional vector search service with FAISS and Elasticsearch integration."""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        
        # FAISS managers for different vector types
        self.faiss_managers: Dict[VectorType, FAISSIndexManager] = {}
        
        # Elasticsearch client
        self.es_client: Optional[AsyncElasticsearch] = None
        
        # Redis client for caching
        self.redis_client: Optional[redis.Redis] = None
        
        # Initialize services
        asyncio.create_task(self._initialize_services())
        
    async def _initialize_services(self):
        """
Initialize external services."""
        try:
            # Initialize Elasticsearch
            if AsyncElasticsearch and hasattr(self.settings, 'ELASTICSEARCH_URL'):
                self.es_client = AsyncElasticsearch(
                    hosts=[self.settings.ELASTICSEARCH_URL],
                    verify_certs=False,
                    ssl_show_warn=False
                )
                await self._create_elasticsearch_indices()
                
            # Initialize Redis
            if redis and hasattr(self.settings, 'REDIS_URL'):
                self.redis_client = redis.from_url(self.settings.REDIS_URL)
                
            self.logger.info("Vector search services initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize vector search services: {e}")
            
    async def _create_elasticsearch_indices(self):
        """Create Elasticsearch indices for vector metadata."""
        if not self.es_client:
            return
            
        # Index mapping for vector metadata
        mapping = {
            "mappings": {
                "properties": {
                    "vector_id": {"type": "keyword"},
                    "content_id": {"type": "keyword"},
                    "vector_type": {"type": "keyword"},
                    "metadata": {"type": "object"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
                }
            }
        }
        
        try:
            await self.es_client.indices.create(
                index="content_vectors",
                body=mapping,
                ignore=400  # Ignore if index already exists
            )
            self.logger.info("Elasticsearch indices created successfully")
        except Exception as e:
            self.logger.error(f"Failed to create Elasticsearch indices: {e}")
            
    def _get_faiss_manager(self, vector_type: VectorType, dimension: int) -> FAISSIndexManager:
        """Get or create FAISS manager for vector type."""
        if vector_type not in self.faiss_managers:
            self.faiss_managers[vector_type] = FAISSIndexManager(
                dimension=dimension,
                metric=SimilarityMetric.COSINE
            )
        return self.faiss_managers[vector_type]
        
    async def store_fingerprint_vector(
        self,
        content_id: str,
        embedding: np.ndarray,
        vector_type: VectorType,
        metadata: Dict[str, Any]
    ) -> str:
        """
Store content fingerprint vector."""
        try:
            vector_id = str(uuid.uuid4())
            
            # Get FAISS manager
            faiss_manager = self._get_faiss_manager(vector_type, embedding.shape[0])
            
            # Prepare metadata with vector info
            full_metadata = {
                **metadata,
                "vector_id": vector_id,
                "content_id": content_id,
                "vector_type": vector_type.value
            }
            
            # Add to FAISS index
            faiss_manager.add_vector(vector_id, embedding, full_metadata)
            
            # Store in Elasticsearch for metadata search
            if self.es_client:
                vector_record = VectorRecord(
                    vector_id=vector_id,
                    content_id=content_id,
                    vector_type=vector_type,
                    embedding=embedding,
                    metadata=metadata
                )
                
                await self.es_client.index(
                    index="content_vectors",
                    id=vector_id,
                    body=vector_record.to_dict()
                )
                
            # Cache in Redis
            if self.redis_client:
                cache_key = f"vector:{vector_id}"
                await self.redis_client.setex(
                    cache_key,
                    3600,  # 1 hour TTL
                    json.dumps(full_metadata)
                )
                
            self.logger.info(f"Stored vector {vector_id} for content {content_id}")
            return vector_id
            
        except Exception as e:
            self.logger.error(f"Failed to store fingerprint vector: {e}")
            raise VectorSearchException(f"Failed to store vector: {str(e)}")
            
    async def search_similar_content(
        self,
        query_embedding: np.ndarray,
        vector_type: VectorType,
        k: int = 10,
        threshold: float = 0.7
    ) -> List[SimilarityResult]:
        """Search for similar content by vector embedding."""
        try:
            if vector_type not in self.faiss_managers:
                return []
                
            faiss_manager = self.faiss_managers[vector_type]
            
            # Search in FAISS
            results = faiss_manager.search_similar(
                query_embedding, 
                k=k, 
                threshold=threshold
            )
            
            # Convert to SimilarityResult objects
            similarity_results = []
            for similarity_score, metadata in results:
                result = SimilarityResult(
                    content_id=metadata.get("content_id", ""),
                    vector_id=metadata.get("vector_id", ""),
                    similarity_score=similarity_score,
                    vector_type=vector_type,
                    metadata=metadata,
                    distance=1.0 - similarity_score  # Convert similarity to distance
                )
                similarity_results.append(result)
                
            self.logger.info(f"Found {len(similarity_results)} similar content items")
            return similarity_results
            
        except Exception as e:
            self.logger.error(f"Failed to search similar content: {e}")
            raise VectorSearchException(f"Failed to search similar content: {str(e)}")
            
    async def get_vector_by_id(self, vector_id: str) -> Optional[VectorRecord]:
        """Get vector record by ID."""
        try:
            # Try cache first
            if self.redis_client:
                cache_key = f"vector:{vector_id}"
                cached_data = await self.redis_client.get(cache_key)
                if cached_data:
                    metadata = json.loads(cached_data)
                    return VectorRecord(
                        vector_id=vector_id,
                        content_id=metadata.get("content_id", ""),
                        vector_type=VectorType(metadata.get("vector_type", "")),
                        embedding=np.array([]),  # Not stored in cache
                        metadata=metadata
                    )
                    
            # Try Elasticsearch
            if self.es_client:
                response = await self.es_client.get(
                    index="content_vectors",
                    id=vector_id,
                    ignore=404
                )
                
                if response.get("found"):
                    source = response["_source"]
                    return VectorRecord(
                        vector_id=vector_id,
                        content_id=source["content_id"],
                        vector_type=VectorType(source["vector_type"]),
                        embedding=np.array([]),  # Not stored in ES
                        metadata=source["metadata"]
                    )
                    
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get vector by ID {vector_id}: {e}")
            return None
            
    async def delete_vector(self, vector_id: str) -> bool:
        """Delete vector by ID."""
        try:
            success = False
            
            # Remove from all FAISS managers
            for faiss_manager in self.faiss_managers.values():
                if faiss_manager.remove_vector(vector_id):
                    success = True
                    
            # Remove from Elasticsearch
            if self.es_client:
                await self.es_client.delete(
                    index="content_vectors",
                    id=vector_id,
                    ignore=404
                )
                success = True
                
            # Remove from Redis cache
            if self.redis_client:
                cache_key = f"vector:{vector_id}"
                await self.redis_client.delete(cache_key)
                
            self.logger.info(f"Deleted vector {vector_id}")
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to delete vector {vector_id}: {e}")
            return False
            
    async def search_by_metadata(
        self,
        query: Dict[str, Any],
        limit: int = 100
    ) -> List[VectorRecord]:
        """Search vectors by metadata using Elasticsearch."""
        if not self.es_client:
            return []
            
        try:
            # Build Elasticsearch query
            es_query = {
                "query": {
                    "bool": {
                        "must": []
                    }
                },
                "size": limit
            }
            
            for key, value in query.items():
                es_query["query"]["bool"]["must"].append({
                    "match": {f"metadata.{key}": value}
                })
                
            # Execute search
            response = await self.es_client.search(
                index="content_vectors",
                body=es_query
            )
            
            # Parse results
            results = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                record = VectorRecord(
                    vector_id=source["vector_id"],
                    content_id=source["content_id"],
                    vector_type=VectorType(source["vector_type"]),
                    embedding=np.array([]),  # Not stored in ES
                    metadata=source["metadata"]
                )
                results.append(record)
                
            self.logger.info(f"Found {len(results)} vectors by metadata search")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to search by metadata: {e}")
            return []
            
    async def get_statistics(self) -> Dict[str, Any]:
        """Get vector database statistics."""
        stats = {
            "total_vectors": 0,
            "vectors_by_type": {},
            "faiss_managers": len(self.faiss_managers)
        }
        
        try:
            # FAISS statistics
            for vector_type, manager in self.faiss_managers.items():
                count = manager.get_total_vectors()
                stats["vectors_by_type"][vector_type.value] = count
                stats["total_vectors"] += count
                
            # Elasticsearch statistics
            if self.es_client:
                es_stats = await self.es_client.count(index="content_vectors")
                stats["elasticsearch_count"] = es_stats.get("count", 0)
                
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return stats
            
    async def save_indices(self, directory: Path):
        """Save all FAISS indices to disk."""
        try:
            directory.mkdir(parents=True, exist_ok=True)
            
            for vector_type, manager in self.faiss_managers.items():
                index_file = directory / f"{vector_type.value}_index.faiss"
                manager.save_index(index_file)
                
            self.logger.info(f"Saved {len(self.faiss_managers)} FAISS indices to {directory}")
            
        except Exception as e:
            self.logger.error(f"Failed to save indices: {e}")
            raise VectorSearchException(f"Failed to save indices: {str(e)}")
            
    async def load_indices(self, directory: Path):
        """Load FAISS indices from disk."""
        try:
            if not directory.exists():
                self.logger.warning(f"Index directory {directory} does not exist")
                return
                
            for vector_type in VectorType:
                index_file = directory / f"{vector_type.value}_index.faiss"
                if index_file.exists():
                    # Determine dimension from saved index
                    temp_index = faiss.read_index(str(index_file))
                    dimension = temp_index.d
                    
                    # Create manager and load index
                    manager = FAISSIndexManager(dimension)
                    manager.load_index(index_file)
                    self.faiss_managers[vector_type] = manager
                    
            self.logger.info(f"Loaded {len(self.faiss_managers)} FAISS indices from {directory}")
            
        except Exception as e:
            self.logger.error(f"Failed to load indices: {e}")
            raise VectorSearchException(f"Failed to load indices: {str(e)}")
            

# Global service instance
_vector_search_service = None

def get_vector_search_service() -> VectorSearchService:
    """Get global vector search service instance."""
    global _vector_search_service
    if _vector_search_service is None:
        _vector_search_service = VectorSearchService()
    return _vector_search_service
