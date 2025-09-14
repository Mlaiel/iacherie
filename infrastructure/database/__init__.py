"""
Database Infrastructure Management
Enterprise database management for Ainflue platform

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

# Database management modules
try:
    from .postgresql_cluster import PostgreSQLCluster
except ImportError:
    PostgreSQLCluster = None

try:
    from .redis_cluster import RedisCluster
except ImportError:
    RedisCluster = None

try:
    from .mongodb_cluster import MongoDBCluster
except ImportError:
    MongoDBCluster = None

try:
    from .elasticsearch_cluster import ElasticsearchCluster
except ImportError:
    ElasticsearchCluster = None

try:
    from .vector_database_manager import VectorDatabaseManager
except ImportError:
    VectorDatabaseManager = None

try:
    from .backup_manager import BackupManager
except ImportError:
    BackupManager = None

try:
    from .migration_manager import MigrationManager
except ImportError:
    MigrationManager = None

try:
    from .replication_manager import ReplicationManager
except ImportError:
    ReplicationManager = None

try:
    from .performance_tuner import PerformanceTuner
except ImportError:
    PerformanceTuner = None

# Enterprise database optimization (Expert Implementation)
try:
    from .enterprise_performance_optimizer import DatabasePerformanceOptimizer
except ImportError:
    DatabasePerformanceOptimizer = None

__all__ = [
    'PostgreSQLCluster',
    'RedisCluster',
    'MongoDBCluster', 
    'ElasticsearchCluster',
    'VectorDatabaseManager',
    'BackupManager',
    'MigrationManager',
    'ReplicationManager',
    'PerformanceTuner',
    'DatabasePerformanceOptimizer'
]