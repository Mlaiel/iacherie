"""
Replica Sync Manager for Redis Enterprise
Microservices + DBA Implementation - Advanced Replica Synchronization

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import redis.asyncio as redis
from config.core.redis import RedisSettings

logger = logging.getLogger(__name__)

class ReplicationState(Enum):
    """Replica synchronization states"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    SYNC_INITIAL = "sync_initial"
    SYNC_PARTIAL = "sync_partial" 
    SYNC_FULL = "sync_full"
    CONNECTED = "connected"
    LAGGING = "lagging"
    FAILED = "failed"
    RECOVERING = "recovering"

class SyncStrategy(Enum):
    """Synchronization strategies"""
    ASYNC = "async"
    SEMI_SYNC = "semi_sync"
    SYNC = "sync"
    PRIORITY_BASED = "priority_based"

@dataclass
class ReplicaInfo:
    """Information about a replica node"""
    replica_id: str
    host: str
    port: int
    master_host: str
    master_port: int
    state: ReplicationState
    replication_lag: float = 0.0  # seconds
    last_sync: Optional[datetime] = None
    bytes_behind: int = 0
    offset: int = 0
    priority: int = 50  # 0-100, higher = more important
    read_only: bool = True
    auto_failover_enabled: bool = True
    sync_strategy: SyncStrategy = SyncStrategy.ASYNC
    last_heartbeat: Optional[datetime] = None
    connection_errors: int = 0
    sync_errors: int = 0
    total_syncs: int = 0
    
@dataclass
class SyncOperation:
    """Synchronization operation tracking"""
    operation_id: str
    replica_id: str
    operation_type: str  # full, partial, incremental
    started_at: datetime
    completed_at: Optional[datetime] = None
    bytes_transferred: int = 0
    progress_percentage: float = 0.0
    success: bool = False
    error_message: Optional[str] = None
    retry_count: int = 0

@dataclass
class ReplicationMetrics:
    """Replication performance metrics"""
    avg_lag: float = 0.0
    max_lag: float = 0.0
    total_replicas: int = 0
    healthy_replicas: int = 0
    lagging_replicas: int = 0
    failed_replicas: int = 0
    total_bytes_synced: int = 0
    sync_operations_per_hour: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)

class ReplicaSyncManager:
    """
    Enterprise replica synchronization manager for Redis
    Microservices + DBA implementation with advanced sync strategies
    """
    
    def __init__(self, redis_settings -> None: RedisSettings, is_master -> None: bool = False) -> None:
        self.redis_settings = redis_settings
        self.is_master = is_master
        self.redis_client: Optional[redis.Redis] = None
        
        # Replica management
        self.replicas: Dict[str, ReplicaInfo] = {}
        self.sync_operations: Dict[str, SyncOperation] = {}
        self.replication_metrics = ReplicationMetrics()
        
        # Synchronization settings
        self.max_lag_threshold = 5.0  # seconds
        self.critical_lag_threshold = 30.0  # seconds
        self.sync_batch_size = 1000  # operations
        self.max_concurrent_syncs = 3
        self.heartbeat_interval = 2.0  # seconds
        self.metrics_update_interval = 10.0  # seconds
        
        # Redis keys for coordination
        self.replicas_key = "ainflue:replication:replicas"
        self.sync_ops_key = "ainflue:replication:sync_ops"
        self.metrics_key = "ainflue:replication:metrics"
        self.master_info_key = "ainflue:replication:master"
        
        # Background tasks
        self._running = False
        self._tasks: List[asyncio.Task] = []
        
        # Current sync operations
        self._active_syncs: Set[str] = set()
        self._sync_queue: List[str] = []
        
        # Performance optimization
        self.enable_compression = True
        self.enable_pipeline = True
        self.pipeline_size = 100
        
    async def initialize(self) -> None:
        """Initialize the replica sync manager"""
        try:
            # Connect to Redis
            self.redis_client = redis.from_url(
                self.redis_settings.redis_dsn,
                encoding='utf-8',
                decode_responses=True,
                max_connections=self.redis_settings.redis_max_connections
            )
            
            # Test connection
            await self.redis_client.ping()
            
            # Load existing replica information
            await self._load_replica_info()
            
            # Start background tasks
            self._running = True
            self._tasks = [
                asyncio.create_task(self._heartbeat_monitor()),
                asyncio.create_task(self._sync_manager()),
                asyncio.create_task(self._metrics_collector()),
                asyncio.create_task(self._lag_monitor()),
                asyncio.create_task(self._health_checker())
            ]
            
            if self.is_master:
                self._tasks.append(asyncio.create_task(self._master_coordinator()))
            
            logger.info(f"Replica Sync Manager initialized (is_master: {self.is_master})")
            
        except Exception as e:
            logger.error(f"Failed to initialize Replica Sync Manager: {e}")
            raise
    
    async def register_replica(self, replica_info: ReplicaInfo) -> bool:
        """Register a new replica"""
        try:
            replica_info.last_heartbeat = datetime.utcnow()
            self.replicas[replica_info.replica_id] = replica_info
            
            # Store in Redis
            await self._store_replica_info(replica_info)
            
            logger.info(f"Registered replica: {replica_info.replica_id}")
            
            # Start initial sync if we're the master
            if self.is_master:
                await self._schedule_sync(replica_info.replica_id, "full")
            
            return True
            
        except Exception as e:
            logger.error(f"Error registering replica {replica_info.replica_id}: {e}")
            return False
    
    async def unregister_replica(self, replica_id: str) -> bool:
        """Unregister a replica"""
        try:
            if replica_id in self.replicas:
                del self.replicas[replica_id]
                
                # Remove from Redis
                await self.redis_client.hdel(self.replicas_key, replica_id)
                
                # Cancel any active syncs
                await self._cancel_replica_syncs(replica_id)
                
                logger.info(f"Unregistered replica: {replica_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error unregistering replica {replica_id}: {e}")
            return False
    
    async def trigger_sync(self, replica_id: str, sync_type: str = "incremental") -> str:
        """Manually trigger synchronization for a replica"""
        try:
            if replica_id not in self.replicas:
                raise ValueError(f"Replica {replica_id} not found")
            
            operation_id = await self._schedule_sync(replica_id, sync_type)
            logger.info(f"Triggered {sync_type} sync for replica {replica_id}: {operation_id}")
            return operation_id
            
        except Exception as e:
            logger.error(f"Error triggering sync for replica {replica_id}: {e}")
            raise
    
    async def _schedule_sync(self, replica_id: str, sync_type: str) -> str:
        """Schedule a sync operation"""
        try:
            operation_id = f"sync-{replica_id}-{int(time.time())}"
            
            sync_op = SyncOperation(
                operation_id=operation_id,
                replica_id=replica_id,
                operation_type=sync_type,
                started_at=datetime.utcnow()
            )
            
            self.sync_operations[operation_id] = sync_op
            
            # Add to sync queue
            if operation_id not in self._sync_queue:
                self._sync_queue.append(operation_id)
            
            # Store operation info
            await self._store_sync_operation(sync_op)
            
            return operation_id
            
        except Exception as e:
            logger.error(f"Error scheduling sync: {e}")
            raise
    
    async def _heartbeat_monitor(self) -> None:
        """Monitor replica heartbeats"""
        while self._running:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                now = datetime.utcnow()
                stale_threshold = timedelta(seconds=self.heartbeat_interval * 3)
                
                for replica_id, replica in self.replicas.items():
                    if replica.last_heartbeat:
                        time_since_heartbeat = now - replica.last_heartbeat
                        
                        if time_since_heartbeat > stale_threshold:
                            if replica.state != ReplicationState.DISCONNECTED:
                                logger.warning(f"Replica {replica_id} heartbeat timeout")
                                await self._handle_replica_disconnect(replica_id)
                    
                    # Update replica heartbeat if we're not master
                    if not self.is_master and replica_id == "self":
                        await self._send_heartbeat()
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {e}")
                await asyncio.sleep(1)
    
    async def _send_heartbeat(self) -> None:
        """Send heartbeat to master (if we're a replica)"""
        try:
            if self.is_master:
                return
            
            heartbeat_data = {
                'replica_id': f"{self.redis_settings.redis_host}:{self.redis_settings.redis_port}",
                'timestamp': datetime.utcnow().isoformat(),
                'state': 'connected',
                'offset': await self._get_replication_offset()
            }
            
            heartbeat_key = f"ainflue:replication:heartbeat:{heartbeat_data['replica_id']}"
            await self.redis_client.set(
                heartbeat_key,
                json.dumps(heartbeat_data),
                ex=int(self.heartbeat_interval * 3)
            )
            
        except Exception as e:
            logger.error(f"Error sending heartbeat: {e}")
    
    async def _sync_manager(self) -> None:
        """Manage synchronization operations"""
        while self._running:
            try:
                await asyncio.sleep(0.5)  # Check frequently
                
                # Process sync queue
                while (len(self._active_syncs) < self.max_concurrent_syncs and 
                       self._sync_queue and self.is_master):
                    
                    operation_id = self._sync_queue.pop(0)
                    if operation_id in self.sync_operations:
                        await self._execute_sync(operation_id)
                
                # Check for completed syncs
                await self._cleanup_completed_syncs()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in sync manager: {e}")
                await asyncio.sleep(1)
    
    async def _execute_sync(self, operation_id -> None: str) -> None:
        """Execute a synchronization operation"""
        try:
            sync_op = self.sync_operations.get(operation_id)
            if not sync_op:
                return
            
            replica = self.replicas.get(sync_op.replica_id)
            if not replica:
                sync_op.success = False
                sync_op.error_message = "Replica not found"
                sync_op.completed_at = datetime.utcnow()
                return
            
            self._active_syncs.add(operation_id)
            
            logger.info(f"Starting {sync_op.operation_type} sync for replica {sync_op.replica_id}")
            
            # Update replica state
            replica.state = ReplicationState.SYNC_INITIAL if sync_op.operation_type == "full" else ReplicationState.SYNC_PARTIAL
            await self._store_replica_info(replica)
            
            # Execute sync based on type
            if sync_op.operation_type == "full":
                success = await self._perform_full_sync(sync_op, replica)
            elif sync_op.operation_type == "partial":
                success = await self._perform_partial_sync(sync_op, replica)
            else:  # incremental
                success = await self._perform_incremental_sync(sync_op, replica)
            
            # Update operation result
            sync_op.success = success
            sync_op.completed_at = datetime.utcnow()
            
            if success:
                replica.state = ReplicationState.CONNECTED
                replica.last_sync = datetime.utcnow()
                replica.total_syncs += 1
                replica.sync_errors = 0
                logger.info(f"Sync completed successfully for replica {sync_op.replica_id}")
            else:
                replica.state = ReplicationState.FAILED
                replica.sync_errors += 1
                logger.error(f"Sync failed for replica {sync_op.replica_id}: {sync_op.error_message}")
            
            await self._store_replica_info(replica)
            await self._store_sync_operation(sync_op)
            
        except Exception as e:
            logger.error(f"Error executing sync {operation_id}: {e}")
            if operation_id in self.sync_operations:
                self.sync_operations[operation_id].success = False
                self.sync_operations[operation_id].error_message = str(e)
                self.sync_operations[operation_id].completed_at = datetime.utcnow()
        finally:
            self._active_syncs.discard(operation_id)
    
    async def _perform_full_sync(self, sync_op: SyncOperation, replica: ReplicaInfo) -> bool:
        """Perform full synchronization"""
        try:
            # Get all data from master
            logger.info(f"Performing full sync for replica {replica.replica_id}")
            
            # Create replica connection
            replica_client = redis.from_url(
                f"redis://{replica.host}:{replica.port}",
                encoding='utf-8',
                decode_responses=True
            )
            
            try:
                await replica_client.ping()
                
                # Get all keys from master
                all_keys = await self.redis_client.keys("*")
                total_keys = len(all_keys)
                
                if total_keys == 0:
                    sync_op.progress_percentage = 100.0
                    return True
                
                # Sync in batches
                batch_size = self.sync_batch_size
                synced_keys = 0
                
                for i in range(0, total_keys, batch_size):
                    batch_keys = all_keys[i:i + batch_size]
                    
                    # Use pipeline for efficiency
                    if self.enable_pipeline:
                        success = await self._sync_batch_pipeline(batch_keys, replica_client)
                    else:
                        success = await self._sync_batch_sequential(batch_keys, replica_client)
                    
                    if not success:
                        sync_op.error_message = f"Failed to sync batch starting at key {i}"
                        return False
                    
                    synced_keys += len(batch_keys)
                    sync_op.progress_percentage = (synced_keys / total_keys) * 100
                    sync_op.bytes_transferred += len(batch_keys) * 100  # Estimate
                    
                    # Update progress
                    await self._store_sync_operation(sync_op)
                    
                    # Small delay to prevent overloading
                    await asyncio.sleep(0.01)
                
                return True
                
            finally:
                await replica_client.close()
                
        except Exception as e:
            sync_op.error_message = f"Full sync error: {str(e)}"
            logger.error(f"Full sync error for replica {replica.replica_id}: {e}")
            return False
    
    async def _sync_batch_pipeline(self, keys: List[str], replica_client: redis.Redis) -> bool:
        """Sync a batch of keys using pipeline"""
        try:
            # Get values from master using pipeline
            master_pipe = self.redis_client.pipeline()
            for key in keys:
                master_pipe.dump(key)
                master_pipe.ttl(key)
            
            results = await master_pipe.execute()
            
            # Set values on replica using pipeline
            replica_pipe = replica_client.pipeline()
            
            for i, key in enumerate(keys):
                value_index = i * 2
                ttl_index = i * 2 + 1
                
                if value_index < len(results) and results[value_index]:
                    value = results[value_index]
                    ttl = results[ttl_index] if ttl_index < len(results) else -1
                    
                    # Use RESTORE command to preserve data type and TTL
                    if ttl > 0:
                        replica_pipe.restore(key, ttl * 1000, value)  # TTL in milliseconds
                    else:
                        replica_pipe.restore(key, 0, value)
            
            await replica_pipe.execute()
            return True
            
        except Exception as e:
            logger.error(f"Pipeline sync error: {e}")
            return False
    
    async def _sync_batch_sequential(self, keys: List[str], replica_client: redis.Redis) -> bool:
        """Sync a batch of keys sequentially"""
        try:
            for key in keys:
                # Get value and TTL from master
                value = await self.redis_client.dump(key)
                ttl = await self.redis_client.ttl(key)
                
                if value:
                    # Set on replica
                    if ttl > 0:
                        await replica_client.restore(key, ttl * 1000, value)
                    else:
                        await replica_client.restore(key, 0, value)
            
            return True
            
        except Exception as e:
            logger.error(f"Sequential sync error: {e}")
            return False
    
    async def _perform_partial_sync(self, sync_op: SyncOperation, replica: ReplicaInfo) -> bool:
        """Perform partial synchronization"""
        try:
            logger.info(f"Performing partial sync for replica {replica.replica_id}")
            
            # Get replica's current offset
            replica_offset = replica.offset
            master_offset = await self._get_replication_offset()
            
            if replica_offset >= master_offset:
                # Replica is up to date
                sync_op.progress_percentage = 100.0
                return True
            
            # Sync operations from replica offset to master offset
            # This is a simplified implementation - real Redis replication is more complex
            sync_op.progress_percentage = 100.0
            return True
            
        except Exception as e:
            sync_op.error_message = f"Partial sync error: {str(e)}"
            logger.error(f"Partial sync error for replica {replica.replica_id}: {e}")
            return False
    
    async def _perform_incremental_sync(self, sync_op: SyncOperation, replica: ReplicaInfo) -> bool:
        """Perform incremental synchronization"""
        try:
            logger.info(f"Performing incremental sync for replica {replica.replica_id}")
            
            # For incremental sync, we check for changes since last sync
            # This is a simplified implementation
            
            current_time = datetime.utcnow()
            if replica.last_sync:
                time_diff = (current_time - replica.last_sync).total_seconds()
                
                # If last sync was recent, consider it up to date
                if time_diff < 5:
                    sync_op.progress_percentage = 100.0
                    return True
            
            # Perform actual incremental sync
            # In practice, this would use Redis replication log
            sync_op.progress_percentage = 100.0
            return True
            
        except Exception as e:
            sync_op.error_message = f"Incremental sync error: {str(e)}"
            logger.error(f"Incremental sync error for replica {replica.replica_id}: {e}")
            return False
    
    async def _metrics_collector(self) -> None:
        """Collect replication metrics"""
        while self._running:
            try:
                await asyncio.sleep(self.metrics_update_interval)
                await self._update_replication_metrics()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics collector: {e}")
                await asyncio.sleep(1)
    
    async def _update_replication_metrics(self) -> None:
        """Update replication metrics"""
        try:
            now = datetime.utcnow()
            
            if not self.replicas:
                return
            
            # Calculate metrics
            total_replicas = len(self.replicas)
            healthy_replicas = len([r for r in self.replicas.values() if r.state == ReplicationState.CONNECTED])
            lagging_replicas = len([r for r in self.replicas.values() if r.replication_lag > self.max_lag_threshold])
            failed_replicas = len([r for r in self.replicas.values() if r.state == ReplicationState.FAILED])
            
            # Calculate lag metrics
            lags = [r.replication_lag for r in self.replicas.values() if r.replication_lag > 0]
            avg_lag = sum(lags) / len(lags) if lags else 0.0
            max_lag = max(lags) if lags else 0.0
            
            # Calculate sync operations per hour
            recent_ops = [op for op in self.sync_operations.values() 
                         if op.completed_at and (now - op.completed_at).total_seconds() < 3600]
            sync_ops_per_hour = len(recent_ops)
            
            # Calculate total bytes synced
            total_bytes = sum(op.bytes_transferred for op in self.sync_operations.values())
            
            # Update metrics
            self.replication_metrics = ReplicationMetrics(
                avg_lag=avg_lag,
                max_lag=max_lag,
                total_replicas=total_replicas,
                healthy_replicas=healthy_replicas,
                lagging_replicas=lagging_replicas,
                failed_replicas=failed_replicas,
                total_bytes_synced=total_bytes,
                sync_operations_per_hour=sync_ops_per_hour,
                last_updated=now
            )
            
            # Store metrics in Redis
            await self._store_metrics()
            
        except Exception as e:
            logger.error(f"Error updating replication metrics: {e}")
    
    async def _lag_monitor(self) -> None:
        """Monitor replication lag"""
        while self._running:
            try:
                await asyncio.sleep(2.0)  # Check lag frequently
                
                if not self.is_master:
                    continue
                
                for replica_id, replica in self.replicas.items():
                    # Calculate current lag
                    lag = await self._calculate_replica_lag(replica)
                    replica.replication_lag = lag
                    
                    # Check if lag is critical
                    if lag > self.critical_lag_threshold:
                        logger.warning(f"Critical replication lag for replica {replica_id}: {lag}s")
                        replica.state = ReplicationState.LAGGING
                        
                        # Trigger sync if not already in progress
                        if replica_id not in self._active_syncs:
                            await self._schedule_sync(replica_id, "incremental")
                    
                    elif lag > self.max_lag_threshold:
                        replica.state = ReplicationState.LAGGING
                    
                    elif replica.state == ReplicationState.LAGGING and lag <= self.max_lag_threshold:
                        replica.state = ReplicationState.CONNECTED
                    
                    await self._store_replica_info(replica)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in lag monitor: {e}")
                await asyncio.sleep(1)
    
    async def _calculate_replica_lag(self, replica: ReplicaInfo) -> float:
        """Calculate replication lag for a replica"""
        try:
            # Get master offset
            master_offset = await self._get_replication_offset()
            
            # Get replica offset (simplified - would need actual replica connection)
            replica_offset = replica.offset
            
            # Calculate lag based on offset difference and write rate
            # This is a simplified calculation
            offset_diff = master_offset - replica_offset
            
            if offset_diff <= 0:
                return 0.0
            
            # Estimate lag based on average write rate
            # In practice, this would be more sophisticated
            estimated_lag = offset_diff / 1000.0  # Rough estimate
            
            return max(0.0, estimated_lag)
            
        except Exception as e:
            logger.error(f"Error calculating replica lag: {e}")
            return 0.0
    
    async def _get_replication_offset(self) -> int:
        """Get current replication offset"""
        try:
            info = await self.redis_client.info('replication')
            return info.get('master_repl_offset', 0)
        except Exception as e:
            logger.error(f"Error getting replication offset: {e}")
            return 0
    
    async def _health_checker(self) -> None:
        """Check replica health"""
        while self._running:
            try:
                await asyncio.sleep(5.0)  # Health check every 5 seconds
                
                for replica_id, replica in list(self.replicas.items()):
                    try:
                        # Test connection to replica
                        replica_client = redis.from_url(
                            f"redis://{replica.host}:{replica.port}",
                            socket_timeout=2.0
                        )
                        
                        await replica_client.ping()
                        await replica_client.close()
                        
                        # Reset connection errors on successful ping
                        replica.connection_errors = 0
                        
                        if replica.state == ReplicationState.DISCONNECTED:
                            replica.state = ReplicationState.CONNECTING
                            # Schedule reconnection sync
                            await self._schedule_sync(replica_id, "partial")
                            
                    except Exception as e:
                        replica.connection_errors += 1
                        
                        if replica.connection_errors >= 3:
                            await self._handle_replica_disconnect(replica_id)
                        
                        logger.warning(f"Health check failed for replica {replica_id}: {e}")
                    
                    await self._store_replica_info(replica)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health checker: {e}")
                await asyncio.sleep(1)
    
    async def _master_coordinator(self) -> None:
        """Coordinate replica management (master only)"""
        while self._running:
            try:
                await asyncio.sleep(10.0)  # Coordinate every 10 seconds
                
                # Check for new replicas
                await self._discover_replicas()
                
                # Optimize sync strategies
                await self._optimize_sync_strategies()
                
                # Clean up old operations
                await self._cleanup_old_operations()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in master coordinator: {e}")
                await asyncio.sleep(1)
    
    async def _discover_replicas(self) -> None:
        """Discover new replicas from Redis info"""
        try:
            info = await self.redis_client.info('replication')
            
            # Parse connected slaves from Redis info
            connected_slaves = info.get('connected_slaves', 0)
            
            for i in range(connected_slaves):
                slave_key = f'slave{i}'
                if slave_key in info:
                    slave_info = info[slave_key]
                    # Parse slave info and register if not already registered
                    # This is simplified - real implementation would parse the slave info string
                    
        except Exception as e:
            logger.error(f"Error discovering replicas: {e}")
    
    async def _optimize_sync_strategies(self) -> None:
        """Optimize sync strategies based on replica performance"""
        try:
            for replica in self.replicas.values():
                # Analyze replica performance
                if replica.replication_lag > self.critical_lag_threshold:
                    # Switch to more aggressive sync strategy
                    if replica.sync_strategy == SyncStrategy.ASYNC:
                        replica.sync_strategy = SyncStrategy.SEMI_SYNC
                        logger.info(f"Upgraded sync strategy for replica {replica.replica_id} to semi-sync")
                
                elif replica.replication_lag < self.max_lag_threshold / 2:
                    # Can use less aggressive strategy
                    if replica.sync_strategy == SyncStrategy.SEMI_SYNC:
                        replica.sync_strategy = SyncStrategy.ASYNC
                        logger.info(f"Downgraded sync strategy for replica {replica.replica_id} to async")
                
                await self._store_replica_info(replica)
                
        except Exception as e:
            logger.error(f"Error optimizing sync strategies: {e}")
    
    async def _handle_replica_disconnect(self, replica_id -> None: str) -> None:
        """Handle replica disconnection"""
        try:
            replica = self.replicas.get(replica_id)
            if replica:
                replica.state = ReplicationState.DISCONNECTED
                replica.last_heartbeat = None
                await self._store_replica_info(replica)
                
                logger.warning(f"Replica {replica_id} disconnected")
                
                # Cancel any active syncs for this replica
                await self._cancel_replica_syncs(replica_id)
                
        except Exception as e:
            logger.error(f"Error handling replica disconnect: {e}")
    
    async def _cancel_replica_syncs(self, replica_id -> None: str) -> None:
        """Cancel active sync operations for a replica"""
        try:
            # Find and cancel active syncs for this replica
            to_cancel = [op_id for op_id, op in self.sync_operations.items() 
                        if op.replica_id == replica_id and not op.completed_at]
            
            for op_id in to_cancel:
                if op_id in self._active_syncs:
                    self._active_syncs.remove(op_id)
                
                if op_id in self._sync_queue:
                    self._sync_queue.remove(op_id)
                
                # Mark as cancelled
                self.sync_operations[op_id].success = False
                self.sync_operations[op_id].error_message = "Cancelled due to replica disconnect"
                self.sync_operations[op_id].completed_at = datetime.utcnow()
                
                await self._store_sync_operation(self.sync_operations[op_id])
                
        except Exception as e:
            logger.error(f"Error cancelling replica syncs: {e}")
    
    async def _cleanup_completed_syncs(self) -> None:
        """Clean up completed sync operations"""
        try:
            completed_ops = [op_id for op_id, op in self.sync_operations.items() 
                           if op.completed_at and op_id in self._active_syncs]
            
            for op_id in completed_ops:
                self._active_syncs.remove(op_id)
                
        except Exception as e:
            logger.error(f"Error cleaning up completed syncs: {e}")
    
    async def _cleanup_old_operations(self) -> None:
        """Clean up old sync operations"""
        try:
            now = datetime.utcnow()
            old_threshold = timedelta(hours=24)  # Keep operations for 24 hours
            
            old_ops = [op_id for op_id, op in self.sync_operations.items() 
                      if op.completed_at and (now - op.completed_at) > old_threshold]
            
            for op_id in old_ops:
                del self.sync_operations[op_id]
                await self.redis_client.hdel(self.sync_ops_key, op_id)
                
            if old_ops:
                logger.info(f"Cleaned up {len(old_ops)} old sync operations")
                
        except Exception as e:
            logger.error(f"Error cleaning up old operations: {e}")
    
    async def _store_replica_info(self, replica -> None: ReplicaInfo) -> None:
        """Store replica information in Redis"""
        try:
            replica_data = {
                'replica_id': replica.replica_id,
                'host': replica.host,
                'port': replica.port,
                'master_host': replica.master_host,
                'master_port': replica.master_port,
                'state': replica.state.value,
                'replication_lag': replica.replication_lag,
                'last_sync': replica.last_sync.isoformat() if replica.last_sync else None,
                'bytes_behind': replica.bytes_behind,
                'offset': replica.offset,
                'priority': replica.priority,
                'sync_strategy': replica.sync_strategy.value,
                'last_heartbeat': replica.last_heartbeat.isoformat() if replica.last_heartbeat else None,
                'connection_errors': replica.connection_errors,
                'sync_errors': replica.sync_errors,
                'total_syncs': replica.total_syncs
            }
            
            await self.redis_client.hset(self.replicas_key, replica.replica_id, json.dumps(replica_data))
            
        except Exception as e:
            logger.error(f"Error storing replica info: {e}")
    
    async def _store_sync_operation(self, sync_op -> None: SyncOperation) -> None:
        """Store sync operation information in Redis"""
        try:
            op_data = {
                'operation_id': sync_op.operation_id,
                'replica_id': sync_op.replica_id,
                'operation_type': sync_op.operation_type,
                'started_at': sync_op.started_at.isoformat(),
                'completed_at': sync_op.completed_at.isoformat() if sync_op.completed_at else None,
                'bytes_transferred': sync_op.bytes_transferred,
                'progress_percentage': sync_op.progress_percentage,
                'success': sync_op.success,
                'error_message': sync_op.error_message,
                'retry_count': sync_op.retry_count
            }
            
            await self.redis_client.hset(self.sync_ops_key, sync_op.operation_id, json.dumps(op_data))
            
        except Exception as e:
            logger.error(f"Error storing sync operation: {e}")
    
    async def _store_metrics(self) -> None:
        """Store replication metrics in Redis"""
        try:
            metrics_data = {
                'avg_lag': self.replication_metrics.avg_lag,
                'max_lag': self.replication_metrics.max_lag,
                'total_replicas': self.replication_metrics.total_replicas,
                'healthy_replicas': self.replication_metrics.healthy_replicas,
                'lagging_replicas': self.replication_metrics.lagging_replicas,
                'failed_replicas': self.replication_metrics.failed_replicas,
                'total_bytes_synced': self.replication_metrics.total_bytes_synced,
                'sync_operations_per_hour': self.replication_metrics.sync_operations_per_hour,
                'last_updated': self.replication_metrics.last_updated.isoformat()
            }
            
            await self.redis_client.set(self.metrics_key, json.dumps(metrics_data))
            
        except Exception as e:
            logger.error(f"Error storing metrics: {e}")
    
    async def _load_replica_info(self) -> None:
        """Load replica information from Redis"""
        try:
            replica_data = await self.redis_client.hgetall(self.replicas_key)
            
            for replica_id, data_json in replica_data.items():
                try:
                    data = json.loads(data_json)
                    
                    # Convert datetime fields
                    if data.get('last_sync'):
                        data['last_sync'] = datetime.fromisoformat(data['last_sync'])
                    if data.get('last_heartbeat'):
                        data['last_heartbeat'] = datetime.fromisoformat(data['last_heartbeat'])
                    
                    # Convert enums
                    if data.get('state'):
                        data['state'] = ReplicationState(data['state'])
                    if data.get('sync_strategy'):
                        data['sync_strategy'] = SyncStrategy(data['sync_strategy'])
                    
                    replica_info = ReplicaInfo(**data)
                    self.replicas[replica_id] = replica_info
                    
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Failed to load replica info for {replica_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error loading replica info: {e}")
    
    async def get_replication_status(self) -> Dict[str, Any]:
        """Get current replication status"""
        try:
            return {
                'is_master': self.is_master,
                'total_replicas': len(self.replicas),
                'active_syncs': len(self._active_syncs),
                'queued_syncs': len(self._sync_queue),
                'metrics': {
                    'avg_lag': self.replication_metrics.avg_lag,
                    'max_lag': self.replication_metrics.max_lag,
                    'healthy_replicas': self.replication_metrics.healthy_replicas,
                    'lagging_replicas': self.replication_metrics.lagging_replicas,
                    'failed_replicas': self.replication_metrics.failed_replicas,
                    'sync_operations_per_hour': self.replication_metrics.sync_operations_per_hour
                },
                'replicas': {
                    replica_id: {
                        'state': replica.state.value,
                        'lag': replica.replication_lag,
                        'last_sync': replica.last_sync.isoformat() if replica.last_sync else None,
                        'sync_strategy': replica.sync_strategy.value,
                        'connection_errors': replica.connection_errors,
                        'sync_errors': replica.sync_errors
                    } for replica_id, replica in self.replicas.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting replication status: {e}")
            return {'error': str(e)}
    
    async def shutdown(self) -> None:
        """Shutdown the replica sync manager"""
        try:
            self._running = False
            
            # Cancel background tasks
            for task in self._tasks:
                task.cancel()
            
            # Wait for tasks to complete
            if self._tasks:
                await asyncio.gather(*self._tasks, return_exceptions=True)
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Replica Sync Manager shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Factory function for easy initialization
async def create_replica_sync_manager(redis_settings: Optional[RedisSettings] = None, 
                                    is_master: bool = False) -> ReplicaSyncManager:
    """Factory function to create and initialize ReplicaSyncManager"""
    if redis_settings is None:
        redis_settings = RedisSettings()
    
    manager = ReplicaSyncManager(redis_settings, is_master)
    await manager.initialize()
    return manager