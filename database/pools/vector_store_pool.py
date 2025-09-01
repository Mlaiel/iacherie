"""Vector Store Connection Pool - IA Influencer Agent + Content Protection Platform

Enterprise vector database connection pool for content fingerprinting,
similarity search, and AI-powered content matching.

Supported Vector Stores:
- FAISS: High-performance similarity search
- Pinecone: Managed vector database service  
- Qdrant: Open-source vector database
- Weaviate: Knowledge graph vector database
- Milvus: Distributed vector database

Vector Operations:
- Content fingerprint storage and retrieval
- Similarity search for content protection
- Real-time content matching
- Multi-modal embeddings (audio, video, image, text)
- Batch processing for large datasets
- Vector clustering and analysis

Content Protection Features:
- Audio fingerprint similarity matching
- Video frame similarity detection
- Image perceptual hashing comparison
- Text semantic similarity analysis
- Cross-platform content identification
- Real-time protection monitoring

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import pickle
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import json
import hashlib

try:
    import faiss
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    import pinecone
    import qdrant_client
    from qdrant_client.http import models
    from qdrant_client.http.models import Distance, VectorParams
    import weaviate
except ImportError as e:
    logging.warning(f"Vector store dependency missing: {e}")

from .manager import IConnectionPool, PoolConfig, DatabaseConnectionInfo, ConnectionState

logger = logging.getLogger(__name__)

# =============== VECTOR STORE CONFIGURATION ===============

@dataclass
class VectorStoreConfig(PoolConfig):
    """Vector store configuration"""
    # Vector dimensions
    vector_dimension: int = 512
    distance_metric: str = "cosine"  # cosine, euclidean, inner_product
    
    # FAISS specific
    faiss_index_type: str = "IndexFlatIP"  # IndexFlatIP, IndexIVFFlat, IndexHNSW
    faiss_nlist: int = 100  # For IVF indices
    faiss_m: int = 16  # For HNSW indices
    faiss_ef_construction: int = 200
    faiss_ef_search: int = 64
    
    # Index management
    index_persist_path: str = "/tmp/vector_indices"
    auto_save_interval: int = 300  # seconds
    batch_size: int = 1000
    
    # Performance tuning
    use_gpu: bool = False
    gpu_device_id: int = 0
    num_threads: int = 4
    
    # Similarity search
    default_top_k: int = 100
    similarity_threshold: float = 0.8
    enable_reranking: bool = True
    
    # Content types
    supported_content_types: List[str] = None

# =============== VECTOR STORE INTERFACES ===============

class IVectorStore:
    """Interface for vector stores"""
    
    async def add_vectors(self, vectors: np.ndarray, metadata: List[Dict[str, Any]], 
                         ids: Optional[List[str]] = None) -> bool:
        """
Add vectors to the store"""
        try:
            if self.index is None:
                # Initialize index with first vectors
                dimension = vectors.shape[1]
                if self.config.index_type == "IVFFlat":
                    quantizer = faiss.IndexFlatIP(dimension) if self.config.similarity_metric == "cosine" else faiss.IndexFlatL2(dimension)
                    self.index = faiss.IndexIVFFlat(quantizer, dimension, self.config.nlist)
                    if vectors.shape[0] >= self.config.nlist:
                        self.index.train(vectors.astype(np.float32))
                else:
                    self.index = faiss.IndexFlatIP(dimension) if self.config.similarity_metric == "cosine" else faiss.IndexFlatL2(dimension)
            
            # Add vectors to index
            start_idx = self.next_id
            vector_ids = ids or [f"{self.store_name}_{start_idx + i}" for i in range(len(vectors))]
            
            self.index.add(vectors.astype(np.float32))
            
            # Update metadata and mappings
            for i, (vector_id, meta) in enumerate(zip(vector_ids, metadata)):
                index_id = start_idx + i
                self.metadata_store[index_id] = meta
                self.id_to_index[vector_id] = index_id
                self.index_to_id[index_id] = vector_id
            
            self.next_id += len(vectors)
            self.stats["total_vectors"] = self.next_id
            
            logger.info(f"✅ Added {len(vectors)} vectors to FAISS store {self.store_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add vectors to FAISS store: {e}")
            return False
    
    async def search_similar(self, query_vector: np.ndarray, top_k: int = 100, 
                           filter_criteria: Optional[Dict] = None) -> List[Tuple[str, float, Dict]]:
        """Search for similar vectors"""
        start_time = time.time()
        
        try:
            if self.index is None or self.index.ntotal == 0:
                return []
            
            # Perform similarity search
            query_vector = query_vector.reshape(1, -1).astype(np.float32)
            distances, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
            
            # Convert results
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx == -1:  # FAISS returns -1 for invalid indices
                    continue
                    
                vector_id = self.index_to_id.get(idx)
                if vector_id is None:
                    continue
                    
                metadata = self.metadata_store.get(idx, {})
                
                # Apply filters if specified
                if filter_criteria:
                    if not self._matches_filter(metadata, filter_criteria):
                        continue
                
                results.append((vector_id, float(dist), metadata))
            
            # Update statistics
            search_time = time.time() - start_time
            self.stats["total_searches"] += 1
            self.stats["avg_search_time"] = (
                (self.stats["avg_search_time"] * (self.stats["total_searches"] - 1) + search_time) /
                self.stats["total_searches"]
            )
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Vector search failed: {e}")
            return []
    
    def _matches_filter(self, metadata: Dict[str, Any], filter_criteria: Dict) -> bool:
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
    
    async def delete_vectors(self, ids: List[str]) -> bool:
        """
Delete vectors by IDs"""
        try:
            # FAISS doesn't support deletion, so we mark as deleted in metadata
            deleted_count = 0
            for vector_id in ids:
                index_id = self.id_to_index.get(vector_id)
                if index_id is not None:
                    # Mark as deleted
                    if index_id in self.metadata_store:
                        self.metadata_store[index_id]["_deleted"] = True
                        deleted_count += 1
            
            logger.info(f"✅ Marked {deleted_count} vectors as deleted in FAISS store")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete vectors: {e}")
            return False
    
    async def update_metadata(self, id: str, metadata: Dict[str, Any]) -> bool:
        """Update metadata for a vector"""
        try:
            index_id = self.id_to_index.get(id)
            if index_id is not None and index_id in self.metadata_store:
                self.metadata_store[index_id].update(metadata)
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to update metadata: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get store statistics"""
        if self.index:
            self.stats["index_size_mb"] = self.index.ntotal * self.config.dimension * 4 / (1024 * 1024)  # 4 bytes per float
        
        return {
            "store_name": self.store_name,
            "total_vectors": self.stats["total_vectors"],
            "active_vectors": sum(1 for meta in self.metadata_store.values() if not meta.get("_deleted", False)),
            "total_searches": self.stats["total_searches"],
            "avg_search_time_ms": self.stats["avg_search_time"] * 1000,
            "index_size_mb": self.stats["index_size_mb"],
            "created_at": self.stats["created_at"],
            "last_save": self.stats["last_save"]
        }

# =============== FAISS VECTOR STORE ===============

class FAISSVectorStore(IVectorStore):
    """FAISS-based vector store implementation"""
    
    def __init__(self, config: VectorStoreConfig, store_name: str):
        self.config = config
        self.store_name = store_name
        self.index: Optional[faiss.Index] = None
        self.metadata_store: Dict[int, Dict[str, Any]] = {}
        self.id_to_index: Dict[str, int] = {}
        self.index_to_id: Dict[int, str] = {}
        self.next_id = 0
        
        # Statistics
        self.stats = {
            "created_at": datetime.utcnow(),
            "total_vectors": 0,
            "total_searches": 0,
            "avg_search_time": 0.0,
            "last_save": None,
            "index_size_mb": 0.0
        }
        
        # Auto-save task
        self._auto_save_task: Optional[asyncio.Task] = None
        self._dirty = False
    
    async def initialize(self) -> bool:
        """Initialize FAISS index"""
        try:
            # Create index based on configuration
            if self.config.faiss_index_type == "IndexFlatIP":
                self.index = faiss.IndexFlatIP(self.config.vector_dimension)
            elif self.config.faiss_index_type == "IndexFlatL2":
                self.index = faiss.IndexFlatL2(self.config.vector_dimension)
            elif self.config.faiss_index_type == "IndexIVFFlat":
                quantizer = faiss.IndexFlatIP(self.config.vector_dimension)
                self.index = faiss.IndexIVFFlat(
                    quantizer, self.config.vector_dimension, self.config.faiss_nlist
                )
            elif self.config.faiss_index_type == "IndexHNSWFlat":
                self.index = faiss.IndexHNSWFlat(self.config.vector_dimension, self.config.faiss_m)
                self.index.hnsw.efConstruction = self.config.faiss_ef_construction
                self.index.hnsw.efSearch = self.config.faiss_ef_search
            else:
                raise ValueError(f"Unsupported FAISS index type: {self.config.faiss_index_type}")
            
            # GPU support
            if self.config.use_gpu and faiss.get_num_gpus() > 0:
                res = faiss.StandardGpuResources()
                self.index = faiss.index_cpu_to_gpu(res, self.config.gpu_device_id, self.index)
                logger.info(f"✅ FAISS index moved to GPU {self.config.gpu_device_id}")
            
            # Set number of threads
            faiss.omp_set_num_threads(self.config.num_threads)
            
            # Try to load existing index
            await self._load_index()
            
            # Start auto-save task
            self._auto_save_task = asyncio.create_task(self._auto_save_loop())
            
            logger.info(f"✅ FAISS vector store '{self.store_name}' initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ FAISS initialization failed: {e}")
            return False
    
    async def _load_index(self) -> None:
        """Load existing index from disk"""
        try:
            index_path = Path(self.config.index_persist_path) / f"{self.store_name}.faiss"
            metadata_path = Path(self.config.index_persist_path) / f"{self.store_name}_metadata.pkl"
            
            if index_path.exists() and metadata_path.exists():
                # Load FAISS index
                self.index = faiss.read_index(str(index_path))
                
                # Load metadata
                with open(metadata_path, 'rb') as f:
                    data = pickle.load(f)
                    self.metadata_store = data['metadata_store']
                    self.id_to_index = data['id_to_index']
                    self.index_to_id = data['index_to_id']
                    self.next_id = data['next_id']
                    self.stats.update(data.get('stats', {}))
                
                self.stats["total_vectors"] = self.index.ntotal
                logger.info(f"✅ Loaded existing index with {self.index.ntotal} vectors")
            
        except Exception as e:
            logger.warning(f"Could not load existing index: {e}")
    
    async def _save_index(self) -> None:
        """Save index to disk"""
        try:
            # Create directory if it doesn't exist
            index_dir = Path(self.config.index_persist_path)
            index_dir.mkdir(parents=True, exist_ok=True)
            
            # Save FAISS index
            index_path = index_dir / f"{self.store_name}.faiss"
            if self.config.use_gpu:
                # Move to CPU for saving
                cpu_index = faiss.index_gpu_to_cpu(self.index)
                faiss.write_index(cpu_index, str(index_path))
            else:
                faiss.write_index(self.index, str(index_path))
            
            # Save metadata
            metadata_path = index_dir / f"{self.store_name}_metadata.pkl"
            save_data = {
                'metadata_store': self.metadata_store,
                'id_to_index': self.id_to_index,
                'index_to_id': self.index_to_id,
                'next_id': self.next_id,
                'stats': self.stats
            }
            
            with open(metadata_path, 'wb') as f:
                pickle.dump(save_data, f)
            
            # Update stats
            self.stats["last_save"] = datetime.utcnow()
            self.stats["index_size_mb"] = index_path.stat().st_size / (1024 * 1024)
            self._dirty = False
            
            logger.info(f"✅ Index saved to {index_path}")
            
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
    
    async def _auto_save_loop(self) -> None:
        """Auto-save loop"""
        while True:
            try:
                await asyncio.sleep(self.config.auto_save_interval)
                if self._dirty:
                    await self._save_index()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Auto-save error: {e}")
    
    async def add_vectors(self, vectors: np.ndarray, metadata: List[Dict[str, Any]], 
                         ids: Optional[List[str]] = None) -> bool:
        """Add vectors to FAISS index"""
        try:
            if vectors.shape[1] != self.config.vector_dimension:
                raise ValueError(f"Vector dimension mismatch: expected {self.config.vector_dimension}, got {vectors.shape[1]}")
            
            # Normalize vectors for cosine similarity
            if self.config.distance_metric == "cosine":
                vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
            
            # Train index if needed
            if hasattr(self.index, 'is_trained') and not self.index.is_trained:
                self.index.train(vectors)
            
            # Generate IDs if not provided
            if ids is None:
                ids = [f"vec_{self.next_id + i}" for i in range(len(vectors))]
            
            # Add vectors to index
            start_idx = self.index.ntotal
            self.index.add(vectors.astype(np.float32))
            
            # Update metadata mappings
            for i, (vec_id, meta) in enumerate(zip(ids, metadata)):
                index_id = start_idx + i
                self.id_to_index[vec_id] = index_id
                self.index_to_id[index_id] = vec_id
                self.metadata_store[index_id] = {
                    "id": vec_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    **meta
                }
            
            self.next_id = max(self.next_id, len(ids)) + len(ids)
            self.stats["total_vectors"] = self.index.ntotal
            self._dirty = True
            
            logger.info(f"✅ Added {len(vectors)} vectors to FAISS index")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add vectors: {e}")
            return False
    
    async def search_similar(self, query_vector: np.ndarray, top_k: int = 100, 
                           filter_criteria: Optional[Dict] = None) -> List[Tuple[str, float, Dict]]:
        """Search for similar vectors"""
        import time
        start_time = time.time()
        
        try:
            # Ensure query vector is 2D
            if query_vector.ndim == 1:
                query_vector = query_vector.reshape(1, -1)
            
            # Normalize for cosine similarity
            if self.config.distance_metric == "cosine":
                query_vector = query_vector / np.linalg.norm(query_vector, axis=1, keepdims=True)
            
            # Search
            distances, indices = self.index.search(query_vector.astype(np.float32), top_k)
            
            # Process results
            results = []
            for distance, idx in zip(distances[0], indices[0]):
                if idx == -1:  # No more results
                    break
                
                # Get metadata
                metadata = self.metadata_store.get(idx, {})
                vec_id = self.index_to_id.get(idx, str(idx))
                
                # Apply filters
                if filter_criteria:
                    if not self._matches_filter(metadata, filter_criteria):
                        continue
                
                # Convert distance to similarity score
                if self.config.distance_metric == "cosine":
                    similarity = float(distance)  # FAISS IP already gives similarity
                else:
                    similarity = 1.0 / (1.0 + float(distance))  # Convert distance to similarity
                
                # Apply threshold
                if similarity >= self.config.similarity_threshold:
                    results.append((vec_id, similarity, metadata))
            
            # Update statistics
            search_time = time.time() - start_time
            self.stats["total_searches"] += 1
            self.stats["avg_search_time"] = (
                (self.stats["avg_search_time"] * (self.stats["total_searches"] - 1) + search_time) /
                self.stats["total_searches"]
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def _matches_filter(self, metadata: Dict[str, Any], filter_criteria: Dict[str, Any]) -> bool:
        """Check if metadata matches filter criteria"""
        for key, value in filter_criteria.items():
            if key not in metadata:
                return False
            
            if isinstance(value, dict):
                # Range filter: {"age": {"$gte": 18, "$lt": 65}}
                metadata_value = metadata[key]
                for op, filter_value in value.items():
                    if op == "$gte" and metadata_value < filter_value:
                        return False
                    elif op == "$gt" and metadata_value <= filter_value:
                        return False
                    elif op == "$lte" and metadata_value > filter_value:
                        return False
                    elif op == "$lt" and metadata_value >= filter_value:
                        return False
                    elif op == "$eq" and metadata_value != filter_value:
                        return False
                    elif op == "$ne" and metadata_value == filter_value:
                        return False
                    elif op == "$in" and metadata_value not in filter_value:
                        return False
                    elif op == "$nin" and metadata_value in filter_value:
                        return False
            else:
                # Direct match
                if metadata[key] != value:
                    return False
        
        return True
    
    async def delete_vectors(self, ids: List[str]) -> bool:
        """Delete vectors by IDs (FAISS doesn't support deletion, so we mark as deleted)"""
        try:
            deleted_count = 0
            for vec_id in ids:
                if vec_id in self.id_to_index:
                    index_id = self.id_to_index[vec_id]
                    
                    # Mark as deleted in metadata
                    if index_id in self.metadata_store:
                        self.metadata_store[index_id]["deleted"] = True
                        self.metadata_store[index_id]["deleted_at"] = datetime.utcnow().isoformat()
                        deleted_count += 1
            
            self._dirty = True
            logger.info(f"✅ Marked {deleted_count} vectors as deleted")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete vectors: {e}")
            return False
    
    async def update_metadata(self, vec_id: str, metadata: Dict[str, Any]) -> bool:
        """Update metadata for a vector"""
        try:
            if vec_id in self.id_to_index:
                index_id = self.id_to_index[vec_id]
                if index_id in self.metadata_store:
                    self.metadata_store[index_id].update(metadata)
                    self.metadata_store[index_id]["updated_at"] = datetime.utcnow().isoformat()
                    self._dirty = True
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update metadata: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get FAISS store statistics"""
        return {
            "store_name": self.store_name,
            "index_type": self.config.faiss_index_type,
            "vector_dimension": self.config.vector_dimension,
            "distance_metric": self.config.distance_metric,
            "use_gpu": self.config.use_gpu,
            **self.stats
        }
    
    async def close(self) -> None:
        """Close FAISS store"""
        try:
            # Cancel auto-save task
            if self._auto_save_task:
                self._auto_save_task.cancel()
                try:
                    await self._auto_save_task
                except asyncio.CancelledError:
                    pass
            
            # Final save
            if self._dirty:
                await self._save_index()
            
            logger.info(f"✅ FAISS store '{self.store_name}' closed")
            
        except Exception as e:
            logger.error(f"Error closing FAISS store: {e}")

# =============== VECTOR STORE CONNECTION POOL ===============

class VectorStoreConnectionPool(IConnectionPool):
    """Vector store connection pool manager"""
    
    def __init__(self, config: VectorStoreConfig, connection_info: DatabaseConnectionInfo):
        self.config = config
        self.connection_info = connection_info
        self.state = ConnectionState.IDLE
        
        # Vector stores by content type
        self.vector_stores: Dict[str, IVectorStore] = {}
        
        # Content type configurations
        self.content_types = self.config.supported_content_types or [
            "audio", "video", "image", "text"
        ]
        
        # Statistics
        self.stats = {
            "created_at": datetime.utcnow(),
            "total_stores": 0,
            "total_vectors": 0,
            "total_searches": 0,
            "avg_search_time": 0.0,
            "last_health_check": None
        }
        
        # Health monitoring
        self._health_check_task: Optional[asyncio.Task] = None
    
    async def initialize(self) -> bool:
        """Initialize vector stores for each content type"""
        try:
            # Create vector store for each content type
            for content_type in self.content_types:
                store_name = f"{self.connection_info.database}_{content_type}"
                
                # Create FAISS store (can be extended to support other vector stores)
                store = FAISSVectorStore(self.config, store_name)
                success = await store.initialize()
                
                if success:
                    self.vector_stores[content_type] = store
                    logger.info(f"✅ Vector store for {content_type} initialized")
                else:
                    logger.error(f"❌ Failed to initialize vector store for {content_type}")
                    return False
            
            self.stats["total_stores"] = len(self.vector_stores)
            self.state = ConnectionState.ACTIVE
            
            # Start health monitoring
            if self.config.enable_monitoring:
                self._health_check_task = asyncio.create_task(self._health_monitor())
            
            logger.info(f"✅ Vector store pool initialized with {len(self.vector_stores)} stores")
            return True
            
        except Exception as e:
            logger.error(f"❌ Vector store pool initialization failed: {e}")
            self.state = ConnectionState.FAILED
            return False
    
    async def acquire(self, timeout: Optional[float] = None) -> Dict[str, IVectorStore]:
        """Acquire vector stores"""
        if not self.vector_stores:
            raise Exception("Vector store pool not initialized")
        
        return self.vector_stores
    
    async def release(self, connection: Any) -> None:
        """Release vector stores (no-op)"""
        pass
    
    async def add_content_fingerprint(self, content_type: str, vector: np.ndarray, 
                                    metadata: Dict[str, Any], 
                                    fingerprint_id: Optional[str] = None) -> bool:
        """
Add content fingerprint to appropriate vector store"""
        try:
            if content_type not in self.vector_stores:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            store = self.vector_stores[content_type]
            
            # Ensure vector is 2D
            if vector.ndim == 1:
                vector = vector.reshape(1, -1)
            
            # Add content type to metadata
            metadata = {
                "content_type": content_type,
                "fingerprint_id": fingerprint_id or self._generate_fingerprint_id(vector),
                **metadata
            }
            
            ids = [fingerprint_id] if fingerprint_id else None
            success = await store.add_vectors(vector, [metadata], ids)
            
            if success:
                self.stats["total_vectors"] += 1
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to add content fingerprint: {e}")
            return False
    
    def _generate_fingerprint_id(self, vector: np.ndarray) -> str:
        """Generate unique fingerprint ID based on vector content"""
        vector_hash = hashlib.sha256(vector.tobytes()).hexdigest()
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"fp_{timestamp}_{vector_hash[:16]}"
    
    async def search_similar_content(self, content_type: str, query_vector: np.ndarray, 
                                   top_k: int = 100, similarity_threshold: float = None,
                                   filter_criteria: Optional[Dict] = None) -> List[Tuple[str, float, Dict]]:
        """Search for similar content across vector stores"""
        try:
            if content_type not in self.vector_stores:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            store = self.vector_stores[content_type]
            
            # Use store-specific threshold if not provided
            if similarity_threshold is None:
                similarity_threshold = self.config.similarity_threshold
            
            # Temporarily update threshold
            original_threshold = store.config.similarity_threshold
            store.config.similarity_threshold = similarity_threshold
            
            try:
                results = await store.search_similar(query_vector, top_k, filter_criteria)
                self.stats["total_searches"] += 1
                return results
            finally:
                # Restore original threshold
                store.config.similarity_threshold = original_threshold
            
        except Exception as e:
            logger.error(f"Failed to search similar content: {e}")
            return []
    
    async def search_cross_content_types(self, query_vector: np.ndarray, 
                                       content_types: Optional[List[str]] = None,
                                       top_k: int = 100) -> Dict[str, List[Tuple[str, float, Dict]]]:
        """Search across multiple content types"""
        try:
            if content_types is None:
                content_types = list(self.vector_stores.keys())
            
            results = {}
            
            # Search each content type
            for content_type in content_types:
                if content_type in self.vector_stores:
                    store_results = await self.search_similar_content(
                        content_type, query_vector, top_k
                    )
                    results[content_type] = store_results
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search cross content types: {e}")
            return {}
    
    async def delete_content_fingerprint(self, content_type: str, fingerprint_id: str) -> bool:
        """Delete content fingerprint"""
        try:
            if content_type not in self.vector_stores:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            store = self.vector_stores[content_type]
            return await store.delete_vectors([fingerprint_id])
            
        except Exception as e:
            logger.error(f"Failed to delete content fingerprint: {e}")
            return False
    
    async def update_content_metadata(self, content_type: str, fingerprint_id: str, 
                                    metadata: Dict[str, Any]) -> bool:
        """Update content metadata"""
        try:
            if content_type not in self.vector_stores:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            store = self.vector_stores[content_type]
            return await store.update_metadata(fingerprint_id, metadata)
            
        except Exception as e:
            logger.error(f"Failed to update content metadata: {e}")
            return False
    
    async def get_content_stats(self, content_type: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for specific content type or all"""
        try:
            if content_type:
                if content_type in self.vector_stores:
                    return await self.vector_stores[content_type].get_stats()
                else:
                    return {}
            else:
                # Get stats for all stores
                all_stats = {}
                for ct, store in self.vector_stores.items():
                    all_stats[ct] = await store.get_stats()
                return all_stats
                
        except Exception as e:
            logger.error(f"Failed to get content stats: {e}")
            return {}
    
    async def health_check(self) -> bool:
        """Check vector store pool health"""
        try:
            healthy_stores = 0
            total_stores = len(self.vector_stores)
            
            for content_type, store in self.vector_stores.items():
                try:
                    # Basic health check - try to get stats
                    stats = await store.get_stats()
                    if stats:
                        healthy_stores += 1
                except Exception as e:
                    logger.warning(f"Health check failed for {content_type} store: {e}")
            
            health_ratio = healthy_stores / total_stores if total_stores > 0 else 0
            self.stats["last_health_check"] = datetime.utcnow()
            
            return health_ratio >= 0.8  # At least 80% of stores should be healthy
            
        except Exception as e:
            logger.error(f"Vector store health check failed: {e}")
            return False
    
    async def _health_monitor(self) -> None:
        """Background health monitoring"""
        while self.state == ConnectionState.ACTIVE:
            try:
                is_healthy = await self.health_check()
                if not is_healthy:
                    logger.warning("Vector store pool health check failed")
                
                # Update aggregated statistics
                await self._update_stats()
                
                await asyncio.sleep(self.config.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Vector store health monitor error: {e}")
                await asyncio.sleep(5)
    
    async def _update_stats(self) -> None:
        """Update aggregated statistics"""
        try:
            total_vectors = 0
            total_searches = 0
            total_search_time = 0
            
            for store in self.vector_stores.values():
                stats = await store.get_stats()
                total_vectors += stats.get("total_vectors", 0)
                total_searches += stats.get("total_searches", 0)
                total_search_time += stats.get("avg_search_time", 0) * stats.get("total_searches", 0)
            
            self.stats["total_vectors"] = total_vectors
            self.stats["total_searches"] = total_searches
            
            if total_searches > 0:
                self.stats["avg_search_time"] = total_search_time / total_searches
            
        except Exception as e:
            logger.error(f"Failed to update stats: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store pool statistics"""
        pool_stats = {
            "content_types": list(self.vector_stores.keys()),
            "vector_dimension": self.config.vector_dimension,
            "distance_metric": self.config.distance_metric,
            "similarity_threshold": self.config.similarity_threshold,
            "state": self.state.value
        }
        pool_stats.update(self.stats)
        return pool_stats
    
    async def close(self) -> None:
        """Close vector store pool"""
        try:
            self.state = ConnectionState.CLOSED
            
            # Cancel health monitoring
            if self._health_check_task:
                self._health_check_task.cancel()
                try:
                    await self._health_check_task
                except asyncio.CancelledError:
                    pass
            
            # Close all vector stores
            for content_type, store in self.vector_stores.items():
                try:
                    await store.close()
                    logger.info(f"✅ Vector store {content_type} closed")
                except Exception as e:
                    logger.error(f"Error closing vector store {content_type}: {e}")
            
            logger.info("✅ Vector store pool closed")
            
        except Exception as e:
            logger.error(f"Error closing vector store pool: {e}")

# =============== EXPORTS ===============

__all__ = [
    "VectorStoreConnectionPool",
    "VectorStoreConfig",
    "FAISSVectorStore",
    "IVectorStore"
]
