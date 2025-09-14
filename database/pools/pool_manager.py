"""
Pool Manager module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""Database Pool Manager - Central Orchestration System
========================================================

Central orchestration and coordination for all database connection pools
in the IA Influencer Agent + Content Protection Platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import json
import weakref

logger = logging.getLogger(__name__)

class PoolType(Enum):
    """Database pool types"""
    POSTGRESQL = "postgresql"
    REDIS = "redis"
    MONGODB = "mongodb"
    ELASTICSEARCH = "elasticsearch"
    VECTOR_STORE = "vector_store"
    CACHE = "cache"

class PoolStatus(Enum):
    """Pool status enumeration"""
    INITIALIZING = "initializing"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    SHUTDOWN = "shutdown"

@dataclass
class PoolStats:
    """Pool statistics and metrics"""
    active_connections: int = 0
    idle_connections: int = 0
    total_connections: int = 0
    failed_connections: int = 0
    avg_response_time: float = 0.0
    status: PoolStatus = PoolStatus.INITIALIZING
    last_health_check: Optional[datetime] = None
    errors: List[str] = field(default_factory=list)

class DatabasePoolManager:
    """Central database pool manager and orchestrator"""
    
    def __init__(self) -> None:
        self.pools: Dict[PoolType, Any] = {}
        self.pool_configs: Dict[PoolType, Any] = {}
        self.pool_stats: Dict[PoolType, PoolStats] = {}
        self._monitoring_task: Optional[asyncio.Task] = None
        self._initialized = False
        self._shutdown = False
        
        # Health check configuration
        self.health_check_interval = 30.0  # seconds
        self.max_failed_health_checks = 3
        
        logger.info("🏊 Database Pool Manager initialized")

    async def initialize_pool(
        self, 
        pool_type: PoolType, 
        config: Dict[str, Any],
        connection_params: Dict[str, Any]
    ) -> bool:
        """Initialize a specific database pool"""
        try:
            logger.info(f"🔧 Initializing {pool_type.value} pool...")
            
            # Store configuration
            self.pool_configs[pool_type] = {
                'config': config,
                'connection_params': connection_params,
                'created_at': datetime.now(timezone.utc)
            }
            
            # Initialize stats
            self.pool_stats[pool_type] = PoolStats()
            
            # Mock pool implementation - in real implementation, this would create actual pools
            mock_pool = {
                'type': pool_type,
                'status': PoolStatus.HEALTHY,
                'connections': [],
                'created_at': datetime.now(timezone.utc)
            }
            
            self.pools[pool_type] = mock_pool
            self.pool_stats[pool_type].status = PoolStatus.HEALTHY
            self.pool_stats[pool_type].last_health_check = datetime.now(timezone.utc)
            
            logger.info(f"✅ {pool_type.value} pool initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {pool_type.value} pool: {e}")
            if pool_type in self.pool_stats:
                self.pool_stats[pool_type].status = PoolStatus.UNHEALTHY
                self.pool_stats[pool_type].errors.append(str(e))
            return False

    async def get_pool(self, pool_type: PoolType) -> Optional[Any]:
        """Get a specific pool instance"""
        if not self._initialized:
            logger.warning("Pool manager not initialized")
            return None
            
        pool = self.pools.get(pool_type)
        if not pool:
            logger.warning(f"Pool {pool_type.value} not found")
            return None
            
        return pool

    @asynccontextmanager
    async def get_connection(self, pool_type -> None: PoolType) -> None:
        """Get a connection from the specified pool"""
        pool = await self.get_pool(pool_type)
        if not pool:
            raise RuntimeError(f"Pool {pool_type.value} not available")
        
        # Mock connection - in real implementation, this would get from actual pool
        connection = {
            'pool_type': pool_type,
            'acquired_at': datetime.now(timezone.utc),
            'connection_id': f"conn_{pool_type.value}_{id(self)}"
        }
        
        try:
            # Update stats
            if pool_type in self.pool_stats:
                self.pool_stats[pool_type].active_connections += 1
                self.pool_stats[pool_type].total_connections += 1
            
            logger.debug(f"🔗 Connection acquired from {pool_type.value} pool")
            yield connection
            
        except Exception as e:
            logger.error(f"❌ Connection error in {pool_type.value} pool: {e}")
            if pool_type in self.pool_stats:
                self.pool_stats[pool_type].failed_connections += 1
                self.pool_stats[pool_type].errors.append(str(e))
            raise
        finally:
            # Update stats
            if pool_type in self.pool_stats:
                self.pool_stats[pool_type].active_connections -= 1
            
            logger.debug(f"🔌 Connection released to {pool_type.value} pool")

    async def health_check_all(self) -> Dict[PoolType, bool]:
        """Perform health check on all pools"""
        results = {}
        
        for pool_type, pool in self.pools.items():
            try:
                # Mock health check - in real implementation, would ping database
                is_healthy = pool.get('status') == PoolStatus.HEALTHY
                
                if pool_type in self.pool_stats:
                    self.pool_stats[pool_type].last_health_check = datetime.now(timezone.utc)
                    if is_healthy:
                        self.pool_stats[pool_type].status = PoolStatus.HEALTHY
                    else:
                        self.pool_stats[pool_type].status = PoolStatus.UNHEALTHY
                
                results[pool_type] = is_healthy
                logger.debug(f"🏥 Health check {pool_type.value}: {'✅' if is_healthy else '❌'}")
                
            except Exception as e:
                logger.error(f"🔥 Health check failed for {pool_type.value}: {e}")
                results[pool_type] = False
                if pool_type in self.pool_stats:
                    self.pool_stats[pool_type].status = PoolStatus.UNHEALTHY
                    self.pool_stats[pool_type].errors.append(str(e))
        
        return results

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all pools"""
        stats = {}
        
        for pool_type, pool_stats in self.pool_stats.items():
            stats[pool_type.value] = {
                'state': pool_stats.status.value,
                'database_type': pool_type.value,
                'active_connections': pool_stats.active_connections,
                'idle_connections': pool_stats.idle_connections,
                'total_connections': pool_stats.total_connections,
                'failed_connections': pool_stats.failed_connections,
                'avg_response_time': pool_stats.avg_response_time,
                'last_health_check': pool_stats.last_health_check.isoformat() if pool_stats.last_health_check else None,
                'error_count': len(pool_stats.errors)
            }
        
        return stats

    async def start_monitoring(self) -> None:
        """Start global pool monitoring"""
        if self._monitoring_task and not self._monitoring_task.done():
            logger.warning("Monitoring already running")
            return
            
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("📊 Global pool monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop global pool monitoring"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            self._monitoring_task = None
            logger.info("📊 Global pool monitoring stopped")

    async def _monitoring_loop(self) -> None:
        """Internal monitoring loop"""
        while not self._shutdown:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                # Perform health checks
                health_results = await self.health_check_all()
                
                # Log unhealthy pools
                unhealthy_pools = [
                    pool_type.value for pool_type, is_healthy 
                    in health_results.items() if not is_healthy
                ]
                
                if unhealthy_pools:
                    logger.warning(f"⚠️ Unhealthy pools detected: {unhealthy_pools}")
                
                # Update pool statistics
                await self._update_pool_statistics()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Monitoring loop error: {e}")

    async def _update_pool_statistics(self) -> None:
        """Update pool statistics"""
        for pool_type, pool in self.pools.items():
            if pool_type in self.pool_stats:
                # Mock statistics update - in real implementation, would gather from actual pools
                stats = self.pool_stats[pool_type]
                stats.idle_connections = max(0, stats.total_connections - stats.active_connections)

    async def shutdown(self) -> None:
        """Shutdown all pools gracefully"""
        logger.info("🛑 Shutting down all database pools...")
        self._shutdown = True
        
        # Stop monitoring
        await self.stop_monitoring()
        
        # Shutdown pools
        for pool_type, pool in self.pools.items():
            try:
                logger.info(f"🛑 Shutting down {pool_type.value} pool...")
                # In real implementation, would call pool.close()
                if pool_type in self.pool_stats:
                    self.pool_stats[pool_type].status = PoolStatus.SHUTDOWN
                
            except Exception as e:
                logger.error(f"❌ Error shutting down {pool_type.value} pool: {e}")
        
        self.pools.clear()
        logger.info("✅ All pools shutdown complete")

    def is_healthy(self) -> bool:
        """Check if all pools are healthy"""
        if not self.pools:
            return False
            
        return all(
            stats.status == PoolStatus.HEALTHY 
            for stats in self.pool_stats.values()
        )

    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive manager summary"""
        return {
            'initialized': self._initialized,
            'total_pools': len(self.pools),
            'healthy_pools': sum(
                1 for stats in self.pool_stats.values() 
                if stats.status == PoolStatus.HEALTHY
            ),
            'monitoring_active': self._monitoring_task is not None and not self._monitoring_task.done(),
            'pool_types': [pool_type.value for pool_type in self.pools.keys()],
            'overall_health': self.is_healthy()
        }

# Global pool manager instance
_pool_manager: Optional[DatabasePoolManager] = None

def get_pool_manager() -> DatabasePoolManager:
    """Get the global database pool manager"""
    global _pool_manager
    if _pool_manager is None:
        _pool_manager = DatabasePoolManager()
    return _pool_manager

async def initialize_all_pools(
    config_dir: str = "config/pools", 
    master_key: str = "demo-key",
    **kwargs
) -> bool:
    """Initialize all configured database pools"""
    pool_manager = get_pool_manager()
    
    try:
        logger.info(f"🚀 Initializing pools from {config_dir}...")
        
        # Mock configuration for demo purposes
        pool_configs = {
            PoolType.POSTGRESQL: {
                'host': 'localhost',
                'port': 5432,
                'database': 'ainflue',
                'min_connections': 5,
                'max_connections': 50
            },
            PoolType.REDIS: {
                'host': 'localhost', 
                'port': 6379,
                'db': 0,
                'min_connections': 3,
                'max_connections': 20
            },
            PoolType.MONGODB: {
                'host': 'localhost',
                'port': 27017,
                'database': 'ainflue',
                'min_connections': 3,
                'max_connections': 30
            }
        }
        
        # Initialize each pool
        success_count = 0
        for pool_type, config in pool_configs.items():
            connection_params = {'url': f'{pool_type.value}://localhost'}
            success = await pool_manager.initialize_pool(pool_type, config, connection_params)
            if success:
                success_count += 1
        
        pool_manager._initialized = True
        
        # Start monitoring
        await pool_manager.start_monitoring()
        
        logger.info(f"✅ Initialized {success_count}/{len(pool_configs)} pools successfully")
        return success_count > 0
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize pools: {e}")
        return False

# Export public interface
__all__ = [
    'DatabasePoolManager',
    'get_pool_manager', 
    'initialize_all_pools',
    'PoolType',
    'PoolStatus',
    'PoolStats'
]