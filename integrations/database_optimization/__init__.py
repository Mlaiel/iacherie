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

# Phase 2: Performance & Monitoring
from .backup_automation_manager import (
    BackupAutomationManager,
    BackupType,
    BackupStatus,
    CompressionLevel,
    EncryptionMethod,
    BackupConfiguration,
    BackupJob,
    RestoreRequest,
    initialize_backup_automation_manager
)

from .performance_monitoring_dashboard import (
    PerformanceMonitoringDashboard,
    MetricType,
    AlertLevel,
    DatabaseEngine as MonitoringDatabaseEngine,
    PerformanceMetric,
    QueryMetrics as MonitoringQueryMetrics,
    PerformanceAlert as MonitoringPerformanceAlert,
    DatabaseHealthScore,
    initialize_performance_monitoring_dashboard
)

from .replica_management_system import (
    ReplicaManagementSystem,
    ReplicaType,
    ReplicaStatus,
    ReplicationStrategy as ReplicaReplicationStrategy,
    LoadBalancingStrategy as ReplicaLoadBalancingStrategy,
    GeographicRegion,
    ReplicaNode,
    ReplicationConfiguration as ReplicaConfiguration,
    FailoverEvent,
    initialize_replica_management_system
)

from .transaction_coordinator import (
    TransactionCoordinator,
    TransactionStatus,
    IsolationLevel,
    TransactionType,
    SagaStepStatus,
    TransactionContext,
    TransactionParticipant,
    SagaStep,
    SagaTransaction,
    DeadlockInfo,
    initialize_transaction_coordinator
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
    "initialize_sharding_controller",
    
    # Phase 2: Performance & Monitoring
    # Backup Automation Manager
    "BackupAutomationManager",
    "BackupType",
    "BackupStatus", 
    "CompressionLevel",
    "EncryptionMethod",
    "BackupConfiguration",
    "BackupJob",
    "RestoreRequest",
    "initialize_backup_automation_manager",
    
    # Performance Monitoring Dashboard
    "PerformanceMonitoringDashboard",
    "MetricType",
    "AlertLevel",
    "MonitoringDatabaseEngine",
    "PerformanceMetric",
    "MonitoringQueryMetrics",
    "MonitoringPerformanceAlert",
    "DatabaseHealthScore",
    "initialize_performance_monitoring_dashboard",
    
    # Replica Management System
    "ReplicaManagementSystem",
    "ReplicaType",
    "ReplicaStatus",
    "ReplicaReplicationStrategy",
    "ReplicaLoadBalancingStrategy",
    "GeographicRegion",
    "ReplicaNode",
    "ReplicaConfiguration",
    "FailoverEvent",
    "initialize_replica_management_system",
    
    # Transaction Coordinator
    "TransactionCoordinator",
    "TransactionStatus",
    "IsolationLevel",
    "TransactionType",
    "SagaStepStatus",
    "TransactionContext",
    "TransactionParticipant",
    "SagaStep",
    "SagaTransaction",
    "DeadlockInfo",
    "initialize_transaction_coordinator"
]