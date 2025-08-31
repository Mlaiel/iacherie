"""Database Performance Monitoring Dashboard

Comprehensive performance monitoring system with real-time metrics,
alerting, and intelligent performance insights.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from enum import Enum
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
import statistics
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from .advanced_index_strategies import AdvancedIndexStrategiesManager
from .advanced_query_optimizer import AdvancedQueryOptimizer
from .connection_pool_optimizer import EnhancedConnectionPoolManager
from .intelligent_partitioning import IntelligentPartitionManager
from .read_replica_manager import ReadReplicaManager
from .database_sharding import DatabaseShardCoordinator
from ...core.logging import get_logger

logger = get_logger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class MetricType(Enum):
    """Metric types"""    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class PerformanceMetric:
    """Performance metric data point"""    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)
    description: str = ""


@dataclass
class PerformanceAlert:
    """Performance alert"""    alert_id: str
    name: str
    severity: AlertSeverity
    message: str
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    metric_name: str = ""
    threshold_value: float = 0.0
    current_value: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DatabaseStats:
    """Database statistics summary"""    total_connections: int = 0
    active_connections: int = 0
    total_queries: int = 0
    slow_queries: int = 0
    avg_query_time: float = 0.0
    cache_hit_ratio: float = 0.0
    index_usage_ratio: float = 0.0
    replication_lag: float = 0.0
    disk_usage_gb: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class MetricsCollector:
    """Collects and stores performance metrics"""    
    def __init__(self, retention_hours: int = 168):  # 7 days
        self.retention_hours = retention_hours
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10080))  # 7 days of minute data
        self.alerts: Dict[str, PerformanceAlert] = {}
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        
    def add_metric(self, metric: PerformanceMetric):
        """Add a metric data point"""        self.metrics[metric.name].append({
            'value': metric.value,
            'timestamp': metric.timestamp,
            'labels': metric.labels
        })
        
        # Check alert rules
        self._check_alert_rules(metric)
    
    def get_metric_values(self, metric_name: str, 
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get metric values within time range"""        if metric_name not in self.metrics:
            return []
        
        values = list(self.metrics[metric_name])
        
        if start_time or end_time:
            filtered_values = []
            for value in values:
                timestamp = value['timestamp']
                if start_time and timestamp < start_time:
                    continue
                if end_time and timestamp > end_time:
                    continue
                filtered_values.append(value)
            values = filtered_values
        
        return values
    
    def get_metric_statistics(self, metric_name: str, 
                            hours_back: int = 1) -> Dict[str, float]:
        """Get statistical summary of metric"""        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours_back)
        
        values = self.get_metric_values(metric_name, start_time, end_time)
        if not values:
            return {}
        
        numeric_values = [v['value'] for v in values]
        
        return {
            'count': len(numeric_values),
            'mean': statistics.mean(numeric_values),
            'median': statistics.median(numeric_values),
            'min': min(numeric_values),
            'max': max(numeric_values),
            'std': statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0.0
        }
    
    def add_alert_rule(self, metric_name: str, threshold: float, 
                      severity: AlertSeverity, condition: str = "greater_than"):
        """Add alert rule for metric"""        self.alert_rules[metric_name] = {
            'threshold': threshold,
            'severity': severity,
            'condition': condition,
            'consecutive_breaches': 0,
            'breach_threshold': 3  # Trigger after 3 consecutive breaches
        }
    
    def _check_alert_rules(self, metric: PerformanceMetric):
        """Check if metric triggers any alerts"""        rule = self.alert_rules.get(metric.name)
        if not rule:
            return
        
        triggered = False
        if rule['condition'] == 'greater_than' and metric.value > rule['threshold']:
            triggered = True
        elif rule['condition'] == 'less_than' and metric.value < rule['threshold']:
            triggered = True
        
        if triggered:
            rule['consecutive_breaches'] += 1
            
            if rule['consecutive_breaches'] >= rule['breach_threshold']:
                self._trigger_alert(metric, rule)
        else:
            rule['consecutive_breaches'] = 0
            self._resolve_alert(metric.name)
    
    def _trigger_alert(self, metric: PerformanceMetric, rule: Dict[str, Any]):
        """Trigger a new alert"""        alert_id = f"{metric.name}_{int(time.time())}"
        
        alert = PerformanceAlert(
            alert_id=alert_id,
            name=f"{metric.name.upper()} threshold exceeded",
            severity=rule['severity'],
            message=f"{metric.name} value {metric.value} exceeds threshold {rule['threshold']}",
            triggered_at=datetime.now(),
            metric_name=metric.name,
            threshold_value=rule['threshold'],
            current_value=metric.value
        )
        
        self.alerts[alert_id] = alert
        logger.warning(f"Alert triggered: {alert.message}")
    
    def _resolve_alert(self, metric_name: str):
        """Resolve alerts for metric"""        for alert_id, alert in list(self.alerts.items()):
            if alert.metric_name == metric_name and not alert.resolved_at:
                alert.resolved_at = datetime.now()
                logger.info(f"Alert resolved: {alert.name}")
    
    def get_active_alerts(self) -> List[PerformanceAlert]:
        """Get currently active alerts"""        return [alert for alert in self.alerts.values() if not alert.resolved_at]
    
    def cleanup_old_data(self):
        """Clean up old metrics data"""        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
        
        for metric_name in list(self.metrics.keys()):
            metric_data = self.metrics[metric_name]
            
            # Remove old data points
            while metric_data and metric_data[0]['timestamp'] < cutoff_time:
                metric_data.popleft()


class DatabasePerformanceMonitor:
    """Database performance monitoring system"""    
    def __init__(self, engines: Dict[str, AsyncEngine]):
        self.engines = engines
        self.metrics_collector = MetricsCollector()
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_monitoring = False
        
        # Component references (will be set externally)
        self.index_manager: Optional[AdvancedIndexStrategiesManager] = None
        self.query_optimizer: Optional[AdvancedQueryOptimizer] = None
        self.pool_manager: Optional[EnhancedConnectionPoolManager] = None
        self.partition_manager: Optional[IntelligentPartitionManager] = None
        self.replica_manager: Optional[ReadReplicaManager] = None
        self.shard_coordinator: Optional[DatabaseShardCoordinator] = None
        
        # Setup default alert rules
        self._setup_default_alerts()
    
    def _setup_default_alerts(self):
        """Setup default alert rules"""        # Database connection alerts
        self.metrics_collector.add_alert_rule(
            "active_connections", 80, AlertSeverity.WARNING, "greater_than"
        )
        self.metrics_collector.add_alert_rule(
            "active_connections", 95, AlertSeverity.CRITICAL, "greater_than"
        )
        
        # Query performance alerts
        self.metrics_collector.add_alert_rule(
            "avg_query_time", 2.0, AlertSeverity.WARNING, "greater_than"
        )
        self.metrics_collector.add_alert_rule(
            "avg_query_time", 5.0, AlertSeverity.CRITICAL, "greater_than"
        )
        
        # Resource utilization alerts
        self.metrics_collector.add_alert_rule(
            "cpu_usage", 0.8, AlertSeverity.WARNING, "greater_than"
        )
        self.metrics_collector.add_alert_rule(
            "memory_usage", 0.9, AlertSeverity.CRITICAL, "greater_than"
        )
        
        # Replication lag alerts
        self.metrics_collector.add_alert_rule(
            "replication_lag", 30.0, AlertSeverity.WARNING, "greater_than"
        )
        self.metrics_collector.add_alert_rule(
            "replication_lag", 60.0, AlertSeverity.CRITICAL, "greater_than"
        )
    
    async def start_monitoring(self, interval_seconds: int = 60):
        """Start performance monitoring"""        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(
            self._monitoring_loop(interval_seconds)
        )
        logger.info("Database performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop performance monitoring"""        self.is_monitoring = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Database performance monitoring stopped")
    
    async def _monitoring_loop(self, interval_seconds: int):
        """Main monitoring loop"""        while self.is_monitoring:
            try:
                # Collect metrics from all sources
                await self._collect_database_metrics()
                await self._collect_component_metrics()
                
                # Cleanup old data
                self.metrics_collector.cleanup_old_data()
                
                await asyncio.sleep(interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(30)
    
    async def _collect_database_metrics(self):
        """Collect core database metrics"""        for engine_name, engine in self.engines.items():
            try:
                await self._collect_engine_metrics(engine_name, engine)
            except Exception as e:
                logger.warning(f"Failed to collect metrics for {engine_name}: {e}")
    
    async def _collect_engine_metrics(self, engine_name: str, engine: AsyncEngine):
        """Collect metrics for a specific database engine"""        try:
            async with engine.begin() as conn:
                # Connection metrics
                conn_result = await conn.execute(text("""                    SELECT 
                        count(*) as total_connections,
                        count(*) FILTER (WHERE state = 'active') as active_connections
                    FROM pg_stat_activity
                """))
                conn_row = conn_result.fetchone()
                
                if conn_row:
                    self.metrics_collector.add_metric(PerformanceMetric(
                        name="total_connections",
                        value=conn_row.total_connections or 0,
                        metric_type=MetricType.GAUGE,
                        labels={"engine": engine_name}
                    ))
                    
                    self.metrics_collector.add_metric(PerformanceMetric(
                        name="active_connections",
                        value=conn_row.active_connections or 0,
                        metric_type=MetricType.GAUGE,
                        labels={"engine": engine_name}
                    ))
                
                # Query metrics
                query_result = await conn.execute(text("""                    SELECT 
                        sum(calls) as total_queries,
                        avg(mean_exec_time) as avg_query_time,
                        count(*) FILTER (WHERE mean_exec_time > 1000) as slow_queries
                    FROM pg_stat_statements
                    WHERE queryid IS NOT NULL
                """))
                query_row = query_result.fetchone()
                
                if query_row:
                    self.metrics_collector.add_metric(PerformanceMetric(
                        name="total_queries",
                        value=query_row.total_queries or 0,
                        metric_type=MetricType.COUNTER,
                        labels={"engine": engine_name}
                    ))
                    
                    self.metrics_collector.add_metric(PerformanceMetric(
                        name="avg_query_time",
                        value=(query_row.avg_query_time or 0) / 1000,  # Convert to seconds
                        metric_type=MetricType.GAUGE,
                        labels={"engine": engine_name}
                    ))
                    
                    self.metrics_collector.add_metric(PerformanceMetric(
                        name="slow_queries",
                        value=query_row.slow_queries or 0,
                        metric_type=MetricType.GAUGE,
                        labels={"engine": engine_name}
                    ))
                
                # Cache metrics
                cache_result = await conn.execute(text("""                    SELECT 
                        sum(heap_blks_hit) / NULLIF(sum(heap_blks_hit + heap_blks_read), 0) as cache_hit_ratio
                    FROM pg_statio_user_tables
                """))
                cache_row = cache_result.fetchone()
                
                if cache_row and cache_row.cache_hit_ratio:
                    self.metrics_collector.add_metric(PerformanceMetric(
                        name="cache_hit_ratio",
                        value=float(cache_row.cache_hit_ratio),
                        metric_type=MetricType.GAUGE,
                        labels={"engine": engine_name}
                    ))
                
                # Database size
                size_result = await conn.execute(text("""                    SELECT sum(pg_database_size(datname)) / (1024*1024*1024) as size_gb
                    FROM pg_database
                    WHERE datname NOT IN ('template0', 'template1', 'postgres')
                """))
                size_row = size_result.fetchone()
                
                if size_row:
                    self.metrics_collector.add_metric(PerformanceMetric(
                        name="database_size_gb",
                        value=size_row.size_gb or 0,
                        metric_type=MetricType.GAUGE,
                        labels={"engine": engine_name}
                    ))
                
        except Exception as e:
            logger.warning(f"Failed to collect engine metrics for {engine_name}: {e}")
    
    async def _collect_component_metrics(self):
        """Collect metrics from optimization components"""        try:
            # Index manager metrics
            if self.index_manager:
                stats = self.index_manager.get_strategy_stats()
                
                self.metrics_collector.add_metric(PerformanceMetric(
                    name="index_optimizations_total",
                    value=stats.get('total_executions', 0),
                    metric_type=MetricType.COUNTER
                ))
                
                self.metrics_collector.add_metric(PerformanceMetric(
                    name="avg_recommendations_per_execution",
                    value=stats.get('average_recommendations_per_execution', 0),
                    metric_type=MetricType.GAUGE
                ))
            
            # Query optimizer metrics
            if self.query_optimizer:
                stats = self.query_optimizer.get_optimization_stats()
                
                self.metrics_collector.add_metric(PerformanceMetric(
                    name="query_optimizations_total",
                    value=stats.get('total_optimizations', 0),
                    metric_type=MetricType.COUNTER
                ))
                
                self.metrics_collector.add_metric(PerformanceMetric(
                    name="avg_query_improvement",
                    value=stats.get('average_improvement', 0),
                    metric_type=MetricType.GAUGE
                ))
            
            # Connection pool metrics
            if self.pool_manager:
                stats = await self.pool_manager.get_optimization_stats()
                
                for pool_id, metrics in stats.get('connection_metrics', {}).items():
                    self.metrics_collector.add_metric(PerformanceMetric(
                        name="pool_active_connections",
                        value=metrics.get('active_connections', 0),
                        metric_type=MetricType.GAUGE,
                        labels={"pool": pool_id}
                    ))
                    
                    self.metrics_collector.add_metric(PerformanceMetric(
                        name="pool_avg_response_time",
                        value=metrics.get('avg_response_time', 0),
                        metric_type=MetricType.GAUGE,
                        labels={"pool": pool_id}
                    ))
            
            # Partition manager metrics
            if self.partition_manager:
                stats = await self.partition_manager.get_partition_stats()
                
                self.metrics_collector.add_metric(PerformanceMetric(
                    name="total_partitioned_tables",
                    value=stats.get('total_tables', 0),
                    metric_type=MetricType.GAUGE
                ))
                
                for table_name, table_stats in stats.get('tables', {}).items():
                    self.metrics_collector.add_metric(PerformanceMetric(
                        name="table_partition_count",
                        value=table_stats.get('partition_count', 0),
                        metric_type=MetricType.GAUGE,
                        labels={"table": table_name}
                    ))
            
            # Replica manager metrics
            if self.replica_manager:
                stats = await self.replica_manager.get_replica_stats()
                
                self.metrics_collector.add_metric(PerformanceMetric(
                    name="active_replicas",
                    value=stats.get('active_replicas', 0),
                    metric_type=MetricType.GAUGE
                ))
                
                for replica_id, replica_stats in stats.get('replicas', {}).items():
                    lag = replica_stats.get('lag_seconds', 0)
                    if lag:
                        self.metrics_collector.add_metric(PerformanceMetric(
                            name="replication_lag",
                            value=lag,
                            metric_type=MetricType.GAUGE,
                            labels={"replica": replica_id}
                        ))
            
            # Shard coordinator metrics
            if self.shard_coordinator:
                stats = await self.shard_coordinator.get_shard_statistics()
                
                self.metrics_collector.add_metric(PerformanceMetric(
                    name="active_shards",
                    value=stats.get('active_shards', 0),
                    metric_type=MetricType.GAUGE
                ))
                
                self.metrics_collector.add_metric(PerformanceMetric(
                    name="total_sharded_rows",
                    value=stats.get('total_rows', 0),
                    metric_type=MetricType.GAUGE
                ))
                
        except Exception as e:
            logger.warning(f"Failed to collect component metrics: {e}")
    
    def get_dashboard_data(self, hours_back: int = 1) -> Dict[str, Any]:
        """Get dashboard data for the specified time period"""        try:
            dashboard_data = {
                'timestamp': datetime.now().isoformat(),
                'time_range_hours': hours_back,
                'metrics': {},
                'alerts': [],
                'summary': {}
            }
            
            # Key metrics with statistics
            key_metrics = [
                'total_connections', 'active_connections', 'avg_query_time',
                'cache_hit_ratio', 'database_size_gb', 'replication_lag',
                'index_optimizations_total', 'query_optimizations_total'
            ]
            
            for metric_name in key_metrics:
                stats = self.metrics_collector.get_metric_statistics(metric_name, hours_back)
                if stats:
                    dashboard_data['metrics'][metric_name] = stats
            
            # Active alerts
            active_alerts = self.metrics_collector.get_active_alerts()
            dashboard_data['alerts'] = [asdict(alert) for alert in active_alerts]
            
            # Summary statistics
            dashboard_data['summary'] = {
                'total_metrics_collected': len(self.metrics_collector.metrics),
                'active_alerts_count': len(active_alerts),
                'critical_alerts_count': len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]),
                'monitoring_uptime_hours': hours_back if self.is_monitoring else 0
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return {'error': str(e)}
    
    def get_metric_trend(self, metric_name: str, hours_back: int = 24) -> Dict[str, Any]:
        """Get trend data for a specific metric"""        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours_back)
            
            values = self.metrics_collector.get_metric_values(metric_name, start_time, end_time)
            
            if not values:
                return {'error': f'No data found for metric {metric_name}'}
            
            # Calculate trend
            numeric_values = [v['value'] for v in values]
            timestamps = [v['timestamp'] for v in values]
            
            # Simple linear trend calculation
            if len(numeric_values) > 1:
                x_values = [(t - timestamps[0]).total_seconds() for t in timestamps]
                correlation = np.corrcoef(x_values, numeric_values)[0, 1] if len(x_values) > 1 else 0
                
                if correlation > 0.1:
                    trend = 'increasing'
                elif correlation < -0.1:
                    trend = 'decreasing'
                else:
                    trend = 'stable'
            else:
                trend = 'stable'
            
            return {
                'metric_name': metric_name,
                'trend': trend,
                'data_points': len(values),
                'latest_value': numeric_values[-1] if numeric_values else 0,
                'min_value': min(numeric_values) if numeric_values else 0,
                'max_value': max(numeric_values) if numeric_values else 0,
                'avg_value': statistics.mean(numeric_values) if numeric_values else 0,
                'correlation': correlation if 'correlation' in locals() else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get metric trend: {e}")
            return {'error': str(e)}
    
    async def generate_performance_report(self, hours_back: int = 24) -> Dict[str, Any]:
        """Generate comprehensive performance report"""        try:
            report = {
                'report_generated_at': datetime.now().isoformat(),
                'time_period_hours': hours_back,
                'executive_summary': {},
                'detailed_metrics': {},
                'recommendations': [],
                'alerts_summary': {},
                'component_health': {}
            }
            
            # Executive summary
            dashboard_data = self.get_dashboard_data(hours_back)
            active_alerts = self.metrics_collector.get_active_alerts()
            
            report['executive_summary'] = {
                'overall_health': 'healthy' if len(active_alerts) == 0 else 'degraded' if any(a.severity == AlertSeverity.CRITICAL for a in active_alerts) else 'warning',
                'total_alerts': len(active_alerts),
                'critical_alerts': len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]),
                'total_metrics_tracked': len(self.metrics_collector.metrics),
                'monitoring_status': 'active' if self.is_monitoring else 'stopped'
            }
            
            # Detailed metrics analysis
            for metric_name in ['avg_query_time', 'active_connections', 'cache_hit_ratio', 'replication_lag']:
                trend_data = self.get_metric_trend(metric_name, hours_back)
                if 'error' not in trend_data:
                    report['detailed_metrics'][metric_name] = trend_data
            
            # Performance recommendations
            recommendations = []
            
            # Check for high query times
            query_time_trend = self.get_metric_trend('avg_query_time', hours_back)
            if 'error' not in query_time_trend and query_time_trend.get('avg_value', 0) > 1.0:
                recommendations.append({
                    'category': 'query_performance',
                    'priority': 'high',
                    'recommendation': 'Consider query optimization - average query time is above 1 second',
                    'details': f"Average query time: {query_time_trend.get('avg_value', 0):.2f}s"
                })
            
            # Check for low cache hit ratio
            cache_trend = self.get_metric_trend('cache_hit_ratio', hours_back)
            if 'error' not in cache_trend and cache_trend.get('avg_value', 1) < 0.9:
                recommendations.append({
                    'category': 'caching',
                    'priority': 'medium',
                    'recommendation': 'Consider increasing shared_buffers or optimizing queries for better cache usage',
                    'details': f"Cache hit ratio: {cache_trend.get('avg_value', 0):.2%}"
                })
            
            # Check for high connection usage
            conn_trend = self.get_metric_trend('active_connections', hours_back)
            if 'error' not in conn_trend and conn_trend.get('max_value', 0) > 80:
                recommendations.append({
                    'category': 'connections',
                    'priority': 'medium',
                    'recommendation': 'Consider connection pooling optimization or increasing max_connections',
                    'details': f"Peak connections: {conn_trend.get('max_value', 0)}"
                })
            
            report['recommendations'] = recommendations
            
            # Alerts summary
            alert_summary = defaultdict(int)
            for alert in active_alerts:
                alert_summary[alert.severity.value] += 1
            
            report['alerts_summary'] = dict(alert_summary)
            
            # Component health check
            component_health = {}
            
            if self.index_manager:
                component_health['index_manager'] = 'healthy'
            
            if self.query_optimizer:
                component_health['query_optimizer'] = 'healthy'
            
            if self.pool_manager:
                component_health['pool_manager'] = 'healthy'
            
            if self.partition_manager:
                component_health['partition_manager'] = 'healthy'
            
            if self.replica_manager:
                component_health['replica_manager'] = 'healthy'
            
            if self.shard_coordinator:
                component_health['shard_coordinator'] = 'healthy'
            
            report['component_health'] = component_health
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            return {'error': str(e)}


# Export main classes
__all__ = [
    'DatabasePerformanceMonitor',
    'MetricsCollector', 
    'PerformanceMetric',
    'PerformanceAlert',
    'AlertSeverity',
    'MetricType'
]