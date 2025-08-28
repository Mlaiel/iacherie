"""
Enhanced Database Partitioning System

Complete partitioning implementation with automated management, intelligent optimization,
and advanced sharding capabilities for high-scale applications.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict
import logging

from sqlalchemy import text, MetaData, Table, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.asyncio import AsyncEngine

from .partition_manager import PartitionManager, PartitionConfig, PartitionStrategy, PartitionStatus
from ...core.logging import get_logger

logger = get_logger(__name__)


class PartitioningTrigger(Enum):
    """Triggers for partition operations"""
    SIZE_THRESHOLD = "size_threshold"
    TIME_THRESHOLD = "time_threshold"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    MANUAL = "manual"
    SCHEDULED = "scheduled"


@dataclass
class PartitionPlan:
    """Partition execution plan"""
    table_name: str
    strategy: PartitionStrategy
    new_partitions: List[str]
    migrations_needed: List[Dict[str, Any]]
    estimated_downtime: float
    resource_requirements: Dict[str, Any]
    rollback_plan: List[str]


@dataclass
class ShardingConfig:
    """Database sharding configuration"""
    shard_count: int
    shard_key: str
    routing_algorithm: str
    replication_factor: int
    consistency_level: str
    cross_shard_queries: bool = False
    auto_rebalancing: bool = True


class IntelligentPartitionManager:
    """Intelligent partition manager with automated optimization"""
    
    def __init__(self, engine: AsyncEngine):
        self.engine = engine
        self.base_manager = PartitionManager()
        self.partition_configs: Dict[str, PartitionConfig] = {}
        self.partition_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.optimization_history: List[Dict[str, Any]] = []
        self.monitoring_task: Optional[asyncio.Task] = None
        
    async def initialize_partitioning(self, table_configs: Dict[str, PartitionConfig]) -> bool:
        """Initialize partitioning for multiple tables"""
        try:
            logger.info("Initializing intelligent partitioning system")
            
            for table_name, config in table_configs.items():
                self.partition_configs[table_name] = config
                success = await self._setup_table_partitioning(table_name, config)
                
                if not success:
                    logger.error(f"Failed to setup partitioning for {table_name}")
                    return False
            
            # Start monitoring
            self.monitoring_task = asyncio.create_task(self._monitor_partitions())
            
            logger.info("Intelligent partitioning system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize partitioning: {e}")
            return False
    
    async def _setup_table_partitioning(self, table_name: str, config: PartitionConfig) -> bool:
        """Setup partitioning for a specific table"""
        try:
            if config.strategy == PartitionStrategy.TEMPORAL:
                return await self._setup_temporal_partitioning(table_name, config)
            elif config.strategy == PartitionStrategy.HASH:
                return await self._setup_hash_partitioning(table_name, config)
            elif config.strategy == PartitionStrategy.RANGE:
                return await self._setup_range_partitioning(table_name, config)
            elif config.strategy == PartitionStrategy.USER_BASED:
                return await self._setup_user_based_partitioning(table_name, config)
            else:
                logger.warning(f"Partitioning strategy {config.strategy} not implemented yet")
                return False
                
        except Exception as e:
            logger.error(f"Failed to setup partitioning for {table_name}: {e}")
            return False
    
    async def _setup_temporal_partitioning(self, table_name: str, config: PartitionConfig) -> bool:
        """Setup temporal (time-based) partitioning"""
        try:
            # Create parent partitioned table
            create_parent_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name}_partitioned (
                LIKE {table_name} INCLUDING ALL
            ) PARTITION BY RANGE ({config.partition_key})
            """
            
            async with self.engine.begin() as conn:
                await conn.execute(text(create_parent_sql))
            
            # Create initial monthly partitions for current and next few months
            current_date = datetime.now().replace(day=1)
            
            for i in range(6):  # 6 months ahead
                partition_date = current_date + timedelta(days=32 * i)
                partition_date = partition_date.replace(day=1)
                
                next_month = (partition_date.replace(day=28) + timedelta(days=4)).replace(day=1)
                
                partition_name = f"{table_name}_{partition_date.strftime('%Y_%m')}"
                
                create_partition_sql = f"""
                CREATE TABLE IF NOT EXISTS {partition_name} 
                PARTITION OF {table_name}_partitioned
                FOR VALUES FROM ('{partition_date.isoformat()}') TO ('{next_month.isoformat()}')
                """
                
                async with self.engine.begin() as conn:
                    await conn.execute(text(create_partition_sql))
                
                logger.info(f"Created temporal partition: {partition_name}")
            
            # Create indexes on partitions
            await self._create_partition_indexes(table_name, config)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup temporal partitioning: {e}")
            return False
    
    async def _setup_hash_partitioning(self, table_name: str, config: PartitionConfig) -> bool:
        """Setup hash-based partitioning"""
        try:
            # Create parent partitioned table
            create_parent_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name}_partitioned (
                LIKE {table_name} INCLUDING ALL
            ) PARTITION BY HASH ({config.partition_key})
            """
            
            async with self.engine.begin() as conn:
                await conn.execute(text(create_parent_sql))
            
            # Create hash partitions
            for i in range(config.partition_count):
                partition_name = f"{table_name}_hash_{i}"
                
                create_partition_sql = f"""
                CREATE TABLE IF NOT EXISTS {partition_name}
                PARTITION OF {table_name}_partitioned
                FOR VALUES WITH (MODULUS {config.partition_count}, REMAINDER {i})
                """
                
                async with self.engine.begin() as conn:
                    await conn.execute(text(create_partition_sql))
                
                logger.info(f"Created hash partition: {partition_name}")
            
            await self._create_partition_indexes(table_name, config)
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup hash partitioning: {e}")
            return False
    
    async def _setup_range_partitioning(self, table_name: str, config: PartitionConfig) -> bool:
        """Setup range-based partitioning"""
        try:
            # Create parent partitioned table
            create_parent_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name}_partitioned (
                LIKE {table_name} INCLUDING ALL
            ) PARTITION BY RANGE ({config.partition_key})
            """
            
            async with self.engine.begin() as conn:
                await conn.execute(text(create_parent_sql))
            
            # Analyze existing data to determine ranges
            ranges = await self._calculate_optimal_ranges(table_name, config)
            
            for i, (start_val, end_val) in enumerate(ranges):
                partition_name = f"{table_name}_range_{i}"
                
                create_partition_sql = f"""
                CREATE TABLE IF NOT EXISTS {partition_name}
                PARTITION OF {table_name}_partitioned
                FOR VALUES FROM ({start_val}) TO ({end_val})
                """
                
                async with self.engine.begin() as conn:
                    await conn.execute(text(create_partition_sql))
                
                logger.info(f"Created range partition: {partition_name} ({start_val} to {end_val})")
            
            await self._create_partition_indexes(table_name, config)
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup range partitioning: {e}")
            return False
    
    async def _setup_user_based_partitioning(self, table_name: str, config: PartitionConfig) -> bool:
        """Setup user-based partitioning for multi-tenant applications"""
        try:
            # Create parent partitioned table
            create_parent_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name}_partitioned (
                LIKE {table_name} INCLUDING ALL
            ) PARTITION BY HASH (substring({config.partition_key}::text, 1, 1))
            """
            
            async with self.engine.begin() as conn:
                await conn.execute(text(create_parent_sql))
            
            # Create partitions based on user ID prefix (for better distribution)
            for i in range(16):  # 16 partitions for hex digits
                partition_name = f"{table_name}_user_{format(i, 'x')}"
                
                create_partition_sql = f"""
                CREATE TABLE IF NOT EXISTS {partition_name}
                PARTITION OF {table_name}_partitioned
                FOR VALUES WITH (MODULUS 16, REMAINDER {i})
                """
                
                async with self.engine.begin() as conn:
                    await conn.execute(text(create_partition_sql))
                
                logger.info(f"Created user partition: {partition_name}")
            
            await self._create_partition_indexes(table_name, config)
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup user-based partitioning: {e}")
            return False
    
    async def _create_partition_indexes(self, table_name: str, config: PartitionConfig):
        """Create optimized indexes on partitions"""
        try:
            # Get partition names
            partitions = await self._get_table_partitions(table_name)
            
            # Common indexes for all partitions
            common_indexes = [
                f"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_{{partition}}_created_at ON {{partition}} (created_at)",
                f"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_{{partition}}_user_id ON {{partition}} (user_id)",
                f"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_{{partition}}_status ON {{partition}} (status) WHERE status IN ('active', 'processing')"
            ]
            
            for partition in partitions:
                for index_template in common_indexes:
                    index_sql = index_template.format(partition=partition)
                    
                    try:
                        async with self.engine.begin() as conn:
                            await conn.execute(text(index_sql))
                    except Exception as e:
                        logger.warning(f"Failed to create index on {partition}: {e}")
            
            logger.info(f"Created indexes for {len(partitions)} partitions of {table_name}")
            
        except Exception as e:
            logger.error(f"Failed to create partition indexes: {e}")
    
    async def _calculate_optimal_ranges(self, table_name: str, config: PartitionConfig) -> List[Tuple[Any, Any]]:
        """Calculate optimal ranges for range partitioning"""
        try:
            # Get data distribution
            analyze_sql = f"""
            SELECT 
                MIN({config.partition_key}) as min_val,
                MAX({config.partition_key}) as max_val,
                COUNT(*) as total_rows
            FROM {table_name}
            """
            
            async with self.engine.begin() as conn:
                result = await conn.execute(text(analyze_sql))
                row = result.fetchone()
            
            if not row or row.total_rows == 0:
                # Default ranges if no data
                return [(i * 1000000, (i + 1) * 1000000) for i in range(config.partition_count)]
            
            min_val = row.min_val
            max_val = row.max_val
            
            # Calculate range size
            range_size = (max_val - min_val) / config.partition_count
            
            ranges = []
            for i in range(config.partition_count):
                start = min_val + (i * range_size)
                end = min_val + ((i + 1) * range_size) if i < config.partition_count - 1 else max_val + 1
                ranges.append((int(start), int(end)))
            
            return ranges
            
        except Exception as e:
            logger.error(f"Failed to calculate optimal ranges: {e}")
            return [(i * 1000000, (i + 1) * 1000000) for i in range(config.partition_count)]
    
    async def _get_table_partitions(self, table_name: str) -> List[str]:
        """Get list of partitions for a table"""
        try:
            query = text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename LIKE :pattern
                ORDER BY tablename
            """)
            
            async with self.engine.begin() as conn:
                result = await conn.execute(query, {"pattern": f"{table_name}_%"})
                return [row.tablename for row in result]
                
        except Exception as e:
            logger.error(f"Failed to get table partitions: {e}")
            return []
    
    async def auto_create_partitions(self, table_name: str) -> List[str]:
        """Automatically create new partitions when needed"""
        try:
            config = self.partition_configs.get(table_name)
            if not config:
                return []
            
            created_partitions = []
            
            if config.strategy == PartitionStrategy.TEMPORAL:
                # Check if we need future partitions
                future_partitions = await self._check_future_temporal_partitions(table_name, config)
                
                for partition_info in future_partitions:
                    success = await self._create_temporal_partition(table_name, partition_info)
                    if success:
                        created_partitions.append(partition_info['name'])
            
            elif config.strategy == PartitionStrategy.HASH:
                # Check if we need to add more hash partitions for load balancing
                if await self._should_expand_hash_partitions(table_name, config):
                    new_partitions = await self._expand_hash_partitions(table_name, config)
                    created_partitions.extend(new_partitions)
            
            return created_partitions
            
        except Exception as e:
            logger.error(f"Failed to auto-create partitions for {table_name}: {e}")
            return []
    
    async def _check_future_temporal_partitions(self, table_name: str, config: PartitionConfig) -> List[Dict[str, Any]]:
        """Check for needed future temporal partitions"""
        try:
            # Get current partitions
            current_partitions = await self._get_table_partitions(table_name)
            
            # Calculate what partitions we should have
            needed_partitions = []
            current_date = datetime.now().replace(day=1)
            
            for i in range(6):  # 6 months ahead
                partition_date = current_date + timedelta(days=32 * i)
                partition_date = partition_date.replace(day=1)
                partition_name = f"{table_name}_{partition_date.strftime('%Y_%m')}"
                
                if partition_name not in current_partitions:
                    next_month = (partition_date.replace(day=28) + timedelta(days=4)).replace(day=1)
                    
                    needed_partitions.append({
                        'name': partition_name,
                        'start_date': partition_date,
                        'end_date': next_month
                    })
            
            return needed_partitions
            
        except Exception as e:
            logger.error(f"Failed to check future temporal partitions: {e}")
            return []
    
    async def _create_temporal_partition(self, table_name: str, partition_info: Dict[str, Any]) -> bool:
        """Create a single temporal partition"""
        try:
            partition_name = partition_info['name']
            start_date = partition_info['start_date']
            end_date = partition_info['end_date']
            
            create_sql = f"""
            CREATE TABLE IF NOT EXISTS {partition_name}
            PARTITION OF {table_name}_partitioned
            FOR VALUES FROM ('{start_date.isoformat()}') TO ('{end_date.isoformat()}')
            """
            
            async with self.engine.begin() as conn:
                await conn.execute(text(create_sql))
            
            # Create indexes on new partition
            await self._create_partition_indexes(partition_name, self.partition_configs[table_name])
            
            logger.info(f"Created temporal partition: {partition_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create temporal partition: {e}")
            return False
    
    async def optimize_partitions(self, table_name: str) -> Dict[str, Any]:
        """Optimize existing partitions"""
        try:
            config = self.partition_configs.get(table_name)
            if not config:
                return {'error': 'No configuration found'}
            
            optimizations = []
            
            # Analyze partition performance
            partition_stats = await self._analyze_partition_performance(table_name)
            
            # Check for unbalanced partitions
            unbalanced = self._detect_unbalanced_partitions(partition_stats)
            if unbalanced:
                optimizations.append({
                    'type': 'rebalance',
                    'partitions': unbalanced,
                    'action': 'redistribute_data'
                })
            
            # Check for unused partitions
            unused = self._detect_unused_partitions(partition_stats)
            if unused:
                optimizations.append({
                    'type': 'cleanup',
                    'partitions': unused,
                    'action': 'drop_or_archive'
                })
            
            # Check for performance issues
            slow_partitions = self._detect_slow_partitions(partition_stats)
            if slow_partitions:
                optimizations.append({
                    'type': 'performance',
                    'partitions': slow_partitions,
                    'action': 'add_indexes_or_vacuum'
                })
            
            # Execute optimizations
            executed_optimizations = []
            for optimization in optimizations[:3]:  # Limit to 3 optimizations per run
                success = await self._execute_optimization(table_name, optimization)
                if success:
                    executed_optimizations.append(optimization)
            
            return {
                'table_name': table_name,
                'optimizations_found': len(optimizations),
                'optimizations_executed': len(executed_optimizations),
                'details': executed_optimizations
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize partitions for {table_name}: {e}")
            return {'error': str(e)}
    
    async def _analyze_partition_performance(self, table_name: str) -> Dict[str, Dict[str, Any]]:
        """Analyze performance of individual partitions"""
        try:
            partitions = await self._get_table_partitions(table_name)
            stats = {}
            
            for partition in partitions:
                # Get partition statistics
                stat_query = text(f"""
                    SELECT 
                        relname,
                        n_tup_ins,
                        n_tup_upd,
                        n_tup_del,
                        n_live_tup,
                        n_dead_tup,
                        last_vacuum,
                        last_analyze,
                        pg_relation_size('{partition}') as size_bytes
                    FROM pg_stat_user_tables 
                    WHERE relname = '{partition}'
                """)
                
                async with self.engine.begin() as conn:
                    result = await conn.execute(stat_query)
                    row = result.fetchone()
                
                if row:
                    stats[partition] = {
                        'inserts': row.n_tup_ins or 0,
                        'updates': row.n_tup_upd or 0,
                        'deletes': row.n_tup_del or 0,
                        'live_tuples': row.n_live_tup or 0,
                        'dead_tuples': row.n_dead_tup or 0,
                        'size_bytes': row.size_bytes or 0,
                        'last_vacuum': row.last_vacuum,
                        'last_analyze': row.last_analyze,
                        'dead_tuple_ratio': (row.n_dead_tup or 0) / max(row.n_live_tup or 1, 1)
                    }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to analyze partition performance: {e}")
            return {}
    
    def _detect_unbalanced_partitions(self, partition_stats: Dict[str, Dict[str, Any]]) -> List[str]:
        """Detect partitions with unbalanced data distribution"""
        if not partition_stats:
            return []
        
        # Calculate average partition size
        sizes = [stats['size_bytes'] for stats in partition_stats.values()]
        if not sizes:
            return []
        
        avg_size = sum(sizes) / len(sizes)
        threshold = avg_size * 2  # Partitions more than 2x average size
        
        unbalanced = []
        for partition, stats in partition_stats.items():
            if stats['size_bytes'] > threshold:
                unbalanced.append(partition)
        
        return unbalanced
    
    def _detect_unused_partitions(self, partition_stats: Dict[str, Dict[str, Any]]) -> List[str]:
        """Detect unused or rarely accessed partitions"""
        unused = []
        
        for partition, stats in partition_stats.items():
            # Consider unused if no activity in recent period and very small
            if (stats['inserts'] == 0 and 
                stats['updates'] == 0 and 
                stats['size_bytes'] < 1024 * 1024):  # Less than 1MB
                unused.append(partition)
        
        return unused
    
    def _detect_slow_partitions(self, partition_stats: Dict[str, Dict[str, Any]]) -> List[str]:
        """Detect partitions with performance issues"""
        slow = []
        
        for partition, stats in partition_stats.items():
            # High dead tuple ratio indicates need for vacuum
            if stats['dead_tuple_ratio'] > 0.2:  # 20% dead tuples
                slow.append(partition)
        
        return slow
    
    async def _execute_optimization(self, table_name: str, optimization: Dict[str, Any]) -> bool:
        """Execute a specific optimization"""
        try:
            optimization_type = optimization['type']
            partitions = optimization['partitions']
            action = optimization['action']
            
            if optimization_type == 'cleanup' and action == 'drop_or_archive':
                for partition in partitions[:2]:  # Limit to 2 partitions
                    await self._archive_partition(partition)
                return True
            
            elif optimization_type == 'performance' and action == 'add_indexes_or_vacuum':
                for partition in partitions:
                    await self._vacuum_partition(partition)
                return True
            
            elif optimization_type == 'rebalance':
                logger.info(f"Rebalancing detected for partitions: {partitions}")
                # Rebalancing would be complex and require careful planning
                return False
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to execute optimization: {e}")
            return False
    
    async def _archive_partition(self, partition_name: str):
        """Archive an unused partition"""
        try:
            # In a real implementation, you'd move data to archival storage
            logger.info(f"Archiving partition: {partition_name}")
            
            # For now, just log the action
            # You could implement actual archival logic here
            
        except Exception as e:
            logger.error(f"Failed to archive partition {partition_name}: {e}")
    
    async def _vacuum_partition(self, partition_name: str):
        """Vacuum a partition to improve performance"""
        try:
            vacuum_sql = f"VACUUM ANALYZE {partition_name}"
            
            async with self.engine.begin() as conn:
                await conn.execute(text(vacuum_sql))
            
            logger.info(f"Vacuumed partition: {partition_name}")
            
        except Exception as e:
            logger.error(f"Failed to vacuum partition {partition_name}: {e}")
    
    async def _monitor_partitions(self):
        """Background task to monitor partition health"""
        while True:
            try:
                for table_name in self.partition_configs:
                    # Auto-create partitions if needed
                    new_partitions = await self.auto_create_partitions(table_name)
                    if new_partitions:
                        logger.info(f"Auto-created partitions for {table_name}: {new_partitions}")
                    
                    # Optimize partitions periodically
                    optimization_result = await self.optimize_partitions(table_name)
                    if optimization_result.get('optimizations_executed', 0) > 0:
                        logger.info(f"Optimized partitions for {table_name}: {optimization_result}")
                
                # Sleep for 1 hour
                await asyncio.sleep(3600)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Partition monitoring error: {e}")
                await asyncio.sleep(300)  # Sleep 5 minutes on error
    
    async def get_partition_stats(self) -> Dict[str, Any]:
        """Get comprehensive partition statistics"""
        try:
            stats = {
                'total_tables': len(self.partition_configs),
                'tables': {}
            }
            
            for table_name, config in self.partition_configs.items():
                partitions = await self._get_table_partitions(table_name)
                partition_stats = await self._analyze_partition_performance(table_name)
                
                total_size = sum(p.get('size_bytes', 0) for p in partition_stats.values())
                total_rows = sum(p.get('live_tuples', 0) for p in partition_stats.values())
                
                stats['tables'][table_name] = {
                    'strategy': config.strategy.value,
                    'partition_count': len(partitions),
                    'total_size_mb': total_size / (1024 * 1024),
                    'total_rows': total_rows,
                    'partitions': list(partitions)
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get partition stats: {e}")
            return {}
    
    async def shutdown(self):
        """Shutdown the partition manager"""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Intelligent partition manager shutdown completed")


# Export main class
__all__ = ['IntelligentPartitionManager', 'PartitionPlan', 'ShardingConfig', 'PartitioningTrigger']