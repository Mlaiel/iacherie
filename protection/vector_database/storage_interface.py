"""🔄 Vector Storage Interface
===========================

Unified interface for different vector storage backends.
Abstracts storage implementation details and provides consistent API.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class StorageBackend(Enum):
    """Available storage backends"""    FAISS = "faiss"
    ELASTICSEARCH = "elasticsearch"
    HNSWLIB = "hnswlib"
    ANNOY = "annoy"
    MEMORY = "memory"


@dataclass
class VectorRecord:
    """Record for storing vector with metadata"""    vector_id: str
    vector: np.ndarray
    metadata: Dict[str, Any]
    timestamp: float
    embedding_type: str


@dataclass
class SearchQuery:
    """Query for vector search"""    query_vector: np.ndarray
    k: int = 10
    similarity_threshold: Optional[float] = None
    metadata_filters: Optional[Dict[str, Any]] = None
    include_metadata: bool = True
    include_vectors: bool = False


@dataclass
class SearchResultItem:
    """Single search result item"""    vector_id: str
    similarity_score: float
    distance: float
    metadata: Dict[str, Any]
    vector: Optional[np.ndarray] = None


class VectorStorageInterface(ABC):
    """Abstract interface for vector storage backends"""    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the storage backend"""        pass
    
    @abstractmethod
    async def add_vector(self, record: VectorRecord) -> bool:
        """Add a single vector record"""        pass
    
    @abstractmethod
    async def add_vectors_batch(self, records: List[VectorRecord]) -> List[bool]:
        """Add multiple vector records in batch"""        pass
    
    @abstractmethod
    async def search(self, query: SearchQuery) -> List[SearchResultItem]:
        """Search for similar vectors"""        pass
    
    @abstractmethod
    async def get_vector(self, vector_id: str) -> Optional[VectorRecord]:
        """Get a specific vector by ID"""        pass
    
    @abstractmethod
    async def update_metadata(self, vector_id: str, metadata: Dict[str, Any]) -> bool:
        """Update metadata for a vector"""        pass
    
    @abstractmethod
    async def remove_vector(self, vector_id: str) -> bool:
        """Remove a vector"""        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""        pass
    
    @abstractmethod
    async def save(self, path: str) -> bool:
        """Save storage to disk"""        pass
    
    @abstractmethod
    async def load(self, path: str) -> bool:
        """Load storage from disk"""        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all vectors"""        pass


class MemoryVectorStorage(VectorStorageInterface):
    """In-memory vector storage implementation"""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.MemoryVectorStorage")
        
        # Storage
        self.vectors: Dict[str, VectorRecord] = {}
        self.dimension = None
        self.total_searches = 0
        self.total_additions = 0
        
        # Configuration
        self.max_vectors = config.get('max_vectors', 100000)
        self.similarity_metric = config.get('similarity_metric', 'cosine')
    
    async def initialize(self) -> bool:
        """Initialize memory storage"""        try:
            self.logger.info("Initializing memory vector storage")
            return True
        except Exception as e:
            self.logger.error(f"Memory storage initialization failed: {e}")
            return False
    
    async def add_vector(self, record: VectorRecord) -> bool:
        """Add a single vector record"""        try:
            if len(self.vectors) >= self.max_vectors:
                self.logger.warning(f"Maximum vector limit ({self.max_vectors}) reached")
                return False
            
            # Set dimension on first vector
            if self.dimension is None:
                self.dimension = len(record.vector)
            elif len(record.vector) != self.dimension:
                self.logger.error(f"Vector dimension mismatch: expected {self.dimension}, got {len(record.vector)}")
                return False
            
            self.vectors[record.vector_id] = record
            self.total_additions += 1
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add vector {record.vector_id}: {e}")
            return False
    
    async def add_vectors_batch(self, records: List[VectorRecord]) -> List[bool]:
        """Add multiple vector records in batch"""        results = []
        
        for record in records:
            result = await self.add_vector(record)
            results.append(result)
        
        return results
    
    async def search(self, query: SearchQuery) -> List[SearchResultItem]:
        """Search for similar vectors"""        try:
            self.total_searches += 1
            
            if not self.vectors:
                return []
            
            # Calculate similarities
            results = []
            
            for vector_id, record in self.vectors.items():
                # Apply metadata filters
                if query.metadata_filters:
                    if not self._matches_filters(record.metadata, query.metadata_filters):
                        continue
                
                # Calculate similarity
                similarity = self._calculate_similarity(query.query_vector, record.vector)
                
                # Apply similarity threshold
                if query.similarity_threshold and similarity < query.similarity_threshold:
                    continue
                
                # Calculate distance (inverse of similarity for consistency)
                distance = 1.0 - similarity
                
                result_item = SearchResultItem(
                    vector_id=vector_id,
                    similarity_score=similarity,
                    distance=distance,
                    metadata=record.metadata if query.include_metadata else {},
                    vector=record.vector if query.include_vectors else None
                )
                results.append(result_item)
            
            # Sort by similarity score (descending)
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            
            # Limit results
            return results[:query.k]
            
        except Exception as e:
            self.logger.error(f"Memory search failed: {e}")
            return []
    
    def _calculate_similarity(self, vector1: np.ndarray, vector2: np.ndarray) -> float:
        """Calculate similarity between two vectors"""        try:
            if self.similarity_metric == 'cosine':
                # Cosine similarity
                dot_product = np.dot(vector1, vector2)
                norm1 = np.linalg.norm(vector1)
                norm2 = np.linalg.norm(vector2)
                
                if norm1 == 0 or norm2 == 0:
                    return 0.0
                
                return dot_product / (norm1 * norm2)
            
            elif self.similarity_metric == 'euclidean':
                # Euclidean distance converted to similarity
                distance = np.linalg.norm(vector1 - vector2)
                max_distance = np.linalg.norm(vector1) + np.linalg.norm(vector2)
                return 1.0 - (distance / (max_distance + 1e-8))
            
            else:
                # Default to cosine
                return self._calculate_similarity(vector1, vector2)
                
        except Exception:
            return 0.0
    
    def _matches_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if metadata matches filters"""        for key, value in filters.items():
            if key not in metadata:
                return False
            
            if isinstance(value, list):
                if metadata[key] not in value:
                    return False
            elif metadata[key] != value:
                return False
        
        return True
    
    async def get_vector(self, vector_id: str) -> Optional[VectorRecord]:
        """Get a specific vector by ID"""        return self.vectors.get(vector_id)
    
    async def update_metadata(self, vector_id: str, metadata: Dict[str, Any]) -> bool:
        """Update metadata for a vector"""        try:
            if vector_id not in self.vectors:
                return False
            
            self.vectors[vector_id].metadata.update(metadata)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update metadata for {vector_id}: {e}")
            return False
    
    async def remove_vector(self, vector_id: str) -> bool:
        """Remove a vector"""        try:
            if vector_id in self.vectors:
                del self.vectors[vector_id]
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to remove vector {vector_id}: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""        memory_usage = sum(
            record.vector.nbytes + len(str(record.metadata))
            for record in self.vectors.values()
        )
        
        return {
            'backend': 'memory',
            'total_vectors': len(self.vectors),
            'dimension': self.dimension,
            'memory_usage_bytes': memory_usage,
            'memory_usage_mb': memory_usage / (1024 * 1024),
            'total_searches': self.total_searches,
            'total_additions': self.total_additions,
            'max_vectors': self.max_vectors,
            'similarity_metric': self.similarity_metric
        }
    
    async def save(self, path: str) -> bool:
        """Save storage to disk"""        try:
            import pickle
            
            with open(path, 'wb') as f:
                pickle.dump({
                    'vectors': self.vectors,
                    'dimension': self.dimension,
                    'total_searches': self.total_searches,
                    'total_additions': self.total_additions,
                    'config': self.config
                }, f)
            
            self.logger.info(f"Memory storage saved to {path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save memory storage: {e}")
            return False
    
    async def load(self, path: str) -> bool:
        """Load storage from disk"""        try:
            import pickle
            
            with open(path, 'rb') as f:
                data = pickle.load(f)
            
            self.vectors = data['vectors']
            self.dimension = data['dimension']
            self.total_searches = data.get('total_searches', 0)
            self.total_additions = data.get('total_additions', 0)
            
            self.logger.info(f"Memory storage loaded from {path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load memory storage: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all vectors"""        try:
            self.vectors.clear()
            self.dimension = None
            self.total_searches = 0
            self.total_additions = 0
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clear memory storage: {e}")
            return False


class VectorStorageFactory:
    """Factory for creating vector storage instances"""    
    @staticmethod
    def create_storage(backend: StorageBackend, config: Dict[str, Any]) -> VectorStorageInterface:
        """Create a vector storage instance"""        
        if backend == StorageBackend.MEMORY:
            return MemoryVectorStorage(config)
        
        elif backend == StorageBackend.FAISS:
            try:
                from .faiss_storage_adapter import FaissStorageAdapter
                return FaissStorageAdapter(config)
            except ImportError:
                logger.warning("FAISS not available, falling back to memory storage")
                return MemoryVectorStorage(config)
        
        elif backend == StorageBackend.ELASTICSEARCH:
            try:
                from .elasticsearch_storage_adapter import ElasticsearchStorageAdapter
                return ElasticsearchStorageAdapter(config)
            except ImportError:
                logger.warning("Elasticsearch not available, falling back to memory storage")
                return MemoryVectorStorage(config)
        
        else:
            logger.warning(f"Unsupported backend {backend}, falling back to memory storage")
            return MemoryVectorStorage(config)


class VectorStorageManager:
    """Manager for multiple vector storage backends"""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.VectorStorageManager")
        
        # Storage instances
        self.storages: Dict[str, VectorStorageInterface] = {}
        
        # Default backend
        self.default_backend = StorageBackend(config.get('default_backend', 'memory'))
    
    async def create_storage(
        self,
        storage_name: str,
        backend: Optional[StorageBackend] = None,
        storage_config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Create a new storage instance"""        try:
            backend = backend or self.default_backend
            config = storage_config or self.config.get('storage_configs', {}).get(storage_name, {})
            
            storage = VectorStorageFactory.create_storage(backend, config)
            
            if await storage.initialize():
                self.storages[storage_name] = storage
                self.logger.info(f"Created storage '{storage_name}' with backend '{backend.value}'")
                return True
            else:
                self.logger.error(f"Failed to initialize storage '{storage_name}'")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to create storage '{storage_name}': {e}")
            return False
    
    def get_storage(self, storage_name: str) -> Optional[VectorStorageInterface]:
        """Get a storage instance"""        return self.storages.get(storage_name)
    
    async def route_operation(
        self,
        operation: str,
        storage_name: Optional[str] = None,
        **kwargs
    ) -> Any:
        """Route operation to appropriate storage"""        try:
            # Use specified storage or default
            if storage_name and storage_name in self.storages:
                storage = self.storages[storage_name]
            elif self.storages:
                storage = next(iter(self.storages.values()))  # Use first available
            else:
                self.logger.error("No storage instances available")
                return None
            
            # Route operation
            if operation == 'add_vector':
                return await storage.add_vector(kwargs['record'])
            elif operation == 'add_vectors_batch':
                return await storage.add_vectors_batch(kwargs['records'])
            elif operation == 'search':
                return await storage.search(kwargs['query'])
            elif operation == 'get_vector':
                return await storage.get_vector(kwargs['vector_id'])
            elif operation == 'update_metadata':
                return await storage.update_metadata(kwargs['vector_id'], kwargs['metadata'])
            elif operation == 'remove_vector':
                return await storage.remove_vector(kwargs['vector_id'])
            elif operation == 'get_stats':
                return await storage.get_stats()
            elif operation == 'save':
                return await storage.save(kwargs['path'])
            elif operation == 'load':
                return await storage.load(kwargs['path'])
            elif operation == 'clear':
                return await storage.clear()
            else:
                self.logger.error(f"Unknown operation: {operation}")
                return None
                
        except Exception as e:
            self.logger.error(f"Operation '{operation}' failed: {e}")
            return None
    
    def list_storages(self) -> List[str]:
        """List available storage instances"""        return list(self.storages.keys())
    
    async def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all storages"""        stats = {}
        
        for name, storage in self.storages.items():
            try:
                stats[name] = await storage.get_stats()
            except Exception as e:
                stats[name] = {'error': str(e)}
        
        return stats
    
    async def remove_storage(self, storage_name: str) -> bool:
        """Remove a storage instance"""        try:
            if storage_name in self.storages:
                del self.storages[storage_name]
                self.logger.info(f"Removed storage '{storage_name}'")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to remove storage '{storage_name}': {e}")
            return False
