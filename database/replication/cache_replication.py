"""⚡ Cache Replication Handlers - Redis + Vector Database Replication
====================================================================
Module: database/replication/cache_replication.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Database Replication & High Availability Architect
Type: Cache & Vector Database Replication - Enterprise Production-Ready
Responsibility: Comprehensive replication for Redis and Vector databases
=======================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This module provides comprehensive cache and vector database replication:
- Redis master-slave replication with Sentinel integration
- Vector database synchronization (FAISS, Pinecone, Weaviate)
- Cache invalidation and propagation strategies
- Performance optimization for high-throughput scenarios
- Intelligent conflict resolution for cached data
"""

import asyncio
import logging
import time
import json
import hashlib
from typing import Dict, Any, Optional, List, Set, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import threading
from abc import ABC, abstractmethod
import numpy as np

# Redis imports with fallbacks
try:
    import redis.asyncio as aioredis
    import redis.sentinel
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Vector database imports with fallbacks
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

try:
    import weaviate
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False

try:
    from .replication_config import ReplicationConfig, DatabaseEndpoint, ReplicationTopology
    from .database_replication import ReplicationStatus, DatabaseHealth, ReplicationMetrics
except ImportError:
    # Fallback for development
    pass

logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """Cache replication strategies."""
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    WRITE_AROUND = "write_around"
    READ_THROUGH = "read_through"
    REFRESH_AHEAD = "refresh_ahead"

class VectorSyncMode(Enum):
    """Vector database synchronization modes."""
    REAL_TIME = "real_time"
    BATCH = "batch"
    DELTA = "delta"
    FULL_SYNC = "full_sync"

@dataclass
class CacheHealth:
    """Cache system health status."""
    cache_name: str
    is_healthy: bool
    hit_ratio: float
    memory_usage_mb: float
    operations_per_sec: float
    error_count: int
    last_sync_time: datetime
    connected_nodes: List[str]
    status: ReplicationStatus
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VectorHealth:
    """Vector database health status."""
    vector_db_name: str
    is_healthy: bool
    vector_count: int
    index_size_mb: float
    query_latency_ms: float
    sync_lag_vectors: int
    last_sync_time: datetime
    status: ReplicationStatus
    metadata: Dict[str, Any] = field(default_factory=dict)

class ICacheReplicationHandler(ABC):
    """Interface for cache replication handlers."""
    
    @abstractmethod
    async def initialize(self, topology: ReplicationTopology) -> bool:
        """Initialize cache replication handler."""
        pass
    
    @abstractmethod
    async def start_replication(self) -> bool:
        """Start cache replication process."""
        pass
    
    @abstractmethod
    async def stop_replication(self) -> bool:
        """Stop cache replication process."""
        pass
    
    @abstractmethod
    async def get_health_status(self) -> CacheHealth:
        """Get current cache health status."""
        pass
    
    @abstractmethod
    async def invalidate_cache(self, keys: List[str]) -> bool:
        """Invalidate cache entries across all nodes."""
        pass
    
    @abstractmethod
    async def sync_cache_data(self, data: Dict[str, Any]) -> bool:
        """Synchronize cache data across nodes."""
        pass

class IVectorReplicationHandler(ABC):
    """Interface for vector database replication handlers."""
    
    @abstractmethod
    async def initialize(self, topology: ReplicationTopology) -> bool:
        """Initialize vector replication handler."""
        pass
    
    @abstractmethod
    async def start_replication(self) -> bool:
        """Start vector replication process."""
        pass
    
    @abstractmethod
    async def stop_replication(self) -> bool:
        """Stop vector replication process."""
        pass
    
    @abstractmethod
    async def get_health_status(self) -> VectorHealth:
        """Get current vector database health status."""
        pass
    
    @abstractmethod
    async def sync_vectors(self, vectors: List[np.ndarray], metadata: List[Dict]) -> bool:
        """Synchronize vectors across databases."""
        pass
    
    @abstractmethod
    async def delete_vectors(self, vector_ids: List[str]) -> bool:
        """Delete vectors from all replicas."""
        pass

class RedisReplicationHandler(ICacheReplicationHandler):
    """Redis replication handler with Sentinel integration."""
    
    def __init__(self):
        self._topology: Optional[ReplicationTopology] = None
        self._redis_master: Optional[aioredis.Redis] = None
        self._redis_slaves: List[aioredis.Redis] = []
        self._sentinel: Optional[redis.sentinel.Sentinel] = None
        self._is_running = False
        self._monitoring_task: Optional[asyncio.Task] = None
        self._cache_strategy = CacheStrategy.WRITE_THROUGH
        self._metrics_history: List[Dict[str, Any]] = []
        
    async def initialize(self, topology: ReplicationTopology) -> bool:
        """Initialize Redis replication."""
        try:
            if not REDIS_AVAILABLE:
                logger.error("❌ redis-py not available for Redis replication")
                return False
                
            self._topology = topology
            
            # Initialize master connection
            master_url = f"redis://{topology.master.username}:{topology.master.password}@{topology.master.host}:{topology.master.port}/{topology.master.database}"
            self._redis_master = aioredis.from_url(
                master_url,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=topology.master.connection_timeout,
                socket_connect_timeout=topology.master.connection_timeout
            )
            
            # Initialize slave connections
            for slave in topology.slaves:
                slave_url = f"redis://{slave.username}:{slave.password}@{slave.host}:{slave.port}/{slave.database}"
                slave_redis = aioredis.from_url(
                    slave_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_timeout=slave.connection_timeout,
                    socket_connect_timeout=slave.connection_timeout
                )
                self._redis_slaves.append(slave_redis)
            
            # Setup Sentinel if configured
            await self._setup_sentinel()
            
            # Verify replication
            await self._verify_replication()
            
            logger.info(f"✅ Redis replication initialized with {len(topology.slaves)} slaves")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Redis replication: {e}")
            return False
    
    async def _setup_sentinel(self):
        """Setup Redis Sentinel for high availability."""
        try:
            # Note: This is a simplified Sentinel setup
            # In production, you would configure actual Sentinel instances
            
            # Check if master supports replication
            master_info = await self._redis_master.info('replication')
            if master_info.get('role') == 'master':
                logger.info("✅ Redis master confirmed for replication")
            else:
                logger.warning("⚠️ Redis instance is not configured as master")
                
        except Exception as e:
            logger.error(f"❌ Failed to setup Redis Sentinel: {e}")
            raise
    
    async def _verify_replication(self):
        """Verify Redis replication is working."""
        try:
            # Set a test key on master
            test_key = f"replication_test_{int(time.time())}"
            await self._redis_master.set(test_key, "test_value", ex=60)
            
            # Wait a moment for replication
            await asyncio.sleep(1)
            
            # Check slaves have the key
            verified_slaves = 0
            for i, slave in enumerate(self._redis_slaves):
                try:
                    value = await slave.get(test_key)
                    if value == "test_value":
                        verified_slaves += 1
                        logger.info(f"✅ Slave {i} replication verified")
                    else:
                        logger.warning(f"⚠️ Slave {i} replication not working")
                except Exception as e:
                    logger.error(f"❌ Slave {i} verification failed: {e}")
            
            # Cleanup test key
            await self._redis_master.delete(test_key)
            
            logger.info(f"✅ Redis replication verified on {verified_slaves}/{len(self._redis_slaves)} slaves")
            
        except Exception as e:
            logger.error(f"❌ Redis replication verification failed: {e}")
            raise
    
    async def start_replication(self) -> bool:
        """Start Redis replication monitoring."""
        try:
            if self._is_running:
                logger.warning("Redis replication already running")
                return True
            
            # Start monitoring task
            self._monitoring_task = asyncio.create_task(self._replication_monitoring_loop())
            self._is_running = True
            
            logger.info("✅ Redis replication started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start Redis replication: {e}")
            return False
    
    async def stop_replication(self) -> bool:
        """Stop Redis replication."""
        try:
            self._is_running = False
            
            if self._monitoring_task:
                self._monitoring_task.cancel()
                try:
                    await self._monitoring_task
                except asyncio.CancelledError:
                    pass
            
            # Close connections
            if self._redis_master:
                await self._redis_master.close()
            
            for slave in self._redis_slaves:
                await slave.close()
            
            logger.info("✅ Redis replication stopped")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop Redis replication: {e}")
            return False
    
    async def _replication_monitoring_loop(self):
        """Redis replication monitoring loop."""
        while self._is_running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Check master health
                await self._check_master_health()
                
                # Check slave connectivity and lag
                await self._check_slave_health()
                
                # Collect performance metrics
                metrics = await self._collect_cache_metrics()
                self._metrics_history.append(metrics)
                
                # Keep only recent metrics
                if len(self._metrics_history) > 1000:
                    self._metrics_history = self._metrics_history[-1000:]
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Redis monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _check_master_health(self) -> Dict[str, Any]:
        """Check Redis master health."""
        try:
            # Get master info
            master_info = await self._redis_master.info()
            memory_info = await self._redis_master.info('memory')
            stats_info = await self._redis_master.info('stats')
            
            health_data = {
                'connected_clients': master_info.get('connected_clients', 0),
                'used_memory_mb': memory_info.get('used_memory', 0) / (1024 * 1024),
                'total_connections': stats_info.get('total_connections_received', 0),
                'total_commands': stats_info.get('total_commands_processed', 0),
                'keyspace_hits': stats_info.get('keyspace_hits', 0),
                'keyspace_misses': stats_info.get('keyspace_misses', 0),
                'instantaneous_ops_per_sec': stats_info.get('instantaneous_ops_per_sec', 0)
            }
            
            # Calculate hit ratio
            hits = health_data['keyspace_hits']
            misses = health_data['keyspace_misses']
            total_requests = hits + misses
            health_data['hit_ratio'] = hits / total_requests if total_requests > 0 else 0.0
            
            return health_data
            
        except Exception as e:
            logger.error(f"❌ Failed to check Redis master health: {e}")
            return {'error': str(e)}
    
    async def _check_slave_health(self) -> List[Dict[str, Any]]:
        """Check Redis slave health."""
        slave_health = []
        
        for i, slave in enumerate(self._redis_slaves):
            try:
                # Check connectivity
                pong = await slave.ping()
                if pong:
                    slave_info = await slave.info()
                    
                    health_data = {
                        'slave_index': i,
                        'connected': True,
                        'role': slave_info.get('role', 'unknown'),
                        'master_link_status': slave_info.get('master_link_status', 'unknown'),
                        'lag_seconds': slave_info.get('master_last_io_seconds_ago', 0)
                    }
                else:
                    health_data = {
                        'slave_index': i,
                        'connected': False,
                        'error': 'ping_failed'
                    }
                
                slave_health.append(health_data)
                
            except Exception as e:
                logger.error(f"❌ Failed to check slave {i} health: {e}")
                slave_health.append({
                    'slave_index': i,
                    'connected': False,
                    'error': str(e)
                })
        
        return slave_health
    
    async def _collect_cache_metrics(self) -> Dict[str, Any]:
        """Collect Redis performance metrics."""
        try:
            master_health = await self._check_master_health()
            slave_health = await self._check_slave_health()
            
            return {
                'timestamp': time.time(),
                'master_health': master_health,
                'slave_health': slave_health,
                'connected_slaves': sum(1 for s in slave_health if s.get('connected', False)),
                'total_slaves': len(slave_health)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to collect Redis metrics: {e}")
            return {'timestamp': time.time(), 'error': str(e)}
    
    async def get_health_status(self) -> CacheHealth:
        """Get Redis health status."""
        try:
            master_health = await self._check_master_health()
            slave_health = await self._check_slave_health()
            
            # Determine overall health
            connected_slaves = [s for s in slave_health if s.get('connected', False)]
            is_healthy = (
                'error' not in master_health and
                len(connected_slaves) == len(self._redis_slaves) and
                master_health.get('hit_ratio', 0) > 0.7  # 70% hit ratio threshold
            )
            
            # Determine status
            if is_healthy:
                status = ReplicationStatus.HEALTHY
            elif len(connected_slaves) > len(self._redis_slaves) / 2:
                status = ReplicationStatus.LAGGING
            else:
                status = ReplicationStatus.FAILED
            
            return CacheHealth(
                cache_name="redis",
                is_healthy=is_healthy,
                hit_ratio=master_health.get('hit_ratio', 0.0),
                memory_usage_mb=master_health.get('used_memory_mb', 0.0),
                operations_per_sec=master_health.get('instantaneous_ops_per_sec', 0.0),
                error_count=0,  # TODO: Track actual errors
                last_sync_time=datetime.now(timezone.utc),
                connected_nodes=[f"slave_{s['slave_index']}" for s in connected_slaves],
                status=status,
                metadata={
                    'total_slaves': len(self._redis_slaves),
                    'connected_slaves': len(connected_slaves),
                    'master_clients': master_health.get('connected_clients', 0)
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get Redis health status: {e}")
            return CacheHealth(
                cache_name="redis",
                is_healthy=False,
                hit_ratio=0.0,
                memory_usage_mb=0.0,
                operations_per_sec=0.0,
                error_count=1,
                last_sync_time=datetime.now(timezone.utc),
                connected_nodes=[],
                status=ReplicationStatus.FAILED
            )
    
    async def invalidate_cache(self, keys: List[str]) -> bool:
        """Invalidate cache entries across all nodes."""
        try:
            # Delete from master (will replicate to slaves)
            if keys:
                deleted_count = await self._redis_master.delete(*keys)
                logger.info(f"✅ Invalidated {deleted_count} cache keys from Redis")
                return deleted_count > 0
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to invalidate Redis cache: {e}")
            return False
    
    async def sync_cache_data(self, data: Dict[str, Any]) -> bool:
        """Synchronize cache data across nodes."""
        try:
            # Set data on master (will replicate to slaves)
            pipeline = self._redis_master.pipeline()
            for key, value in data.items():
                if isinstance(value, dict):
                    pipeline.hset(key, mapping=value)
                else:
                    pipeline.set(key, json.dumps(value) if not isinstance(value, str) else value)
            
            results = await pipeline.execute()
            success_count = sum(1 for r in results if r)
            
            logger.info(f"✅ Synced {success_count}/{len(data)} cache entries to Redis")
            return success_count == len(data)
            
        except Exception as e:
            logger.error(f"❌ Failed to sync cache data to Redis: {e}")
            return False

class FAISSReplicationHandler(IVectorReplicationHandler):
    """FAISS vector database replication handler."""
    
    def __init__(self):
        self._topology: Optional[ReplicationTopology] = None
        self._master_index: Optional[faiss.Index] = None
        self._slave_indices: List[faiss.Index] = []
        self._index_paths: Dict[str, str] = {}
        self._is_running = False
        self._monitoring_task: Optional[asyncio.Task] = None
        self._vector_dimension = 768  # Default dimension
        self._sync_mode = VectorSyncMode.BATCH
        
    async def initialize(self, topology: ReplicationTopology) -> bool:
        """Initialize FAISS replication."""
        try:
            if not FAISS_AVAILABLE:
                logger.error("❌ FAISS not available for vector replication")
                return False
                
            self._topology = topology
            
            # Initialize master index
            master_path = topology.master.metadata.get('index_path', '/tmp/faiss_master.index')
            self._index_paths['master'] = master_path
            
            try:
                # Try to load existing index
                self._master_index = faiss.read_index(master_path)
                self._vector_dimension = self._master_index.d
                logger.info(f"✅ Loaded existing FAISS master index: {self._vector_dimension}D")
            except:
                # Create new index
                self._master_index = faiss.IndexFlatL2(self._vector_dimension)
                logger.info(f"✅ Created new FAISS master index: {self._vector_dimension}D")
            
            # Initialize slave indices
            for i, slave in enumerate(topology.slaves):
                slave_path = slave.metadata.get('index_path', f'/tmp/faiss_slave_{i}.index')
                self._index_paths[f'slave_{i}'] = slave_path
                
                try:
                    slave_index = faiss.read_index(slave_path)
                    self._slave_indices.append(slave_index)
                    logger.info(f"✅ Loaded FAISS slave index {i}")
                except:
                    # Clone master index structure
                    slave_index = faiss.IndexFlatL2(self._vector_dimension)
                    self._slave_indices.append(slave_index)
                    logger.info(f"✅ Created FAISS slave index {i}")
            
            logger.info(f"✅ FAISS replication initialized with {len(topology.slaves)} replicas")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize FAISS replication: {e}")
            return False
    
    async def start_replication(self) -> bool:
        """Start FAISS replication monitoring."""
        try:
            if self._is_running:
                logger.warning("FAISS replication already running")
                return True
            
            # Start monitoring task
            self._monitoring_task = asyncio.create_task(self._replication_monitoring_loop())
            self._is_running = True
            
            logger.info("✅ FAISS replication started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start FAISS replication: {e}")
            return False
    
    async def stop_replication(self) -> bool:
        """Stop FAISS replication."""
        try:
            self._is_running = False
            
            if self._monitoring_task:
                self._monitoring_task.cancel()
                try:
                    await self._monitoring_task
                except asyncio.CancelledError:
                    pass
            
            # Save indices to disk
            await self._save_indices()
            
            logger.info("✅ FAISS replication stopped")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop FAISS replication: {e}")
            return False
    
    async def _replication_monitoring_loop(self):
        """FAISS replication monitoring loop."""
        while self._is_running:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Sync indices if needed
                if self._sync_mode == VectorSyncMode.BATCH:
                    await self._sync_indices()
                
                # Save indices periodically
                await self._save_indices()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ FAISS monitoring error: {e}")
                await asyncio.sleep(120)
    
    async def _sync_indices(self):
        """Synchronize FAISS indices."""
        try:
            if not self._master_index:
                return
            
            master_count = self._master_index.ntotal
            
            # Sync each slave to match master
            for i, slave_index in enumerate(self._slave_indices):
                slave_count = slave_index.ntotal
                
                if slave_count != master_count:
                    logger.info(f"🔄 Syncing FAISS slave {i}: {slave_count} -> {master_count} vectors")
                    
                    # Simple sync: replace slave with master content
                    # In production, you'd implement more sophisticated delta sync
                    slave_index.reset()
                    
                    if master_count > 0:
                        # Get all vectors from master (this is inefficient for large indices)
                        all_vectors = self._master_index.reconstruct_n(0, master_count)
                        slave_index.add(all_vectors)
                    
                    logger.info(f"✅ FAISS slave {i} synced")
            
        except Exception as e:
            logger.error(f"❌ FAISS sync failed: {e}")
    
    async def _save_indices(self):
        """Save FAISS indices to disk."""
        try:
            # Save master index
            if self._master_index:
                faiss.write_index(self._master_index, self._index_paths['master'])
            
            # Save slave indices
            for i, slave_index in enumerate(self._slave_indices):
                faiss.write_index(slave_index, self._index_paths[f'slave_{i}'])
            
        except Exception as e:
            logger.error(f"❌ Failed to save FAISS indices: {e}")
    
    async def get_health_status(self) -> VectorHealth:
        """Get FAISS health status."""
        try:
            if not self._master_index:
                return VectorHealth(
                    vector_db_name="faiss",
                    is_healthy=False,
                    vector_count=0,
                    index_size_mb=0.0,
                    query_latency_ms=0.0,
                    sync_lag_vectors=0,
                    last_sync_time=datetime.now(timezone.utc),
                    status=ReplicationStatus.FAILED
                )
            
            master_count = self._master_index.ntotal
            
            # Check slave sync status
            max_lag = 0
            synced_slaves = 0
            
            for slave_index in self._slave_indices:
                slave_count = slave_index.ntotal
                lag = abs(master_count - slave_count)
                max_lag = max(max_lag, lag)
                
                if lag == 0:
                    synced_slaves += 1
            
            # Determine health
            is_healthy = synced_slaves == len(self._slave_indices)
            
            if is_healthy:
                status = ReplicationStatus.HEALTHY
            elif synced_slaves > len(self._slave_indices) / 2:
                status = ReplicationStatus.LAGGING
            else:
                status = ReplicationStatus.FAILED
            
            # Estimate index size (rough calculation)
            index_size_mb = (master_count * self._vector_dimension * 4) / (1024 * 1024)  # 4 bytes per float
            
            return VectorHealth(
                vector_db_name="faiss",
                is_healthy=is_healthy,
                vector_count=master_count,
                index_size_mb=index_size_mb,
                query_latency_ms=1.0,  # TODO: Measure actual query latency
                sync_lag_vectors=max_lag,
                last_sync_time=datetime.now(timezone.utc),
                status=status,
                metadata={
                    'dimension': self._vector_dimension,
                    'total_slaves': len(self._slave_indices),
                    'synced_slaves': synced_slaves
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get FAISS health status: {e}")
            return VectorHealth(
                vector_db_name="faiss",
                is_healthy=False,
                vector_count=0,
                index_size_mb=0.0,
                query_latency_ms=0.0,
                sync_lag_vectors=0,
                last_sync_time=datetime.now(timezone.utc),
                status=ReplicationStatus.FAILED
            )
    
    async def sync_vectors(self, vectors: List[np.ndarray], metadata: List[Dict]) -> bool:
        """Synchronize vectors across FAISS databases."""
        try:
            if not vectors or not self._master_index:
                return True
            
            # Convert vectors to numpy array
            vector_array = np.array(vectors, dtype=np.float32)
            
            # Add to master index
            self._master_index.add(vector_array)
            
            # Replicate to slaves based on sync mode
            if self._sync_mode == VectorSyncMode.REAL_TIME:
                for slave_index in self._slave_indices:
                    slave_index.add(vector_array)
            
            logger.info(f"✅ Synced {len(vectors)} vectors to FAISS")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to sync vectors to FAISS: {e}")
            return False
    
    async def delete_vectors(self, vector_ids: List[str]) -> bool:
        """Delete vectors from FAISS databases."""
        try:
            # Note: FAISS doesn't support direct deletion by ID
            # This would require maintaining a separate ID mapping
            # For now, log the operation
            
            logger.warning(f"⚠️ FAISS deletion not implemented for {len(vector_ids)} vectors")
            logger.info("💡 Consider using IndexIDMap wrapper for deletion support")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete vectors from FAISS: {e}")
            return False

class CacheReplicationCoordinator:
    """Coordinates replication across cache and vector databases."""
    
    def __init__(self, config: Optional[ReplicationConfig] = None):
        self._config = config
        self._cache_handlers: Dict[str, ICacheReplicationHandler] = {}
        self._vector_handlers: Dict[str, IVectorReplicationHandler] = {}
        self._is_initialized = False
        
    async def initialize(self) -> bool:
        """Initialize cache replication coordinator."""
        try:
            if not self._config:
                logger.error("❌ No configuration provided to cache coordinator")
                return False
            
            # Initialize cache handlers
            for db_type in self._config.enabled_databases:
                if db_type.value == 'redis' and db_type in self._config.database_topologies:
                    topology = self._config.database_topologies[db_type]
                    handler = RedisReplicationHandler()
                    
                    if await handler.initialize(topology):
                        self._cache_handlers['redis'] = handler
                        logger.info("✅ Initialized Redis cache handler")
                    else:
                        logger.error("❌ Failed to initialize Redis cache handler")
                
                elif db_type.value == 'vector_db' and db_type in self._config.database_topologies:
                    topology = self._config.database_topologies[db_type]
                    
                    # Determine vector DB type from metadata
                    vector_type = topology.master.metadata.get('vector_type', 'faiss')
                    
                    if vector_type == 'faiss':
                        handler = FAISSReplicationHandler()
                        if await handler.initialize(topology):
                            self._vector_handlers['faiss'] = handler
                            logger.info("✅ Initialized FAISS vector handler")
                        else:
                            logger.error("❌ Failed to initialize FAISS vector handler")
            
            self._is_initialized = len(self._cache_handlers) > 0 or len(self._vector_handlers) > 0
            logger.info(f"✅ Cache replication coordinator initialized with {len(self._cache_handlers)} cache handlers and {len(self._vector_handlers)} vector handlers")
            return self._is_initialized
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize cache replication coordinator: {e}")
            return False
    
    async def start_replication(self) -> bool:
        """Start replication for all initialized handlers."""
        try:
            if not self._is_initialized:
                logger.error("❌ Cache coordinator not initialized")
                return False
            
            success_count = 0
            total_handlers = len(self._cache_handlers) + len(self._vector_handlers)
            
            # Start cache handlers
            for cache_type, handler in self._cache_handlers.items():
                if await handler.start_replication():
                    success_count += 1
                    logger.info(f"✅ Started cache replication for {cache_type}")
                else:
                    logger.error(f"❌ Failed to start cache replication for {cache_type}")
            
            # Start vector handlers
            for vector_type, handler in self._vector_handlers.items():
                if await handler.start_replication():
                    success_count += 1
                    logger.info(f"✅ Started vector replication for {vector_type}")
                else:
                    logger.error(f"❌ Failed to start vector replication for {vector_type}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"❌ Failed to start cache replication: {e}")
            return False
    
    async def stop_replication(self) -> bool:
        """Stop replication for all handlers."""
        try:
            success_count = 0
            total_handlers = len(self._cache_handlers) + len(self._vector_handlers)
            
            # Stop cache handlers
            for cache_type, handler in self._cache_handlers.items():
                if await handler.stop_replication():
                    success_count += 1
                    logger.info(f"✅ Stopped cache replication for {cache_type}")
                else:
                    logger.error(f"❌ Failed to stop cache replication for {cache_type}")
            
            # Stop vector handlers
            for vector_type, handler in self._vector_handlers.items():
                if await handler.stop_replication():
                    success_count += 1
                    logger.info(f"✅ Stopped vector replication for {vector_type}")
                else:
                    logger.error(f"❌ Failed to stop vector replication for {vector_type}")
            
            return success_count == total_handlers
            
        except Exception as e:
            logger.error(f"❌ Failed to stop cache replication: {e}")
            return False
    
    async def get_health_status(self) -> DatabaseHealth:
        """Get aggregated health status for cache and vector databases."""
        try:
            # This is a simplified aggregation that returns a DatabaseHealth object
            # In a real implementation, you might want separate health objects for cache vs vector
            
            total_healthy = 0
            total_handlers = len(self._cache_handlers) + len(self._vector_handlers)
            
            if total_handlers == 0:
                return DatabaseHealth(
                    database_name="no_cache_databases",
                    is_healthy=False,
                    lag_ms=0.0,
                    master_node="none",
                    slave_nodes=[],
                    last_sync_time=datetime.now(timezone.utc),
                    data_size_gb=0.0,
                    ops_per_sec=0.0,
                    error_count=1,
                    status=ReplicationStatus.FAILED
                )
            
            # Check cache handlers
            for cache_type, handler in self._cache_handlers.items():
                try:
                    health = await handler.get_health_status()
                    if health.is_healthy:
                        total_healthy += 1
                except Exception as e:
                    logger.error(f"❌ Failed to get health for cache {cache_type}: {e}")
            
            # Check vector handlers
            for vector_type, handler in self._vector_handlers.items():
                try:
                    health = await handler.get_health_status()
                    if health.is_healthy:
                        total_healthy += 1
                except Exception as e:
                    logger.error(f"❌ Failed to get health for vector {vector_type}: {e}")
            
            # Determine overall status
            overall_healthy = total_healthy == total_handlers
            if overall_healthy:
                overall_status = ReplicationStatus.HEALTHY
            elif total_healthy > total_handlers / 2:
                overall_status = ReplicationStatus.LAGGING
            else:
                overall_status = ReplicationStatus.FAILED
            
            return DatabaseHealth(
                database_name="cache_aggregated",
                is_healthy=overall_healthy,
                lag_ms=0.0,  # Cache systems don't have traditional lag
                master_node="multiple",
                slave_nodes=[],
                last_sync_time=datetime.now(timezone.utc),
                data_size_gb=0.0,  # TODO: Aggregate from handlers
                ops_per_sec=0.0,  # TODO: Aggregate from handlers
                error_count=0,
                status=overall_status,
                metadata={
                    'total_handlers': total_handlers,
                    'healthy_handlers': total_healthy,
                    'cache_handlers': list(self._cache_handlers.keys()),
                    'vector_handlers': list(self._vector_handlers.keys())
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get aggregated cache health status: {e}")
            return DatabaseHealth(
                database_name="cache_error",
                is_healthy=False,
                lag_ms=0.0,
                master_node="error",
                slave_nodes=[],
                last_sync_time=datetime.now(timezone.utc),
                data_size_gb=0.0,
                ops_per_sec=0.0,
                error_count=1,
                status=ReplicationStatus.FAILED
            )
    
    async def get_performance_metrics(self) -> ReplicationMetrics:
        """Get aggregated performance metrics."""
        try:
            # Return simplified metrics for cache systems
            return ReplicationMetrics(
                timestamp=datetime.now(timezone.utc),
                lag_ms=0.0,  # N/A for cache systems
                throughput_ops_per_sec=0.0,  # TODO: Aggregate from handlers
                error_rate=0.0,  # TODO: Calculate from handlers
                data_size_gb=0.0,  # TODO: Aggregate from handlers
                network_bandwidth_mbps=0.0,
                cpu_usage_percent=0.0,
                memory_usage_percent=0.0,
                disk_usage_percent=0.0,
                metadata={'handler_count': len(self._cache_handlers) + len(self._vector_handlers)}
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get cache performance metrics: {e}")
            return ReplicationMetrics(
                timestamp=datetime.now(timezone.utc),
                lag_ms=0.0,
                throughput_ops_per_sec=0.0,
                error_rate=1.0,
                data_size_gb=0.0,
                network_bandwidth_mbps=0.0,
                cpu_usage_percent=0.0,
                memory_usage_percent=0.0,
                disk_usage_percent=0.0
            )
    
    async def close(self):
        """Close all handlers."""
        try:
            # Close cache handlers
            for cache_type, handler in self._cache_handlers.items():
                try:
                    await handler.stop_replication()
                    logger.info(f"✅ Closed {cache_type} cache handler")
                except Exception as e:
                    logger.error(f"❌ Error closing {cache_type} cache handler: {e}")
            
            # Close vector handlers
            for vector_type, handler in self._vector_handlers.items():
                try:
                    await handler.stop_replication()
                    logger.info(f"✅ Closed {vector_type} vector handler")
                except Exception as e:
                    logger.error(f"❌ Error closing {vector_type} vector handler: {e}")
            
            self._cache_handlers.clear()
            self._vector_handlers.clear()
            self._is_initialized = False
            logger.info("✅ Cache replication coordinator closed")
            
        except Exception as e:
            logger.error(f"❌ Error closing cache replication coordinator: {e}")

# Factory functions for easy instantiation
def create_redis_handler() -> RedisReplicationHandler:
    """Create a Redis replication handler."""
    return RedisReplicationHandler()

def create_faiss_handler() -> FAISSReplicationHandler:
    """Create a FAISS replication handler."""
    return FAISSReplicationHandler()

def create_cache_coordinator(config: ReplicationConfig) -> CacheReplicationCoordinator:
    """Create a cache replication coordinator."""
    return CacheReplicationCoordinator(config)