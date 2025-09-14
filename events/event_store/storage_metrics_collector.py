"""🚀 Storage Metrics Collector - IA Influencer Agent Platform
==============================================================
Module: events/event_store/storage_metrics_collector.py
Author: Fahed Mlaiel (mlaiel@live.de)
==============================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 STORAGE METRICS COLLECTOR
Comprehensive metrics collection and analysis for Ainflue event store
with real-time monitoring, alerting, and performance optimization insights.

Key Features:
- Real-time storage performance metrics
- Multi-backend monitoring and alerting
- Cost analysis and optimization insights
- Capacity planning and forecasting
- SLA compliance monitoring
- Business intelligence dashboards
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import statistics

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of storage metrics"""
    PERFORMANCE = "performance"           # Latency, throughput, etc.
    CAPACITY = "capacity"                # Storage utilization, growth
    AVAILABILITY = "availability"        # Uptime, reliability
    COST = "cost"                       # Storage and operational costs
    BUSINESS = "business"               # Business-specific metrics
    COMPLIANCE = "compliance"           # SLA and compliance metrics


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"               # Immediate attention required
    HIGH = "high"                      # Urgent but not critical
    MEDIUM = "medium"                  # Important but not urgent
    LOW = "low"                        # Informational
    INFO = "info"                      # General information


class AlertStatus(Enum):
    """Status of alerts"""
    ACTIVE = "active"                  # Currently active
    ACKNOWLEDGED = "acknowledged"       # Acknowledged by operator
    RESOLVED = "resolved"              # Issue resolved
    SUPPRESSED = "suppressed"          # Temporarily suppressed


@dataclass
class MetricDataPoint:
    """Single metric data point"""
    timestamp: datetime
    value: float
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricSeries:
    """Time series of metric data points"""
    metric_name: str
    metric_type: MetricType
    unit: str
    backend: str
    data_points: deque = field(default_factory=lambda: deque(maxlen=1440))  # 24 hours at 1-minute intervals
    aggregated_values: Dict[str, float] = field(default_factory=dict)
    thresholds: Dict[str, float] = field(default_factory=dict)


@dataclass
class StorageAlert:
    """Storage monitoring alert"""
    alert_id: str
    alert_type: str
    severity: AlertSeverity
    status: AlertStatus
    title: str
    description: str
    backend: str
    metric_name: str
    current_value: float
    threshold_value: float
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class CapacityForecast:
    """Storage capacity forecast"""
    backend: str
    metric_name: str
    current_value: float
    projected_values: Dict[str, float]  # timeframe -> projected value
    growth_rate_per_day: float
    confidence_interval: Tuple[float, float]
    forecast_date: datetime
    assumptions: List[str] = field(default_factory=list)


@dataclass
class CostAnalysis:
    """Storage cost analysis"""
    backend: str
    period_start: datetime
    period_end: datetime
    total_cost: float
    cost_breakdown: Dict[str, float]
    cost_per_gb: float
    cost_per_operation: float
    optimization_opportunities: List[str] = field(default_factory=list)
    projected_savings: float = 0.0


class StorageMetricsCollector:
    """
    Comprehensive storage metrics collector for Ainflue event store
    
    Features:
    - Real-time metrics collection from all backends
    - Automated alerting and threshold monitoring
    - Capacity planning and forecasting
    - Cost analysis and optimization insights
    - SLA compliance tracking
    - Business intelligence dashboards
    """
    
    def __init__(self) -> None:
        self._metric_series: Dict[str, MetricSeries] = {}
        self._alerts: Dict[str, StorageAlert] = {}
        self._backend_connections: Dict[str, Any] = {}
        self._collection_tasks: Dict[str, asyncio.Task] = {}
        self._alert_handlers: List[callable] = []
        self._dashboards: Dict[str, Dict[str, Any]] = {}
        self._is_initialized = False
        
        # Configuration
        self.config = {
            'collection_interval_seconds': 60,
            'retention_hours': 168,  # 1 week
            'alert_check_interval_seconds': 30,
            'forecast_days': [7, 30, 90],
            'cost_analysis_interval_hours': 24,
            'sla_targets': {
                'availability_percent': 99.9,
                'max_latency_ms': 100,
                'max_error_rate_percent': 0.1
            }
        }
        
        # Initialize Ainflue business metrics
        self._initialize_business_metrics()
    
    def _initialize_business_metrics(self) -> None:
        """Initialize Ainflue-specific business metrics and thresholds"""
        
        # Define metric configurations for Ainflue business logic
        self._metric_configs = {
            # Performance metrics
            'query_latency_ms': {
                'type': MetricType.PERFORMANCE,
                'unit': 'milliseconds',
                'thresholds': {'warning': 50, 'critical': 100},
                'description': 'Average query response time'
            },
            'throughput_events_per_sec': {
                'type': MetricType.PERFORMANCE,
                'unit': 'events/second',
                'thresholds': {'warning': 10000, 'critical': 5000},
                'description': 'Event processing throughput'
            },
            'error_rate_percent': {
                'type': MetricType.PERFORMANCE,
                'unit': 'percent',
                'thresholds': {'warning': 0.5, 'critical': 1.0},
                'description': 'Error rate percentage'
            },
            
            # Capacity metrics
            'storage_utilization_percent': {
                'type': MetricType.CAPACITY,
                'unit': 'percent',
                'thresholds': {'warning': 80, 'critical': 90},
                'description': 'Storage space utilization'
            },
            'storage_size_gb': {
                'type': MetricType.CAPACITY,
                'unit': 'gigabytes',
                'thresholds': {'warning': 1000, 'critical': 1500},
                'description': 'Total storage size'
            },
            'event_count_total': {
                'type': MetricType.CAPACITY,
                'unit': 'count',
                'thresholds': {'warning': 10000000, 'critical': 15000000},
                'description': 'Total number of events stored'
            },
            
            # Availability metrics
            'uptime_percent': {
                'type': MetricType.AVAILABILITY,
                'unit': 'percent',
                'thresholds': {'warning': 99.5, 'critical': 99.0},
                'description': 'Backend availability percentage'
            },
            'connection_pool_utilization': {
                'type': MetricType.AVAILABILITY,
                'unit': 'percent',
                'thresholds': {'warning': 80, 'critical': 95},
                'description': 'Database connection pool utilization'
            },
            
            # Business metrics specific to Ainflue
            'content_events_per_hour': {
                'type': MetricType.BUSINESS,
                'unit': 'events/hour',
                'thresholds': {'warning': 1000, 'critical': 500},
                'description': 'Content lifecycle events per hour'
            },
            'revenue_events_per_hour': {
                'type': MetricType.BUSINESS,
                'unit': 'events/hour',
                'thresholds': {'warning': 100, 'critical': 50},
                'description': 'Revenue events per hour'
            },
            'user_interaction_events_per_hour': {
                'type': MetricType.BUSINESS,
                'unit': 'events/hour',
                'thresholds': {'warning': 5000, 'critical': 2000},
                'description': 'User interaction events per hour'
            },
            'analytics_processing_lag_minutes': {
                'type': MetricType.BUSINESS,
                'unit': 'minutes',
                'thresholds': {'warning': 15, 'critical': 30},
                'description': 'Analytics processing lag'
            },
            
            # Cost metrics
            'cost_per_hour_usd': {
                'type': MetricType.COST,
                'unit': 'USD/hour',
                'thresholds': {'warning': 50, 'critical': 100},
                'description': 'Storage cost per hour'
            },
            'cost_per_gb_usd': {
                'type': MetricType.COST,
                'unit': 'USD/GB',
                'thresholds': {'warning': 0.20, 'critical': 0.50},
                'description': 'Cost per gigabyte stored'
            }
        }
        
        # Initialize Business Intelligence dashboards
        self._dashboards = {
            'executive_summary': {
                'title': 'Executive Summary Dashboard',
                'metrics': ['storage_size_gb', 'cost_per_hour_usd', 'uptime_percent', 'throughput_events_per_sec'],
                'refresh_interval': 300  # 5 minutes
            },
            'performance_monitoring': {
                'title': 'Performance Monitoring Dashboard',
                'metrics': ['query_latency_ms', 'throughput_events_per_sec', 'error_rate_percent', 'connection_pool_utilization'],
                'refresh_interval': 60  # 1 minute
            },
            'business_analytics': {
                'title': 'Business Analytics Dashboard',
                'metrics': ['content_events_per_hour', 'revenue_events_per_hour', 'user_interaction_events_per_hour', 'analytics_processing_lag_minutes'],
                'refresh_interval': 300  # 5 minutes
            },
            'capacity_planning': {
                'title': 'Capacity Planning Dashboard',
                'metrics': ['storage_utilization_percent', 'storage_size_gb', 'event_count_total'],
                'refresh_interval': 600  # 10 minutes
            },
            'cost_optimization': {
                'title': 'Cost Optimization Dashboard',
                'metrics': ['cost_per_hour_usd', 'cost_per_gb_usd', 'storage_utilization_percent'],
                'refresh_interval': 900  # 15 minutes
            }
        }
    
    async def initialize(self, backend_connections -> None: Dict[str, Any]) -> None:
        """Initialize the storage metrics collector"""
        
        self._backend_connections = backend_connections
        
        # Initialize metric series for each backend
        for backend_name in backend_connections.keys():
            await self._initialize_backend_metrics(backend_name)
        
        # Start collection tasks
        for backend_name in backend_connections.keys():
            task = asyncio.create_task(self._collection_task(backend_name))
            self._collection_tasks[backend_name] = task
        
        # Start monitoring tasks
        asyncio.create_task(self._alert_monitoring_task())
        asyncio.create_task(self._capacity_forecasting_task())
        asyncio.create_task(self._cost_analysis_task())
        asyncio.create_task(self._sla_monitoring_task())
        
        self._is_initialized = True
        logger.info(f"Storage Metrics Collector initialized for {len(backend_connections)} backends")
    
    async def _initialize_backend_metrics(self, backend_name -> None: str) -> None:
        """Initialize metric series for a specific backend"""
        
        for metric_name, config in self._metric_configs.items():
            series_key = f"{backend_name}_{metric_name}"
            
            metric_series = MetricSeries(
                metric_name=metric_name,
                metric_type=config['type'],
                unit=config['unit'],
                backend=backend_name,
                thresholds=config['thresholds']
            )
            
            self._metric_series[series_key] = metric_series
        
        logger.info(f"Initialized {len(self._metric_configs)} metrics for backend {backend_name}")
    
    async def collect_metric(self, backend -> None: str, metric_name -> None: str, 
                           value -> None: float, tags -> None: Optional[Dict[str, str]] = None) -> None:
        """Collect a single metric value"""
        
        series_key = f"{backend}_{metric_name}"
        
        if series_key not in self._metric_series:
            logger.warning(f"Unknown metric series: {series_key}")
            return
        
        metric_series = self._metric_series[series_key]
        
        data_point = MetricDataPoint(
            timestamp=datetime.utcnow(),
            value=value,
            tags=tags or {}
        )
        
        metric_series.data_points.append(data_point)
        
        # Update aggregated values
        await self._update_aggregated_values(metric_series)
        
        # Check for threshold violations
        await self._check_thresholds(metric_series, data_point)
    
    async def _update_aggregated_values(self, metric_series -> None: MetricSeries) -> None:
        """Update aggregated values for metric series"""
        
        if not metric_series.data_points:
            return
        
        values = [dp.value for dp in metric_series.data_points]
        
        metric_series.aggregated_values.update({
            'current': values[-1],
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0
        })
        
        # Calculate percentiles if enough data
        if len(values) >= 10:
            sorted_values = sorted(values)
            metric_series.aggregated_values.update({
                'p50': self._percentile(sorted_values, 50),
                'p95': self._percentile(sorted_values, 95),
                'p99': self._percentile(sorted_values, 99)
            })
    
    def _percentile(self, sorted_values: List[float], percentile: int) -> float:
        """Calculate percentile value"""
        if not sorted_values:
            return 0.0
        
        index = (percentile / 100) * (len(sorted_values) - 1)
        lower_index = int(index)
        upper_index = min(lower_index + 1, len(sorted_values) - 1)
        
        if lower_index == upper_index:
            return sorted_values[lower_index]
        
        # Linear interpolation
        weight = index - lower_index
        return sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight
    
    async def _check_thresholds(self, metric_series -> None: MetricSeries, data_point -> None: MetricDataPoint) -> None:
        """Check if metric violates thresholds and create alerts"""
        
        current_value = data_point.value
        
        for threshold_type, threshold_value in metric_series.thresholds.items():
            # Determine if threshold is violated
            violated = False
            severity = AlertSeverity.INFO
            
            if threshold_type == 'critical':
                severity = AlertSeverity.CRITICAL
                # Handle different threshold types
                if metric_series.metric_name in ['query_latency_ms', 'error_rate_percent', 'storage_utilization_percent']:
                    violated = current_value >= threshold_value
                elif metric_series.metric_name in ['uptime_percent']:
                    violated = current_value <= threshold_value
                else:
                    violated = current_value >= threshold_value
            
            elif threshold_type == 'warning':
                severity = AlertSeverity.HIGH
                if metric_series.metric_name in ['query_latency_ms', 'error_rate_percent', 'storage_utilization_percent']:
                    violated = current_value >= threshold_value
                elif metric_series.metric_name in ['uptime_percent']:
                    violated = current_value <= threshold_value
                else:
                    violated = current_value >= threshold_value
            
            if violated:
                await self._create_alert(
                    metric_series=metric_series,
                    severity=severity,
                    threshold_type=threshold_type,
                    current_value=current_value,
                    threshold_value=threshold_value
                )
    
    async def _create_alert(self, metric_series -> None: MetricSeries, severity -> None: AlertSeverity,
                          threshold_type -> None: str, current_value -> None: float, threshold_value -> None: float) -> None:
        """Create an alert for threshold violation"""
        
        alert_id = f"{metric_series.backend}_{metric_series.metric_name}_{threshold_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Check if similar alert already exists
        existing_alert = self._find_existing_alert(metric_series.backend, metric_series.metric_name, threshold_type)
        if existing_alert and existing_alert.status == AlertStatus.ACTIVE:
            return  # Don't create duplicate alerts
        
        # Create new alert
        alert = StorageAlert(
            alert_id=alert_id,
            alert_type=f"{threshold_type}_threshold_violation",
            severity=severity,
            status=AlertStatus.ACTIVE,
            title=f"{metric_series.metric_name} {threshold_type} threshold exceeded",
            description=f"{metric_series.metric_name} on {metric_series.backend} is {current_value:.2f} {metric_series.unit}, exceeding {threshold_type} threshold of {threshold_value:.2f}",
            backend=metric_series.backend,
            metric_name=metric_series.metric_name,
            current_value=current_value,
            threshold_value=threshold_value,
            created_at=datetime.utcnow(),
            tags={
                'metric_type': metric_series.metric_type.value,
                'backend': metric_series.backend,
                'threshold_type': threshold_type
            }
        )
        
        self._alerts[alert_id] = alert
        
        # Notify alert handlers
        for handler in self._alert_handlers:
            try:
                await handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
        
        logger.warning(f"Alert created: {alert.title}")
    
    def _find_existing_alert(self, backend: str, metric_name: str, threshold_type: str) -> Optional[StorageAlert]:
        """Find existing alert for the same condition"""
        
        for alert in self._alerts.values():
            if (alert.backend == backend and 
                alert.metric_name == metric_name and 
                threshold_type in alert.alert_type and
                alert.status == AlertStatus.ACTIVE):
                return alert
        
        return None
    
    async def _collection_task(self, backend_name -> None: str) -> None:
        """Background task for collecting metrics from a specific backend"""
        
        while self._is_initialized:
            try:
                await self._collect_backend_metrics(backend_name)
                await asyncio.sleep(self.config['collection_interval_seconds'])
            except Exception as e:
                logger.error(f"Collection task error for {backend_name}: {e}")
                await asyncio.sleep(60)  # Retry after 1 minute
    
    async def _collect_backend_metrics(self, backend_name -> None: str) -> None:
        """Collect metrics from a specific backend"""
        
        try:
            # Simulate metric collection (in real implementation, query actual backends)
            
            if backend_name == 'postgresql':
                await self._collect_postgresql_metrics()
            elif backend_name == 'mongodb':
                await self._collect_mongodb_metrics()
            elif backend_name == 'elasticsearch':
                await self._collect_elasticsearch_metrics()
            elif backend_name == 'redis':
                await self._collect_redis_metrics()
            
        except Exception as e:
            logger.error(f"Failed to collect metrics from {backend_name}: {e}")
            
            # Record error metric
            await self.collect_metric(backend_name, 'error_rate_percent', 100.0)
    
    async def _collect_postgresql_metrics(self) -> None:
        """Collect PostgreSQL-specific metrics"""
        
        # Simulate PostgreSQL metrics collection
        import random
        
        base_latency = 15.0
        latency_variation = random.uniform(-5, 10)
        await self.collect_metric('postgresql', 'query_latency_ms', base_latency + latency_variation)
        
        await self.collect_metric('postgresql', 'throughput_events_per_sec', random.uniform(8000, 12000))
        await self.collect_metric('postgresql', 'error_rate_percent', random.uniform(0, 0.2))
        await self.collect_metric('postgresql', 'storage_utilization_percent', random.uniform(65, 85))
        await self.collect_metric('postgresql', 'storage_size_gb', random.uniform(800, 1200))
        await self.collect_metric('postgresql', 'uptime_percent', random.uniform(99.8, 100.0))
        await self.collect_metric('postgresql', 'connection_pool_utilization', random.uniform(30, 70))
        
        # Business metrics
        await self.collect_metric('postgresql', 'content_events_per_hour', random.uniform(800, 1500))
        await self.collect_metric('postgresql', 'revenue_events_per_hour', random.uniform(80, 150))
        
        # Cost metrics
        await self.collect_metric('postgresql', 'cost_per_hour_usd', random.uniform(20, 40))
        await self.collect_metric('postgresql', 'cost_per_gb_usd', random.uniform(0.10, 0.15))
    
    async def _collect_mongodb_metrics(self) -> None:
        """Collect MongoDB-specific metrics"""
        
        import random
        
        await self.collect_metric('mongodb', 'query_latency_ms', random.uniform(8, 25))
        await self.collect_metric('mongodb', 'throughput_events_per_sec', random.uniform(15000, 25000))
        await self.collect_metric('mongodb', 'error_rate_percent', random.uniform(0, 0.1))
        await self.collect_metric('mongodb', 'storage_utilization_percent', random.uniform(55, 75))
        await self.collect_metric('mongodb', 'storage_size_gb', random.uniform(1200, 2000))
        await self.collect_metric('mongodb', 'uptime_percent', random.uniform(99.7, 100.0))
        
        # Business metrics
        await self.collect_metric('mongodb', 'user_interaction_events_per_hour', random.uniform(4000, 8000))
        await self.collect_metric('mongodb', 'analytics_processing_lag_minutes', random.uniform(2, 12))
        
        # Cost metrics
        await self.collect_metric('mongodb', 'cost_per_hour_usd', random.uniform(15, 30))
        await self.collect_metric('mongodb', 'cost_per_gb_usd', random.uniform(0.08, 0.12))
    
    async def _collect_elasticsearch_metrics(self) -> None:
        """Collect Elasticsearch-specific metrics"""
        
        import random
        
        await self.collect_metric('elasticsearch', 'query_latency_ms', random.uniform(20, 50))
        await self.collect_metric('elasticsearch', 'throughput_events_per_sec', random.uniform(5000, 10000))
        await self.collect_metric('elasticsearch', 'error_rate_percent', random.uniform(0, 0.3))
        await self.collect_metric('elasticsearch', 'storage_utilization_percent', random.uniform(70, 90))
        await self.collect_metric('elasticsearch', 'storage_size_gb', random.uniform(500, 1000))
        await self.collect_metric('elasticsearch', 'uptime_percent', random.uniform(99.5, 100.0))
        
        # Cost metrics
        await self.collect_metric('elasticsearch', 'cost_per_hour_usd', random.uniform(25, 45))
        await self.collect_metric('elasticsearch', 'cost_per_gb_usd', random.uniform(0.15, 0.25))
    
    async def _collect_redis_metrics(self) -> None:
        """Collect Redis-specific metrics"""
        
        import random
        
        await self.collect_metric('redis', 'query_latency_ms', random.uniform(1, 5))
        await self.collect_metric('redis', 'throughput_events_per_sec', random.uniform(50000, 100000))
        await self.collect_metric('redis', 'error_rate_percent', random.uniform(0, 0.05))
        await self.collect_metric('redis', 'storage_utilization_percent', random.uniform(40, 60))
        await self.collect_metric('redis', 'storage_size_gb', random.uniform(50, 200))
        await self.collect_metric('redis', 'uptime_percent', random.uniform(99.9, 100.0))
        
        # Cost metrics
        await self.collect_metric('redis', 'cost_per_hour_usd', random.uniform(5, 15))
        await self.collect_metric('redis', 'cost_per_gb_usd', random.uniform(0.20, 0.30))
    
    async def get_metrics_summary(self, backend: Optional[str] = None,
                                metric_type: Optional[MetricType] = None) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        
        summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'backends': {},
            'alerts_summary': {},
            'sla_compliance': {},
            'cost_summary': {}
        }
        
        # Filter metric series
        filtered_series = {}
        for series_key, series in self._metric_series.items():
            if backend and series.backend != backend:
                continue
            if metric_type and series.metric_type != metric_type:
                continue
            filtered_series[series_key] = series
        
        # Group by backend
        backend_metrics = defaultdict(dict)
        for series_key, series in filtered_series.items():
            backend_name = series.backend
            metric_name = series.metric_name
            
            backend_metrics[backend_name][metric_name] = {
                'current_value': series.aggregated_values.get('current'),
                'unit': series.unit,
                'mean': series.aggregated_values.get('mean'),
                'min': series.aggregated_values.get('min'),
                'max': series.aggregated_values.get('max'),
                'p95': series.aggregated_values.get('p95'),
                'data_points': len(series.data_points),
                'last_updated': series.data_points[-1].timestamp.isoformat() if series.data_points else None
            }
        
        summary['backends'] = dict(backend_metrics)
        
        # Alerts summary
        alert_counts = defaultdict(int)
        for alert in self._alerts.values():
            if alert.status == AlertStatus.ACTIVE:
                alert_counts[alert.severity.value] += 1
        
        summary['alerts_summary'] = {
            'total_active_alerts': sum(alert_counts.values()),
            'by_severity': dict(alert_counts),
            'recent_alerts': [
                {
                    'alert_id': alert.alert_id,
                    'title': alert.title,
                    'severity': alert.severity.value,
                    'backend': alert.backend,
                    'created_at': alert.created_at.isoformat()
                }
                for alert in sorted(self._alerts.values(), 
                                  key=lambda a: a.created_at, reverse=True)[:5]
            ]
        }
        
        # SLA compliance
        sla_compliance = await self._calculate_sla_compliance()
        summary['sla_compliance'] = sla_compliance
        
        # Cost summary
        total_cost = 0.0
        cost_by_backend = {}
        
        for backend_name, metrics in backend_metrics.items():
            if 'cost_per_hour_usd' in metrics:
                backend_cost = metrics['cost_per_hour_usd']['current_value'] or 0
                cost_by_backend[backend_name] = backend_cost
                total_cost += backend_cost
        
        summary['cost_summary'] = {
            'total_hourly_cost_usd': total_cost,
            'daily_cost_usd': total_cost * 24,
            'monthly_cost_usd': total_cost * 24 * 30,
            'cost_by_backend': cost_by_backend
        }
        
        return summary
    
    async def _calculate_sla_compliance(self) -> Dict[str, Any]:
        """Calculate SLA compliance metrics"""
        
        compliance_results = {}
        
        for backend_name in self._backend_connections.keys():
            backend_compliance = {}
            
            # Availability SLA
            uptime_series = self._metric_series.get(f"{backend_name}_uptime_percent")
            if uptime_series and uptime_series.aggregated_values:
                current_uptime = uptime_series.aggregated_values.get('current', 0)
                target_uptime = self.config['sla_targets']['availability_percent']
                backend_compliance['availability'] = {
                    'current_percent': current_uptime,
                    'target_percent': target_uptime,
                    'compliant': current_uptime >= target_uptime
                }
            
            # Latency SLA
            latency_series = self._metric_series.get(f"{backend_name}_query_latency_ms")
            if latency_series and latency_series.aggregated_values:
                current_latency = latency_series.aggregated_values.get('p95', 0)
                target_latency = self.config['sla_targets']['max_latency_ms']
                backend_compliance['latency'] = {
                    'current_p95_ms': current_latency,
                    'target_max_ms': target_latency,
                    'compliant': current_latency <= target_latency
                }
            
            # Error rate SLA
            error_series = self._metric_series.get(f"{backend_name}_error_rate_percent")
            if error_series and error_series.aggregated_values:
                current_error_rate = error_series.aggregated_values.get('mean', 0)
                target_error_rate = self.config['sla_targets']['max_error_rate_percent']
                backend_compliance['error_rate'] = {
                    'current_percent': current_error_rate,
                    'target_max_percent': target_error_rate,
                    'compliant': current_error_rate <= target_error_rate
                }
            
            compliance_results[backend_name] = backend_compliance
        
        return compliance_results
    
    async def generate_capacity_forecast(self, backend: str, 
                                       metric_name: str) -> CapacityForecast:
        """Generate capacity forecast for specific metric"""
        
        series_key = f"{backend}_{metric_name}"
        
        if series_key not in self._metric_series:
            raise ValueError(f"Metric series {series_key} not found")
        
        metric_series = self._metric_series[series_key]
        
        if len(metric_series.data_points) < 10:
            raise ValueError("Insufficient data for forecasting")
        
        # Calculate growth rate (simplified linear regression)
        data_points = list(metric_series.data_points)
        
        # Use last 7 days of data for trend calculation
        recent_points = data_points[-min(len(data_points), 7 * 24 * 60 // self.config['collection_interval_seconds']):]
        
        if len(recent_points) < 2:
            growth_rate = 0.0
        else:
            # Simple linear growth calculation
            time_diff = (recent_points[-1].timestamp - recent_points[0].timestamp).total_seconds() / (24 * 3600)  # days
            value_diff = recent_points[-1].value - recent_points[0].value
            growth_rate = value_diff / max(time_diff, 0.1)  # per day
        
        current_value = recent_points[-1].value
        
        # Generate projections
        projected_values = {}
        for days in self.config['forecast_days']:
            projected_value = current_value + (growth_rate * days)
            projected_values[f"{days}_days"] = max(0, projected_value)  # Don't allow negative values
        
        # Calculate confidence interval (simplified)
        values = [dp.value for dp in recent_points]
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        confidence_interval = (current_value - 2 * std_dev, current_value + 2 * std_dev)
        
        forecast = CapacityForecast(
            backend=backend,
            metric_name=metric_name,
            current_value=current_value,
            projected_values=projected_values,
            growth_rate_per_day=growth_rate,
            confidence_interval=confidence_interval,
            forecast_date=datetime.utcnow(),
            assumptions=[
                "Linear growth based on recent trend",
                f"Using last {len(recent_points)} data points",
                "Assumes current usage patterns continue"
            ]
        )
        
        return forecast
    
    async def generate_cost_analysis(self, backend: str, 
                                   period_days: int = 30) -> CostAnalysis:
        """Generate cost analysis for backend over specified period"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        
        # Get cost metrics
        cost_series = self._metric_series.get(f"{backend}_cost_per_hour_usd")
        storage_series = self._metric_series.get(f"{backend}_storage_size_gb")
        
        if not cost_series or not storage_series:
            raise ValueError(f"Cost metrics not available for backend {backend}")
        
        # Calculate average costs
        cost_data_points = [dp for dp in cost_series.data_points 
                           if start_date <= dp.timestamp <= end_date]
        storage_data_points = [dp for dp in storage_series.data_points 
                              if start_date <= dp.timestamp <= end_date]
        
        if not cost_data_points or not storage_data_points:
            raise ValueError("Insufficient data for cost analysis")
        
        avg_hourly_cost = statistics.mean([dp.value for dp in cost_data_points])
        avg_storage_gb = statistics.mean([dp.value for dp in storage_data_points])
        
        total_cost = avg_hourly_cost * 24 * period_days
        cost_per_gb = avg_hourly_cost / max(avg_storage_gb, 1)
        
        # Cost breakdown (simplified)
        cost_breakdown = {
            'storage_cost': total_cost * 0.6,
            'compute_cost': total_cost * 0.3,
            'network_cost': total_cost * 0.1
        }
        
        # Optimization opportunities
        optimization_opportunities = []
        utilization_series = self._metric_series.get(f"{backend}_storage_utilization_percent")
        
        if utilization_series and utilization_series.aggregated_values:
            avg_utilization = utilization_series.aggregated_values.get('mean', 0)
            
            if avg_utilization < 50:
                optimization_opportunities.append("Storage utilization is low - consider downsizing")
                projected_savings = total_cost * 0.3
            elif avg_utilization < 70:
                optimization_opportunities.append("Moderate storage utilization - optimization possible")
                projected_savings = total_cost * 0.15
            else:
                projected_savings = 0.0
        else:
            projected_savings = 0.0
        
        # Check for cost anomalies
        if avg_hourly_cost > self._metric_configs['cost_per_hour_usd']['thresholds']['warning']:
            optimization_opportunities.append("Hourly cost exceeds normal range")
        
        analysis = CostAnalysis(
            backend=backend,
            period_start=start_date,
            period_end=end_date,
            total_cost=total_cost,
            cost_breakdown=cost_breakdown,
            cost_per_gb=cost_per_gb,
            cost_per_operation=total_cost / max(period_days * 1000, 1),  # Simplified
            optimization_opportunities=optimization_opportunities,
            projected_savings=projected_savings
        )
        
        return analysis
    
    async def get_dashboard_data(self, dashboard_name: str) -> Dict[str, Any]:
        """Get data for specific dashboard"""
        
        if dashboard_name not in self._dashboards:
            raise ValueError(f"Dashboard {dashboard_name} not found")
        
        dashboard_config = self._dashboards[dashboard_name]
        dashboard_data = {
            'title': dashboard_config['title'],
            'refresh_interval': dashboard_config['refresh_interval'],
            'last_updated': datetime.utcnow().isoformat(),
            'metrics': {}
        }
        
        # Collect data for each metric in dashboard
        for metric_name in dashboard_config['metrics']:
            metric_data = {}
            
            # Collect from all backends
            for backend_name in self._backend_connections.keys():
                series_key = f"{backend_name}_{metric_name}"
                
                if series_key in self._metric_series:
                    series = self._metric_series[series_key]
                    
                    metric_data[backend_name] = {
                        'current_value': series.aggregated_values.get('current'),
                        'unit': series.unit,
                        'trend': self._calculate_trend(series),
                        'status': self._get_metric_status(series),
                        'chart_data': self._get_chart_data(series)
                    }
            
            dashboard_data['metrics'][metric_name] = metric_data
        
        return dashboard_data
    
    def _calculate_trend(self, metric_series: MetricSeries) -> str:
        """Calculate trend direction for metric"""
        
        if len(metric_series.data_points) < 10:
            return 'stable'
        
        recent_values = [dp.value for dp in list(metric_series.data_points)[-10:]]
        
        # Calculate simple trend
        first_half = statistics.mean(recent_values[:5])
        second_half = statistics.mean(recent_values[5:])
        
        change_percent = ((second_half - first_half) / max(first_half, 0.1)) * 100
        
        if change_percent > 5:
            return 'increasing'
        elif change_percent < -5:
            return 'decreasing'
        else:
            return 'stable'
    
    def _get_metric_status(self, metric_series: MetricSeries) -> str:
        """Get status of metric based on thresholds"""
        
        if not metric_series.aggregated_values or not metric_series.thresholds:
            return 'unknown'
        
        current_value = metric_series.aggregated_values.get('current', 0)
        
        # Check critical threshold
        if 'critical' in metric_series.thresholds:
            critical_threshold = metric_series.thresholds['critical']
            
            if metric_series.metric_name in ['uptime_percent']:
                if current_value <= critical_threshold:
                    return 'critical'
            else:
                if current_value >= critical_threshold:
                    return 'critical'
        
        # Check warning threshold
        if 'warning' in metric_series.thresholds:
            warning_threshold = metric_series.thresholds['warning']
            
            if metric_series.metric_name in ['uptime_percent']:
                if current_value <= warning_threshold:
                    return 'warning'
            else:
                if current_value >= warning_threshold:
                    return 'warning'
        
        return 'healthy'
    
    def _get_chart_data(self, metric_series: MetricSeries, points: int = 60) -> List[Dict[str, Any]]:
        """Get chart data for metric visualization"""
        
        # Get last N data points
        recent_points = list(metric_series.data_points)[-points:]
        
        chart_data = []
        for dp in recent_points:
            chart_data.append({
                'timestamp': dp.timestamp.isoformat(),
                'value': dp.value
            })
        
        return chart_data
    
    def add_alert_handler(self, handler -> None: callable) -> None:
        """Add alert notification handler"""
        self._alert_handlers.append(handler)
    
    async def acknowledge_alert(self, alert_id -> None: str, acknowledged_by -> None: str) -> None:
        """Acknowledge an alert"""
        
        if alert_id in self._alerts:
            alert = self._alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.utcnow()
            alert.tags['acknowledged_by'] = acknowledged_by
            
            logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
    
    async def resolve_alert(self, alert_id -> None: str, resolved_by -> None: str) -> None:
        """Resolve an alert"""
        
        if alert_id in self._alerts:
            alert = self._alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.utcnow()
            alert.tags['resolved_by'] = resolved_by
            
            logger.info(f"Alert {alert_id} resolved by {resolved_by}")
    
    async def _alert_monitoring_task(self) -> None:
        """Background task for alert monitoring"""
        
        while self._is_initialized:
            try:
                await self._process_alert_lifecycle()
                await asyncio.sleep(self.config['alert_check_interval_seconds'])
            except Exception as e:
                logger.error(f"Alert monitoring task error: {e}")
                await asyncio.sleep(60)
    
    async def _process_alert_lifecycle(self) -> None:
        """Process alert lifecycle (auto-resolve, cleanup, etc.)"""
        
        current_time = datetime.utcnow()
        
        for alert_id, alert in list(self._alerts.items()):
            # Auto-resolve alerts that are no longer violating thresholds
            if alert.status == AlertStatus.ACTIVE:
                series_key = f"{alert.backend}_{alert.metric_name}"
                
                if series_key in self._metric_series:
                    metric_series = self._metric_series[series_key]
                    
                    if metric_series.aggregated_values:
                        current_value = metric_series.aggregated_values.get('current', 0)
                        
                        # Check if threshold is no longer violated
                        threshold_key = 'critical' if 'critical' in alert.alert_type else 'warning'
                        threshold_value = metric_series.thresholds.get(threshold_key)
                        
                        if threshold_value:
                            is_violated = False
                            
                            if alert.metric_name in ['uptime_percent']:
                                is_violated = current_value <= threshold_value
                            else:
                                is_violated = current_value >= threshold_value
                            
                            if not is_violated:
                                alert.status = AlertStatus.RESOLVED
                                alert.resolved_at = current_time
                                alert.tags['auto_resolved'] = 'true'
            
            # Clean up old resolved alerts (older than 24 hours)
            if (alert.status == AlertStatus.RESOLVED and 
                alert.resolved_at and
                (current_time - alert.resolved_at).total_seconds() > 24 * 3600):
                del self._alerts[alert_id]
    
    async def _capacity_forecasting_task(self) -> None:
        """Background task for capacity forecasting"""
        
        while self._is_initialized:
            try:
                await self._generate_capacity_forecasts()
                await asyncio.sleep(24 * 3600)  # Daily forecasting
            except Exception as e:
                logger.error(f"Capacity forecasting task error: {e}")
                await asyncio.sleep(3600)
    
    async def _generate_capacity_forecasts(self) -> None:
        """Generate capacity forecasts for key metrics"""
        
        capacity_metrics = ['storage_size_gb', 'storage_utilization_percent', 'event_count_total']
        
        for backend_name in self._backend_connections.keys():
            for metric_name in capacity_metrics:
                try:
                    forecast = await self.generate_capacity_forecast(backend_name, metric_name)
                    
                    # Check for capacity alerts
                    for days, projected_value in forecast.projected_values.items():
                        if metric_name == 'storage_utilization_percent' and projected_value > 90:
                            await self._create_capacity_alert(backend_name, metric_name, days, projected_value)
                    
                except Exception as e:
                    logger.debug(f"Could not generate forecast for {backend_name}.{metric_name}: {e}")
    
    async def _create_capacity_alert(self, backend -> None: str, metric_name -> None: str, 
                                   timeframe -> None: str, projected_value -> None: float) -> None:
        """Create capacity planning alert"""
        
        alert_id = f"capacity_{backend}_{metric_name}_{timeframe}_{datetime.utcnow().strftime('%Y%m%d')}"
        
        alert = StorageAlert(
            alert_id=alert_id,
            alert_type="capacity_forecast",
            severity=AlertSeverity.MEDIUM,
            status=AlertStatus.ACTIVE,
            title=f"Capacity forecast alert for {metric_name}",
            description=f"Projected {metric_name} for {backend} will reach {projected_value:.1f}% in {timeframe}",
            backend=backend,
            metric_name=metric_name,
            current_value=0,  # Not applicable for forecasts
            threshold_value=90,  # Capacity threshold
            created_at=datetime.utcnow(),
            tags={
                'type': 'capacity_forecast',
                'timeframe': timeframe
            }
        )
        
        self._alerts[alert_id] = alert
        logger.warning(f"Capacity alert created: {alert.title}")
    
    async def _cost_analysis_task(self) -> None:
        """Background task for cost analysis"""
        
        while self._is_initialized:
            try:
                await self._perform_cost_analysis()
                await asyncio.sleep(self.config['cost_analysis_interval_hours'] * 3600)
            except Exception as e:
                logger.error(f"Cost analysis task error: {e}")
                await asyncio.sleep(3600)
    
    async def _perform_cost_analysis(self) -> None:
        """Perform cost analysis for all backends"""
        
        for backend_name in self._backend_connections.keys():
            try:
                analysis = await self.generate_cost_analysis(backend_name)
                
                # Check for cost optimization opportunities
                if analysis.optimization_opportunities:
                    logger.info(f"Cost optimization opportunities for {backend_name}: {analysis.optimization_opportunities}")
                
                # Check cost thresholds
                if analysis.total_cost > 1000:  # $1000 threshold
                    await self._create_cost_alert(backend_name, analysis.total_cost)
                
            except Exception as e:
                logger.debug(f"Could not generate cost analysis for {backend_name}: {e}")
    
    async def _create_cost_alert(self, backend -> None: str, total_cost -> None: float) -> None:
        """Create cost threshold alert"""
        
        alert_id = f"cost_{backend}_{datetime.utcnow().strftime('%Y%m%d')}"
        
        alert = StorageAlert(
            alert_id=alert_id,
            alert_type="cost_threshold",
            severity=AlertSeverity.MEDIUM,
            status=AlertStatus.ACTIVE,
            title=f"High cost alert for {backend}",
            description=f"Monthly cost for {backend} is ${total_cost:.2f}, exceeding threshold",
            backend=backend,
            metric_name="cost_per_hour_usd",
            current_value=total_cost,
            threshold_value=1000,
            created_at=datetime.utcnow(),
            tags={'type': 'cost_threshold'}
        )
        
        self._alerts[alert_id] = alert
        logger.warning(f"Cost alert created: {alert.title}")
    
    async def _sla_monitoring_task(self) -> None:
        """Background task for SLA compliance monitoring"""
        
        while self._is_initialized:
            try:
                compliance = await self._calculate_sla_compliance()
                
                # Check for SLA violations
                for backend_name, backend_compliance in compliance.items():
                    for sla_type, sla_data in backend_compliance.items():
                        if not sla_data.get('compliant', True):
                            await self._create_sla_violation_alert(backend_name, sla_type, sla_data)
                
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                logger.error(f"SLA monitoring task error: {e}")
                await asyncio.sleep(300)
    
    async def _create_sla_violation_alert(self, backend -> None: str, sla_type -> None: str, sla_data -> None: Dict[str, Any]) -> None:
        """Create SLA violation alert"""
        
        alert_id = f"sla_{backend}_{sla_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M')}"
        
        # Skip if similar alert already exists
        if any(alert.alert_id.startswith(f"sla_{backend}_{sla_type}") 
               for alert in self._alerts.values() 
               if alert.status == AlertStatus.ACTIVE):
            return
        
        if sla_type == 'availability':
            description = f"Availability SLA violation: {sla_data['current_percent']:.2f}% < {sla_data['target_percent']:.2f}%"
        elif sla_type == 'latency':
            description = f"Latency SLA violation: {sla_data['current_p95_ms']:.2f}ms > {sla_data['target_max_ms']:.2f}ms"
        elif sla_type == 'error_rate':
            description = f"Error rate SLA violation: {sla_data['current_percent']:.2f}% > {sla_data['target_max_percent']:.2f}%"
        else:
            description = f"SLA violation for {sla_type}"
        
        alert = StorageAlert(
            alert_id=alert_id,
            alert_type=f"sla_violation_{sla_type}",
            severity=AlertSeverity.HIGH,
            status=AlertStatus.ACTIVE,
            title=f"SLA violation: {sla_type} for {backend}",
            description=description,
            backend=backend,
            metric_name=f"{sla_type}_sla",
            current_value=list(sla_data.values())[0] if sla_data else 0,
            threshold_value=list(sla_data.values())[1] if len(sla_data) > 1 else 0,
            created_at=datetime.utcnow(),
            tags={'type': 'sla_violation', 'sla_type': sla_type}
        )
        
        self._alerts[alert_id] = alert
        logger.error(f"SLA violation alert created: {alert.title}")


# Export public APIs
__all__ = [
    'StorageMetricsCollector',
    'MetricType',
    'AlertSeverity',
    'AlertStatus',
    'MetricDataPoint',
    'MetricSeries',
    'StorageAlert',
    'CapacityForecast',
    'CostAnalysis'
]