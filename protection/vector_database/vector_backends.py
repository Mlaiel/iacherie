"""🔄 Vector Storage Backends
===========================

Unified interface and implementations for different vector storage backends.
Includes FAISS high-performance implementation and abstract storage interface.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL IMPORTANT ⚠️
=====================================
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et constitue une violation 
des droits d'auteur passible de poursuites judiciaires.

Contact: mlaiel@live.de
"""

import asyncio
import logging
import numpy as np
import pickle
import json
from abc import ABC, abstractmethod
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


# =============================================================================
# STORAGE INTERFACE SECTION
# =============================================================================

class StorageBackend(Enum):
    """Available storage backends"""
    FAISS = "faiss"
    ELASTICSEARCH = "elasticsearch"
    HNSWLIB = "hnswlib"
    ANNOY = "annoy"
    MEMORY = "memory"


@dataclass
class VectorRecord:
    """Record for storing vector with metadata"""
    vector_id: str
    vector: np.ndarray
    metadata: Dict[str, Any]
    timestamp: float
    embedding_type: str


@dataclass
class SearchQuery:
    """Query for vector search"""
    query_vector: np.ndarray
    k: int = 10
    similarity_threshold: Optional[float] = None
    metadata_filters: Optional[Dict[str, Any]] = None
    include_metadata: bool = True
    include_vectors: bool = False


@dataclass
class SearchResultItem:
    """Single search result item"""
    vector_id: str
    similarity_score: float
    distance: float
    metadata: Dict[str, Any]
    vector: Optional[np.ndarray] = None


class VectorStorageInterface(ABC):
    """Abstract interface for vector storage backends"""
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the storage backend"""
        pass
    
    @abstractmethod
    async def add_vector(self, vector_record: VectorRecord) -> bool:
        """Add a single vector to storage"""
        pass
    
    @abstractmethod
    async def add_vectors_batch(self, vector_records: List[VectorRecord]) -> bool:
        """Add multiple vectors to storage"""
        pass
    
    @abstractmethod
    async def search(self, query: SearchQuery) -> List[SearchResultItem]:
        """Search for similar vectors"""
        pass
    
    @abstractmethod
    async def get_vector(self, vector_id: str) -> Optional[VectorRecord]:
        """Get a specific vector by ID"""
        pass
    
    @abstractmethod
    async def remove_vector(self, vector_id: str) -> bool:
        """Remove a vector from storage"""
        pass
    
    @abstractmethod
    async def update_metadata(self, vector_id: str, metadata: Dict[str, Any]) -> bool:
        """Update metadata for a vector"""
        pass
    
    @abstractmethod
    async def get_vector_count(self) -> int:
        """Get total number of vectors in storage"""
        pass
    
    @abstractmethod
    async def save(self, filepath: str) -> bool:
        """Save storage to file"""
        pass
    
    @abstractmethod
    async def load(self, filepath: str) -> bool:
        """Load storage from file"""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all vectors from storage"""
        pass


# =============================================================================
# FAISS IMPLEMENTATION SECTION
# =============================================================================

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
    """Index statistics"""
    total_vectors: int
    index_type: str
    dimension: int
    memory_usage_mb: float
    build_time_seconds: float
    last_update: float


class FAISSVectorStore(VectorStorageInterface):
    """
    High-performance vector database using Facebook AI Similarity Search (FAISS).
    Optimized for real-time similarity search across millions of content fingerprints.
    """
    
    def __init__(self, dimension: int, index_type: IndexType = IndexType.FLAT_L2, **kwargs):
        """
        Initialize FAISS vector store.
        
        Args:
            dimension: Vector dimension
            index_type: Type of FAISS index to use
            **kwargs: Additional configuration options
        """
        if not FAISS_AVAILABLE:
            raise ImportError("FAISS is not available. Please install faiss-cpu or faiss-gpu.")
        
        self.dimension = dimension
        self.index_type = index_type
        self.index = None
        self.id_mapping = {}  # faiss_id -> vector_id
        self.reverse_id_mapping = {}  # vector_id -> faiss_id
        self.metadata_store = {}  # vector_id -> metadata
        self.next_id = 0
        
        # Configuration from kwargs
        self.nlist = kwargs.get('nlist', 100)
        self.m = kwargs.get('pq_m', 8)
        self.nbits = kwargs.get('pq_nbits', 8)
        self.ef_construction = kwargs.get('ef_construction', 200)
        self.ef_search = kwargs.get('ef_search', 50)
        
        # Thread executor for async operations
        self.executor = ThreadPoolExecutor(max_workers=kwargs.get('max_workers', 4))
        
        self.logger = logging.getLogger(f"{__name__}.FAISSVectorStore")
        self.logger.info(f"Initialized FAISS store with dimension={dimension}, type={index_type.value}")
    
    async def initialize(self) -> bool:
        """Initialize the FAISS index"""
        try:
            self.index = self._create_index()
            self.logger.info(f"FAISS index initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize FAISS index: {e}")
            return False
    
    def _create_index(self):
        """Create FAISS index based on type"""
        if self.index_type == IndexType.FLAT_L2:
            return faiss.IndexFlatL2(self.dimension)
        
        elif self.index_type == IndexType.FLAT_IP:
            return faiss.IndexFlatIP(self.dimension)
        
        elif self.index_type == IndexType.IVF_FLAT:
            quantizer = faiss.IndexFlatL2(self.dimension)
            index = faiss.IndexIVFFlat(quantizer, self.dimension, self.nlist)
            return index
        
        elif self.index_type == IndexType.IVF_PQ:
            quantizer = faiss.IndexFlatL2(self.dimension)
            index = faiss.IndexIVFPQ(quantizer, self.dimension, self.nlist, self.m, self.nbits)
            return index
        
        elif self.index_type == IndexType.HNSW:
            index = faiss.IndexHNSWFlat(self.dimension, 32)
            index.hnsw.efConstruction = self.ef_construction
            index.hnsw.efSearch = self.ef_search
            return index
        
        elif self.index_type == IndexType.LSH:
            return faiss.IndexLSH(self.dimension, 256)
        
        else:
            raise ValueError(f"Unsupported index type: {self.index_type}")
    
    async def add_vector(self, vector_record: VectorRecord) -> bool:
        """Add a single vector to the index"""
        try:
            # Prepare vector for FAISS
            vector = vector_record.vector.astype(np.float32)
            if vector.ndim == 1:
                vector = vector.reshape(1, -1)
            
            # Add to FAISS index
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self.executor, self._add_vector_sync, vector)
            
            # Store metadata and mappings
            faiss_id = self.next_id
            self.id_mapping[faiss_id] = vector_record.vector_id
            self.reverse_id_mapping[vector_record.vector_id] = faiss_id
            self.metadata_store[vector_record.vector_id] = vector_record.metadata
            self.next_id += 1
            
            self.logger.debug(f"Added vector {vector_record.vector_id} with FAISS ID {faiss_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add vector {vector_record.vector_id}: {e}")
            return False
    
    def _add_vector_sync(self, vector: np.ndarray):
        """Synchronous vector addition to FAISS"""
        self.index.add(vector)
    
    async def add_vectors_batch(self, vector_records: List[VectorRecord]) -> bool:
        """Add multiple vectors to the index"""
        try:
            # Prepare vectors for batch addition
            vectors = []
            for record in vector_records:
                vector = record.vector.astype(np.float32)
                vectors.append(vector)
            
            # Stack vectors for batch addition
            batch_vectors = np.stack(vectors)
            
            # Add batch to FAISS
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self.executor, self._add_vectors_batch_sync, batch_vectors)
            
            # Store metadata and mappings
            for i, record in enumerate(vector_records):
                faiss_id = self.next_id + i
                self.id_mapping[faiss_id] = record.vector_id
                self.reverse_id_mapping[record.vector_id] = faiss_id
                self.metadata_store[record.vector_id] = record.metadata
            
            self.next_id += len(vector_records)
            
            self.logger.info(f"Added batch of {len(vector_records)} vectors")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add vector batch: {e}")
            return False
    
    def _add_vectors_batch_sync(self, vectors: np.ndarray):
        """Synchronous batch vector addition to FAISS"""
        self.index.add(vectors)
    
    async def search(self, query: SearchQuery) -> List[SearchResultItem]:
        """Search for similar vectors"""
        try:
            # Prepare query vector
            query_vector = query.query_vector.astype(np.float32)
            if query_vector.ndim == 1:
                query_vector = query_vector.reshape(1, -1)
            
            # Perform search
            loop = asyncio.get_event_loop()
            distances, indices = await loop.run_in_executor(
                self.executor, self._search_sync, query_vector, query.k
            )
            
            # Process results
            results = []
            for i, (distance, faiss_id) in enumerate(zip(distances[0], indices[0])):
                if faiss_id == -1:  # No more results
                    break
                
                vector_id = self.id_mapping.get(faiss_id)
                if not vector_id:
                    continue
                
                metadata = self.metadata_store.get(vector_id, {})
                
                # Apply metadata filters
                if query.metadata_filters and not self._matches_filter(metadata, query.metadata_filters):
                    continue
                
                # Calculate similarity score
                if self.index_type == IndexType.FLAT_IP:
                    similarity_score = float(distance)  # IP is already similarity
                else:
                    # Convert L2 distance to similarity (0-1 range)
                    similarity_score = 1.0 / (1.0 + float(distance))
                
                # Apply similarity threshold
                if query.similarity_threshold and similarity_score < query.similarity_threshold:
                    continue
                
                result = SearchResultItem(
                    vector_id=vector_id,
                    similarity_score=similarity_score,
                    distance=float(distance),
                    metadata=metadata if query.include_metadata else {}
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
    
    async def get_vector(self, vector_id: str) -> Optional[VectorRecord]:
        """Get a specific vector by ID"""
        try:
            if vector_id not in self.reverse_id_mapping:
                return None
            
            faiss_id = self.reverse_id_mapping[vector_id]
            metadata = self.metadata_store.get(vector_id, {})
            
            # FAISS doesn't store original vectors efficiently, so we return metadata only
            # In production, you might want to store vectors separately
            return VectorRecord(
                vector_id=vector_id,
                vector=np.array([]),  # Empty array as placeholder
                metadata=metadata,
                timestamp=metadata.get('timestamp', time.time()),
                embedding_type=metadata.get('embedding_type', 'unknown')
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get vector {vector_id}: {e}")
            return None
    
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
                build_time_seconds=0.0,  # Not tracked in this implementation
                last_update=time.time()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get stats: {e}")
            return IndexStats(
                total_vectors=0,
                index_type=self.index_type.value,
                dimension=self.dimension,
                memory_usage_mb=0.0,
                build_time_seconds=0.0,
                last_update=time.time()
            )
    
    async def save(self, filepath: str) -> bool:
        """Save index and metadata to file"""
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Save FAISS index
            index_path = str(filepath.with_suffix('.faiss'))
            await asyncio.get_event_loop().run_in_executor(
                self.executor, faiss.write_index, self.index, index_path
            )
            
            # Save metadata
            metadata_path = str(filepath.with_suffix('.meta'))
            metadata = {
                'id_mapping': self.id_mapping,
                'reverse_id_mapping': self.reverse_id_mapping,
                'metadata_store': self.metadata_store,
                'next_id': self.next_id,
                'dimension': self.dimension,
                'index_type': self.index_type.value
            }
            
            with open(metadata_path, 'wb') as f:
                pickle.dump(metadata, f)
            
            self.logger.info(f"Saved index to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save index: {e}")
            return False
    
    async def load(self, filepath: str) -> bool:
        """Load index and metadata from file"""
        try:
            filepath = Path(filepath)
            
            # Load FAISS index
            index_path = str(filepath.with_suffix('.faiss'))
            if not Path(index_path).exists():
                self.logger.error(f"Index file not found: {index_path}")
                return False
            
            self.index = await asyncio.get_event_loop().run_in_executor(
                self.executor, faiss.read_index, index_path
            )
            
            # Load metadata
            metadata_path = str(filepath.with_suffix('.meta'))
            if not Path(metadata_path).exists():
                self.logger.error(f"Metadata file not found: {metadata_path}")
                return False
            
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
            
            self.id_mapping = metadata['id_mapping']
            self.reverse_id_mapping = metadata['reverse_id_mapping']
            self.metadata_store = metadata['metadata_store']
            self.next_id = metadata['next_id']
            
            # Verify dimension compatibility
            if metadata['dimension'] != self.dimension:
                self.logger.warning(f"Dimension mismatch: expected {self.dimension}, got {metadata['dimension']}")
            
            self.logger.info(f"Loaded index from {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load index: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all vectors from the index"""
        try:
            # Recreate the index
            self.index = self._create_index()
            
            # Clear all mappings and metadata
            self.id_mapping.clear()
            self.reverse_id_mapping.clear()
            self.metadata_store.clear()
            self.next_id = 0
            
            self.logger.info("Cleared all vectors from index")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clear index: {e}")
            return False
    
    def __del__(self):
        """Cleanup thread executor"""
        if hasattr(self, 'executor') and self.executor:
            self.executor.shutdown(wait=False)


class VectorStorageFactory:
    """Factory for creating vector storage instances"""
    
    @staticmethod
    def create_storage(backend: StorageBackend, **kwargs) -> VectorStorageInterface:
        """
        Create a vector storage instance.
        
        Args:
            backend: Storage backend type
            **kwargs: Backend-specific configuration
            
        Returns:
            Vector storage instance
        """
        if backend == StorageBackend.FAISS:
            if not FAISS_AVAILABLE:
                raise ImportError("FAISS is not available")
            
            dimension = kwargs.get('dimension', 512)
            index_type_str = kwargs.get('index_type', 'IndexFlatL2')
            
            # Convert string to enum
            index_type = IndexType.FLAT_L2
            for it in IndexType:
                if it.value == index_type_str:
                    index_type = it
                    break
            
            return FAISSVectorStore(dimension=dimension, index_type=index_type, **kwargs)
        
        elif backend == StorageBackend.MEMORY:
            # Placeholder for in-memory implementation
            raise NotImplementedError("Memory backend not implemented yet")
        
        else:
            raise ValueError(f"Unsupported backend: {backend}")


# Export all classes and functions
__all__ = [
    # Interface classes
    'StorageBackend',
    'VectorRecord',
    'SearchQuery', 
    'SearchResultItem',
    'VectorStorageInterface',
    
    # FAISS implementation
    'IndexType',
    'SearchResult',
    'IndexStats',
    'FAISSVectorStore',
    
    # Factory
    'VectorStorageFactory'
]