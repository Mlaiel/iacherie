"""
Vector Database Manager - Enterprise AI Infrastructure
High-performance vector database management for Ainflue AI content analysis and recommendations

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

ML Engineer Role Implementation:
- Multi-modal vector storage (audio, video, image, text)
- Content similarity and recommendation engines
- AI-powered content fingerprinting
- Real-time embedding search and matching
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class VectorDBType(Enum):
    """Supported vector database types"""
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"
    CHROMA = "chroma"
    QDRANT = "qdrant"
    MILVUS = "milvus"


class ContentType(Enum):
    """Content types for vector storage"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MULTI_MODAL = "multi_modal"


class SimilarityMetric(Enum):
    """Vector similarity metrics"""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"
    MANHATTAN = "manhattan"


@dataclass
class VectorConfig:
    """Vector database configuration"""
    db_type: VectorDBType
    dimension: int  # Vector dimensions (e.g., 1536 for OpenAI, 768 for sentence transformers)
    metric: SimilarityMetric = SimilarityMetric.COSINE
    index_type: str = "hnsw"  # Hierarchical Navigable Small World
    replica_count: int = 3
    shard_count: int = 1
    memory_limit_gb: int = 8
    ef_construction: int = 200  # HNSW parameter
    max_connections: int = 16  # HNSW parameter


@dataclass
class EmbeddingMetadata:
    """Metadata for vector embeddings"""
    content_id: str
    creator_id: str
    content_type: ContentType
    upload_timestamp: datetime
    tags: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    duration_seconds: Optional[float] = None
    file_size_mb: Optional[float] = None
    platform_source: Optional[str] = None
    ai_analysis: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """Vector search result"""
    content_id: str
    similarity_score: float
    metadata: EmbeddingMetadata
    vector: Optional[np.ndarray] = None


class VectorDatabaseManager:
    """Enterprise vector database management for Ainflue AI content analysis"""
    
    def __init__(self):
        """Initialize vector database manager"""
        self.vector_stores: Dict[str, Dict[str, Any]] = {}
        self.embedding_cache: Dict[str, np.ndarray] = {}
        self.metadata_cache: Dict[str, EmbeddingMetadata] = {}
        logger.info("Vector database manager initialized for Ainflue AI processing")
        
    async def setup_vector_store(self, config: VectorConfig, collection_name: str) -> Dict[str, Any]:
        """
        Setup vector database for Ainflue content embeddings
        
        Optimized for:
        - Content similarity matching
        - Creator collaboration recommendations
        - Copyright protection fingerprinting
        - AI-powered content analysis
        """
        store_info = {
            'collection_id': f"vectors-{collection_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'name': collection_name,
            'config': config,
            'status': 'creating',
            'created_at': datetime.utcnow(),
            'endpoints': {
                'read': f"vector-read-{collection_name}.ainflue.com:443",
                'write': f"vector-write-{collection_name}.ainflue.com:443",
                'search': f"vector-search-{collection_name}.ainflue.com:443"
            },
            'indexes': {},
            'statistics': {
                'total_vectors': 0,
                'total_size_gb': 0.0,
                'avg_query_latency_ms': 0.0
            }
        }
        
        # Configure content-specific indexes
        await self._setup_content_indexes(store_info, config)
        
        # Setup embedding collections for different content types
        store_info['collections'] = await self._setup_embedding_collections(config)
        
        self.vector_stores[store_info['collection_id']] = store_info
        store_info['status'] = 'active'
        
        logger.info(f"Vector store {collection_name} created with {config.dimension}D vectors")
        return store_info
        
    async def _setup_content_indexes(self, store_info: Dict[str, Any], config: VectorConfig) -> None:
        """Setup vector indexes optimized for content types"""
        indexes = {
            'audio_content': {
                'dimension': config.dimension,
                'metric': config.metric.value,
                'index_config': {
                    'ef_construction': config.ef_construction,
                    'max_connections': config.max_connections,
                    'audio_specific': {
                        'tempo_weight': 0.3,
                        'pitch_weight': 0.4,
                        'timbre_weight': 0.3
                    }
                }
            },
            'visual_content': {
                'dimension': config.dimension,
                'metric': config.metric.value,
                'index_config': {
                    'ef_construction': config.ef_construction,
                    'max_connections': config.max_connections,
                    'visual_specific': {
                        'color_weight': 0.25,
                        'texture_weight': 0.25,
                        'shape_weight': 0.25,
                        'composition_weight': 0.25
                    }
                }
            },
            'text_content': {
                'dimension': config.dimension,
                'metric': config.metric.value,
                'index_config': {
                    'ef_construction': config.ef_construction,
                    'max_connections': config.max_connections,
                    'text_specific': {
                        'semantic_weight': 0.6,
                        'syntactic_weight': 0.4
                    }
                }
            },
            'creator_profiles': {
                'dimension': config.dimension,
                'metric': config.metric.value,
                'index_config': {
                    'ef_construction': config.ef_construction,
                    'max_connections': config.max_connections,
                    'profile_specific': {
                        'content_style_weight': 0.4,
                        'collaboration_history_weight': 0.3,
                        'audience_similarity_weight': 0.3
                    }
                }
            }
        }
        
        store_info['indexes'] = indexes
        logger.info(f"Configured {len(indexes)} specialized indexes for content types")
        
    async def _setup_embedding_collections(self, config: VectorConfig) -> Dict[str, Any]:
        """Setup embedding collections for Ainflue business logic"""
        collections = {
            'content_fingerprints': {
                'purpose': 'Copyright protection and duplicate detection',
                'vector_type': 'content_hash',
                'metadata_schema': {
                    'original_hash': str,
                    'content_type': str,
                    'creator_id': str,
                    'protection_level': str
                }
            },
            'content_recommendations': {
                'purpose': 'AI-powered content discovery and recommendations',
                'vector_type': 'content_semantic',
                'metadata_schema': {
                    'genre': str,
                    'mood': str,
                    'engagement_score': float,
                    'audience_demographics': dict
                }
            },
            'creator_matching': {
                'purpose': 'Collaboration partner recommendations',
                'vector_type': 'creator_profile',
                'metadata_schema': {
                    'content_types': list,
                    'collaboration_history': list,
                    'style_preferences': dict,
                    'availability': str
                }
            },
            'trend_analysis': {
                'purpose': 'Content trend identification and prediction',
                'vector_type': 'trend_semantic',
                'metadata_schema': {
                    'trending_score': float,
                    'category': str,
                    'time_period': str,
                    'geographic_relevance': list
                }
            }
        }
        
        logger.info(f"Configured {len(collections)} embedding collections for Ainflue AI")
        return collections
        
    async def store_embedding(
        self, 
        collection_id: str, 
        vector: np.ndarray, 
        metadata: EmbeddingMetadata
    ) -> str:
        """Store content embedding with metadata"""
        if collection_id not in self.vector_stores:
            raise ValueError(f"Collection {collection_id} not found")
            
        # Generate unique embedding ID
        embedding_id = f"embed_{metadata.content_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        # Validate vector dimensions
        store = self.vector_stores[collection_id]
        expected_dim = store['config'].dimension
        if vector.shape[0] != expected_dim:
            raise ValueError(f"Vector dimension {vector.shape[0]} doesn't match expected {expected_dim}")
            
        # Normalize vector for cosine similarity
        if store['config'].metric == SimilarityMetric.COSINE:
            vector = vector / np.linalg.norm(vector)
            
        # Store in cache (in production, would store in actual vector DB)
        self.embedding_cache[embedding_id] = vector
        self.metadata_cache[embedding_id] = metadata
        
        # Update statistics
        store['statistics']['total_vectors'] += 1
        store['statistics']['total_size_gb'] += vector.nbytes / (1024**3)
        
        logger.info(f"Stored {expected_dim}D embedding for content {metadata.content_id}")
        return embedding_id
        
    async def search_similar_content(
        self, 
        collection_id: str, 
        query_vector: np.ndarray, 
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar content using vector similarity"""
        if collection_id not in self.vector_stores:
            raise ValueError(f"Collection {collection_id} not found")
            
        store = self.vector_stores[collection_id]
        metric = store['config'].metric
        
        # Normalize query vector if using cosine similarity
        if metric == SimilarityMetric.COSINE:
            query_vector = query_vector / np.linalg.norm(query_vector)
            
        results = []
        
        # Search through cached embeddings (in production, would use vector DB search)
        for embed_id, stored_vector in self.embedding_cache.items():
            if embed_id not in self.metadata_cache:
                continue
                
            metadata = self.metadata_cache[embed_id]
            
            # Apply filters if provided
            if filters and not self._matches_filters(metadata, filters):
                continue
                
            # Calculate similarity
            similarity = self._calculate_similarity(query_vector, stored_vector, metric)
            
            results.append(SearchResult(
                content_id=metadata.content_id,
                similarity_score=similarity,
                metadata=metadata,
                vector=stored_vector
            ))
            
        # Sort by similarity and return top-k
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:top_k]
        
    def _matches_filters(self, metadata: EmbeddingMetadata, filters: Dict[str, Any]) -> bool:
        """Check if metadata matches search filters"""
        for key, value in filters.items():
            if key == 'content_type' and metadata.content_type.value != value:
                return False
            elif key == 'creator_id' and metadata.creator_id != value:
                return False
            elif key == 'min_quality_score' and metadata.quality_score < value:
                return False
            elif key == 'tags' and not any(tag in metadata.tags for tag in value):
                return False
                
        return True
        
    def _calculate_similarity(
        self, 
        vec1: np.ndarray, 
        vec2: np.ndarray, 
        metric: SimilarityMetric
    ) -> float:
        """Calculate similarity between two vectors"""
        if metric == SimilarityMetric.COSINE:
            return float(np.dot(vec1, vec2))
        elif metric == SimilarityMetric.EUCLIDEAN:
            return float(1.0 / (1.0 + np.linalg.norm(vec1 - vec2)))
        elif metric == SimilarityMetric.DOT_PRODUCT:
            return float(np.dot(vec1, vec2))
        elif metric == SimilarityMetric.MANHATTAN:
            return float(1.0 / (1.0 + np.sum(np.abs(vec1 - vec2))))
        else:
            return 0.0
            
    async def detect_content_duplicates(
        self, 
        collection_id: str, 
        content_vector: np.ndarray, 
        threshold: float = 0.95
    ) -> List[SearchResult]:
        """Detect potential content duplicates for copyright protection"""
        similar_content = await self.search_similar_content(
            collection_id, 
            content_vector, 
            top_k=50
        )
        
        # Filter for high similarity (potential duplicates)
        duplicates = [
            result for result in similar_content 
            if result.similarity_score >= threshold
        ]
        
        if duplicates:
            logger.warning(f"Found {len(duplicates)} potential duplicates with similarity >= {threshold}")
            
        return duplicates
        
    async def recommend_collaborators(
        self, 
        creator_id: str, 
        creator_style_vector: np.ndarray,
        max_recommendations: int = 20
    ) -> List[SearchResult]:
        """Recommend collaboration partners based on content style similarity"""
        # Search for creators with complementary styles
        filters = {
            'content_type': ContentType.MULTI_MODAL.value,
            'min_quality_score': 0.7
        }
        
        # Exclude the creator themselves
        collaborators = []
        for collection_id in self.vector_stores:
            results = await self.search_similar_content(
                collection_id,
                creator_style_vector,
                top_k=max_recommendations * 2,
                filters=filters
            )
            
            # Filter out self and low-quality matches
            filtered_results = [
                result for result in results
                if (result.metadata.creator_id != creator_id and 
                    result.similarity_score >= 0.6 and
                    result.similarity_score <= 0.9)  # Similar but not too similar
            ]
            
            collaborators.extend(filtered_results)
            
        # Sort by collaboration potential and return top recommendations
        collaborators.sort(key=lambda x: x.similarity_score, reverse=True)
        return collaborators[:max_recommendations]
        
    async def get_performance_metrics(self, collection_id: str) -> Dict[str, Any]:
        """Get vector database performance metrics"""
        if collection_id not in self.vector_stores:
            raise ValueError(f"Collection {collection_id} not found")
            
        store = self.vector_stores[collection_id]
        
        # Simulate performance metrics (in production, would query actual DB)
        metrics = {
            'total_vectors': store['statistics']['total_vectors'],
            'index_size_gb': store['statistics']['total_size_gb'],
            'avg_query_latency_ms': 12.5,  # Fast vector search
            'throughput_qps': 1500,  # Queries per second
            'memory_usage_gb': 6.2,
            'cache_hit_ratio': 0.92,
            'last_updated': datetime.utcnow()
        }
        
        store['statistics'].update(metrics)
        return metrics
        
    async def store_embeddings(self, collection_id: str, embeddings_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Store multiple embeddings in batch for efficient processing
        ML Engineer Role Implementation for Ainflue AI content analysis
        
        Args:
            collection_id: Collection identifier
            embeddings_batch: List of embedding dictionaries with vectors and metadata
            
        Returns:
            Batch storage result with success/failure details
        """
        logger.info(f"Storing batch of {len(embeddings_batch)} embeddings in collection: {collection_id}")
        
        if collection_id not in self.vector_stores:
            raise ValueError(f"Collection {collection_id} not found")
            
        store = self.vector_stores[collection_id]
        batch_results = {
            'collection_id': collection_id,
            'total_embeddings': len(embeddings_batch),
            'successful_insertions': 0,
            'failed_insertions': 0,
            'processing_time_ms': 0,
            'batch_id': f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'errors': []
        }
        
        start_time = datetime.utcnow()
        
        try:
            # Process embeddings in chunks for better memory management
            chunk_size = 100  # Process 100 embeddings at a time
            processed_count = 0
            
            for i in range(0, len(embeddings_batch), chunk_size):
                chunk = embeddings_batch[i:i + chunk_size]
                
                for embedding_data in chunk:
                    try:
                        # Validate embedding data structure
                        if not self._validate_embedding_data(embedding_data):
                            batch_results['failed_insertions'] += 1
                            batch_results['errors'].append(f"Invalid embedding data at index {processed_count}")
                            continue
                            
                        # Prepare embedding for storage
                        embedding_id = embedding_data.get('id') or f"{collection_id}_{len(store['vectors'])}"
                        vector = np.array(embedding_data['vector'])
                        metadata = EmbeddingMetadata(**embedding_data.get('metadata', {}))
                        
                        # Store in vector database
                        await self._store_single_embedding(store, embedding_id, vector, metadata)
                        
                        batch_results['successful_insertions'] += 1
                        processed_count += 1
                        
                        # Update collection statistics
                        store['statistics']['total_vectors'] += 1
                        store['statistics']['last_updated'] = datetime.utcnow()
                        
                    except Exception as e:
                        batch_results['failed_insertions'] += 1
                        batch_results['errors'].append(f"Failed to store embedding at index {processed_count}: {str(e)}")
                        logger.warning(f"Failed to store embedding: {e}")
                        
                # Log progress for large batches
                if len(embeddings_batch) > chunk_size:
                    logger.info(f"Processed {min(i + chunk_size, len(embeddings_batch))}/{len(embeddings_batch)} embeddings")
                    
            # Calculate processing time
            end_time = datetime.utcnow()
            batch_results['processing_time_ms'] = int((end_time - start_time).total_seconds() * 1000)
            
            # Update store statistics
            store['statistics']['total_size_gb'] = self._calculate_collection_size(store)
            store['statistics']['last_batch_size'] = len(embeddings_batch)
            store['statistics']['batch_success_rate'] = (
                batch_results['successful_insertions'] / batch_results['total_embeddings'] * 100
                if batch_results['total_embeddings'] > 0 else 0
            )
            
            logger.info(f"Batch storage completed: {batch_results['successful_insertions']}/{batch_results['total_embeddings']} successful")
            return batch_results
            
        except Exception as e:
            logger.error(f"Batch embedding storage failed: {e}")
            batch_results['errors'].append(f"Batch operation failed: {str(e)}")
            return batch_results
            
    def _validate_embedding_data(self, embedding_data: Dict[str, Any]) -> bool:
        """Validate embedding data structure"""
        required_fields = ['vector']
        
        for field in required_fields:
            if field not in embedding_data:
                return False
                
        # Validate vector
        vector = embedding_data['vector']
        if not isinstance(vector, (list, np.ndarray)):
            return False
            
        if len(vector) == 0:
            return False
            
        # Validate metadata if present
        if 'metadata' in embedding_data:
            metadata = embedding_data['metadata']
            if not isinstance(metadata, dict):
                return False
                
        return True
        
    async def _store_single_embedding(self, store: Dict[str, Any], embedding_id: str, vector: np.ndarray, metadata: EmbeddingMetadata) -> None:
        """Store a single embedding in the vector store"""
        
        # Create embedding entry
        embedding_entry = {
            'id': embedding_id,
            'vector': vector.tolist() if isinstance(vector, np.ndarray) else vector,
            'metadata': {
                'content_type': metadata.content_type,
                'creator_id': metadata.creator_id,
                'timestamp': metadata.timestamp or datetime.utcnow(),
                'content_id': metadata.content_id,
                'tags': metadata.tags or [],
                'custom_fields': metadata.custom_fields or {}
            },
            'indexed_at': datetime.utcnow()
        }
        
        # Add to vector store
        store['vectors'][embedding_id] = embedding_entry
        
        # Update indexes for fast retrieval
        content_type = metadata.content_type
        if content_type not in store['indexes']:
            store['indexes'][content_type] = []
        store['indexes'][content_type].append(embedding_id)
        
        # Creator index for collaboration features
        creator_id = metadata.creator_id
        if creator_id:
            if 'creator_index' not in store:
                store['creator_index'] = {}
            if creator_id not in store['creator_index']:
                store['creator_index'][creator_id] = []
            store['creator_index'][creator_id].append(embedding_id)
            
    def _calculate_collection_size(self, store: Dict[str, Any]) -> float:
        """Calculate approximate size of collection in GB"""
        total_vectors = len(store['vectors'])
        avg_vector_size_kb = 4  # Approximate size per vector in KB
        total_size_gb = (total_vectors * avg_vector_size_kb) / (1024 * 1024)  # Convert to GB
        return round(total_size_gb, 3)