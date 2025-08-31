"""Cache Serializer Module
=======================

Specialized serialization for cache data and storage optimization.
Optimized for high-performance caching, TTL management, and data retrieval.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION:
This code, concept, and intellectual property belong exclusively to Fahed Mlaiel (mlaiel@live.de). 
Any unauthorized copying, distribution, modification, or commercial use is STRICTLY PROHIBITED 
and will result in immediate legal action under German and International Copyright Law.

ZERO TOLERANCE POLICY: Anyone attempting to steal, copy, or misappropriate this code or concept 
will face severe legal consequences including but not limited to criminal charges, civil litigation, 
and substantial financial damages.

AUTHORIZED USE ONLY: Contact mlaiel@live.de for official licensing agreements.

Expertise combinée:
- Lead Developer IA: Architecture de cache intelligente et optimisée
- Backend Senior: Infrastructure de cache haute performance distribuée
- ML Engineer: Algorithmes prédictifs pour optimisation de cache
- DBA Expert: Optimisation stockage et récupération de données
- Sécurité: Protection et chiffrement des données en cache
- Microservices: Architecture de cache distribuée multi-niveaux
- Audio/Vidéo: Cache optimisé pour contenu multimédia lourd
- DevOps: Monitoring et scaling automatique des systèmes de cache
- IA Prompt Engineer: Cache intelligent pour réponses IA optimisées
"""
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
import base64
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

class CacheType(Enum):
    """Types of cache storage."""    MEMORY = "memory"
    REDIS = "redis"
    DISK = "disk"
    DISTRIBUTED = "distributed"
    HYBRID = "hybrid"

class CacheStrategy(Enum):
    """Cache eviction strategies."""    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time To Live
    ADAPTIVE = "adaptive"

class CompressionAlgorithm(Enum):
    """Compression algorithms for cache data."""    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    ZSTD = "zstd"
    SNAPPY = "snappy"

@dataclass
class CacheMetrics:
    """Cache performance metrics."""    hit_count: int = 0
    miss_count: int = 0
    eviction_count: int = 0
    total_size_bytes: int = 0
    entry_count: int = 0
    average_access_time: float = 0.0
    compression_ratio: float = 1.0
    memory_efficiency: float = 100.0

@dataclass
class CacheEntry:
    """Individual cache entry."""    key: str
    data: Any
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    access_count: int = 0
    size_bytes: int = 0
    compressed: bool = False
    compression_algorithm: Optional[CompressionAlgorithm] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

class CacheData(BaseModel):
    """    Comprehensive cache data model.
    
    Represents cache entries, metadata, and performance metrics
    for the IA-Influencer-Agent crawler caching system.
    """    
    # Cache identification
    cache_id: str = Field(..., description="Unique cache identifier")
    cache_name: str = Field(..., description="Cache name/namespace")
    cache_type: CacheType = Field(default=CacheType.MEMORY)
    cache_strategy: CacheStrategy = Field(default=CacheStrategy.LRU)
    
    # Cache configuration
    max_size_bytes: int = Field(default=100 * 1024 * 1024)  # 100MB
    max_entries: int = Field(default=10000)
    default_ttl_seconds: int = Field(default=3600)  # 1 hour
    compression_enabled: bool = Field(default=True)
    compression_threshold: int = Field(default=1024)  # 1KB
    compression_algorithm: CompressionAlgorithm = Field(default=CompressionAlgorithm.ZSTD)
    
    # Cache entries
    entries: Dict[str, CacheEntry] = Field(default_factory=dict)
    
    # Performance metrics
    metrics: CacheMetrics = Field(default_factory=CacheMetrics)
    
    # Access patterns
    hot_keys: List[str] = Field(default_factory=list)
    cold_keys: List[str] = Field(default_factory=list)
    access_frequency: Dict[str, int] = Field(default_factory=dict)
    
    # Maintenance
    last_cleanup: datetime = Field(default_factory=datetime.now)
    next_cleanup: datetime = Field(default_factory=lambda: datetime.now() + timedelta(hours=1))
    cleanup_interval_seconds: int = Field(default=3600)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @validator('cache_type', pre=True)
    def validate_cache_type(cls, v):
        if isinstance(v, str):
            return CacheType(v.lower())
        return v
    
    @validator('cache_strategy', pre=True)
    def validate_cache_strategy(cls, v):
        if isinstance(v, str):
            return CacheStrategy(v.lower())
        return v
    
    @validator('compression_algorithm', pre=True)
    def validate_compression_algorithm(cls, v):
        if isinstance(v, str):
            return CompressionAlgorithm(v.lower())
        return v

class CacheSerializer:
    """    Advanced cache data serialization system.
    
    Handles efficient serialization and deserialization of cache
    entries, metadata, and performance metrics with optimization
    for high-frequency cache operations.
    """    
    def __init__(self):
        """Initialize cache serializer."""        self.serialization_cache = {}  # Internal cache for serialization
        self.max_entry_size = 10 * 1024 * 1024  # 10MB per entry
        
        logger.info("Cache serializer initialized")
    
    def serialize_cache_data(
        self,
        cache_data: CacheData,
        include_entries: bool = True,
        max_entries: Optional[int] = None
    ) -> Dict[str, Any]:
        """        Serialize cache data to dictionary format.
        
        Args:
            cache_data: Cache data to serialize
            include_entries: Whether to include cache entries
            max_entries: Maximum number of entries to include
            
        Returns:
            Serialized cache dictionary
        """        try:
            # Convert to dictionary
            data = cache_data.dict(exclude={'entries'})
            
            # Handle datetime conversions
            data['created_at'] = cache_data.created_at.isoformat()
            data['updated_at'] = cache_data.updated_at.isoformat()
            data['last_cleanup'] = cache_data.last_cleanup.isoformat()
            data['next_cleanup'] = cache_data.next_cleanup.isoformat()
            
            # Serialize cache metrics
            data['metrics'] = self._serialize_cache_metrics(cache_data.metrics)
            
            # Handle cache entries
            if include_entries and cache_data.entries:
                entries_to_serialize = cache_data.entries
                
                # Limit number of entries if specified
                if max_entries and len(entries_to_serialize) > max_entries:
                    # Keep most recently accessed entries
                    sorted_entries = sorted(
                        entries_to_serialize.items(),
                        key=lambda x: x[1].accessed_at,
                        reverse=True
                    )
                    entries_to_serialize = dict(sorted_entries[:max_entries])
                    data['_entries_truncated'] = True
                    data['_total_entries_count'] = len(cache_data.entries)
                
                data['entries'] = {
                    key: self._serialize_cache_entry(entry)
                    for key, entry in entries_to_serialize.items()
                }
            else:
                data['entries'] = {}
            
            # Convert enums
            data['cache_type'] = cache_data.cache_type.value
            data['cache_strategy'] = cache_data.cache_strategy.value
            data['compression_algorithm'] = cache_data.compression_algorithm.value
            
            # Add serialization metadata
            data['_serialization'] = {
                'version': '2.0.0',
                'serialized_at': datetime.now().isoformat(),
                'includes_entries': include_entries,
                'max_entries': max_entries,
                'cache_type': cache_data.cache_type.value
            }
            
            logger.debug(f"Serialized cache data {cache_data.cache_id}")
            return data
            
        except Exception as e:
            logger.error(f"Cache data serialization failed: {e}")
            raise
    
    def deserialize_cache_data(
        self,
        data: Dict[str, Any]
    ) -> CacheData:
        """        Deserialize cache data from dictionary format.
        
        Args:
            data: Serialized cache dictionary
            
        Returns:
            Deserialized CacheData object
        """        try:
            # Handle datetime conversions
            datetime_fields = ['created_at', 'updated_at', 'last_cleanup', 'next_cleanup']
            for field in datetime_fields:
                if isinstance(data.get(field), str):
                    data[field] = datetime.fromisoformat(data[field])
            
            # Deserialize cache metrics
            if 'metrics' in data and data['metrics']:
                data['metrics'] = self._deserialize_cache_metrics(data['metrics'])
            
            # Deserialize cache entries
            if 'entries' in data and data['entries']:
                data['entries'] = {
                    key: self._deserialize_cache_entry(entry_data)
                    for key, entry_data in data['entries'].items()
                }
            
            # Remove serialization metadata
            data.pop('_serialization', None)
            data.pop('_entries_truncated', None)
            data.pop('_total_entries_count', None)
            
            # Create CacheData object
            cache_data = CacheData(**data)
            
            logger.debug(f"Deserialized cache data {cache_data.cache_id}")
            return cache_data
            
        except Exception as e:
            logger.error(f"Cache data deserialization failed: {e}")
            raise
    
    def serialize_cache_entry(
        self,
        entry: CacheEntry,
        compress_data: bool = True
    ) -> Dict[str, Any]:
        """        Serialize individual cache entry.
        
        Args:
            entry: Cache entry to serialize
            compress_data: Whether to compress entry data
            
        Returns:
            Serialized cache entry dictionary
        """        try:
            return self._serialize_cache_entry(entry, compress_data)
            
        except Exception as e:
            logger.error(f"Cache entry serialization failed: {e}")
            raise
    
    def deserialize_cache_entry(
        self,
        data: Dict[str, Any]
    ) -> CacheEntry:
        """        Deserialize individual cache entry.
        
        Args:
            data: Serialized cache entry dictionary
            
        Returns:
            Deserialized CacheEntry object
        """        try:
            return self._deserialize_cache_entry(data)
            
        except Exception as e:
            logger.error(f"Cache entry deserialization failed: {e}")
            raise
    
    def _serialize_cache_entry(
        self,
        entry: CacheEntry,
        compress_data: bool = True
    ) -> Dict[str, Any]:
        """Internal cache entry serialization."""        data = {
            'key': entry.key,
            'created_at': entry.created_at.isoformat(),
            'accessed_at': entry.accessed_at.isoformat(),
            'access_count': entry.access_count,
            'size_bytes': entry.size_bytes,
            'compressed': entry.compressed,
            'metadata': entry.metadata,
            'tags': entry.tags
        }
        
        if entry.expires_at:
            data['expires_at'] = entry.expires_at.isoformat()
        
        if entry.compression_algorithm:
            data['compression_algorithm'] = entry.compression_algorithm.value
        
        # Handle entry data serialization
        try:
            # Calculate data size
            data_json = json.dumps(entry.data, default=str)
            data_size = len(data_json.encode('utf-8'))
            
            # Check if data should be compressed
            should_compress = (
                compress_data and 
                data_size > 1024 and  # > 1KB
                data_size < self.max_entry_size
            )
            
            if should_compress:
                compressed_data = self._compress_entry_data(entry.data)
                data['data'] = compressed_data
                data['_data_compressed'] = True
            else:
                data['data'] = entry.data
                data['_data_compressed'] = False
                
        except Exception as e:
            logger.warning(f"Entry data serialization failed: {e}")
            data['data'] = str(entry.data)  # Fallback to string representation
            data['_data_compressed'] = False
        
        return data
    
    def _deserialize_cache_entry(self, data: Dict[str, Any]) -> CacheEntry:
        """Internal cache entry deserialization."""        # Handle datetime conversions
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        if isinstance(data.get('accessed_at'), str):
            data['accessed_at'] = datetime.fromisoformat(data['accessed_at'])
        
        if isinstance(data.get('expires_at'), str):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        
        # Handle compression algorithm enum
        if isinstance(data.get('compression_algorithm'), str):
            data['compression_algorithm'] = CompressionAlgorithm(data['compression_algorithm'])
        
        # Handle entry data deserialization
        if data.get('_data_compressed', False):
            data['data'] = self._decompress_entry_data(data['data'])
        
        # Remove compression metadata
        data.pop('_data_compressed', None)
        
        return CacheEntry(**data)
    
    def _serialize_cache_metrics(self, metrics: CacheMetrics) -> Dict[str, Any]:
        """Serialize cache metrics."""        return {
            'hit_count': metrics.hit_count,
            'miss_count': metrics.miss_count,
            'eviction_count': metrics.eviction_count,
            'total_size_bytes': metrics.total_size_bytes,
            'entry_count': metrics.entry_count,
            'average_access_time': metrics.average_access_time,
            'compression_ratio': metrics.compression_ratio,
            'memory_efficiency': metrics.memory_efficiency
        }
    
    def _deserialize_cache_metrics(self, data: Dict[str, Any]) -> CacheMetrics:
        """Deserialize cache metrics."""        return CacheMetrics(**data)
    
    def _compress_entry_data(self, data: Any) -> str:
        """Compress cache entry data."""        try:
            import gzip
            import pickle
            
            # Serialize data to bytes
            pickled_data = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Compress
            compressed = gzip.compress(pickled_data)
            
            # Encode to base64
            encoded = base64.b64encode(compressed).decode('utf-8')
            
            return f"gzip_pickle:{encoded}"
            
        except Exception as e:
            logger.error(f"Entry data compression failed: {e}")
            # Fallback to JSON
            return json.dumps(data, default=str)
    
    def _decompress_entry_data(self, compressed_data: str) -> Any:
        """Decompress cache entry data."""        try:
            if compressed_data.startswith('gzip_pickle:'):
                import gzip
                import pickle
                
                # Remove prefix and decode
                encoded = compressed_data[12:]
                compressed = base64.b64decode(encoded)
                
                # Decompress
                pickled_data = gzip.decompress(compressed)
                
                # Unpickle
                return pickle.loads(pickled_data)
            else:
                # JSON fallback
                return json.loads(compressed_data)
                
        except Exception as e:
            logger.error(f"Entry data decompression failed: {e}")
            return compressed_data  # Return as-is if decompression fails
    
    def calculate_cache_key(
        self,
        base_key: str,
        parameters: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None
    ) -> str:
        """Calculate standardized cache key."""        try:
            key_components = [base_key]
            
            if namespace:
                key_components.insert(0, namespace)
            
            if parameters:
                # Sort parameters for consistent key generation
                sorted_params = sorted(parameters.items())
                param_string = json.dumps(sorted_params, sort_keys=True, default=str)
                param_hash = hashlib.sha256(param_string.encode()).hexdigest()[:16]
                key_components.append(param_hash)
            
            cache_key = ':'.join(key_components)
            
            # Ensure key length is reasonable
            if len(cache_key) > 250:  # Redis key limit is 512MB, but keep reasonable
                key_hash = hashlib.sha256(cache_key.encode()).hexdigest()
                cache_key = f"{base_key}:{key_hash[:16]}"
            
            return cache_key
            
        except Exception as e:
            logger.error(f"Cache key calculation failed: {e}")
            return base_key
    
    def optimize_cache_data(
        self,
        cache_data: CacheData,
        cleanup_expired: bool = True,
        compress_large_entries: bool = True
    ) -> CacheData:
        """Optimize cache data for better performance."""        try:
            optimized_entries = {}
            current_time = datetime.now()
            
            for key, entry in cache_data.entries.items():
                # Skip expired entries if cleanup is enabled
                if cleanup_expired and entry.expires_at and entry.expires_at < current_time:
                    cache_data.metrics.eviction_count += 1
                    continue
                
                # Compress large entries if needed
                if compress_large_entries and entry.size_bytes > cache_data.compression_threshold:
                    if not entry.compressed:
                        # Re-serialize with compression
                        serialized = self._serialize_cache_entry(entry, compress_data=True)
                        entry = self._deserialize_cache_entry(serialized)
                
                optimized_entries[key] = entry
            
            # Update cache data
            cache_data.entries = optimized_entries
            cache_data.metrics.entry_count = len(optimized_entries)
            cache_data.metrics.total_size_bytes = sum(
                entry.size_bytes for entry in optimized_entries.values()
            )
            cache_data.last_cleanup = current_time
            cache_data.next_cleanup = current_time + timedelta(
                seconds=cache_data.cleanup_interval_seconds
            )
            cache_data.updated_at = current_time
            
            logger.info(f"Optimized cache {cache_data.cache_id}: {len(optimized_entries)} entries")
            return cache_data
            
        except Exception as e:
            logger.error(f"Cache optimization failed: {e}")
            return cache_data
    
    def calculate_cache_statistics(self, cache_data: CacheData) -> Dict[str, Any]:
        """Calculate comprehensive cache statistics."""        try:
            total_requests = cache_data.metrics.hit_count + cache_data.metrics.miss_count
            hit_rate = cache_data.metrics.hit_count / max(total_requests, 1) * 100
            
            # Entry size distribution
            entry_sizes = [entry.size_bytes for entry in cache_data.entries.values()]
            size_stats = {}
            if entry_sizes:
                size_stats = {
                    'min_size': min(entry_sizes),
                    'max_size': max(entry_sizes),
                    'avg_size': sum(entry_sizes) / len(entry_sizes),
                    'total_size': sum(entry_sizes)
                }
            
            # Access pattern analysis
            access_counts = [entry.access_count for entry in cache_data.entries.values()]
            access_stats = {}
            if access_counts:
                access_stats = {
                    'min_access': min(access_counts),
                    'max_access': max(access_counts),
                    'avg_access': sum(access_counts) / len(access_counts),
                    'total_accesses': sum(access_counts)
                }
            
            # Age analysis
            current_time = datetime.now()
            ages = [
                (current_time - entry.created_at).total_seconds()
                for entry in cache_data.entries.values()
            ]
            age_stats = {}
            if ages:
                age_stats = {
                    'newest_age_seconds': min(ages),
                    'oldest_age_seconds': max(ages),
                    'avg_age_seconds': sum(ages) / len(ages)
                }
            
            return {
                'cache_id': cache_data.cache_id,
                'cache_type': cache_data.cache_type.value,
                'performance': {
                    'hit_rate_percent': hit_rate,
                    'miss_rate_percent': 100 - hit_rate,
                    'total_requests': total_requests,
                    'eviction_count': cache_data.metrics.eviction_count,
                    'average_access_time': cache_data.metrics.average_access_time
                },
                'capacity': {
                    'entry_count': len(cache_data.entries),
                    'max_entries': cache_data.max_entries,
                    'utilization_percent': len(cache_data.entries) / max(cache_data.max_entries, 1) * 100,
                    'total_size_bytes': cache_data.metrics.total_size_bytes,
                    'max_size_bytes': cache_data.max_size_bytes,
                    'size_utilization_percent': cache_data.metrics.total_size_bytes / max(cache_data.max_size_bytes, 1) * 100
                },
                'entry_statistics': size_stats,
                'access_statistics': access_stats,
                'age_statistics': age_stats,
                'compression': {
                    'compression_ratio': cache_data.metrics.compression_ratio,
                    'compression_enabled': cache_data.compression_enabled,
                    'compression_algorithm': cache_data.compression_algorithm.value
                },
                'last_cleanup': cache_data.last_cleanup.isoformat(),
                'next_cleanup': cache_data.next_cleanup.isoformat(),
                'calculated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Cache statistics calculation failed: {e}")
            return {'error': str(e)}


# Export main classes
__all__ = [
    'CacheSerializer',
    'CacheData',
    'CacheEntry',
    'CacheMetrics',
    'CacheType',
    'CacheStrategy',
    'CompressionAlgorithm'
]
