"""Vector Database Backend Configuration Management
==============================================

Advanced configuration management for multiple vector database backends
with enterprise-grade settings, optimization, and monitoring capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️ COPYRIGHT WARNING ⚠️
This code is protected by copyright law. Any unauthorized reproduction, distribution, 
modification, or use of this code without explicit written permission from 
Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result in legal action.

For licensing and authorization requests, contact: mlaiel@live.de

TEAM SPECIALTIES:
- Lead AI Developer + Backend Senior Engineer: Fahed Mlaiel
- ML Engineer + Data Scientist: Advanced algorithms & optimization
- Database Administrator + Performance Specialist: Scalability & efficiency  
- Security Engineer + DevOps Engineer: System security & deployment
- Audio Processing Specialist: Audio fingerprinting & analysis
- Computer Vision Engineer: Image/video processing & recognition
- Microservices Architect: Distributed systems & API design
"""import os
import yaml
import json
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict, field
from pathlib import Path
from enum import Enum
import socket
import psutil
import threading
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class BackendType(Enum):
    """Supported vector database backends."""    FAISS = "faiss"
    CHROMA = "chroma"
    ELASTICSEARCH = "elasticsearch"
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"
    QDRANT = "qdrant"


class IndexType(Enum):
    """FAISS index types for different use cases."""    FLAT = "IndexFlatL2"
    IVF_FLAT = "IndexIVFFlat"
    IVF_PQ = "IndexIVFPQ"
    HNSW = "IndexHNSWFlat"
    LSH = "IndexLSH"
    SCALAR_QUANTIZER = "IndexScalarQuantizer"


class MetricType(Enum):
    """Distance metrics for similarity computation."""    EUCLIDEAN = "l2"
    COSINE = "cosine"
    INNER_PRODUCT = "ip"
    MANHATTAN = "l1"
    HAMMING = "hamming"


@dataclass
class PerformanceSettings:
    """Performance optimization settings."""    enable_gpu: bool = False
    gpu_devices: List[int] = field(default_factory=list)
    num_threads: int = 4
    batch_size: int = 32
    memory_limit_gb: float = 8.0
    cache_size_mb: int = 512
    prefetch_enabled: bool = True
    parallel_search: bool = True
    async_operations: bool = True


@dataclass
class SecuritySettings:
    """Security and access control settings."""    encryption_enabled: bool = True
    encryption_algorithm: str = "AES-256"
    key_rotation_days: int = 90
    access_logging: bool = True
    rate_limiting: bool = True
    max_requests_per_second: int = 100
    ip_whitelist: List[str] = field(default_factory=list)
    api_key_required: bool = True
    ssl_enabled: bool = True


@dataclass
class MonitoringSettings:
    """Monitoring and observability settings."""    metrics_enabled: bool = True
    prometheus_port: int = 9090
    health_check_interval: int = 30
    performance_logging: bool = True
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'memory_usage': 0.8,
        'cpu_usage': 0.85,
        'query_latency_ms': 1000,
        'error_rate': 0.05
    })
    retention_days: int = 30


@dataclass
class FAISSBackendConfig:
    """FAISS-specific configuration."""    index_type: IndexType = IndexType.IVF_FLAT
    nlist: int = 1024
    nprobe: int = 64
    m_pq: int = 8
    nbits_pq: int = 8
    ef_construction: int = 200
    ef_search: int = 50
    train_size: int = 100000
    use_gpu: bool = False
    gpu_device_ids: List[int] = field(default_factory=list)
    shard_size: int = 1000000
    index_path: str = "./faiss_indices"
    mmap_enabled: bool = True


@dataclass
class ChromaDBConfig:
    """ChromaDB-specific configuration."""    persist_directory: str = "./chroma_db"
    collection_metadata: Dict[str, Any] = field(default_factory=dict)
    distance_function: MetricType = MetricType.COSINE
    anonymized_telemetry: bool = False
    allow_reset: bool = True
    tenant: str = "default_tenant"
    database: str = "default_database"
    heartbeat_interval: int = 60
    max_batch_size: int = 5461


@dataclass
class ElasticsearchConfig:
    """Elasticsearch-specific configuration."""    hosts: List[str] = field(default_factory=lambda: ["localhost:9200"])
    username: Optional[str] = None
    password: Optional[str] = None
    use_ssl: bool = False
    verify_certs: bool = True
    ca_certs: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    index_prefix: str = "vector_db"
    refresh_interval: str = "1s"
    number_of_shards: int = 1
    number_of_replicas: int = 1


@dataclass
class PineconeConfig:
    """Pinecone-specific configuration."""    api_key: Optional[str] = None
    environment: str = "us-west1-gcp"
    project_name: Optional[str] = None
    index_name: str = "vector-index"
    dimension: int = 384
    metric: MetricType = MetricType.COSINE
    pods: int = 1
    replicas: int = 1
    pod_type: str = "p1.x1"
    metadata_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WeaviateConfig:
    """Weaviate-specific configuration."""    url: str = "http://localhost:8080"
    auth_client_secret: Optional[str] = None
    timeout_config: Dict[str, int] = field(default_factory=lambda: {
        'query': 60,
        'insert': 120,
        'init': 2
    })
    additional_headers: Dict[str, str] = field(default_factory=dict)
    startup_period: int = 5


@dataclass
class QdrantConfig:
    """Qdrant-specific configuration."""    host: str = "localhost"
    port: int = 6333
    grpc_port: int = 6334
    prefer_grpc: bool = False
    https: bool = False
    api_key: Optional[str] = None
    prefix: Optional[str] = None
    timeout: int = 60
    collection_config: Dict[str, Any] = field(default_factory=lambda: {
        'vectors': {
            'size': 384,
            'distance': 'Cosine'
        },
        'optimizers_config': {
            'default_segment_number': 2
        },
        'replication_factor': 1
    })


@dataclass
class VectorBackendConfig:
    """Complete vector database backend configuration."""    backend_type: BackendType = BackendType.FAISS
    data_directory: str = "./vector_data"
    
    # Backend-specific configurations
    faiss: FAISSBackendConfig = field(default_factory=FAISSBackendConfig)
    chroma: ChromaDBConfig = field(default_factory=ChromaDBConfig)
    elasticsearch: ElasticsearchConfig = field(default_factory=ElasticsearchConfig)
    pinecone: PineconeConfig = field(default_factory=PineconeConfig)
    weaviate: WeaviateConfig = field(default_factory=WeaviateConfig)
    qdrant: QdrantConfig = field(default_factory=QdrantConfig)
    
    # Cross-backend settings
    performance: PerformanceSettings = field(default_factory=PerformanceSettings)
    security: SecuritySettings = field(default_factory=SecuritySettings)
    monitoring: MonitoringSettings = field(default_factory=MonitoringSettings)
    
    # Global settings
    default_metric: MetricType = MetricType.COSINE
    default_dimension: int = 384
    auto_optimize: bool = True
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    
    def __post_init__(self):
        """Initialize configuration after creation."""        self._validate_configuration()
        self._setup_directories()
    
    def _validate_configuration(self):
        """Validate configuration settings."""        try:
            # Validate backend type
            if not isinstance(self.backend_type, BackendType):
                raise ValueError(f"Invalid backend type: {self.backend_type}")
            
            # Validate dimension
            if self.default_dimension <= 0:
                raise ValueError("Dimension must be positive")
            
            # Validate performance settings
            if self.performance.num_threads <= 0:
                raise ValueError("Number of threads must be positive")
            
            if self.performance.memory_limit_gb <= 0:
                raise ValueError("Memory limit must be positive")
            
            # Validate security settings
            if self.security.max_requests_per_second <= 0:
                raise ValueError("Rate limit must be positive")
            
            # Backend-specific validation
            if self.backend_type == BackendType.FAISS:
                self._validate_faiss_config()
            elif self.backend_type == BackendType.PINECONE:
                self._validate_pinecone_config()
            elif self.backend_type == BackendType.ELASTICSEARCH:
                self._validate_elasticsearch_config()
            
            logger.info("Configuration validation passed")
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {str(e)}")
            raise
    
    def _validate_faiss_config(self):
        """Validate FAISS-specific configuration."""        if self.faiss.nlist <= 0:
            raise ValueError("FAISS nlist must be positive")
        
        if self.faiss.nprobe <= 0 or self.faiss.nprobe > self.faiss.nlist:
            raise ValueError("FAISS nprobe must be positive and <= nlist")
        
        if self.faiss.use_gpu and not self.faiss.gpu_device_ids:
            raise ValueError("GPU device IDs must be specified when GPU is enabled")
    
    def _validate_pinecone_config(self):
        """Validate Pinecone-specific configuration."""        if not self.pinecone.api_key:
            if 'PINECONE_API_KEY' not in os.environ:
                raise ValueError("Pinecone API key must be provided")
            self.pinecone.api_key = os.environ['PINECONE_API_KEY']
        
        if self.pinecone.dimension != self.default_dimension:
            logger.warning("Pinecone dimension differs from default dimension")
    
    def _validate_elasticsearch_config(self):
        """Validate Elasticsearch-specific configuration."""        if not self.elasticsearch.hosts:
            raise ValueError("Elasticsearch hosts must be specified")
        
        for host in self.elasticsearch.hosts:
            if ':' not in host:
                raise ValueError(f"Invalid Elasticsearch host format: {host}")
    
    def _setup_directories(self):
        """Setup required directories."""        try:
            # Create main data directory
            Path(self.data_directory).mkdir(parents=True, exist_ok=True)
            
            # Create backend-specific directories
            if self.backend_type == BackendType.FAISS:
                Path(self.faiss.index_path).mkdir(parents=True, exist_ok=True)
            elif self.backend_type == BackendType.CHROMA:
                Path(self.chroma.persist_directory).mkdir(parents=True, exist_ok=True)
            
            # Create backup directory if enabled
            if self.backup_enabled:
                backup_dir = os.path.join(self.data_directory, "backups")
                Path(backup_dir).mkdir(parents=True, exist_ok=True)
            
            logger.info("Directories setup completed")
            
        except Exception as e:
            logger.error(f"Directory setup failed: {str(e)}")
            raise


class VectorBackendConfigManager:
    """Manager for vector database backend configurations."""    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.getenv(
            'VECTOR_BACKEND_CONFIG',
            './config/vector_backend_config.yaml'
        )
        self.config: Optional[VectorBackendConfig] = None
        self._lock = threading.Lock()
        self._load_config()
    
    def _load_config(self) -> VectorBackendConfig:
        """Load configuration from file or environment."""        try:
            with self._lock:
                if os.path.exists(self.config_path):
                    self.config = self._load_from_file()
                else:
                    self.config = self._load_from_environment()
                
                logger.info(f"Configuration loaded: {self.config.backend_type.value}")
                return self.config
                
        except Exception as e:
            logger.error(f"Configuration loading failed: {str(e)}")
            # Fall back to default configuration
            self.config = VectorBackendConfig()
            return self.config
    
    def _load_from_file(self) -> VectorBackendConfig:
        """Load configuration from YAML file."""        try:
            with open(self.config_path, 'r') as f:
                if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                    config_dict = yaml.safe_load(f)
                else:
                    config_dict = json.load(f)
            
            return self._dict_to_config(config_dict)
            
        except Exception as e:
            logger.error(f"File loading failed: {str(e)}")
            raise
    
    def _load_from_environment(self) -> VectorBackendConfig:
        """Load configuration from environment variables."""        config = VectorBackendConfig()
        
        # Backend type
        backend_type = os.getenv('VECTOR_BACKEND_TYPE', 'faiss')
        try:
            config.backend_type = BackendType(backend_type)
        except ValueError:
            logger.warning(f"Invalid backend type in env: {backend_type}, using FAISS")
        
        # Data directory
        config.data_directory = os.getenv('VECTOR_DATA_DIR', './vector_data')
        
        # Dimension
        try:
            config.default_dimension = int(os.getenv('VECTOR_DIMENSION', '384'))
        except ValueError:
            logger.warning("Invalid dimension in env, using default")
        
        # Performance settings
        try:
            config.performance.num_threads = int(os.getenv('VECTOR_THREADS', '4'))
            config.performance.memory_limit_gb = float(os.getenv('VECTOR_MEMORY_LIMIT', '8.0'))
            config.performance.enable_gpu = os.getenv('VECTOR_ENABLE_GPU', 'false').lower() == 'true'
        except ValueError:
            logger.warning("Invalid performance settings in env, using defaults")
        
        # Security settings
        config.security.encryption_enabled = os.getenv('VECTOR_ENCRYPTION', 'true').lower() == 'true'
        config.security.api_key_required = os.getenv('VECTOR_API_KEY_REQUIRED', 'true').lower() == 'true'
        
        # Backend-specific environment loading
        if config.backend_type == BackendType.PINECONE:
            config.pinecone.api_key = os.getenv('PINECONE_API_KEY')
            config.pinecone.environment = os.getenv('PINECONE_ENVIRONMENT', 'us-west1-gcp')
        elif config.backend_type == BackendType.ELASTICSEARCH:
            hosts = os.getenv('ELASTICSEARCH_HOSTS', 'localhost:9200')
            config.elasticsearch.hosts = [h.strip() for h in hosts.split(',')]
            config.elasticsearch.username = os.getenv('ELASTICSEARCH_USERNAME')
            config.elasticsearch.password = os.getenv('ELASTICSEARCH_PASSWORD')
        
        return config
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> VectorBackendConfig:
        """Convert dictionary to configuration object."""        try:
            # Handle backend type
            if 'backend_type' in config_dict:
                backend_str = config_dict['backend_type']
                config_dict['backend_type'] = BackendType(backend_str)
            
            # Handle metric type
            if 'default_metric' in config_dict:
                metric_str = config_dict['default_metric']
                config_dict['default_metric'] = MetricType(metric_str)
            
            # Handle nested configurations
            for backend_name in ['faiss', 'chroma', 'elasticsearch', 'pinecone', 'weaviate', 'qdrant']:
                if backend_name in config_dict:
                    backend_config = config_dict[backend_name]
                    
                    # Handle enums in backend configs
                    if backend_name == 'faiss' and 'index_type' in backend_config:
                        backend_config['index_type'] = IndexType(backend_config['index_type'])
                    
                    if 'distance_function' in backend_config:
                        backend_config['distance_function'] = MetricType(backend_config['distance_function'])
                    
                    if 'metric' in backend_config:
                        backend_config['metric'] = MetricType(backend_config['metric'])
            
            # Create configuration object
            return VectorBackendConfig(**config_dict)
            
        except Exception as e:
            logger.error(f"Dictionary to config conversion failed: {str(e)}")
            raise
    
    def save_config(self, config: Optional[VectorBackendConfig] = None) -> bool:
        """Save configuration to file."""        try:
            with self._lock:
                config_to_save = config or self.config
                if not config_to_save:
                    raise ValueError("No configuration to save")
                
                # Create directory if needed
                config_dir = os.path.dirname(self.config_path)
                if config_dir:
                    Path(config_dir).mkdir(parents=True, exist_ok=True)
                
                # Convert to dictionary
                config_dict = self._config_to_dict(config_to_save)
                
                # Save to file
                with open(self.config_path, 'w') as f:
                    if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                        yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                    else:
                        json.dump(config_dict, f, indent=2)
                
                logger.info(f"Configuration saved to {self.config_path}")
                return True
                
        except Exception as e:
            logger.error(f"Configuration saving failed: {str(e)}")
            return False
    
    def _config_to_dict(self, config: VectorBackendConfig) -> Dict[str, Any]:
        """Convert configuration object to dictionary."""        try:
            config_dict = asdict(config)
            
            # Convert enums to strings
            config_dict['backend_type'] = config.backend_type.value
            config_dict['default_metric'] = config.default_metric.value
            
            # Handle nested enum conversions
            if 'faiss' in config_dict and 'index_type' in config_dict['faiss']:
                config_dict['faiss']['index_type'] = config.faiss.index_type.value
            
            for backend_name in ['chroma', 'elasticsearch', 'pinecone']:
                if backend_name in config_dict:
                    backend_config = config_dict[backend_name]
                    for key, value in backend_config.items():
                        if isinstance(value, MetricType):
                            backend_config[key] = value.value
            
            return config_dict
            
        except Exception as e:
            logger.error(f"Config to dictionary conversion failed: {str(e)}")
            raise
    
    def get_backend_config(self, backend_type: Optional[BackendType] = None) -> Dict[str, Any]:
        """Get backend-specific configuration."""        if not self.config:
            raise ValueError("Configuration not loaded")
        
        target_backend = backend_type or self.config.backend_type
        
        if target_backend == BackendType.FAISS:
            return asdict(self.config.faiss)
        elif target_backend == BackendType.CHROMA:
            return asdict(self.config.chroma)
        elif target_backend == BackendType.ELASTICSEARCH:
            return asdict(self.config.elasticsearch)
        elif target_backend == BackendType.PINECONE:
            return asdict(self.config.pinecone)
        elif target_backend == BackendType.WEAVIATE:
            return asdict(self.config.weaviate)
        elif target_backend == BackendType.QDRANT:
            return asdict(self.config.qdrant)
        else:
            raise ValueError(f"Unsupported backend type: {target_backend}")
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """Update configuration with new values."""        try:
            with self._lock:
                if not self.config:
                    raise ValueError("Configuration not loaded")
                
                # Apply updates to current config
                for key, value in updates.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
                    else:
                        logger.warning(f"Unknown configuration key: {key}")
                
                # Re-validate configuration
                self.config._validate_configuration()
                
                # Save updated configuration
                return self.save_config()
                
        except Exception as e:
            logger.error(f"Configuration update failed: {str(e)}")
            return False
    
    def get_system_recommendations(self) -> Dict[str, Any]:
        """Get system-specific configuration recommendations."""        try:
            recommendations = {}
            
            # Memory recommendations
            available_memory = psutil.virtual_memory().total / (1024**3)  # GB
            recommended_memory = min(available_memory * 0.7, 16.0)
            recommendations['memory_limit_gb'] = recommended_memory
            
            # CPU recommendations
            cpu_count = psutil.cpu_count()
            recommended_threads = min(cpu_count, 8)
            recommendations['num_threads'] = recommended_threads
            
            # GPU recommendations
            try:
                import torch
                if torch.cuda.is_available():
                    gpu_count = torch.cuda.device_count()
                    recommendations['enable_gpu'] = True
                    recommendations['gpu_devices'] = list(range(gpu_count))
                else:
                    recommendations['enable_gpu'] = False
            except ImportError:
                recommendations['enable_gpu'] = False
            
            # Storage recommendations
            disk_usage = psutil.disk_usage('/')
            available_space = disk_usage.free / (1024**3)  # GB
            if available_space < 10:
                recommendations['warning'] = "Low disk space - consider cleanup or expansion"
            
            # Network recommendations
            recommendations['network_optimizations'] = {
                'enable_compression': True,
                'batch_operations': True,
                'connection_pooling': True
            }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"System recommendations failed: {str(e)}")
            return {}
    
    def validate_system_compatibility(self) -> Dict[str, Any]:
        """Validate system compatibility with current configuration."""        try:
            compatibility_report = {
                'compatible': True,
                'warnings': [],
                'errors': [],
                'recommendations': []
            }
            
            # Memory check
            available_memory = psutil.virtual_memory().total / (1024**3)
            required_memory = self.config.performance.memory_limit_gb
            
            if required_memory > available_memory:
                compatibility_report['compatible'] = False
                compatibility_report['errors'].append(
                    f"Insufficient memory: required {required_memory}GB, available {available_memory:.1f}GB"
                )
            elif required_memory > available_memory * 0.8:
                compatibility_report['warnings'].append(
                    f"High memory usage: {required_memory}GB of {available_memory:.1f}GB available"
                )
            
            # CPU check
            available_cores = psutil.cpu_count()
            required_threads = self.config.performance.num_threads
            
            if required_threads > available_cores:
                compatibility_report['warnings'].append(
                    f"Thread count ({required_threads}) exceeds CPU cores ({available_cores})"
                )
            
            # GPU check
            if self.config.performance.enable_gpu:
                try:
                    import torch
                    if not torch.cuda.is_available():
                        compatibility_report['compatible'] = False
                        compatibility_report['errors'].append("GPU enabled but CUDA not available")
                except ImportError:
                    compatibility_report['compatible'] = False
                    compatibility_report['errors'].append("GPU enabled but PyTorch not installed")
            
            # Disk space check
            disk_usage = psutil.disk_usage(self.config.data_directory)
            available_space = disk_usage.free / (1024**3)
            
            if available_space < 5:
                compatibility_report['compatible'] = False
                compatibility_report['errors'].append(f"Insufficient disk space: {available_space:.1f}GB available")
            elif available_space < 20:
                compatibility_report['warnings'].append(f"Low disk space: {available_space:.1f}GB available")
            
            # Network connectivity check (for cloud backends)
            if self.config.backend_type in [BackendType.PINECONE, BackendType.ELASTICSEARCH]:
                try:
                    socket.create_connection(("8.8.8.8", 53), timeout=3)
                except OSError:
                    compatibility_report['warnings'].append("Network connectivity issues detected")
            
            return compatibility_report
            
        except Exception as e:
            logger.error(f"System compatibility check failed: {str(e)}")
            return {
                'compatible': False,
                'errors': [f"Compatibility check failed: {str(e)}"],
                'warnings': [],
                'recommendations': []
            }


# Configuration presets for different deployment scenarios
DEPLOYMENT_PRESETS = {
    'development': VectorBackendConfig(
        backend_type=BackendType.FAISS,
        faiss=FAISSBackendConfig(
            index_type=IndexType.FLAT,
            use_gpu=False,
            shard_size=100000
        ),
        performance=PerformanceSettings(
            enable_gpu=False,
            num_threads=2,
            memory_limit_gb=2.0,
            batch_size=16
        ),
        security=SecuritySettings(
            encryption_enabled=False,
            api_key_required=False,
            rate_limiting=False
        ),
        monitoring=MonitoringSettings(
            metrics_enabled=False,
            performance_logging=False
        )
    ),
    
    'production': VectorBackendConfig(
        backend_type=BackendType.FAISS,
        faiss=FAISSBackendConfig(
            index_type=IndexType.IVF_FLAT,
            nlist=2048,
            nprobe=128,
            use_gpu=True,
            shard_size=5000000
        ),
        performance=PerformanceSettings(
            enable_gpu=True,
            num_threads=8,
            memory_limit_gb=16.0,
            batch_size=128
        ),
        security=SecuritySettings(
            encryption_enabled=True,
            api_key_required=True,
            rate_limiting=True,
            max_requests_per_second=1000
        ),
        monitoring=MonitoringSettings(
            metrics_enabled=True,
            performance_logging=True,
            health_check_interval=10
        )
    ),
    
    'cloud_scale': VectorBackendConfig(
        backend_type=BackendType.PINECONE,
        pinecone=PineconeConfig(
            pods=4,
            replicas=2,
            pod_type="p1.x2"
        ),
        performance=PerformanceSettings(
            num_threads=16,
            memory_limit_gb=32.0,
            batch_size=256
        ),
        security=SecuritySettings(
            encryption_enabled=True,
            api_key_required=True,
            rate_limiting=True,
            max_requests_per_second=5000
        )
    ),
    
    'hybrid_search': VectorBackendConfig(
        backend_type=BackendType.ELASTICSEARCH,
        elasticsearch=ElasticsearchConfig(
            number_of_shards=3,
            number_of_replicas=2
        ),
        performance=PerformanceSettings(
            num_threads=12,
            memory_limit_gb=24.0,
            batch_size=192
        )
    )
}


def load_preset(preset_name: str) -> VectorBackendConfig:
    """Load a deployment preset configuration."""    if preset_name not in DEPLOYMENT_PRESETS:
        available = list(DEPLOYMENT_PRESETS.keys())
        raise ValueError(f"Unknown preset: {preset_name}. Available: {available}")
    
    return DEPLOYMENT_PRESETS[preset_name]


def auto_detect_optimal_config() -> VectorBackendConfig:
    """Auto-detect optimal configuration based on system resources."""    try:
        # Get system info
        memory_gb = psutil.virtual_memory().total / (1024**3)
        cpu_cores = psutil.cpu_count()
        
        # Determine appropriate preset
        if memory_gb >= 32 and cpu_cores >= 16:
            base_config = load_preset('production')
        elif memory_gb >= 8 and cpu_cores >= 4:
            base_config = load_preset('development')
            base_config.performance.memory_limit_gb = min(memory_gb * 0.7, 16.0)
            base_config.performance.num_threads = min(cpu_cores, 8)
        else:
            base_config = load_preset('development')
            base_config.performance.memory_limit_gb = min(memory_gb * 0.5, 4.0)
            base_config.performance.num_threads = min(cpu_cores, 4)
        
        # GPU detection
        try:
            import torch
            if torch.cuda.is_available():
                base_config.performance.enable_gpu = True
                base_config.performance.gpu_devices = list(range(torch.cuda.device_count()))
                base_config.faiss.use_gpu = True
                base_config.faiss.gpu_device_ids = base_config.performance.gpu_devices
        except ImportError:
            pass
        
        logger.info(f"Auto-detected configuration: {memory_gb:.1f}GB RAM, {cpu_cores} cores")
        return base_config
        
    except Exception as e:
        logger.error(f"Auto-detection failed: {str(e)}, using development preset")
        return load_preset('development')


# Default configuration manager instance
default_config_manager = VectorBackendConfigManager()
