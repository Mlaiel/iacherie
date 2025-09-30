"""
Database Module - Ainflue Infrastructure
=======================================
Enterprise-grade database management and optimization infrastructure

This module provides comprehensive database management capabilities including:
- Multi-database clustering (PostgreSQL, MongoDB, Redis, Elasticsearch)
- Performance optimization and tuning
- Backup and replication management
- Vector database support for AI/ML workloads

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Infrastructure Enterprise
Version: 1.0 Production
"""

import logging

logger = logging.getLogger(__name__)

try:
    from .backup_manager import BackupManager
except ImportError as e:
    logger.warning(f"BackupManager import failed: {e}")
    BackupManager = None

try:
    from .elasticsearch_cluster import ElasticsearchCluster
except ImportError as e:
    logger.warning(f"ElasticsearchCluster import failed: {e}")
    ElasticsearchCluster = None

try:
    from .enterprise_performance_optimizer import EnterprisePerformanceOptimizer
except ImportError as e:
    logger.warning(f"EnterprisePerformanceOptimizer import failed: {e}")
    EnterprisePerformanceOptimizer = None

try:
    from .migration_manager import MigrationManager
except ImportError as e:
    logger.warning(f"MigrationManager import failed: {e}")
    MigrationManager = None

try:
    from .mongodb_cluster import MongoDBCluster
except ImportError as e:
    logger.warning(f"MongoDBCluster import failed: {e}")
    MongoDBCluster = None

try:
    from .performance_tuner import PerformanceTuner
except ImportError as e:
    logger.warning(f"PerformanceTuner import failed: {e}")
    PerformanceTuner = None

try:
    from .postgresql_cluster import PostgreSQLCluster
except ImportError as e:
    logger.warning(f"PostgreSQLCluster import failed: {e}")
    PostgreSQLCluster = None

try:
    from .redis_cluster import RedisCluster
except ImportError as e:
    logger.warning(f"RedisCluster import failed: {e}")
    RedisCluster = None

try:
    from .replication_manager import ReplicationManager
except ImportError as e:
    logger.warning(f"ReplicationManager import failed: {e}")
    ReplicationManager = None

try:
    from .vector_database_manager import VectorDatabaseManager
except ImportError as e:
    logger.warning(f"VectorDatabaseManager import failed: {e}")
    VectorDatabaseManager = None

# Exports publics
__all__ = [
    'BackupManager',
    'ElasticsearchCluster', 
    'EnterprisePerformanceOptimizer',
    'MigrationManager',
    'MongoDBCluster',
    'PerformanceTuner',
    'PostgreSQLCluster',
    'RedisCluster',
    'ReplicationManager',
    'VectorDatabaseManager'
]

# Metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise database management infrastructure"

# Configuration logique métier Ainflue
AINFLUE_DATABASE_CONFIG = {
    'upload': 'Multi-format content storage with vector indexing',
    'ai_processing': 'Vector database for AI model serving and caching', 
    'protection': 'Rights protection data with blockchain integration',
    'monetization': 'Revenue optimization data analytics storage',
    'collaboration': 'Creator matching data and relationship storage',
    'seo': 'SEO data optimization across 644 languages',
    'distribution': 'Platform distribution data for 65+ platforms'
}

# Database performance targets
DATABASE_PERFORMANCE_TARGETS = {
    'query_latency_ms': 50,
    'throughput_qps': 10000,
    'availability_percent': 99.99,
    'backup_frequency_hours': 1,
    'replication_lag_ms': 100
}