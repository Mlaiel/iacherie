"""🔗 Vector Index Management
============================

Unified vector database interface and multi-index management system.
Provides high-level API for content fingerprint storage, search, analytics
and comprehensive index lifecycle management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL IMPORTANT ⚠️
=====================================
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et constitue une violation 
des droits d'auteur passible de poursuites judiciaires.

Contact: mlaiel@live.de

🎯 PROJECT TEAM SPECIALTIES 🎯
==============================
Lead Developer IA: Fahed Mlaiel (mlaiel@live.de)
Backend Senior: Advanced Python & FastAPI Architecture
ML Engineer: Deep Learning & Vector Embeddings
DBA: Vector Database Optimization & Performance
Security: Content Protection & Rights Management
Microservices: Scalable Distributed Architecture
Audio: Signal Processing & Fingerprinting
DevOps: Infrastructure & Cloud Deployment
IA Prompt Engineer: AI Model Integration & Optimization
"""

import asyncio
import logging
import numpy as np
import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


# =============================================================================
# MAIN VECTOR DATABASE INTERFACE SECTION
# =============================================================================

class VectorDatabaseStatus(Enum):
    """Status of the vector database"""
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class ContentFingerprint:
    """Content fingerprint for storage"""
    content_id: str
    content_type: str
    embedding_vector: np.ndarray
    metadata: Dict[str, Any]
    created_at: float
    embedding_type: str


@dataclass
class SearchRequest:
    """Search request configuration"""
    query_vector: np.ndarray
    content_type: Optional[str] = None
    similarity_threshold: float = 0.7
    max_results: int = 10
    include_metadata: bool = True
    metadata_filters: Optional[Dict[str, Any]] = None


@dataclass
class DatabaseStats:
    """Vector database statistics"""
    total_vectors: int
    vectors_by_type: Dict[str, int]
    total_memory_mb: float
    index_count: int
    avg_search_time_ms: float
    last_updated: float


class VectorDatabase:
    """
    Unified entry point for the advanced vector database system.
    Provides high-level API for content fingerprint storage, search, and analytics.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize vector database with configuration.
        
        Args:
            config: Database configuration dictionary
        """
        self.config = config
        self.status = VectorDatabaseStatus.INITIALIZING
        
        # Initialize components (will be properly imported in real implementation)
        self.embedding_service = None
        self.index_manager = None
        self.search_engine = None
        self.analytics_engine = None
        
        # Performance tracking
        self.performance_stats = {
            'total_operations': 0,
            'search_operations': 0,
            'storage_operations': 0,
            'avg_operation_time_ms': 0.0
        }
        
        self.logger = logging.getLogger(f"{__name__}.VectorDatabase")
        self.logger.info("Vector database initialized")
    
    async def initialize(self) -> bool:
        """Initialize all database components"""
        try:
            self.status = VectorDatabaseStatus.INITIALIZING
            
            # Initialize embedding service
            self.logger.info("Initializing embedding service...")
            # self.embedding_service = EmbeddingService(self.config.get('embeddings', {}))
            # await self.embedding_service.initialize()
            
            # Initialize index manager
            self.logger.info("Initializing index manager...")
            # self.index_manager = VectorIndexManager(self.config.get('index_manager', {}))
            # await self.index_manager.initialize()
            
            # Initialize search engine
            self.logger.info("Initializing search engine...")
            # self.search_engine = SearchEngine(self.config.get('search', {}))
            
            # Initialize analytics
            if self.config.get('analytics', {}).get('enabled', False):
                self.logger.info("Initializing analytics engine...")
                # self.analytics_engine = AnalyticsEngine(self.config.get('analytics', {}))
                # await self.analytics_engine.initialize()
            
            self.status = VectorDatabaseStatus.READY
            self.logger.info("Vector database initialization completed successfully")
            return True
            
        except Exception as e:
            self.status = VectorDatabaseStatus.ERROR
            self.logger.error(f"Database initialization failed: {e}")
            return False
    
    async def store_content_fingerprint(self, fingerprint: ContentFingerprint) -> bool:
        """
        Store content fingerprint in the database.
        
        Args:
            fingerprint: Content fingerprint to store
            
        Returns:
            True if storage was successful
        """
        start_time = time.time()
        
        try:
            if self.status != VectorDatabaseStatus.READY:
                raise RuntimeError(f"Database not ready. Status: {self.status}")
            
            # Store fingerprint using index manager
            success = True  # Placeholder
            # success = await self.index_manager.add_vector(
            #     fingerprint.content_id,
            #     fingerprint.embedding_vector,
            #     fingerprint.metadata,
            #     fingerprint.embedding_type
            # )
            
            if success:
                self.performance_stats['storage_operations'] += 1
                self._update_operation_stats(time.time() - start_time)
                self.logger.debug(f"Stored fingerprint for content {fingerprint.content_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to store fingerprint for {fingerprint.content_id}: {e}")
            return False
    
    async def search_similar_content(self, request: SearchRequest) -> List[Dict[str, Any]]:
        """
        Search for similar content using vector similarity.
        
        Args:
            request: Search request configuration
            
        Returns:
            List of similar content matches
        """
        start_time = time.time()
        
        try:
            if self.status != VectorDatabaseStatus.READY:
                raise RuntimeError(f"Database not ready. Status: {self.status}")
            
            # Perform search using search engine
            results = []  # Placeholder
            # results = await self.search_engine.search(
            #     query_vector=request.query_vector,
            #     content_type=request.content_type,
            #     similarity_threshold=request.similarity_threshold,
            #     max_results=request.max_results,
            #     metadata_filters=request.metadata_filters
            # )
            
            self.performance_stats['search_operations'] += 1
            self._update_operation_stats(time.time() - start_time)
            
            self.logger.debug(f"Search completed: {len(results)} results found")
            return results
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []
    
    async def get_database_stats(self) -> DatabaseStats:
        """Get comprehensive database statistics"""
        try:
            # Collect stats from all components
            total_vectors = 0
            vectors_by_type = {}
            total_memory_mb = 0.0
            index_count = 0
            
            # if self.index_manager:
            #     stats = await self.index_manager.get_comprehensive_stats()
            #     total_vectors = stats.total_vectors
            #     vectors_by_type = stats.vectors_by_type
            #     total_memory_mb = stats.total_memory_mb
            #     index_count = stats.index_count
            
            return DatabaseStats(
                total_vectors=total_vectors,
                vectors_by_type=vectors_by_type,
                total_memory_mb=total_memory_mb,
                index_count=index_count,
                avg_search_time_ms=self.performance_stats['avg_operation_time_ms'],
                last_updated=time.time()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get database stats: {e}")
            return DatabaseStats(
                total_vectors=0,
                vectors_by_type={},
                total_memory_mb=0.0,
                index_count=0,
                avg_search_time_ms=0.0,
                last_updated=time.time()
            )
    
    def _update_operation_stats(self, operation_time_seconds: float):
        """Update operation performance statistics"""
        operation_time_ms = operation_time_seconds * 1000
        
        self.performance_stats['total_operations'] += 1
        
        # Update rolling average
        current_avg = self.performance_stats['avg_operation_time_ms']
        total_ops = self.performance_stats['total_operations']
        
        new_avg = ((current_avg * (total_ops - 1)) + operation_time_ms) / total_ops
        self.performance_stats['avg_operation_time_ms'] = new_avg
    
    async def shutdown(self):
        """Gracefully shutdown the database"""
        try:
            self.status = VectorDatabaseStatus.MAINTENANCE
            
            # Save all indexes
            # if self.index_manager:
            #     await self.index_manager.save_all_indexes()
            
            # Shutdown analytics
            # if self.analytics_engine:
            #     await self.analytics_engine.shutdown()
            
            self.logger.info("Vector database shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


# =============================================================================
# INDEX MANAGER SECTION
# =============================================================================

class IndexStatus(Enum):
    """Status of vector index"""
    INITIALIZING = "initializing"
    READY = "ready"
    TRAINING = "training"
    OPTIMIZING = "optimizing"
    SAVING = "saving"
    LOADING = "loading"
    ERROR = "error"


class EmbeddingType(Enum):
    """Types of embeddings supported"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    COMPOSITE = "composite"


class IndexType(Enum):
    """FAISS index types"""
    FLAT_L2 = "IndexFlatL2"
    FLAT_IP = "IndexFlatIP"
    IVF_FLAT = "IndexIVFFlat"
    IVF_PQ = "IndexIVFPQ"
    HNSW = "IndexHNSWFlat"


class SimilarityMetric(Enum):
    """Similarity metrics"""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"


@dataclass
class IndexConfiguration:
    """Configuration for a vector index"""
    index_name: str
    embedding_type: EmbeddingType
    dimension: int
    index_type: IndexType
    similarity_metric: SimilarityMetric
    storage_path: str
    auto_optimize: bool = True
    backup_enabled: bool = True
    metadata: Dict[str, Any] = None


@dataclass
class IndexInfo:
    """Information about a vector index"""
    config: IndexConfiguration
    status: IndexStatus
    vector_count: int
    memory_usage_mb: float
    last_updated: float
    last_optimized: float
    error_message: Optional[str] = None


@dataclass
class ComprehensiveStats:
    """Comprehensive statistics across all indexes"""
    total_vectors: int
    vectors_by_type: Dict[str, int]
    total_memory_mb: float
    index_count: int
    indexes_by_status: Dict[str, int]
    performance_metrics: Dict[str, float]
    last_updated: float


class VectorIndexManager:
    """
    Manages multiple vector indexes for different content types and embedding dimensions.
    Provides unified interface for index lifecycle management and optimization.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize index manager.
        
        Args:
            config: Index manager configuration
        """
        self.config = config
        self.indexes: Dict[str, Any] = {}  # index_name -> vector_store
        self.index_configs: Dict[str, IndexConfiguration] = {}
        self.index_info: Dict[str, IndexInfo] = {}
        
        # Storage configuration
        self.base_storage_path = Path(config.get('storage_path', './vector_indexes'))
        self.base_storage_path.mkdir(parents=True, exist_ok=True)
        
        # Management settings
        self.auto_create_indexes = config.get('auto_create_indexes', True)
        self.auto_optimize = config.get('auto_optimize', True)
        self.backup_interval_hours = config.get('backup_interval_hours', 24)
        self.max_indexes = config.get('max_indexes', 50)
        
        # Thread executor for background tasks
        self.executor = ThreadPoolExecutor(max_workers=config.get('max_workers', 4))
        
        # Performance tracking
        self.operation_stats = {
            'index_operations': 0,
            'search_operations': 0,
            'optimization_operations': 0,
            'avg_operation_time_ms': 0.0
        }
        
        self.logger = logging.getLogger(f"{__name__}.VectorIndexManager")
        self.logger.info("Vector index manager initialized")
    
    async def initialize(self) -> bool:
        """Initialize the index manager"""
        try:
            # Load existing index configurations
            await self._load_existing_indexes()
            
            # Start background tasks
            if self.auto_optimize:
                asyncio.create_task(self._optimization_scheduler())
            
            # Start backup scheduler
            asyncio.create_task(self._backup_scheduler())
            
            self.logger.info("Index manager initialization completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Index manager initialization failed: {e}")
            return False
    
    async def create_index(self, config: IndexConfiguration) -> bool:
        """
        Create a new vector index.
        
        Args:
            config: Index configuration
            
        Returns:
            True if index was created successfully
        """
        try:
            if len(self.indexes) >= self.max_indexes:
                raise RuntimeError(f"Maximum number of indexes ({self.max_indexes}) reached")
            
            if config.index_name in self.indexes:
                raise ValueError(f"Index {config.index_name} already exists")
            
            self.logger.info(f"Creating index: {config.index_name}")
            
            # Create vector store instance (placeholder)
            # In real implementation, would create FAISSVectorStore
            vector_store = None
            # vector_store = FAISSVectorStore(
            #     dimension=config.dimension,
            #     index_type=config.index_type,
            #     **config.metadata or {}
            # )
            # await vector_store.initialize()
            
            # Store index
            self.indexes[config.index_name] = vector_store
            self.index_configs[config.index_name] = config
            
            # Create index info
            self.index_info[config.index_name] = IndexInfo(
                config=config,
                status=IndexStatus.READY,
                vector_count=0,
                memory_usage_mb=0.0,
                last_updated=time.time(),
                last_optimized=time.time()
            )
            
            # Save configuration
            await self._save_index_config(config)
            
            self.logger.info(f"Index {config.index_name} created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create index {config.index_name}: {e}")
            return False
    
    async def add_vector(
        self, 
        index_name: str, 
        vector_id: str, 
        vector: np.ndarray, 
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Add vector to specified index.
        
        Args:
            index_name: Name of target index
            vector_id: Unique vector identifier
            vector: Vector data
            metadata: Associated metadata
            
        Returns:
            True if vector was added successfully
        """
        try:
            if index_name not in self.indexes:
                if self.auto_create_indexes:
                    # Auto-create index with default config
                    await self._auto_create_index(index_name, vector.shape[0])
                else:
                    raise ValueError(f"Index {index_name} does not exist")
            
            # Add vector to index
            vector_store = self.indexes[index_name]
            # success = await vector_store.add_vector(vector_id, vector, metadata)
            success = True  # Placeholder
            
            if success:
                # Update index info
                self.index_info[index_name].vector_count += 1
                self.index_info[index_name].last_updated = time.time()
                
                self.logger.debug(f"Added vector {vector_id} to index {index_name}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to add vector to {index_name}: {e}")
            return False
    
    async def search_index(
        self, 
        index_name: str, 
        query_vector: np.ndarray, 
        k: int = 10, 
        similarity_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search specific index for similar vectors.
        
        Args:
            index_name: Name of index to search
            query_vector: Query vector
            k: Number of results to return
            similarity_threshold: Minimum similarity threshold
            
        Returns:
            List of search results
        """
        try:
            if index_name not in self.indexes:
                raise ValueError(f"Index {index_name} does not exist")
            
            vector_store = self.indexes[index_name]
            # results = await vector_store.search(query_vector, k, similarity_threshold)
            results = []  # Placeholder
            
            self.operation_stats['search_operations'] += 1
            
            return results
            
        except Exception as e:
            self.logger.error(f"Search failed in index {index_name}: {e}")
            return []
    
    async def search_all_indexes(
        self, 
        query_vector: np.ndarray, 
        content_type: Optional[str] = None,
        k: int = 10,
        similarity_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search all relevant indexes for similar vectors.
        
        Args:
            query_vector: Query vector
            content_type: Optional content type filter
            k: Number of results to return per index
            similarity_threshold: Minimum similarity threshold
            
        Returns:
            Aggregated search results from all indexes
        """
        all_results = []
        
        # Filter indexes by content type if specified
        target_indexes = self.indexes.keys()
        if content_type:
            target_indexes = [
                name for name, config in self.index_configs.items()
                if config.embedding_type.value == content_type
            ]
        
        # Search each target index
        for index_name in target_indexes:
            try:
                results = await self.search_index(
                    index_name, query_vector, k, similarity_threshold
                )
                
                # Add index information to results
                for result in results:
                    result['source_index'] = index_name
                
                all_results.extend(results)
                
            except Exception as e:
                self.logger.warning(f"Search failed in index {index_name}: {e}")
                continue
        
        # Sort by similarity score and limit results
        all_results.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        return all_results[:k]
    
    async def optimize_index(self, index_name: str) -> bool:
        """
        Optimize specific index for better performance.
        
        Args:
            index_name: Name of index to optimize
            
        Returns:
            True if optimization was successful
        """
        try:
            if index_name not in self.indexes:
                raise ValueError(f"Index {index_name} does not exist")
            
            self.index_info[index_name].status = IndexStatus.OPTIMIZING
            
            # Perform optimization (placeholder)
            # In real implementation, would call vector_store.optimize()
            await asyncio.sleep(0.1)  # Simulate optimization time
            
            self.index_info[index_name].status = IndexStatus.READY
            self.index_info[index_name].last_optimized = time.time()
            
            self.operation_stats['optimization_operations'] += 1
            
            self.logger.info(f"Index {index_name} optimized successfully")
            return True
            
        except Exception as e:
            self.index_info[index_name].status = IndexStatus.ERROR
            self.index_info[index_name].error_message = str(e)
            self.logger.error(f"Failed to optimize index {index_name}: {e}")
            return False
    
    async def save_index(self, index_name: str) -> bool:
        """
        Save index to persistent storage.
        
        Args:
            index_name: Name of index to save
            
        Returns:
            True if save was successful
        """
        try:
            if index_name not in self.indexes:
                raise ValueError(f"Index {index_name} does not exist")
            
            self.index_info[index_name].status = IndexStatus.SAVING
            
            # Save index data
            storage_path = self.base_storage_path / f"{index_name}.index"
            vector_store = self.indexes[index_name]
            # success = await vector_store.save(str(storage_path))
            success = True  # Placeholder
            
            if success:
                self.index_info[index_name].status = IndexStatus.READY
                self.logger.info(f"Index {index_name} saved successfully")
            else:
                self.index_info[index_name].status = IndexStatus.ERROR
                self.index_info[index_name].error_message = "Save operation failed"
            
            return success
            
        except Exception as e:
            self.index_info[index_name].status = IndexStatus.ERROR
            self.index_info[index_name].error_message = str(e)
            self.logger.error(f"Failed to save index {index_name}: {e}")
            return False
    
    async def load_index(self, index_name: str) -> bool:
        """
        Load index from persistent storage.
        
        Args:
            index_name: Name of index to load
            
        Returns:
            True if load was successful
        """
        try:
            # Load configuration first
            config = await self._load_index_config(index_name)
            if not config:
                raise ValueError(f"Configuration for index {index_name} not found")
            
            self.index_info[index_name] = IndexInfo(
                config=config,
                status=IndexStatus.LOADING,
                vector_count=0,
                memory_usage_mb=0.0,
                last_updated=time.time(),
                last_optimized=time.time()
            )
            
            # Create and load vector store
            storage_path = self.base_storage_path / f"{index_name}.index"
            # vector_store = FAISSVectorStore(...)
            # success = await vector_store.load(str(storage_path))
            success = True  # Placeholder
            
            if success:
                self.indexes[index_name] = None  # vector_store
                self.index_configs[index_name] = config
                self.index_info[index_name].status = IndexStatus.READY
                
                self.logger.info(f"Index {index_name} loaded successfully")
            else:
                self.index_info[index_name].status = IndexStatus.ERROR
                self.index_info[index_name].error_message = "Load operation failed"
            
            return success
            
        except Exception as e:
            if index_name in self.index_info:
                self.index_info[index_name].status = IndexStatus.ERROR
                self.index_info[index_name].error_message = str(e)
            self.logger.error(f"Failed to load index {index_name}: {e}")
            return False
    
    async def delete_index(self, index_name: str) -> bool:
        """
        Delete index and all associated data.
        
        Args:
            index_name: Name of index to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            if index_name not in self.indexes:
                raise ValueError(f"Index {index_name} does not exist")
            
            # Remove from memory
            del self.indexes[index_name]
            del self.index_configs[index_name]
            del self.index_info[index_name]
            
            # Remove from disk
            storage_path = self.base_storage_path / f"{index_name}.index"
            config_path = self.base_storage_path / f"{index_name}.config.json"
            
            if storage_path.exists():
                storage_path.unlink()
            if config_path.exists():
                config_path.unlink()
            
            self.logger.info(f"Index {index_name} deleted successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete index {index_name}: {e}")
            return False
    
    async def get_index_info(self, index_name: str) -> Optional[IndexInfo]:
        """Get information about specific index"""
        return self.index_info.get(index_name)
    
    async def list_indexes(self) -> List[str]:
        """Get list of all index names"""
        return list(self.indexes.keys())
    
    async def get_comprehensive_stats(self) -> ComprehensiveStats:
        """Get comprehensive statistics across all indexes"""
        total_vectors = sum(info.vector_count for info in self.index_info.values())
        total_memory_mb = sum(info.memory_usage_mb for info in self.index_info.values())
        
        vectors_by_type = {}
        indexes_by_status = {}
        
        for info in self.index_info.values():
            # Count vectors by embedding type
            embedding_type = info.config.embedding_type.value
            vectors_by_type[embedding_type] = vectors_by_type.get(embedding_type, 0) + info.vector_count
            
            # Count indexes by status
            status = info.status.value
            indexes_by_status[status] = indexes_by_status.get(status, 0) + 1
        
        return ComprehensiveStats(
            total_vectors=total_vectors,
            vectors_by_type=vectors_by_type,
            total_memory_mb=total_memory_mb,
            index_count=len(self.indexes),
            indexes_by_status=indexes_by_status,
            performance_metrics=self.operation_stats,
            last_updated=time.time()
        )
    
    async def _auto_create_index(self, index_name: str, dimension: int):
        """Auto-create index with default configuration"""
        config = IndexConfiguration(
            index_name=index_name,
            embedding_type=EmbeddingType.COMPOSITE,  # Default
            dimension=dimension,
            index_type=IndexType.FLAT_L2,  # Default
            similarity_metric=SimilarityMetric.COSINE,  # Default
            storage_path=str(self.base_storage_path / index_name)
        )
        
        await self.create_index(config)
    
    async def _load_existing_indexes(self):
        """Load configurations of existing indexes"""
        for config_file in self.base_storage_path.glob("*.config.json"):
            try:
                index_name = config_file.stem.replace('.config', '')
                config = await self._load_index_config(index_name)
                if config:
                    await self.load_index(index_name)
            except Exception as e:
                self.logger.warning(f"Failed to load existing index {config_file}: {e}")
    
    async def _save_index_config(self, config: IndexConfiguration):
        """Save index configuration to file"""
        config_path = self.base_storage_path / f"{config.index_name}.config.json"
        config_dict = asdict(config)
        
        # Convert enums to strings for JSON serialization
        config_dict['embedding_type'] = config.embedding_type.value
        config_dict['index_type'] = config.index_type.value
        config_dict['similarity_metric'] = config.similarity_metric.value
        
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    async def _load_index_config(self, index_name: str) -> Optional[IndexConfiguration]:
        """Load index configuration from file"""
        config_path = self.base_storage_path / f"{index_name}.config.json"
        
        if not config_path.exists():
            return None
        
        try:
            with open(config_path, 'r') as f:
                config_dict = json.load(f)
            
            # Convert string enums back to enum objects
            config_dict['embedding_type'] = EmbeddingType(config_dict['embedding_type'])
            config_dict['index_type'] = IndexType(config_dict['index_type'])
            config_dict['similarity_metric'] = SimilarityMetric(config_dict['similarity_metric'])
            
            return IndexConfiguration(**config_dict)
            
        except Exception as e:
            self.logger.error(f"Failed to load config for {index_name}: {e}")
            return None
    
    async def _optimization_scheduler(self):
        """Background task for automatic index optimization"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                for index_name, info in self.index_info.items():
                    if info.config.auto_optimize and info.status == IndexStatus.READY:
                        # Check if optimization is needed
                        hours_since_last = (time.time() - info.last_optimized) / 3600
                        if hours_since_last >= 24:  # Optimize daily
                            await self.optimize_index(index_name)
                
            except Exception as e:
                self.logger.error(f"Optimization scheduler error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
    
    async def _backup_scheduler(self):
        """Background task for automatic index backups"""
        while True:
            try:
                await asyncio.sleep(self.backup_interval_hours * 3600)
                
                for index_name in self.indexes.keys():
                    await self.save_index(index_name)
                
                self.logger.info("Automatic backup completed")
                
            except Exception as e:
                self.logger.error(f"Backup scheduler error: {e}")
                await asyncio.sleep(1800)  # Wait 30 minutes before retrying


# Export all classes and functions
__all__ = [
    # Main database interface
    'VectorDatabaseStatus',
    'ContentFingerprint',
    'SearchRequest',
    'DatabaseStats', 
    'VectorDatabase',
    
    # Index manager
    'IndexStatus',
    'EmbeddingType',
    'IndexType',
    'SimilarityMetric',
    'IndexConfiguration',
    'IndexInfo',
    'ComprehensiveStats',
    'VectorIndexManager'
]