"""Database Optimization Integration Module

Comprehensive integration of all database optimization components for the Ainflue platform.
Provides unified interface and orchestration for all optimization strategies.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
import logging

from sqlalchemy.ext.asyncio import AsyncEngine

from .advanced_index_strategies import AdvancedIndexStrategiesManager, AdvancedIndexStrategy, WorkloadProfile
from .advanced_query_optimizer import AdvancedQueryOptimizer, OptimizationLevel
from .connection_pool_optimizer import EnhancedConnectionPoolManager, PoolOptimizationConfig
from .intelligent_partitioning import IntelligentPartitionManager, PartitionConfig, PartitionStrategy
from .read_replica_manager import ReadReplicaManager, ReplicaConfig, LoadBalancingStrategy
from .database_sharding import DatabaseShardCoordinator, ShardConfig, ShardingRule, ShardingStrategy
from .performance_monitor import DatabasePerformanceMonitor, MetricsCollector
from .backup_optimizer import BackupScheduler, BackupConfig, BackupType
from ..pools.manager import DatabasePoolManager
from .index_optimizer import IndexOptimizer, IndexConfig
from .query_optimizer import QueryOptimizer
from ...core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class OptimizationConfig:
    """Complete optimization configuration"""    # Index optimization
    enable_index_optimization: bool = True
    index_strategy: AdvancedIndexStrategy = AdvancedIndexStrategy.ADAPTIVE
    
    # Query optimization
    enable_query_optimization: bool = True
    query_optimization_level: OptimizationLevel = OptimizationLevel.INTERMEDIATE
    
    # Connection pooling
    enable_pool_optimization: bool = True
    pool_config: Optional[PoolOptimizationConfig] = None
    
    # Partitioning
    enable_partitioning: bool = True
    partition_configs: Dict[str, PartitionConfig] = field(default_factory=dict)
    
    # Read replicas
    enable_read_replicas: bool = True
    replica_configs: Dict[str, ReplicaConfig] = field(default_factory=dict)
    load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.INTELLIGENT
    
    # Sharding
    enable_sharding: bool = False
    shard_configs: Dict[str, ShardConfig] = field(default_factory=dict)
    sharding_rules: Dict[str, ShardingRule] = field(default_factory=dict)
    
    # Performance monitoring
    enable_monitoring: bool = True
    monitoring_interval: int = 60
    
    # Backup optimization
    enable_backup_optimization: bool = True
    backup_configs: Dict[str, BackupConfig] = field(default_factory=dict)


class DatabaseOptimizationOrchestrator:
    """Main orchestrator for all database optimization components"""    
    def __init__(self, engines: Dict[str, AsyncEngine], config: OptimizationConfig):
        self.engines = engines
        self.config = config
        
        # Core components
        self.pool_manager: Optional[DatabasePoolManager] = None
        self.base_index_optimizer: Optional[IndexOptimizer] = None
        self.base_query_optimizer: Optional[QueryOptimizer] = None
        
        # Advanced optimization components
        self.index_manager: Optional[AdvancedIndexStrategiesManager] = None
        self.query_optimizer: Optional[AdvancedQueryOptimizer] = None
        self.pool_optimizer: Optional[EnhancedConnectionPoolManager] = None
        self.partition_manager: Optional[IntelligentPartitionManager] = None
        self.replica_manager: Optional[ReadReplicaManager] = None
        self.shard_coordinator: Optional[DatabaseShardCoordinator] = None
        self.performance_monitor: Optional[DatabasePerformanceMonitor] = None
        self.backup_scheduler: Optional[BackupScheduler] = None
        
        # State tracking
        self.initialized = False
        self.running_components: List[str] = []
        
    async def initialize(self) -> bool:
        """Initialize all optimization components"""        try:
            logger.info("Initializing database optimization orchestrator")
            
            # Initialize core components first
            await self._initialize_core_components()
            
            # Initialize advanced optimization components
            if self.config.enable_index_optimization:
                await self._initialize_index_optimization()
            
            if self.config.enable_query_optimization:
                await self._initialize_query_optimization()
            
            if self.config.enable_pool_optimization:
                await self._initialize_pool_optimization()
            
            if self.config.enable_partitioning:
                await self._initialize_partitioning()
            
            if self.config.enable_read_replicas:
                await self._initialize_read_replicas()
            
            if self.config.enable_sharding:
                await self._initialize_sharding()
            
            if self.config.enable_monitoring:
                await self._initialize_monitoring()
            
            if self.config.enable_backup_optimization:
                await self._initialize_backup_optimization()
            
            # Cross-component integration
            await self._setup_component_integration()
            
            self.initialized = True
            logger.info(f"Database optimization orchestrator initialized with components: {self.running_components}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize optimization orchestrator: {e}")
            return False
    
    async def _initialize_core_components(self):
        """Initialize core database components"""        try:
            # Initialize base index optimizer
            index_config = IndexConfig()
            self.base_index_optimizer = IndexOptimizer(index_config)
            
            # Initialize base query optimizer
            self.base_query_optimizer = QueryOptimizer()
            
            logger.info("Core components initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize core components: {e}")
            raise
    
    async def _initialize_index_optimization(self):
        """Initialize advanced index optimization"""        try:
            if not self.base_index_optimizer:
                raise Exception("Base index optimizer not initialized")
            
            self.index_manager = AdvancedIndexStrategiesManager(self.base_index_optimizer)
            self.running_components.append("index_optimization")
            
            logger.info("Advanced index optimization initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize index optimization: {e}")
            raise
    
    async def _initialize_query_optimization(self):
        """Initialize advanced query optimization"""        try:
            if not self.base_query_optimizer:
                raise Exception("Base query optimizer not initialized")
            
            self.query_optimizer = AdvancedQueryOptimizer(self.base_query_optimizer)
            self.running_components.append("query_optimization")
            
            logger.info("Advanced query optimization initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize query optimization: {e}")
            raise
    
    async def _initialize_pool_optimization(self):
        """Initialize connection pool optimization"""        try:
            # Create pool manager if not exists
            if not self.pool_manager:
                from ..pools.manager import get_pool_manager
                self.pool_manager = get_pool_manager()
            
            # Initialize enhanced pool manager
            pool_config = self.config.pool_config or PoolOptimizationConfig()
            self.pool_optimizer = EnhancedConnectionPoolManager(self.pool_manager, pool_config)
            
            await self.pool_optimizer.start_optimization()
            self.running_components.append("pool_optimization")
            
            logger.info("Connection pool optimization initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize pool optimization: {e}")
            raise
    
    async def _initialize_partitioning(self):
        """Initialize intelligent partitioning"""        try:
            primary_engine = list(self.engines.values())[0] if self.engines else None
            if not primary_engine:
                raise Exception("No database engine available for partitioning")
            
            self.partition_manager = IntelligentPartitionManager(primary_engine)
            
            if self.config.partition_configs:
                success = await self.partition_manager.initialize_partitioning(self.config.partition_configs)
                if success:
                    self.running_components.append("partitioning")
                    logger.info("Intelligent partitioning initialized")
                else:
                    logger.warning("Partitioning initialization failed")
            
        except Exception as e:
            logger.error(f"Failed to initialize partitioning: {e}")
            raise
    
    async def _initialize_read_replicas(self):
        """Initialize read replica management"""        try:
            primary_engine = list(self.engines.values())[0] if self.engines else None
            if not primary_engine:
                raise Exception("No database engine available for replicas")
            
            if not self.config.replica_configs:
                logger.info("No replica configurations provided, skipping replica initialization")
                return
            
            self.replica_manager = ReadReplicaManager(
                primary_engine, 
                self.config.replica_configs,
                self.config.load_balancing_strategy
            )
            
            success = await self.replica_manager.initialize()
            if success:
                self.running_components.append("read_replicas")
                logger.info("Read replica management initialized")
            else:
                logger.warning("Read replica initialization failed")
            
        except Exception as e:
            logger.error(f"Failed to initialize read replicas: {e}")
            raise
    
    async def _initialize_sharding(self):
        """Initialize database sharding"""        try:
            if not self.config.shard_configs or not self.config.sharding_rules:
                logger.info("No sharding configurations provided, skipping sharding initialization")
                return
            
            self.shard_coordinator = DatabaseShardCoordinator(
                self.config.shard_configs,
                self.config.sharding_rules
            )
            
            success = await self.shard_coordinator.initialize()
            if success:
                self.running_components.append("sharding")
                logger.info("Database sharding initialized")
            else:
                logger.warning("Sharding initialization failed")
            
        except Exception as e:
            logger.error(f"Failed to initialize sharding: {e}")
            raise
    
    async def _initialize_monitoring(self):
        """Initialize performance monitoring"""        try:
            self.performance_monitor = DatabasePerformanceMonitor(self.engines)
            
            await self.performance_monitor.start_monitoring(self.config.monitoring_interval)
            self.running_components.append("monitoring")
            
            logger.info("Performance monitoring initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize monitoring: {e}")
            raise
    
    async def _initialize_backup_optimization(self):
        """Initialize backup optimization"""        try:
            self.backup_scheduler = BackupScheduler(self.engines)
            
            # Add backup configurations
            for backup_config in self.config.backup_configs.values():
                self.backup_scheduler.add_backup_config(backup_config)
            
            await self.backup_scheduler.start_scheduler()
            self.running_components.append("backup_optimization")
            
            logger.info("Backup optimization initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize backup optimization: {e}")
            raise
    
    async def _setup_component_integration(self):
        """Setup integration between components"""        try:
            # Integrate performance monitor with other components
            if self.performance_monitor:
                self.performance_monitor.index_manager = self.index_manager
                self.performance_monitor.query_optimizer = self.query_optimizer
                self.performance_monitor.pool_manager = self.pool_optimizer
                self.performance_monitor.partition_manager = self.partition_manager
                self.performance_monitor.replica_manager = self.replica_manager
                self.performance_monitor.shard_coordinator = self.shard_coordinator
            
            logger.info("Component integration completed")
            
        except Exception as e:
            logger.error(f"Failed to setup component integration: {e}")
            raise
    
    async def execute_optimization_cycle(self) -> Dict[str, Any]:
        """Execute a complete optimization cycle"""        try:
            results = {
                'timestamp': datetime.now().isoformat(),
                'cycle_results': {},
                'errors': []
            }
            
            logger.info("Starting optimization cycle")
            
            # Index optimization
            if self.index_manager:
                try:
                    primary_engine = list(self.engines.values())[0]
                    index_result = await self.index_manager.execute_strategy(
                        primary_engine, 
                        self.config.index_strategy
                    )
                    results['cycle_results']['index_optimization'] = index_result
                except Exception as e:
                    results['errors'].append(f"Index optimization failed: {e}")
            
            # Query optimization for recent queries
            if self.query_optimizer:
                try:
                    # This would typically analyze recent slow queries
                    optimization_stats = self.query_optimizer.get_optimization_stats()
                    results['cycle_results']['query_optimization'] = optimization_stats
                except Exception as e:
                    results['errors'].append(f"Query optimization failed: {e}")
            
            # Partition optimization
            if self.partition_manager:
                try:
                    for table_name in self.config.partition_configs.keys():
                        partition_result = await self.partition_manager.optimize_partitions(table_name)
                        results['cycle_results'][f'partition_{table_name}'] = partition_result
                except Exception as e:
                    results['errors'].append(f"Partition optimization failed: {e}")
            
            # Pool optimization (automatic via background tasks)
            if self.pool_optimizer:
                try:
                    pool_stats = await self.pool_optimizer.get_optimization_stats()
                    results['cycle_results']['pool_optimization'] = pool_stats
                except Exception as e:
                    results['errors'].append(f"Pool optimization failed: {e}")
            
            logger.info(f"Optimization cycle completed with {len(results['errors'])} errors")
            return results
            
        except Exception as e:
            logger.error(f"Optimization cycle failed: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    async def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all optimization components"""        try:
            status = {
                'orchestrator': {
                    'initialized': self.initialized,
                    'running_components': self.running_components,
                    'total_engines': len(self.engines)
                },
                'components': {}
            }
            
            # Index optimization status
            if self.index_manager:
                status['components']['index_optimization'] = self.index_manager.get_strategy_stats()
            
            # Query optimization status  
            if self.query_optimizer:
                status['components']['query_optimization'] = self.query_optimizer.get_optimization_stats()
            
            # Pool optimization status
            if self.pool_optimizer:
                status['components']['pool_optimization'] = await self.pool_optimizer.get_optimization_stats()
            
            # Partitioning status
            if self.partition_manager:
                status['components']['partitioning'] = await self.partition_manager.get_partition_stats()
            
            # Read replica status
            if self.replica_manager:
                status['components']['read_replicas'] = await self.replica_manager.get_replica_stats()
            
            # Sharding status
            if self.shard_coordinator:
                status['components']['sharding'] = await self.shard_coordinator.get_shard_statistics()
            
            # Monitoring status
            if self.performance_monitor:
                status['components']['monitoring'] = self.performance_monitor.get_dashboard_data(1)
            
            # Backup status
            if self.backup_scheduler:
                status['components']['backup'] = self.backup_scheduler.get_backup_status()
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get comprehensive status: {e}")
            return {'error': str(e)}
    
    async def shutdown(self):
        """Shutdown all optimization components"""        try:
            logger.info("Shutting down database optimization orchestrator")
            
            # Stop monitoring first
            if self.performance_monitor:
                await self.performance_monitor.stop_monitoring()
            
            # Stop backup scheduler
            if self.backup_scheduler:
                await self.backup_scheduler.stop_scheduler()
            
            # Stop pool optimization
            if self.pool_optimizer:
                await self.pool_optimizer.stop_optimization()
            
            # Shutdown partition manager
            if self.partition_manager:
                await self.partition_manager.shutdown()
            
            # Shutdown replica manager
            if self.replica_manager:
                await self.replica_manager.shutdown()
            
            # Shutdown shard coordinator
            if self.shard_coordinator:
                await self.shard_coordinator.shutdown()
            
            self.initialized = False
            self.running_components.clear()
            
            logger.info("Database optimization orchestrator shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Convenience function to create orchestrator with default configurations
def create_optimization_orchestrator(engines: Dict[str, AsyncEngine],
                                   custom_config: Optional[OptimizationConfig] = None) -> DatabaseOptimizationOrchestrator:
    """Create orchestrator with default or custom configuration"""    
    if custom_config:
        config = custom_config
    else:
        # Create default configuration for Ainflue platform
        config = OptimizationConfig()
        
        # Default partition configurations for key tables
        config.partition_configs = {
            'content': PartitionConfig(
                strategy=PartitionStrategy.TEMPORAL,
                partition_type='HORIZONTAL',
                table_name='content',
                partition_key='created_at',
                partition_count=12  # Monthly partitions
            ),
            'content_performance': PartitionConfig(
                strategy=PartitionStrategy.TEMPORAL,
                partition_type='HORIZONTAL',
                table_name='content_performance',
                partition_key='collected_at',
                partition_count=12
            ),
            'revenue_tracking': PartitionConfig(
                strategy=PartitionStrategy.TEMPORAL,
                partition_type='HORIZONTAL',
                table_name='revenue_tracking',
                partition_key='created_at',
                partition_count=12
            )
        }
        
        # Default backup configurations
        config.backup_configs = {
            'daily_full': BackupConfig(
                backup_id='daily_full_backup',
                database_name='ainflue_platform',
                backup_type=BackupType.FULL,
                schedule_cron='0 2 * * *',  # Daily at 2 AM
                retention_days=30
            ),
            'hourly_incremental': BackupConfig(
                backup_id='hourly_incremental_backup',
                database_name='ainflue_platform',
                backup_type=BackupType.INCREMENTAL,
                schedule_cron='0 * * * *',  # Every hour
                retention_days=7
            )
        }
    
    return DatabaseOptimizationOrchestrator(engines, config)


# Export main classes
__all__ = [
    'DatabaseOptimizationOrchestrator',
    'OptimizationConfig',
    'create_optimization_orchestrator'
]