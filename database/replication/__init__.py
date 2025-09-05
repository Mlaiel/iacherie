"""🔄 Database Replication Module - Enterprise High Availability System
========================================================================
Module: database/replication/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Database Replication & High Availability Architect
Type: Core Module Interface & Exports - Enterprise Production-Ready
Responsibility: Central interface for comprehensive database replication management
================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This module provides the central interface for enterprise database replication:
- Multi-database replication orchestration
- Real-time streaming replication with automated failover
- Cross-region data synchronization
- Performance monitoring and analytics
- Automated disaster recovery
"""

from typing import Dict, Any, Optional, List

# Core replication management exports
from .replication_manager import (
    ReplicationManager,
    ReplicationOrchestrator,
    GlobalReplicationCoordinator
)

# Database-specific replication handlers
from .database_replication import (
    PostgreSQLReplicationHandler,
    MongoDBReplicationHandler,
    ElasticsearchReplicationHandler,
    DatabaseReplicationCoordinator
)

# Cache and vector database replication
from .cache_replication import (
    RedisReplicationHandler,
    VectorDatabaseReplicationHandler,
    CacheReplicationCoordinator
)

# Configuration and topology management
from .replication_config import (
    ReplicationConfig,
    TopologyManager,
    SecurityManager,
    NetworkOptimizer
)

# Monitoring and analytics
from .replication_monitoring import (
    ReplicationMonitor,
    PerformanceAnalyzer,
    HealthTracker,
    MetricsCollector
)

# Failover and recovery management
from .failover_manager import (
    FailoverManager,
    RecoveryOrchestrator,
    DisasterRecoveryManager,
    HealthAssessment
)

# Export all public interfaces
__all__ = [
    # Core management
    'ReplicationManager',
    'ReplicationOrchestrator', 
    'GlobalReplicationCoordinator',
    
    # Database replication
    'PostgreSQLReplicationHandler',
    'MongoDBReplicationHandler',
    'ElasticsearchReplicationHandler',
    'DatabaseReplicationCoordinator',
    
    # Cache replication
    'RedisReplicationHandler',
    'VectorDatabaseReplicationHandler',
    'CacheReplicationCoordinator',
    
    # Configuration management
    'ReplicationConfig',
    'TopologyManager',
    'SecurityManager',
    'NetworkOptimizer',
    
    # Monitoring and analytics
    'ReplicationMonitor',
    'PerformanceAnalyzer',
    'HealthTracker',
    'MetricsCollector',
    
    # Failover and recovery
    'FailoverManager',
    'RecoveryOrchestrator',
    'DisasterRecoveryManager',
    'HealthAssessment',
]

# Module version and metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary - All Rights Reserved"
__copyright__ = "Copyright (c) 2025 Fahed Mlaiel"

# Quick access factory functions
def get_replication_manager() -> ReplicationManager:
    """Get the global replication manager instance."""
    return ReplicationManager()

def get_failover_manager() -> FailoverManager:
    """Get the global failover manager instance.""" 
    return FailoverManager()

def get_monitoring_system() -> ReplicationMonitor:
    """Get the global monitoring system instance."""
    return ReplicationMonitor()

# Enterprise feature flags
ENTERPRISE_FEATURES = {
    'multi_master_replication': True,
    'cross_region_sync': True,
    'automated_failover': True,
    'performance_optimization': True,
    'conflict_resolution': True,
    'disaster_recovery': True,
    'real_time_monitoring': True,
    'intelligent_routing': True,
}

# Support information
SUPPORT_INFO = {
    'contact_email': 'mlaiel@live.de',
    'documentation': 'See README.md for complete documentation',
    'enterprise_support': 'Available for licensed customers',
    'legal_notice': 'Unauthorized use strictly prohibited',
}

def get_module_info() -> Dict[str, Any]:
    """Get comprehensive module information."""
    return {
        'module': 'database.replication',
        'version': __version__,
        'author': __author__,
        'contact': __email__,
        'license': __license__,
        'copyright': __copyright__,
        'features': ENTERPRISE_FEATURES,
        'support': SUPPORT_INFO,
    }