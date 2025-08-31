"""
Vector Store Configuration for IA-Influencer Agent Platform
==========================================================

Professional Vector Database and Similarity Search configuration.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

STRICT COPYRIGHT NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, distribution, or reverse engineering
without explicit written permission is STRICTLY PROHIBITED and will be
prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
from pydantic import BaseSettings, validator
from enum import Enum
from dataclasses import dataclass, field
import os


class VectorDatabase(str, Enum):
    """Supported vector database engines."""
    
    FAISS = "faiss"
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"
    QDRANT = "qdrant"
    MILVUS = "milvus"
    CHROMA = "chroma"
    REDIS = "redis"
    ELASTICSEARCH = "elasticsearch"
    PGVECTOR = "pgvector"


class IndexType(str, Enum):
    """Vector index types for different use cases."""
    
    FLAT = "flat"
    IVF = "ivf"
    HNSW = "hnsw"
    LSH = "lsh"
    ANNOY = "annoy"
    SCANN = "scann"
    IVF_PQ = "ivf_pq"
    IVF_FLAT = "ivf_flat"


class DistanceMetric(str, Enum):
    """Distance metrics for similarity calculations."""
    
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    MANHATTAN = "manhattan"
    DOT_PRODUCT = "dot_product"
    HAMMING = "hamming"
    JACCARD = "jaccard"


@dataclass
class VectorCollection:
    """Configuration for a vector collection/index."""
    
    name: str
    dimension: int
    index_type: IndexType
    distance_metric: DistanceMetric
    description: str = ""
    max_vectors: Optional[int] = None
    replicas: int = 1
    shards: int = 1
    metadata_schema: Dict[str, str] = field(default_factory=dict)
    index_parameters: Dict[str, Any] = field(default_factory=dict)
    search_parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VectorStoreConnection:
    """Connection configuration for vector database."""
    
    database: VectorDatabase
    host: str = "localhost"
    port: int = 6333
    api_key: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database_name: str = "ia_influencer"
    ssl_enabled: bool = False
    timeout: int = 30
    pool_size: int = 10
    custom_config: Dict[str, Any] = field(default_factory=dict)


class VectorStoreConfig(BaseSettings):
    """
    Professional Vector Store Configuration for IA-Influencer Agent Platform.
    
    Manages vector databases, similarity search, embeddings storage, and
    high-performance retrieval systems for content protection and matching.
    """
    
    # Core Vector Store Configuration
    DEFAULT_VECTOR_DB: VectorDatabase = VectorDatabase.FAISS
    VECTOR_DIMENSION: int = 512
    DEFAULT_INDEX_TYPE: IndexType = IndexType.HNSW
    DEFAULT_DISTANCE_METRIC: DistanceMetric = DistanceMetric.COSINE
    
    # Storage Configuration
    VECTOR_STORAGE_PATH: str = "/data/vectors"
    INDEX_STORAGE_PATH: str = "/data/indexes"
    BACKUP_STORAGE_PATH: str = "/data/backups/vectors"
    
    # Performance Configuration
    BATCH_SIZE: int = 1000
    MAX_VECTORS_PER_COLLECTION: int = 10000000
    SEARCH_TIMEOUT: int = 30
    INDEX_BUILD_TIMEOUT: int = 3600
    
    # Search Configuration
    DEFAULT_TOP_K: int = 10
    MAX_TOP_K: int = 1000
    SIMILARITY_THRESHOLD: float = 0.8
    SEARCH_EF: int = 64  # HNSW search parameter
    
    # Index Configuration
    HNSW_M: int = 16  # HNSW connections per layer
    HNSW_EF_CONSTRUCTION: int = 200  # HNSW construction parameter
    IVF_NLIST: int = 100  # IVF number of clusters
    PQ_M: int = 8  # Product Quantization subvectors
    
    # Connection Configuration
    VECTOR_DB_HOST: str = "localhost"
    VECTOR_DB_PORT: int = 6333
    VECTOR_DB_API_KEY: Optional[str] = None
    VECTOR_DB_USERNAME: Optional[str] = None
    VECTOR_DB_PASSWORD: Optional[str] = None
    CONNECTION_POOL_SIZE: int = 10
    CONNECTION_TIMEOUT: int = 30
    
    # Replication and Sharding
    DEFAULT_REPLICAS: int = 1
    DEFAULT_SHARDS: int = 1
    AUTO_SHARDING_ENABLED: bool = False
    REPLICATION_FACTOR: int = 1
    
    # Backup and Recovery
    AUTO_BACKUP_ENABLED: bool = True
    BACKUP_INTERVAL_HOURS: int = 24
    BACKUP_RETENTION_DAYS: int = 30
    INCREMENTAL_BACKUP: bool = True
    
    # Monitoring and Analytics
    METRICS_ENABLED: bool = True
    PERFORMANCE_MONITORING: bool = True
    QUERY_LOGGING_ENABLED: bool = True
    SLOW_QUERY_THRESHOLD_MS: int = 1000
    
    # Collection Configurations
    AUDIO_FINGERPRINT_COLLECTION: str = "audio_fingerprints"
    IMAGE_FINGERPRINT_COLLECTION: str = "image_fingerprints"
    TEXT_EMBEDDING_COLLECTION: str = "text_embeddings"
    VIDEO_FINGERPRINT_COLLECTION: str = "video_fingerprints"
    USER_CONTENT_COLLECTION: str = "user_content"
    
    class Config:
        env_prefix = "VECTOR_STORE_"
        case_sensitive = False
        env_file = ".env"
    
    @validator("VECTOR_STORAGE_PATH", "INDEX_STORAGE_PATH", "BACKUP_STORAGE_PATH")
    def create_storage_directories(cls, v):
        """Ensure vector storage directories exist."""
        os.makedirs(v, exist_ok=True)
        return v
    
    def get_vector_collection_config(self, collection_name: str) -> VectorCollection:
        """Get vector collection configuration by name."""
        
        collections = {
            self.AUDIO_FINGERPRINT_COLLECTION: VectorCollection(
                name=self.AUDIO_FINGERPRINT_COLLECTION,
                dimension=512,
                index_type=IndexType.HNSW,
                distance_metric=DistanceMetric.COSINE,
                description="Audio fingerprints for copyright detection and similarity matching",
                max_vectors=50000000,  # 50M audio tracks
                metadata_schema={
                    "track_id": "string",
                    "artist": "string",
                    "title": "string",
                    "duration": "float",
                    "genre": "string",
                    "upload_date": "datetime",
                    "user_id": "string",
                },
                index_parameters={
                    "M": self.HNSW_M,
                    "ef_construction": self.HNSW_EF_CONSTRUCTION,
                },
                search_parameters={
                    "ef": self.SEARCH_EF,
                    "top_k": self.DEFAULT_TOP_K,
                }
            ),
            
            self.IMAGE_FINGERPRINT_COLLECTION: VectorCollection(
                name=self.IMAGE_FINGERPRINT_COLLECTION,
                dimension=512,
                index_type=IndexType.HNSW,
                distance_metric=DistanceMetric.COSINE,
                description="Image fingerprints for visual content protection",
                max_vectors=100000000,  # 100M images
                metadata_schema={
                    "image_id": "string",
                    "filename": "string",
                    "width": "integer",
                    "height": "integer",
                    "format": "string",
                    "upload_date": "datetime",
                    "user_id": "string",
                    "content_type": "string",
                },
                index_parameters={
                    "M": self.HNSW_M,
                    "ef_construction": self.HNSW_EF_CONSTRUCTION,
                },
            ),
            
            self.TEXT_EMBEDDING_COLLECTION: VectorCollection(
                name=self.TEXT_EMBEDDING_COLLECTION,
                dimension=384,  # Sentence transformer dimension
                index_type=IndexType.HNSW,
                distance_metric=DistanceMetric.COSINE,
                description="Text embeddings for semantic search and content matching",
                max_vectors=10000000,  # 10M text documents
                metadata_schema={
                    "text_id": "string",
                    "content_hash": "string",
                    "language": "string",
                    "word_count": "integer",
                    "category": "string",
                    "upload_date": "datetime",
                    "user_id": "string",
                },
                index_parameters={
                    "M": 32,  # Higher M for text similarity
                    "ef_construction": 400,
                },
            ),
            
            self.VIDEO_FINGERPRINT_COLLECTION: VectorCollection(
                name=self.VIDEO_FINGERPRINT_COLLECTION,
                dimension=768,  # Video features are typically higher dimensional
                index_type=IndexType.IVF,  # IVF for large video collections
                distance_metric=DistanceMetric.COSINE,
                description="Video fingerprints for video content protection",
                max_vectors=5000000,  # 5M videos
                metadata_schema={
                    "video_id": "string",
                    "filename": "string",
                    "duration": "float",
                    "resolution": "string",
                    "fps": "integer",
                    "codec": "string",
                    "upload_date": "datetime",
                    "user_id": "string",
                },
                index_parameters={
                    "nlist": self.IVF_NLIST,
                    "nprobe": 10,
                },
            ),
            
            self.USER_CONTENT_COLLECTION: VectorCollection(
                name=self.USER_CONTENT_COLLECTION,
                dimension=512,
                index_type=IndexType.HNSW,
                distance_metric=DistanceMetric.COSINE,
                description="User content embeddings for recommendation and discovery",
                max_vectors=20000000,  # 20M user content items
                metadata_schema={
                    "content_id": "string",
                    "user_id": "string",
                    "content_type": "string",
                    "title": "string",
                    "description": "string",
                    "tags": "array",
                    "upload_date": "datetime",
                    "privacy_level": "string",
                },
                index_parameters={
                    "M": self.HNSW_M,
                    "ef_construction": self.HNSW_EF_CONSTRUCTION,
                },
            ),
        }
        
        return collections.get(collection_name, self._get_default_collection(collection_name))
    
    def _get_default_collection(self, name: str) -> VectorCollection:
        """Get default vector collection configuration."""



        return VectorCollection(
            name=name,
            dimension=self.VECTOR_DIMENSION,
            index_type=self.DEFAULT_INDEX_TYPE,
            distance_metric=self.DEFAULT_DISTANCE_METRIC,
            description=f"Default collection for {name}",
        )
    
    def get_connection_config(self, database: Optional[VectorDatabase] = None) -> VectorStoreConnection:
        """Get vector database connection configuration."""
        db = database or self.DEFAULT_VECTOR_DB
        
        connections = {
            VectorDatabase.FAISS: VectorStoreConnection(
                database=VectorDatabase.FAISS,
                # FAISS is file-based, no network connection needed
                custom_config={
                    "storage_path": self.VECTOR_STORAGE_PATH,
                    "memory_mapping": True,
                    "compression": True,
                }
            ),
            
            VectorDatabase.QDRANT: VectorStoreConnection(
                database=VectorDatabase.QDRANT,
                host=self.VECTOR_DB_HOST,
                port=self.VECTOR_DB_PORT or 6333,
                api_key=self.VECTOR_DB_API_KEY,
                timeout=self.CONNECTION_TIMEOUT,
                pool_size=self.CONNECTION_POOL_SIZE,
                custom_config={
                    "prefer_grpc": True,
                    "https": False,
                }
            ),
            
            VectorDatabase.PINECONE: VectorStoreConnection(
                database=VectorDatabase.PINECONE,
                api_key=self.VECTOR_DB_API_KEY,
                custom_config={
                    "environment": "us-west1-gcp",
                    "project_name": "ia-influencer",
                }
            ),
            
            VectorDatabase.WEAVIATE: VectorStoreConnection(
                database=VectorDatabase.WEAVIATE,
                host=self.VECTOR_DB_HOST,
                port=self.VECTOR_DB_PORT or 8080,
                username=self.VECTOR_DB_USERNAME,
                password=self.VECTOR_DB_PASSWORD,
                custom_config={
                    "startup_period": 5,
                    "additional_headers": {},
                }
            ),
            
            VectorDatabase.REDIS: VectorStoreConnection(
                database=VectorDatabase.REDIS,
                host=self.VECTOR_DB_HOST,
                port=self.VECTOR_DB_PORT or 6379,
                password=self.VECTOR_DB_PASSWORD,
                database_name="0",
                custom_config={
                    "decode_responses": True,
                    "health_check_interval": 30,
                }
            ),
        }
        
        return connections.get(db, connections[VectorDatabase.FAISS])
    
    def get_search_config(self) -> Dict[str, Any]:
        """Get vector search configuration."""



        return {
            "default_top_k": self.DEFAULT_TOP_K,
            "max_top_k": self.MAX_TOP_K,
            "similarity_threshold": self.SIMILARITY_THRESHOLD,
            "search_timeout": self.SEARCH_TIMEOUT,
            "distance_metric": self.DEFAULT_DISTANCE_METRIC,
            "filters": {
                "enabled": True,
                "max_filter_conditions": 10,
                "supported_operators": ["eq", "ne", "gt", "lt", "gte", "lte", "in", "not_in"],
            },
            "aggregation": {
                "enabled": True,
                "max_aggregations": 5,
                "supported_functions": ["count", "avg", "min", "max", "sum"],
            },
            "hybrid_search": {
                "enabled": True,
                "sparse_dense_ratio": 0.7,
                "reranking_enabled": True,
            }
        }
    
    def get_indexing_config(self) -> Dict[str, Any]:
        """Get vector indexing configuration."""



        return {
            "batch_size": self.BATCH_SIZE,
            "build_timeout": self.INDEX_BUILD_TIMEOUT,
            "parallel_build": True,
            "index_types": {
                "hnsw": {
                    "M": self.HNSW_M,
                    "ef_construction": self.HNSW_EF_CONSTRUCTION,
                    "max_connections": self.HNSW_M * 2,
                    "ef": self.SEARCH_EF,
                },
                "ivf": {
                    "nlist": self.IVF_NLIST,
                    "nprobe": 10,
                    "quantizer": "flat",
                },
                "pq": {
                    "m": self.PQ_M,
                    "nbits": 8,
                    "metric": self.DEFAULT_DISTANCE_METRIC,
                },
            },
            "optimization": {
                "auto_optimize": True,
                "optimize_threshold": 10000,
                "rebuild_threshold": 0.1,  # 10% deleted vectors
            }
        }
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Get vector storage configuration."""



        return {
            "storage_path": self.VECTOR_STORAGE_PATH,
            "index_path": self.INDEX_STORAGE_PATH,
            "backup_path": self.BACKUP_STORAGE_PATH,
            "compression": {
                "enabled": True,
                "algorithm": "lz4",
                "level": 1,
            },
            "memory_mapping": {
                "enabled": True,
                "preload": False,
                "lock_memory": False,
            },
            "persistence": {
                "sync_interval": 60,  # seconds
                "write_buffer_size": 64 * 1024 * 1024,  # 64MB
                "max_write_buffer_size": 256 * 1024 * 1024,  # 256MB
            }
        }
    
    def get_backup_config(self) -> Dict[str, Any]:
        """Get backup and recovery configuration."""



        return {
            "auto_backup": self.AUTO_BACKUP_ENABLED,
            "backup_interval_hours": self.BACKUP_INTERVAL_HOURS,
            "retention_days": self.BACKUP_RETENTION_DAYS,
            "incremental_backup": self.INCREMENTAL_BACKUP,
            "backup_path": self.BACKUP_STORAGE_PATH,
            "compression": True,
            "encryption": False,  # Can be enabled for sensitive data
            "verification": True,
            "cloud_backup": {
                "enabled": False,
                "provider": "s3",
                "bucket": "ia-influencer-vector-backups",
            }
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance optimization configuration."""



        return {
            "connection_pooling": {
                "pool_size": self.CONNECTION_POOL_SIZE,
                "max_overflow": 5,
                "timeout": self.CONNECTION_TIMEOUT,
                "recycle": 3600,
            },
            "caching": {
                "query_cache_size": 1000,
                "result_cache_ttl": 300,  # 5 minutes
                "embedding_cache_size": 10000,
            },
            "batch_processing": {
                "batch_size": self.BATCH_SIZE,
                "max_batch_size": self.BATCH_SIZE * 4,
                "batch_timeout_ms": 100,
            },
            "parallel_processing": {
                "worker_threads": 4,
                "io_threads": 2,
                "search_parallelism": True,
            }
        }
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring and observability configuration."""



        return {
            "metrics": {
                "enabled": self.METRICS_ENABLED,
                "performance_monitoring": self.PERFORMANCE_MONITORING,
                "collection_stats": True,
                "query_stats": True,
            },
            "logging": {
                "query_logging": self.QUERY_LOGGING_ENABLED,
                "slow_query_threshold_ms": self.SLOW_QUERY_THRESHOLD_MS,
                "log_level": "INFO",
                "log_format": "json",
            },
            "alerts": {
                "high_memory_usage": 0.8,
                "high_disk_usage": 0.9,
                "slow_queries": self.SLOW_QUERY_THRESHOLD_MS,
                "connection_errors": 5,
            },
            "health_checks": {
                "interval": 30,
                "timeout": 5,
                "checks": ["connection", "storage", "memory", "indexes"],
            }
        }
    
    def estimate_storage_requirements(self, num_vectors: int, dimension: int) -> Dict[str, Any]:
        """Estimate storage requirements for vector collection."""
        # Base storage per vector (in bytes)
        vector_size = dimension * 4  # float32 = 4 bytes
        metadata_size = 200  # Average metadata size
        index_overhead = 0.3  # 30% overhead for indexing
        
        base_storage_gb = (num_vectors * (vector_size + metadata_size)) / (1024**3)
        total_storage_gb = base_storage_gb * (1 + index_overhead)
        
        return {
            "num_vectors": num_vectors,
            "dimension": dimension,
            "vector_storage_gb": base_storage_gb,
            "total_storage_gb": total_storage_gb,
            "recommended_memory_gb": min(total_storage_gb * 0.5, 32),
            "estimated_search_qps": min(1000, num_vectors / 1000),
            "recommended_shards": max(1, num_vectors // 1000000),
        }


# Global vector store configuration instance
vector_store_config = VectorStoreConfig()
