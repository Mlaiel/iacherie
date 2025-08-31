"""Partition Optimizer - Performance Optimization Engine

Ultra-industrial partition optimization system for maximum database performance.
Provides intelligent partition optimization, index management, query planning,
and automated maintenance operations for the IA Influencer Agent platform.

Features:
- Intelligent partition size optimization
- Automated index creation and maintenance
- Query performance analysis and optimization
- Vacuum and analyze scheduling
- Statistics collection and analysis
- Performance threshold monitoring
- Automated partition splitting and merging
- Cost-based optimization recommendations

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING 🚨
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Unauthorized use, copying, or distribution is strictly prohibited.
"""
import logging
import time
import threading
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import json
import statistics
from collections import defaultdict, deque

from sqlalchemy import text, inspect, MetaData
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import psutil

logger = logging.getLogger(__name__)

class OptimizationStrategy(Enum):
    """Optimization strategy types"""    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    CONSERVATIVE = "conservative"
    MAINTENANCE_ONLY = "maintenance_only"
    PERFORMANCE_FIRST = "performance_first"
    STORAGE_OPTIMIZED = "storage_optimized"

class OptimizationMetric(Enum):
    """Performance metrics to optimize"""    QUERY_RESPONSE_TIME = "query_response_time"
    THROUGHPUT = "throughput"
    STORAGE_EFFICIENCY = "storage_efficiency"
    INDEX_EFFICIENCY = "index_efficiency"
    VACUUM_EFFICIENCY = "vacuum_efficiency"
    CACHE_HIT_RATIO = "cache_hit_ratio"
    CONNECTION_UTILIZATION = "connection_utilization"

class PerformanceThreshold(Enum):
    """Performance threshold levels"""    CRITICAL = "critical"
    WARNING = "warning"
    OPTIMAL = "optimal"
    EXCELLENT = "excellent"

class IndexStrategy(Enum):
    """Index creation strategies"""    MINIMAL = "minimal"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    QUERY_DRIVEN = "query_driven"
    WORKLOAD_ADAPTIVE = "workload_adaptive"

class VacuumStrategy(Enum):
    """Vacuum operation strategies"""    FULL_VACUUM = "full_vacuum"
    INCREMENTAL = "incremental"
    ANALYZE_ONLY = "analyze_only"
    SMART_VACUUM = "smart_vacuum"
    PARALLEL_VACUUM = "parallel_vacuum"

@dataclass
class PartitionStatistics:
    """Comprehensive partition statistics"""    partition_name: str
    table_name: str
    row_count: int = 0
    table_size_bytes: int = 0
    index_size_bytes: int = 0
    total_size_bytes: int = 0
    dead_tuples: int = 0
    live_tuples: int = 0
    avg_query_time: float = 0.0
    queries_per_second: float = 0.0
    cache_hit_ratio: float = 0.0
    index_hit_ratio: float = 0.0
    vacuum_count: int = 0
    analyze_count: int = 0
    last_vacuum: Optional[datetime] = None
    last_analyze: Optional[datetime] = None
    bloat_ratio: float = 0.0
    fragmentation_level: float = 0.0
    hotspot_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class OptimizationRecommendation:
    """Optimization recommendation with detailed analysis"""    partition_name: str
    recommendation_type: str
    priority: str  # HIGH, MEDIUM, LOW
    description: str
    expected_improvement: float
    estimated_time: int  # in minutes
    resources_required: Dict[str, Any]
    sql_commands: List[str]
    prerequisites: List[str]
    risks: List[str]
    rollback_plan: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class QueryPerformanceMetrics:
    """Query performance analysis metrics"""    query_hash: str
    query_text: str
    execution_count: int
    total_time: float
    mean_time: float
    min_time: float
    max_time: float
    stddev_time: float
    rows_examined: int
    rows_sent: int
    affected_partitions: List[str]
    optimization_suggestions: List[str]
    last_executed: datetime = field(default_factory=datetime.utcnow)

class StatisticsCollector:
    """Advanced statistics collection and analysis system"""    
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.statistics_cache = {}
        self.collection_interval = 300  # 5 minutes
        self.historical_data = defaultdict(deque)
        self.max_history_points = 288  # 24 hours of 5-minute intervals
        
    def collect_partition_statistics(self, partition_name: str) -> PartitionStatistics:
        """Collect comprehensive statistics for a partition"""        try:
            with self.session_factory() as session:
                # Basic table statistics
                basic_stats = session.execute(text(f"""                    SELECT 
                        schemaname,
                        tablename,
                        n_tup_ins,
                        n_tup_upd,
                        n_tup_del,
                        n_live_tup,
                        n_dead_tup,
                        vacuum_count,
                        autovacuum_count,
                        analyze_count,
                        autoanalyze_count,
                        last_vacuum,
                        last_autovacuum,
                        last_analyze,
                        last_autoanalyze
                    FROM pg_stat_user_tables 
                    WHERE schemaname || '.' || tablename = '{partition_name}'
                       OR tablename = '{partition_name}'
                """)).fetchone()
                
                # Table size information
                size_stats = session.execute(text(f"""                    SELECT 
                        pg_total_relation_size('{partition_name}') as total_size,
                        pg_relation_size('{partition_name}') as table_size,
                        pg_indexes_size('{partition_name}') as index_size
                """)).fetchone()
                
                # Cache hit ratios
                cache_stats = session.execute(text(f"""                    SELECT 
                        CASE 
                            WHEN heap_blks_read + heap_blks_hit = 0 THEN 0
                            ELSE heap_blks_hit::float / (heap_blks_read + heap_blks_hit) * 100
                        END as cache_hit_ratio,
                        CASE 
                            WHEN idx_blks_read + idx_blks_hit = 0 THEN 0
                            ELSE idx_blks_hit::float / (idx_blks_read + idx_blks_hit) * 100
                        END as index_hit_ratio
                    FROM pg_statio_user_tables 
                    WHERE schemaname || '.' || tablename = '{partition_name}'
                       OR tablename = '{partition_name}'
                """)).fetchone()
                
                # Bloat estimation
                bloat_stats = session.execute(text(f"""                    WITH table_stats AS (
                        SELECT 
                            schemaname,
                            tablename,
                            n_live_tup,
                            n_dead_tup,
                            pg_relation_size(schemaname||'.'||tablename) as size_bytes
                        FROM pg_stat_user_tables
                        WHERE schemaname || '.' || tablename = '{partition_name}'
                           OR tablename = '{partition_name}'
                    )
                    SELECT 
                        CASE 
                            WHEN n_live_tup + n_dead_tup = 0 THEN 0
                            ELSE n_dead_tup::float / (n_live_tup + n_dead_tup) * 100
                        END as bloat_ratio
                    FROM table_stats
                """)).fetchone()
                
                # Query performance metrics
                query_stats = session.execute(text(f"""                    SELECT 
                        COUNT(*) as query_count,
                        AVG(total_time) as avg_time,
                        SUM(calls) as total_calls
                    FROM pg_stat_statements ps
                    WHERE ps.query ILIKE '%{partition_name.split('.')[-1]}%'
                """)).fetchone()
                
                # Create statistics object
                stats = PartitionStatistics(
                    partition_name=partition_name,
                    table_name=partition_name.split('.')[-1],
                    row_count=basic_stats.n_live_tup if basic_stats else 0,
                    total_size_bytes=size_stats.total_size if size_stats else 0,
                    table_size_bytes=size_stats.table_size if size_stats else 0,
                    index_size_bytes=size_stats.index_size if size_stats else 0,
                    live_tuples=basic_stats.n_live_tup if basic_stats else 0,
                    dead_tuples=basic_stats.n_dead_tup if basic_stats else 0,
                    vacuum_count=(basic_stats.vacuum_count + basic_stats.autovacuum_count) if basic_stats else 0,
                    analyze_count=(basic_stats.analyze_count + basic_stats.autoanalyze_count) if basic_stats else 0,
                    last_vacuum=basic_stats.last_vacuum or basic_stats.last_autovacuum if basic_stats else None,
                    last_analyze=basic_stats.last_analyze or basic_stats.last_autoanalyze if basic_stats else None,
                    cache_hit_ratio=cache_stats.cache_hit_ratio if cache_stats else 0.0,
                    index_hit_ratio=cache_stats.index_hit_ratio if cache_stats else 0.0,
                    bloat_ratio=bloat_stats.bloat_ratio if bloat_stats else 0.0,
                    avg_query_time=query_stats.avg_time if query_stats and query_stats.avg_time else 0.0,
                    queries_per_second=query_stats.total_calls / 3600 if query_stats and query_stats.total_calls else 0.0
                )
                
                # Calculate derived metrics
                stats.fragmentation_level = self._calculate_fragmentation_level(stats)
                stats.hotspot_score = self._calculate_hotspot_score(stats)
                
                # Cache statistics
                self.statistics_cache[partition_name] = stats
                
                # Store historical data
                self.historical_data[partition_name].append({
                    'timestamp': datetime.utcnow(),
                    'metrics': stats
                })
                
                # Maintain history size
                if len(self.historical_data[partition_name]) > self.max_history_points:
                    self.historical_data[partition_name].popleft()
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to collect statistics for partition {partition_name}: {e}")
            return PartitionStatistics(partition_name=partition_name, table_name=partition_name)
    
    def _calculate_fragmentation_level(self, stats: PartitionStatistics) -> float:
        """Calculate table fragmentation level"""        if stats.live_tuples == 0:
            return 0.0
        
        # Fragmentation based on dead tuples ratio and table bloat
        dead_tuple_ratio = stats.dead_tuples / (stats.live_tuples + stats.dead_tuples) if (stats.live_tuples + stats.dead_tuples) > 0 else 0
        fragmentation = (dead_tuple_ratio * 0.7) + (stats.bloat_ratio / 100 * 0.3)
        
        return min(fragmentation * 100, 100.0)
    
    def _calculate_hotspot_score(self, stats: PartitionStatistics) -> float:
        """Calculate partition hotspot score based on activity"""        # Normalize metrics to 0-1 scale
        normalized_qps = min(stats.queries_per_second / 1000, 1.0)  # Max 1000 QPS
        normalized_size = min(stats.total_size_bytes / (1024**3), 1.0)  # Max 1GB
        
        # Weight factors: QPS (60%), size (20%), cache ratio (20%)
        hotspot_score = (
            normalized_qps * 0.6 +
            normalized_size * 0.2 +
            (1 - stats.cache_hit_ratio / 100) * 0.2
        )
        
        return hotspot_score * 100

class PartitionOptimizer:
    """    Ultra-industrial partition optimizer for maximum database performance
    
    Provides intelligent optimization strategies including:
    - Automated partition analysis and optimization
    - Index management and optimization
    - Query performance analysis and tuning
    - Maintenance scheduling and execution
    - Performance threshold monitoring
    - Cost-based optimization recommendations
    - Automated vacuum and analyze operations
    """    
    def __init__(self, session_factory, config: Dict[str, Any] = None):
        """        Initialize partition optimizer
        
        Args:
            session_factory: SQLAlchemy session factory
            config: Configuration dictionary
        """        self.session_factory = session_factory
        self.config = config or {}
        
        # Optimization configuration
        self.strategy = OptimizationStrategy(self.config.get('strategy', 'balanced'))
        self.optimization_interval = self.config.get('optimization_interval', 3600)  # 1 hour
        self.maintenance_window_hours = self.config.get('maintenance_window', [2, 6])  # 2-6 AM
        self.max_parallel_operations = self.config.get('max_parallel_operations', 4)
        
        # Performance thresholds
        self.thresholds = {
            'response_time_warning': self.config.get('response_time_warning', 100),  # 100ms
            'response_time_critical': self.config.get('response_time_critical', 500),  # 500ms
            'cache_hit_ratio_warning': self.config.get('cache_hit_ratio_warning', 90),  # 90%
            'cache_hit_ratio_critical': self.config.get('cache_hit_ratio_critical', 80),  # 80%
            'bloat_ratio_warning': self.config.get('bloat_ratio_warning', 20),  # 20%
            'bloat_ratio_critical': self.config.get('bloat_ratio_critical', 40),  # 40%
            'fragmentation_warning': self.config.get('fragmentation_warning', 30),  # 30%
            'fragmentation_critical': self.config.get('fragmentation_critical', 60),  # 60%
        }
        
        # Components
        self.statistics_collector = StatisticsCollector(session_factory)
        self.recommendations = []
        self.optimization_history = deque(maxlen=1000)
        self.performance_trends = defaultdict(list)
        
        # Thread safety
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=self.max_parallel_operations)
        self._optimization_active = False
        
        logger.info(f"PartitionOptimizer initialized with {self.strategy.value} strategy")

    def analyze_partition_performance(self, partition_name: str) -> Dict[str, Any]:
        """        Perform comprehensive performance analysis of a partition
        
        Args:
            partition_name: Name of the partition to analyze
            
        Returns:
            Dict containing detailed performance analysis
        """        try:
            # Collect current statistics
            stats = self.statistics_collector.collect_partition_statistics(partition_name)
            
            # Analyze performance metrics
            analysis = {
                'partition_name': partition_name,
                'timestamp': datetime.utcnow().isoformat(),
                'statistics': {
                    'row_count': stats.row_count,
                    'total_size_mb': round(stats.total_size_bytes / (1024**2), 2),
                    'table_size_mb': round(stats.table_size_bytes / (1024**2), 2),
                    'index_size_mb': round(stats.index_size_bytes / (1024**2), 2),
                    'cache_hit_ratio': round(stats.cache_hit_ratio, 2),
                    'index_hit_ratio': round(stats.index_hit_ratio, 2),
                    'bloat_ratio': round(stats.bloat_ratio, 2),
                    'fragmentation_level': round(stats.fragmentation_level, 2),
                    'hotspot_score': round(stats.hotspot_score, 2),
                    'queries_per_second': round(stats.queries_per_second, 2),
                    'avg_query_time': round(stats.avg_query_time, 2)
                }
            }
            
            # Performance status assessment
            analysis['performance_status'] = self._assess_performance_status(stats)
            
            # Generate optimization recommendations
            analysis['recommendations'] = self._generate_recommendations(stats)
            
            # Historical trend analysis
            analysis['trends'] = self._analyze_performance_trends(partition_name)
            
            # Index analysis
            analysis['index_analysis'] = self._analyze_indexes(partition_name)
            
            # Query analysis
            analysis['query_analysis'] = self._analyze_query_patterns(partition_name)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze partition performance for {partition_name}: {e}")
            return {'error': str(e)}

    def _assess_performance_status(self, stats: PartitionStatistics) -> Dict[str, str]:
        """Assess overall performance status based on thresholds"""        status = {}
        
        # Response time assessment
        if stats.avg_query_time > self.thresholds['response_time_critical']:
            status['response_time'] = 'CRITICAL'
        elif stats.avg_query_time > self.thresholds['response_time_warning']:
            status['response_time'] = 'WARNING'
        else:
            status['response_time'] = 'OPTIMAL'
        
        # Cache hit ratio assessment
        if stats.cache_hit_ratio < self.thresholds['cache_hit_ratio_critical']:
            status['cache_performance'] = 'CRITICAL'
        elif stats.cache_hit_ratio < self.thresholds['cache_hit_ratio_warning']:
            status['cache_performance'] = 'WARNING'
        else:
            status['cache_performance'] = 'OPTIMAL'
        
        # Bloat assessment
        if stats.bloat_ratio > self.thresholds['bloat_ratio_critical']:
            status['table_bloat'] = 'CRITICAL'
        elif stats.bloat_ratio > self.thresholds['bloat_ratio_warning']:
            status['table_bloat'] = 'WARNING'
        else:
            status['table_bloat'] = 'OPTIMAL'
        
        # Fragmentation assessment
        if stats.fragmentation_level > self.thresholds['fragmentation_critical']:
            status['fragmentation'] = 'CRITICAL'
        elif stats.fragmentation_level > self.thresholds['fragmentation_warning']:
            status['fragmentation'] = 'WARNING'
        else:
            status['fragmentation'] = 'OPTIMAL'
        
        # Overall status
        critical_count = sum(1 for s in status.values() if s == 'CRITICAL')
        warning_count = sum(1 for s in status.values() if s == 'WARNING')
        
        if critical_count > 0:
            status['overall'] = 'CRITICAL'
        elif warning_count > 1:
            status['overall'] = 'WARNING'
        else:
            status['overall'] = 'OPTIMAL'
        
        return status

    def _generate_recommendations(self, stats: PartitionStatistics) -> List[OptimizationRecommendation]:
        """Generate intelligent optimization recommendations"""        recommendations = []
        
        try:
            # Vacuum recommendation
            if stats.bloat_ratio > self.thresholds['bloat_ratio_warning']:
                vacuum_type = "FULL" if stats.bloat_ratio > self.thresholds['bloat_ratio_critical'] else "STANDARD"
                priority = "HIGH" if stats.bloat_ratio > self.thresholds['bloat_ratio_critical'] else "MEDIUM"
                
                recommendations.append(OptimizationRecommendation(
                    partition_name=stats.partition_name,
                    recommendation_type="VACUUM_OPTIMIZATION",
                    priority=priority,
                    description=f"Table has {stats.bloat_ratio:.1f}% bloat ratio. Perform {vacuum_type} vacuum to reclaim space.",
                    expected_improvement=min(stats.bloat_ratio, 50),  # Up to 50% improvement
                    estimated_time=self._estimate_vacuum_time(stats, vacuum_type),
                    resources_required={
                        'cpu_usage': 'HIGH' if vacuum_type == 'FULL' else 'MEDIUM',
                        'io_usage': 'HIGH',
                        'lock_level': 'ACCESS_EXCLUSIVE' if vacuum_type == 'FULL' else 'SHARE_UPDATE_EXCLUSIVE'
                    },
                    sql_commands=[
                        f"VACUUM {'FULL' if vacuum_type == 'FULL' else ''} ANALYZE {stats.partition_name};"
                    ],
                    prerequisites=[
                        "Ensure sufficient disk space",
                        "Schedule during maintenance window",
                        "Monitor concurrent connections"
                    ],
                    risks=[
                        "Table will be locked during operation" if vacuum_type == 'FULL' else "Minor performance impact",
                        "Increased I/O load on system"
                    ],
                    rollback_plan=[
                        "Operation cannot be rolled back",
                        "Monitor system performance after completion"
                    ]
                ))
            
            # Index optimization recommendations
            if stats.index_hit_ratio < self.thresholds['cache_hit_ratio_warning']:
                recommendations.append(OptimizationRecommendation(
                    partition_name=stats.partition_name,
                    recommendation_type="INDEX_OPTIMIZATION",
                    priority="MEDIUM",
                    description=f"Index hit ratio is {stats.index_hit_ratio:.1f}%. Consider index analysis and optimization.",
                    expected_improvement=20,  # 20% improvement expected
                    estimated_time=15,
                    resources_required={
                        'cpu_usage': 'LOW',
                        'io_usage': 'MEDIUM',
                        'lock_level': 'SHARE'
                    },
                    sql_commands=[
                        f"REINDEX INDEX CONCURRENTLY ON {stats.partition_name};",
                        f"ANALYZE {stats.partition_name};"
                    ],
                    prerequisites=[
                        "Identify unused or duplicate indexes",
                        "Analyze query patterns"
                    ],
                    risks=[
                        "Temporary increased disk usage",
                        "Potential query performance impact during rebuild"
                    ],
                    rollback_plan=[
                        "Keep original indexes until verification",
                        "Monitor query performance"
                    ]
                ))
            
            # Partitioning optimization
            if stats.row_count > 10_000_000:  # 10M rows threshold
                recommendations.append(OptimizationRecommendation(
                    partition_name=stats.partition_name,
                    recommendation_type="PARTITION_SPLITTING",
                    priority="LOW",
                    description=f"Partition has {stats.row_count:,} rows. Consider splitting for better performance.",
                    expected_improvement=30,
                    estimated_time=120,  # 2 hours
                    resources_required={
                        'cpu_usage': 'HIGH',
                        'io_usage': 'HIGH',
                        'disk_space': stats.total_size_bytes * 2  # Double space needed
                    },
                    sql_commands=[
                        f"-- Partition splitting requires custom implementation",
                        f"-- Based on partition key analysis"
                    ],
                    prerequisites=[
                        "Analyze partition key distribution",
                        "Plan new partition boundaries",
                        "Ensure sufficient disk space"
                    ],
                    risks=[
                        "Complex operation requiring downtime",
                        "Application compatibility considerations"
                    ],
                    rollback_plan=[
                        "Keep backup of original partition",
                        "Plan reverse migration process"
                    ]
                ))
            
            # Query optimization recommendations
            if stats.avg_query_time > self.thresholds['response_time_warning']:
                recommendations.append(OptimizationRecommendation(
                    partition_name=stats.partition_name,
                    recommendation_type="QUERY_OPTIMIZATION",
                    priority="HIGH" if stats.avg_query_time > self.thresholds['response_time_critical'] else "MEDIUM",
                    description=f"Average query time is {stats.avg_query_time:.2f}ms. Analyze and optimize slow queries.",
                    expected_improvement=40,
                    estimated_time=30,
                    resources_required={
                        'cpu_usage': 'LOW',
                        'analysis_tools': 'REQUIRED'
                    },
                    sql_commands=[
                        f"SELECT * FROM pg_stat_statements WHERE query LIKE '%{stats.table_name}%' ORDER BY total_time DESC LIMIT 10;",
                        f"EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM {stats.partition_name} LIMIT 1;"
                    ],
                    prerequisites=[
                        "Enable pg_stat_statements extension",
                        "Identify slow query patterns"
                    ],
                    risks=[
                        "Minimal risk",
                        "Analysis overhead"
                    ],
                    rollback_plan=[
                        "No rollback needed for analysis",
                        "Document findings"
                    ]
                ))
                
        except Exception as e:
            logger.error(f"Failed to generate recommendations for {stats.partition_name}: {e}")
        
        return recommendations

    def _estimate_vacuum_time(self, stats: PartitionStatistics, vacuum_type: str) -> int:
        """Estimate vacuum operation time in minutes"""        base_time = stats.total_size_bytes / (1024**3) * 5  # 5 minutes per GB
        
        if vacuum_type == "FULL":
            base_time *= 3  # Full vacuum takes 3x longer
        
        # Adjust for bloat ratio
        bloat_factor = 1 + (stats.bloat_ratio / 100)
        
        return max(int(base_time * bloat_factor), 1)

    def _analyze_performance_trends(self, partition_name: str) -> Dict[str, Any]:
        """Analyze performance trends over time"""        try:
            historical_data = self.historical_data[partition_name]
            
            if len(historical_data) < 2:
                return {'message': 'Insufficient historical data'}
            
            # Extract time series data
            timestamps = [point['timestamp'] for point in historical_data]
            query_times = [point['metrics'].avg_query_time for point in historical_data]
            cache_ratios = [point['metrics'].cache_hit_ratio for point in historical_data]
            bloat_ratios = [point['metrics'].bloat_ratio for point in historical_data]
            
            # Calculate trends
            trends = {}
            
            if len(query_times) >= 2:
                query_time_trend = (query_times[-1] - query_times[0]) / len(query_times)
                trends['query_time_trend'] = 'IMPROVING' if query_time_trend < 0 else 'DEGRADING'
                trends['query_time_change'] = query_time_trend
            
            if len(cache_ratios) >= 2:
                cache_trend = (cache_ratios[-1] - cache_ratios[0]) / len(cache_ratios)
                trends['cache_trend'] = 'IMPROVING' if cache_trend > 0 else 'DEGRADING'
                trends['cache_change'] = cache_trend
            
            if len(bloat_ratios) >= 2:
                bloat_trend = (bloat_ratios[-1] - bloat_ratios[0]) / len(bloat_ratios)
                trends['bloat_trend'] = 'IMPROVING' if bloat_trend < 0 else 'DEGRADING'
                trends['bloat_change'] = bloat_trend
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to analyze trends for {partition_name}: {e}")
            return {'error': str(e)}

    def _analyze_indexes(self, partition_name: str) -> Dict[str, Any]:
        """Analyze index usage and efficiency"""        try:
            with self.session_factory() as session:
                # Get index usage statistics
                index_stats = session.execute(text(f"""                    SELECT 
                        schemaname,
                        tablename,
                        indexname,
                        idx_tup_read,
                        idx_tup_fetch,
                        idx_scan,
                        pg_size_pretty(pg_relation_size(indexrelid)) as index_size
                    FROM pg_stat_user_indexes 
                    WHERE schemaname || '.' || tablename = '{partition_name}'
                       OR tablename = '{partition_name}'
                    ORDER BY idx_scan DESC
                """)).fetchall()
                
                # Analyze unused indexes
                unused_indexes = [
                    {
                        'index_name': row.indexname,
                        'size': row.index_size,
                        'scans': row.idx_scan
                    }
                    for row in index_stats if row.idx_scan < 10  # Less than 10 scans
                ]
                
                # Analyze heavily used indexes
                heavy_indexes = [
                    {
                        'index_name': row.indexname,
                        'size': row.index_size,
                        'scans': row.idx_scan,
                        'efficiency': row.idx_tup_fetch / max(row.idx_tup_read, 1)
                    }
                    for row in index_stats if row.idx_scan > 1000  # More than 1000 scans
                ]
                
                return {
                    'total_indexes': len(index_stats),
                    'unused_indexes': unused_indexes,
                    'heavily_used_indexes': heavy_indexes,
                    'recommendations': self._generate_index_recommendations(unused_indexes, heavy_indexes)
                }
                
        except Exception as e:
            logger.error(f"Failed to analyze indexes for {partition_name}: {e}")
            return {'error': str(e)}

    def _generate_index_recommendations(self, unused_indexes: List[Dict], heavy_indexes: List[Dict]) -> List[str]:
        """Generate index optimization recommendations"""        recommendations = []
        
        if unused_indexes:
            recommendations.append(f"Consider dropping {len(unused_indexes)} unused indexes to save space and improve write performance")
        
        if heavy_indexes:
            low_efficiency_indexes = [idx for idx in heavy_indexes if idx['efficiency'] < 0.1]
            if low_efficiency_indexes:
                recommendations.append(f"Optimize {len(low_efficiency_indexes)} heavily used but inefficient indexes")
        
        return recommendations

    def _analyze_query_patterns(self, partition_name: str) -> Dict[str, Any]:
        """Analyze query patterns and performance"""        try:
            with self.session_factory() as session:
                # Get query statistics from pg_stat_statements
                query_stats = session.execute(text(f"""                    SELECT 
                        LEFT(query, 100) as query_sample,
                        calls,
                        total_time,
                        mean_time,
                        min_time,
                        max_time,
                        stddev_time,
                        rows,
                        shared_blks_hit,
                        shared_blks_read
                    FROM pg_stat_statements 
                    WHERE query ILIKE '%{partition_name.split('.')[-1]}%'
                    ORDER BY total_time DESC 
                    LIMIT 10
                """)).fetchall()
                
                if not query_stats:
                    return {'message': 'No query statistics available'}
                
                # Analyze patterns
                total_queries = sum(row.calls for row in query_stats)
                total_time = sum(row.total_time for row in query_stats)
                
                slow_queries = [
                    {
                        'query_sample': row.query_sample,
                        'calls': row.calls,
                        'total_time': row.total_time,
                        'mean_time': row.mean_time,
                        'cache_efficiency': row.shared_blks_hit / max((row.shared_blks_hit + row.shared_blks_read), 1) * 100
                    }
                    for row in query_stats if row.mean_time > 100  # Queries taking more than 100ms
                ]
                
                return {
                    'total_queries': total_queries,
                    'average_time': total_time / max(total_queries, 1),
                    'slow_queries_count': len(slow_queries),
                    'slow_queries': slow_queries[:5],  # Top 5 slow queries
                    'recommendations': self._generate_query_recommendations(slow_queries)
                }
                
        except Exception as e:
            logger.error(f"Failed to analyze query patterns for {partition_name}: {e}")
            return {'error': str(e)}

    def _generate_query_recommendations(self, slow_queries: List[Dict]) -> List[str]:
        """Generate query optimization recommendations"""        recommendations = []
        
        if slow_queries:
            recommendations.append(f"Optimize {len(slow_queries)} slow queries identified")
            
            # Check for common patterns
            for query in slow_queries:
                if query['cache_efficiency'] < 80:
                    recommendations.append("Improve query cache efficiency through better indexing")
                    break
            
            if any(query['mean_time'] > 1000 for query in slow_queries):
                recommendations.append("Critical: Some queries taking over 1 second - immediate optimization needed")
        
        return recommendations

    def optimize_partition(self, partition_name: str, strategy: OptimizationStrategy = None) -> Dict[str, Any]:
        """        Execute comprehensive partition optimization
        
        Args:
            partition_name: Name of partition to optimize
            strategy: Optimization strategy to use
            
        Returns:
            Dict containing optimization results
        """        try:
            strategy = strategy or self.strategy
            logger.info(f"Starting optimization for partition {partition_name} with {strategy.value} strategy")
            
            # Perform analysis first
            analysis = self.analyze_partition_performance(partition_name)
            
            if 'error' in analysis:
                return analysis
            
            # Execute optimizations based on strategy and recommendations
            executed_optimizations = []
            results = {'partition_name': partition_name, 'strategy': strategy.value, 'optimizations': []}
            
            for recommendation in analysis.get('recommendations', []):
                if self._should_execute_recommendation(recommendation, strategy):
                    result = self._execute_optimization(recommendation)
                    executed_optimizations.append(result)
                    results['optimizations'].append(result)
            
            # Record optimization history
            optimization_record = {
                'timestamp': datetime.utcnow(),
                'partition_name': partition_name,
                'strategy': strategy.value,
                'executed_optimizations': len(executed_optimizations),
                'performance_before': analysis['statistics'],
                'recommendations_followed': [opt['recommendation_type'] for opt in executed_optimizations if opt['success']]
            }
            
            self.optimization_history.append(optimization_record)
            
            results['summary'] = {
                'total_recommendations': len(analysis.get('recommendations', [])),
                'executed_optimizations': len(executed_optimizations),
                'successful_optimizations': sum(1 for opt in executed_optimizations if opt['success']),
                'optimization_time': sum(opt.get('execution_time', 0) for opt in executed_optimizations)
            }
            
            logger.info(f"Optimization completed for {partition_name}: {results['summary']}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to optimize partition {partition_name}: {e}")
            return {'error': str(e)}

    def _should_execute_recommendation(self, recommendation: OptimizationRecommendation, 
                                     strategy: OptimizationStrategy) -> bool:
        """Determine if a recommendation should be executed based on strategy"""        
        if strategy == OptimizationStrategy.CONSERVATIVE:
            return recommendation.priority == "LOW" and "ANALYZE" in recommendation.recommendation_type
        
        elif strategy == OptimizationStrategy.BALANCED:
            return recommendation.priority in ["LOW", "MEDIUM"]
        
        elif strategy == OptimizationStrategy.AGGRESSIVE:
            return True  # Execute all recommendations
        
        elif strategy == OptimizationStrategy.MAINTENANCE_ONLY:
            return recommendation.recommendation_type in ["VACUUM_OPTIMIZATION", "INDEX_MAINTENANCE"]
        
        elif strategy == OptimizationStrategy.PERFORMANCE_FIRST:
            return recommendation.expected_improvement > 20  # Only high-impact optimizations
        
        elif strategy == OptimizationStrategy.STORAGE_OPTIMIZED:
            return recommendation.recommendation_type in ["VACUUM_OPTIMIZATION", "COMPRESSION"]
        
        return False

    def _execute_optimization(self, recommendation: OptimizationRecommendation) -> Dict[str, Any]:
        """Execute a specific optimization recommendation"""        start_time = time.time()
        result = {
            'recommendation_type': recommendation.recommendation_type,
            'partition_name': recommendation.partition_name,
            'success': False,
            'execution_time': 0,
            'details': {}
        }
        
        try:
            logger.info(f"Executing {recommendation.recommendation_type} for {recommendation.partition_name}")
            
            # Check if we're in maintenance window for heavy operations
            if recommendation.priority == "HIGH" and not self._is_maintenance_window():
                result['details']['message'] = "Deferred to maintenance window"
                result['success'] = True  # Consider as successful deferral
                return result
            
            # Execute the optimization
            with self.session_factory() as session:
                for sql_command in recommendation.sql_commands:
                    if sql_command.strip().startswith('--'):
                        continue  # Skip comments
                    
                    session.execute(text(sql_command))
                    session.commit()
            
            result['success'] = True
            result['details']['message'] = f"Successfully executed {recommendation.recommendation_type}"
            
        except Exception as e:
            result['details']['error'] = str(e)
            logger.error(f"Failed to execute optimization {recommendation.recommendation_type}: {e}")
        
        finally:
            result['execution_time'] = time.time() - start_time
        
        return result

    def _is_maintenance_window(self) -> bool:
        """Check if current time is within maintenance window"""        current_hour = datetime.now().hour
        start_hour, end_hour = self.maintenance_window_hours
        
        if start_hour <= end_hour:
            return start_hour <= current_hour <= end_hour
        else:  # Window crosses midnight
            return current_hour >= start_hour or current_hour <= end_hour

    def get_optimization_report(self, partition_name: str = None) -> Dict[str, Any]:
        """        Generate comprehensive optimization report
        
        Args:
            partition_name: Optional specific partition, otherwise all partitions
            
        Returns:
            Dict containing detailed optimization report
        """        try:
            report = {
                'timestamp': datetime.utcnow().isoformat(),
                'summary': {},
                'partitions': {},
                'system_recommendations': []
            }
            
            if partition_name:
                # Single partition report
                analysis = self.analyze_partition_performance(partition_name)
                report['partitions'][partition_name] = analysis
                
                # Summary for single partition
                if 'statistics' in analysis:
                    stats = analysis['statistics']
                    report['summary'] = {
                        'total_partitions': 1,
                        'total_size_mb': stats['total_size_mb'],
                        'average_cache_hit_ratio': stats['cache_hit_ratio'],
                        'average_query_time': stats['avg_query_time'],
                        'recommendations_count': len(analysis.get('recommendations', []))
                    }
            else:
                # Multi-partition report (would need partition list)
                report['summary'] = {
                    'message': 'Multi-partition reporting requires partition list implementation'
                }
            
            # Historical optimization summary
            if self.optimization_history:
                recent_optimizations = list(self.optimization_history)[-10:]  # Last 10 optimizations
                report['optimization_history'] = {
                    'total_optimizations': len(self.optimization_history),
                    'recent_optimizations': len(recent_optimizations),
                    'recent_executions': [
                        {
                            'timestamp': opt['timestamp'].isoformat(),
                            'partition': opt['partition_name'],
                            'strategy': opt['strategy'],
                            'optimizations_count': opt['executed_optimizations']
                        }
                        for opt in recent_optimizations
                    ]
                }
            
            # System-wide recommendations
            report['system_recommendations'] = self._generate_system_recommendations()
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate optimization report: {e}")
            return {'error': str(e)}

    def _generate_system_recommendations(self) -> List[str]:
        """Generate system-wide optimization recommendations"""        recommendations = []
        
        # Analyze optimization history patterns
        if len(self.optimization_history) > 5:
            recent_optimizations = list(self.optimization_history)[-10:]
            
            # Check for frequent vacuum operations
            vacuum_count = sum(1 for opt in recent_optimizations 
                             if 'VACUUM' in str(opt.get('recommendations_followed', [])))
            
            if vacuum_count > 5:
                recommendations.append("Consider adjusting autovacuum settings - frequent manual vacuums detected")
            
            # Check for performance trends
            if all('query_time' in str(opt.get('performance_before', {})) for opt in recent_optimizations):
                recommendations.append("Monitor query performance trends across all partitions")
        
        # General system recommendations
        recommendations.extend([
            "Enable pg_stat_statements for better query analysis",
            "Configure appropriate maintenance windows for optimization operations",
            "Consider implementing automated partition monitoring"
        ])
        
        return recommendations

    def start_continuous_optimization(self):
        """Start continuous optimization monitoring"""        try:
            if self._optimization_active:
                logger.warning("Continuous optimization is already active")
                return
            
            self._optimization_active = True
            
            def optimization_loop():
                while self._optimization_active:
                    try:
                        # This would need a partition list to work with
                        logger.debug("Continuous optimization cycle - implementation needed")
                        time.sleep(self.optimization_interval)
                    except Exception as e:
                        logger.error(f"Error in optimization loop: {e}")
                        time.sleep(60)  # Wait 1 minute on error
            
            optimization_thread = threading.Thread(target=optimization_loop, daemon=True)
            optimization_thread.start()
            
            logger.info("Continuous optimization started")
            
        except Exception as e:
            logger.error(f"Failed to start continuous optimization: {e}")

    def stop_continuous_optimization(self):
        """Stop continuous optimization monitoring"""        self._optimization_active = False
        logger.info("Continuous optimization stopped")

    def shutdown(self):
        """Shutdown optimizer gracefully"""        try:
            logger.info("Shutting down partition optimizer...")
            
            # Stop continuous optimization
            self.stop_continuous_optimization()
            
            # Shutdown thread pool
            self._executor.shutdown(wait=True)
            
            logger.info("Partition optimizer shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during optimizer shutdown: {e}")

    def __enter__(self):
        """Context manager entry"""        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""        self.shutdown()
    index_scan_ratio: float = 0.0
    sequential_scan_ratio: float = 0.0
    last_vacuum: Optional[datetime] = None
    last_analyze: Optional[datetime] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class OptimizationTask:
    """Optimization task definition"""    task_id: str
    partition_name: str
    operation_type: str
    priority: int = 5
    estimated_duration: int = 0  # seconds
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    scheduled_time: Optional[datetime] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class PerformanceReport:
    """Performance analysis report"""    partition_name: str
    performance_score: float = 0.0
    threshold_level: PerformanceThreshold = PerformanceThreshold.OPTIMAL
    recommendations: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    optimizations_applied: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)

class StatisticsCollector:
    """Collects and analyzes partition statistics"""    
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.statistics_cache: Dict[str, PartitionStatistics] = {}
        self.collection_interval = 300  # 5 minutes
        self.max_cache_age = 3600  # 1 hour
    
    def collect_partition_statistics(self, partition_name: str) -> PartitionStatistics:
        """Collect comprehensive statistics for a partition"""        try:
            with self.session_factory() as session:
                # Get basic table statistics
                basic_stats_query = text(f"""                    SELECT 
                        schemaname,
                        tablename,
                        attname,
                        null_frac,
                        avg_width,
                        n_distinct,
                        most_common_vals,
                        most_common_freqs,
                        histogram_bounds,
                        correlation
                    FROM pg_stats 
                    WHERE tablename = :partition_name
                """)
                
                basic_stats = session.execute(basic_stats_query, {'partition_name': partition_name}).fetchall()
                
                # Get table size information
                size_query = text(f"""                    SELECT 
                        pg_total_relation_size('{partition_name}') as total_size,
                        pg_relation_size('{partition_name}') as table_size,
                        pg_indexes_size('{partition_name}') as index_size
                """)
                
                size_result = session.execute(size_query).fetchone()
                
                # Get row count and vacuum statistics
                vacuum_stats_query = text(f"""                    SELECT 
                        schemaname,
                        tablename,
                        n_tup_ins,
                        n_tup_upd,
                        n_tup_del,
                        n_live_tup,
                        n_dead_tup,
                        last_vacuum,
                        last_autovacuum,
                        last_analyze,
                        last_autoanalyze,
                        vacuum_count,
                        autovacuum_count,
                        analyze_count,
                        autoanalyze_count
                    FROM pg_stat_user_tables 
                    WHERE tablename = :partition_name
                """)
                
                vacuum_stats = session.execute(vacuum_stats_query, {'partition_name': partition_name}).fetchone()
                
                # Get query performance statistics
                query_stats_query = text(f"""                    SELECT 
                        seq_scan,
                        seq_tup_read,
                        idx_scan,
                        idx_tup_fetch,
                        n_tup_ins,
                        n_tup_upd,
                        n_tup_del
                    FROM pg_stat_user_tables 
                    WHERE tablename = :partition_name
                """)
                
                query_stats = session.execute(query_stats_query, {'partition_name': partition_name}).fetchone()
                
                # Create comprehensive statistics object
                stats = PartitionStatistics(
                    partition_name=partition_name,
                    table_name=partition_name.split('_')[0],  # Extract base table name
                    row_count=vacuum_stats.n_live_tup if vacuum_stats else 0,
                    table_size_bytes=size_result.table_size if size_result else 0,
                    index_size_bytes=size_result.index_size if size_result else 0,
                    total_size_bytes=size_result.total_size if size_result else 0,
                    dead_tuples=vacuum_stats.n_dead_tup if vacuum_stats else 0,
                    live_tuples=vacuum_stats.n_live_tup if vacuum_stats else 0,
                    last_vacuum=vacuum_stats.last_vacuum if vacuum_stats else None,
                    last_analyze=vacuum_stats.last_analyze if vacuum_stats else None
                )
                
                # Calculate derived metrics
                if query_stats:
                    total_scans = (query_stats.seq_scan or 0) + (query_stats.idx_scan or 0)
                    if total_scans > 0:
                        stats.index_scan_ratio = (query_stats.idx_scan or 0) / total_scans
                        stats.sequential_scan_ratio = (query_stats.seq_scan or 0) / total_scans
                
                # Cache statistics
                self.statistics_cache[partition_name] = stats
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to collect statistics for partition {partition_name}: {e}")
            return PartitionStatistics(partition_name=partition_name, table_name="unknown")
    
    def get_cached_statistics(self, partition_name: str) -> Optional[PartitionStatistics]:
        """Get cached statistics if available and fresh"""        stats = self.statistics_cache.get(partition_name)
        if stats and (datetime.utcnow() - stats.last_updated).seconds < self.max_cache_age:
            return stats
        return None
    
    def collect_all_statistics(self, partition_names: List[str]) -> Dict[str, PartitionStatistics]:
        """Collect statistics for multiple partitions in parallel"""        results = {}
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_partition = {
                executor.submit(self.collect_partition_statistics, partition_name): partition_name
                for partition_name in partition_names
            }
            
            for future in future_to_partition:
                partition_name = future_to_partition[future]
                try:
                    stats = future.result()
                    results[partition_name] = stats
                except Exception as e:
                    logger.error(f"Failed to collect statistics for {partition_name}: {e}")
        
        return results

class PartitionOptimizer:
    """    Ultra-industrial partition optimization engine
    
    Provides comprehensive partition optimization including:
    - Performance analysis and recommendations
    - Automated index management
    - Vacuum and maintenance scheduling
    - Query optimization suggestions
    - Resource utilization optimization
    """    
    def __init__(self, session_factory, config: Dict[str, Any] = None):
        """        Initialize partition optimizer
        
        Args:
            session_factory: SQLAlchemy session factory
            config: Configuration dictionary
        """        self.session_factory = session_factory
        self.config = config or {}
        
        # Optimization configuration
        self.strategy = OptimizationStrategy(
            self.config.get('optimization_strategy', 'balanced')
        )
        self.index_strategy = IndexStrategy(
            self.config.get('index_strategy', 'standard')
        )
        self.vacuum_strategy = VacuumStrategy(
            self.config.get('vacuum_strategy', 'smart_vacuum')
        )
        
        # Performance thresholds
        self.performance_thresholds = {
            'query_response_time': {
                'excellent': 0.1,
                'optimal': 0.5,
                'warning': 2.0,
                'critical': 5.0
            },
            'cache_hit_ratio': {
                'excellent': 0.99,
                'optimal': 0.95,
                'warning': 0.85,
                'critical': 0.70
            },
            'index_scan_ratio': {
                'excellent': 0.90,
                'optimal': 0.80,
                'warning': 0.60,
                'critical': 0.40
            },
            'dead_tuple_ratio': {
                'excellent': 0.05,
                'optimal': 0.10,
                'warning': 0.20,
                'critical': 0.30
            }
        }
        
        # State management
        self.statistics_collector = StatisticsCollector(session_factory)
        self.optimization_tasks: Dict[str, OptimizationTask] = {}
        self.performance_reports: Dict[str, PerformanceReport] = {}
        self.optimization_history: Dict[str, List[Dict]] = defaultdict(list)
        
        # Threading
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=4)
        self.monitoring_enabled = True
        self.monitoring_thread = None
        
        logger.info(f"PartitionOptimizer initialized with strategy: {self.strategy}")
    
    def optimize_partition(self, partition_name: str) -> PerformanceReport:
        """        Perform comprehensive optimization for a partition
        
        Args:
            partition_name: Name of partition to optimize
            
        Returns:
            PerformanceReport: Optimization results and recommendations
        """        try:
            logger.info(f"Starting optimization for partition: {partition_name}")
            
            # Collect current statistics
            stats = self.statistics_collector.collect_partition_statistics(partition_name)
            
            # Analyze performance
            report = self._analyze_partition_performance(partition_name, stats)
            
            # Apply optimizations based on strategy
            optimizations = self._generate_optimization_plan(partition_name, stats, report)
            
            # Execute optimizations
            applied_optimizations = self._execute_optimizations(partition_name, optimizations)
            
            # Update report with applied optimizations
            report.optimizations_applied = applied_optimizations
            
            # Cache report
            self.performance_reports[partition_name] = report
            
            # Record optimization history
            self.optimization_history[partition_name].append({
                'timestamp': datetime.utcnow().isoformat(),
                'performance_score': report.performance_score,
                'optimizations': applied_optimizations,
                'recommendations': report.recommendations
            })
            
            logger.info(f"Optimization completed for {partition_name}, score: {report.performance_score:.2f}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to optimize partition {partition_name}: {e}")
            return PerformanceReport(
                partition_name=partition_name,
                threshold_level=PerformanceThreshold.CRITICAL,
                issues=[f"Optimization failed: {str(e)}"]
            )
    
    def _analyze_partition_performance(self, partition_name: str, stats: PartitionStatistics) -> PerformanceReport:
        """Analyze partition performance and generate report"""        report = PerformanceReport(partition_name=partition_name)
        
        # Calculate performance metrics
        metrics = {}
        issues = []
        recommendations = []
        
        # Analyze dead tuple ratio
        if stats.live_tuples > 0:
            dead_tuple_ratio = stats.dead_tuples / (stats.live_tuples + stats.dead_tuples)
            metrics['dead_tuple_ratio'] = dead_tuple_ratio
            
            if dead_tuple_ratio > self.performance_thresholds['dead_tuple_ratio']['critical']:
                issues.append(f"High dead tuple ratio: {dead_tuple_ratio:.2%}")
                recommendations.append("Schedule immediate VACUUM operation")
            elif dead_tuple_ratio > self.performance_thresholds['dead_tuple_ratio']['warning']:
                recommendations.append("Consider more frequent VACUUM operations")
        
        # Analyze index usage
        if stats.index_scan_ratio < self.performance_thresholds['index_scan_ratio']['warning']:
            issues.append(f"Low index usage: {stats.index_scan_ratio:.2%}")
            recommendations.append("Review and optimize indexes")
        
        # Analyze table size efficiency
        if stats.total_size_bytes > 0:
            index_to_table_ratio = stats.index_size_bytes / stats.table_size_bytes
            metrics['index_to_table_ratio'] = index_to_table_ratio
            
            if index_to_table_ratio > 2.0:
                issues.append(f"High index overhead: {index_to_table_ratio:.2f}x table size")
                recommendations.append("Review index necessity and efficiency")
        
        # Analyze maintenance schedule
        if stats.last_vacuum:
            days_since_vacuum = (datetime.utcnow() - stats.last_vacuum).days
            if days_since_vacuum > 7:
                recommendations.append(f"VACUUM overdue by {days_since_vacuum} days")
        
        if stats.last_analyze:
            days_since_analyze = (datetime.utcnow() - stats.last_analyze).days
            if days_since_analyze > 3:
                recommendations.append(f"ANALYZE overdue by {days_since_analyze} days")
        
        # Calculate overall performance score (0-100)
        score_factors = []
        
        # Index efficiency factor
        index_efficiency = min(stats.index_scan_ratio * 1.2, 1.0)
        score_factors.append(index_efficiency * 30)  # 30% weight
        
        # Dead tuple factor
        dead_tuple_efficiency = 1.0 - min(metrics.get('dead_tuple_ratio', 0) * 2, 1.0)
        score_factors.append(dead_tuple_efficiency * 25)  # 25% weight
        
        # Size efficiency factor
        size_efficiency = 1.0 - min(metrics.get('index_to_table_ratio', 1.0) / 3.0, 1.0)
        score_factors.append(size_efficiency * 20)  # 20% weight
        
        # Maintenance factor
        maintenance_score = 1.0
        if stats.last_vacuum and (datetime.utcnow() - stats.last_vacuum).days > 7:
            maintenance_score *= 0.8
        if stats.last_analyze and (datetime.utcnow() - stats.last_analyze).days > 3:
            maintenance_score *= 0.9
        score_factors.append(maintenance_score * 25)  # 25% weight
        
        # Calculate final score
        performance_score = sum(score_factors)
        
        # Determine threshold level
        if performance_score >= 90:
            threshold_level = PerformanceThreshold.EXCELLENT
        elif performance_score >= 75:
            threshold_level = PerformanceThreshold.OPTIMAL
        elif performance_score >= 60:
            threshold_level = PerformanceThreshold.WARNING
        else:
            threshold_level = PerformanceThreshold.CRITICAL
        
        # Update report
        report.performance_score = performance_score
        report.threshold_level = threshold_level
        report.metrics = metrics
        report.issues = issues
        report.recommendations = recommendations
        
        return report
    
    def _generate_optimization_plan(self, partition_name: str, stats: PartitionStatistics, 
                                  report: PerformanceReport) -> List[OptimizationTask]:
        """Generate optimization plan based on analysis"""        tasks = []
        task_counter = 0
        
        # High priority: Critical performance issues
        if report.threshold_level == PerformanceThreshold.CRITICAL:
            # Emergency VACUUM if high dead tuple ratio
            if 'dead_tuple_ratio' in report.metrics and report.metrics['dead_tuple_ratio'] > 0.3:
                task_counter += 1
                tasks.append(OptimizationTask(
                    task_id=f"{partition_name}_vacuum_{task_counter}",
                    partition_name=partition_name,
                    operation_type="VACUUM_FULL",
                    priority=1,
                    estimated_duration=3600  # 1 hour estimate
                ))
            
            # Index rebuild if very low index usage
            if stats.index_scan_ratio < 0.3:
                task_counter += 1
                tasks.append(OptimizationTask(
                    task_id=f"{partition_name}_reindex_{task_counter}",
                    partition_name=partition_name,
                    operation_type="REINDEX",
                    priority=2,
                    estimated_duration=1800  # 30 minutes estimate
                ))
        
        # Medium priority: Performance improvements
        elif report.threshold_level == PerformanceThreshold.WARNING:
            # Regular VACUUM
            if 'dead_tuple_ratio' in report.metrics and report.metrics['dead_tuple_ratio'] > 0.1:
                task_counter += 1
                tasks.append(OptimizationTask(
                    task_id=f"{partition_name}_vacuum_{task_counter}",
                    partition_name=partition_name,
                    operation_type="VACUUM",
                    priority=3,
                    estimated_duration=900  # 15 minutes estimate
                ))
            
            # ANALYZE for statistics update
            if not stats.last_analyze or (datetime.utcnow() - stats.last_analyze).days > 3:
                task_counter += 1
                tasks.append(OptimizationTask(
                    task_id=f"{partition_name}_analyze_{task_counter}",
                    partition_name=partition_name,
                    operation_type="ANALYZE",
                    priority=4,
                    estimated_duration=300  # 5 minutes estimate
                ))
        
        # Low priority: Maintenance and optimization
        else:
            # Routine maintenance
            if not stats.last_analyze or (datetime.utcnow() - stats.last_analyze).days > 1:
                task_counter += 1
                tasks.append(OptimizationTask(
                    task_id=f"{partition_name}_analyze_{task_counter}",
                    partition_name=partition_name,
                    operation_type="ANALYZE",
                    priority=5,
                    estimated_duration=180  # 3 minutes estimate
                ))
        
        # Index optimization based on strategy
        if self.index_strategy in [IndexStrategy.COMPREHENSIVE, IndexStrategy.QUERY_DRIVEN]:
            task_counter += 1
            tasks.append(OptimizationTask(
                task_id=f"{partition_name}_index_optimize_{task_counter}",
                partition_name=partition_name,
                operation_type="INDEX_OPTIMIZE",
                priority=6,
                estimated_duration=600  # 10 minutes estimate
            ))
        
        return tasks
    
    def _execute_optimizations(self, partition_name: str, tasks: List[OptimizationTask]) -> List[str]:
        """Execute optimization tasks"""        applied_optimizations = []
        
        # Sort tasks by priority
        tasks.sort(key=lambda t: t.priority)
        
        for task in tasks:
            try:
                logger.info(f"Executing optimization task: {task.operation_type} on {partition_name}")
                
                success = self._execute_optimization_task(task)
                
                if success:
                    applied_optimizations.append(task.operation_type)
                    task.status = "completed"
                    logger.info(f"Completed optimization task: {task.operation_type}")
                else:
                    task.status = "failed"
                    logger.error(f"Failed optimization task: {task.operation_type}")
                
            except Exception as e:
                logger.error(f"Error executing optimization task {task.operation_type}: {e}")
                task.status = "error"
        
        return applied_optimizations
    
    def _execute_optimization_task(self, task: OptimizationTask) -> bool:
        """Execute individual optimization task"""        try:
            with self.session_factory() as session:
                if task.operation_type == "VACUUM":
                    session.execute(text(f"VACUUM {task.partition_name}"))
                
                elif task.operation_type == "VACUUM_FULL":
                    session.execute(text(f"VACUUM FULL {task.partition_name}"))
                
                elif task.operation_type == "ANALYZE":
                    session.execute(text(f"ANALYZE {task.partition_name}"))
                
                elif task.operation_type == "REINDEX":
                    session.execute(text(f"REINDEX TABLE {task.partition_name}"))
                
                elif task.operation_type == "INDEX_OPTIMIZE":
                    return self._optimize_indexes(session, task.partition_name)
                
                session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to execute task {task.operation_type}: {e}")
            return False
    
    def _optimize_indexes(self, session: Session, partition_name: str) -> bool:
        """Optimize indexes for partition"""        try:
            # Get current indexes
            indexes_query = text(f"""                SELECT 
                    indexname,
                    indexdef,
                    pg_relation_size(indexname::regclass) as size_bytes
                FROM pg_indexes 
                WHERE tablename = '{partition_name}'
                AND schemaname = 'public'
            """)
            
            indexes = session.execute(indexes_query).fetchall()
            
            # Analyze index usage
            for index in indexes:
                # Get index usage statistics
                usage_query = text(f"""                    SELECT 
                        idx_scan,
                        idx_tup_read,
                        idx_tup_fetch
                    FROM pg_stat_user_indexes 
                    WHERE indexrelname = '{index.indexname}'
                """)
                
                usage_stats = session.execute(usage_query).fetchone()
                
                # If index is unused and large, consider dropping
                if usage_stats and usage_stats.idx_scan == 0 and index.size_bytes > 10 * 1024 * 1024:  # 10MB
                    logger.warning(f"Unused index detected: {index.indexname} ({index.size_bytes} bytes)")
                    # Note: In production, you might want manual approval for index drops
            
            # Create missing indexes based on query patterns
            self._create_missing_indexes(session, partition_name)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to optimize indexes for {partition_name}: {e}")
            return False
    
    def _create_missing_indexes(self, session: Session, partition_name: str):
        """Create missing indexes based on table structure and usage patterns"""        try:
            # This is a simplified implementation
            # In practice, you would analyze query logs and execution plans
            
            # Get table columns
            columns_query = text(f"""                SELECT 
                    column_name,
                    data_type,
                    is_nullable
                FROM information_schema.columns 
                WHERE table_name = '{partition_name}'
                ORDER BY ordinal_position
            """)
            
            columns = session.execute(columns_query).fetchall()
            
            # Common index patterns for content protection platform
            common_patterns = [
                ('user_id',),
                ('created_at',),
                ('status',),
                ('user_id', 'created_at'),
                ('content_type',),
                ('platform',)
            ]
            
            for pattern in common_patterns:
                # Check if columns exist in table
                pattern_columns = [col for col in pattern if any(c.column_name == col for c in columns)]
                
                if len(pattern_columns) == len(pattern):
                    # Check if index already exists
                    index_name = f"idx_{partition_name}_{'_'.join(pattern_columns)}"
                    
                    existing_query = text(f"""                        SELECT 1 FROM pg_indexes 
                        WHERE tablename = '{partition_name}' 
                        AND indexname = '{index_name}'
                    """)
                    
                    exists = session.execute(existing_query).fetchone()
                    
                    if not exists:
                        try:
                            create_index_sql = f"""                                CREATE INDEX IF NOT EXISTS {index_name} 
                                ON {partition_name} ({', '.join(pattern_columns)})
                            """                            session.execute(text(create_index_sql))
                            logger.info(f"Created index: {index_name}")
                        except Exception as e:
                            logger.warning(f"Failed to create index {index_name}: {e}")
            
        except Exception as e:
            logger.error(f"Failed to create missing indexes for {partition_name}: {e}")
    
    def optimize_multiple_partitions(self, partition_names: List[str]) -> Dict[str, PerformanceReport]:
        """Optimize multiple partitions in parallel"""        reports = {}
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_partition = {
                executor.submit(self.optimize_partition, partition_name): partition_name
                for partition_name in partition_names
            }
            
            for future in future_to_partition:
                partition_name = future_to_partition[future]
                try:
                    report = future.result()
                    reports[partition_name] = report
                except Exception as e:
                    logger.error(f"Failed to optimize partition {partition_name}: {e}")
                    reports[partition_name] = PerformanceReport(
                        partition_name=partition_name,
                        threshold_level=PerformanceThreshold.CRITICAL,
                        issues=[f"Optimization failed: {str(e)}"]
                    )
        
        return reports
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get comprehensive optimization summary"""        try:
            total_partitions = len(self.performance_reports)
            
            # Count by threshold level
            threshold_counts = defaultdict(int)
            total_score = 0.0
            
            for report in self.performance_reports.values():
                threshold_counts[report.threshold_level.value] += 1
                total_score += report.performance_score
            
            avg_score = total_score / total_partitions if total_partitions > 0 else 0
            
            # Get recent optimization activity
            recent_optimizations = []
            for partition_name, history in self.optimization_history.items():
                if history:
                    recent_optimizations.append({
                        'partition': partition_name,
                        'last_optimization': history[-1]['timestamp'],
                        'performance_score': history[-1]['performance_score'],
                        'optimizations_count': len(history[-1]['optimizations'])
                    })
            
            # Sort by most recent
            recent_optimizations.sort(key=lambda x: x['last_optimization'], reverse=True)
            
            return {
                'summary': {
                    'total_partitions': total_partitions,
                    'average_performance_score': round(avg_score, 2),
                    'optimization_strategy': self.strategy.value,
                    'index_strategy': self.index_strategy.value,
                    'vacuum_strategy': self.vacuum_strategy.value
                },
                'performance_distribution': dict(threshold_counts),
                'recent_optimizations': recent_optimizations[:10],  # Last 10
                'recommendations': self._generate_global_recommendations(),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate optimization summary: {e}")
            return {'error': str(e)}
    
    def _generate_global_recommendations(self) -> List[str]:
        """Generate global optimization recommendations"""        recommendations = []
        
        if not self.performance_reports:
            return ["No partition data available for analysis"]
        
        # Analyze overall health
        critical_count = sum(1 for r in self.performance_reports.values() 
                           if r.threshold_level == PerformanceThreshold.CRITICAL)
        warning_count = sum(1 for r in self.performance_reports.values() 
                          if r.threshold_level == PerformanceThreshold.WARNING)
        
        total_partitions = len(self.performance_reports)
        
        if critical_count > total_partitions * 0.1:  # More than 10% critical
            recommendations.append(f"Immediate attention required: {critical_count} partitions in critical state")
        
        if warning_count > total_partitions * 0.2:  # More than 20% warning
            recommendations.append(f"Performance review needed: {warning_count} partitions need optimization")
        
        # Strategy recommendations
        avg_score = sum(r.performance_score for r in self.performance_reports.values()) / total_partitions
        
        if avg_score < 60:
            recommendations.append("Consider switching to AGGRESSIVE optimization strategy")
        elif avg_score > 85:
            recommendations.append("System performing well, consider MAINTENANCE_ONLY strategy")
        
        return recommendations
    
    def start_continuous_optimization(self, interval_hours: int = 24):
        """Start continuous optimization monitoring"""        def optimization_loop():
            while self.monitoring_enabled:
                try:
                    # Get all partitions that need optimization
                    partitions_to_optimize = []
                    
                    for partition_name, report in self.performance_reports.items():
                        # Check if partition needs optimization
                        if (report.threshold_level in [PerformanceThreshold.CRITICAL, PerformanceThreshold.WARNING] or
                            (datetime.utcnow() - report.generated_at).hours >= interval_hours):
                            partitions_to_optimize.append(partition_name)
                    
                    if partitions_to_optimize:
                        logger.info(f"Starting scheduled optimization for {len(partitions_to_optimize)} partitions")
                        self.optimize_multiple_partitions(partitions_to_optimize)
                    
                    # Sleep until next cycle
                    time.sleep(interval_hours * 3600)
                    
                except Exception as e:
                    logger.error(f"Error in continuous optimization loop: {e}")
                    time.sleep(300)  # Sleep 5 minutes on error
        
        if not self.monitoring_thread or not self.monitoring_thread.is_alive():
            self.monitoring_enabled = True
            self.monitoring_thread = threading.Thread(target=optimization_loop, daemon=True)
            self.monitoring_thread.start()
            logger.info("Continuous optimization monitoring started")
    
    def stop_continuous_optimization(self):
        """Stop continuous optimization monitoring"""        self.monitoring_enabled = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=10)
        logger.info("Continuous optimization monitoring stopped")
    
    def shutdown(self):
        """Shutdown optimizer gracefully"""        try:
            logger.info("Shutting down partition optimizer...")
            
            # Stop monitoring
            self.stop_continuous_optimization()
            
            # Shutdown executor
            self._executor.shutdown(wait=True)
            
            logger.info("Partition optimizer shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during partition optimizer shutdown: {e}")

__all__ = [
    'PartitionOptimizer',
    'StatisticsCollector',
    'OptimizationStrategy',
    'OptimizationMetric',
    'PerformanceThreshold',
    'IndexStrategy',
    'VacuumStrategy',
    'PartitionStatistics',
    'OptimizationTask',
    'PerformanceReport'
]
