"""
Database Optimizations Module

This module provides enterprise-level database optimization capabilities for the IA Influencer Agent platform.
Includes query optimization, connection management, intelligent caching, and performance monitoring with
specialized support for content protection, monetization, and multimedia processing.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

from .cache_manager import CacheManager, CacheStrategy, CacheConfig
from .connection_optimizer import (
    ConnectionOptimizer, 
    ConnectionPoolConfig,
    ContentProtectionConnectionManager,
    MonetizationConnectionManager,
    MultimediaConnectionManager,
    AIProcessingConnectionManager
)
from .index_optimizer import (
    IndexOptimizer, 
    IndexStrategy, 
    IndexAnalyzer,
    ContentProtectionIndexOptimizer,
    MonetizationIndexOptimizer,
    MultimediaIndexOptimizer,
    AIProcessingIndexOptimizer
)
from .performance_analyzer import PerformanceAnalyzer, QueryMetrics, PerformanceReport
from .query_optimizer import QueryOptimizer, QueryPlan, ExecutionPlan
from .resource_monitor import (
    ResourceMonitor, 
    ResourceMetrics, 
    ResourceAlert,
    ContentProtectionResourceMonitor,
    MonetizationResourceMonitor,
    MultimediaResourceMonitor,
    AIProcessingResourceMonitor
)
from .batch_processor import BatchProcessor, BatchConfig, BatchResult
from .execution_planner import (
    ExecutionPlanner, 
    PlanOptimizer, 
    CostEstimator,
    ContentProtectionExecutionPlanner,
    MonetizationExecutionPlanner,
    MultimediaExecutionPlanner,
    AIProcessingExecutionPlanner
)

__all__ = [
    # Core Cache Management
    'CacheManager',
    'CacheStrategy', 
    'CacheConfig',
    
    # Connection Optimization
    'ConnectionOptimizer',
    'ConnectionPoolConfig',
    'ContentProtectionConnectionManager',
    'MonetizationConnectionManager',
    'MultimediaConnectionManager',
    'AIProcessingConnectionManager',
    
    # Index Management
    'IndexOptimizer',
    'IndexStrategy',
    'IndexAnalyzer',
    'ContentProtectionIndexOptimizer',
    'MonetizationIndexOptimizer',
    'MultimediaIndexOptimizer',
    'AIProcessingIndexOptimizer',
    
    # Performance Monitoring
    'PerformanceAnalyzer',
    'QueryMetrics',
    'PerformanceReport',
    
    # Query Optimization
    'QueryOptimizer',
    'QueryPlan',
    'ExecutionPlan',
    
    # Resource Management
    'ResourceMonitor',
    'ResourceMetrics',
    'ResourceAlert',
    'ContentProtectionResourceMonitor',
    'MonetizationResourceMonitor',
    'MultimediaResourceMonitor',
    'AIProcessingResourceMonitor',
    
    # Batch Processing
    'BatchProcessor',
    'BatchConfig',
    'BatchResult',
    
    # Execution Planning
    'ExecutionPlanner',
    'PlanOptimizer',
    'CostEstimator',
    'ContentProtectionExecutionPlanner',
    'MonetizationExecutionPlanner',
    'MultimediaExecutionPlanner',
    'AIProcessingExecutionPlanner',
]

__version__ = '2.0.0'
__author__ = 'Fahed Mlaiel'
__email__ = 'mlaiel@live.de'
__description__ = 'Ultra-advanced database optimization module for IA Influencer Agent platform'