"""
📊 Vector Index Manager
=======================

Manages multiple vector indexes for different content types and embedding dimensions.
Provides unified interface for index lifecycle management and optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import time
import hashlib
from concurrent.futures import ThreadPoolExecutor

from .faiss_store import FaissVectorStore, IndexType, SearchResult, IndexStats
from .embeddings import EmbeddingType, EmbeddingResult
from .similarity_search import SearchEngine, SimilarityResult, SearchConfiguration, SimilarityMetric
import numpy as np

logger = logging.getLogger(__name__)


class IndexStatus(Enum):
    """Status of vector index"""
    INITIALIZING = "initializing"
    READY = "ready"
    TRAINING = "training"
    OPTIMIZING = "optimizing"
    SAVING = "saving"
    LOADING = "loading"
    ERROR = "error"


@dataclass
class IndexConfiguration:
    """Configuration for a vector index"""
    index_name: str
    embedding_type: EmbeddingType
    dimension: int
    index_type: IndexType
    similarity_metric: SimilarityMetric
    storage_path: str
    auto_save_interval: int = 3600  # seconds
    max_vectors: int = 1000000
    training_sample_size: int = 10000


@dataclass
class IndexInfo:
    """Information about a managed index"""
    config: IndexConfiguration
    status: IndexStatus
    vector_count: int
    memory_usage_mb: float
    last_updated: str
    last_saved: str
    search_performance_ms: float


class VectorIndexManager:
    """Manages multiple vector indexes for different content types"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.VectorIndexManager")
        
        # Storage configuration
        self.base_storage_path = Path(config.get('storage_path', './data/vector_indexes'))
        self.base_storage_path.mkdir(parents=True, exist_ok=True)
        
        # Index storage
        self.indexes: Dict[str, FaissVectorStore] = {}
        self.search_engines: Dict[str, SearchEngine] = {}
        self.index_configs: Dict[str, IndexConfiguration] = {}
        self.index_status: Dict[str, IndexStatus] = {}
        
        # Performance tracking
        self.performance_stats = {}
        
        # Auto-save task
        self.auto_save_task = None
        self.executor = ThreadPoolExecutor(max_workers=config.get('max_workers', 4))
        
        # Default configurations for different content types
        self.default_configs = self._create_default_configurations()
        
        self.logger.info("VectorIndexManager initialized")
    
    def _create_default_configurations(self) -> Dict[EmbeddingType, IndexConfiguration]:
        """Create default configurations for different embedding types"""
        base_path = str(self.base_storage_path)
        
        return {
            EmbeddingType.AUDIO_SPECTRAL: IndexConfiguration(
                index_name="audio_spectral",
                embedding_type=EmbeddingType.AUDIO_SPECTRAL,
                dimension=512,
                index_type=IndexType.HNSW,
                similarity_metric=SimilarityMetric.COSINE,
                storage_path=f"{base_path}/audio_spectral",
                training_sample_size=5000
            ),
            EmbeddingType.VIDEO_TEMPORAL: IndexConfiguration(
                index_name="video_temporal",
                embedding_type=EmbeddingType.VIDEO_TEMPORAL,
                dimension=1024,
                index_type=IndexType.IVF_FLAT,
                similarity_metric=SimilarityMetric.COSINE,
                storage_path=f"{base_path}/video_temporal",
                training_sample_size=8000
            ),
            EmbeddingType.IMAGE_VISUAL: IndexConfiguration(
                index_name="image_visual",
                embedding_type=EmbeddingType.IMAGE_VISUAL,
                dimension=768,
                index_type=IndexType.HNSW,
                similarity_metric=SimilarityMetric.COSINE,
                storage_path=f"{base_path}/image_visual",
                training_sample_size=6000
            ),
            EmbeddingType.TEXT_SEMANTIC: IndexConfiguration(
                index_name="text_semantic",
                embedding_type=EmbeddingType.TEXT_SEMANTIC,
                dimension=384,
                index_type=IndexType.FLAT_IP,
                similarity_metric=SimilarityMetric.DOT_PRODUCT,
                storage_path=f"{base_path}/text_semantic",
                training_sample_size=4000
            ),
            EmbeddingType.COMPOSITE_MULTIMODAL: IndexConfiguration(
                index_name="composite_multimodal",
                embedding_type=EmbeddingType.COMPOSITE_MULTIMODAL,
                dimension=1536,
                index_type=IndexType.IVF_PQ,
                similarity_metric=SimilarityMetric.COSINE,
                storage_path=f"{base_path}/composite_multimodal",
                training_sample_size=10000
            )
        }
    
    async def create_index(
        self,
        embedding_type: EmbeddingType,
        custom_config: Optional[IndexConfiguration] = None
    ) -> bool:
        """Create a new vector index"""
        try:
            # Use custom config or default
            config = custom_config or self.default_configs[embedding_type]
            index_name = config.index_name
            
            if index_name in self.indexes:
                self.logger.warning(f"Index {index_name} already exists")
                return False
            
            self.logger.info(f"Creating index {index_name} for {embedding_type.value}")
            self.index_status[index_name] = IndexStatus.INITIALIZING
            
            # Create storage directory
            storage_path = Path(config.storage_path)
            storage_path.mkdir(parents=True, exist_ok=True)
            
            # Configure FAISS store
            faiss_config = {
                'dimension': config.dimension,
                'index_type': config.index_type.value,
                'storage_path': config.storage_path,
                'nlist': self.config.get('nlist', 100),
                'pq_m': self.config.get('pq_m', 8),
                'pq_nbits': self.config.get('pq_nbits', 8),
                'ef_construction': self.config.get('ef_construction', 200),
                'ef_search': self.config.get('ef_search', 50)
            }
            
            # Create FAISS store
            vector_store = FaissVectorStore(faiss_config)
            
            # Create search engine
            search_config = {
                'max_workers': self.config.get('max_workers', 4),
                'cache_max_size': self.config.get('cache_max_size', 1000)
            }
            search_engine = SearchEngine(search_config)
            
            # Store components
            self.indexes[index_name] = vector_store
            self.search_engines[index_name] = search_engine
            self.index_configs[index_name] = config
            self.index_status[index_name] = IndexStatus.READY
            
            # Initialize performance tracking
            self.performance_stats[index_name] = {
                'total_searches': 0,
                'total_additions': 0,
                'average_search_time': 0.0,
                'average_addition_time': 0.0
            }
            
            self.logger.info(f"Index {index_name} created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create index for {embedding_type.value}: {e}")
            if index_name in self.index_status:
                self.index_status[index_name] = IndexStatus.ERROR
            return False
    
    async def add_embedding(
        self,
        embedding_result: EmbeddingResult,
        content_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add an embedding to the appropriate index"""
        try:
            # Find the appropriate index
            index_name = self._get_index_name(embedding_result.embedding_type)
            
            if index_name not in self.indexes:
                # Create index if it doesn't exist
                await self.create_index(embedding_result.embedding_type)
            
            if index_name not in self.indexes:
                self.logger.error(f"No index available for {embedding_result.embedding_type.value}")
                return False
            
            start_time = time.time()
            
            # Prepare metadata
            full_metadata = {
                'content_id': content_id,
                'embedding_id': embedding_result.embedding_id,
                'embedding_type': embedding_result.embedding_type.value,
                'confidence_score': embedding_result.confidence_score,
                'dimension': embedding_result.dimension,
                'created_at': time.time(),
                **(metadata or {}),
                **embedding_result.metadata
            }
            
            # Add to vector store
            success = await self.indexes[index_name].add_vector(
                embedding_result.embedding_id,
                embedding_result.vector,
                full_metadata
            )
            
            if success:
                # Update performance stats
                addition_time = time.time() - start_time
                stats = self.performance_stats[index_name]
                stats['total_additions'] += 1
                stats['average_addition_time'] = (
                    (stats['average_addition_time'] * (stats['total_additions'] - 1) + addition_time) /
                    stats['total_additions']
                )
                
                self.logger.debug(f"Added embedding {embedding_result.embedding_id} to index {index_name}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to add embedding {embedding_result.embedding_id}: {e}")
            return False
    
    async def add_embeddings_batch(
        self,
        embeddings: List[Tuple[EmbeddingResult, str, Optional[Dict[str, Any]]]]
    ) -> List[bool]:
        """Add multiple embeddings in batch"""
        try:
            # Group embeddings by index
            grouped_embeddings = {}
            
            for embedding_result, content_id, metadata in embeddings:
                index_name = self._get_index_name(embedding_result.embedding_type)
                
                if index_name not in grouped_embeddings:
                    grouped_embeddings[index_name] = []
                
                grouped_embeddings[index_name].append((embedding_result, content_id, metadata))
            
            # Process each group
            results = []
            
            for index_name, group_embeddings in grouped_embeddings.items():
                # Ensure index exists
                if index_name not in self.indexes:
                    embedding_type = group_embeddings[0][0].embedding_type
                    await self.create_index(embedding_type)
                
                if index_name not in self.indexes:
                    results.extend([False] * len(group_embeddings))
                    continue
                
                # Prepare batch data
                vectors_data = []
                for embedding_result, content_id, metadata in group_embeddings:
                    full_metadata = {
                        'content_id': content_id,
                        'embedding_id': embedding_result.embedding_id,
                        'embedding_type': embedding_result.embedding_type.value,
                        'confidence_score': embedding_result.confidence_score,
                        'dimension': embedding_result.dimension,
                        'created_at': time.time(),
                        **(metadata or {}),
                        **embedding_result.metadata
                    }
                    
                    vectors_data.append((
                        embedding_result.embedding_id,
                        embedding_result.vector,
                        full_metadata
                    ))
                
                # Batch add to index
                batch_results = await self.indexes[index_name].add_vectors_batch(vectors_data)
                results.extend(batch_results)
                
                # Update performance stats
                successful_additions = sum(batch_results)
                if successful_additions > 0:
                    stats = self.performance_stats[index_name]
                    stats['total_additions'] += successful_additions
            
            return results
            
        except Exception as e:
            self.logger.error(f"Batch embedding addition failed: {e}")
            return [False] * len(embeddings)
    
    async def search_similar(
        self,
        query_embedding: EmbeddingResult,
        k: int = 10,
        similarity_threshold: Optional[float] = None,
        cross_modal_search: bool = False,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar embeddings"""
        try:
            start_time = time.time()
            
            if cross_modal_search:
                # Search across all indexes
                results = await self._cross_modal_search(
                    query_embedding, k, similarity_threshold, metadata_filter
                )
            else:
                # Search in specific index
                index_name = self._get_index_name(query_embedding.embedding_type)
                
                if index_name not in self.indexes:
                    self.logger.warning(f"No index found for {query_embedding.embedding_type.value}")
                    return []
                
                results = await self.indexes[index_name].search(
                    query_embedding.vector, k, similarity_threshold, metadata_filter
                )
            
            # Update performance stats
            search_time = time.time() - start_time
            for index_name in self.indexes:
                if index_name in self.performance_stats:
                    stats = self.performance_stats[index_name]
                    stats['total_searches'] += 1
                    stats['average_search_time'] = (
                        (stats['average_search_time'] * (stats['total_searches'] - 1) + search_time) /
                        stats['total_searches']
                    )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Similarity search failed: {e}")
            return []
    
    async def _cross_modal_search(
        self,
        query_embedding: EmbeddingResult,
        k: int,
        similarity_threshold: Optional[float],
        metadata_filter: Optional[Dict[str, Any]]
    ) -> List[SearchResult]:
        """Search across multiple indexes"""
        try:
            all_results = []
            
            # Search in each index
            for index_name, vector_store in self.indexes.items():
                try:
                    # Adapt query vector to index dimension if needed
                    adapted_vector = self._adapt_vector_dimension(
                        query_embedding.vector,
                        self.index_configs[index_name].dimension
                    )
                    
                    results = await vector_store.search(
                        adapted_vector, k, similarity_threshold, metadata_filter
                    )
                    
                    # Add index information to results
                    for result in results:
                        result.metadata['source_index'] = index_name
                        result.metadata['cross_modal'] = True
                    
                    all_results.extend(results)
                    
                except Exception as e:
                    self.logger.warning(f"Cross-modal search failed for index {index_name}: {e}")
                    continue
            
            # Sort and limit results
            all_results.sort(key=lambda x: x.similarity_score, reverse=True)
            return all_results[:k]
            
        except Exception as e:
            self.logger.error(f"Cross-modal search failed: {e}")
            return []
    
    def _adapt_vector_dimension(self, vector: np.ndarray, target_dimension: int) -> np.ndarray:
        """Adapt vector to target dimension"""
        current_dim = len(vector)
        
        if current_dim == target_dimension:
            return vector
        elif current_dim > target_dimension:
            # Truncate
            return vector[:target_dimension]
        else:
            # Pad with zeros
            padded = np.zeros(target_dimension, dtype=vector.dtype)
            padded[:current_dim] = vector
            return padded
    
    async def train_indexes(self, training_data: Optional[Dict[str, List[np.ndarray]]] = None) -> Dict[str, bool]:
        """Train indexes that require training"""
        results = {}
        
        for index_name, vector_store in self.indexes.items():
            try:
                config = self.index_configs[index_name]
                
                # Check if training is required
                if config.index_type in [IndexType.IVF_FLAT, IndexType.IVF_PQ]:
                    self.logger.info(f"Training index {index_name}")
                    self.index_status[index_name] = IndexStatus.TRAINING
                    
                    # Use provided training data or generate sample data
                    if training_data and index_name in training_data:
                        train_vectors = np.array(training_data[index_name])
                    else:
                        # Generate random training data
                        train_vectors = np.random.random((
                            config.training_sample_size,
                            config.dimension
                        )).astype(np.float32)
                    
                    success = await vector_store.train_index(train_vectors)
                    results[index_name] = success
                    
                    if success:
                        self.index_status[index_name] = IndexStatus.READY
                    else:
                        self.index_status[index_name] = IndexStatus.ERROR
                else:
                    results[index_name] = True  # No training required
                    
            except Exception as e:
                self.logger.error(f"Training failed for index {index_name}: {e}")
                results[index_name] = False
                self.index_status[index_name] = IndexStatus.ERROR
        
        return results
    
    async def optimize_indexes(self) -> Dict[str, bool]:
        """Optimize all indexes for better performance"""
        results = {}
        
        for index_name, vector_store in self.indexes.items():
            try:
                self.logger.info(f"Optimizing index {index_name}")
                self.index_status[index_name] = IndexStatus.OPTIMIZING
                
                success = await vector_store.optimize_index()
                results[index_name] = success
                
                if success:
                    self.index_status[index_name] = IndexStatus.READY
                else:
                    self.index_status[index_name] = IndexStatus.ERROR
                    
            except Exception as e:
                self.logger.error(f"Optimization failed for index {index_name}: {e}")
                results[index_name] = False
                self.index_status[index_name] = IndexStatus.ERROR
        
        return results
    
    async def save_indexes(self) -> Dict[str, str]:
        """Save all indexes to disk"""
        results = {}
        
        for index_name, vector_store in self.indexes.items():
            try:
                self.logger.info(f"Saving index {index_name}")
                self.index_status[index_name] = IndexStatus.SAVING
                
                filename = f"{index_name}_{int(time.time())}.index"
                index_path = await vector_store.save_index(filename)
                results[index_name] = index_path
                
                # Save index configuration
                config_path = Path(self.index_configs[index_name].storage_path) / f"{filename}.config"
                with open(config_path, 'w') as f:
                    json.dump(asdict(self.index_configs[index_name]), f, indent=2)
                
                self.index_status[index_name] = IndexStatus.READY
                self.logger.info(f"Index {index_name} saved to {index_path}")
                
            except Exception as e:
                self.logger.error(f"Failed to save index {index_name}: {e}")
                results[index_name] = f"Error: {str(e)}"
                self.index_status[index_name] = IndexStatus.ERROR
        
        return results
    
    async def load_indexes(self, index_files: Dict[str, str]) -> Dict[str, bool]:
        """Load indexes from disk"""
        results = {}
        
        for index_name, filename in index_files.items():
            try:
                self.logger.info(f"Loading index {index_name} from {filename}")
                self.index_status[index_name] = IndexStatus.LOADING
                
                # Load configuration if available
                config_path = Path(filename).with_suffix('.config')
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        config_dict = json.load(f)
                        config = IndexConfiguration(**config_dict)
                        self.index_configs[index_name] = config
                
                # Create vector store with loaded config
                if index_name in self.index_configs:
                    config = self.index_configs[index_name]
                    faiss_config = {
                        'dimension': config.dimension,
                        'index_type': config.index_type.value,
                        'storage_path': config.storage_path
                    }
                    vector_store = FaissVectorStore(faiss_config)
                    
                    # Load the index
                    success = await vector_store.load_index(filename)
                    
                    if success:
                        self.indexes[index_name] = vector_store
                        self.index_status[index_name] = IndexStatus.READY
                        results[index_name] = True
                        self.logger.info(f"Index {index_name} loaded successfully")
                    else:
                        results[index_name] = False
                        self.index_status[index_name] = IndexStatus.ERROR
                else:
                    self.logger.error(f"No configuration found for index {index_name}")
                    results[index_name] = False
                    
            except Exception as e:
                self.logger.error(f"Failed to load index {index_name}: {e}")
                results[index_name] = False
                self.index_status[index_name] = IndexStatus.ERROR
        
        return results
    
    def _get_index_name(self, embedding_type: EmbeddingType) -> str:
        """Get index name for embedding type"""
        return embedding_type.value.replace('_', '_')
    
    async def get_index_info(self, index_name: Optional[str] = None) -> Union[IndexInfo, Dict[str, IndexInfo]]:
        """Get information about indexes"""
        try:
            if index_name:
                # Get info for specific index
                if index_name not in self.indexes:
                    raise ValueError(f"Index {index_name} not found")
                
                return await self._get_single_index_info(index_name)
            else:
                # Get info for all indexes
                info = {}
                for idx_name in self.indexes:
                    info[idx_name] = await self._get_single_index_info(idx_name)
                return info
                
        except Exception as e:
            self.logger.error(f"Failed to get index info: {e}")
            if index_name:
                return IndexInfo(
                    config=self.index_configs.get(index_name),
                    status=IndexStatus.ERROR,
                    vector_count=0,
                    memory_usage_mb=0.0,
                    last_updated="unknown",
                    last_saved="unknown",
                    search_performance_ms=0.0
                )
            else:
                return {}
    
    async def _get_single_index_info(self, index_name: str) -> IndexInfo:
        """Get information for a single index"""
        vector_store = self.indexes[index_name]
        config = self.index_configs[index_name]
        
        # Get stats from vector store
        stats = await vector_store.get_stats()
        
        # Get performance stats
        perf_stats = self.performance_stats.get(index_name, {})
        
        return IndexInfo(
            config=config,
            status=self.index_status.get(index_name, IndexStatus.ERROR),
            vector_count=stats.total_vectors,
            memory_usage_mb=stats.memory_usage_mb,
            last_updated=stats.last_updated,
            last_saved="unknown",  # Would track this separately
            search_performance_ms=perf_stats.get('average_search_time', 0.0) * 1000
        )
    
    async def remove_vector(self, embedding_id: str, index_name: Optional[str] = None) -> bool:
        """Remove a vector from index(es)"""
        try:
            if index_name:
                # Remove from specific index
                if index_name in self.indexes:
                    return await self.indexes[index_name].remove_vector(embedding_id)
                else:
                    return False
            else:
                # Remove from all indexes
                results = []
                for idx_name, vector_store in self.indexes.items():
                    result = await vector_store.remove_vector(embedding_id)
                    results.append(result)
                
                return any(results)  # Return True if removed from at least one index
                
        except Exception as e:
            self.logger.error(f"Failed to remove vector {embedding_id}: {e}")
            return False
    
    async def clear_index(self, index_name: str) -> bool:
        """Clear all vectors from an index"""
        try:
            if index_name not in self.indexes:
                return False
            
            success = await self.indexes[index_name].clear_index()
            
            if success:
                # Reset performance stats
                self.performance_stats[index_name] = {
                    'total_searches': 0,
                    'total_additions': 0,
                    'average_search_time': 0.0,
                    'average_addition_time': 0.0
                }
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to clear index {index_name}: {e}")
            return False
    
    def get_manager_stats(self) -> Dict[str, Any]:
        """Get overall manager statistics"""
        total_vectors = sum(
            self.performance_stats.get(name, {}).get('total_additions', 0)
            for name in self.indexes
        )
        
        total_searches = sum(
            self.performance_stats.get(name, {}).get('total_searches', 0)
            for name in self.indexes
        )
        
        return {
            'total_indexes': len(self.indexes),
            'total_vectors': total_vectors,
            'total_searches': total_searches,
            'index_status': {name: status.value for name, status in self.index_status.items()},
            'performance_stats': self.performance_stats,
            'supported_embedding_types': [e.value for e in EmbeddingType]
        }
    
    def __del__(self):
        """Cleanup resources"""
        if self.auto_save_task:
            self.auto_save_task.cancel()
        
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
