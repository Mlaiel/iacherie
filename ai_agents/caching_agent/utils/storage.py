"""Cache Storage - Multi-Layer Storage Implementation

Advanced storage backend providing seamless integration across memory, Redis,
database, and CDN layers with intelligent data placement and retrieval.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import pickle
import gzip
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum
import hashlib
import os

import redis.asyncio as aioredis
import psycopg2.pool
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import aioboto3
import aiofiles

logger = logging.getLogger(__name__)

class StorageLevel(Enum):
    """
Storage tier levels"""

    L1_MEMORY = 1
    L2_REDIS = 2
    L3_DATABASE = 3
    L4_S3_CDN = 4

class CompressionType(Enum):
    """
Supported compression algorithms"""

    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    ZSTD = "zstd"

@dataclass
class StorageConfig:
    """Storage configuration settings"""
    # Memory settings
    max_memory_size: int = 512 * 1024 * 1024  # 512MB
    memory_cleanup_threshold: float = 0.8
    
    # Redis settings
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0
    redis_max_connections: int = 100
    redis_key_prefix: str = "cache:"
    
    # Database settings
    database_url: str = ""
    database_table: str = "cache_storage"
    database_pool_size: int = 20
    
    # S3/CDN settings
    s3_bucket: str = ""
    s3_region: str = "us-east-1"
    s3_key_prefix: str = "cache/"
    cdn_url: str = ""
    
    # Compression settings
    compression_threshold: int = 1024  # bytes
    default_compression: CompressionType = CompressionType.GZIP
    
    # Performance settings
    batch_size: int = 100
    timeout_seconds: int = 30
    retry_attempts: int = 3

@dataclass
class StorageMetrics:
    """Storage performance metrics"""
    total_reads: int = 0
    total_writes: int = 0
    cache_hits_by_level: Dict[StorageLevel, int] = field(default_factory=dict)
    average_read_time_by_level: Dict[StorageLevel, float] = field(default_factory=dict)
    storage_size_by_level: Dict[StorageLevel, int] = field(default_factory=dict)
    compression_ratio: float = 0.0
    error_count: int = 0

class CacheStorage(ABC):
    """
Abstract base class for cache storage implementations"""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.metrics = StorageMetrics()
        
    @abstractmethod
    async def initialize(self) -> bool:
        try:
            logger.info(f"Executing initialize")
            
            # Implementation for initialize
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"initialize completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing set")
            
            # Implementation for set
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"set completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing exists")
            
            # Implementation for exists
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"exists completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing clear")
            
            # Implementation for clear
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"clear completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing close")
            
            # Implementation for close
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"close completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"close failed: {e}")
            raise
            return result
            
        except Exception as e:
            logger.error(f"clear failed: {e}")
            raise
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle_get_size_request(data)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler get_size failed: {e}")
                    return {"status": "error", "message": str(e)}
            return result
            
        except Exception as e:
            logger.error(f"exists failed: {e}")
            raise
                        await session.commit()
                        logger.info(f"Database operation delete completed")
                        return True
                
                except Exception as e:
                    logger.error(f"Database operation delete failed: {e}")
                    raise
            return result
            
        except Exception as e:
            logger.error(f"set failed: {e}")
            raise
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle_get_request(key)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler get failed: {e}")
                    return {"status": "error", "message": str(e)}
            return result
            
        except Exception as e:
            logger.error(f"initialize failed: {e}")
            raise
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """
Retrieve value by key"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
Store value with optional TTL"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
Delete value by key"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
Check if key exists"""
        pass
    
    @abstractmethod
    async def get_size(self) -> int:
        """
Get total storage size in bytes"""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """
Clear all stored data"""
        pass
    
    @abstractmethod
    async def close(self):
        """
Close storage connections"""
        pass

class MemoryStorage(CacheStorage):
    """
High-performance in-memory storage with intelligent eviction"""
    
    def __init__(self, config: StorageConfig):
        super().__init__(config)
        self._storage: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, datetime] = {}
        self._sizes: Dict[str, int] = {}
        self._current_size = 0
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> bool:
        """
Initialize memory storage"""
        logger.info("MemoryStorage initialized")
        return True
    
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve value from memory with access time tracking"""
        start_time = time.time()
        
        async with self._lock:
            if key not in self._storage:
                return None
            
            entry = self._storage[key]
            
            # Check TTL expiration
            if entry.get('expires_at') and datetime.utcnow() > entry['expires_at']:
                await self._remove_entry(key)
                return None
            
            # Update access time
            self._access_times[key] = datetime.utcnow()
            
            # Update metrics
            self.metrics.total_reads += 1
            self.metrics.cache_hits_by_level[StorageLevel.L1_MEMORY] = (
                self.metrics.cache_hits_by_level.get(StorageLevel.L1_MEMORY, 0) + 1
            )
            
            read_time = time.time() - start_time
            self._update_average_read_time(StorageLevel.L1_MEMORY, read_time)
            
            return entry['value']
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
Store value in memory with automatic compression and eviction"""
        try:
            serialized = pickle.dumps(value)
            size_bytes = len(serialized)
            
            # Apply compression if beneficial
            compressed_data = serialized
            if size_bytes > self.config.compression_threshold:
                compressed_data = await self._compress_data(serialized)
                compression_ratio = len(compressed_data) / size_bytes
                self.metrics.compression_ratio = (
                    self.metrics.compression_ratio * 0.9 + compression_ratio * 0.1
                )
            
            async with self._lock:
                # Check if we need to make space
                if self._current_size + len(compressed_data) > self.config.max_memory_size:
                    await self._evict_space(len(compressed_data))
                
                # Store entry
                entry = {
                    'value': value,
                    'data': compressed_data,
                    'created_at': datetime.utcnow(),
                    'size_bytes': len(compressed_data)
                }
                
                if ttl:
                    entry['expires_at'] = datetime.utcnow() + timedelta(seconds=ttl)
                
                # Update storage
                old_size = self._sizes.get(key, 0)
                self._storage[key] = entry
                self._sizes[key] = len(compressed_data)
                self._access_times[key] = datetime.utcnow()
                
                # Update current size
                self._current_size = self._current_size - old_size + len(compressed_data)
                
                # Update metrics
                self.metrics.total_writes += 1
                self.metrics.storage_size_by_level[StorageLevel.L1_MEMORY] = self._current_size
                
                return True
                
        except Exception as e:
            logger.error(f"MemoryStorage set error for key {key}: {e}")
            self.metrics.error_count += 1
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete entry from memory"""
        async with self._lock:
            if key in self._storage:
                await self._remove_entry(key)
                return True
            return False
    
    async def exists(self, key: str) -> bool:
        """
Check if key exists in memory"""
        async with self._lock:
            if key not in self._storage:
                return False
            
            entry = self._storage[key]
            # Check TTL expiration
            if entry.get('expires_at') and datetime.utcnow() > entry['expires_at']:
                await self._remove_entry(key)
                return False
            
            return True
    
    async def get_size(self) -> int:
        """
Get current memory usage"""
        return self._current_size
    
    async def clear(self) -> bool:
        """
Clear all memory storage"""
        async with self._lock:
            self._storage.clear()
            self._access_times.clear()
            self._sizes.clear()
            self._current_size = 0
            return True
    
    async def close(self):
        """
Close memory storage (cleanup)"""
        await self.clear()
        logger.info("MemoryStorage closed")
    
    # Private helper methods
    
    async def _remove_entry(self, key: str):
        """Remove entry and update size tracking"""
        if key in self._storage:
            self._current_size -= self._sizes.get(key, 0)
            del self._storage[key]
            self._sizes.pop(key, None)
            self._access_times.pop(key, None)
    
    async def _evict_space(self, required_space: int):
        """
Evict entries to make space using LRU policy"""
        # Sort by access time (oldest first)
        sorted_keys = sorted(
            self._access_times.items(),
            key=lambda x: x[1]
        )
        
        freed_space = 0
        for key, _ in sorted_keys:
            if freed_space >= required_space:
                break
                
            freed_space += self._sizes.get(key, 0)
            await self._remove_entry(key)
    
    async def _compress_data(self, data: bytes) -> bytes:
        """
Compress data based on configuration"""
        if self.config.default_compression == CompressionType.GZIP:
            return gzip.compress(data)
        elif self.config.default_compression == CompressionType.LZ4:
            try:
                import lz4.frame
                return lz4.frame.compress(data)
            except ImportError:
                logger.warning("LZ4 not available, falling back to gzip")
                return gzip.compress(data)
        else:
            return data
    
    def _update_average_read_time(self, level: StorageLevel, read_time: float):
        """Update average read time for level"""
        current_avg = self.metrics.average_read_time_by_level.get(level, 0.0)
        # Exponential moving average
        self.metrics.average_read_time_by_level[level] = current_avg * 0.9 + read_time * 0.1

class RedisStorage(CacheStorage):
    """
Redis-based distributed cache storage with advanced features"""
    
    def __init__(self, config: StorageConfig):
        super().__init__(config)
        self._redis: Optional[aioredis.Redis] = None
        self._connection_pool: Optional[aioredis.ConnectionPool] = None
    
    async def initialize(self) -> bool:
        """
Initialize Redis connection with retry logic"""
        try:
            self._connection_pool = aioredis.ConnectionPool.from_url(
                self.config.redis_url,
                max_connections=self.config.redis_max_connections,
                db=self.config.redis_db,
                decode_responses=False  # We handle binary data
            )
            
            self._redis = aioredis.Redis(connection_pool=self._connection_pool)
            
            # Test connection
            await self._redis.ping()
            
            logger.info("RedisStorage initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize RedisStorage: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve value from Redis with decompression"""
        if not self._redis:
            return None
        
        start_time = time.time()
        
        try:
            redis_key = f"{self.config.redis_key_prefix}{key}"
            data = await self._redis.get(redis_key)
            
            if data is None:
                return None
            
            # Decompress and deserialize
            decompressed = await self._decompress_data(data)
            value = pickle.loads(decompressed)
            
            # Update metrics
            self.metrics.total_reads += 1
            self.metrics.cache_hits_by_level[StorageLevel.L2_REDIS] = (
                self.metrics.cache_hits_by_level.get(StorageLevel.L2_REDIS, 0) + 1
            )
            
            read_time = time.time() - start_time
            self._update_average_read_time(StorageLevel.L2_REDIS, read_time)
            
            return value
            
        except Exception as e:
            logger.error(f"RedisStorage get error for key {key}: {e}")
            self.metrics.error_count += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store value in Redis with compression and TTL"""
        if not self._redis:
            return False
        
        try:
            # Serialize and compress
            serialized = pickle.dumps(value)
            compressed = await self._compress_data(serialized)
            
            redis_key = f"{self.config.redis_key_prefix}{key}"
            
            # Set with optional TTL
            if ttl:
                success = await self._redis.setex(redis_key, ttl, compressed)
            else:
                success = await self._redis.set(redis_key, compressed)
            
            if success:
                self.metrics.total_writes += 1
                # Update storage size estimate
                current_size = self.metrics.storage_size_by_level.get(StorageLevel.L2_REDIS, 0)
                self.metrics.storage_size_by_level[StorageLevel.L2_REDIS] = current_size + len(compressed)
            
            return bool(success)
            
        except Exception as e:
            logger.error(f"RedisStorage set error for key {key}: {e}")
            self.metrics.error_count += 1
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from Redis"""
        if not self._redis:
            return False
        
        try:
            redis_key = f"{self.config.redis_key_prefix}{key}"
            result = await self._redis.delete(redis_key)
            return result > 0
            
        except Exception as e:
            logger.error(f"RedisStorage delete error for key {key}: {e}")
            self.metrics.error_count += 1
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        if not self._redis:
            return False
        
        try:
            redis_key = f"{self.config.redis_key_prefix}{key}"
            result = await self._redis.exists(redis_key)
            return result > 0
            
        except Exception as e:
            logger.error(f"RedisStorage exists error for key {key}: {e}")
            return False
    
    async def get_size(self) -> int:
        """Get approximate Redis memory usage"""
        if not self._redis:
            return 0
        
        try:
            info = await self._redis.info('memory')
            return info.get('used_memory', 0)
            
        except Exception as e:
            logger.error(f"RedisStorage get_size error: {e}")
            return 0
    
    async def clear(self) -> bool:
        """Clear all Redis keys with prefix"""
        if not self._redis:
            return False
        
        try:
            pattern = f"{self.config.redis_key_prefix}*"
            keys = await self._redis.keys(pattern)
            
            if keys:
                await self._redis.delete(*keys)
            
            return True
            
        except Exception as e:
            logger.error(f"RedisStorage clear error: {e}")
            return False
    
    async def close(self):
        """Close Redis connections"""
        if self._redis:
            await self._redis.close()
        if self._connection_pool:
            await self._connection_pool.disconnect()
        
        logger.info("RedisStorage closed")
    
    # Helper methods
    
    async def _compress_data(self, data: bytes) -> bytes:
        """Compress data for Redis storage"""
        if len(data) > self.config.compression_threshold:
            if self.config.default_compression == CompressionType.GZIP:
                return gzip.compress(data)
        return data
    
    async def _decompress_data(self, data: bytes) -> bytes:
        """
Decompress data from Redis"""
        # Try to detect if data is compressed
        if data.startswith(b'\x1f\x8b'):  # Gzip magic number
            return gzip.decompress(data)
        return data
    
    def _update_average_read_time(self, level: StorageLevel, read_time: float):
        """
Update average read time metrics"""
        current_avg = self.metrics.average_read_time_by_level.get(level, 0.0)
        self.metrics.average_read_time_by_level[level] = current_avg * 0.9 + read_time * 0.1

class DatabaseStorage(CacheStorage):
    """
Database-backed persistent cache storage"""
    
    def __init__(self, config: StorageConfig):
        super().__init__(config)
        self._engine = None
        self._session_factory = None
    
    async def initialize(self) -> bool:
        """
Initialize database connection and create table if needed"""
        try:
            self._engine = create_engine(
                self.config.database_url,
                pool_size=self.config.database_pool_size,
                echo=False
            )
            
            self._session_factory = sessionmaker(bind=self._engine)
            
            # Create cache table if it doesn't exist
            await self._create_cache_table()
            
            logger.info("DatabaseStorage initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize DatabaseStorage: {e}")
            return False
    
    async def _create_cache_table(self):
        """Create cache storage table"""
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.config.database_table} (
            key VARCHAR(255) PRIMARY KEY,
            value BYTEA NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            size_bytes INTEGER DEFAULT 0,
            access_count INTEGER DEFAULT 0,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        with self._engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.commit()
    
    async def get(self, key: str) -> Optional[Any]:
        """
Retrieve value from database"""
        start_time = time.time()
        
        try:
            with self._session_factory() as session:
                # Check for expired entries
                current_time = datetime.utcnow()
                
                result = session.execute(
                    text(f"""
                    SELECT value FROM {self.config.database_table}
                    WHERE key = :key 
                    AND (expires_at IS NULL OR expires_at > :current_time)
                    """),
                    {"key": key, "current_time": current_time}
                ).fetchone()
                
                if result is None:
                    return None
                
                # Update access tracking
                session.execute(
                    text(f"""
                    UPDATE {self.config.database_table}
                    SET access_count = access_count + 1, 
                        last_accessed = :current_time
                    WHERE key = :key
                    """),
                    {"key": key, "current_time": current_time}
                )
                session.commit()
                
                # Deserialize value
                value = pickle.loads(result[0])
                
                # Update metrics
                self.metrics.total_reads += 1
                self.metrics.cache_hits_by_level[StorageLevel.L3_DATABASE] = (
                    self.metrics.cache_hits_by_level.get(StorageLevel.L3_DATABASE, 0) + 1
                )
                
                read_time = time.time() - start_time
                self._update_average_read_time(StorageLevel.L3_DATABASE, read_time)
                
                return value
                
        except Exception as e:
            logger.error(f"DatabaseStorage get error for key {key}: {e}")
            self.metrics.error_count += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store value in database"""
        try:
            serialized = pickle.dumps(value)
            size_bytes = len(serialized)
            
            expires_at = None
            if ttl:
                expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            
            with self._session_factory() as session:
                # Use UPSERT (INSERT ... ON CONFLICT)
                session.execute(
                    text(f"""
                    INSERT INTO {self.config.database_table} 
                    (key, value, created_at, expires_at, size_bytes, access_count, last_accessed)
                    VALUES (:key, :value, :created_at, :expires_at, :size_bytes, 1, :last_accessed)
                    ON CONFLICT (key) DO UPDATE SET
                        value = :value,
                        expires_at = :expires_at,
                        size_bytes = :size_bytes,
                        access_count = {self.config.database_table}.access_count + 1,
                        last_accessed = :last_accessed
                    """),
                    {
                        "key": key,
                        "value": serialized,
                        "created_at": datetime.utcnow(),
                        "expires_at": expires_at,
                        "size_bytes": size_bytes,
                        "last_accessed": datetime.utcnow()
                    }
                )
                session.commit()
                
                self.metrics.total_writes += 1
                return True
                
        except Exception as e:
            logger.error(f"DatabaseStorage set error for key {key}: {e}")
            self.metrics.error_count += 1
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from database"""
        try:
            with self._session_factory() as session:
                result = session.execute(
                    text(f"DELETE FROM {self.config.database_table} WHERE key = :key"),
                    {"key": key}
                )
                session.commit()
                return result.rowcount > 0
                
        except Exception as e:
            logger.error(f"DatabaseStorage delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in database"""
        try:
            with self._session_factory() as session:
                result = session.execute(
                    text(f"""
                    SELECT 1 FROM {self.config.database_table} 
                    WHERE key = :key 
                    AND (expires_at IS NULL OR expires_at > :current_time)
                    """),
                    {"key": key, "current_time": datetime.utcnow()}
                ).fetchone()
                
                return result is not None
                
        except Exception as e:
            logger.error(f"DatabaseStorage exists error for key {key}: {e}")
            return False
    
    async def get_size(self) -> int:
        """Get total database storage size"""
        try:
            with self._session_factory() as session:
                result = session.execute(
                    text(f"SELECT COALESCE(SUM(size_bytes), 0) FROM {self.config.database_table}")
                ).fetchone()
                
                return result[0] if result else 0
                
        except Exception as e:
            logger.error(f"DatabaseStorage get_size error: {e}")
            return 0
    
    async def clear(self) -> bool:
        """Clear all database cache entries"""
        try:
            with self._session_factory() as session:
                session.execute(text(f"DELETE FROM {self.config.database_table}"))
                session.commit()
                return True
                
        except Exception as e:
            logger.error(f"DatabaseStorage clear error: {e}")
            return False
    
    async def close(self):
        """Close database connections"""
        if self._engine:
            self._engine.dispose()
        logger.info("DatabaseStorage closed")
    
    def _update_average_read_time(self, level: StorageLevel, read_time: float):
        """Update average read time metrics"""
        current_avg = self.metrics.average_read_time_by_level.get(level, 0.0)
        self.metrics.average_read_time_by_level[level] = current_avg * 0.9 + read_time * 0.1

class HybridStorage(CacheStorage):
    """
Multi-layer hybrid storage orchestrating all cache levels"""
    
    def __init__(self, config: StorageConfig):
        super().__init__(config)
        self.storage_layers: Dict[StorageLevel, CacheStorage] = {}
        self._initialized = False
    
    async def initialize(self) -> bool:
        """
Initialize all storage layers"""
        try:
            # Initialize Memory (L1)
            self.storage_layers[StorageLevel.L1_MEMORY] = MemoryStorage(self.config)
            await self.storage_layers[StorageLevel.L1_MEMORY].initialize()
            
            # Initialize Redis (L2) 
            if self.config.redis_url:
                self.storage_layers[StorageLevel.L2_REDIS] = RedisStorage(self.config)
                await self.storage_layers[StorageLevel.L2_REDIS].initialize()
            
            # Initialize Database (L3)
            if self.config.database_url:
                self.storage_layers[StorageLevel.L3_DATABASE] = DatabaseStorage(self.config)
                await self.storage_layers[StorageLevel.L3_DATABASE].initialize()
            
            self._initialized = True
            logger.info("HybridStorage initialized with all available layers")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize HybridStorage: {e}")
            return False
    
    async def get_from_level(self, level: StorageLevel, key: str) -> Optional[Any]:
        """Get value from specific storage level"""
        if level not in self.storage_layers:
            return None
        
        return await self.storage_layers[level].get(key)
    
    async def set_in_level(self, level: StorageLevel, key: str, entry: Any) -> bool:
        """
Set value in specific storage level"""
        if level not in self.storage_layers:
            return False
        
        return await self.storage_layers[level].set(key, entry.value, entry.ttl)
    
    async def get(self, key: str) -> Optional[Any]:
        """
Get value from storage hierarchy (L1->L2->L3->L4)"""
        # Try each level in order
        for level in [StorageLevel.L1_MEMORY, StorageLevel.L2_REDIS, 
                     StorageLevel.L3_DATABASE, StorageLevel.L4_S3_CDN]:
            
            if level in self.storage_layers:
                value = await self.storage_layers[level].get(key)
                if value is not None:
                    # Promote to higher levels for faster future access
                    await self._promote_to_higher_levels(key, value, level)
                    return value
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
Set value across appropriate storage levels"""
        success = False
        
        # Store in all available levels (write-through strategy)
        for level in self.storage_layers:
            try:
                if await self.storage_layers[level].set(key, value, ttl):
                    success = True
            except Exception as e:
                logger.error(f"Failed to set in level {level}: {e}")
        
        return success
    
    async def delete(self, key: str) -> bool:
        """Delete from all storage levels"""
        success = False
        
        for level in self.storage_layers:
            try:
                if await self.storage_layers[level].delete(key):
                    success = True
            except Exception as e:
                logger.error(f"Failed to delete from level {level}: {e}")
        
        return success
    
    async def exists(self, key: str) -> bool:
        """Check existence across all levels"""
        for level in self.storage_layers:
            if await self.storage_layers[level].exists(key):
                return True
        return False
    
    async def get_size(self) -> int:
        """
Get total size across all levels"""
        total_size = 0
        for level in self.storage_layers:
            total_size += await self.storage_layers[level].get_size()
        return total_size
    
    async def clear(self) -> bool:
        """
Clear all storage levels"""
        success = True
        for level in self.storage_layers:
            if not await self.storage_layers[level].clear():
                success = False
        return success
    
    async def close(self):
        """
Close all storage layers"""
        for level in self.storage_layers:
            await self.storage_layers[level].close()
        logger.info("HybridStorage closed")
    
    async def _promote_to_higher_levels(
        self, 
        key: str, 
        value: Any, 
        current_level: StorageLevel
    ):
        """Promote cache entry to higher performance levels"""
        # Promote from L3/L4 -> L2 -> L1
        if current_level.value > StorageLevel.L2_REDIS.value:
            if StorageLevel.L2_REDIS in self.storage_layers:
                await self.storage_layers[StorageLevel.L2_REDIS].set(key, value)
        
        if current_level.value > StorageLevel.L1_MEMORY.value:
            if StorageLevel.L1_MEMORY in self.storage_layers:
                await self.storage_layers[StorageLevel.L1_MEMORY].set(key, value)
