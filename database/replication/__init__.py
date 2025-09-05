"""🔄 Database Replication Module - Enterprise Replication Management
========================================================================
Module: database/replication/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Core Module Interface & Exports
Responsibility: Complete database replication orchestration for multi-format content platform
===========================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This module provides comprehensive database replication for:
- Multi-database replication orchestration (PostgreSQL, Redis, MongoDB, Elasticsearch)
- Intelligent sharding strategies for high-volume content data
- Real-time streaming replication with automated failover
- Cross-region data synchronization and geo-distribution
- Conflict detection and resolution for multi-master setups
- High availability with automated topology management
- Performance monitoring and lag analysis
- Disaster recovery with automated failback procedures
"""

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "Copyright (c) 2025 Fahed Mlaiel. All rights reserved."

# Core replication imports will be added as modules are implemented
__all__ = [
    # Core interfaces and enums
    "ReplicationMode",
    "ReplicationStatus", 
    "NodeRole",
    "ConflictResolution",
    
    # Configuration classes
    "ReplicationConfig",
    "DatabaseConfig",
    "ShardConfig",
    "NodeConfig",
    "MonitoringConfig",
    
    # Main managers and coordinators
    "ReplicationManager",
    "DatabaseReplicationManager", 
    "CacheReplicationManager",
    "FailoverManager",
    "ReplicationMonitor",
    
    # Database-specific handlers
    "PostgreSQLReplicationHandler",
    "RedisReplicationHandler", 
    "MongoDBReplicationHandler",
    "ElasticsearchReplicationHandler",
    "VectorStoreReplicationHandler",
    
    # Monitoring and metrics
    "ReplicationMetrics",
    "HealthMonitor",
    "PerformanceAnalyzer",
    
    # Utilities
    "ReplicationUtils",
    "ConflictResolver",
    "TopologyManager"
]

# Module level logger
import logging
logger = logging.getLogger(__name__)

# Import core enums and constants
from enum import Enum

class ReplicationMode(Enum):
    """Replication mode enumeration."""
    MASTER_SLAVE = "master_slave"
    MASTER_MASTER = "master_master"
    REPLICA_SET = "replica_set"
    CLUSTER = "cluster"
    STREAMING = "streaming"

class ReplicationStatus(Enum):
    """Replication status enumeration."""
    INITIALIZING = "initializing"
    SYNCING = "syncing"
    ACTIVE = "active"
    LAGGING = "lagging"
    FAILED = "failed"
    STOPPED = "stopped"

class NodeRole(Enum):
    """Node role enumeration."""
    MASTER = "master"
    SLAVE = "slave"
    REPLICA = "replica"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    ARBITER = "arbiter"

class ConflictResolution(Enum):
    """Conflict resolution strategy enumeration."""
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MANUAL_RESOLUTION = "manual_resolution"
    TIMESTAMP_BASED = "timestamp_based"
    PRIORITY_BASED = "priority_based"
    MERGE_STRATEGY = "merge_strategy"

# Initialize module
def initialize_replication_module():
    """Initialize the database replication module."""
    logger.info("🔄 Initializing Database Replication Module v%s", __version__)
    logger.info("📧 Author: %s (%s)", __author__, __email__)
    logger.info("⚖️ %s", __copyright__)
    logger.info("✅ Database Replication Module initialized successfully")

# Auto-initialize when module is imported
initialize_replication_module()