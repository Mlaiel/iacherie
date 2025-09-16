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

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    "EnterpriseDatabaseOptimizer",
    "DatabaseConfiguration",
    "DatabaseNode", 
    "DatabaseType",
    "ReplicationStrategy",
    "BackupStrategy",
    "OptimizationLevel",
    "QueryMetrics",
    "PerformanceAlert",
    "initialize_database_optimizer"
]