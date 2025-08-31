"""Data Serializers Module - Professional Serialization System
==========================================================

Advanced data serialization and deserialization system for IA-Influencer-Agent platform.
Implements comprehensive serialization for crawler data, content protection, and surveillance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts
"""
import logging
from typing import Dict, List, Optional, Any, Type, Union, Protocol
from datetime import datetime
import json
import pickle
import msgpack
import orjson
from dataclasses import dataclass, asdict
from enum import Enum
import base64
import gzip
import lz4.frame
import zstandard as zstd
from pydantic import BaseModel, Field, ValidationError
import numpy as np

# Import all serializer modules
from .content_serializer import ContentSerializer, ContentData
from .surveillance_serializer import SurveillanceSerializer, SurveillanceData
from .platform_serializer import PlatformSerializer, PlatformData
from .fingerprint_serializer import FingerprintSerializer, FingerprintData
from .violation_serializer import ViolationSerializer, ViolationData
from .analytics_serializer import AnalyticsSerializer, AnalyticsData
from .cache_serializer import CacheSerializer, CacheData
from .streaming_serializer import StreamingSerializer, StreamData
from .export_serializer import ExportSerializer, ExportData
from .metadata_serializer import MetadataSerializer, MetadataData

# Import index and orchestration system
from .index import (
    SerializerIndex,
    SerializerOrchestrator,
    SerializerType,
    OperationType,
    Priority,
    SerializationTask,
    SerializationMetrics,
    get_serializer_index,
    reset_serializer_index
)

logger = logging.getLogger(__name__)

class SerializationFormat(Enum):
    """Supported serialization formats."""    JSON = "json"
    ORJSON = "orjson"
    MSGPACK = "msgpack"
    PICKLE = "pickle"
    BINARY = "binary"
    PROTOBUF = "protobuf"
    AVRO = "avro"
    PARQUET = "parquet"

class CompressionType(Enum):
    """Supported compression types."""    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    ZSTD = "zstd"
    SNAPPY = "snappy"

class EncryptionLevel(Enum):
    """Data encryption levels."""    NONE = "none"
    BASIC = "basic"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"

@dataclass
class SerializationConfig:
    """Serialization configuration."""    default_format: SerializationFormat = SerializationFormat.ORJSON
    compression: CompressionType = CompressionType.ZSTD
    encryption: EncryptionLevel = EncryptionLevel.BASIC
    enable_validation: bool = True
    enable_versioning: bool = True
    enable_checksums: bool = True
    max_object_size: int = 100 * 1024 * 1024  # 100MB
    compression_threshold: int = 1024  # 1KB

class SerializationMetrics:
    """Serialization performance metrics."""    
    def __init__(self):
        self.serialization_count = 0
        self.deserialization_count = 0
        self.total_size_serialized = 0
        self.total_size_deserialized = 0
        self.compression_ratio_sum = 0.0
        self.serialization_time_sum = 0.0
        self.deserialization_time_sum = 0.0
        self.error_count = 0
        self.last_reset = datetime.now()
    
    def record_serialization(
        self,
        original_size: int,
        serialized_size: int,
        processing_time: float
    ) -> None:
        """Record serialization metrics."""        self.serialization_count += 1
        self.total_size_serialized += serialized_size
        self.compression_ratio_sum += original_size / serialized_size if serialized_size > 0 else 1.0
        self.serialization_time_sum += processing_time
    
    def record_deserialization(
        self,
        size: int,
        processing_time: float
    ) -> None:
        """Record deserialization metrics."""        self.deserialization_count += 1
        self.total_size_deserialized += size
        self.deserialization_time_sum += processing_time
    
    def record_error(self) -> None:
        """Record serialization error."""        self.error_count += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""        duration = (datetime.now() - self.last_reset).total_seconds()
        
        return {
            'period_duration_seconds': duration,
            'serialization': {
                'count': self.serialization_count,
                'total_size_bytes': self.total_size_serialized,
                'average_size_bytes': self.total_size_serialized / max(self.serialization_count, 1),
                'average_compression_ratio': self.compression_ratio_sum / max(self.serialization_count, 1),
                'average_time_seconds': self.serialization_time_sum / max(self.serialization_count, 1),
                'throughput_ops_per_second': self.serialization_count / max(duration, 1),
                'throughput_mb_per_second': (self.total_size_serialized / 1024 / 1024) / max(duration, 1)
            },
            'deserialization': {
                'count': self.deserialization_count,
                'total_size_bytes': self.total_size_deserialized,
                'average_size_bytes': self.total_size_deserialized / max(self.deserialization_count, 1),
                'average_time_seconds': self.deserialization_time_sum / max(self.deserialization_count, 1),
                'throughput_ops_per_second': self.deserialization_count / max(duration, 1),
                'throughput_mb_per_second': (self.total_size_deserialized / 1024 / 1024) / max(duration, 1)
            },
            'errors': {
                'count': self.error_count,
                'error_rate': self.error_count / max(self.serialization_count + self.deserialization_count, 1)
            }
        }
    
    def reset(self) -> None:
        """Reset all metrics."""        self.__init__()

class SerializationRegistry:
    """Registry for custom serializers."""    
    def __init__(self):
        self._serializers: Dict[str, Type] = {}
        self._deserializers: Dict[str, Type] = {}
        
        # Register built-in serializers
        self.register_serializer('content', ContentSerializer)
        self.register_serializer('surveillance', SurveillanceSerializer)
        self.register_serializer('platform', PlatformSerializer)
        self.register_serializer('metadata', MetadataSerializer)
        self.register_serializer('fingerprint', FingerprintSerializer)
        self.register_serializer('violation', ViolationSerializer)
        self.register_serializer('analytics', AnalyticsSerializer)
        self.register_serializer('cache', CacheSerializer)
        self.register_serializer('streaming', StreamingSerializer)
        self.register_serializer('export', ExportSerializer)
    
    def register_serializer(self, name: str, serializer_class: Type) -> None:
        """Register custom serializer."""        self._serializers[name] = serializer_class
        logger.debug(f"Registered serializer: {name}")
    
    def get_serializer(self, name: str) -> Optional[Type]:
        """Get serializer by name."""


        return self._serializers.get(name)
    
    def list_serializers(self) -> List[str]:
        """List available serializers."""


        return list(self._serializers.keys())

class SerializerManager:
    """    Central serializer management system.
    
    Coordinates all serialization operations with:
    - Multiple format support
    - Compression optimization
    - Encryption capabilities
    - Performance monitoring
    - Error handling
    - Data validation
    - Version management
    """    
    def __init__(self, config: Optional[SerializationConfig] = None):
        """Initialize serializer manager."""        self.config = config or SerializationConfig()
        self.metrics = SerializationMetrics()
        self.registry = SerializationRegistry()
        
        # Initialize compression engines
        self._init_compression_engines()
        
        # Initialize encryption
        self._init_encryption()
        
        logger.info("Serializer manager initialized successfully")
    
    def _init_compression_engines(self) -> None:
        """Initialize compression engines."""        self.compression_engines = {}
        
        # GZIP
        self.compression_engines[CompressionType.GZIP] = {
            'compress': lambda data: gzip.compress(data),
            'decompress': lambda data: gzip.decompress(data)
        }
        
        # LZ4
        self.compression_engines[CompressionType.LZ4] = {
            'compress': lambda data: lz4.frame.compress(data),
            'decompress': lambda data: lz4.frame.decompress(data)
        }
        
        # ZSTD
        cctx = zstd.ZstdCompressor(level=3)
        dctx = zstd.ZstdDecompressor()
        self.compression_engines[CompressionType.ZSTD] = {
            'compress': lambda data: cctx.compress(data),
            'decompress': lambda data: dctx.decompress(data)
        }
    
    def _init_encryption(self) -> None:
        """Initialize encryption systems."""        # Basic encryption placeholder
        self.encryption_key = b"default_key_placeholder_32_bytes"
        
        if self.config.encryption != EncryptionLevel.NONE:
            logger.info(f"Encryption enabled: {self.config.encryption.value}")
    
    async def serialize(
        self,
        data: Any,
        format_type: Optional[SerializationFormat] = None,
        compression: Optional[CompressionType] = None,
        include_metadata: bool = True
    ) -> bytes:
        """Serialize data with optional compression and encryption."""        start_time = datetime.now()
        
        try:
            # Use configured defaults
            format_type = format_type or self.config.default_format
            compression = compression or self.config.compression
            
            # Validate input size
            if hasattr(data, '__sizeof__'):
                size = data.__sizeof__()
                if size > self.config.max_object_size:
                    raise ValueError(f"Object too large: {size} > {self.config.max_object_size}")
            
            # Serialize data
            serialized_data = await self._serialize_data(data, format_type)
            original_size = len(serialized_data)
            
            # Apply compression if needed
            if compression != CompressionType.NONE and original_size >= self.config.compression_threshold:
                serialized_data = self._compress_data(serialized_data, compression)
            
            # Add metadata wrapper if requested
            if include_metadata:
                metadata = {
                    'format': format_type.value,
                    'compression': compression.value,
                    'original_size': original_size,
                    'compressed_size': len(serialized_data),
                    'serialized_at': datetime.now().isoformat(),
                    'version': '2.0.0'
                }
                
                if self.config.enable_checksums:
                    import hashlib
                    metadata['checksum'] = hashlib.sha256(serialized_data).hexdigest()
                
                # Wrap with metadata
                wrapper = {
                    'metadata': metadata,
                    'data': base64.b64encode(serialized_data).decode('utf-8')
                }
                
                serialized_data = orjson.dumps(wrapper)
            
            # Apply encryption if enabled
            if self.config.encryption != EncryptionLevel.NONE:
                serialized_data = self._encrypt_data(serialized_data)
            
            # Record metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.metrics.record_serialization(original_size, len(serialized_data), processing_time)
            
            logger.debug(
                f"Serialized data: {original_size} -> {len(serialized_data)} bytes "
                f"({format_type.value}, {compression.value}) in {processing_time:.3f}s"
            )
            
            return serialized_data
            
        except Exception as e:
            self.metrics.record_error()
            logger.error(f"Serialization failed: {e}")
            raise
    
    async def deserialize(
        self,
        data: bytes,
        expected_type: Optional[Type] = None
    ) -> Any:
        """Deserialize data with automatic format detection."""        start_time = datetime.now()
        
        try:
            # Apply decryption if needed
            if self.config.encryption != EncryptionLevel.NONE:
                data = self._decrypt_data(data)
            
            # Check for metadata wrapper
            metadata = None
            try:
                wrapper = orjson.loads(data)
                if isinstance(wrapper, dict) and 'metadata' in wrapper and 'data' in wrapper:
                    metadata = wrapper['metadata']
                    data = base64.b64decode(wrapper['data'])
            except:
                pass  # Not a metadata wrapper
            
            # Extract format and compression info
            format_type = SerializationFormat.ORJSON
            compression = CompressionType.NONE
            
            if metadata:
                format_type = SerializationFormat(metadata.get('format', 'orjson'))
                compression = CompressionType(metadata.get('compression', 'none'))
                
                # Verify checksum if available
                if self.config.enable_checksums and 'checksum' in metadata:
                    import hashlib
                    actual_checksum = hashlib.sha256(data).hexdigest()
                    if actual_checksum != metadata['checksum']:
                        raise ValueError("Checksum verification failed")
            
            # Apply decompression if needed
            if compression != CompressionType.NONE:
                data = self._decompress_data(data, compression)
            
            # Deserialize data
            result = await self._deserialize_data(data, format_type, expected_type)
            
            # Record metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.metrics.record_deserialization(len(data), processing_time)
            
            logger.debug(
                f"Deserialized {len(data)} bytes "
                f"({format_type.value}, {compression.value}) in {processing_time:.3f}s"
            )
            
            return result
            
        except Exception as e:
            self.metrics.record_error()
            logger.error(f"Deserialization failed: {e}")
            raise
    
    async def _serialize_data(
        self,
        data: Any,
        format_type: SerializationFormat
    ) -> bytes:
        """Serialize data in specified format."""        if format_type == SerializationFormat.JSON:
            return json.dumps(data, default=str, ensure_ascii=False).encode('utf-8')
        
        elif format_type == SerializationFormat.ORJSON:
            return orjson.dumps(data, default=str)
        
        elif format_type == SerializationFormat.MSGPACK:
            return msgpack.packb(data, default=str, use_bin_type=True)
        
        elif format_type == SerializationFormat.PICKLE:
            return pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
        
        elif format_type == SerializationFormat.BINARY:
            if hasattr(data, 'tobytes'):
                return data.tobytes()
            elif isinstance(data, bytes):
                return data
            else:
                raise ValueError("Data type not supported for binary serialization")
        
        else:
            raise ValueError(f"Unsupported serialization format: {format_type}")
    
    async def _deserialize_data(
        self,
        data: bytes,
        format_type: SerializationFormat,
        expected_type: Optional[Type] = None
    ) -> Any:
        """Deserialize data from specified format."""        if format_type == SerializationFormat.JSON:
            result = json.loads(data.decode('utf-8'))
        
        elif format_type == SerializationFormat.ORJSON:
            result = orjson.loads(data)
        
        elif format_type == SerializationFormat.MSGPACK:
            result = msgpack.unpackb(data, raw=False)
        
        elif format_type == SerializationFormat.PICKLE:
            result = pickle.loads(data)
        
        elif format_type == SerializationFormat.BINARY:
            if expected_type == np.ndarray:
                result = np.frombuffer(data)
            else:
                result = data
        
        else:
            raise ValueError(f"Unsupported deserialization format: {format_type}")
        
        # Validate result type if specified
        if expected_type and self.config.enable_validation:
            if not isinstance(result, expected_type):
                logger.warning(f"Deserialized type {type(result)} != expected {expected_type}")
        
        return result
    
    def _compress_data(self, data: bytes, compression: CompressionType) -> bytes:
        """Compress data using specified algorithm."""        if compression == CompressionType.NONE:
            return data
        
        engine = self.compression_engines.get(compression)
        if not engine:
            raise ValueError(f"Compression type not supported: {compression}")
        
        return engine['compress'](data)
    
    def _decompress_data(self, data: bytes, compression: CompressionType) -> bytes:
        """Decompress data using specified algorithm."""        if compression == CompressionType.NONE:
            return data
        
        engine = self.compression_engines.get(compression)
        if not engine:
            raise ValueError(f"Compression type not supported: {compression}")
        
        return engine['decompress'](data)
    
    def _encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data based on encryption level."""        if self.config.encryption == EncryptionLevel.NONE:
            return data
        
        # Basic encryption implementation
        # In production, use proper encryption libraries like cryptography
        from cryptography.fernet import Fernet
        
        # Generate or use existing key
        key = base64.urlsafe_b64encode(self.encryption_key)
        cipher = Fernet(key)
        
        return cipher.encrypt(data)
    
    def _decrypt_data(self, data: bytes) -> bytes:
        """Decrypt data based on encryption level."""        if self.config.encryption == EncryptionLevel.NONE:
            return data
        
        # Basic decryption implementation
        from cryptography.fernet import Fernet
        
        key = base64.urlsafe_b64encode(self.encryption_key)
        cipher = Fernet(key)
        
        return cipher.decrypt(data)
    
    def get_serializer(self, name: str) -> Optional[Type]:
        """Get specialized serializer by name."""


        return self.registry.get_serializer(name)
    
    def register_serializer(self, name: str, serializer_class: Type) -> None:
        """Register custom serializer."""        self.registry.register_serializer(name, serializer_class)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get serialization metrics."""


        return self.metrics.get_statistics()
    
    def reset_metrics(self) -> None:
        """Reset performance metrics."""        self.metrics.reset()
    
    async def benchmark_formats(
        self,
        test_data: Any,
        iterations: int = 100
    ) -> Dict[str, Dict[str, float]]:
        """Benchmark different serialization formats."""        results = {}
        
        for format_type in SerializationFormat:
            try:
                # Serialization benchmark
                start_time = datetime.now()
                for _ in range(iterations):
                    serialized = await self._serialize_data(test_data, format_type)
                serialization_time = (datetime.now() - start_time).total_seconds()
                
                # Deserialization benchmark
                start_time = datetime.now()
                for _ in range(iterations):
                    await self._deserialize_data(serialized, format_type)
                deserialization_time = (datetime.now() - start_time).total_seconds()
                
                results[format_type.value] = {
                    'serialization_time': serialization_time / iterations,
                    'deserialization_time': deserialization_time / iterations,
                    'serialized_size': len(serialized),
                    'compression_ratio': len(str(test_data).encode()) / len(serialized)
                }
                
            except Exception as e:
                logger.warning(f"Format {format_type.value} benchmark failed: {e}")
                results[format_type.value] = {'error': str(e)}
        
        return results


# Export main classes and functions
__all__ = [
    'SerializerManager',
    'SerializationConfig',
    'SerializationFormat',
    'CompressionType',
    'EncryptionLevel',
    'SerializationMetrics',
    'SerializationRegistry',
    'ContentSerializer',
    'SurveillanceSerializer',
    'PlatformSerializer',
    'MetadataSerializer',
    'FingerprintSerializer',
    'ViolationSerializer',
    'AnalyticsSerializer',
    'CacheSerializer',
    'StreamingSerializer',
    'ExportSerializer',
    'ContentData',
    'SurveillanceData',
    'PlatformData',
    'MetadataData',
    'FingerprintData',
    'ViolationData',
    'AnalyticsData',
    'CacheData',
    'StreamData',
    'ExportData',
    # Index and orchestration
    'SerializerIndex',
    'SerializerOrchestrator',
    'SerializerType',
    'OperationType',
    'Priority',
    'SerializationTask',
    'SerializationMetrics',
    'get_serializer_index',
    'reset_serializer_index'
]
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
