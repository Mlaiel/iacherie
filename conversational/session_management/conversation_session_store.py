"""Conversation Session Store - IA Influencer Agent

Enterprise-grade conversation session storage with distributed caching,
data persistence, and high-performance session state management for
multi-format content creators across platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
Unauthorized use prohibited. Contact: mlaiel@live.de
"""

import asyncio
import json
import pickle
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from enum import Enum
from dataclasses import dataclass, field
from uuid import uuid4

from pydantic import BaseModel, Field, validator
import redis.asyncio as redis
from sqlalchemy import select, update, insert, delete, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import JSONB
import asyncpg

from ...core.database import get_async_session, get_connection_pool
from ...core.cache import CacheManager, RedisManager
from ...core.logging import get_logger
from ...core.config import settings
from ...models.session import SessionModel, ConversationModel, SessionState
from ...models.user import UserModel
from ...security.encryption import EncryptionManager
from ...utils.metrics import MetricsCollector
from ...utils.serialization import SerializationManager
from ...utils.compression import CompressionManager

logger = get_logger(__name__)


class StorageBackend(Enum):
    """
Storage backend types"""

    REDIS = "redis"
    POSTGRESQL = "postgresql"
    MEMORY = "memory"
    DISTRIBUTED = "distributed"


class CompressionType(Enum):
    """Compression algorithms"""

    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    ZSTD = "zstd"


@dataclass
class SessionStoreConfig:
    """Session store configuration"""
    primary_backend: StorageBackend = StorageBackend.REDIS
    secondary_backend: Optional[StorageBackend] = StorageBackend.POSTGRESQL
    cache_ttl: int = 3600  # seconds
    compression: CompressionType = CompressionType.LZ4
    encryption_enabled: bool = True
    auto_backup: bool = True
    backup_interval: int = 300  # seconds
    max_memory_sessions: int = 1000
    cleanup_interval: int = 900  # seconds
    replication_factor: int = 2


class SessionData(BaseModel):
    """
Session data structure"""
    session_id: str
    user_id: str
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    context_stack: List[Dict[str, Any]] = Field(default_factory=list)
    entity_repository: Dict[str, Any] = Field(default_factory=dict)
    intent_history: List[str] = Field(default_factory=list)
    collaboration_workspace: Dict[str, Any] = Field(default_factory=dict)
    content_protection_logs: List[Dict[str, Any]] = Field(default_factory=list)
    monetization_tracking: Dict[str, Any] = Field(default_factory=dict)
    personalization_profile: Dict[str, Any] = Field(default_factory=dict)
    platform_states: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    access_count: int = 0
    data_size: int = 0
    checksum: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SessionCacheManager:
    """
Advanced session caching with intelligent eviction"""
    
    def __init__(self, config: SessionStoreConfig):
        self.config = config
        self.redis_manager = RedisManager()
        self.compression_manager = CompressionManager()
        self.encryption_manager = EncryptionManager()
        self.metrics_collector = MetricsCollector()
        self.logger = get_logger(self.__class__.__name__)
        
        # Cache statistics
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "size": 0
        }
    
    async def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get session from cache with intelligent loading"""
        
        try:
            # Try primary cache first
            cache_key = f"session_data:{session_id}"
            cached_data = await self.redis_manager.get(cache_key)
            
            if cached_data:
                # Decompress and decrypt if needed
                session_data = await self._deserialize_session_data(cached_data)
                
                # Update access statistics
                session_data.last_accessed = datetime.utcnow()
                session_data.access_count += 1
                
                # Update cache with new access info
                await self._store_session_in_cache(session_id, session_data)
                
                self.cache_stats["hits"] += 1
                await self.metrics_collector.increment("session_cache.hits")
                
                return session_data
            
            self.cache_stats["misses"] += 1
            await self.metrics_collector.increment("session_cache.misses")
            return None
            
        except Exception as e:
            self.logger.error(f"Cache get error: {str(e)}")
            await self.metrics_collector.increment("session_cache.errors")
            return None
    
    async def store_session(self, session_data: SessionData) -> bool:
        """Store session in cache with optimization"""
        
        try:
            # Update metadata
            session_data.updated_at = datetime.utcnow()
            session_data.data_size = await self._calculate_data_size(session_data)
            session_data.checksum = await self._calculate_checksum(session_data)
            
            # Store in cache
            success = await self._store_session_in_cache(session_data.session_id, session_data)
            
            if success:
                await self.metrics_collector.increment("session_cache.stores")
                self.cache_stats["size"] = await self._get_cache_size()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Cache store error: {str(e)}")
            await self.metrics_collector.increment("session_cache.store_errors")
            return False
    
    async def _store_session_in_cache(self, session_id: str, session_data: SessionData) -> bool:
        """Internal method to store session in cache"""
        
        try:
            # Serialize, compress, and encrypt
            serialized_data = await self._serialize_session_data(session_data)
            
            # Store with TTL
            cache_key = f"session_data:{session_id}"
            await self.redis_manager.set(
                cache_key,
                serialized_data,
                ttl=self.config.cache_ttl
            )
            
            # Store in secondary indexes for efficient lookup
            await self._update_cache_indexes(session_id, session_data)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Cache storage failed: {str(e)}")
            return False
    
    async def _serialize_session_data(self, session_data: SessionData) -> bytes:
        """Serialize session data with compression and encryption"""
        
        # Convert to dict
        data_dict = session_data.dict()
        
        # Serialize to JSON
        json_data = json.dumps(data_dict, default=str).encode('utf-8')
        
        # Compress if enabled
        if self.config.compression != CompressionType.NONE:
            json_data = await self.compression_manager.compress(
                json_data,
                algorithm=self.config.compression.value
            )
        
        # Encrypt if enabled
        if self.config.encryption_enabled:
            json_data = await self.encryption_manager.encrypt_data(json_data)
        
        return json_data
    
    async def _deserialize_session_data(self, serialized_data: bytes) -> SessionData:
        """
Deserialize session data with decompression and decryption"""
        
        # Decrypt if enabled
        if self.config.encryption_enabled:
            serialized_data = await self.encryption_manager.decrypt_data(serialized_data)
        
        # Decompress if needed
        if self.config.compression != CompressionType.NONE:
            serialized_data = await self.compression_manager.decompress(
                serialized_data,
                algorithm=self.config.compression.value
            )
        
        # Deserialize from JSON
        data_dict = json.loads(serialized_data.decode('utf-8'))
        
        # Convert datetime strings back to datetime objects
        for field in ['created_at', 'updated_at', 'last_accessed']:
            if field in data_dict and isinstance(data_dict[field], str):
                data_dict[field] = datetime.fromisoformat(data_dict[field])
        
        return SessionData(**data_dict)
    
    async def _calculate_data_size(self, session_data: SessionData) -> int:
        """
Calculate session data size in bytes"""
        
        try:
            serialized_data = await self._serialize_session_data(session_data)
            return len(serialized_data)
        except Exception:
            return 0
    
    async def _calculate_checksum(self, session_data: SessionData) -> str:
        """
Calculate session data checksum for integrity verification"""
        
        import hashlib
        
        try:
            # Create reproducible string representation
            data_str = json.dumps(session_data.dict(), sort_keys=True, default=str)
            return hashlib.sha256(data_str.encode()).hexdigest()[:16]
        except Exception:
            return ""
    
    async def _update_cache_indexes(self, session_id: str, session_data: SessionData):
        """Update cache indexes for efficient lookups"""
        
        try:
            # User sessions index
            user_sessions_key = f"user_sessions:{session_data.user_id}"
            await self.redis_manager.set_add(user_sessions_key, session_id)
            await self.redis_manager.expire(user_sessions_key, self.config.cache_ttl)
            
            # Active sessions index
            active_sessions_key = "active_sessions"
            await self.redis_manager.set_add(active_sessions_key, session_id)
            
            # Session metadata index
            metadata_key = f"session_metadata:{session_id}"
            metadata = {
                "user_id": session_data.user_id,
                "created_at": session_data.created_at.isoformat(),
                "last_accessed": session_data.last_accessed.isoformat(),
                "access_count": session_data.access_count,
                "data_size": session_data.data_size
            }
            await self.redis_manager.set(metadata_key, json.dumps(metadata), ttl=self.config.cache_ttl)
            
        except Exception as e:
            self.logger.error(f"Index update failed: {str(e)}")
    
    async def _get_cache_size(self) -> int:
        """Get current cache size"""
        
        try:
            active_sessions = await self.redis_manager.set_members("active_sessions")
            return len(active_sessions) if active_sessions else 0
        except Exception:
            return 0
    
    async def evict_session(self, session_id: str) -> bool:
        """Evict session from cache"""
        
        try:
            # Remove session data
            cache_key = f"session_data:{session_id}"
            await self.redis_manager.delete(cache_key)
            
            # Remove from indexes
            await self._remove_from_indexes(session_id)
            
            self.cache_stats["evictions"] += 1
            await self.metrics_collector.increment("session_cache.evictions")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Cache eviction failed: {str(e)}")
            return False
    
    async def _remove_from_indexes(self, session_id: str):
        """Remove session from cache indexes"""
        
        try:
            # Get session metadata to find user_id
            metadata_key = f"session_metadata:{session_id}"
            metadata_json = await self.redis_manager.get(metadata_key)
            
            if metadata_json:
                metadata = json.loads(metadata_json)
                user_id = metadata.get("user_id")
                
                if user_id:
                    user_sessions_key = f"user_sessions:{user_id}"
                    await self.redis_manager.set_remove(user_sessions_key, session_id)
            
            # Remove from active sessions
            await self.redis_manager.set_remove("active_sessions", session_id)
            
            # Remove metadata
            await self.redis_manager.delete(metadata_key)
            
        except Exception as e:
            self.logger.error(f"Index removal failed: {str(e)}")
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        
        try:
            active_sessions_count = await self._get_cache_size()
            memory_usage = await self.redis_manager.get_memory_usage()
            
            return {
                "hits": self.cache_stats["hits"],
                "misses": self.cache_stats["misses"],
                "hit_ratio": self.cache_stats["hits"] / (self.cache_stats["hits"] + self.cache_stats["misses"]) if (self.cache_stats["hits"] + self.cache_stats["misses"]) > 0 else 0,
                "evictions": self.cache_stats["evictions"],
                "active_sessions": active_sessions_count,
                "memory_usage_mb": memory_usage / (1024 * 1024) if memory_usage else 0,
                "max_sessions": self.config.max_memory_sessions
            }
            
        except Exception as e:
            self.logger.error(f"Stats calculation failed: {str(e)}")
            return {}


class SessionDataPersistence:
    """Persistent storage for session data"""
    
    def __init__(self, config: SessionStoreConfig):
        self.config = config
        self.metrics_collector = MetricsCollector()
        self.logger = get_logger(self.__class__.__name__)
    
    async def save_session(self, session_data: SessionData) -> bool:
        """
Save session to persistent storage"""
        
        try:
            async with get_async_session() as session:
                # Check if session exists
                query = select(SessionModel).where(SessionModel.session_id == session_data.session_id)
                result = await session.execute(query)
                existing_session = result.scalar_one_or_none()
                
                if existing_session:
                    # Update existing session
                    await session.execute(
                        update(SessionModel)
                        .where(SessionModel.session_id == session_data.session_id)
                        .values(
                            conversation_data=session_data.conversation_history,
                            context_data=session_data.context_stack,
                            entity_data=session_data.entity_repository,
                            collaboration_data=session_data.collaboration_workspace,
                            platform_data=session_data.platform_states,
                            updated_at=session_data.updated_at,
                            last_accessed=session_data.last_accessed,
                            access_count=session_data.access_count,
                            data_size=session_data.data_size,
                            checksum=session_data.checksum
                        )
                    )
                else:
                    # Create new session record
                    new_session = SessionModel(
                        session_id=session_data.session_id,
                        user_id=session_data.user_id,
                        conversation_data=session_data.conversation_history,
                        context_data=session_data.context_stack,
                        entity_data=session_data.entity_repository,
                        collaboration_data=session_data.collaboration_workspace,
                        platform_data=session_data.platform_states,
                        created_at=session_data.created_at,
                        updated_at=session_data.updated_at,
                        last_accessed=session_data.last_accessed,
                        access_count=session_data.access_count,
                        data_size=session_data.data_size,
                        checksum=session_data.checksum
                    )
                    session.add(new_session)
                
                await session.commit()
                
                await self.metrics_collector.increment("session_persistence.saves")
                return True
                
        except Exception as e:
            self.logger.error(f"Session save failed: {str(e)}")
            await self.metrics_collector.increment("session_persistence.save_errors")
            return False
    
    async def load_session(self, session_id: str) -> Optional[SessionData]:
        """Load session from persistent storage"""
        
        try:
            async with get_async_session() as session:
                query = select(SessionModel).where(SessionModel.session_id == session_id)
                result = await session.execute(query)
                db_session = result.scalar_one_or_none()
                
                if not db_session:
                    return None
                
                session_data = SessionData(
                    session_id=db_session.session_id,
                    user_id=db_session.user_id,
                    conversation_history=db_session.conversation_data or [],
                    context_stack=db_session.context_data or [],
                    entity_repository=db_session.entity_data or {},
                    collaboration_workspace=db_session.collaboration_data or {},
                    platform_states=db_session.platform_data or {},
                    created_at=db_session.created_at,
                    updated_at=db_session.updated_at,
                    last_accessed=db_session.last_accessed or datetime.utcnow(),
                    access_count=db_session.access_count or 0,
                    data_size=db_session.data_size or 0,
                    checksum=db_session.checksum
                )
                
                await self.metrics_collector.increment("session_persistence.loads")
                return session_data
                
        except Exception as e:
            self.logger.error(f"Session load failed: {str(e)}")
            await self.metrics_collector.increment("session_persistence.load_errors")
            return None
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session from persistent storage"""
        
        try:
            async with get_async_session() as session:
                await session.execute(
                    delete(SessionModel).where(SessionModel.session_id == session_id)
                )
                await session.commit()
                
                await self.metrics_collector.increment("session_persistence.deletes")
                return True
                
        except Exception as e:
            self.logger.error(f"Session delete failed: {str(e)}")
            await self.metrics_collector.increment("session_persistence.delete_errors")
            return False
    
    async def get_user_sessions(self, user_id: str) -> List[SessionData]:
        """Get all sessions for a user"""
        
        try:
            async with get_async_session() as session:
                query = select(SessionModel).where(SessionModel.user_id == user_id)
                result = await session.execute(query)
                db_sessions = result.scalars().all()
                
                sessions = []
                for db_session in db_sessions:
                    session_data = SessionData(
                        session_id=db_session.session_id,
                        user_id=db_session.user_id,
                        conversation_history=db_session.conversation_data or [],
                        context_stack=db_session.context_data or [],
                        entity_repository=db_session.entity_data or {},
                        collaboration_workspace=db_session.collaboration_data or {},
                        platform_states=db_session.platform_data or {},
                        created_at=db_session.created_at,
                        updated_at=db_session.updated_at,
                        last_accessed=db_session.last_accessed or datetime.utcnow(),
                        access_count=db_session.access_count or 0,
                        data_size=db_session.data_size or 0,
                        checksum=db_session.checksum
                    )
                    sessions.append(session_data)
                
                return sessions
                
        except Exception as e:
            self.logger.error(f"User sessions load failed: {str(e)}")
            return []
    
    async def cleanup_old_sessions(self, max_age_days: int = 30) -> int:
        """Clean up old sessions from persistent storage"""
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
            
            async with get_async_session() as session:
                # Delete old sessions
                result = await session.execute(
                    delete(SessionModel)
                    .where(SessionModel.last_accessed < cutoff_date)
                    .returning(SessionModel.session_id)
                )
                deleted_sessions = result.fetchall()
                
                await session.commit()
                
                deleted_count = len(deleted_sessions)
                await self.metrics_collector.increment(
                    "session_persistence.cleanup",
                    value=deleted_count
                )
                
                self.logger.info(f"Cleaned up {deleted_count} old sessions")
                return deleted_count
                
        except Exception as e:
            self.logger.error(f"Session cleanup failed: {str(e)}")
            return 0


class DistributedSessionStorage:
    """Distributed session storage with replication and consistency"""
    
    def __init__(self, config: SessionStoreConfig):
        self.config = config
        self.cache_manager = SessionCacheManager(config)
        self.persistence = SessionDataPersistence(config)
        self.metrics_collector = MetricsCollector()
        self.logger = get_logger(self.__class__.__name__)
        
        # Background tasks
        self.backup_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
    
    async def start_background_tasks(self):
        """
Start background maintenance tasks"""
        
        if self.config.auto_backup:
            self.backup_task = asyncio.create_task(self._backup_loop())
        
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        self.logger.info("Background tasks started")
    
    async def stop_background_tasks(self):
        try:
            logger.info(f"Executing stop_background_tasks")
            
            # Implementation for stop_background_tasks
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"stop_background_tasks completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"stop_background_tasks failed: {e}")
            raise
    async def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get session with cache and persistence fallback"""
        
        # Try cache first
        session_data = await self.cache_manager.get_session(session_id)
        
        if session_data:
            return session_data
        
        # Fallback to persistence
        session_data = await self.persistence.load_session(session_id)
        
        if session_data:
            # Store in cache for future access
            await self.cache_manager.store_session(session_data)
        
        return session_data
    
    async def store_session(self, session_data: SessionData) -> bool:
        """
Store session in both cache and persistence"""
        
        try:
            # Store in cache first (fast)
            cache_success = await self.cache_manager.store_session(session_data)
            
            # Store in persistence (durable)
            persistence_success = await self.persistence.save_session(session_data)
            
            # Consider success if either succeeds (resilience)
            success = cache_success or persistence_success
            
            if success:
                await self.metrics_collector.increment("distributed_storage.stores")
            else:
                await self.metrics_collector.increment("distributed_storage.store_failures")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Distributed store failed: {str(e)}")
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session from both cache and persistence"""
        
        try:
            # Remove from cache
            cache_success = await self.cache_manager.evict_session(session_id)
            
            # Remove from persistence
            persistence_success = await self.persistence.delete_session(session_id)
            
            success = cache_success and persistence_success
            
            if success:
                await self.metrics_collector.increment("distributed_storage.deletes")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Distributed delete failed: {str(e)}")
            return False
    
    async def get_user_sessions(self, user_id: str) -> List[SessionData]:
        """Get all sessions for a user"""
        
        return await self.persistence.get_user_sessions(user_id)
    
    async def _backup_loop(self):
        """
Background backup task"""
        
        try:
            while True:
                await asyncio.sleep(self.config.backup_interval)
                await self._perform_backup()
                
        except asyncio.CancelledError:
            self.logger.info("Backup loop cancelled")
        except Exception as e:
            self.logger.error(f"Backup loop error: {str(e)}")
    
    async def _cleanup_loop(self):
        """Background cleanup task"""
        
        try:
            while True:
                await asyncio.sleep(self.config.cleanup_interval)
                await self._perform_cleanup()
                
        except asyncio.CancelledError:
            self.logger.info("Cleanup loop cancelled")
        except Exception as e:
            self.logger.error(f"Cleanup loop error: {str(e)}")
    
    async def _perform_backup(self):
        """Perform periodic backup of cache to persistence"""
        
        try:
            # Get all active sessions from cache
            active_sessions = await self.cache_manager.redis_manager.set_members("active_sessions")
            
            if not active_sessions:
                return
            
            backup_count = 0
            
            for session_id in active_sessions:
                session_data = await self.cache_manager.get_session(session_id)
                if session_data:
                    success = await self.persistence.save_session(session_data)
                    if success:
                        backup_count += 1
            
            self.logger.info(f"Backed up {backup_count} sessions")
            await self.metrics_collector.increment("distributed_storage.backups", value=backup_count)
            
        except Exception as e:
            self.logger.error(f"Backup failed: {str(e)}")
    
    async def _perform_cleanup(self):
        """Perform periodic cleanup"""
        
        try:
            # Clean up old persistent sessions
            deleted_count = await self.persistence.cleanup_old_sessions()
            
            # Clean up cache if over limit
            cache_size = await self.cache_manager._get_cache_size()
            
            if cache_size > self.config.max_memory_sessions:
                # Implement LRU eviction
                evicted_count = await self._evict_lru_sessions(
                    cache_size - self.config.max_memory_sessions
                )
                self.logger.info(f"Evicted {evicted_count} LRU sessions")
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {str(e)}")
    
    async def _evict_lru_sessions(self, count_to_evict: int) -> int:
        """Evict least recently used sessions"""
        
        try:
            # Get session metadata sorted by last access time
            active_sessions = await self.cache_manager.redis_manager.set_members("active_sessions")
            
            session_access_times = []
            
            for session_id in active_sessions:
                metadata_key = f"session_metadata:{session_id}"
                metadata_json = await self.cache_manager.redis_manager.get(metadata_key)
                
                if metadata_json:
                    metadata = json.loads(metadata_json)
                    last_accessed = datetime.fromisoformat(metadata.get("last_accessed", "1970-01-01"))
                    session_access_times.append((session_id, last_accessed))
            
            # Sort by access time (oldest first)
            session_access_times.sort(key=lambda x: x[1])
            
            # Evict oldest sessions
            evicted_count = 0
            for session_id, _ in session_access_times[:count_to_evict]:
                success = await self.cache_manager.evict_session(session_id)
                if success:
                    evicted_count += 1
            
            return evicted_count
            
        except Exception as e:
            self.logger.error(f"LRU eviction failed: {str(e)}")
            return 0
    
    async def get_storage_statistics(self) -> Dict[str, Any]:
        """Get comprehensive storage statistics"""
        
        try:
            cache_stats = await self.cache_manager.get_cache_statistics()
            
            # Get persistence statistics
            async with get_async_session() as session:
                total_sessions_query = select(text("COUNT(*)")).select_from(SessionModel)
                result = await session.execute(total_sessions_query)
                total_persistent_sessions = result.scalar()
                
                avg_size_query = select(text("AVG(data_size)")).select_from(SessionModel)
                result = await session.execute(avg_size_query)
                avg_session_size = result.scalar() or 0
            
            return {
                "cache": cache_stats,
                "persistence": {
                    "total_sessions": total_persistent_sessions,
                    "average_session_size": float(avg_session_size)
                },
                "configuration": {
                    "primary_backend": self.config.primary_backend.value,
                    "secondary_backend": self.config.secondary_backend.value if self.config.secondary_backend else None,
                    "compression": self.config.compression.value,
                    "encryption_enabled": self.config.encryption_enabled,
                    "auto_backup": self.config.auto_backup
                }
            }
            
        except Exception as e:
            self.logger.error(f"Statistics calculation failed: {str(e)}")
            return {}


class ConversationSessionStore:
    """Main conversation session store facade"""
    
    def __init__(self, config: Optional[SessionStoreConfig] = None):
        self.config = config or SessionStoreConfig()
        self.distributed_storage = DistributedSessionStorage(self.config)
        self.logger = get_logger(self.__class__.__name__)
    
    async def initialize(self):
        """
Initialize the session store"""
        
        await self.distributed_storage.start_background_tasks()
        self.logger.info("Conversation session store initialized")
    
    async def shutdown(self):
        """Shutdown the session store"""
        
        await self.distributed_storage.stop_background_tasks()
        self.logger.info("Conversation session store shutdown")
    
    async def create_session(self, session_id: str, user_id: str) -> SessionData:
        """Create new session"""
        
        session_data = SessionData(
            session_id=session_id,
            user_id=user_id
        )
        
        await self.distributed_storage.store_session(session_data)
        return session_data
    
    async def get_session(self, session_id: str) -> Optional[SessionData]:
        """
Get session by ID"""
        
        return await self.distributed_storage.get_session(session_id)
    
    async def update_session(self, session_data: SessionData) -> bool:
        """
Update session data"""
        
        return await self.distributed_storage.store_session(session_data)
    
    async def delete_session(self, session_id: str) -> bool:
        """
Delete session"""
        
        return await self.distributed_storage.delete_session(session_id)
    
    async def get_user_sessions(self, user_id: str) -> List[SessionData]:
        """
Get all sessions for user"""
        
        return await self.distributed_storage.get_user_sessions(user_id)
    
    async def add_conversation_message(
        self,
        session_id: str,
        message: Dict[str, Any]
    ) -> bool:
        """
Add message to conversation history"""
        
        try:
            session_data = await self.get_session(session_id)
            
            if not session_data:
                return False
            
            # Add message with timestamp
            message["timestamp"] = datetime.utcnow().isoformat()
            message["message_id"] = str(uuid4())
            
            session_data.conversation_history.append(message)
            session_data.updated_at = datetime.utcnow()
            
            return await self.update_session(session_data)
            
        except Exception as e:
            self.logger.error(f"Failed to add conversation message: {str(e)}")
            return False
    
    async def update_context(
        self,
        session_id: str,
        context_update: Dict[str, Any]
    ) -> bool:
        """Update session context"""
        
        try:
            session_data = await self.get_session(session_id)
            
            if not session_data:
                return False
            
            # Add context with timestamp
            context_update["timestamp"] = datetime.utcnow().isoformat()
            
            session_data.context_stack.append(context_update)
            session_data.updated_at = datetime.utcnow()
            
            # Keep only last 50 context entries
            if len(session_data.context_stack) > 50:
                session_data.context_stack = session_data.context_stack[-50:]
            
            return await self.update_session(session_data)
            
        except Exception as e:
            self.logger.error(f"Failed to update context: {str(e)}")
            return False
    
    async def get_conversation_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get conversation history for session"""
        
        try:
            session_data = await self.get_session(session_id)
            
            if not session_data:
                return []
            
            history = session_data.conversation_history
            
            if limit:
                history = history[-limit:]
            
            return history
            
        except Exception as e:
            self.logger.error(f"Failed to get conversation history: {str(e)}")
            return []
    
    async def get_storage_statistics(self) -> Dict[str, Any]:
        """Get storage system statistics"""
        
        return await self.distributed_storage.get_storage_statistics()
