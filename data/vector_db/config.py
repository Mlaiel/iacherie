"""Vector Database Configuration Module
===================================

Configuration management for vector database backends and operations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ COPYRIGHT WARNING ⚠️
This code is protected by copyright law. Any unauthorized reproduction, distribution, 
modification, or use of this code without explicit written permission from 
Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result in legal action.

For licensing and authorization requests, contact: mlaiel@live.de
"""

import os
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class EmbeddingConfig:
    """
Configuration for embedding models and engines."""
    text_model: str = "all-MiniLM-L6-v2"
    audio_model: str = "facebook/wav2vec2-base-960h"
    image_model: str = "openai/clip-vit-base-patch32"
    video_model: str = "microsoft/xclip-base-patch32"
    dimension: int = 384
    batch_size: int = 32
    device: str = "auto"  # auto, cpu, cuda
    cache_dir: Optional[str] = None

@dataclass 
class FAISSConfig:
    """Configuration for FAISS backend."""
    index_type: str = "IVFFlat"  # Flat, IVFFlat, HNSW, IVF_PQ
    nlist: int = 100  # Number of clusters for IVF
    nprobe: int = 10  # Number of clusters to search
    M: int = 8  # Number of subvectors for PQ
    nbits: int = 8  # Bits per subvector for PQ
    ef_construction: int = 200  # Construction parameter for HNSW
    ef_search: int = 50  # Search parameter for HNSW
    metric: str = "L2"  # L2, IP (inner product)
    gpu_enabled: bool = False
    gpu_ids: List[int] = None
    shard_size: int = 1000000  # Maximum vectors per shard

@dataclass
class ChromaConfig:
    """Configuration for ChromaDB backend."""
    persist_directory: str = "./chroma_db"
    collection_metadata: Dict[str, Any] = None
    distance_function: str = "cosine"  # cosine, l2, ip
    anonymized_telemetry: bool = False
    allow_reset: bool = True
    tenant: str = "default_tenant"
    database: str = "default_database"

@dataclass
class SearchConfig:
    """Configuration for similarity search operations."""
    default_k: int = 10
    max_k: int = 1000
    similarity_thresholds: Dict[str, float] = None
    rerank_enabled: bool = True
    rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    duplicate_threshold: float = 0.95
    collaboration_threshold: float = 0.75
    content_aware_search: bool = True

@dataclass
class PerformanceConfig:
    """Configuration for performance optimization."""
    batch_size: int = 100
    max_workers: int = 4
    timeout_seconds: int = 30
    memory_limit_mb: int = 2048
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    metrics_enabled: bool = True
    profiling_enabled: bool = False

@dataclass
class SecurityConfig:
    """
Configuration for security and access control."""
    encryption_enabled: bool = True
    encryption_key_path: Optional[str] = None
    access_logs_enabled: bool = True
    rate_limiting_enabled: bool = True
    max_requests_per_minute: int = 1000
    ip_whitelist: List[str] = None
    api_key_required: bool = False

@dataclass
class VectorDBConfig:
    """
Complete vector database configuration."""
    backend: str = "faiss"  # faiss, chroma
    data_directory: str = "./vector_data"
    embedding: EmbeddingConfig = None
    faiss: FAISSConfig = None
    chroma: ChromaConfig = None
    search: SearchConfig = None
    performance: PerformanceConfig = None
    security: SecurityConfig = None
    
    def __post_init__(self):
        """Initialize default sub-configurations."""
        if self.embedding is None:
            self.embedding = EmbeddingConfig()
        if self.faiss is None:
            self.faiss = FAISSConfig()
        if self.chroma is None:
            self.chroma = ChromaConfig()
        if self.search is None:
            self.search = SearchConfig()
        if self.performance is None:
            self.performance = PerformanceConfig()
        if self.security is None:
            self.security = SecurityConfig()
            
        # Set default similarity thresholds if not provided
        if self.search.similarity_thresholds is None:
            self.search.similarity_thresholds = {
                'text': 0.8,
                'audio': 0.85,
                'image': 0.9,
                'video': 0.87,
                'multimodal': 0.82
            }

class ConfigManager:
    """
Manager for vector database configuration."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.getenv(
            'VECTOR_DB_CONFIG', 
            './config/vector_db_config.json'
        )
        self.config = self._load_config()
    
    def _load_config(self) -> VectorDBConfig:
        """
Load configuration from file or create default."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config_dict = json.load(f)
                
                # Convert nested dicts to dataclass instances
                if 'embedding' in config_dict:
                    config_dict['embedding'] = EmbeddingConfig(**config_dict['embedding'])
                if 'faiss' in config_dict:
                    config_dict['faiss'] = FAISSConfig(**config_dict['faiss'])
                if 'chroma' in config_dict:
                    config_dict['chroma'] = ChromaConfig(**config_dict['chroma'])
                if 'search' in config_dict:
                    config_dict['search'] = SearchConfig(**config_dict['search'])
                if 'performance' in config_dict:
                    config_dict['performance'] = PerformanceConfig(**config_dict['performance'])
                if 'security' in config_dict:
                    config_dict['security'] = SecurityConfig(**config_dict['security'])
                
                config = VectorDBConfig(**config_dict)
                logger.info(f"Loaded configuration from {self.config_path}")
                return config
            else:
                logger.info("No config file found, using defaults")
                return VectorDBConfig()
                
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            logger.info("Using default configuration")
            return VectorDBConfig()
    
    def save_config(self) -> bool:
        """Save current configuration to file."""
        try:
            # Create directory if it doesn't exist
            config_dir = os.path.dirname(self.config_path)
            if config_dir:
                os.makedirs(config_dir, exist_ok=True)
            
            # Convert dataclass to dict
            config_dict = asdict(self.config)
            
            with open(self.config_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            logger.info(f"Configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
    
    def update_config(self, **kwargs) -> bool:
        """Update configuration parameters."""
        try:
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                else:
                    logger.warning(f"Unknown config parameter: {key}")
            
            return self.save_config()
            
        except Exception as e:
            logger.error(f"Error updating config: {e}")
            return False
    
    def get_backend_config(self) -> Dict[str, Any]:
        """Get configuration for the selected backend."""
        if self.config.backend == 'faiss':
            return asdict(self.config.faiss)
        elif self.config.backend == 'chroma':
            return asdict(self.config.chroma)
        else:
            raise ValueError(f"Unknown backend: {self.config.backend}")
    
    def get_embedding_config(self) -> Dict[str, Any]:
        """Get embedding configuration."""
        return asdict(self.config.embedding)
    
    def get_search_config(self) -> Dict[str, Any]:
        """
Get search configuration."""
        return asdict(self.config.search)
    
    def validate_config(self) -> List[str]:
        """
Validate configuration and return list of issues."""
        issues = []
        
        # Validate backend
        if self.config.backend not in ['faiss', 'chroma']:
            issues.append(f"Invalid backend: {self.config.backend}")
        
        # Validate directories
        if not os.path.exists(os.path.dirname(self.config.data_directory)):
            issues.append(f"Data directory parent does not exist: {self.config.data_directory}")
        
        # Validate embedding models
        embedding_models = [
            self.config.embedding.text_model,
            self.config.embedding.audio_model,
            self.config.embedding.image_model,
            self.config.embedding.video_model
        ]
        
        for model in embedding_models:
            if not model or len(model.strip()) == 0:
                issues.append(f"Empty embedding model configuration")
        
        # Validate FAISS config
        if self.config.backend == 'faiss':
            if self.config.faiss.index_type not in ['Flat', 'IVFFlat', 'HNSW', 'IVF_PQ']:
                issues.append(f"Invalid FAISS index type: {self.config.faiss.index_type}")
            
            if self.config.faiss.nlist <= 0:
                issues.append("FAISS nlist must be positive")
        
        # Validate performance config
        if self.config.performance.batch_size <= 0:
            issues.append("Batch size must be positive")
        
        if self.config.performance.max_workers <= 0:
            issues.append("Max workers must be positive")
        
        return issues

# Default configuration instance
default_config = VectorDBConfig()

# Configuration presets for different use cases
PRESETS = {
    'development': VectorDBConfig(
        backend='faiss',
        faiss=FAISSConfig(
            index_type='Flat',
            gpu_enabled=False
        ),
        performance=PerformanceConfig(
            batch_size=32,
            max_workers=2,
            memory_limit_mb=1024
        ),
        security=SecurityConfig(
            encryption_enabled=False,
            access_logs_enabled=False
        )
    ),
    
    'production': VectorDBConfig(
        backend='faiss',
        faiss=FAISSConfig(
            index_type='IVFFlat',
            nlist=1000,
            gpu_enabled=True
        ),
        performance=PerformanceConfig(
            batch_size=128,
            max_workers=8,
            memory_limit_mb=8192,
            enable_caching=True
        ),
        security=SecurityConfig(
            encryption_enabled=True,
            access_logs_enabled=True,
            rate_limiting_enabled=True
        )
    ),
    
    'high_throughput': VectorDBConfig(
        backend='faiss',
        faiss=FAISSConfig(
            index_type='HNSW',
            ef_construction=400,
            ef_search=100,
            gpu_enabled=True
        ),
        performance=PerformanceConfig(
            batch_size=256,
            max_workers=16,
            memory_limit_mb=16384
        )
    ),
    
    'memory_optimized': VectorDBConfig(
        backend='chroma',
        performance=PerformanceConfig(
            batch_size=64,
            max_workers=4,
            memory_limit_mb=2048,
            enable_caching=False
        )
    )
}

def load_preset(preset_name: str) -> VectorDBConfig:
    """Load a configuration preset."""
    if preset_name not in PRESETS:
        raise ValueError(f"Unknown preset: {preset_name}. Available: {list(PRESETS.keys())}")
    
    return PRESETS[preset_name]

def create_config_from_env() -> VectorDBConfig:
    """Create configuration from environment variables."""
    config = VectorDBConfig()
    
    # Backend selection
    if 'VECTOR_DB_BACKEND' in os.environ:
        config.backend = os.environ['VECTOR_DB_BACKEND']
    
    # Data directory
    if 'VECTOR_DB_DATA_DIR' in os.environ:
        config.data_directory = os.environ['VECTOR_DB_DATA_DIR']
    
    # Embedding configuration
    if 'EMBEDDING_TEXT_MODEL' in os.environ:
        config.embedding.text_model = os.environ['EMBEDDING_TEXT_MODEL']
    
    if 'EMBEDDING_DEVICE' in os.environ:
        config.embedding.device = os.environ['EMBEDDING_DEVICE']
    
    # FAISS configuration
    if 'FAISS_INDEX_TYPE' in os.environ:
        config.faiss.index_type = os.environ['FAISS_INDEX_TYPE']
    
    if 'FAISS_GPU_ENABLED' in os.environ:
        config.faiss.gpu_enabled = os.environ['FAISS_GPU_ENABLED'].lower() == 'true'
    
    # Performance configuration
    if 'VECTOR_DB_BATCH_SIZE' in os.environ:
        config.performance.batch_size = int(os.environ['VECTOR_DB_BATCH_SIZE'])
    
    if 'VECTOR_DB_MAX_WORKERS' in os.environ:
        config.performance.max_workers = int(os.environ['VECTOR_DB_MAX_WORKERS'])
    
    return config
