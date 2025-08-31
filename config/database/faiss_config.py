"""FAISS Vector Database Configuration Module for IA-Influencer Agent Platform
===========================================================================

Professional FAISS (Facebook AI Similarity Search) configuration for content
fingerprinting, similarity matching, and vector-based content protection.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel. 
Any unauthorized use, reproduction, or distribution of this code 
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
import os
import pickle
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import faiss
from faiss import IndexFlatL2, IndexIVFFlat, IndexHNSWFlat, IndexLSH
import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class FAISSEnvironment(Enum):
    """FAISS environment configurations"""    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class FAISSIndexType(Enum):
    """FAISS index types for different use cases"""    FLAT_L2 = "flat_l2"  # Exact search, small datasets
    IVF_FLAT = "ivf_flat"  # Fast search with clustering
    HNSW_FLAT = "hnsw_flat"  # Hierarchical graph-based
    LSH = "lsh"  # Locality Sensitive Hashing
    PQ = "pq"  # Product Quantization
    IVF_PQ = "ivf_pq"  # IVF + Product Quantization


class FAISSContentType(Enum):
    """Content types for vector indexing"""    AUDIO_FINGERPRINT = "audio_fingerprint"
    VIDEO_FINGERPRINT = "video_fingerprint"
    IMAGE_FINGERPRINT = "image_fingerprint"
    TEXT_EMBEDDING = "text_embedding"
    MULTIMODAL_EMBEDDING = "multimodal_embedding"


@dataclass
class FAISSIndexConfig:
    """FAISS index configuration"""    index_type: FAISSIndexType
    dimension: int
    nlist: Optional[int] = None  # For IVF indexes
    nprobe: Optional[int] = None  # Search parameter for IVF
    m: Optional[int] = None  # For HNSW and PQ
    ef_construction: Optional[int] = None  # For HNSW
    ef_search: Optional[int] = None  # For HNSW
    nbits: Optional[int] = None  # For LSH
    use_gpu: bool = False
    gpu_ids: List[int] = field(default_factory=list)


@dataclass
class FAISSPerformanceConfig:
    """FAISS performance optimization settings"""    batch_size: int = 1000
    max_memory_mb: int = 1024
    parallel_search_threads: int = 4
    index_cache_size: int = 100
    similarity_threshold: float = 0.8
    max_results: int = 100
    use_omp_threads: bool = True
    omp_num_threads: int = 4


@dataclass
class FAISSStorageConfig:
    """FAISS storage and persistence configuration"""    base_path: str = "/data/faiss_indexes"
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    compression_enabled: bool = True
    metadata_storage: str = "json"  # json, pickle, parquet
    versioning_enabled: bool = True
    max_versions: int = 10


class FAISSConfig:
    """    Professional FAISS configuration manager for IA-Influencer Agent Platform
    
    Manages vector indexing for content fingerprinting, similarity search,
    and content protection across audio, video, image, and text content.
    """
    def __init__(self, 
                 environment: FAISSEnvironment = FAISSEnvironment.DEVELOPMENT,
                 content_type: FAISSContentType = FAISSContentType.AUDIO_FINGERPRINT):
        self.environment = environment
        self.content_type = content_type
        self.index_configs = self._get_index_configs()
        self.performance_config = self._get_performance_config()
        self.storage_config = self._get_storage_config()
        self._indexes: Dict[str, faiss.Index] = {}
        self._index_metadata: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._setup_logging()
        self._setup_directories()
        self._configure_faiss()

    def _setup_logging(self) -> None:
        """Setup FAISS-specific logging"""        self.logger = logging.getLogger(f"faiss.{self.environment.value}.{self.content_type.value}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _setup_directories(self) -> None:
        """Setup FAISS storage directories"""        try:
            base_path = Path(self.storage_config.base_path)
            base_path.mkdir(parents=True, exist_ok=True)
            
            # Create environment and content type specific directories
            env_path = base_path / self.environment.value
            env_path.mkdir(exist_ok=True)
            
            content_path = env_path / self.content_type.value
            content_path.mkdir(exist_ok=True)
            
            # Create subdirectories
            (content_path / "indexes").mkdir(exist_ok=True)
            (content_path / "metadata").mkdir(exist_ok=True)
            (content_path / "backups").mkdir(exist_ok=True)
            (content_path / "versions").mkdir(exist_ok=True)
            
            self.logger.info(f"FAISS directories setup completed: {content_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to setup FAISS directories: {str(e)}")
            raise

    def _configure_faiss(self) -> None:
        """Configure FAISS global settings"""        try:
            # Set OpenMP threads if enabled
            if self.performance_config.use_omp_threads:
                faiss.omp_set_num_threads(self.performance_config.omp_num_threads)
            
            self.logger.info("FAISS global configuration completed")
            
        except Exception as e:
            self.logger.error(f"Failed to configure FAISS: {str(e)}")
            raise

    def _get_index_configs(self) -> Dict[FAISSContentType, FAISSIndexConfig]:
        """Get index configurations for different content types"""        configs = {
            FAISSContentType.AUDIO_FINGERPRINT: FAISSIndexConfig(
                index_type=FAISSIndexType.IVF_FLAT,
                dimension=1024,  # Chromaprint/audio feature dimension
                nlist=1000,
                nprobe=10,
                use_gpu=self.environment == FAISSEnvironment.PRODUCTION
            ),
            FAISSContentType.VIDEO_FINGERPRINT: FAISSIndexConfig(
                index_type=FAISSIndexType.HNSW_FLAT,
                dimension=2048,  # Video feature dimension
                m=16,
                ef_construction=200,
                ef_search=50,
                use_gpu=self.environment == FAISSEnvironment.PRODUCTION
            ),
            FAISSContentType.IMAGE_FINGERPRINT: FAISSIndexConfig(
                index_type=FAISSIndexType.IVF_PQ,
                dimension=512,  # Image feature dimension (ResNet/CLIP)
                nlist=500,
                nprobe=5,
                m=64,
                use_gpu=self.environment == FAISSEnvironment.PRODUCTION
            ),
            FAISSContentType.TEXT_EMBEDDING: FAISSIndexConfig(
                index_type=FAISSIndexType.IVF_FLAT,
                dimension=768,  # BERT/RoBERTa embedding dimension
                nlist=100,
                nprobe=5,
                use_gpu=False  # Text embeddings typically don't need GPU
            ),
            FAISSContentType.MULTIMODAL_EMBEDDING: FAISSIndexConfig(
                index_type=FAISSIndexType.HNSW_FLAT,
                dimension=1536,  # Combined multimodal features
                m=32,
                ef_construction=400,
                ef_search=100,
                use_gpu=self.environment == FAISSEnvironment.PRODUCTION
            )
        }
        
        return configs

    def _get_performance_config(self) -> FAISSPerformanceConfig:
        """Get performance configuration based on environment"""        configs = {
            FAISSEnvironment.DEVELOPMENT: FAISSPerformanceConfig(
                batch_size=100,
                max_memory_mb=512,
                parallel_search_threads=2,
                omp_num_threads=2
            ),
            FAISSEnvironment.STAGING: FAISSPerformanceConfig(
                batch_size=500,
                max_memory_mb=1024,
                parallel_search_threads=4,
                omp_num_threads=4
            ),
            FAISSEnvironment.PRODUCTION: FAISSPerformanceConfig(
                batch_size=1000,
                max_memory_mb=4096,
                parallel_search_threads=8,
                index_cache_size=500,
                omp_num_threads=8
            ),
            FAISSEnvironment.TESTING: FAISSPerformanceConfig(
                batch_size=50,
                max_memory_mb=256,
                parallel_search_threads=1,
                omp_num_threads=1
            )
        }
        
        return configs.get(self.environment, FAISSPerformanceConfig())

    def _get_storage_config(self) -> FAISSStorageConfig:
        """Get storage configuration based on environment"""        base_path = os.getenv(f"FAISS_STORAGE_PATH_{self.environment.value.upper()}", 
                             f"/data/faiss_{self.environment.value}")
        
        if self.environment == FAISSEnvironment.PRODUCTION:
            return FAISSStorageConfig(
                base_path=base_path,
                backup_enabled=True,
                backup_interval_hours=12,
                compression_enabled=True,
                versioning_enabled=True,
                max_versions=20
            )
        elif self.environment == FAISSEnvironment.STAGING:
            return FAISSStorageConfig(
                base_path=base_path,
                backup_enabled=True,
                backup_interval_hours=24,
                versioning_enabled=True,
                max_versions=10
            )
        else:
            return FAISSStorageConfig(
                base_path=base_path,
                backup_enabled=False,
                versioning_enabled=False
            )

    def create_index(self, 
                    content_type: Optional[FAISSContentType] = None,
                    custom_config: Optional[FAISSIndexConfig] = None) -> faiss.Index:
        """        Create FAISS index based on content type and configuration
        
        Args:
            content_type: Type of content for the index
            custom_config: Custom index configuration
            
        Returns:
            Configured FAISS index
        """        content_type = content_type or self.content_type
        config = custom_config or self.index_configs[content_type]
        
        index_key = f"{content_type.value}_{config.index_type.value}"
        
        with self._lock:
            if index_key in self._indexes:
                return self._indexes[index_key]
            
            try:
                index = self._create_index_by_type(config)
                
                # Move to GPU if configured
                if config.use_gpu and config.gpu_ids:
                    index = self._move_to_gpu(index, config.gpu_ids)
                
                self._indexes[index_key] = index
                self._index_metadata[index_key] = {
                    "content_type": content_type.value,
                    "config": config,
                    "created_at": time.time(),
                    "total_vectors": 0,
                    "last_updated": time.time()
                }
                
                self.logger.info(f"FAISS index created: {index_key}")
                return index
                
            except Exception as e:
                self.logger.error(f"Failed to create FAISS index {index_key}: {str(e)}")
                raise

    def _create_index_by_type(self, config: FAISSIndexConfig) -> faiss.Index:
        """Create index based on specified type"""        if config.index_type == FAISSIndexType.FLAT_L2:
            return IndexFlatL2(config.dimension)
        
        elif config.index_type == FAISSIndexType.IVF_FLAT:
            quantizer = IndexFlatL2(config.dimension)
            index = IndexIVFFlat(quantizer, config.dimension, config.nlist)
            return index
        
        elif config.index_type == FAISSIndexType.HNSW_FLAT:
            index = IndexHNSWFlat(config.dimension, config.m)
            index.hnsw.efConstruction = config.ef_construction
            index.hnsw.efSearch = config.ef_search
            return index
        
        elif config.index_type == FAISSIndexType.LSH:
            return IndexLSH(config.dimension, config.nbits or (config.dimension // 8))
        
        elif config.index_type == FAISSIndexType.PQ:
            return faiss.IndexPQ(config.dimension, config.m, 8)  # 8 bits per sub-quantizer
        
        elif config.index_type == FAISSIndexType.IVF_PQ:
            quantizer = IndexFlatL2(config.dimension)
            return faiss.IndexIVFPQ(quantizer, config.dimension, config.nlist, config.m, 8)
        
        else:
            raise ValueError(f"Unsupported index type: {config.index_type}")

    def _move_to_gpu(self, index: faiss.Index, gpu_ids: List[int]) -> faiss.Index:
        """Move index to GPU(s)"""        try:
            if len(gpu_ids) == 1:
                # Single GPU
                res = faiss.StandardGpuResources()
                return faiss.index_cpu_to_gpu(res, gpu_ids[0], index)
            else:
                # Multiple GPUs
                return faiss.index_cpu_to_all_gpus(index, ngpu=len(gpu_ids))
        except Exception as e:
            self.logger.warning(f"Failed to move index to GPU: {str(e)}, using CPU")
            return index

    def add_vectors(self, 
                   index_key: str, 
                   vectors: np.ndarray, 
                   ids: Optional[np.ndarray] = None) -> None:
        """        Add vectors to FAISS index
        
        Args:
            index_key: Index identifier
            vectors: Vector array to add
            ids: Optional vector IDs
        """        with self._lock:
            if index_key not in self._indexes:
                raise ValueError(f"Index {index_key} not found")
            
            index = self._indexes[index_key]
            
            try:
                # Validate vector dimensions
                config = self._index_metadata[index_key]["config"]
                if vectors.shape[1] != config.dimension:
                    raise ValueError(f"Vector dimension mismatch: expected {config.dimension}, got {vectors.shape[1]}")
                
                # Ensure vectors are float32
                if vectors.dtype != np.float32:
                    vectors = vectors.astype(np.float32)
                
                # Train index if needed (for IVF-based indexes)
                if not index.is_trained and hasattr(index, 'train'):
                    self.logger.info(f"Training index {index_key} with {len(vectors)} vectors")
                    index.train(vectors)
                
                # Add vectors
                if ids is not None:
                    if len(ids) != len(vectors):
                        raise ValueError("Number of IDs must match number of vectors")
                    
                    # For indexes that support IDs
                    if hasattr(index, 'add_with_ids'):
                        index.add_with_ids(vectors, ids.astype(np.int64))
                    else:
                        index.add(vectors)
                        self.logger.warning(f"Index {index_key} does not support IDs, added vectors without IDs")
                else:
                    index.add(vectors)
                
                # Update metadata
                self._index_metadata[index_key]["total_vectors"] += len(vectors)
                self._index_metadata[index_key]["last_updated"] = time.time()
                
                self.logger.info(f"Added {len(vectors)} vectors to index {index_key}")
                
            except Exception as e:
                self.logger.error(f"Failed to add vectors to index {index_key}: {str(e)}")
                raise

    def search_similar(self, 
                      index_key: str, 
                      query_vector: np.ndarray, 
                      k: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """        Search for similar vectors in FAISS index
        
        Args:
            index_key: Index identifier
            query_vector: Query vector
            k: Number of nearest neighbors to return
            
        Returns:
            Tuple of (distances, indices)
        """        with self._lock:
            if index_key not in self._indexes:
                raise ValueError(f"Index {index_key} not found")
            
            index = self._indexes[index_key]
            
            try:
                # Validate query vector
                config = self._index_metadata[index_key]["config"]
                if query_vector.shape[-1] != config.dimension:
                    raise ValueError(f"Query vector dimension mismatch: expected {config.dimension}, got {query_vector.shape[-1]}")
                
                # Ensure proper shape and type
                if query_vector.ndim == 1:
                    query_vector = query_vector.reshape(1, -1)
                
                if query_vector.dtype != np.float32:
                    query_vector = query_vector.astype(np.float32)
                
                # Perform search
                distances, indices = index.search(query_vector, k)
                
                return distances[0], indices[0]
                
            except Exception as e:
                self.logger.error(f"Failed to search index {index_key}: {str(e)}")
                raise

    def batch_search(self, 
                    index_key: str, 
                    query_vectors: np.ndarray, 
                    k: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """        Batch search for similar vectors
        
        Args:
            index_key: Index identifier
            query_vectors: Query vectors array
            k: Number of nearest neighbors to return per query
            
        Returns:
            Tuple of (distances, indices) arrays
        """        with self._lock:
            if index_key not in self._indexes:
                raise ValueError(f"Index {index_key} not found")
            
            index = self._indexes[index_key]
            
            try:
                # Process in batches to manage memory
                batch_size = self.performance_config.batch_size
                all_distances = []
                all_indices = []
                
                for i in range(0, len(query_vectors), batch_size):
                    batch = query_vectors[i:i + batch_size]
                    
                    if batch.dtype != np.float32:
                        batch = batch.astype(np.float32)
                    
                    distances, indices = index.search(batch, k)
                    all_distances.append(distances)
                    all_indices.append(indices)
                
                return np.vstack(all_distances), np.vstack(all_indices)
                
            except Exception as e:
                self.logger.error(f"Failed to batch search index {index_key}: {str(e)}")
                raise

    def save_index(self, index_key: str, version: Optional[str] = None) -> str:
        """        Save FAISS index to disk
        
        Args:
            index_key: Index identifier
            version: Optional version string
            
        Returns:
            Path to saved index file
        """        with self._lock:
            if index_key not in self._indexes:
                raise ValueError(f"Index {index_key} not found")
            
            try:
                # Generate file paths
                base_path = Path(self.storage_config.base_path) / self.environment.value / self.content_type.value
                
                if version:
                    save_path = base_path / "versions" / f"{index_key}_v{version}.index"
                else:
                    save_path = base_path / "indexes" / f"{index_key}.index"
                
                metadata_path = save_path.with_suffix('.metadata.pkl')
                
                # Save index
                index = self._indexes[index_key]
                faiss.write_index(index, str(save_path))
                
                # Save metadata
                with open(metadata_path, 'wb') as f:
                    pickle.dump(self._index_metadata[index_key], f)
                
                self.logger.info(f"FAISS index saved: {save_path}")
                return str(save_path)
                
            except Exception as e:
                self.logger.error(f"Failed to save index {index_key}: {str(e)}")
                raise

    def load_index(self, index_key: str, file_path: Optional[str] = None) -> faiss.Index:
        """        Load FAISS index from disk
        
        Args:
            index_key: Index identifier
            file_path: Optional specific file path
            
        Returns:
            Loaded FAISS index
        """        with self._lock:
            try:
                if file_path:
                    load_path = Path(file_path)
                else:
                    base_path = Path(self.storage_config.base_path) / self.environment.value / self.content_type.value
                    load_path = base_path / "indexes" / f"{index_key}.index"
                
                metadata_path = load_path.with_suffix('.metadata.pkl')
                
                if not load_path.exists():
                    raise FileNotFoundError(f"Index file not found: {load_path}")
                
                # Load index
                index = faiss.read_index(str(load_path))
                
                # Load metadata if available
                if metadata_path.exists():
                    with open(metadata_path, 'rb') as f:
                        metadata = pickle.load(f)
                        self._index_metadata[index_key] = metadata
                
                self._indexes[index_key] = index
                
                self.logger.info(f"FAISS index loaded: {load_path}")
                return index
                
            except Exception as e:
                self.logger.error(f"Failed to load index {index_key}: {str(e)}")
                raise

    def get_index_stats(self, index_key: str) -> Dict[str, Any]:
        """        Get statistics about FAISS index
        
        Args:
            index_key: Index identifier
            
        Returns:
            Index statistics dictionary
        """        with self._lock:
            if index_key not in self._indexes:
                raise ValueError(f"Index {index_key} not found")
            
            index = self._indexes[index_key]
            metadata = self._index_metadata[index_key]
            
            stats = {
                "index_key": index_key,
                "content_type": metadata["content_type"],
                "index_type": metadata["config"].index_type.value,
                "dimension": metadata["config"].dimension,
                "total_vectors": index.ntotal,
                "is_trained": index.is_trained,
                "memory_usage_bytes": index.d * index.ntotal * 4,  # Approximate for float32
                "created_at": metadata["created_at"],
                "last_updated": metadata["last_updated"]
            }
            
            # Add type-specific stats
            if hasattr(index, 'nlist'):
                stats["nlist"] = index.nlist
            if hasattr(index, 'nprobe'):
                stats["nprobe"] = index.nprobe
            
            return stats

    def health_check(self) -> Dict[str, Any]:
        """        Perform comprehensive health check on FAISS indexes
        
        Returns:
            Health check results dictionary
        """        health_status = {
            "status": "healthy",
            "environment": self.environment.value,
            "content_type": self.content_type.value,
            "indexes": {},
            "storage": {},
            "timestamp": None
        }
        
        import datetime
        health_status["timestamp"] = datetime.datetime.utcnow().isoformat()
        
        try:
            # Check each index
            with self._lock:
                for index_key, index in self._indexes.items():
                    try:
                        stats = self.get_index_stats(index_key)
                        health_status["indexes"][index_key] = {
                            "status": "healthy",
                            **stats
                        }
                    except Exception as e:
                        health_status["indexes"][index_key] = {
                            "status": "unhealthy",
                            "error": str(e)
                        }
            
            # Check storage
            base_path = Path(self.storage_config.base_path)
            if base_path.exists():
                storage_info = os.statvfs(base_path)
                total_space = storage_info.f_frsize * storage_info.f_blocks
                free_space = storage_info.f_frsize * storage_info.f_available
                
                health_status["storage"] = {
                    "status": "healthy",
                    "base_path": str(base_path),
                    "total_space_gb": round(total_space / (1024**3), 2),
                    "free_space_gb": round(free_space / (1024**3), 2),
                    "usage_percent": round((total_space - free_space) / total_space * 100, 2)
                }
            else:
                health_status["storage"] = {
                    "status": "unhealthy",
                    "error": f"Storage path does not exist: {base_path}"
                }
                
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            self.logger.error(f"FAISS health check failed: {str(e)}")
        
        return health_status

    def cleanup_old_versions(self, max_versions: Optional[int] = None) -> None:
        """        Cleanup old index versions
        
        Args:
            max_versions: Maximum versions to keep (uses config default if None)
        """        if not self.storage_config.versioning_enabled:
            return
        
        max_versions = max_versions or self.storage_config.max_versions
        
        try:
            versions_path = Path(self.storage_config.base_path) / self.environment.value / self.content_type.value / "versions"
            
            if not versions_path.exists():
                return
            
            # Group files by index name
            version_files = {}
            for file_path in versions_path.glob("*.index"):
                # Extract index name from filename (remove version suffix)
                base_name = file_path.stem.split('_v')[0]
                if base_name not in version_files:
                    version_files[base_name] = []
                version_files[base_name].append(file_path)
            
            # Cleanup old versions for each index
            for index_name, files in version_files.items():
                if len(files) > max_versions:
                    # Sort by modification time and remove oldest
                    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                    
                    for old_file in files[max_versions:]:
                        try:
                            old_file.unlink()
                            # Also remove corresponding metadata file
                            metadata_file = old_file.with_suffix('.metadata.pkl')
                            if metadata_file.exists():
                                metadata_file.unlink()
                            
                            self.logger.info(f"Removed old version: {old_file}")
                        except Exception as e:
                            self.logger.error(f"Failed to remove {old_file}: {str(e)}")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old versions: {str(e)}")

    def close_all_indexes(self) -> None:
        """Close all indexes and cleanup resources"""        with self._lock:
            for index_key in list(self._indexes.keys()):
                try:
                    # Save index before closing if configured
                    if self.storage_config.backup_enabled:
                        self.save_index(index_key)
                    
                    del self._indexes[index_key]
                    del self._index_metadata[index_key]
                    
                    self.logger.info(f"Closed FAISS index: {index_key}")
                except Exception as e:
                    self.logger.error(f"Error closing index {index_key}: {str(e)}")

    def __del__(self):
        """Cleanup on object destruction"""        try:
            self.close_all_indexes()
        except:
            pass
