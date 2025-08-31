"""Vector Database Configuration Module for IA-Influencer Agent Platform
===================================================================

Professional vector database configuration for content fingerprinting, similarity search,
and AI-powered content protection systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel. 
Any unauthorized use, reproduction, or distribution of this code 
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""import os
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import faiss
import json
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

logger = logging.getLogger(__name__)


class VectorIndexType(Enum):
    """Vector index types for different use cases"""    FLAT = "flat"  # Exact search
    IVF_FLAT = "ivf_flat"  # Fast approximate search
    IVF_PQ = "ivf_pq"  # Memory optimized
    HNSW = "hnsw"  # Hierarchical navigable small world
    LSH = "lsh"  # Locality sensitive hashing


class SimilarityMetric(Enum):
    """Similarity metrics for vector comparison"""    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    INNER_PRODUCT = "inner_product"
    HAMMING = "hamming"


class ContentType(Enum):
    """Content types for fingerprinting"""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MIXED_MEDIA = "mixed_media"


@dataclass
class VectorDatabaseCredentials:
    """Vector database authentication credentials"""    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    environment: str = "development"


@dataclass
class IndexConfiguration:
    """Configuration for vector index"""    index_type: VectorIndexType
    dimension: int
    similarity_metric: SimilarityMetric
    nlist: int = 100  # Number of clusters for IVF
    nprobe: int = 10  # Number of clusters to search
    m: int = 8  # Number of sub-quantizers for PQ
    nbits: int = 8  # Number of bits per sub-quantizer
    ef_construction: int = 200  # HNSW construction parameter
    ef_search: int = 100  # HNSW search parameter
    max_connections: int = 16  # HNSW max connections


@dataclass
class VectorDatabaseConfig:
    """Professional vector database configuration"""    # Core configuration
    host: str = "localhost"
    port: int = 8000
    database_name: str = "ia_influencer_vectors"
    credentials: VectorDatabaseCredentials = field(default_factory=VectorDatabaseCredentials)
    
    # Storage configuration
    index_storage_path: str = "/data/vector_indexes"
    backup_storage_path: str = "/data/vector_backups"
    temp_storage_path: str = "/tmp/vector_processing"
    
    # Performance configuration
    max_memory_usage_gb: float = 8.0
    batch_size: int = 1000
    max_connections: int = 100
    connection_timeout: int = 30
    query_timeout: int = 60
    
    # Content fingerprinting configuration
    audio_index_config: IndexConfiguration = field(
        default_factory=lambda: IndexConfiguration(
            index_type=VectorIndexType.IVF_FLAT,
            dimension=1024,
            similarity_metric=SimilarityMetric.COSINE,
            nlist=256,
            nprobe=32
        )
    )
    
    video_index_config: IndexConfiguration = field(
        default_factory=lambda: IndexConfiguration(
            index_type=VectorIndexType.HNSW,
            dimension=2048,
            similarity_metric=SimilarityMetric.EUCLIDEAN,
            ef_construction=400,
            ef_search=200
        )
    )
    
    image_index_config: IndexConfiguration = field(
        default_factory=lambda: IndexConfiguration(
            index_type=VectorIndexType.IVF_PQ,
            dimension=512,
            similarity_metric=SimilarityMetric.COSINE,
            nlist=128,
            nprobe=16,
            m=16,
            nbits=8
        )
    )
    
    text_index_config: IndexConfiguration = field(
        default_factory=lambda: IndexConfiguration(
            index_type=VectorIndexType.FLAT,
            dimension=768,
            similarity_metric=SimilarityMetric.COSINE
        )
    )
    
    # Quality thresholds for content protection
    similarity_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "exact_match": 0.95,
        "near_duplicate": 0.85,
        "similar": 0.70,
        "related": 0.50,
        "different": 0.30
    })
    
    # Index management
    auto_rebuild_threshold: float = 0.3  # Rebuild when index size increases by 30%
    auto_backup_interval_hours: int = 24
    index_compression_enabled: bool = True
    
    # Monitoring and logging
    enable_performance_monitoring: bool = True
    enable_query_logging: bool = True
    log_slow_queries_threshold_ms: int = 1000


class VectorDatabaseManager:
    """Professional vector database management system"""    
    def __init__(self, config: VectorDatabaseConfig):
        self.config = config
        self.indexes: Dict[str, faiss.Index] = {}
        self.index_metadata: Dict[str, Dict] = {}
        self.executor = ThreadPoolExecutor(max_workers=8)
        self._setup_storage_directories()
        
    def _setup_storage_directories(self):
        """Create necessary storage directories"""        for path in [
            self.config.index_storage_path,
            self.config.backup_storage_path,
            self.config.temp_storage_path
        ]:
            Path(path).mkdir(parents=True, exist_ok=True)
            
    def _create_faiss_index(self, config: IndexConfiguration) -> faiss.Index:
        """Create FAISS index based on configuration"""        dimension = config.dimension
        
        if config.index_type == VectorIndexType.FLAT:
            if config.similarity_metric == SimilarityMetric.COSINE:
                index = faiss.IndexFlatIP(dimension)
            else:
                index = faiss.IndexFlatL2(dimension)
                
        elif config.index_type == VectorIndexType.IVF_FLAT:
            quantizer = faiss.IndexFlatL2(dimension)
            index = faiss.IndexIVFFlat(quantizer, dimension, config.nlist)
            
        elif config.index_type == VectorIndexType.IVF_PQ:
            quantizer = faiss.IndexFlatL2(dimension)
            index = faiss.IndexIVFPQ(
                quantizer, dimension, config.nlist, 
                config.m, config.nbits
            )
            
        elif config.index_type == VectorIndexType.HNSW:
            index = faiss.IndexHNSWFlat(dimension, config.max_connections)
            index.hnsw.efConstruction = config.ef_construction
            
        else:
            # Fallback to flat index
            index = faiss.IndexFlatL2(dimension)
            
        return index
        
    async def initialize_indexes(self) -> Dict[str, bool]:
        """Initialize all vector indexes"""        results = {}
        
        try:
            # Initialize content type indexes
            content_configs = {
                ContentType.AUDIO: self.config.audio_index_config,
                ContentType.VIDEO: self.config.video_index_config,
                ContentType.IMAGE: self.config.image_index_config,
                ContentType.TEXT: self.config.text_index_config
            }
            
            for content_type, index_config in content_configs.items():
                index_name = f"{content_type.value}_fingerprints"
                
                # Create index
                index = self._create_faiss_index(index_config)
                
                # Load existing index if available
                index_path = os.path.join(
                    self.config.index_storage_path, 
                    f"{index_name}.faiss"
                )
                
                if os.path.exists(index_path):
                    try:
                        index = faiss.read_index(index_path)
                        logger.info(f"Loaded existing index: {index_name}")
                    except Exception as e:
                        logger.warning(f"Failed to load index {index_name}: {e}")
                        
                self.indexes[index_name] = index
                self.index_metadata[index_name] = {
                    "content_type": content_type.value,
                    "config": index_config,
                    "created_at": time.time(),
                    "last_updated": time.time(),
                    "vector_count": index.ntotal
                }
                
                results[index_name] = True
                logger.info(f"Initialized index: {index_name}")
                
        except Exception as e:
            logger.error(f"Error initializing indexes: {e}")
            results["error"] = str(e)
            
        return results
        
    async def add_vectors(
        self, 
        index_name: str, 
        vectors: np.ndarray,
        ids: Optional[List[int]] = None
    ) -> bool:
        """Add vectors to specified index"""        try:
            if index_name not in self.indexes:
                raise ValueError(f"Index {index_name} not found")
                
            index = self.indexes[index_name]
            
            # Ensure vectors are float32
            if vectors.dtype != np.float32:
                vectors = vectors.astype(np.float32)
                
            # Normalize vectors for cosine similarity
            content_type = self.index_metadata[index_name]["content_type"]
            config = self.index_metadata[index_name]["config"]
            
            if config.similarity_metric == SimilarityMetric.COSINE:
                faiss.normalize_L2(vectors)
                
            # Add vectors
            if hasattr(index, 'train') and not index.is_trained:
                index.train(vectors)
                
            if ids:
                index.add_with_ids(vectors, np.array(ids, dtype=np.int64))
            else:
                index.add(vectors)
                
            # Update metadata
            self.index_metadata[index_name]["vector_count"] = index.ntotal
            self.index_metadata[index_name]["last_updated"] = time.time()
            
            logger.info(
                f"Added {len(vectors)} vectors to {index_name}. "
                f"Total: {index.ntotal}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Error adding vectors to {index_name}: {e}")
            return False
            
    async def search_similar(
        self,
        index_name: str,
        query_vector: np.ndarray,
        top_k: int = 10,
        threshold: Optional[float] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Search for similar vectors"""        try:
            if index_name not in self.indexes:
                raise ValueError(f"Index {index_name} not found")
                
            index = self.indexes[index_name]
            config = self.index_metadata[index_name]["config"]
            
            # Ensure query vector is float32
            if query_vector.dtype != np.float32:
                query_vector = query_vector.astype(np.float32)
                
            # Reshape if needed
            if len(query_vector.shape) == 1:
                query_vector = query_vector.reshape(1, -1)
                
            # Normalize for cosine similarity
            if config.similarity_metric == SimilarityMetric.COSINE:
                faiss.normalize_L2(query_vector)
                
            # Set search parameters for IVF indexes
            if hasattr(index, 'nprobe'):
                index.nprobe = config.nprobe
                
            # Perform search
            distances, indices = index.search(query_vector, top_k)
            
            # Apply threshold if specified
            if threshold is not None:
                mask = distances[0] >= threshold
                distances = distances[0][mask]
                indices = indices[0][mask]
            else:
                distances = distances[0]
                indices = indices[0]
                
            return distances, indices
            
        except Exception as e:
            logger.error(f"Error searching in {index_name}: {e}")
            return np.array([]), np.array([])
            
    async def save_indexes(self) -> Dict[str, bool]:
        """Save all indexes to disk"""        results = {}
        
        for index_name, index in self.indexes.items():
            try:
                index_path = os.path.join(
                    self.config.index_storage_path,
                    f"{index_name}.faiss"
                )
                
                # Save index
                faiss.write_index(index, index_path)
                
                # Save metadata
                metadata_path = os.path.join(
                    self.config.index_storage_path,
                    f"{index_name}_metadata.json"
                )
                
                with open(metadata_path, 'w') as f:
                    # Convert non-serializable objects
                    metadata = self.index_metadata[index_name].copy()
                    metadata['config'] = {
                        'index_type': metadata['config'].index_type.value,
                        'dimension': metadata['config'].dimension,
                        'similarity_metric': metadata['config'].similarity_metric.value
                    }
                    json.dump(metadata, f, indent=2)
                    
                results[index_name] = True
                logger.info(f"Saved index: {index_name}")
                
            except Exception as e:
                logger.error(f"Error saving index {index_name}: {e}")
                results[index_name] = False
                
        return results
        
    async def get_index_statistics(self, index_name: str) -> Dict[str, Any]:
        """Get statistics for specific index"""        if index_name not in self.indexes:
            return {"error": "Index not found"}
            
        index = self.indexes[index_name]
        metadata = self.index_metadata[index_name]
        
        return {
            "index_name": index_name,
            "content_type": metadata["content_type"],
            "vector_count": index.ntotal,
            "dimension": metadata["config"].dimension,
            "index_type": metadata["config"].index_type.value,
            "similarity_metric": metadata["config"].similarity_metric.value,
            "is_trained": getattr(index, 'is_trained', True),
            "memory_usage_mb": self._estimate_index_memory(index),
            "created_at": metadata["created_at"],
            "last_updated": metadata["last_updated"]
        }
        
    def _estimate_index_memory(self, index: faiss.Index) -> float:
        """Estimate memory usage of index in MB"""        # Rough estimation based on vector count and dimension
        vector_count = index.ntotal
        if hasattr(index, 'd'):
            dimension = index.d
        else:
            dimension = 512  # Default estimate
            
        # 4 bytes per float32 value
        estimated_bytes = vector_count * dimension * 4
        return estimated_bytes / (1024 * 1024)  # Convert to MB
        
    async def backup_indexes(self) -> Dict[str, str]:
        """Create backup of all indexes"""        results = {}
        timestamp = int(time.time())
        
        for index_name in self.indexes:
            try:
                backup_dir = os.path.join(
                    self.config.backup_storage_path,
                    f"backup_{timestamp}"
                )
                os.makedirs(backup_dir, exist_ok=True)
                
                # Backup index file
                source_path = os.path.join(
                    self.config.index_storage_path,
                    f"{index_name}.faiss"
                )
                backup_path = os.path.join(
                    backup_dir,
                    f"{index_name}.faiss"
                )
                
                if os.path.exists(source_path):
                    import shutil
                    shutil.copy2(source_path, backup_path)
                    results[index_name] = backup_path
                    
            except Exception as e:
                logger.error(f"Error backing up {index_name}: {e}")
                results[index_name] = f"Error: {e}"
                
        return results
        
    async def cleanup_old_backups(self, keep_days: int = 7) -> int:
        """Clean up old backup files"""        try:
            cutoff_time = time.time() - (keep_days * 24 * 3600)
            removed_count = 0
            
            backup_dir = Path(self.config.backup_storage_path)
            for backup_folder in backup_dir.iterdir():
                if backup_folder.is_dir() and backup_folder.name.startswith("backup_"):
                    try:
                        timestamp = int(backup_folder.name.split("_")[1])
                        if timestamp < cutoff_time:
                            import shutil
                            shutil.rmtree(backup_folder)
                            removed_count += 1
                    except (ValueError, IndexError):
                        continue
                        
            logger.info(f"Cleaned up {removed_count} old backups")
            return removed_count
            
        except Exception as e:
            logger.error(f"Error cleaning up backups: {e}")
            return 0


def create_vector_database_config(
    environment: str = "development",
    custom_settings: Optional[Dict[str, Any]] = None
) -> VectorDatabaseConfig:
    """Factory function to create vector database configuration"""    
    # Environment-specific defaults
    config_defaults = {
        "development": {
            "host": "localhost",
            "port": 8000,
            "max_memory_usage_gb": 2.0,
            "batch_size": 100,
            "enable_performance_monitoring": True
        },
        "staging": {
            "host": os.getenv("VECTOR_DB_HOST", "vector-db-staging"),
            "port": int(os.getenv("VECTOR_DB_PORT", "8000")),
            "max_memory_usage_gb": 4.0,
            "batch_size": 500,
            "enable_performance_monitoring": True
        },
        "production": {
            "host": os.getenv("VECTOR_DB_HOST", "vector-db-prod"),
            "port": int(os.getenv("VECTOR_DB_PORT", "8000")),
            "max_memory_usage_gb": 16.0,
            "batch_size": 1000,
            "enable_performance_monitoring": True,
            "auto_backup_interval_hours": 6
        }
    }
    
    defaults = config_defaults.get(environment, config_defaults["development"])
    
    # Merge with custom settings
    if custom_settings:
        defaults.update(custom_settings)
    
    # Create credentials
    credentials = VectorDatabaseCredentials(
        api_key=os.getenv("VECTOR_DB_API_KEY"),
        secret_key=os.getenv("VECTOR_DB_SECRET_KEY"),
        environment=environment
    )
    
    defaults["credentials"] = credentials
    
    return VectorDatabaseConfig(**defaults)
