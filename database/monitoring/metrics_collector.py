"""
Database Metrics Collector

Comprehensive database metrics collection system with real-time monitoring,
historical data storage, and advanced analytics capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

⚠️  AVERTISSEMENT STRICT ⚠️
Toute utilisation, modification ou distribution non autorisée de ce code est strictement interdite.
Propriété intellectuelle de Fahed Mlaiel (mlaiel@live.de).
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
from collections import defaultdict, deque
import json
import statistics
import psutil
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import asyncpg

from ..core.database import get_database_session
from ..models.monitoring import DatabaseMetric, MetricSnapshot
from ...core.config import Settings
from ...utils.cache import RedisCache
from ...utils.time_series import TimeSeriesStorage


class MetricType(Enum):
    """Database metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class MetricCategory(Enum):
    """Metric categories for organization"""
    PERFORMANCE = "performance"
    CONNECTIONS = "connections"
    QUERIES = "queries"
    STORAGE = "storage"
    REPLICATION = "replication"
    LOCKS = "locks"
    CACHE = "cache"
    TRANSACTIONS = "transactions"
    SYSTEM = "system"


@dataclass
class MetricDefinition:
    """Metric definition and metadata"""
    name: str
    category: MetricCategory
    metric_type: MetricType
    description: str
    unit: str
    sql_query: str
    collection_interval: int
    retention_days: int
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    aggregations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['category'] = self.category.value
        data['metric_type'] = self.metric_type.value
        return data


@dataclass
class MetricValue:
    """Single metric value with timestamp"""
    name: str
    value: Union[float, int]
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class MetricSummary:
    """Metric summary statistics"""
    name: str
    period_start: datetime
    period_end: datetime
    sample_count: int
    avg_value: float
    min_value: float
    max_value: float
    sum_value: float
    std_deviation: float
    percentiles: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['period_start'] = self.period_start.isoformat()
        data['period_end'] = self.period_end.isoformat()
        return data


class MetricsCollector:
    """
    Advanced database metrics collection system.
    
    Features:
    - Real-time metric collection
    - Custom metric definitions
    - Historical data storage
    - Aggregation and analytics
    - Alert threshold monitoring
    - Multi-dimensional labeling
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.cache = RedisCache()
        self.time_series = TimeSeriesStorage()
        
        # Collection state
        self.collecting_active = False
        self.metric_definitions: Dict[str, MetricDefinition] = {}
        self.collected_metrics: deque = deque(maxlen=10000)
        self.metric_cache: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Initialize standard metrics
        self._initialize_standard_metrics()
        
        self.logger.info("Metrics Collector initialized")
    
    def _initialize_standard_metrics(self) -> None:
        """Initialize standard database metrics"""
        
        # Performance metrics
        self.add_metric_definition(MetricDefinition(
            name="database_connections_active",
            category=MetricCategory.CONNECTIONS,
            metric_type=MetricType.GAUGE,
            description="Number of active database connections",
            unit="connections",
            sql_query="SELECT count(*) FROM pg_stat_activity WHERE state = 'active'",
            collection_interval=30,
            retention_days=30,
            alert_thresholds={"warning": 80, "critical": 95}
        ))
        
        self.add_metric_definition(MetricDefinition(
            name="database_connections_total",
            category=MetricCategory.CONNECTIONS,
            metric_type=MetricType.GAUGE,
            description="Total number of database connections",
            unit="connections",
            sql_query="SELECT count(*) FROM pg_stat_activity",
            collection_interval=30,
            retention_days=30
        ))
        
        self.add_metric_definition(MetricDefinition(
            name="database_queries_per_second",
            category=MetricCategory.PERFORMANCE,
            metric_type=MetricType.GAUGE,
            description="Queries executed per second",
            unit="queries/sec",
            sql_query="""
                SELECT sum(xact_commit + xact_rollback) 
                FROM pg_stat_database 
                WHERE datname NOT IN ('template0', 'template1', 'postgres')
            """,
            collection_interval=60,
            retention_days=30
        ))
        
        self.add_metric_definition(MetricDefinition(
            name="database_cache_hit_ratio",
            category=MetricCategory.CACHE,
            metric_type=MetricType.GAUGE,
            description="Database cache hit ratio",
            unit="ratio",
            sql_query="""
                SELECT CASE 
                    WHEN sum(heap_blks_hit + heap_blks_read) = 0 THEN 0
                    ELSE sum(heap_blks_hit)::float / sum(heap_blks_hit + heap_blks_read)
                END
                FROM pg_statio_user_tables
            """,
            collection_interval=60,
            retention_days=30,
            alert_thresholds={"warning": 0.8, "critical": 0.7}
        ))
        
        self.add_metric_definition(MetricDefinition(
            name="database_slow_queries",
            category=MetricCategory.QUERIES,
            metric_type=MetricType.GAUGE,
            description="Number of slow queries",
            unit="queries",
            sql_query="""
                SELECT count(*) 
                FROM pg_stat_statements 
                WHERE mean_exec_time > 1000
            """,
            collection_interval=60,
            retention_days=30,
            alert_thresholds={"warning": 10, "critical": 50}
        ))
        
        self.add_metric_definition(MetricDefinition(
            name="database_deadlocks",
            category=MetricCategory.LOCKS,
            metric_type=MetricType.COUNTER,
            description="Number of deadlocks",
            unit="deadlocks",
            sql_query="SELECT sum(deadlocks) FROM pg_stat_database",
            collection_interval=300,
            retention_days=30
        ))
        
        self.add_metric_definition(MetricDefinition(
            name="database_lock_waits",
            category=MetricCategory.LOCKS,
            metric_type=MetricType.GAUGE,
            description="Number of lock waits",
            unit="waits",
            sql_query="""
                SELECT count(*) 
                FROM pg_stat_activity 
                WHERE wait_event_type = 'Lock'
            """,
            collection_interval=30,
            retention_days=30
        ))
        
        self.add_metric_definition(MetricDefinition(
            name="database_size_bytes",
            category=MetricCategory.STORAGE,
            metric_type=MetricType.GAUGE,
            description="Total database size in bytes",
            unit="bytes",
            sql_query="""
                SELECT sum(pg_database_size(datname)) 
                FROM pg_database 
                WHERE datname NOT IN ('template0', 'template1')
            """,
            collection_interval=3600,
            retention_days=90
        ))
        
        self.add_metric_definition(MetricDefinition(
            name="database_transactions_per_second",
            category=MetricCategory.TRANSACTIONS,
            metric_type=MetricType.GAUGE,
            description="Transactions per second",
            unit="txn/sec",
            sql_query="""
                SELECT sum(xact_commit + xact_rollback) 
                FROM pg_stat_database
            """,
            collection_interval=60,
            retention_days=30
        ))
        
        # System metrics
        self.add_metric_definition(MetricDefinition(
            name="system_cpu_usage",
            category=MetricCategory.SYSTEM,
            metric_type=MetricType.GAUGE,
            description="System CPU usage percentage",
            unit="percent",
            sql_query="",  # Collected via psutil
            collection_interval=30,
            retention_days=30,
            alert_thresholds={"warning": 80, "critical": 90}
        ))
        
        self.add_metric_definition(MetricDefinition(
            name="system_memory_usage",
            category=MetricCategory.SYSTEM,
            metric_type=MetricType.GAUGE,
            description="System memory usage percentage",
            unit="percent",
            sql_query="",  # Collected via psutil
            collection_interval=30,
            retention_days=30,
            alert_thresholds={"warning": 85, "critical": 95}
        ))
    
    def add_metric_definition(self, metric_def: MetricDefinition) -> None:
        """Add a metric definition"""
        self.metric_definitions[metric_def.name] = metric_def
        self.logger.debug(f"Added metric definition: {metric_def.name}")
    
    async def start_collection(self) -> None:
        """Start metrics collection"""
        if self.collecting_active:
            self.logger.warning("Metrics collection already active")
            return
        
        self.collecting_active = True
        self.logger.info("Starting metrics collection")
        
        try:
            # Start collection tasks for each metric
            tasks = []
            for metric_name, metric_def in self.metric_definitions.items():
                if metric_def.collection_interval > 0:
                    task = asyncio.create_task(
                        self._collect_metric_loop(metric_name, metric_def)
                    )
                    tasks.append(task)
            
            # Start cleanup task
            cleanup_task = asyncio.create_task(self._cleanup_old_metrics())
            tasks.append(cleanup_task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            self.logger.error(f"Metrics collection error: {e}")
            self.collecting_active = False
            raise
    
    async def stop_collection(self) -> None:
        """Stop metrics collection"""
        self.collecting_active = False
        self.logger.info("Metrics collection stopped")
    
    async def _collect_metric_loop(self, metric_name: str, metric_def: MetricDefinition) -> None:
        """Collection loop for a single metric"""
        while self.collecting_active:
            try:
                value = await self._collect_single_metric(metric_name, metric_def)
                if value is not None:
                    await self._store_metric_value(metric_name, value)
                
                await asyncio.sleep(metric_def.collection_interval)
                
            except Exception as e:
                self.logger.error(f"Error collecting metric {metric_name}: {e}")
                await asyncio.sleep(metric_def.collection_interval)
    
    async def _collect_single_metric(
        self, 
        metric_name: str, 
        metric_def: MetricDefinition
    ) -> Optional[MetricValue]:
        """Collect a single metric value"""
        try:
            timestamp = datetime.utcnow()
            
            # System metrics (non-SQL)
            if metric_name == "system_cpu_usage":
                value = psutil.cpu_percent(interval=1)
            elif metric_name == "system_memory_usage":
                value = psutil.virtual_memory().percent
            else:
                # Database metrics (SQL-based)
                if not metric_def.sql_query.strip():
                    return None
                
                async with get_database_session() as session:
                    result = await session.execute(text(metric_def.sql_query))
                    raw_value = result.scalar()
                    
                    if raw_value is None:
                        return None
                    
                    value = float(raw_value)
            
            # Handle counter metrics (calculate rate)
            if metric_def.metric_type == MetricType.COUNTER:
                value = await self._calculate_counter_rate(metric_name, value, timestamp)
                if value is None:
                    return None
            
            metric_value = MetricValue(
                name=metric_name,
                value=value,
                timestamp=timestamp,
                labels={"category": metric_def.category.value},
                metadata={"unit": metric_def.unit}
            )
            
            return metric_value
            
        except Exception as e:
            self.logger.error(f"Error collecting metric {metric_name}: {e}")
            return None
    
    async def _calculate_counter_rate(
        self, 
        metric_name: str, 
        current_value: float, 
        timestamp: datetime
    ) -> Optional[float]:
        """Calculate rate for counter metrics"""
        cache_key = f"counter:{metric_name}"
        
        try:
            # Get previous value
            previous_data = await self.cache.get(cache_key)
            
            if previous_data:
                prev_value, prev_timestamp_str = json.loads(previous_data)
                prev_timestamp = datetime.fromisoformat(prev_timestamp_str)
                
                # Calculate rate
                time_diff = (timestamp - prev_timestamp).total_seconds()
                if time_diff > 0:
                    rate = (current_value - prev_value) / time_diff
                else:
                    rate = 0.0
                
                # Store current value for next calculation
                await self.cache.set(
                    cache_key,
                    json.dumps([current_value, timestamp.isoformat()]),
                    expire=3600
                )
                
                return max(0.0, rate)  # Ensure non-negative rate
            else:
                # First measurement, store and return None
                await self.cache.set(
                    cache_key,
                    json.dumps([current_value, timestamp.isoformat()]),
                    expire=3600
                )
                return None
                
        except Exception as e:
            self.logger.error(f"Error calculating counter rate for {metric_name}: {e}")
            return None
    
    async def _store_metric_value(self, metric_name: str, metric_value: MetricValue) -> None:
        """Store metric value"""
        try:
            # Add to in-memory cache
            self.collected_metrics.append(metric_value)
            self.metric_cache[metric_name].append(metric_value)
            
            # Store in time series database
            await self.time_series.store_metric(
                metric_name,
                metric_value.value,
                metric_value.timestamp,
                metric_value.labels
            )
            
            # Cache latest value
            await self.cache.set(
                f"metric:latest:{metric_name}",
                json.dumps(metric_value.to_dict()),
                expire=3600
            )
            
            # Check alert thresholds
            await self._check_metric_alerts(metric_name, metric_value)
            
        except Exception as e:
            self.logger.error(f"Error storing metric value {metric_name}: {e}")
    
    async def _check_metric_alerts(self, metric_name: str, metric_value: MetricValue) -> None:
        """Check metric against alert thresholds"""
        try:
            metric_def = self.metric_definitions.get(metric_name)
            if not metric_def or not metric_def.alert_thresholds:
                return
            
            value = metric_value.value
            
            # Check thresholds
            for threshold_level, threshold_value in metric_def.alert_thresholds.items():
                if value >= threshold_value:
                    alert = {
                        "metric_name": metric_name,
                        "alert_level": threshold_level,
                        "current_value": value,
                        "threshold_value": threshold_value,
                        "timestamp": metric_value.timestamp.isoformat(),
                        "message": f"Metric {metric_name} {threshold_level}: {value} >= {threshold_value}"
                    }
                    
                    # Store alert
                    await self.cache.lpush(
                        "metrics:alerts",
                        json.dumps(alert)
                    )
                    
                    self.logger.warning(f"Metric alert: {alert['message']}")
                    break
            
        except Exception as e:
            self.logger.error(f"Error checking metric alerts for {metric_name}: {e}")
    
    async def _cleanup_old_metrics(self) -> None:
        """Cleanup old metric data"""
        while self.collecting_active:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                for metric_name, metric_def in self.metric_definitions.items():
                    cutoff_date = datetime.utcnow() - timedelta(days=metric_def.retention_days)
                    
                    # Cleanup time series data
                    await self.time_series.cleanup_old_data(metric_name, cutoff_date)
                
                self.logger.debug("Completed metrics cleanup")
                
            except Exception as e:
                self.logger.error(f"Error during metrics cleanup: {e}")
    
    async def get_metric_value(self, metric_name: str, latest: bool = True) -> Optional[Dict[str, Any]]:
        """Get metric value"""
        try:
            if latest:
                # Get latest cached value
                cached_data = await self.cache.get(f"metric:latest:{metric_name}")
                if cached_data:
                    return json.loads(cached_data)
            
            # Get from in-memory cache
            if metric_name in self.metric_cache and self.metric_cache[metric_name]:
                latest_value = self.metric_cache[metric_name][-1]
                return latest_value.to_dict()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting metric value {metric_name}: {e}")
            return None
    
    async def get_metric_history(
        self, 
        metric_name: str, 
        start_time: datetime, 
        end_time: datetime,
        aggregation: str = None
    ) -> List[Dict[str, Any]]:
        """Get metric history"""
        try:
            # Get from time series database
            values = await self.time_series.get_metric_range(
                metric_name, start_time, end_time, aggregation
            )
            
            return [{"timestamp": ts.isoformat(), "value": val} for ts, val in values]
            
        except Exception as e:
            self.logger.error(f"Error getting metric history {metric_name}: {e}")
            return []
    
    async def get_metric_summary(
        self, 
        metric_name: str, 
        start_time: datetime, 
        end_time: datetime
    ) -> Optional[MetricSummary]:
        """Get metric summary statistics"""
        try:
            # Get values from time series
            values = await self.time_series.get_metric_range(metric_name, start_time, end_time)
            
            if not values:
                return None
            
            numeric_values = [val for _, val in values]
            
            # Calculate statistics
            summary = MetricSummary(
                name=metric_name,
                period_start=start_time,
                period_end=end_time,
                sample_count=len(numeric_values),
                avg_value=statistics.mean(numeric_values),
                min_value=min(numeric_values),
                max_value=max(numeric_values),
                sum_value=sum(numeric_values),
                std_deviation=statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0.0
            )
            
            # Calculate percentiles
            if len(numeric_values) > 1:
                sorted_values = sorted(numeric_values)
                summary.percentiles = {
                    "p50": self._calculate_percentile(sorted_values, 50),
                    "p90": self._calculate_percentile(sorted_values, 90),
                    "p95": self._calculate_percentile(sorted_values, 95),
                    "p99": self._calculate_percentile(sorted_values, 99)
                }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting metric summary {metric_name}: {e}")
            return None
    
    def _calculate_percentile(self, sorted_values: List[float], percentile: int) -> float:
        """Calculate percentile value"""
        if not sorted_values:
            return 0.0
        
        index = (percentile / 100.0) * (len(sorted_values) - 1)
        lower_index = int(index)
        upper_index = min(lower_index + 1, len(sorted_values) - 1)
        
        if lower_index == upper_index:
            return sorted_values[lower_index]
        
        # Linear interpolation
        weight = index - lower_index
        return sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight
    
    async def get_all_metrics(self, category: MetricCategory = None) -> Dict[str, Any]:
        """Get all current metric values"""
        try:
            metrics = {}
            
            for metric_name, metric_def in self.metric_definitions.items():
                if category is None or metric_def.category == category:
                    value = await self.get_metric_value(metric_name)
                    if value:
                        metrics[metric_name] = value
            
            return {
                "metrics": metrics,
                "collection_active": self.collecting_active,
                "last_update": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting all metrics: {e}")
            return {"error": str(e)}
    
    async def get_metric_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Get all metric definitions"""
        return {
            name: definition.to_dict()
            for name, definition in self.metric_definitions.items()
        }
    
    async def get_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent metric alerts"""
        try:
            alerts_data = await self.cache.lrange("metrics:alerts", 0, limit - 1)
            return [json.loads(alert) for alert in alerts_data]
        except Exception as e:
            self.logger.error(f"Error getting metric alerts: {e}")
            return []
    
    async def collect_metric_now(self, metric_name: str) -> Optional[Dict[str, Any]]:
        """Collect a specific metric immediately"""
        try:
            metric_def = self.metric_definitions.get(metric_name)
            if not metric_def:
                return {"error": f"Metric {metric_name} not found"}
            
            metric_value = await self._collect_single_metric(metric_name, metric_def)
            
            if metric_value:
                await self._store_metric_value(metric_name, metric_value)
                return metric_value.to_dict()
            else:
                return {"error": f"Failed to collect metric {metric_name}"}
                
        except Exception as e:
            self.logger.error(f"Error collecting metric {metric_name} now: {e}")
            return {"error": str(e)}
    
    async def export_metrics(
        self, 
        start_time: datetime, 
        end_time: datetime,
        format_type: str = "json"
    ) -> Dict[str, Any]:
        """Export metrics data"""
        try:
            exported_data = {
                "export_info": {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "format": format_type,
                    "exported_at": datetime.utcnow().isoformat()
                },
                "metric_definitions": await self.get_metric_definitions(),
                "metrics_data": {}
            }
            
            # Export each metric's data
            for metric_name in self.metric_definitions.keys():
                history = await self.get_metric_history(metric_name, start_time, end_time)
                summary = await self.get_metric_summary(metric_name, start_time, end_time)
                
                exported_data["metrics_data"][metric_name] = {
                    "history": history,
                    "summary": summary.to_dict() if summary else None
                }
            
            return exported_data
            
        except Exception as e:
            self.logger.error(f"Error exporting metrics: {e}")
            return {"error": str(e)}
