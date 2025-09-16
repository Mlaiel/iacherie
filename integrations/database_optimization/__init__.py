"""🗄️ Database Optimization Module - Enterprise Implementation
=========================================================

Module d'optimisation database enterprise avec clustering haute disponibilité,
réplication multi-region et performance tuning pour Ainflue.

Author: Fahed Mlaiel (mlaiel@live.de)
Date: 14 Septembre 2025
"""

from .enterprise_database_optimizer import (
    EnterpriseDatabaseOptimizer,
    DatabaseConfiguration,
    DatabaseNode,
    DatabaseType,
    ReplicationStrategy,
    BackupStrategy,
    OptimizationLevel,
    QueryMetrics,
    PerformanceAlert,
    initialize_database_optimizer
)

# Phase 1: Core Optimization Infrastructure
from .query_optimization_engine import (
    QueryOptimizationEngine,
    QueryType,
    OptimizationLevel as QueryOptimizationLevel,
    IndexType,
    QueryMetrics as QueryEngineMetrics,
    QueryPattern,
    IndexRecommendation,
    OptimizationRecommendation,
    initialize_query_optimizer
)

from .connection_pool_manager import (
    ConnectionPoolManager,
    ConnectionPool,
    DatabaseEndpoint,
    PoolConfiguration,
    DatabaseType as PoolDatabaseType,
    ConnectionState,
    LoadBalancingStrategy,
    PoolScalingMode,
    ConnectionMetrics,
    CircuitBreakerConfig,
    get_database_connection,
    initialize_connection_pool_manager
)

from .indexing_strategies_manager import (
    IndexingStrategiesManager,
    IndexType as IndexingIndexType,
    IndexCategory,
    IndexPriority,
    MaintenanceAction,
    TableSchema,
    QueryPattern as IndexingQueryPattern,
    ExistingIndex,
    IndexRecommendation as IndexingRecommendation,
    IndexPerformanceMetrics,
    initialize_indexing_strategies_manager
)

from .sharding_controller import (
    ShardingController,
    ConsistentHashRing,
    ShardConfiguration,
    ShardKeyMapping,
    ShardMetrics,
    RebalancingPlan,
    QueryRoutingInfo,
    ShardingStrategy,
    ShardState,
    RebalancingTrigger,
    DataDistributionMethod,
    initialize_sharding_controller
)

__version__ = "2.1.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    # Core Enterprise Optimizer
    "EnterpriseDatabaseOptimizer",
    "DatabaseConfiguration",
    "DatabaseNode", 
    "DatabaseType",
    "ReplicationStrategy",
    "BackupStrategy",
    "OptimizationLevel",
    "QueryMetrics",
    "PerformanceAlert",
    "initialize_database_optimizer",
    
    # Query Optimization Engine
    "QueryOptimizationEngine",
    "QueryType",
    "QueryOptimizationLevel",
    "IndexType",
    "QueryEngineMetrics",
    "QueryPattern",
    "IndexRecommendation",
    "OptimizationRecommendation",
    "initialize_query_optimizer",
    
    # Connection Pool Manager
    "ConnectionPoolManager",
    "ConnectionPool",
    "DatabaseEndpoint",
    "PoolConfiguration",
    "PoolDatabaseType",
    "ConnectionState",
    "LoadBalancingStrategy",
    "PoolScalingMode",
    "ConnectionMetrics",
    "CircuitBreakerConfig",
    "get_database_connection",
    "initialize_connection_pool_manager",
    
    # Indexing Strategies Manager
    "IndexingStrategiesManager",
    "IndexingIndexType",
    "IndexCategory",
    "IndexPriority",
    "MaintenanceAction",
    "TableSchema",
    "IndexingQueryPattern",
    "ExistingIndex",
    "IndexingRecommendation",
    "IndexPerformanceMetrics",
    "initialize_indexing_strategies_manager",
    
    # Sharding Controller
    "ShardingController",
    "ConsistentHashRing",
    "ShardConfiguration",
    "ShardKeyMapping",
    "ShardMetrics",
    "RebalancingPlan",
    "QueryRoutingInfo",
    "ShardingStrategy",
    "ShardState",
    "RebalancingTrigger",
    "DataDistributionMethod",
    "initialize_sharding_controller"
]