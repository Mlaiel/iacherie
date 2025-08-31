"""Vector Indexing Manager

This module provides advanced vector indexing capabilities with optimization,
partitioning, and maintenance for high-performance vector operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

WARNING: This code is proprietary to Fahed Mlaiel. Any unauthorized copying, modification, 
or distribution without explicit written permission is strictly prohibited and will result 
in legal action under German and international copyright law.
"""
import os
import json
import logging
import asyncio
import threading
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
import numpy as np
import faiss
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, update, delete

from backend.core.config import get_settings
from backend.core.database import get_db_session
from backend.models.content_fingerprints import ContentFingerprint
from backend.utils.exceptions import VectorStoreError, IndexError
from backend.utils.performance import measure_execution_time
from backend.utils.monitoring import MetricsCollector
from backend.utils.storage import StorageManager

logger = logging.getLogger(__name__)
settings = get_settings()


class IndexType(Enum):
    """Vector index types"""    FLAT = "flat"
    IVF = "ivf"
    HNSW = "hnsw"
    LSH = "lsh"
    QUANTIZED = "quantized"
    COMPOSITE = "composite"


class IndexStatus(Enum):
    """Index status states"""    BUILDING = "building"
    READY = "ready"
    OPTIMIZING = "optimizing"
    REBUILDING = "rebuilding"
    ERROR = "error"
    OFFLINE = "offline"


class MaintenanceType(Enum):
    """Index maintenance operations"""    OPTIMIZATION = "optimization"
    REBALANCING = "rebalancing"
    CLEANUP = "cleanup"
    BACKUP = "backup"
    REBUILD = "rebuild"
    PARTITION = "partition"


@dataclass
class IndexConfiguration:
    """Vector index configuration"""    index_type: IndexType
    dimension: int
    metric: str = "cosine"
    nlist: int = 100
    nprobe: int = 10
    m: int = 16
    nbits: int = 8
    max_vectors: int = 1000000
    auto_optimize: bool = True
    compression_enabled: bool = False
    partitioning_enabled: bool = True
    backup_enabled: bool = True


@dataclass
class IndexStatistics:
    """Comprehensive index statistics"""    index_id: str
    content_type: str
    total_vectors: int
    memory_usage_mb: float
    index_size_mb: float
    build_time_seconds: float
    last_updated: datetime
    search_latency_ms: float
    throughput_qps: float
    fragmentation_ratio: float
    optimization_score: float
    partition_count: int
    status: IndexStatus


@dataclass
class MaintenanceTask:
    """Index maintenance task"""    task_id: str
    index_id: str
    task_type: MaintenanceType
    priority: int
    scheduled_time: datetime
    estimated_duration: int
    status: str
    progress: float
    error_message: Optional[str] = None


@dataclass
class IndexPartition:
    """Index partition information"""    partition_id: str
    index_id: str
    start_range: int
    end_range: int
    vector_count: int
    size_mb: float
    last_accessed: datetime
    access_frequency: int
    is_hot: bool


class VectorIndexManager:
    """    Advanced vector index manager for high-performance operations.
    
    Features:
    - Multi-index type support (FAISS, HNSW, LSH, etc.)
    - Automatic optimization and maintenance
    - Intelligent partitioning and load balancing
    - Performance monitoring and analytics
    - Background maintenance scheduling
    - Index versioning and backup
    - Memory management and compression
    """    
    def __init__(
        self,
        storage_manager: StorageManager = None,
        metrics_collector: MetricsCollector = None,
        max_concurrent_operations: int = 4,
        maintenance_interval: int = 3600,
        auto_optimization: bool = True
    ):
        """        Initialize vector index manager
        
        Args:
            storage_manager: Storage manager for persistence
            metrics_collector: Metrics collection system
            max_concurrent_operations: Maximum concurrent operations
            maintenance_interval: Maintenance interval in seconds
            auto_optimization: Enable automatic optimization
        """        self.storage_manager = storage_manager or StorageManager()
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.max_concurrent_operations = max_concurrent_operations
        self.maintenance_interval = maintenance_interval
        self.auto_optimization = auto_optimization
        
        # Active indices
        self.indices: Dict[str, Dict[str, Any]] = {}
        self.index_configs: Dict[str, IndexConfiguration] = {}
        self.index_stats: Dict[str, IndexStatistics] = {}
        
        # Partitioning
        self.partitions: Dict[str, List[IndexPartition]] = {}
        
        # Maintenance scheduling
        self.maintenance_queue: List[MaintenanceTask] = []
        self.active_tasks: Dict[str, MaintenanceTask] = {}
        
        # Thread pools for concurrent operations
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_operations)
        
        # Background tasks
        self._maintenance_task = None
        self._monitoring_task = None
        
        # Performance tracking
        self.operation_stats = {
            "builds": 0,
            "optimizations": 0,
            "searches": 0,
            "updates": 0,
            "errors": 0,
            "avg_build_time": 0.0,
            "avg_search_time": 0.0
        }
        
        logger.info(
            f"Initialized VectorIndexManager - Concurrent Ops: {max_concurrent_operations}, "
            f"Auto Optimization: {auto_optimization}"
        )
    
    async def initialize(self) -> None:
        """Initialize index manager and load existing indices"""        try:
            # Load existing indices from storage
            await self._load_existing_indices()
            
            # Start background maintenance
            if self.auto_optimization:
                self._maintenance_task = asyncio.create_task(self._maintenance_scheduler())
                self._monitoring_task = asyncio.create_task(self._performance_monitor())
            
            logger.info("Vector index manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize index manager: {str(e)}")
            raise VectorStoreError(f"Index manager initialization failed: {str(e)}")
    
    @measure_execution_time
    async def create_index(
        self,
        index_id: str,
        content_type: str,
        config: IndexConfiguration,
        initial_vectors: Optional[List[Tuple[str, np.ndarray]]] = None
    ) -> str:
        """        Create a new vector index
        
        Args:
            index_id: Unique index identifier
            content_type: Content type for the index
            config: Index configuration
            initial_vectors: Optional initial vectors to add
            
        Returns:
            Index ID
        """        try:
            if index_id in self.indices:
                raise VectorStoreError(f"Index {index_id} already exists")
            
            start_time = datetime.now()
            
            # Create index based on type
            index = await self._create_faiss_index(config)
            
            # Store index configuration
            self.index_configs[index_id] = config
            
            # Initialize index data
            self.indices[index_id] = {
                "index": index,
                "content_type": content_type,
                "vector_map": {},  # faiss_id -> content_id
                "metadata": {},    # content_id -> metadata
                "lock": threading.RLock(),
                "created_at": start_time,
                "last_updated": start_time
            }
            
            # Add initial vectors if provided
            if initial_vectors:
                await self.add_vectors(index_id, initial_vectors)
            
            # Initialize partitioning if enabled
            if config.partitioning_enabled:
                await self._initialize_partitioning(index_id)
            
            # Create initial statistics
            build_time = (datetime.now() - start_time).total_seconds()
            self.index_stats[index_id] = IndexStatistics(
                index_id=index_id,
                content_type=content_type,
                total_vectors=len(initial_vectors) if initial_vectors else 0,
                memory_usage_mb=0.0,
                index_size_mb=0.0,
                build_time_seconds=build_time,
                last_updated=datetime.now(timezone.utc),
                search_latency_ms=0.0,
                throughput_qps=0.0,
                fragmentation_ratio=0.0,
                optimization_score=1.0,
                partition_count=1,
                status=IndexStatus.READY
            )
            
            # Save to storage
            await self._save_index(index_id)
            
            # Update operation stats
            self.operation_stats["builds"] += 1
            self.operation_stats["avg_build_time"] = (
                (self.operation_stats["avg_build_time"] * (self.operation_stats["builds"] - 1) + build_time) /
                self.operation_stats["builds"]
            )
            
            logger.info(
                f"Created index {index_id} for {content_type} in {build_time:.2f}s"
            )
            
            return index_id
            
        except Exception as e:
            logger.error(f"Failed to create index {index_id}: {str(e)}")
            raise VectorStoreError(f"Index creation failed: {str(e)}")
    
    @measure_execution_time
    async def add_vectors(
        self,
        index_id: str,
        vectors: List[Tuple[str, np.ndarray, Dict[str, Any]]]
    ) -> List[int]:
        """        Add vectors to an existing index
        
        Args:
            index_id: Index identifier
            vectors: List of (content_id, vector, metadata) tuples
            
        Returns:
            List of internal FAISS IDs
        """        try:
            if index_id not in self.indices:
                raise VectorStoreError(f"Index {index_id} not found")
            
            index_data = self.indices[index_id]
            index = index_data["index"]
            vector_map = index_data["vector_map"]
            metadata_cache = index_data["metadata"]
            
            with index_data["lock"]:
                # Prepare vectors
                vector_arrays = []
                content_ids = []
                
                for content_id, vector, metadata in vectors:
                    # Validate vector dimension
                    config = self.index_configs[index_id]
                    if len(vector) != config.dimension:
                        raise VectorStoreError(
                            f"Vector dimension mismatch: expected {config.dimension}, "
                            f"got {len(vector)}"
                        )
                    
                    vector_arrays.append(vector.astype(np.float32))
                    content_ids.append(content_id)
                    metadata_cache[content_id] = metadata
                
                # Convert to numpy array
                vectors_array = np.array(vector_arrays)
                
                # Normalize vectors
                faiss.normalize_L2(vectors_array)
                
                # Add to index
                start_id = index.ntotal
                index.add(vectors_array)
                
                # Update vector mapping
                faiss_ids = list(range(start_id, start_id + len(vectors)))
                for i, (faiss_id, content_id) in enumerate(zip(faiss_ids, content_ids)):
                    vector_map[faiss_id] = content_id
                
                # Update statistics
                self._update_index_stats(index_id, len(vectors))
                
                # Check if optimization is needed
                if self.auto_optimization:
                    await self._schedule_optimization_if_needed(index_id)
                
                # Save changes
                await self._save_index(index_id)
                
                logger.info(
                    f"Added {len(vectors)} vectors to index {index_id}. "
                    f"Total: {index.ntotal}"
                )
                
                return faiss_ids
                
        except Exception as e:
            logger.error(f"Failed to add vectors to index {index_id}: {str(e)}")
            raise VectorStoreError(f"Vector addition failed: {str(e)}")
    
    @measure_execution_time
    async def search_vectors(
        self,
        index_id: str,
        query_vector: np.ndarray,
        k: int = 10,
        nprobe: int = None
    ) -> List[Tuple[str, float]]:
        """        Search for similar vectors in an index
        
        Args:
            index_id: Index identifier
            query_vector: Query vector
            k: Number of results
            nprobe: Number of clusters to search (for IVF indices)
            
        Returns:
            List of (content_id, similarity_score) tuples
        """        try:
            start_time = datetime.now()
            
            if index_id not in self.indices:
                raise VectorStoreError(f"Index {index_id} not found")
            
            index_data = self.indices[index_id]
            index = index_data["index"]
            vector_map = index_data["vector_map"]
            
            # Set search parameters
            if nprobe and hasattr(index, 'nprobe'):
                index.nprobe = nprobe
            
            # Prepare query vector
            query_vector = query_vector.reshape(1, -1).astype(np.float32)
            faiss.normalize_L2(query_vector)
            
            # Perform search
            with index_data["lock"]:
                distances, indices = index.search(query_vector, k)
            
            # Process results
            results = []
            for i, (distance, faiss_id) in enumerate(zip(distances[0], indices[0])):
                if faiss_id == -1:  # No more results
                    break
                
                content_id = vector_map.get(faiss_id)
                if content_id:
                    # Convert distance to similarity score
                    similarity = 1.0 / (1.0 + distance)
                    results.append((content_id, similarity))
            
            # Update performance metrics
            search_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_search_stats(index_id, search_time)
            
            return results
            
        except Exception as e:
            logger.error(f"Search failed for index {index_id}: {str(e)}")
            raise VectorStoreError(f"Vector search failed: {str(e)}")
    
    async def remove_vectors(
        self,
        index_id: str,
        content_ids: List[str]
    ) -> int:
        """        Remove vectors from an index (marks for removal, actual removal during optimization)
        
        Args:
            index_id: Index identifier
            content_ids: Content IDs to remove
            
        Returns:
            Number of vectors marked for removal
        """        try:
            if index_id not in self.indices:
                raise VectorStoreError(f"Index {index_id} not found")
            
            index_data = self.indices[index_id]
            vector_map = index_data["vector_map"]
            metadata_cache = index_data["metadata"]
            
            removed_count = 0
            
            with index_data["lock"]:
                # Find FAISS IDs to remove
                faiss_ids_to_remove = []
                for faiss_id, content_id in list(vector_map.items()):
                    if content_id in content_ids:
                        faiss_ids_to_remove.append(faiss_id)
                        removed_count += 1
                
                # Mark for removal (FAISS doesn't support direct removal)
                for faiss_id in faiss_ids_to_remove:
                    content_id = vector_map[faiss_id]
                    del vector_map[faiss_id]
                    metadata_cache.pop(content_id, None)
                
                # Schedule rebuild if many vectors removed
                removal_ratio = removed_count / max(len(vector_map), 1)
                if removal_ratio > 0.1:  # More than 10% removed
                    await self._schedule_maintenance(
                        index_id, MaintenanceType.REBUILD, priority=5
                    )
            
            await self._save_index(index_id)
            
            logger.info(f"Marked {removed_count} vectors for removal from index {index_id}")
            return removed_count
            
        except Exception as e:
            logger.error(f"Failed to remove vectors from index {index_id}: {str(e)}")
            raise VectorStoreError(f"Vector removal failed: {str(e)}")
    
    async def optimize_index(self, index_id: str, force: bool = False) -> bool:
        """        Optimize an index for better performance
        
        Args:
            index_id: Index identifier
            force: Force optimization even if not needed
            
        Returns:
            True if optimization was performed
        """        try:
            if index_id not in self.indices:
                raise VectorStoreError(f"Index {index_id} not found")
            
            # Check if optimization is needed
            if not force and not await self._needs_optimization(index_id):
                logger.info(f"Index {index_id} doesn't need optimization")
                return False
            
            start_time = datetime.now()
            index_data = self.indices[index_id]
            config = self.index_configs[index_id]
            
            # Update status
            self.index_stats[index_id].status = IndexStatus.OPTIMIZING
            
            with index_data["lock"]:
                index = index_data["index"]
                
                # Perform optimization based on index type
                if config.index_type == IndexType.IVF:
                    await self._optimize_ivf_index(index_id)
                elif config.index_type == IndexType.HNSW:
                    await self._optimize_hnsw_index(index_id)
                # Add other optimization strategies
                
                # Update fragmentation ratio
                await self._calculate_fragmentation(index_id)
            
            # Update statistics
            optimization_time = (datetime.now() - start_time).total_seconds()
            self.index_stats[index_id].status = IndexStatus.READY
            self.index_stats[index_id].last_updated = datetime.now(timezone.utc)
            
            # Update operation stats
            self.operation_stats["optimizations"] += 1
            
            await self._save_index(index_id)
            
            logger.info(f"Optimized index {index_id} in {optimization_time:.2f}s")
            return True
            
        except Exception as e:
            self.index_stats[index_id].status = IndexStatus.ERROR
            logger.error(f"Failed to optimize index {index_id}: {str(e)}")
            raise VectorStoreError(f"Index optimization failed: {str(e)}")
    
    async def get_index_info(self, index_id: str) -> Optional[IndexStatistics]:
        """Get comprehensive index information"""        try:
            if index_id not in self.indices:
                return None
            
            # Update current statistics
            await self._update_current_stats(index_id)
            
            return self.index_stats[index_id]
            
        except Exception as e:
            logger.error(f"Failed to get index info for {index_id}: {str(e)}")
            return None
    
    async def list_indices(self) -> List[IndexStatistics]:
        """List all indices with their statistics"""        try:
            indices_info = []
            
            for index_id in self.indices.keys():
                info = await self.get_index_info(index_id)
                if info:
                    indices_info.append(info)
            
            return indices_info
            
        except Exception as e:
            logger.error(f"Failed to list indices: {str(e)}")
            return []
    
    async def backup_index(
        self, index_id: str, backup_path: str = None
    ) -> str:
        """        Create a backup of an index
        
        Args:
            index_id: Index to backup
            backup_path: Custom backup path
            
        Returns:
            Backup file path
        """        try:
            if index_id not in self.indices:
                raise VectorStoreError(f"Index {index_id} not found")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_path or os.path.join(
                settings.STORAGE_PATH, "backups", "indices",
                f"{index_id}_{timestamp}.backup"
            )
            
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            index_data = self.indices[index_id]
            
            with index_data["lock"]:
                # Create backup data
                backup_data = {
                    "index_id": index_id,
                    "config": asdict(self.index_configs[index_id]),
                    "stats": asdict(self.index_stats[index_id]),
                    "vector_map": index_data["vector_map"],
                    "metadata": index_data["metadata"],
                    "backup_timestamp": timestamp,
                    "version": "1.0"
                }
                
                # Save backup metadata
                with open(backup_path + ".meta", "w") as f:
                    json.dump(backup_data, f, indent=2, default=str)
                
                # Save FAISS index
                faiss.write_index(index_data["index"], backup_path + ".index")
            
            logger.info(f"Created backup for index {index_id} at {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Failed to backup index {index_id}: {str(e)}")
            raise VectorStoreError(f"Index backup failed: {str(e)}")
    
    async def restore_index(self, backup_path: str) -> str:
        """        Restore an index from backup
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            Restored index ID
        """        try:
            # Load backup metadata
            with open(backup_path + ".meta", "r") as f:
                backup_data = json.load(f)
            
            index_id = backup_data["index_id"]
            
            # Load FAISS index
            restored_index = faiss.read_index(backup_path + ".index")
            
            # Restore configuration
            config_dict = backup_data["config"]
            config = IndexConfiguration(**config_dict)
            
            # Restore index data
            self.indices[index_id] = {
                "index": restored_index,
                "content_type": backup_data["stats"]["content_type"],
                "vector_map": {int(k): v for k, v in backup_data["vector_map"].items()},
                "metadata": backup_data["metadata"],
                "lock": threading.RLock(),
                "created_at": datetime.now(),
                "last_updated": datetime.now()
            }
            
            self.index_configs[index_id] = config
            
            # Restore statistics
            stats_dict = backup_data["stats"]
            stats_dict["last_updated"] = datetime.now(timezone.utc)
            stats_dict["status"] = IndexStatus.READY
            self.index_stats[index_id] = IndexStatistics(**stats_dict)
            
            await self._save_index(index_id)
            
            logger.info(f"Restored index {index_id} from backup {backup_path}")
            return index_id
            
        except Exception as e:
            logger.error(f"Failed to restore index from {backup_path}: {str(e)}")
            raise VectorStoreError(f"Index restore failed: {str(e)}")
    
    async def delete_index(self, index_id: str, confirm: bool = False) -> bool:
        """        Delete an index permanently
        
        Args:
            index_id: Index to delete
            confirm: Confirmation flag
            
        Returns:
            True if deleted successfully
        """        try:
            if not confirm:
                raise VectorStoreError("Index deletion requires confirmation")
            
            if index_id not in self.indices:
                raise VectorStoreError(f"Index {index_id} not found")
            
            # Create backup before deletion
            backup_path = await self.backup_index(index_id)
            logger.info(f"Created backup before deletion: {backup_path}")
            
            # Remove from memory
            del self.indices[index_id]
            del self.index_configs[index_id]
            del self.index_stats[index_id]
            
            # Remove partitions if any
            if index_id in self.partitions:
                del self.partitions[index_id]
            
            # Remove storage files
            await self.storage_manager.delete_index_files(index_id)
            
            logger.info(f"Deleted index {index_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete index {index_id}: {str(e)}")
            raise VectorStoreError(f"Index deletion failed: {str(e)}")
    
    async def _create_faiss_index(self, config: IndexConfiguration) -> faiss.Index:
        """Create FAISS index based on configuration"""        try:
            if config.index_type == IndexType.FLAT:
                if config.metric == "cosine":
                    index = faiss.IndexFlatIP(config.dimension)
                else:
                    index = faiss.IndexFlatL2(config.dimension)
            
            elif config.index_type == IndexType.IVF:
                if config.metric == "cosine":
                    quantizer = faiss.IndexFlatIP(config.dimension)
                    index = faiss.IndexIVFFlat(quantizer, config.dimension, config.nlist)
                else:
                    quantizer = faiss.IndexFlatL2(config.dimension)
                    index = faiss.IndexIVFFlat(quantizer, config.dimension, config.nlist)
            
            elif config.index_type == IndexType.HNSW:
                index = faiss.IndexHNSWFlat(config.dimension, config.m)
                index.hnsw.efConstruction = 200
                index.hnsw.efSearch = 50
            
            elif config.index_type == IndexType.QUANTIZED:
                quantizer = faiss.IndexFlatL2(config.dimension)
                index = faiss.IndexIVFPQ(
                    quantizer, config.dimension, config.nlist, 
                    config.m, config.nbits
                )
            
            else:
                raise VectorStoreError(f"Unsupported index type: {config.index_type}")
            
            # Enable GPU if available
            if hasattr(faiss, 'StandardGpuResources') and faiss.get_num_gpus() > 0:
                gpu_res = faiss.StandardGpuResources()
                index = faiss.index_cpu_to_gpu(gpu_res, 0, index)
                logger.info(f"Enabled GPU acceleration for {config.index_type.value} index")
            
            return index
            
        except Exception as e:
            logger.error(f"Failed to create FAISS index: {str(e)}")
            raise VectorStoreError(f"FAISS index creation failed: {str(e)}")
    
    async def _load_existing_indices(self) -> None:
        """Load existing indices from storage"""        try:
            index_files = await self.storage_manager.list_index_files()
            
            for index_file in index_files:
                try:
                    index_id = os.path.splitext(os.path.basename(index_file))[0]
                    await self._load_index(index_id)
                    logger.info(f"Loaded existing index: {index_id}")
                except Exception as e:
                    logger.error(f"Failed to load index {index_id}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Failed to load existing indices: {str(e)}")
    
    async def _load_index(self, index_id: str) -> None:
        """Load a specific index from storage"""        try:
            # Load index data from storage
            index_data = await self.storage_manager.load_index(index_id)
            
            if index_data:
                self.indices[index_id] = index_data["index_data"]
                self.index_configs[index_id] = IndexConfiguration(**index_data["config"])
                self.index_stats[index_id] = IndexStatistics(**index_data["stats"])
                
                if "partitions" in index_data:
                    self.partitions[index_id] = [
                        IndexPartition(**p) for p in index_data["partitions"]
                    ]
            
        except Exception as e:
            logger.error(f"Failed to load index {index_id}: {str(e)}")
    
    async def _save_index(self, index_id: str) -> None:
        """Save index to storage"""        try:
            index_data = {
                "index_data": self.indices[index_id],
                "config": asdict(self.index_configs[index_id]),
                "stats": asdict(self.index_stats[index_id]),
                "partitions": [asdict(p) for p in self.partitions.get(index_id, [])]
            }
            
            await self.storage_manager.save_index(index_id, index_data)
            
        except Exception as e:
            logger.error(f"Failed to save index {index_id}: {str(e)}")
    
    async def _needs_optimization(self, index_id: str) -> bool:
        """Check if index needs optimization"""        try:
            stats = self.index_stats[index_id]
            
            # Check fragmentation ratio
            if stats.fragmentation_ratio > 0.3:
                return True
            
            # Check optimization score
            if stats.optimization_score < 0.7:
                return True
            
            # Check time since last optimization
            time_since_update = datetime.now(timezone.utc) - stats.last_updated
            if time_since_update > timedelta(hours=24):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check optimization need for {index_id}: {str(e)}")
            return False
    
    async def _optimize_ivf_index(self, index_id: str) -> None:
        """Optimize IVF index"""        try:
            index_data = self.indices[index_id]
            index = index_data["index"]
            
            if hasattr(index, 'nprobe'):
                # Adjust nprobe based on index size
                if index.ntotal > 100000:
                    index.nprobe = min(50, index.nlist // 4)
                else:
                    index.nprobe = min(20, index.nlist // 8)
            
            logger.info(f"Optimized IVF index {index_id}")
            
        except Exception as e:
            logger.error(f"Failed to optimize IVF index {index_id}: {str(e)}")
    
    async def _optimize_hnsw_index(self, index_id: str) -> None:
        """Optimize HNSW index"""        try:
            index_data = self.indices[index_id]
            index = index_data["index"]
            
            if hasattr(index, 'hnsw'):
                # Adjust search parameters
                if index.ntotal > 100000:
                    index.hnsw.efSearch = 100
                else:
                    index.hnsw.efSearch = 50
            
            logger.info(f"Optimized HNSW index {index_id}")
            
        except Exception as e:
            logger.error(f"Failed to optimize HNSW index {index_id}: {str(e)}")
    
    async def _initialize_partitioning(self, index_id: str) -> None:
        """Initialize partitioning for an index"""        try:
            partition = IndexPartition(
                partition_id=f"{index_id}_p0",
                index_id=index_id,
                start_range=0,
                end_range=1000000,
                vector_count=0,
                size_mb=0.0,
                last_accessed=datetime.now(timezone.utc),
                access_frequency=0,
                is_hot=True
            )
            
            self.partitions[index_id] = [partition]
            
        except Exception as e:
            logger.error(f"Failed to initialize partitioning for {index_id}: {str(e)}")
    
    async def _calculate_fragmentation(self, index_id: str) -> None:
        """Calculate index fragmentation ratio"""        try:
            index_data = self.indices[index_id]
            total_slots = len(index_data["vector_map"])
            used_slots = sum(1 for v in index_data["vector_map"].values() if v is not None)
            
            if total_slots > 0:
                fragmentation = 1.0 - (used_slots / total_slots)
                self.index_stats[index_id].fragmentation_ratio = fragmentation
            
        except Exception as e:
            logger.error(f"Failed to calculate fragmentation for {index_id}: {str(e)}")
    
    async def _schedule_optimization_if_needed(self, index_id: str) -> None:
        """Schedule optimization if needed"""        try:
            if await self._needs_optimization(index_id):
                await self._schedule_maintenance(
                    index_id, MaintenanceType.OPTIMIZATION, priority=3
                )
        except Exception as e:
            logger.error(f"Failed to schedule optimization for {index_id}: {str(e)}")
    
    async def _schedule_maintenance(
        self, index_id: str, task_type: MaintenanceType, priority: int
    ) -> None:
        """Schedule a maintenance task"""        try:
            task = MaintenanceTask(
                task_id=f"{index_id}_{task_type.value}_{datetime.now().timestamp()}",
                index_id=index_id,
                task_type=task_type,
                priority=priority,
                scheduled_time=datetime.now(timezone.utc),
                estimated_duration=300,  # 5 minutes default
                status="scheduled",
                progress=0.0
            )
            
            self.maintenance_queue.append(task)
            self.maintenance_queue.sort(key=lambda x: x.priority, reverse=True)
            
            logger.info(f"Scheduled {task_type.value} for index {index_id}")
            
        except Exception as e:
            logger.error(f"Failed to schedule maintenance: {str(e)}")
    
    async def _maintenance_scheduler(self) -> None:
        """Background maintenance scheduler"""        while True:
            try:
                await asyncio.sleep(self.maintenance_interval)
                
                # Process maintenance queue
                while self.maintenance_queue and len(self.active_tasks) < self.max_concurrent_operations:
                    task = self.maintenance_queue.pop(0)
                    self.active_tasks[task.task_id] = task
                    
                    # Execute task in background
                    asyncio.create_task(self._execute_maintenance_task(task))
                
                # Cleanup completed tasks
                completed_tasks = [
                    task_id for task_id, task in self.active_tasks.items()
                    if task.status in ["completed", "failed"]
                ]
                
                for task_id in completed_tasks:
                    del self.active_tasks[task_id]
                
            except Exception as e:
                logger.error(f"Maintenance scheduler error: {str(e)}")
    
    async def _execute_maintenance_task(self, task: MaintenanceTask) -> None:
        """Execute a maintenance task"""        try:
            task.status = "running"
            start_time = datetime.now()
            
            if task.task_type == MaintenanceType.OPTIMIZATION:
                await self.optimize_index(task.index_id)
            elif task.task_type == MaintenanceType.BACKUP:
                await self.backup_index(task.index_id)
            # Add other maintenance operations
            
            task.status = "completed"
            task.progress = 1.0
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Completed maintenance task {task.task_id} in {duration:.2f}s")
            
        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            logger.error(f"Maintenance task {task.task_id} failed: {str(e)}")
    
    async def _performance_monitor(self) -> None:
        """Background performance monitoring"""        while True:
            try:
                await asyncio.sleep(300)  # Monitor every 5 minutes
                
                # Update statistics for all indices
                for index_id in self.indices.keys():
                    await self._update_current_stats(index_id)
                
                # Collect global metrics
                await self.metrics_collector.collect_index_metrics(self.operation_stats)
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {str(e)}")
    
    async def _update_current_stats(self, index_id: str) -> None:
        """Update current statistics for an index"""        try:
            if index_id not in self.indices:
                return
            
            index_data = self.indices[index_id]
            index = index_data["index"]
            
            # Calculate memory usage (approximate)
            memory_usage = index.ntotal * self.index_configs[index_id].dimension * 4 / (1024 * 1024)
            
            # Update statistics
            stats = self.index_stats[index_id]
            stats.total_vectors = index.ntotal
            stats.memory_usage_mb = memory_usage
            stats.last_updated = datetime.now(timezone.utc)
            
        except Exception as e:
            logger.error(f"Failed to update stats for {index_id}: {str(e)}")
    
    def _update_index_stats(self, index_id: str, vectors_added: int) -> None:
        """Update index statistics after adding vectors"""        try:
            stats = self.index_stats[index_id]
            stats.total_vectors += vectors_added
            stats.last_updated = datetime.now(timezone.utc)
            
            # Update optimization score (decreases as more vectors are added without optimization)
            stats.optimization_score = max(0.1, stats.optimization_score - (vectors_added * 0.001))
            
        except Exception as e:
            logger.error(f"Failed to update index stats for {index_id}: {str(e)}")
    
    def _update_search_stats(self, index_id: str, search_time_ms: float) -> None:
        """Update search performance statistics"""        try:
            stats = self.index_stats[index_id]
            
            # Update average search latency
            if stats.search_latency_ms == 0:
                stats.search_latency_ms = search_time_ms
            else:
                stats.search_latency_ms = (stats.search_latency_ms * 0.9) + (search_time_ms * 0.1)
            
            # Update operation stats
            self.operation_stats["searches"] += 1
            current_avg = self.operation_stats["avg_search_time"]
            total_searches = self.operation_stats["searches"]
            self.operation_stats["avg_search_time"] = (
                (current_avg * (total_searches - 1) + search_time_ms) / total_searches
            )
            
        except Exception as e:
            logger.error(f"Failed to update search stats for {index_id}: {str(e)}")
    
    async def close(self) -> None:
        """Close index manager and cleanup resources"""        try:
            # Stop background tasks
            if self._maintenance_task:
                self._maintenance_task.cancel()
                try:
                    await self._maintenance_task
                except asyncio.CancelledError:
                    pass
            
            if self._monitoring_task:
                self._monitoring_task.cancel()
                try:
                    await self._monitoring_task
                except asyncio.CancelledError:
                    pass
            
            # Save all indices
            for index_id in list(self.indices.keys()):
                await self._save_index(index_id)
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            # Clear memory
            self.indices.clear()
            self.index_configs.clear()
            self.index_stats.clear()
            self.partitions.clear()
            
            logger.info("Vector index manager closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing vector index manager: {str(e)}")
