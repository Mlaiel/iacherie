"""
🗄️ **Model Artifact Manager - Enterprise Data Governance**

Ersteller: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Alle Rechte vorbehalten.
Version: 1.0.0

**⚠️ WARNUNG:** Dieser Code ist urheberrechtlich geschützt und vertraulich.

Enterprise model artifact storage, compression, and distribution system with
advanced data governance, lineage tracking, and multi-cloud storage optimization.
"""

import asyncio
import logging
import numpy as np
import torch
import pickle
import gzip
import lz4.frame
import brotli
import hashlib
import json
import os
from typing import Dict, List, Optional, Any, Tuple, Union, BinaryIO
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timedelta
import boto3
from azure.storage.blob import BlobServiceClient
from google.cloud import storage as gcs
import aiofiles
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import threading
from enum import Enum

# Ainflue ML Core Imports
from ..model_registry.model_encryption_manager import ModelEncryptionManager
from ..monitoring.performance_monitor import PerformanceMonitor
from ..monitoring.audit_trail_generator import AuditTrailGenerator

class StorageProvider(Enum):
    """Supported storage providers."""
    LOCAL = "local"
    AWS_S3 = "aws_s3"
    AZURE_BLOB = "azure_blob"
    GCP_STORAGE = "gcp_storage"
    HYBRID = "hybrid"

class CompressionAlgorithm(Enum):
    """Supported compression algorithms."""
    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    BROTLI = "brotli"
    CUSTOM_ML = "custom_ml"

class ArtifactType(Enum):
    """Types of ML artifacts."""
    MODEL_WEIGHTS = "model_weights"
    MODEL_ARCHITECTURE = "model_architecture"
    TOKENIZER = "tokenizer"
    PREPROCESSOR = "preprocessor"
    METADATA = "metadata"
    TRAINING_DATA = "training_data"
    VALIDATION_DATA = "validation_data"
    FEATURE_STORE = "feature_store"
    EXPERIMENT_LOG = "experiment_log"

@dataclass
class ArtifactMetadata:
    """Comprehensive metadata for ML artifacts."""
    artifact_id: str
    artifact_type: ArtifactType
    creator_type: str
    model_name: str
    model_version: str
    file_size_bytes: int
    compressed_size_bytes: int
    compression_ratio: float
    compression_algorithm: CompressionAlgorithm
    storage_provider: StorageProvider
    storage_path: str
    checksum: str
    encryption_key_id: Optional[str]
    created_at: datetime
    last_accessed: datetime
    access_count: int
    tags: Dict[str, str]
    lineage: Dict[str, Any]
    retention_policy: Dict[str, Any]
    compliance_flags: Dict[str, bool]

@dataclass
class StorageConfig:
    """Configuration for storage providers."""
    provider: StorageProvider
    bucket_name: str
    region: str = None
    credentials: Dict[str, str] = None
    encryption_enabled: bool = True
    replication_factor: int = 1
    storage_class: str = "STANDARD"

@dataclass
class CompressionConfig:
    """Configuration for compression strategies."""
    algorithm: CompressionAlgorithm
    compression_level: int = 6
    chunk_size: int = 1024 * 1024  # 1MB chunks
    parallel_compression: bool = True
    adaptive_compression: bool = True

class CustomMLCompressor:
    """Custom ML-specific compression using model structure knowledge."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def compress_model_weights(self, weights: Dict[str, torch.Tensor]) -> bytes:
        """Compress model weights using ML-specific techniques."""
        compressed_data = {}
        
        for layer_name, tensor in weights.items():
            # Quantization-aware compression
            if tensor.dtype == torch.float32:
                # Convert to FP16 for compression
                quantized = tensor.half()
                compressed_data[layer_name] = {
                    'data': quantized.cpu().numpy().tobytes(),
                    'shape': tensor.shape,
                    'dtype': 'float16',
                    'original_dtype': 'float32'
                }
            else:
                compressed_data[layer_name] = {
                    'data': tensor.cpu().numpy().tobytes(),
                    'shape': tensor.shape,
                    'dtype': str(tensor.dtype)
                }
        
        # Serialize and compress
        serialized = pickle.dumps(compressed_data)
        return lz4.frame.compress(serialized, compression_level=4)
    
    def decompress_model_weights(self, compressed_data: bytes) -> Dict[str, torch.Tensor]:
        """Decompress model weights."""
        decompressed = lz4.frame.decompress(compressed_data)
        data = pickle.loads(decompressed)
        
        weights = {}
        for layer_name, layer_data in data.items():
            tensor_data = np.frombuffer(layer_data['data'], dtype=layer_data['dtype'])
            tensor = torch.from_numpy(tensor_data.reshape(layer_data['shape']))
            
            # Convert back to original dtype if needed
            if layer_data.get('original_dtype') == 'float32' and tensor.dtype == torch.float16:
                tensor = tensor.float()
            
            weights[layer_name] = tensor
        
        return weights

class StorageBackend:
    """Abstract storage backend interface."""
    
    async def upload(self, data: bytes, path: str, metadata: Dict[str, Any]) -> bool:
        raise NotImplementedError
    
    async def download(self, path: str) -> bytes:
        raise NotImplementedError
    
    async def delete(self, path: str) -> bool:
        raise NotImplementedError
    
    async def list_objects(self, prefix: str) -> List[str]:
        raise NotImplementedError
    
    async def get_metadata(self, path: str) -> Dict[str, Any]:
        raise NotImplementedError

class LocalStorageBackend(StorageBackend):
    """Local filesystem storage backend."""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    async def upload(self, data: bytes, path: str, metadata: Dict[str, Any]) -> bool:
        try:
            file_path = self.base_path / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(data)
            
            # Save metadata
            metadata_path = file_path.with_suffix('.metadata.json')
            async with aiofiles.open(metadata_path, 'w') as f:
                await f.write(json.dumps(metadata, default=str))
            
            return True
        except Exception as e:
            self.logger.error(f"Error uploading to local storage: {e}")
            return False
    
    async def download(self, path: str) -> bytes:
        try:
            file_path = self.base_path / path
            async with aiofiles.open(file_path, 'rb') as f:
                return await f.read()
        except Exception as e:
            self.logger.error(f"Error downloading from local storage: {e}")
            raise
    
    async def delete(self, path: str) -> bool:
        try:
            file_path = self.base_path / path
            metadata_path = file_path.with_suffix('.metadata.json')
            
            if file_path.exists():
                file_path.unlink()
            if metadata_path.exists():
                metadata_path.unlink()
            
            return True
        except Exception as e:
            self.logger.error(f"Error deleting from local storage: {e}")
            return False
    
    async def list_objects(self, prefix: str) -> List[str]:
        try:
            prefix_path = self.base_path / prefix
            if not prefix_path.exists():
                return []
            
            files = []
            for file_path in prefix_path.rglob('*'):
                if file_path.is_file() and not file_path.name.endswith('.metadata.json'):
                    relative_path = file_path.relative_to(self.base_path)
                    files.append(str(relative_path))
            
            return files
        except Exception as e:
            self.logger.error(f"Error listing objects: {e}")
            return []
    
    async def get_metadata(self, path: str) -> Dict[str, Any]:
        try:
            file_path = self.base_path / path
            metadata_path = file_path.with_suffix('.metadata.json')
            
            if metadata_path.exists():
                async with aiofiles.open(metadata_path, 'r') as f:
                    content = await f.read()
                    return json.loads(content)
            
            return {}
        except Exception as e:
            self.logger.error(f"Error getting metadata: {e}")
            return {}

class S3StorageBackend(StorageBackend):
    """AWS S3 storage backend."""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.s3_client = boto3.client(
            's3',
            region_name=config.region,
            aws_access_key_id=config.credentials.get('access_key'),
            aws_secret_access_key=config.credentials.get('secret_key')
        )
        self.logger = logging.getLogger(__name__)
    
    async def upload(self, data: bytes, path: str, metadata: Dict[str, Any]) -> bool:
        try:
            # Convert metadata to strings
            s3_metadata = {k: str(v) for k, v in metadata.items() if k != 'tags'}
            
            self.s3_client.put_object(
                Bucket=self.config.bucket_name,
                Key=path,
                Body=data,
                Metadata=s3_metadata,
                StorageClass=self.config.storage_class
            )
            return True
        except Exception as e:
            self.logger.error(f"Error uploading to S3: {e}")
            return False
    
    async def download(self, path: str) -> bytes:
        try:
            response = self.s3_client.get_object(
                Bucket=self.config.bucket_name,
                Key=path
            )
            return response['Body'].read()
        except Exception as e:
            self.logger.error(f"Error downloading from S3: {e}")
            raise
    
    async def delete(self, path: str) -> bool:
        try:
            self.s3_client.delete_object(
                Bucket=self.config.bucket_name,
                Key=path
            )
            return True
        except Exception as e:
            self.logger.error(f"Error deleting from S3: {e}")
            return False
    
    async def list_objects(self, prefix: str) -> List[str]:
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.config.bucket_name,
                Prefix=prefix
            )
            
            return [obj['Key'] for obj in response.get('Contents', [])]
        except Exception as e:
            self.logger.error(f"Error listing S3 objects: {e}")
            return []
    
    async def get_metadata(self, path: str) -> Dict[str, Any]:
        try:
            response = self.s3_client.head_object(
                Bucket=self.config.bucket_name,
                Key=path
            )
            return response.get('Metadata', {})
        except Exception as e:
            self.logger.error(f"Error getting S3 metadata: {e}")
            return {}

class ModelArtifactManager:
    """
    🗄️ **Enterprise Model Artifact Manager**
    
    Advanced artifact storage, compression, and distribution system with
    multi-cloud support, data governance, and performance optimization.
    """
    
    def __init__(
        self,
        storage_configs: List[StorageConfig],
        compression_config: CompressionConfig,
        encryption_enabled: bool = True
    ):
        self.storage_configs = storage_configs
        self.compression_config = compression_config
        self.encryption_enabled = encryption_enabled
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.encryption_manager = ModelEncryptionManager() if encryption_enabled else None
        self.performance_monitor = PerformanceMonitor()
        self.audit_trail = AuditTrailGenerator()
        
        # Initialize storage backends
        self.storage_backends = {}
        self._initialize_storage_backends()
        
        # Compression components
        self.ml_compressor = CustomMLCompressor()
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
        # Artifact cache and metadata store
        self.artifact_metadata = {}
        self.access_cache = {}
        self.cache_lock = threading.Lock()
        
        self.logger.info(f"ModelArtifactManager initialized with {len(storage_configs)} storage backends")
    
    def _initialize_storage_backends(self):
        """Initialize storage backends based on configuration."""
        for config in self.storage_configs:
            if config.provider == StorageProvider.LOCAL:
                backend = LocalStorageBackend(config.bucket_name)
            elif config.provider == StorageProvider.AWS_S3:
                backend = S3StorageBackend(config)
            elif config.provider == StorageProvider.AZURE_BLOB:
                # Azure implementation would go here
                self.logger.warning("Azure Blob storage not yet implemented")
                continue
            elif config.provider == StorageProvider.GCP_STORAGE:
                # GCP implementation would go here
                self.logger.warning("GCP storage not yet implemented")
                continue
            else:
                self.logger.warning(f"Unknown storage provider: {config.provider}")
                continue
            
            self.storage_backends[config.provider] = backend
    
    def _calculate_checksum(self, data: bytes) -> str:
        """Calculate SHA-256 checksum of data."""
        return hashlib.sha256(data).hexdigest()
    
    def _compress_data(self, data: bytes, algorithm: CompressionAlgorithm) -> bytes:
        """Compress data using specified algorithm."""
        if algorithm == CompressionAlgorithm.NONE:
            return data
        elif algorithm == CompressionAlgorithm.GZIP:
            return gzip.compress(data, compresslevel=self.compression_config.compression_level)
        elif algorithm == CompressionAlgorithm.LZ4:
            return lz4.frame.compress(data, compression_level=self.compression_config.compression_level)
        elif algorithm == CompressionAlgorithm.BROTLI:
            return brotli.compress(data, quality=self.compression_config.compression_level)
        else:
            return data
    
    def _decompress_data(self, data: bytes, algorithm: CompressionAlgorithm) -> bytes:
        """Decompress data using specified algorithm."""
        if algorithm == CompressionAlgorithm.NONE:
            return data
        elif algorithm == CompressionAlgorithm.GZIP:
            return gzip.decompress(data)
        elif algorithm == CompressionAlgorithm.LZ4:
            return lz4.frame.decompress(data)
        elif algorithm == CompressionAlgorithm.BROTLI:
            return brotli.decompress(data)
        else:
            return data
    
    def _select_optimal_compression(self, data: bytes, artifact_type: ArtifactType) -> CompressionAlgorithm:
        """Select optimal compression algorithm based on data characteristics."""
        if not self.compression_config.adaptive_compression:
            return self.compression_config.algorithm
        
        # ML-specific compression selection
        if artifact_type == ArtifactType.MODEL_WEIGHTS:
            return CompressionAlgorithm.CUSTOM_ML
        elif artifact_type in [ArtifactType.TRAINING_DATA, ArtifactType.VALIDATION_DATA]:
            return CompressionAlgorithm.LZ4  # Fast for large datasets
        elif artifact_type == ArtifactType.METADATA:
            return CompressionAlgorithm.BROTLI  # High compression for text
        else:
            return CompressionAlgorithm.GZIP  # Balanced default
    
    def _generate_storage_path(self, artifact_id: str, creator_type: str, artifact_type: ArtifactType) -> str:
        """Generate optimized storage path for artifact."""
        date_prefix = datetime.now().strftime("%Y/%m/%d")
        return f"artifacts/{creator_type}/{artifact_type.value}/{date_prefix}/{artifact_id}"
    
    async def store_artifact(
        self,
        artifact_data: Any,
        artifact_id: str,
        artifact_type: ArtifactType,
        creator_type: str,
        model_name: str,
        model_version: str,
        tags: Dict[str, str] = None,
        lineage: Dict[str, Any] = None
    ) -> ArtifactMetadata:
        """
        🎯 **Store ML Artifact with Optimization**
        
        Store artifact with compression, encryption, and multi-cloud distribution.
        """
        try:
            start_time = datetime.now()
            
            # Serialize artifact data
            if artifact_type == ArtifactType.MODEL_WEIGHTS and isinstance(artifact_data, dict):
                # Special handling for PyTorch state dict
                if self.compression_config.algorithm == CompressionAlgorithm.CUSTOM_ML:
                    serialized_data = self.ml_compressor.compress_model_weights(artifact_data)
                    compression_algorithm = CompressionAlgorithm.CUSTOM_ML
                else:
                    serialized_data = pickle.dumps(artifact_data)
                    compression_algorithm = self._select_optimal_compression(serialized_data, artifact_type)
                    serialized_data = self._compress_data(serialized_data, compression_algorithm)
            else:
                # Standard serialization
                if isinstance(artifact_data, (dict, list)):
                    serialized_data = json.dumps(artifact_data, default=str).encode('utf-8')
                elif isinstance(artifact_data, str):
                    serialized_data = artifact_data.encode('utf-8')
                else:
                    serialized_data = pickle.dumps(artifact_data)
                
                compression_algorithm = self._select_optimal_compression(serialized_data, artifact_type)
                serialized_data = self._compress_data(serialized_data, compression_algorithm)
            
            original_size = len(pickle.dumps(artifact_data))
            compressed_size = len(serialized_data)
            compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
            
            # Encrypt if enabled
            encryption_key_id = None
            if self.encryption_enabled and self.encryption_manager:
                serialized_data, encryption_key_id = await self.encryption_manager.encrypt_data(
                    serialized_data, f"artifact_{artifact_id}"
                )
            
            # Calculate checksum
            checksum = self._calculate_checksum(serialized_data)
            
            # Generate storage path
            storage_path = self._generate_storage_path(artifact_id, creator_type, artifact_type)
            
            # Create metadata
            metadata = ArtifactMetadata(
                artifact_id=artifact_id,
                artifact_type=artifact_type,
                creator_type=creator_type,
                model_name=model_name,
                model_version=model_version,
                file_size_bytes=original_size,
                compressed_size_bytes=compressed_size,
                compression_ratio=compression_ratio,
                compression_algorithm=compression_algorithm,
                storage_provider=list(self.storage_backends.keys())[0],  # Primary storage
                storage_path=storage_path,
                checksum=checksum,
                encryption_key_id=encryption_key_id,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=0,
                tags=tags or {},
                lineage=lineage or {},
                retention_policy={'default_retention_days': 365},
                compliance_flags={'gdpr_compliant': True, 'dmca_protected': True}
            )
            
            # Store in all configured backends
            upload_tasks = []
            for provider, backend in self.storage_backends.items():
                metadata_dict = asdict(metadata)
                upload_tasks.append(backend.upload(serialized_data, storage_path, metadata_dict))
            
            upload_results = await asyncio.gather(*upload_tasks, return_exceptions=True)
            
            # Check upload success
            successful_uploads = sum(1 for result in upload_results if result is True)
            if successful_uploads == 0:
                raise Exception("Failed to upload to any storage backend")
            
            # Cache metadata
            with self.cache_lock:
                self.artifact_metadata[artifact_id] = metadata
            
            # Log metrics
            end_time = datetime.now()
            storage_time = (end_time - start_time).total_seconds()
            
            await self.performance_monitor.log_metrics(
                model_id=model_name,
                metrics={
                    'artifact_storage_time': storage_time,
                    'compression_ratio': compression_ratio,
                    'storage_efficiency': (original_size / compressed_size) / storage_time
                }
            )
            
            # Audit trail
            await self.audit_trail.log_event(
                event_type='artifact_stored',
                entity_id=artifact_id,
                metadata={
                    'artifact_type': artifact_type.value,
                    'creator_type': creator_type,
                    'compression_ratio': compression_ratio,
                    'storage_backends': list(self.storage_backends.keys())
                }
            )
            
            self.logger.info(
                f"Artifact {artifact_id} stored successfully. "
                f"Compression: {compression_ratio:.2f}x, Storage time: {storage_time:.2f}s"
            )
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error storing artifact {artifact_id}: {e}")
            raise
    
    async def retrieve_artifact(self, artifact_id: str, cache_enabled: bool = True) -> Tuple[Any, ArtifactMetadata]:
        """
        📥 **Retrieve ML Artifact with Caching**
        
        Retrieve artifact with intelligent caching and performance optimization.
        """
        try:
            start_time = datetime.now()
            
            # Check cache first
            if cache_enabled and artifact_id in self.access_cache:
                cached_data, cached_metadata = self.access_cache[artifact_id]
                self.logger.debug(f"Retrieved artifact {artifact_id} from cache")
                return cached_data, cached_metadata
            
            # Get metadata
            if artifact_id not in self.artifact_metadata:
                # Try to load from storage backends
                await self._load_artifact_metadata(artifact_id)
            
            if artifact_id not in self.artifact_metadata:
                raise ValueError(f"Artifact {artifact_id} not found")
            
            metadata = self.artifact_metadata[artifact_id]
            
            # Download from primary storage
            primary_backend = self.storage_backends[metadata.storage_provider]
            encrypted_data = await primary_backend.download(metadata.storage_path)
            
            # Decrypt if needed
            if metadata.encryption_key_id and self.encryption_manager:
                decrypted_data = await self.encryption_manager.decrypt_data(
                    encrypted_data, metadata.encryption_key_id
                )
            else:
                decrypted_data = encrypted_data
            
            # Verify checksum
            actual_checksum = self._calculate_checksum(decrypted_data)
            if actual_checksum != metadata.checksum:
                raise ValueError(f"Checksum mismatch for artifact {artifact_id}")
            
            # Decompress
            if metadata.compression_algorithm == CompressionAlgorithm.CUSTOM_ML:
                if metadata.artifact_type == ArtifactType.MODEL_WEIGHTS:
                    artifact_data = self.ml_compressor.decompress_model_weights(decrypted_data)
                else:
                    decompressed_data = self._decompress_data(decrypted_data, metadata.compression_algorithm)
                    artifact_data = pickle.loads(decompressed_data)
            else:
                decompressed_data = self._decompress_data(decrypted_data, metadata.compression_algorithm)
                
                # Deserialize based on artifact type
                if metadata.artifact_type in [ArtifactType.METADATA, ArtifactType.EXPERIMENT_LOG]:
                    try:
                        artifact_data = json.loads(decompressed_data.decode('utf-8'))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        artifact_data = pickle.loads(decompressed_data)
                else:
                    artifact_data = pickle.loads(decompressed_data)
            
            # Update access statistics
            metadata.last_accessed = datetime.now()
            metadata.access_count += 1
            
            # Cache if enabled
            if cache_enabled:
                with self.cache_lock:
                    self.access_cache[artifact_id] = (artifact_data, metadata)
                    
                    # Implement LRU cache eviction
                    if len(self.access_cache) > 100:  # Max cache size
                        oldest_artifact = min(
                            self.access_cache.keys(),
                            key=lambda k: self.access_cache[k][1].last_accessed
                        )
                        del self.access_cache[oldest_artifact]
            
            # Log metrics
            end_time = datetime.now()
            retrieval_time = (end_time - start_time).total_seconds()
            
            await self.performance_monitor.log_metrics(
                model_id=metadata.model_name,
                metrics={
                    'artifact_retrieval_time': retrieval_time,
                    'cache_hit': cache_enabled and artifact_id in self.access_cache
                }
            )
            
            # Audit trail
            await self.audit_trail.log_event(
                event_type='artifact_retrieved',
                entity_id=artifact_id,
                metadata={
                    'retrieval_time': retrieval_time,
                    'cache_hit': cache_enabled
                }
            )
            
            self.logger.debug(f"Retrieved artifact {artifact_id} in {retrieval_time:.2f}s")
            
            return artifact_data, metadata
            
        except Exception as e:
            self.logger.error(f"Error retrieving artifact {artifact_id}: {e}")
            raise
    
    async def _load_artifact_metadata(self, artifact_id: str):
        """Load artifact metadata from storage backends."""
        for provider, backend in self.storage_backends.items():
            try:
                # Try to find artifact by scanning storage paths
                objects = await backend.list_objects(f"artifacts/")
                for obj_path in objects:
                    if artifact_id in obj_path:
                        metadata_dict = await backend.get_metadata(obj_path)
                        if metadata_dict:
                            # Convert back to ArtifactMetadata
                            metadata = ArtifactMetadata(**metadata_dict)
                            self.artifact_metadata[artifact_id] = metadata
                            return
            except Exception as e:
                self.logger.debug(f"Error loading metadata from {provider}: {e}")
                continue
    
    async def delete_artifact(self, artifact_id: str, force: bool = False) -> bool:
        """
        🗑️ **Delete ML Artifact with Governance**
        
        Delete artifact with retention policy checks and audit logging.
        """
        try:
            if artifact_id not in self.artifact_metadata:
                await self._load_artifact_metadata(artifact_id)
            
            if artifact_id not in self.artifact_metadata:
                raise ValueError(f"Artifact {artifact_id} not found")
            
            metadata = self.artifact_metadata[artifact_id]
            
            # Check retention policy
            if not force:
                retention_days = metadata.retention_policy.get('default_retention_days', 365)
                age_days = (datetime.now() - metadata.created_at).days
                
                if age_days < retention_days:
                    raise ValueError(
                        f"Artifact {artifact_id} cannot be deleted. "
                        f"Retention policy requires {retention_days} days, artifact is {age_days} days old"
                    )
            
            # Delete from all storage backends
            deletion_tasks = []
            for provider, backend in self.storage_backends.items():
                deletion_tasks.append(backend.delete(metadata.storage_path))
            
            deletion_results = await asyncio.gather(*deletion_tasks, return_exceptions=True)
            
            # Check deletion success
            successful_deletions = sum(1 for result in deletion_results if result is True)
            
            # Remove from cache and metadata
            with self.cache_lock:
                if artifact_id in self.access_cache:
                    del self.access_cache[artifact_id]
                if artifact_id in self.artifact_metadata:
                    del self.artifact_metadata[artifact_id]
            
            # Audit trail
            await self.audit_trail.log_event(
                event_type='artifact_deleted',
                entity_id=artifact_id,
                metadata={
                    'forced_deletion': force,
                    'successful_deletions': successful_deletions,
                    'total_backends': len(self.storage_backends)
                }
            )
            
            self.logger.info(f"Artifact {artifact_id} deleted from {successful_deletions} backends")
            
            return successful_deletions > 0
            
        except Exception as e:
            self.logger.error(f"Error deleting artifact {artifact_id}: {e}")
            raise
    
    async def list_artifacts(
        self,
        creator_type: str = None,
        artifact_type: ArtifactType = None,
        model_name: str = None,
        tags: Dict[str, str] = None
    ) -> List[ArtifactMetadata]:
        """
        📋 **List Artifacts with Filtering**
        
        List artifacts with comprehensive filtering and sorting options.
        """
        try:
            # Load all metadata if not already loaded
            if not self.artifact_metadata:
                for provider, backend in self.storage_backends.items():
                    objects = await backend.list_objects("artifacts/")
                    for obj_path in objects:
                        metadata_dict = await backend.get_metadata(obj_path)
                        if metadata_dict:
                            artifact_id = metadata_dict.get('artifact_id')
                            if artifact_id:
                                metadata = ArtifactMetadata(**metadata_dict)
                                self.artifact_metadata[artifact_id] = metadata
            
            # Filter artifacts
            filtered_artifacts = []
            for artifact_id, metadata in self.artifact_metadata.items():
                # Apply filters
                if creator_type and metadata.creator_type != creator_type:
                    continue
                if artifact_type and metadata.artifact_type != artifact_type:
                    continue
                if model_name and metadata.model_name != model_name:
                    continue
                if tags:
                    if not all(metadata.tags.get(k) == v for k, v in tags.items()):
                        continue
                
                filtered_artifacts.append(metadata)
            
            # Sort by creation time (newest first)
            filtered_artifacts.sort(key=lambda x: x.created_at, reverse=True)
            
            return filtered_artifacts
            
        except Exception as e:
            self.logger.error(f"Error listing artifacts: {e}")
            raise
    
    async def get_storage_analytics(self) -> Dict[str, Any]:
        """
        📊 **Storage Analytics and Insights**
        
        Comprehensive analytics on storage usage, efficiency, and costs.
        """
        try:
            artifacts = await self.list_artifacts()
            
            if not artifacts:
                return {
                    'total_artifacts': 0,
                    'total_storage_bytes': 0,
                    'compression_efficiency': 0,
                    'storage_distribution': {},
                    'creator_type_distribution': {},
                    'artifact_type_distribution': {}
                }
            
            # Calculate analytics
            total_original_size = sum(a.file_size_bytes for a in artifacts)
            total_compressed_size = sum(a.compressed_size_bytes for a in artifacts)
            
            compression_efficiency = (
                (total_original_size - total_compressed_size) / total_original_size * 100
                if total_original_size > 0 else 0
            )
            
            # Distribution analytics
            storage_distribution = {}
            creator_type_distribution = {}
            artifact_type_distribution = {}
            
            for artifact in artifacts:
                # Storage provider distribution
                provider = artifact.storage_provider.value
                storage_distribution[provider] = storage_distribution.get(provider, 0) + 1
                
                # Creator type distribution
                creator = artifact.creator_type
                creator_type_distribution[creator] = creator_type_distribution.get(creator, 0) + 1
                
                # Artifact type distribution
                art_type = artifact.artifact_type.value
                artifact_type_distribution[art_type] = artifact_type_distribution.get(art_type, 0) + 1
            
            # Access patterns
            most_accessed = max(artifacts, key=lambda x: x.access_count) if artifacts else None
            avg_access_count = np.mean([a.access_count for a in artifacts])
            
            analytics = {
                'total_artifacts': len(artifacts),
                'total_storage_bytes': total_compressed_size,
                'original_size_bytes': total_original_size,
                'compression_efficiency_percent': compression_efficiency,
                'average_compression_ratio': np.mean([a.compression_ratio for a in artifacts]),
                'storage_distribution': storage_distribution,
                'creator_type_distribution': creator_type_distribution,
                'artifact_type_distribution': artifact_type_distribution,
                'access_patterns': {
                    'most_accessed_artifact': most_accessed.artifact_id if most_accessed else None,
                    'max_access_count': most_accessed.access_count if most_accessed else 0,
                    'average_access_count': avg_access_count
                },
                'storage_efficiency_score': (compression_efficiency + avg_access_count) / 2
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error generating storage analytics: {e}")
            raise
    
    def cleanup_cache(self):
        """Clean up memory cache."""
        with self.cache_lock:
            self.access_cache.clear()
        self.logger.info("Artifact cache cleared")

# Factory for creating model artifact managers
class ModelArtifactManagerFactory:
    """Factory for creating optimized model artifact managers."""
    
    @staticmethod
    def create_local_manager(base_path: str = "./artifacts") -> ModelArtifactManager:
        """Create manager with local storage only."""
        storage_config = StorageConfig(
            provider=StorageProvider.LOCAL,
            bucket_name=base_path
        )
        compression_config = CompressionConfig(
            algorithm=CompressionAlgorithm.LZ4,
            compression_level=4
        )
        return ModelArtifactManager([storage_config], compression_config)
    
    @staticmethod
    def create_cloud_manager(
        aws_config: Dict[str, str] = None,
        azure_config: Dict[str, str] = None,
        gcp_config: Dict[str, str] = None
    ) -> ModelArtifactManager:
        """Create manager with cloud storage backends."""
        storage_configs = []
        
        if aws_config:
            storage_configs.append(StorageConfig(
                provider=StorageProvider.AWS_S3,
                bucket_name=aws_config['bucket'],
                region=aws_config.get('region', 'us-east-1'),
                credentials=aws_config
            ))
        
        # Add other cloud providers as needed
        
        compression_config = CompressionConfig(
            algorithm=CompressionAlgorithm.CUSTOM_ML,
            adaptive_compression=True
        )
        
        return ModelArtifactManager(storage_configs, compression_config)
    
    @staticmethod
    def create_hybrid_manager(local_path: str, cloud_configs: List[Dict]) -> ModelArtifactManager:
        """Create manager with hybrid local + cloud storage."""
        storage_configs = [
            StorageConfig(
                provider=StorageProvider.LOCAL,
                bucket_name=local_path
            )
        ]
        
        for config in cloud_configs:
            if config['provider'] == 'aws':
                storage_configs.append(StorageConfig(
                    provider=StorageProvider.AWS_S3,
                    bucket_name=config['bucket'],
                    region=config.get('region'),
                    credentials=config
                ))
        
        compression_config = CompressionConfig(
            algorithm=CompressionAlgorithm.CUSTOM_ML,
            adaptive_compression=True,
            parallel_compression=True
        )
        
        return ModelArtifactManager(storage_configs, compression_config, encryption_enabled=True)

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Example usage
    async def demo_artifact_manager():
        manager = ModelArtifactManagerFactory.create_local_manager()
        
        # Store a model artifact
        dummy_model = {'layer1.weight': torch.randn(100, 50), 'layer1.bias': torch.randn(100)}
        
        metadata = await manager.store_artifact(
            artifact_data=dummy_model,
            artifact_id="demo_model_v1",
            artifact_type=ArtifactType.MODEL_WEIGHTS,
            creator_type="musician",
            model_name="audio_classifier",
            model_version="1.0.0",
            tags={"experiment": "baseline"},
            lineage={"training_data": "dataset_v1"}
        )
        
        print(f"Stored artifact: {metadata.artifact_id}")
        
        # Retrieve artifact
        retrieved_data, retrieved_metadata = await manager.retrieve_artifact("demo_model_v1")
        print(f"Retrieved artifact: {retrieved_metadata.artifact_id}")
        
        # Get analytics
        analytics = await manager.get_storage_analytics()
        print(f"Storage analytics: {analytics}")
    
    # Run demo
    asyncio.run(demo_artifact_manager())