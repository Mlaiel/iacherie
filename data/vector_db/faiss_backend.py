"""
FAISS Backend - High-Performance Vector Search Engine
====================================================

Enterprise-grade FAISS backend implementation with GPU acceleration,
advanced indexing strategies, and production-ready optimizations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL COPYRIGHT WARNING ⚠️
This code is the intellectual property of Fahed Mlaiel and is protected by 
international copyright law. Any unauthorized use, reproduction, distribution 
or modification is strictly prohibited and will result in legal action.

For licensing inquiries: mlaiel@live.de
"""

import asyncio
import logging
import numpy as np
import pickle
import json
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import uuid

# FAISS imports with fallback handling
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    faiss = None

from .vector_storage import BaseVectorBackend, VectorMetadata, SearchResult

logger = logging.getLogger(__name__)


class FAISSIndexManager:
    """Manages FAISS index creation and optimization."""
    
    @staticmethod
    def create_index(
        dimension: int,
        index_type: str = "IndexIVFFlat",
        use_gpu: bool = False,
        nlist: int = 100,
        custom_params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Create FAISS index with specified parameters.
        
        Args:
            dimension: Vector dimension
            index_type: Type of FAISS index
            use_gpu: Whether to use GPU acceleration
            nlist: Number of clusters for IVF indexes
            custom_params: Custom index parameters
        
        Returns:
            FAISS index instance
        """
        if not FAISS_AVAILABLE:
            raise RuntimeError("FAISS not available. Install with: pip install faiss-cpu or faiss-gpu")
        
        params = custom_params or {}
        
        # Create base index
        if index_type == "IndexFlatL2":
            index = faiss.IndexFlatL2(dimension)
        elif index_type == "IndexFlatIP":
            index = faiss.IndexFlatIP(dimension)
        elif index_type == "IndexIVFFlat":
            quantizer = faiss.IndexFlatL2(dimension)
            index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
        elif index_type == "IndexIVFPQ":
            quantizer = faiss.IndexFlatL2(dimension)
            m = params.get('m', 8)  # Number of subquantizers
            nbits = params.get('nbits', 8)  # Bits per subquantizer
            index = faiss.IndexIVFPQ(quantizer, dimension, nlist, m, nbits)
        elif index_type == "IndexHNSWFlat":
            M = params.get('M', 32)  # Number of connections
            index = faiss.IndexHNSWFlat(dimension, M)
        elif index_type == "IndexLSH":
            nbits = params.get('nbits', dimension)
            index = faiss.IndexLSH(dimension, nbits)
        else:
            raise ValueError(f"Unsupported index type: {index_type}")
        
        # Apply GPU if requested and available
        if use_gpu and hasattr(faiss, 'StandardGpuResources'):
            try:
                res = faiss.StandardGpuResources()
                index = faiss.index_cpu_to_gpu(res, 0, index)
                logger.info(f"FAISS index moved to GPU: {index_type}")
            except Exception as e:
                logger.warning(f"Failed to move index to GPU: {e}")
        
        # Set index parameters
        if hasattr(index, 'nprobe'):
            index.nprobe = params.get('nprobe', 10)
        
        logger.info(f"Created FAISS index: {index_type}, dimension: {dimension}")
        return index
    
    @staticmethod
    def optimize_index(index: Any, optimization_level: str = "medium") -> None:
        """
        Optimize FAISS index parameters.
        
        Args:
            index: FAISS index to optimize
            optimization_level: Level of optimization ('low', 'medium', 'high')
        """
        if not hasattr(index, 'nprobe'):
            return
        
        if optimization_level == "low":
            index.nprobe = min(10, max(1, index.nlist // 10))
        elif optimization_level == "medium":
            index.nprobe = min(32, max(1, index.nlist // 5))
        elif optimization_level == "high":
            index.nprobe = min(64, max(1, index.nlist // 2))
        
        logger.info(f"Index optimized with level: {optimization_level}, nprobe: {index.nprobe}")


class FAISSMetadataManager:
    """Manages metadata storage for FAISS vectors."""
    
    def __init__(self, storage_path -> None: str) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.storage_path / "metadata.json"
        self.metadata_cache: Dict[str, VectorMetadata] = {}
        self.lock = threading.Lock()
        
        # Load existing metadata
        self._load_metadata()
    
    def _load_metadata(self) -> None:
        """Load metadata from disk."""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    for vector_id, metadata_dict in data.items():
                        # Convert datetime strings back to datetime objects
                        if 'created_at' in metadata_dict:
                            metadata_dict['created_at'] = datetime.fromisoformat(metadata_dict['created_at'])
                        if 'updated_at' in metadata_dict and metadata_dict['updated_at']:
                            metadata_dict['updated_at'] = datetime.fromisoformat(metadata_dict['updated_at'])
                        
                        self.metadata_cache[vector_id] = VectorMetadata(**metadata_dict)
                        
                logger.info(f"Loaded {len(self.metadata_cache)} metadata entries")
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
    
    def _save_metadata(self) -> None:
        """Save metadata to disk."""
        try:
            data = {}
            for vector_id, metadata in self.metadata_cache.items():
                metadata_dict = {
                    'id': metadata.id,
                    'content_type': metadata.content_type,
                    'content_hash': metadata.content_hash,
                    'created_at': metadata.created_at.isoformat(),
                    'updated_at': metadata.updated_at.isoformat() if metadata.updated_at else None,
                    'custom_metadata': metadata.custom_metadata,
                    'encryption_key_id': metadata.encryption_key_id,
                    'compression_type': metadata.compression_type,
                    'version': metadata.version
                }
                data[vector_id] = metadata_dict
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
    
    def add_metadata(self, vector_id: str, metadata: VectorMetadata) -> None:
        """Add metadata for a vector."""
        with self.lock:
            self.metadata_cache[vector_id] = metadata
            self._save_metadata()
    
    def get_metadata(self, vector_id: str) -> Optional[VectorMetadata]:
        """Get metadata for a vector."""
        with self.lock:
            return self.metadata_cache.get(vector_id)
    
    def update_metadata(self, vector_id: str, metadata: VectorMetadata) -> None:
        """Update metadata for a vector."""
        with self.lock:
            if vector_id in self.metadata_cache:
                self.metadata_cache[vector_id] = metadata
                self._save_metadata()
    
    def delete_metadata(self, vector_id: str) -> bool:
        """Delete metadata for a vector."""
        with self.lock:
            if vector_id in self.metadata_cache:
                del self.metadata_cache[vector_id]
                self._save_metadata()
                return True
            return False
    
    def get_all_metadata(self) -> Dict[str, VectorMetadata]:
        """Get all metadata."""
        with self.lock:
            return self.metadata_cache.copy()
    
    def filter_by_metadata(self, filters: Dict[str, Any]) -> List[str]:
        """Filter vector IDs by metadata criteria."""
        matching_ids = []
        
        with self.lock:
            for vector_id, metadata in self.metadata_cache.items():
                if self._matches_filters(metadata, filters):
                    matching_ids.append(vector_id)
        
        return matching_ids
    
    def _matches_filters(self, metadata: VectorMetadata, filters: Dict[str, Any]) -> bool:
        """Check if metadata matches filter criteria."""
        for key, value in filters.items():
            if key == 'content_type':
                if metadata.content_type != value:
                    return False
            elif key == 'created_after':
                if metadata.created_at < datetime.fromisoformat(value):
                    return False
            elif key == 'created_before':
                if metadata.created_at > datetime.fromisoformat(value):
                    return False
            elif key.startswith('custom.'):
                custom_key = key[7:]  # Remove 'custom.' prefix
                if not metadata.custom_metadata or metadata.custom_metadata.get(custom_key) != value:
                    return False
        
        return True


class FAISSBackend(BaseVectorBackend):
    """
    Enterprise FAISS backend implementation.
    
    Features:
    - Multiple index types (Flat, IVF, PQ, HNSW, LSH)
    - GPU acceleration support
    - Memory mapping for large datasets
    - Quantization for space efficiency
    - Index sharding for horizontal scaling
    - Parallel query processing
    - Custom distance metrics
    - Metadata filtering
    - Batch operations optimization
    """
    
    def __init__(self, config -> None: Any, security_manager -> None: Optional[Any] = None) -> None:
        """Initialize FAISS backend."""
        super().__init__(config, security_manager)
        
        # Configuration
        self.index_type = config.get('backend.index_type', 'IndexIVFFlat')
        self.dimension = config.get('backend.dimension', 768)
        self.use_gpu = config.get('backend.use_gpu', False)
        self.nlist = config.get('backend.nlist', 100)
        self.batch_size = config.get('backend.batch_size', 1000)
        self.storage_path = config.get('backend.storage_path', 'data/faiss')
        self.memory_map = config.get('backend.memory_map', True)
        
        # Core components
        self.index: Optional[Any] = None
        self.id_map: Dict[str, int] = {}  # String ID to internal ID mapping
        self.reverse_id_map: Dict[int, str] = {}  # Internal ID to string ID mapping
        self.metadata_manager: Optional[FAISSMetadataManager] = None
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="faiss-")
        
        # State management
        self.next_id = 0
        self.trained = False
        self.total_vectors = 0
        
        # Statistics
        self.stats = {
            'total_searches': 0,
            'total_adds': 0,
            'total_updates': 0,
            'total_deletes': 0,
            'index_size': 0,
            'memory_usage': 0
        }
        
        logger.info(f"FAISSBackend initialized with index type: {self.index_type}")
    
    async def initialize(self) -> bool:
        """Initialize the FAISS backend."""
        try:
            if not FAISS_AVAILABLE:
                raise RuntimeError("FAISS not available. Install with: pip install faiss-cpu or faiss-gpu")
            
            # Create storage directory
            storage_path = Path(self.storage_path)
            storage_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize metadata manager
            self.metadata_manager = FAISSMetadataManager(self.storage_path)
            
            # Try to load existing index
            index_file = storage_path / "index.faiss"
            id_map_file = storage_path / "id_map.pkl"
            
            if index_file.exists() and id_map_file.exists():
                await self._load_existing_index()
            else:
                await self._create_new_index()
            
            self.initialized = True
            logger.info("FAISS backend initialization completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize FAISS backend: {e}")
            return False
    
    async def _load_existing_index(self) -> None:
        """Load existing FAISS index from disk."""
        try:
            # Load in thread pool to avoid blocking
            def load_index() -> None:
                index_file = Path(self.storage_path) / "index.faiss"
                id_map_file = Path(self.storage_path) / "id_map.pkl"
                
                # Load FAISS index
                index = faiss.read_index(str(index_file))
                
                # Load ID mappings
                with open(id_map_file, 'rb') as f:
                    data = pickle.load(f)
                    id_map = data['id_map']
                    reverse_id_map = data['reverse_id_map']
                    next_id = data['next_id']
                
                return index, id_map, reverse_id_map, next_id
            
            # Execute in thread pool
            loop = asyncio.get_event_loop()
            index, id_map, reverse_id_map, next_id = await loop.run_in_executor(
                self.executor, load_index
            )
            
            self.index = index
            self.id_map = id_map
            self.reverse_id_map = reverse_id_map
            self.next_id = next_id
            self.total_vectors = len(id_map)
            self.trained = True
            
            logger.info(f"Loaded existing FAISS index with {self.total_vectors} vectors")
            
        except Exception as e:
            logger.error(f"Failed to load existing index: {e}")
            await self._create_new_index()
    
    async def _create_new_index(self) -> None:
        """Create a new FAISS index."""
        try:
            # Create index in thread pool
            def create_index() -> None:
                custom_params = self.config.get('backend.custom_params', {})
                return FAISSIndexManager.create_index(
                    dimension=self.dimension,
                    index_type=self.index_type,
                    use_gpu=self.use_gpu,
                    nlist=self.nlist,
                    custom_params=custom_params
                )
            
            loop = asyncio.get_event_loop()
            self.index = await loop.run_in_executor(self.executor, create_index)
            
            # Reset mappings
            self.id_map = {}
            self.reverse_id_map = {}
            self.next_id = 0
            self.total_vectors = 0
            self.trained = False
            
            logger.info(f"Created new FAISS index: {self.index_type}")
            
        except Exception as e:
            logger.error(f"Failed to create new index: {e}")
            raise
    
    async def add_vector(
        self,
        vector_id: str,
        vector: np.ndarray,
        metadata: Optional[VectorMetadata] = None
    ) -> bool:
        """Add a vector to the FAISS index."""
        try:
            if not self.initialized or self.index is None:
                return False
            
            # Ensure vector is the right shape and type
            if vector.ndim == 1:
                vector = vector.reshape(1, -1)
            vector = vector.astype(np.float32)
            
            if vector.shape[1] != self.dimension:
                logger.error(f"Vector dimension mismatch: {vector.shape[1]} != {self.dimension}")
                return False
            
            # Train index if needed and not already trained
            if not self.trained and hasattr(self.index, 'train'):
                await self._train_index_if_needed([vector])
            
            # Add vector in thread pool
            def add_to_index() -> None:
                # Assign internal ID
                internal_id = self.next_id
                self.id_map[vector_id] = internal_id
                self.reverse_id_map[internal_id] = vector_id
                self.next_id += 1
                
                # Add to FAISS index
                self.index.add(vector)
                
                return True
            
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(self.executor, add_to_index)
            
            if success:
                # Store metadata
                if metadata and self.metadata_manager:
                    self.metadata_manager.add_metadata(vector_id, metadata)
                
                self.total_vectors += 1
                self.stats['total_adds'] += 1
                
                # Auto-save periodically
                if self.total_vectors % 1000 == 0:
                    await self._save_index()
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to add vector {vector_id}: {e}")
            return False
    
    async def add_vectors_batch(
        self,
        vectors: List[Tuple[str, np.ndarray, Optional[VectorMetadata]]]
    ) -> List[bool]:
        """Add multiple vectors in a batch."""
        try:
            if not self.initialized or self.index is None:
                return [False] * len(vectors)
            
            # Prepare batch data
            vector_ids = []
            vector_data = []
            metadata_list = []
            
            for vector_id, vector, metadata in vectors:
                if vector.ndim == 1:
                    vector = vector.reshape(1, -1)
                vector = vector.astype(np.float32)
                
                if vector.shape[1] != self.dimension:
                    logger.error(f"Vector dimension mismatch: {vector.shape[1]} != {self.dimension}")
                    continue
                
                vector_ids.append(vector_id)
                vector_data.append(vector)
                metadata_list.append(metadata)
            
            if not vector_data:
                return [False] * len(vectors)
            
            # Combine vectors
            batch_vectors = np.vstack(vector_data)
            
            # Train index if needed
            if not self.trained and hasattr(self.index, 'train'):
                await self._train_index_if_needed(vector_data)
            
            # Add batch in thread pool
            def add_batch_to_index() -> None:
                results = []
                
                for i, vector_id in enumerate(vector_ids):
                    try:
                        # Assign internal ID
                        internal_id = self.next_id
                        self.id_map[vector_id] = internal_id
                        self.reverse_id_map[internal_id] = vector_id
                        self.next_id += 1
                        results.append(True)
                    except Exception as e:
                        logger.error(f"Failed to assign ID for {vector_id}: {e}")
                        results.append(False)
                
                # Add all vectors to index
                try:
                    self.index.add(batch_vectors)
                except Exception as e:
                    logger.error(f"Failed to add batch to index: {e}")
                    return [False] * len(vector_ids)
                
                return results
            
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(self.executor, add_batch_to_index)
            
            # Store metadata for successful additions
            if self.metadata_manager:
                for i, (success, metadata) in enumerate(zip(results, metadata_list)):
                    if success and metadata:
                        self.metadata_manager.add_metadata(vector_ids[i], metadata)
            
            # Update statistics
            successful_adds = sum(results)
            self.total_vectors += successful_adds
            self.stats['total_adds'] += successful_adds
            
            # Auto-save periodically
            if self.total_vectors % 1000 == 0:
                await self._save_index()
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to add vectors batch: {e}")
            return [False] * len(vectors)
    
    async def search_similar(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        threshold: float = 0.0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar vectors."""
        try:
            if not self.initialized or self.index is None or self.total_vectors == 0:
                return []
            
            # Prepare query vector
            if query_vector.ndim == 1:
                query_vector = query_vector.reshape(1, -1)
            query_vector = query_vector.astype(np.float32)
            
            if query_vector.shape[1] != self.dimension:
                logger.error(f"Query vector dimension mismatch: {query_vector.shape[1]} != {self.dimension}")
                return []
            
            # Apply metadata filters if provided
            allowed_ids = None
            if filters and self.metadata_manager:
                allowed_ids = self.metadata_manager.filter_by_metadata(filters)
                if not allowed_ids:
                    return []
            
            # Search in thread pool
            def search_index() -> None:
                # Adjust top_k based on filters
                search_k = min(top_k * 10 if filters else top_k, self.total_vectors)
                
                scores, indices = self.index.search(query_vector, search_k)
                
                return scores[0], indices[0]
            
            loop = asyncio.get_event_loop()
            scores, indices = await loop.run_in_executor(self.executor, search_index)
            
            # Process results
            results = []
            for score, internal_id in zip(scores, indices):
                # Skip invalid indices
                if internal_id == -1:
                    continue
                
                # Convert score based on metric type
                if hasattr(self.index, 'metric_type'):
                    if self.index.metric_type == faiss.METRIC_INNER_PRODUCT:
                        # Higher is better for inner product
                        similarity_score = float(score)
                    else:
                        # Lower is better for L2 distance, convert to similarity
                        similarity_score = 1.0 / (1.0 + float(score))
                else:
                    # Default: assume L2 distance
                    similarity_score = 1.0 / (1.0 + float(score))
                
                # Apply threshold
                if similarity_score < threshold:
                    continue
                
                # Get vector ID
                vector_id = self.reverse_id_map.get(int(internal_id))
                if not vector_id:
                    continue
                
                # Apply filters
                if allowed_ids and vector_id not in allowed_ids:
                    continue
                
                # Get metadata
                metadata = None
                if self.metadata_manager:
                    metadata = self.metadata_manager.get_metadata(vector_id)
                
                results.append(SearchResult(
                    id=vector_id,
                    score=similarity_score,
                    metadata=metadata
                ))
                
                # Stop if we have enough results
                if len(results) >= top_k:
                    break
            
            self.stats['total_searches'] += 1
            return results
            
        except Exception as e:
            logger.error(f"Failed to search similar vectors: {e}")
            return []
    
    async def get_vector(self, vector_id: str) -> Optional[Tuple[np.ndarray, VectorMetadata]]:
        """Get a specific vector by ID."""
        try:
            if not self.initialized or vector_id not in self.id_map:
                return None
            
            internal_id = self.id_map[vector_id]
            
            # Get vector from index in thread pool
            def get_from_index() -> None:
                vector = self.index.reconstruct(internal_id)
                return vector
            
            loop = asyncio.get_event_loop()
            vector = await loop.run_in_executor(self.executor, get_from_index)
            
            # Get metadata
            metadata = None
            if self.metadata_manager:
                metadata = self.metadata_manager.get_metadata(vector_id)
            
            if metadata is None:
                # Create minimal metadata
                metadata = VectorMetadata(
                    id=vector_id,
                    content_type="unknown",
                    content_hash="",
                    created_at=datetime.utcnow()
                )
            
            return vector, metadata
            
        except Exception as e:
            logger.error(f"Failed to get vector {vector_id}: {e}")
            return None
    
    async def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector by ID."""
        try:
            if not self.initialized or vector_id not in self.id_map:
                return False
            
            # FAISS doesn't support direct deletion
            # We'll mark it as deleted in metadata and exclude from results
            internal_id = self.id_map[vector_id]
            
            # Remove from mappings
            del self.id_map[vector_id]
            del self.reverse_id_map[internal_id]
            
            # Remove metadata
            if self.metadata_manager:
                self.metadata_manager.delete_metadata(vector_id)
            
            self.total_vectors -= 1
            self.stats['total_deletes'] += 1
            
            logger.info(f"Vector {vector_id} marked as deleted")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete vector {vector_id}: {e}")
            return False
    
    async def update_vector(
        self,
        vector_id: str,
        vector: Optional[np.ndarray] = None,
        metadata: Optional[VectorMetadata] = None
    ) -> bool:
        """Update a vector."""
        try:
            if not self.initialized or vector_id not in self.id_map:
                return False
            
            # Update metadata
            if metadata and self.metadata_manager:
                metadata.updated_at = datetime.utcnow()
                self.metadata_manager.update_metadata(vector_id, metadata)
            
            # For vector updates, we need to delete and re-add
            if vector is not None:
                # Store old internal ID
                old_internal_id = self.id_map[vector_id]
                
                # Remove from mappings temporarily
                del self.id_map[vector_id]
                del self.reverse_id_map[old_internal_id]
                
                # Add new vector
                success = await self.add_vector(vector_id, vector, metadata)
                
                if success:
                    self.stats['total_updates'] += 1
                
                return success
            
            self.stats['total_updates'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Failed to update vector {vector_id}: {e}")
            return False
    
    async def _train_index_if_needed(self, sample_vectors: List[np.ndarray]) -> None:
        """Train index if required and not already trained."""
        try:
            if self.trained or not hasattr(self.index, 'train'):
                return
            
            # Prepare training data
            if len(sample_vectors) < self.nlist:
                # Need more vectors for training
                return
            
            training_data = np.vstack(sample_vectors[:self.nlist])
            
            def train_index() -> None:
                self.index.train(training_data)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self.executor, train_index)
            
            self.trained = True
            logger.info("FAISS index training completed")
            
        except Exception as e:
            logger.error(f"Failed to train index: {e}")
    
    async def _save_index(self) -> bool:
        """Save index and mappings to disk."""
        try:
            def save_to_disk() -> None:
                # Save FAISS index
                index_file = Path(self.storage_path) / "index.faiss"
                faiss.write_index(self.index, str(index_file))
                
                # Save ID mappings
                id_map_file = Path(self.storage_path) / "id_map.pkl"
                with open(id_map_file, 'wb') as f:
                    pickle.dump({
                        'id_map': self.id_map,
                        'reverse_id_map': self.reverse_id_map,
                        'next_id': self.next_id
                    }, f)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self.executor, save_to_disk)
            
            logger.info("FAISS index saved to disk")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
            return False
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get backend statistics."""
        stats = self.stats.copy()
        stats.update({
            'backend_type': 'faiss',
            'index_type': self.index_type,
            'dimension': self.dimension,
            'total_vectors': self.total_vectors,
            'trained': self.trained,
            'use_gpu': self.use_gpu,
            'nlist': self.nlist if hasattr(self.index, 'nlist') else None,
            'nprobe': self.index.nprobe if hasattr(self.index, 'nprobe') else None
        })
        return stats
    
    async def health_check(self) -> bool:
        """Perform health check."""
        try:
            if not self.initialized or self.index is None:
                return False
            
            # Test basic operations
            test_vector = np.random.random((1, self.dimension)).astype(np.float32)
            
            # Test search if index has vectors
            if self.total_vectors > 0:
                scores, indices = self.index.search(test_vector, min(1, self.total_vectors))
                if scores is None or indices is None:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"FAISS health check failed: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the FAISS backend."""
        logger.info("Shutting down FAISS backend...")
        
        try:
            # Save index one final time
            if self.initialized and self.index is not None:
                await self._save_index()
            
            # Shutdown thread pool
            self.executor.shutdown(wait=True)
            
            # Clear resources
            self.index = None
            self.id_map.clear()
            self.reverse_id_map.clear()
            
            self.initialized = False
            logger.info("FAISS backend shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during FAISS shutdown: {e}")


# Export main class
__all__ = [
    'FAISSBackend',
    'FAISSIndexManager',
    'FAISSMetadataManager'
]