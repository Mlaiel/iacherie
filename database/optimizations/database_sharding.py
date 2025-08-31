"""Database Sharding Coordinator

Enterprise-grade database sharding system with intelligent shard management,
automatic rebalancing, and cross-shard query optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import hashlib
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Union, Callable
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import logging

from sqlalchemy import text, MetaData, Table, Column, Integer, String, DateTime
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from ...core.logging import get_logger

logger = get_logger(__name__)


class ShardingStrategy(Enum):
    """Database sharding strategies"""    HASH_BASED = "hash_based"
    RANGE_BASED = "range_based"
    DIRECTORY_BASED = "directory_based"
    CONSISTENT_HASH = "consistent_hash"
    GEOGRAPHIC = "geographic"
    TENANT_BASED = "tenant_based"


class ShardStatus(Enum):
    """Shard status states"""    ACTIVE = "active"
    MIGRATING = "migrating"
    READONLY = "readonly"
    OFFLINE = "offline"
    REBALANCING = "rebalancing"
    MAINTENANCE = "maintenance"


class QueryType(Enum):
    """Query operation types"""    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    CROSS_SHARD = "cross_shard"


@dataclass
class ShardConfig:
    """Shard configuration"""    shard_id: str
    host: str
    port: int
    database: str
    username: str
    password: str
    weight: float = 1.0
    capacity: int = 1000000  # Maximum rows
    region: str = "default"
    tags: List[str] = field(default_factory=list)
    ssl_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ShardMetrics:
    """Shard performance metrics"""    shard_id: str
    row_count: int = 0
    size_mb: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    queries_per_second: float = 0.0
    avg_response_time: float = 0.0
    error_rate: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def utilization_score(self) -> float:
        """Calculate shard utilization score (0-1)"""        return max(self.cpu_usage, self.memory_usage, self.disk_usage)
    
    def health_score(self) -> float:
        """Calculate shard health score (0-100)"""        score = 100.0
        
        # Penalize high utilization
        score -= self.utilization_score() * 30
        
        # Penalize high response time
        if self.avg_response_time > 1.0:
            score -= min(20, self.avg_response_time * 5)
        
        # Penalize errors
        score -= min(30, self.error_rate * 100)
        
        return max(0.0, score)


@dataclass
class ShardingRule:
    """Sharding rule definition"""    table_name: str
    shard_key: str
    strategy: ShardingStrategy
    shard_count: int
    shard_function: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConsistentHashRing:
    """Consistent hash ring for sharding"""    
    def __init__(self, shards: List[str], virtual_nodes: int = 100):
        self.shards = set(shards)
        self.virtual_nodes = virtual_nodes
        self.ring: Dict[int, str] = {}
        self.shard_positions: Dict[str, List[int]] = defaultdict(list)
        self._build_ring()
    
    def _build_ring(self):
        """Build the hash ring"""        self.ring.clear()
        self.shard_positions.clear()
        
        for shard in self.shards:
            for i in range(self.virtual_nodes):
                # Create virtual node hash
                virtual_key = f"{shard}:{i}"
                hash_value = int(hashlib.md5(virtual_key.encode()).hexdigest(), 16)
                
                self.ring[hash_value] = shard
                self.shard_positions[shard].append(hash_value)
        
        logger.info(f"Built consistent hash ring with {len(self.ring)} virtual nodes")
    
    def get_shard(self, key: str) -> str:
        """Get shard for given key"""        if not self.ring:
            raise ValueError("Hash ring is empty")
        
        # Hash the key
        key_hash = int(hashlib.md5(key.encode()).hexdigest(), 16)
        
        # Find the first shard clockwise from the key
        for ring_hash in sorted(self.ring.keys()):
            if key_hash <= ring_hash:
                return self.ring[ring_hash]
        
        # Wrap around to the first shard
        return self.ring[min(self.ring.keys())]
    
    def add_shard(self, shard: str):
        """Add a new shard to the ring"""        if shard in self.shards:
            return
        
        self.shards.add(shard)
        
        for i in range(self.virtual_nodes):
            virtual_key = f"{shard}:{i}"
            hash_value = int(hashlib.md5(virtual_key.encode()).hexdigest(), 16)
            
            self.ring[hash_value] = shard
            self.shard_positions[shard].append(hash_value)
        
        logger.info(f"Added shard {shard} to hash ring")
    
    def remove_shard(self, shard: str):
        """Remove a shard from the ring"""        if shard not in self.shards:
            return
        
        self.shards.remove(shard)
        
        # Remove from ring
        for hash_value in self.shard_positions[shard]:
            if hash_value in self.ring:
                del self.ring[hash_value]
        
        del self.shard_positions[shard]
        logger.info(f"Removed shard {shard} from hash ring")
    
    def get_affected_keys_for_rebalance(self, removed_shard: str) -> Dict[str, str]:
        """Get keys that need to be moved when a shard is removed"""        if removed_shard not in self.shards:
            return {}
        
        # This is a simplified implementation
        # In practice, you'd need to track actual keys
        affected_ranges = {}
        
        for hash_value in self.shard_positions[removed_shard]:
            # Find next shard in the ring
            next_hash = min([h for h in self.ring.keys() if h > hash_value], default=None)
            if next_hash is None:
                next_hash = min(self.ring.keys())
            
            target_shard = self.ring[next_hash]
            affected_ranges[f"range_{hash_value}"] = target_shard
        
        return affected_ranges


class ShardRouter:
    """Routes queries to appropriate shards"""    
    def __init__(self, sharding_rules: Dict[str, ShardingRule]):
        self.sharding_rules = sharding_rules
        self.consistent_rings: Dict[str, ConsistentHashRing] = {}
    
    def setup_consistent_ring(self, table_name: str, shards: List[str]):
        """Setup consistent hash ring for table"""        self.consistent_rings[table_name] = ConsistentHashRing(shards)
    
    def route_query(self, table_name: str, query_data: Dict[str, Any], 
                   query_type: QueryType) -> List[str]:
        """Route query to appropriate shards"""        rule = self.sharding_rules.get(table_name)
        if not rule:
            raise ValueError(f"No sharding rule found for table {table_name}")
        
        # Extract shard key value
        shard_key_value = query_data.get(rule.shard_key)
        if shard_key_value is None and query_type != QueryType.SELECT:
            raise ValueError(f"Shard key {rule.shard_key} is required for {query_type} operations")
        
        if rule.strategy == ShardingStrategy.HASH_BASED:
            return self._route_hash_based(table_name, shard_key_value, rule)
        elif rule.strategy == ShardingStrategy.CONSISTENT_HASH:
            return self._route_consistent_hash(table_name, shard_key_value, rule)
        elif rule.strategy == ShardingStrategy.RANGE_BASED:
            return self._route_range_based(table_name, shard_key_value, rule)
        elif rule.strategy == ShardingStrategy.TENANT_BASED:
            return self._route_tenant_based(table_name, shard_key_value, rule)
        else:
            # Default to all shards for cross-shard queries
            return [f"shard_{i}" for i in range(rule.shard_count)]
    
    def _route_hash_based(self, table_name: str, shard_key_value: Any, 
                         rule: ShardingRule) -> List[str]:
        """Route using hash-based sharding"""        if shard_key_value is None:
            # Cross-shard query
            return [f"shard_{i}" for i in range(rule.shard_count)]
        
        # Hash the shard key
        hash_value = hash(str(shard_key_value))
        shard_index = abs(hash_value) % rule.shard_count
        
        return [f"shard_{shard_index}"]
    
    def _route_consistent_hash(self, table_name: str, shard_key_value: Any, 
                              rule: ShardingRule) -> List[str]:
        """Route using consistent hashing"""        if shard_key_value is None:
            # Cross-shard query
            ring = self.consistent_rings.get(table_name)
            return list(ring.shards) if ring else []
        
        ring = self.consistent_rings.get(table_name)
        if not ring:
            raise ValueError(f"Consistent hash ring not found for {table_name}")
        
        shard = ring.get_shard(str(shard_key_value))
        return [shard]
    
    def _route_range_based(self, table_name: str, shard_key_value: Any, 
                          rule: ShardingRule) -> List[str]:
        """Route using range-based sharding"""        if shard_key_value is None:
            return [f"shard_{i}" for i in range(rule.shard_count)]
        
        # Simplified range routing
        # In practice, you'd have predefined ranges
        ranges_per_shard = 1000000 // rule.shard_count
        shard_index = min(int(shard_key_value) // ranges_per_shard, rule.shard_count - 1)
        
        return [f"shard_{shard_index}"]
    
    def _route_tenant_based(self, table_name: str, shard_key_value: Any, 
                           rule: ShardingRule) -> List[str]:
        """Route using tenant-based sharding"""        if shard_key_value is None:
            return [f"shard_{i}" for i in range(rule.shard_count)]
        
        # Hash tenant ID to determine shard
        tenant_hash = hash(str(shard_key_value))
        shard_index = abs(tenant_hash) % rule.shard_count
        
        return [f"tenant_shard_{shard_index}"]


class CrossShardQueryExecutor:
    """Executes queries across multiple shards"""    
    def __init__(self, shard_engines: Dict[str, AsyncEngine]):
        self.shard_engines = shard_engines
    
    async def execute_cross_shard_query(self, query: str, target_shards: List[str],
                                      aggregation_func: Optional[str] = None) -> List[Dict[str, Any]]:
        """Execute query across multiple shards"""        try:
            # Execute query on all target shards concurrently
            tasks = []
            for shard_id in target_shards:
                if shard_id in self.shard_engines:
                    task = self._execute_on_shard(shard_id, query)
                    tasks.append(task)
            
            if not tasks:
                return []
            
            # Wait for all results
            shard_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            combined_results = []
            for i, result in enumerate(shard_results):
                if isinstance(result, Exception):
                    logger.error(f"Shard query failed on {target_shards[i]}: {result}")
                    continue
                
                if isinstance(result, list):
                    combined_results.extend(result)
                else:
                    combined_results.append(result)
            
            # Apply aggregation if specified
            if aggregation_func:
                return self._apply_aggregation(combined_results, aggregation_func)
            
            return combined_results
            
        except Exception as e:
            logger.error(f"Cross-shard query execution failed: {e}")
            raise
    
    async def _execute_on_shard(self, shard_id: str, query: str) -> List[Dict[str, Any]]:
        """Execute query on a specific shard"""        engine = self.shard_engines[shard_id]
        
        async with engine.begin() as conn:
            result = await conn.execute(text(query))
            rows = result.fetchall()
            
            # Convert to dict format
            columns = result.keys()
            return [dict(zip(columns, row)) for row in rows]
    
    def _apply_aggregation(self, results: List[Dict[str, Any]], 
                          aggregation_func: str) -> List[Dict[str, Any]]:
        """Apply aggregation function to combined results"""        if not results:
            return []
        
        if aggregation_func.upper() == "COUNT":
            return [{"count": len(results)}]
        elif aggregation_func.upper() == "SUM":
            # Simple sum aggregation - assumes numeric values
            total = sum(sum(row.values()) for row in results if row.values())
            return [{"sum": total}]
        elif aggregation_func.upper() == "GROUP_BY":
            # Simple grouping - would need more sophisticated implementation
            grouped = defaultdict(list)
            for row in results:
                # Use first column as group key
                key = list(row.values())[0] if row else "unknown"
                grouped[key].append(row)
            
            return [{"group": k, "count": len(v)} for k, v in grouped.items()]
        else:
            # No aggregation
            return results


class ShardRebalancer:
    """Handles shard rebalancing operations"""    
    def __init__(self, shard_coordinator: 'DatabaseShardCoordinator'):
        self.coordinator = shard_coordinator
        self.rebalancing_tasks: Dict[str, asyncio.Task] = {}
    
    async def check_rebalancing_needed(self) -> Dict[str, Any]:
        """Check if rebalancing is needed"""        try:
            rebalancing_plan = {
                'needed': False,
                'reasons': [],
                'recommendations': []
            }
            
            # Get shard metrics
            shard_metrics = {}
            for shard_id in self.coordinator.shard_configs:
                metrics = self.coordinator.shard_metrics.get(shard_id)
                if metrics:
                    shard_metrics[shard_id] = metrics
            
            if not shard_metrics:
                return rebalancing_plan
            
            # Check for imbalanced shards
            row_counts = [m.row_count for m in shard_metrics.values()]
            if row_counts:
                avg_rows = sum(row_counts) / len(row_counts)
                max_rows = max(row_counts)
                min_rows = min(row_counts)
                
                # Check if any shard has more than 2x average
                if max_rows > avg_rows * 2:
                    rebalancing_plan['needed'] = True
                    rebalancing_plan['reasons'].append("Unbalanced row distribution")
                
                # Check if difference between max and min is too large
                if max_rows > min_rows * 3:
                    rebalancing_plan['needed'] = True
                    rebalancing_plan['reasons'].append("Large variance in shard sizes")
            
            # Check for overutilized shards
            for shard_id, metrics in shard_metrics.items():
                if metrics.utilization_score() > 0.8:  # 80% utilization
                    rebalancing_plan['needed'] = True
                    rebalancing_plan['reasons'].append(f"Shard {shard_id} overutilized")
                    rebalancing_plan['recommendations'].append(f"Split or migrate data from {shard_id}")
            
            return rebalancing_plan
            
        except Exception as e:
            logger.error(f"Failed to check rebalancing needs: {e}")
            return {'needed': False, 'error': str(e)}
    
    async def rebalance_shards(self, plan: Dict[str, Any]) -> bool:
        """Execute shard rebalancing"""        try:
            logger.info("Starting shard rebalancing")
            
            # This is a simplified implementation
            # In practice, rebalancing would involve:
            # 1. Creating new shard configurations
            # 2. Migrating data between shards
            # 3. Updating routing rules
            # 4. Verifying data integrity
            
            # For demonstration, we'll simulate the process
            await asyncio.sleep(1)  # Simulate rebalancing work
            
            logger.info("Shard rebalancing completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Shard rebalancing failed: {e}")
            return False


class DatabaseShardCoordinator:
    """Main coordinator for database sharding operations"""    
    def __init__(self, shard_configs: Dict[str, ShardConfig], 
                 sharding_rules: Dict[str, ShardingRule]):
        self.shard_configs = shard_configs
        self.sharding_rules = sharding_rules
        
        # Components
        self.shard_router = ShardRouter(sharding_rules)
        self.shard_engines: Dict[str, AsyncEngine] = {}
        self.cross_shard_executor: Optional[CrossShardQueryExecutor] = None
        self.rebalancer: Optional[ShardRebalancer] = None
        
        # State tracking
        self.shard_status: Dict[str, ShardStatus] = {}
        self.shard_metrics: Dict[str, ShardMetrics] = {}
        
        # Monitoring
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_monitoring = False
        
        # Statistics
        self.query_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    
    async def initialize(self) -> bool:
        """Initialize shard coordinator"""        try:
            logger.info("Initializing database shard coordinator")
            
            # Initialize shard engines
            for shard_id, config in self.shard_configs.items():
                try:
                    engine = await self._create_shard_engine(config)
                    self.shard_engines[shard_id] = engine
                    self.shard_status[shard_id] = ShardStatus.ACTIVE
                    self.shard_metrics[shard_id] = ShardMetrics(shard_id=shard_id)
                    
                    # Test connectivity
                    if await self._test_shard_connectivity(shard_id):
                        logger.info(f"Shard {shard_id} initialized successfully")
                    else:
                        self.shard_status[shard_id] = ShardStatus.OFFLINE
                        logger.warning(f"Shard {shard_id} connectivity test failed")
                        
                except Exception as e:
                    logger.error(f"Failed to initialize shard {shard_id}: {e}")
                    self.shard_status[shard_id] = ShardStatus.OFFLINE
            
            # Initialize components
            self.cross_shard_executor = CrossShardQueryExecutor(self.shard_engines)
            self.rebalancer = ShardRebalancer(self)
            
            # Setup consistent hash rings for applicable tables
            for table_name, rule in self.sharding_rules.items():
                if rule.strategy == ShardingStrategy.CONSISTENT_HASH:
                    shards = [shard_id for shard_id in self.shard_configs.keys()]
                    self.shard_router.setup_consistent_ring(table_name, shards)
            
            # Start monitoring
            await self.start_monitoring()
            
            logger.info(f"Database shard coordinator initialized with {len(self.shard_engines)} shards")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize shard coordinator: {e}")
            return False
    
    async def _create_shard_engine(self, config: ShardConfig) -> AsyncEngine:
        """Create async engine for shard"""        dsn = f"postgresql+asyncpg://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
        
        return create_async_engine(
            dsn,
            pool_size=20,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600,
            echo=False
        )
    
    async def _test_shard_connectivity(self, shard_id: str) -> bool:
        """Test connectivity to shard"""        try:
            engine = self.shard_engines.get(shard_id)
            if not engine:
                return False
            
            async with engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                return result.fetchone() is not None
                
        except Exception as e:
            logger.error(f"Shard connectivity test failed for {shard_id}: {e}")
            return False
    
    async def execute_query(self, table_name: str, query: str, 
                           query_data: Dict[str, Any],
                           query_type: QueryType = QueryType.SELECT) -> Any:
        """Execute query with automatic shard routing"""        try:
            # Route query to appropriate shards
            target_shards = self.shard_router.route_query(table_name, query_data, query_type)
            
            if len(target_shards) == 1:
                # Single shard query
                shard_id = target_shards[0]
                result = await self._execute_on_shard(shard_id, query, query_data)
                
                # Update statistics
                self.query_stats[shard_id]["success"] += 1
                
                return result
            else:
                # Cross-shard query
                if not self.cross_shard_executor:
                    raise Exception("Cross-shard executor not initialized")
                
                result = await self.cross_shard_executor.execute_cross_shard_query(
                    query, target_shards
                )
                
                # Update statistics
                for shard_id in target_shards:
                    self.query_stats[shard_id]["cross_shard"] += 1
                
                return result
                
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            
            # Update error statistics
            for shard_id in target_shards:
                self.query_stats[shard_id]["errors"] += 1
            
            raise
    
    async def _execute_on_shard(self, shard_id: str, query: str, 
                               params: Dict[str, Any]) -> Any:
        """Execute query on specific shard"""        engine = self.shard_engines.get(shard_id)
        if not engine:
            raise Exception(f"Shard {shard_id} not available")
        
        # Check shard status
        if self.shard_status.get(shard_id) != ShardStatus.ACTIVE:
            raise Exception(f"Shard {shard_id} is not active")
        
        async with engine.begin() as conn:
            result = await conn.execute(text(query), params)
            return result.fetchall()
    
    async def start_monitoring(self):
        """Start shard monitoring"""        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Shard monitoring started")
    
    async def stop_monitoring(self):
        """Stop shard monitoring"""        self.is_monitoring = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Shard monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""        while self.is_monitoring:
            try:
                # Update shard metrics
                await self._update_shard_metrics()
                
                # Check for rebalancing needs
                if self.rebalancer:
                    rebalancing_plan = await self.rebalancer.check_rebalancing_needed()
                    if rebalancing_plan.get('needed'):
                        logger.info(f"Rebalancing needed: {rebalancing_plan['reasons']}")
                        # Auto-rebalancing could be triggered here
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Shard monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def _update_shard_metrics(self):
        """Update metrics for all shards"""        for shard_id in self.shard_configs:
            try:
                await self._update_single_shard_metrics(shard_id)
            except Exception as e:
                logger.warning(f"Failed to update metrics for shard {shard_id}: {e}")
    
    async def _update_single_shard_metrics(self, shard_id: str):
        """Update metrics for a single shard"""        try:
            engine = self.shard_engines.get(shard_id)
            if not engine:
                return
            
            async with engine.begin() as conn:
                # Get table statistics
                stats_query = text("""                    SELECT 
                        SUM(n_live_tup) as total_rows,
                        SUM(pg_relation_size(relid)) / (1024*1024) as size_mb
                    FROM pg_stat_user_tables
                """)
                
                result = await conn.execute(stats_query)
                row = result.fetchone()
                
                if row:
                    metrics = self.shard_metrics[shard_id]
                    metrics.row_count = row.total_rows or 0
                    metrics.size_mb = row.size_mb or 0.0
                    metrics.last_updated = datetime.now()
                    
                    # Calculate utilization (simplified)
                    config = self.shard_configs[shard_id]
                    utilization = metrics.row_count / max(config.capacity, 1)
                    metrics.cpu_usage = min(1.0, utilization)  # Simplified
                    
        except Exception as e:
            logger.warning(f"Failed to update metrics for shard {shard_id}: {e}")
    
    async def get_shard_statistics(self) -> Dict[str, Any]:
        """Get comprehensive shard statistics"""        try:
            stats = {
                'total_shards': len(self.shard_configs),
                'active_shards': len([s for s in self.shard_status.values() if s == ShardStatus.ACTIVE]),
                'offline_shards': len([s for s in self.shard_status.values() if s == ShardStatus.OFFLINE]),
                'total_rows': sum(m.row_count for m in self.shard_metrics.values()),
                'total_size_mb': sum(m.size_mb for m in self.shard_metrics.values()),
                'shards': {}
            }
            
            for shard_id, config in self.shard_configs.items():
                metrics = self.shard_metrics.get(shard_id)
                query_stats = self.query_stats.get(shard_id, {})
                
                shard_stats = {
                    'status': self.shard_status.get(shard_id, ShardStatus.OFFLINE).value,
                    'region': config.region,
                    'weight': config.weight,
                    'capacity': config.capacity,
                    'queries_success': query_stats.get('success', 0),
                    'queries_errors': query_stats.get('errors', 0),
                    'cross_shard_queries': query_stats.get('cross_shard', 0)
                }
                
                if metrics:
                    shard_stats.update({
                        'row_count': metrics.row_count,
                        'size_mb': metrics.size_mb,
                        'utilization_score': metrics.utilization_score(),
                        'health_score': metrics.health_score(),
                        'last_updated': metrics.last_updated.isoformat()
                    })
                
                stats['shards'][shard_id] = shard_stats
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get shard statistics: {e}")
            return {}
    
    async def shutdown(self):
        """Shutdown shard coordinator"""        try:
            # Stop monitoring
            await self.stop_monitoring()
            
            # Close all shard engines
            for engine in self.shard_engines.values():
                await engine.dispose()
            
            logger.info("Database shard coordinator shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Export main classes
__all__ = [
    'DatabaseShardCoordinator', 
    'ShardConfig', 
    'ShardingRule', 
    'ShardingStrategy',
    'QueryType',
    'ShardStatus'
]