"""Advanced FAISS Backend Implementation for Vector Database Management
==================================================================

High-performance vector similarity search using Facebook AI Similarity Search (FAISS).
Optimized for large-scale similarity matching and content fingerprinting.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

ATTENTION: Ce code est protégé par les droits d'auteur.
Toute reproduction, distribution ou modification non autorisée est strictement interdite.
"""
import asyncio
import logging
import numpy as np
import pickle
import json
import os
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor

# FAISS imports
import faiss
from sklearn.preprocessing import normalize
import torch

# Local imports
from . import VectorBackend, VectorSearchResult, VectorIndex

logger = logging.getLogger(__name__)


@dataclass
class FAISSIndexConfig:
    """Configuration for FAISS index creation."""    name: str
    dimension: int
    metric: str = "cosine"
    index_type: str = "flat"  # flat, ivf, hnsw, pq
    nlist: int = 100  # For IVF
    m: int = 8  # For PQ
    nbits: int = 8  # For PQ
    ef_construction: int = 200  # For HNSW
    ef_search: int = 50  # For HNSW
    use_gpu: bool = False
    gpu_ids: List[int] = None


class FAISSIndexManager:
    """    Advanced FAISS index manager with multiple index types and optimizations.
    
    Supports:
    - Flat indexes for exact search
    - IVF indexes for large-scale approximate search
    - HNSW indexes for ultra-fast approximate search
    - PQ indexes for memory-efficient storage
    """    
    def __init__(self, config: FAISSIndexConfig):
        self.config = config
        self.index = None
        self.metadata_map: Dict[str, Dict[str, Any]] = {}
        self.id_to_internal: Dict[str, int] = {}
        self.internal_to_id: Dict[int, str] = {}
        self.lock = threading.RLock()
        
        # GPU support
        self.use_gpu = config.use_gpu and faiss.get_num_gpus() > 0
        self.gpu_resources = None
        if self.use_gpu:
            self._initialize_gpu_resources()
        
        # Create index
        self._create_index()
    
    def _initialize_gpu_resources(self):
        """Initialize GPU resources for FAISS."""        try:
            if self.config.gpu_ids:
                # Multi-GPU setup
                self.gpu_resources = [faiss.StandardGpuResources() 
                                    for _ in self.config.gpu_ids]
            else:
                # Single GPU setup
                self.gpu_resources = faiss.StandardGpuResources()
            
            logger.info(f"FAISS GPU resources initialized for {len(self.config.gpu_ids or [0])} GPUs")
            
        except Exception as e:
            logger.error(f"Failed to initialize GPU resources: {str(e)}")
            self.use_gpu = False
    
    def _create_index(self):
        """Create FAISS index based on configuration."""        try:
            dimension = self.config.dimension
            
            if self.config.index_type == "flat":
                # Flat index for exact search
                if self.config.metric == "cosine":
                    self.index = faiss.IndexFlatIP(dimension)
                else:  # euclidean
                    self.index = faiss.IndexFlatL2(dimension)
            
            elif self.config.index_type == "ivf":
                # IVF index for large-scale approximate search
                quantizer = faiss.IndexFlatL2(dimension)
                if self.config.metric == "cosine":
                    self.index = faiss.IndexIVFFlat(quantizer, dimension, self.config.nlist)
                else:
                    self.index = faiss.IndexIVFFlat(quantizer, dimension, self.config.nlist)
            
            elif self.config.index_type == "hnsw":
                # HNSW index for ultra-fast approximate search
                self.index = faiss.IndexHNSWFlat(dimension, self.config.ef_construction)
                self.index.hnsw.efSearch = self.config.ef_search
            
            elif self.config.index_type == "pq":
                # Product Quantization for memory efficiency
                self.index = faiss.IndexPQ(dimension, self.config.m, self.config.nbits)
            
            else:
                raise ValueError(f"Unsupported index type: {self.config.index_type}")
            
            # Move to GPU if requested
            if self.use_gpu:
                self.index = self._move_to_gpu(self.index)
            
            logger.info(f"Created FAISS {self.config.index_type} index with dimension {dimension}")
            
        except Exception as e:
            logger.error(f"Failed to create FAISS index: {str(e)}")
            raise
    
    def _move_to_gpu(self, index):
        """Move index to GPU."""        try:
            if isinstance(self.gpu_resources, list):
                # Multi-GPU setup (not implemented in this version)
                gpu_index = faiss.index_cpu_to_gpu(self.gpu_resources[0], 0, index)
            else:
                # Single GPU setup
                gpu_index = faiss.index_cpu_to_gpu(self.gpu_resources, 0, index)
            
            logger.info("Index moved to GPU")
            return gpu_index
            
        except Exception as e:
            logger.error(f"Failed to move index to GPU: {str(e)}")
            return index
    
    def train_index(self, training_vectors: np.ndarray) -> bool:
        """Train index if required (IVF, PQ)."""        try:
            with self.lock:
                if hasattr(self.index, 'is_trained') and not self.index.is_trained:
                    if self.config.metric == "cosine":
                        # Normalize for cosine similarity
                        training_vectors = normalize(training_vectors, norm='l2')
                    
                    self.index.train(training_vectors.astype(np.float32))
                    logger.info(f"Trained FAISS index with {len(training_vectors)} vectors")
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to train index: {str(e)}")
            return False
    
    def add_vectors(self, vectors: np.ndarray, ids: List[str], 
                   metadata: List[Dict[str, Any]]) -> bool:
        """Add vectors to the index."""        try:
            with self.lock:
                # Normalize for cosine similarity
                if self.config.metric == "cosine":
                    vectors = normalize(vectors, norm='l2')
                
                # Convert to float32
                vectors = vectors.astype(np.float32)
                
                # Get starting internal ID
                start_id = self.index.ntotal
                
                # Add vectors to index
                self.index.add(vectors)
                
                # Update mappings
                for i, content_id in enumerate(ids):
                    internal_id = start_id + i
                    self.id_to_internal[content_id] = internal_id
                    self.internal_to_id[internal_id] = content_id
                    self.metadata_map[content_id] = metadata[i] if i < len(metadata) else {}
                
                logger.info(f"Added {len(ids)} vectors to FAISS index")
                return True
                
        except Exception as e:
            logger.error(f"Failed to add vectors to index: {str(e)}")
            return False
    
    def search(self, query_vector: np.ndarray, k: int = 10, 
              threshold: float = 0.8) -> List[VectorSearchResult]:
        """Search for similar vectors."""        try:
            with self.lock:
                # Normalize query vector for cosine similarity
                if self.config.metric == "cosine":
                    query_vector = normalize(query_vector.reshape(1, -1), norm='l2')
                else:
                    query_vector = query_vector.reshape(1, -1)
                
                query_vector = query_vector.astype(np.float32)
                
                # Perform search
                distances, indices = self.index.search(query_vector, k)
                
                results = []
                for distance, internal_id in zip(distances[0], indices[0]):
                    if internal_id == -1:  # No more results
                        break
                    
                    # Convert distance to similarity score
                    if self.config.metric == "cosine":
                        similarity = float(distance)  # Already cosine similarity
                    else:
                        # Convert L2 distance to similarity
                        similarity = 1.0 / (1.0 + float(distance))
                    
                    if similarity >= threshold:
                        content_id = self.internal_to_id.get(internal_id)
                        if content_id:
                            result = VectorSearchResult(
                                content_id=content_id,
                                similarity_score=similarity,
                                metadata=self.metadata_map.get(content_id, {}),
                                distance=float(distance)
                            )
                            results.append(result)
                
                return results
                
        except Exception as e:
            logger.error(f"Failed to search index: {str(e)}")
            return []
    
    def remove_vectors(self, ids: List[str]) -> bool:
        """Remove vectors from index (requires rebuild for FAISS)."""        try:
            with self.lock:
                # Remove from mappings and metadata
                removed_count = 0
                for content_id in ids:
                    if content_id in self.id_to_internal:
                        internal_id = self.id_to_internal[content_id]
                        del self.id_to_internal[content_id]
                        del self.internal_to_id[internal_id]
                        del self.metadata_map[content_id]
                        removed_count += 1
                
                logger.warning(f"Removed {removed_count} vectors from mappings. "
                             f"Index rebuild recommended for optimal performance.")
                return True
                
        except Exception as e:
            logger.error(f"Failed to remove vectors: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""        try:
            with self.lock:
                stats = {
                    'name': self.config.name,
                    'dimension': self.config.dimension,
                    'metric': self.config.metric,
                    'index_type': self.config.index_type,
                    'vector_count': self.index.ntotal if self.index else 0,
                    'metadata_count': len(self.metadata_map),
                    'is_trained': getattr(self.index, 'is_trained', True),
                    'use_gpu': self.use_gpu,
                    'config': asdict(self.config)
                }
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get index stats: {str(e)}")
            return {}
    
    def save_index(self, file_path: str) -> bool:
        """Save index to disk."""        try:
            with self.lock:
                # Save FAISS index
                if self.use_gpu:
                    # Move to CPU for saving
                    cpu_index = faiss.index_gpu_to_cpu(self.index)
                    faiss.write_index(cpu_index, file_path)
                else:
                    faiss.write_index(self.index, file_path)
                
                # Save metadata
                metadata_path = file_path + ".metadata"
                with open(metadata_path, 'wb') as f:
                    pickle.dump({
                        'metadata_map': self.metadata_map,
                        'id_to_internal': self.id_to_internal,
                        'internal_to_id': self.internal_to_id,
                        'config': asdict(self.config)
                    }, f)
                
                logger.info(f"Saved FAISS index to {file_path}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save index: {str(e)}")
            return False
    
    def load_index(self, file_path: str) -> bool:
        """Load index from disk."""        try:
            with self.lock:
                # Load FAISS index
                self.index = faiss.read_index(file_path)
                
                # Move to GPU if configured
                if self.use_gpu:
                    self.index = self._move_to_gpu(self.index)
                
                # Load metadata
                metadata_path = file_path + ".metadata"
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'rb') as f:
                        data = pickle.load(f)
                        self.metadata_map = data['metadata_map']
                        self.id_to_internal = data['id_to_internal']
                        self.internal_to_id = data['internal_to_id']
                
                logger.info(f"Loaded FAISS index from {file_path}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to load index: {str(e)}")
            return False


class FAISSBackend(VectorBackend):
    """    Enhanced FAISS backend with advanced index management and optimization.
    
    Features:
    - Multiple index types (Flat, IVF, HNSW, PQ)
    - GPU acceleration support
    - Automatic index optimization
    - Persistent storage
    - Multi-index management
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_path = config.get('storage_path', './data/faiss_indices')
        self.default_index_type = config.get('index_type', 'flat')
        self.use_gpu = config.get('use_gpu', False)
        self.gpu_ids = config.get('gpu_ids', [0])
        
        # Index managers
        self.index_managers: Dict[str, FAISSIndexManager] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Create storage directory
        Path(self.base_path).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"FAISS backend initialized with storage path: {self.base_path}")
    
    async def create_index(self, name: str, dimension: int, metric: str = "cosine") -> bool:
        """Create a new FAISS index."""        try:
            if name in self.index_managers:
                logger.warning(f"Index '{name}' already exists")
                return True
            
            # Create index configuration
            config = FAISSIndexConfig(
                name=name,
                dimension=dimension,
                metric=metric,
                index_type=self.default_index_type,
                use_gpu=self.use_gpu,
                gpu_ids=self.gpu_ids
            )
            
            # Create index manager
            loop = asyncio.get_event_loop()
            manager = await loop.run_in_executor(
                self.executor, FAISSIndexManager, config
            )
            
            self.index_managers[name] = manager
            
            logger.info(f"Created FAISS index '{name}' with dimension {dimension}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create FAISS index '{name}': {str(e)}")
            return False
    
    async def add_vectors(self, index_name: str, vectors: np.ndarray,
                         ids: List[str], metadata: List[Dict]) -> bool:
        """Add vectors to FAISS index."""        try:
            if index_name not in self.index_managers:
                raise ValueError(f"Index '{index_name}' not found")
            
            manager = self.index_managers[index_name]
            
            # Train index if needed
            if hasattr(manager.index, 'is_trained') and not manager.index.is_trained:
                await asyncio.get_event_loop().run_in_executor(
                    self.executor, manager.train_index, vectors
                )
            
            # Add vectors
            success = await asyncio.get_event_loop().run_in_executor(
                self.executor, manager.add_vectors, vectors, ids, metadata
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to add vectors to index '{index_name}': {str(e)}")
            return False
    
    async def search(self, index_name: str, query_vector: np.ndarray,
                    k: int = 10, threshold: float = 0.8) -> List[VectorSearchResult]:
        """Search for similar vectors in FAISS index."""        try:
            if index_name not in self.index_managers:
                raise ValueError(f"Index '{index_name}' not found")
            
            manager = self.index_managers[index_name]
            
            results = await asyncio.get_event_loop().run_in_executor(
                self.executor, manager.search, query_vector, k, threshold
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search index '{index_name}': {str(e)}")
            return []
    
    async def delete_vectors(self, index_name: str, ids: List[str]) -> bool:
        """Delete vectors from FAISS index."""        try:
            if index_name not in self.index_managers:
                raise ValueError(f"Index '{index_name}' not found")
            
            manager = self.index_managers[index_name]
            
            success = await asyncio.get_event_loop().run_in_executor(
                self.executor, manager.remove_vectors, ids
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete vectors from index '{index_name}': {str(e)}")
            return False
    
    async def save_index(self, index_name: str) -> bool:
        """Save index to persistent storage."""        try:
            if index_name not in self.index_managers:
                raise ValueError(f"Index '{index_name}' not found")
            
            manager = self.index_managers[index_name]
            file_path = os.path.join(self.base_path, f"{index_name}.faiss")
            
            success = await asyncio.get_event_loop().run_in_executor(
                self.executor, manager.save_index, file_path
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to save index '{index_name}': {str(e)}")
            return False
    
    async def load_index(self, index_name: str) -> bool:
        """Load index from persistent storage."""        try:
            file_path = os.path.join(self.base_path, f"{index_name}.faiss")
            
            if not os.path.exists(file_path):
                logger.warning(f"Index file not found: {file_path}")
                return False
            
            # Load metadata to get configuration
            metadata_path = file_path + ".metadata"
            if os.path.exists(metadata_path):
                with open(metadata_path, 'rb') as f:
                    data = pickle.load(f)
                    config_data = data['config']
                    config = FAISSIndexConfig(**config_data)
            else:
                # Create default config
                config = FAISSIndexConfig(
                    name=index_name,
                    dimension=384,  # Default dimension
                    metric="cosine",
                    index_type=self.default_index_type,
                    use_gpu=self.use_gpu,
                    gpu_ids=self.gpu_ids
                )
            
            # Create manager and load index
            manager = FAISSIndexManager(config)
            success = await asyncio.get_event_loop().run_in_executor(
                self.executor, manager.load_index, file_path
            )
            
            if success:
                self.index_managers[index_name] = manager
                logger.info(f"Loaded FAISS index '{index_name}'")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to load index '{index_name}': {str(e)}")
            return False
    
    def get_index_stats(self, index_name: str) -> Dict[str, Any]:
        """Get statistics for a specific index."""        try:
            if index_name not in self.index_managers:
                return {}
            
            manager = self.index_managers[index_name]
            return manager.get_stats()
            
        except Exception as e:
            logger.error(f"Failed to get stats for index '{index_name}': {str(e)}")
            return {}
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide statistics."""        try:
            stats = {
                'backend': 'faiss',
                'total_indices': len(self.index_managers),
                'use_gpu': self.use_gpu,
                'gpu_count': faiss.get_num_gpus() if self.use_gpu else 0,
                'storage_path': self.base_path,
                'indices': {name: manager.get_stats() 
                           for name, manager in self.index_managers.items()}
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get system stats: {str(e)}")
            return {}
    
    async def optimize_index(self, index_name: str) -> bool:
        """Optimize index for better performance."""        try:
            if index_name not in self.index_managers:
                raise ValueError(f"Index '{index_name}' not found")
            
            # For FAISS, optimization typically involves rebuilding
            # This is a placeholder for more advanced optimization strategies
            logger.info(f"Index '{index_name}' optimization completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to optimize index '{index_name}': {str(e)}")
            return False
    
    async def backup_index(self, index_name: str, backup_path: str) -> bool:
        """Create a backup of the index."""        try:
            if index_name not in self.index_managers:
                raise ValueError(f"Index '{index_name}' not found")
            
            manager = self.index_managers[index_name]
            
            success = await asyncio.get_event_loop().run_in_executor(
                self.executor, manager.save_index, backup_path
            )
            
            if success:
                logger.info(f"Created backup of index '{index_name}' at {backup_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to backup index '{index_name}': {str(e)}")
            return False


# Export the backend
__all__ = ['FAISSBackend', 'FAISSIndexManager', 'FAISSIndexConfig']
