"""🔍 FAISS Vector Store
=====================

High-performance vector database using Facebook AI Similarity Search (FAISS).
Optimized for real-time similarity search across millions of content fingerprints.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import numpy as np
import asyncio
import logging
import pickle
import json
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

logger = logging.getLogger(__name__)


class IndexType(Enum):
    """FAISS index types"""
    FLAT_L2 = "IndexFlatL2"
    FLAT_IP = "IndexFlatIP"
    IVF_FLAT = "IndexIVFFlat"
    IVF_PQ = "IndexIVFPQ"
    HNSW = "IndexHNSWFlat"
    LSH = "IndexLSH"


@dataclass
class SearchResult:
    """Vector search result"""
    vector_id: str
    similarity_score: float
    distance: float
    metadata: Dict[str, Any]
    content_id: str
    embedding_type: str


@dataclass
class IndexStats:
    """FAISS index statistics"""
    total_vectors: int
    index_type: str
    dimension: int
    memory_usage_mb: float
    search_time_ms: float
    last_updated: str


class FaissVectorStore:
    """FAISS-based vector storage and search engine"""
    
    def __init__(self, config: Dict[str, Any]):
        if not FAISS_AVAILABLE:
            raise ImportError("FAISS is required but not available")
        
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.FaissVectorStore")
        
        # Configuration
        self.dimension = config.get('dimension', 512)
        self.index_type = IndexType(config.get('index_type', 'IndexFlatL2'))
        self.storage_path = Path(config.get('storage_path', './data/faiss'))
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # FAISS parameters
        self.nlist = config.get('nlist', 100)  # Number of clusters for IVF
        self.m = config.get('pq_m', 8)  # Number of subquantizers for PQ
        self.nbits = config.get('pq_nbits', 8)  # Bits per subquantizer
        self.ef_construction = config.get('ef_construction', 200)  # HNSW construction parameter
        self.ef_search = config.get('ef_search', 50)  # HNSW search parameter
        
        # Index and metadata storage
        self.index = None
        self.metadata_store = {}  # vector_id -> metadata mapping
        self.id_mapping = {}  # faiss_id -> vector_id mapping
        self.reverse_id_mapping = {}  # vector_id -> faiss_id mapping
        self.next_id = 0
        
        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=config.get('max_workers', 4))
        
        self._initialize_index()
        self.logger.info(f"FaissVectorStore initialized with {self.index_type.value}")
    
    def _initialize_index(self):
        """Initialize FAISS index based on configuration"""
        try:
            if self.index_type == IndexType.FLAT_L2:
                self.index = faiss.IndexFlatL2(self.dimension)
            elif self.index_type == IndexType.FLAT_IP:
                self.index = faiss.IndexFlatIP(self.dimension)
            elif self.index_type == IndexType.IVF_FLAT:
                quantizer = faiss.IndexFlatL2(self.dimension)
                self.index = faiss.IndexIVFFlat(quantizer, self.dimension, self.nlist)
            elif self.index_type == IndexType.IVF_PQ:
                quantizer = faiss.IndexFlatL2(self.dimension)
                self.index = faiss.IndexIVFPQ(quantizer, self.dimension, self.nlist, self.m, self.nbits)
            elif self.index_type == IndexType.HNSW:
                self.index = faiss.IndexHNSWFlat(self.dimension, 32)  # M=32 connections
                self.index.hnsw.efConstruction = self.ef_construction
                self.index.hnsw.efSearch = self.ef_search
            elif self.index_type == IndexType.LSH:
                self.index = faiss.IndexLSH(self.dimension, self.dimension // 8)
            else:
                raise ValueError(f"Unsupported index type: {self.index_type}")
            
            # Add ID mapping for indexes that support it
            if hasattr(self.index, 'make_direct_map'):
                self.index.make_direct_map()
            
            self.logger.info(f"Initialized {self.index_type.value} index with dimension {self.dimension}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize FAISS index: {e}")
            raise
    
    async def add_vector(
        self,
        vector_id: str,
        vector: np.ndarray,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add a vector to the index"""
        try:
            # Validate vector
            if vector.shape[0] != self.dimension:
                raise ValueError(f"Vector dimension {vector.shape[0]} doesn't match index dimension {self.dimension}")
            
            # Normalize vector for IP indexes
            if self.index_type == IndexType.FLAT_IP:
                vector = vector / np.linalg.norm(vector)
            
            # Add to FAISS index
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                self._add_vector_sync,
                vector_id,
                vector.reshape(1, -1).astype(np.float32),
                metadata or {}
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add vector {vector_id}: {e}")
            return False
    
    def _add_vector_sync(self, vector_id: str, vector: np.ndarray, metadata: Dict[str, Any]):
        """Synchronous vector addition"""
        faiss_id = self.next_id
        
        # Add to FAISS index
        self.index.add(vector)
        
        # Update mappings
        self.id_mapping[faiss_id] = vector_id
        self.reverse_id_mapping[vector_id] = faiss_id
        self.metadata_store[vector_id] = {
            'faiss_id': faiss_id,
            'added_at': time.time(),
            **metadata
        }
        
        self.next_id += 1
    
    async def add_vectors_batch(
        self,
        vectors_data: List[Tuple[str, np.ndarray, Optional[Dict[str, Any]]]]
    ) -> List[bool]:
        """Add multiple vectors in batch"""
        try:
            # Validate all vectors first
            for vector_id, vector, _ in vectors_data:
                if vector.shape[0] != self.dimension:
                    raise ValueError(f"Vector {vector_id} dimension mismatch")
            
            # Prepare batch data
            vectors = []
            vector_ids = []
            metadatas = []
            
            for vector_id, vector, metadata in vectors_data:
                # Normalize for IP indexes
                if self.index_type == IndexType.FLAT_IP:
                    vector = vector / np.linalg.norm(vector)
                
                vectors.append(vector)
                vector_ids.append(vector_id)
                metadatas.append(metadata or {})
            
            # Convert to numpy array
            vectors_array = np.array(vectors, dtype=np.float32)
            
            # Add to index
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                self._add_vectors_batch_sync,
                vector_ids,
                vectors_array,
                metadatas
            )
            
            return [True] * len(vectors_data)
            
        except Exception as e:
            self.logger.error(f"Batch vector addition failed: {e}")
            return [False] * len(vectors_data)
    
    def _add_vectors_batch_sync(
        self,
        vector_ids: List[str],
        vectors: np.ndarray,
        metadatas: List[Dict[str, Any]]
    ):
        """Synchronous batch vector addition"""
        start_id = self.next_id
        
        # Add to FAISS index
        self.index.add(vectors)
        
        # Update mappings
        for i, vector_id in enumerate(vector_ids):
            faiss_id = start_id + i
            self.id_mapping[faiss_id] = vector_id
            self.reverse_id_mapping[vector_id] = faiss_id
            self.metadata_store[vector_id] = {
                'faiss_id': faiss_id,
                'added_at': time.time(),
                **metadatas[i]
            }
        
        self.next_id += len(vector_ids)
    
    async def search(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        similarity_threshold: Optional[float] = None,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar vectors"""
        try:
            # Validate query vector
            if query_vector.shape[0] != self.dimension:
                raise ValueError(f"Query vector dimension mismatch")
            
            # Normalize for IP indexes
            if self.index_type == IndexType.FLAT_IP:
                query_vector = query_vector / np.linalg.norm(query_vector)
            
            # Perform search
            loop = asyncio.get_event_loop()
            distances, indices = await loop.run_in_executor(
                self.executor,
                self._search_sync,
                query_vector.reshape(1, -1).astype(np.float32),
                k
            )
            
            # Process results
            results = []
            for i, (distance, faiss_id) in enumerate(zip(distances[0], indices[0])):
                if faiss_id == -1:  # Invalid result
                    continue
                
                # Get vector ID and metadata
                if faiss_id in self.id_mapping:
                    vector_id = self.id_mapping[faiss_id]
                    metadata = self.metadata_store.get(vector_id, {})
                    
                    # Apply metadata filter
                    if metadata_filter and not self._matches_filter(metadata, metadata_filter):
                        continue
                    
                    # Convert distance to similarity score
                    if self.index_type == IndexType.FLAT_IP:
                        similarity_score = float(distance)  # IP is already similarity
                    else:
                        # Convert L2 distance to similarity (0-1 range)
                        similarity_score = 1.0 / (1.0 + float(distance))
                    
                    # Apply similarity threshold
                    if similarity_threshold and similarity_score < similarity_threshold:
                        continue
                    
                    result = SearchResult(
                        vector_id=vector_id,
                        similarity_score=similarity_score,
                        distance=float(distance),
                        metadata=metadata,
                        content_id=metadata.get('content_id', vector_id),
                        embedding_type=metadata.get('embedding_type', 'unknown')
                    )
                    results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Vector search failed: {e}")
            return []
    
    def _search_sync(self, query_vector: np.ndarray, k: int) -> Tuple[np.ndarray, np.ndarray]:
        """Synchronous vector search"""
        return self.index.search(query_vector, k)
    
    def _matches_filter(self, metadata: Dict[str, Any], filter_criteria: Dict[str, Any]) -> bool:
        """Check if metadata matches filter criteria"""
        for key, value in filter_criteria.items():
            if key not in metadata:
                return False
            
            if isinstance(value, list):
                if metadata[key] not in value:
                    return False
            elif metadata[key] != value:
                return False
        
        return True
    
    async def remove_vector(self, vector_id: str) -> bool:
        """Remove a vector from the index"""
        try:
            if vector_id not in self.reverse_id_mapping:
                self.logger.warning(f"Vector {vector_id} not found in index")
                return False
            
            # FAISS doesn't support efficient removal, so we mark as deleted
            # In production, you'd implement periodic index rebuilding
            faiss_id = self.reverse_id_mapping[vector_id]
            
            # Remove from mappings
            del self.id_mapping[faiss_id]
            del self.reverse_id_mapping[vector_id]
            del self.metadata_store[vector_id]
            
            self.logger.info(f"Marked vector {vector_id} for deletion")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove vector {vector_id}: {e}")
            return False
    
    async def update_metadata(self, vector_id: str, metadata: Dict[str, Any]) -> bool:
        """Update metadata for a vector"""
        try:
            if vector_id not in self.metadata_store:
                return False
            
            self.metadata_store[vector_id].update(metadata)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update metadata for {vector_id}: {e}")
            return False
    
    async def get_vector_count(self) -> int:
        """Get total number of vectors in index"""
        return self.index.ntotal if self.index else 0
    
    async def get_stats(self) -> IndexStats:
        """Get index statistics"""
        try:
            # Calculate memory usage (approximate)
            if hasattr(self.index, 'sa_encode'):
                # For PQ indexes
                memory_mb = (self.index.ntotal * self.m * self.nbits / 8) / (1024 * 1024)
            else:
                # For flat indexes
                memory_mb = (self.index.ntotal * self.dimension * 4) / (1024 * 1024)  # 4 bytes per float
            
            return IndexStats(
                total_vectors=self.index.ntotal,
                index_type=self.index_type.value,
                dimension=self.dimension,
                memory_usage_mb=memory_mb,
                search_time_ms=0.0,  # Would be measured during actual searches
                last_updated=time.strftime('%Y-%m-%d %H:%M:%S')
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get stats: {e}")
            return IndexStats(0, self.index_type.value, self.dimension, 0.0, 0.0, "unknown")
    
    async def save_index(self, filename: Optional[str] = None) -> str:
        """Save index to disk"""
        try:
            if filename is None:
                filename = f"faiss_index_{self.index_type.value}_{self.dimension}d.index"
            
            index_path = self.storage_path / filename
            metadata_path = self.storage_path / f"{filename}.metadata"
            
            # Save FAISS index
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                faiss.write_index,
                self.index,
                str(index_path)
            )
            
            # Save metadata and mappings
            metadata_dict = {
                'metadata_store': self.metadata_store,
                'id_mapping': self.id_mapping,
                'reverse_id_mapping': self.reverse_id_mapping,
                'next_id': self.next_id,
                'config': self.config
            }
            
            with open(metadata_path, 'wb') as f:
                pickle.dump(metadata_dict, f)
            
            self.logger.info(f"Index saved to {index_path}")
            return str(index_path)
            
        except Exception as e:
            self.logger.error(f"Failed to save index: {e}")
            raise
    
    async def load_index(self, filename: str) -> bool:
        """Load index from disk"""
        try:
            index_path = self.storage_path / filename
            metadata_path = self.storage_path / f"{filename}.metadata"
            
            if not index_path.exists() or not metadata_path.exists():
                self.logger.error(f"Index files not found: {index_path}")
                return False
            
            # Load FAISS index
            loop = asyncio.get_event_loop()
            self.index = await loop.run_in_executor(
                self.executor,
                faiss.read_index,
                str(index_path)
            )
            
            # Load metadata and mappings
            with open(metadata_path, 'rb') as f:
                metadata_dict = pickle.load(f)
            
            self.metadata_store = metadata_dict['metadata_store']
            self.id_mapping = metadata_dict['id_mapping']
            self.reverse_id_mapping = metadata_dict['reverse_id_mapping']
            self.next_id = metadata_dict['next_id']
            
            self.logger.info(f"Index loaded from {index_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load index: {e}")
            return False
    
    async def train_index(self, training_vectors: np.ndarray) -> bool:
        """Train index (required for some index types like IVF)"""
        try:
            if not self.index.is_trained:
                self.logger.info(f"Training {self.index_type.value} index with {len(training_vectors)} vectors")
                
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    self.executor,
                    self.index.train,
                    training_vectors.astype(np.float32)
                )
                
                self.logger.info("Index training completed")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Index training failed: {e}")
            return False
    
    async def optimize_index(self) -> bool:
        """Optimize index for better performance"""
        try:
            # For IVF indexes, set search parameters
            if self.index_type in [IndexType.IVF_FLAT, IndexType.IVF_PQ]:
                # Set number of clusters to search
                nprobe = min(self.nlist, max(1, self.nlist // 4))
                self.index.nprobe = nprobe
                self.logger.info(f"Set nprobe to {nprobe} for IVF index")
            
            # For HNSW indexes, set search parameters
            elif self.index_type == IndexType.HNSW:
                self.index.hnsw.efSearch = self.ef_search
                self.logger.info(f"Set efSearch to {self.ef_search} for HNSW index")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Index optimization failed: {e}")
            return False
    
    async def clear_index(self) -> bool:
        """Clear all vectors from index"""
        try:
            # Reinitialize index
            self._initialize_index()
            
            # Clear metadata
            self.metadata_store.clear()
            self.id_mapping.clear()
            self.reverse_id_mapping.clear()
            self.next_id = 0
            
            self.logger.info("Index cleared successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clear index: {e}")
            return False
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
