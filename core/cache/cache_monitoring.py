"""Cache Monitoring for IA Influencer Agent Platform
Advanced monitoring, alerting, and observability for cache systems

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""import asyncio
import logging
import json
import time
import threading
from typing import Any, Dict, List, Optional, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import statistics
import psutil
import traceback

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """Alert severity levels"""    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetricType(Enum):
    """Types of metrics"""    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"

class MonitoringEvent(Enum):
    """Cache monitoring events"""    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    CACHE_EVICTION = "cache_eviction"
    CACHE_ERROR = "cache_error"
    HIGH_LATENCY = "high_latency"
    HIGH_MEMORY_USAGE = "high_memory_usage"
    LOW_HIT_RATE = "low_hit_rate"
    CONNECTION_FAILURE = "connection_failure"

@dataclass
class MetricValue:
    """Single metric value with timestamp"""    value: float
    timestamp: datetime
    labels: Dict[str, str] = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = {}

@dataclass
class Alert:
    """Cache alert information"""    id: str
    level: AlertLevel
    title: str
    message: str
    metric_name: str
    metric_value: float
    threshold: float
    cache_name: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        if self.resolved_at:
            data['resolved_at'] = self.resolved_at.isoformat()
        data['level'] = self.level.value
        return data

@dataclass
class CacheHealthStatus:
    """Overall cache health status"""    cache_name: str
    status: str  # healthy, warning, error, critical
    hit_rate: float
    memory_utilization: float
    average_latency: float
    error_rate: float
    uptime: float
    last_updated: datetime
    issues: List[str]
    recommendations: List[str]

class MetricCollector:
    """Collect and store cache metrics"""    
    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        self.metrics = defaultdict(lambda: deque(maxlen=10000))  # Store up to 10k data points per metric
        self.lock = threading.RLock()
        
        # Metric metadata
        self.metric_metadata = {}
        
    def record_metric(self,
                     name: str,
                     value: float,
                     metric_type: MetricType = MetricType.GAUGE,
                     labels: Optional[Dict[str, str]] = None,
                     timestamp: Optional[datetime] = None):
        """Record a metric value"""        
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        with self.lock:
            metric_key = self._generate_metric_key(name, labels)
            metric_value = MetricValue(value, timestamp, labels or {})
            
            self.metrics[metric_key].append(metric_value)
            
            # Store metadata
            self.metric_metadata[metric_key] = {
                'name': name,
                'type': metric_type,
                'labels': labels or {},
                'last_updated': timestamp
            }
            
            # Clean old metrics
            self._cleanup_old_metrics()
    
    def _generate_metric_key(self, name: str, labels: Optional[Dict[str, str]]) -> str:
        """Generate unique key for metric with labels"""        if not labels:
            return name
        
        label_parts = [f"{k}={v}" for k, v in sorted(labels.items())]
        return f"{name}:{':'.join(label_parts)}"
    
    def _cleanup_old_metrics(self):
        """Remove old metric values"""        cutoff_time = datetime.utcnow() - timedelta(hours=self.retention_hours)
        
        for metric_key in list(self.metrics.keys()):
            metric_values = self.metrics[metric_key]
            
            # Remove old values
            while metric_values and metric_values[0].timestamp < cutoff_time:
                metric_values.popleft()
            
            # Remove empty metrics
            if not metric_values:
                del self.metrics[metric_key]
                if metric_key in self.metric_metadata:
                    del self.metric_metadata[metric_key]
    
    def get_metric_values(self,
                         name: str,
                         labels: Optional[Dict[str, str]] = None,
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> List[MetricValue]:
        """Get metric values for time range"""        
        metric_key = self._generate_metric_key(name, labels)
        
        with self.lock:
            if metric_key not in self.metrics:
                return []
            
            values = list(self.metrics[metric_key])
            
            # Filter by time range
            if start_time or end_time:
                filtered_values = []
                for value in values:
                    if start_time and value.timestamp < start_time:
                        continue
                    if end_time and value.timestamp > end_time:
                        continue
                    filtered_values.append(value)
                values = filtered_values
            
            return values
    
    def get_latest_value(self, name: str, labels: Optional[Dict[str, str]] = None) -> Optional[MetricValue]:
        """Get latest value for metric"""        metric_key = self._generate_metric_key(name, labels)
        
        with self.lock:
            if metric_key not in self.metrics or not self.metrics[metric_key]:
                return None
            
            return self.metrics[metric_key][-1]
    
    def get_metric_statistics(self,
                            name: str,
                            labels: Optional[Dict[str, str]] = None,
                            window_minutes: int = 60) -> Dict[str, float]:
        """Get statistical summary for metric"""        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=window_minutes)
        
        values = self.get_metric_values(name, labels, start_time, end_time)
        
        if not values:
            return {}
        
        numeric_values = [v.value for v in values]
        
        return {
            'count': len(numeric_values),
            'min': min(numeric_values),
            'max': max(numeric_values),
            'mean': statistics.mean(numeric_values),
            'median': statistics.median(numeric_values),
            'std_dev': statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0.0,
            'p95': self._percentile(numeric_values, 95),
            'p99': self._percentile(numeric_values, 99)
        }
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile"""        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = (percentile / 100.0) * (len(sorted_values) - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower = sorted_values[int(index)]
            upper = sorted_values[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))

class AlertManager:
    """Manage cache alerts and notifications"""    
    def __init__(self):
        self.alerts = {}  # alert_id -> Alert
        self.alert_rules = {}  # rule_name -> rule_config
        self.alert_handlers = []  # List of alert handler functions
        self.lock = threading.RLock()
        
        # Default alert rules
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Setup default alerting rules"""        
        self.add_alert_rule(
            name="low_hit_rate",
            metric_name="cache_hit_rate",
            threshold=0.8,
            comparison="<",
            level=AlertLevel.WARNING,
            window_minutes=5,
            title="Low Cache Hit Rate",
            message_template="Cache hit rate is {value:.2%}, below threshold of {threshold:.2%}"
        )
        
        self.add_alert_rule(
            name="high_memory_usage",
            metric_name="memory_utilization",
            threshold=0.9,
            comparison=">",
            level=AlertLevel.ERROR,
            window_minutes=2,
            title="High Memory Usage",
            message_template="Memory utilization is {value:.1%}, above threshold of {threshold:.1%}"
        )
        
        self.add_alert_rule(
            name="high_latency",
            metric_name="average_latency",
            threshold=100.0,  # 100ms
            comparison=">",
            level=AlertLevel.WARNING,
            window_minutes=5,
            title="High Cache Latency",
            message_template="Average latency is {value:.2f}ms, above threshold of {threshold:.2f}ms"
        )
        
        self.add_alert_rule(
            name="error_rate",
            metric_name="error_rate",
            threshold=0.05,  # 5%
            comparison=">",
            level=AlertLevel.ERROR,
            window_minutes=5,
            title="High Error Rate",
            message_template="Error rate is {value:.2%}, above threshold of {threshold:.2%}"
        )
    
    def add_alert_rule(self,
                      name: str,
                      metric_name: str,
                      threshold: float,
                      comparison: str,  # >, <, >=, <=, ==, !=
                      level: AlertLevel,
                      window_minutes: int = 5,
                      title: str = "",
                      message_template: str = "",
                      labels: Optional[Dict[str, str]] = None):
        """Add alert rule"""        
        rule = {
            'name': name,
            'metric_name': metric_name,
            'threshold': threshold,
            'comparison': comparison,
            'level': level,
            'window_minutes': window_minutes,
            'title': title or f"Alert for {metric_name}",
            'message_template': message_template or f"{metric_name} is {{value}}, threshold: {{threshold}}",
            'labels': labels or {},
            'enabled': True
        }
        
        with self.lock:
            self.alert_rules[name] = rule
    
    def remove_alert_rule(self, name: str):
        """Remove alert rule"""        with self.lock:
            if name in self.alert_rules:
                del self.alert_rules[name]
    
    def add_alert_handler(self, handler: Callable[[Alert], None]):
        """Add alert handler function"""        self.alert_handlers.append(handler)
    
    def check_alerts(self, metric_collector: MetricCollector, cache_name: str):
        """Check all alert rules against current metrics"""        
        with self.lock:
            for rule_name, rule in self.alert_rules.items():
                if not rule.get('enabled', True):
                    continue
                
                try:
                    self._check_rule(rule, metric_collector, cache_name)
                except Exception as e:
                    logger.error(f"Error checking alert rule {rule_name}: {e}")
    
    def _check_rule(self, rule: Dict[str, Any], metric_collector: MetricCollector, cache_name: str):
        """Check single alert rule"""        
        # Get metric statistics for window
        stats = metric_collector.get_metric_statistics(
            rule['metric_name'],
            rule.get('labels'),
            rule['window_minutes']
        )
        
        if not stats:
            return
        
        # Use mean value for comparison
        current_value = stats['mean']
        threshold = rule['threshold']
        comparison = rule['comparison']
        
        # Evaluate condition
        triggered = False
        if comparison == '>':
            triggered = current_value > threshold
        elif comparison == '<':
            triggered = current_value < threshold
        elif comparison == '>=':
            triggered = current_value >= threshold
        elif comparison == '<=':
            triggered = current_value <= threshold
        elif comparison == '==':
            triggered = abs(current_value - threshold) < 0.001
        elif comparison == '!=':
            triggered = abs(current_value - threshold) >= 0.001
        
        # Generate alert ID
        alert_id = f"{cache_name}:{rule['name']}"
        
        if triggered:
            # Create or update alert
            if alert_id not in self.alerts or self.alerts[alert_id].resolved:
                alert = Alert(
                    id=alert_id,
                    level=rule['level'],
                    title=rule['title'],
                    message=rule['message_template'].format(
                        value=current_value,
                        threshold=threshold
                    ),
                    metric_name=rule['metric_name'],
                    metric_value=current_value,
                    threshold=threshold,
                    cache_name=cache_name,
                    timestamp=datetime.utcnow()
                )
                
                self.alerts[alert_id] = alert
                
                # Notify handlers
                for handler in self.alert_handlers:
                    try:
                        handler(alert)
                    except Exception as e:
                        logger.error(f"Alert handler error: {e}")
        else:
            # Resolve alert if it exists
            if alert_id in self.alerts and not self.alerts[alert_id].resolved:
                self.alerts[alert_id].resolved = True
                self.alerts[alert_id].resolved_at = datetime.utcnow()
    
    def get_active_alerts(self, cache_name: Optional[str] = None) -> List[Alert]:
        """Get active alerts"""        with self.lock:
            alerts = [alert for alert in self.alerts.values() if not alert.resolved]
            
            if cache_name:
                alerts = [alert for alert in alerts if alert.cache_name == cache_name]
            
            return sorted(alerts, key=lambda a: a.timestamp, reverse=True)
    
    def get_alert_history(self,
                         cache_name: Optional[str] = None,
                         hours: int = 24) -> List[Alert]:
        """Get alert history"""        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        with self.lock:
            alerts = [
                alert for alert in self.alerts.values()
                if alert.timestamp >= cutoff_time
            ]
            
            if cache_name:
                alerts = [alert for alert in alerts if alert.cache_name == cache_name]
            
            return sorted(alerts, key=lambda a: a.timestamp, reverse=True)

class CacheMonitor:
    """Main cache monitoring class"""    
    def __init__(self, monitoring_interval: int = 30):
        self.monitoring_interval = monitoring_interval
        self.metric_collector = MetricCollector()
        self.alert_manager = AlertManager()
        self.cache_instances = {}
        self.monitoring_tasks = {}
        
        # System metrics
        self.system_metrics_enabled = True
        
        # Setup default alert handlers
        self.alert_manager.add_alert_handler(self._log_alert)
        
        logger.info("CacheMonitor initialized")
    
    def register_cache(self, name: str, cache_instance):
        """Register cache for monitoring"""        self.cache_instances[name] = cache_instance
        logger.info(f"Registered cache '{name}' for monitoring")
    
    def start_monitoring(self, cache_name: str):
        """Start monitoring for specific cache"""        if cache_name not in self.cache_instances:
            logger.error(f"Cache '{cache_name}' not registered")
            return
        
        # Start monitoring task
        task = asyncio.create_task(self._monitoring_loop(cache_name))
        self.monitoring_tasks[cache_name] = task
        logger.info(f"Started monitoring for cache '{cache_name}'")
    
    def stop_monitoring(self, cache_name: str):
        """Stop monitoring for specific cache"""        if cache_name in self.monitoring_tasks:
            self.monitoring_tasks[cache_name].cancel()
            del self.monitoring_tasks[cache_name]
            logger.info(f"Stopped monitoring for cache '{cache_name}'")
    
    async def _monitoring_loop(self, cache_name: str):
        """Main monitoring loop for cache"""        try:
            while True:
                await self._collect_cache_metrics(cache_name)
                await self._collect_system_metrics()
                self.alert_manager.check_alerts(self.metric_collector, cache_name)
                await asyncio.sleep(self.monitoring_interval)
        except asyncio.CancelledError:
            logger.info(f"Monitoring cancelled for cache '{cache_name}'")
        except Exception as e:
            logger.error(f"Monitoring error for cache '{cache_name}': {e}")
    
    async def _collect_cache_metrics(self, cache_name: str):
        """Collect metrics from cache instance"""        cache = self.cache_instances[cache_name]
        
        try:
            # Get cache statistics
            if hasattr(cache, 'get_stats'):
                stats = await cache.get_stats() if asyncio.iscoroutinefunction(cache.get_stats) else cache.get_stats()
                
                # Record basic metrics
                labels = {'cache': cache_name}
                
                if 'hit_rate' in stats:
                    self.metric_collector.record_metric('cache_hit_rate', stats['hit_rate'], MetricType.GAUGE, labels)
                
                if 'miss_rate' in stats:
                    self.metric_collector.record_metric('cache_miss_rate', stats['miss_rate'], MetricType.GAUGE, labels)
                
                if 'memory_usage' in stats and 'memory_limit' in stats:
                    utilization = stats['memory_usage'] / stats['memory_limit'] if stats['memory_limit'] > 0 else 0
                    self.metric_collector.record_metric('memory_utilization', utilization, MetricType.GAUGE, labels)
                
                if 'average_latency' in stats:
                    self.metric_collector.record_metric('average_latency', stats['average_latency'], MetricType.GAUGE, labels)
                
                if 'total_requests' in stats:
                    self.metric_collector.record_metric('total_requests', stats['total_requests'], MetricType.COUNTER, labels)
                
                if 'errors' in stats:
                    self.metric_collector.record_metric('total_errors', stats['errors'], MetricType.COUNTER, labels)
                
                # Calculate error rate
                if 'total_requests' in stats and 'errors' in stats and stats['total_requests'] > 0:
                    error_rate = stats['errors'] / stats['total_requests']
                    self.metric_collector.record_metric('error_rate', error_rate, MetricType.GAUGE, labels)
                
                # Record evictions if available
                if 'evictions' in stats:
                    self.metric_collector.record_metric('evictions', stats['evictions'], MetricType.COUNTER, labels)
                
                # Record connection info if available
                if 'connections' in stats:
                    self.metric_collector.record_metric('active_connections', stats['connections'], MetricType.GAUGE, labels)
        
        except Exception as e:
            logger.error(f"Failed to collect metrics for cache '{cache_name}': {e}")
            # Record error metric
            labels = {'cache': cache_name}
            self.metric_collector.record_metric('monitoring_errors', 1, MetricType.COUNTER, labels)
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics"""        if not self.system_metrics_enabled:
            return
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metric_collector.record_metric('system_cpu_usage', cpu_percent / 100.0, MetricType.GAUGE)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.metric_collector.record_metric('system_memory_usage', memory.percent / 100.0, MetricType.GAUGE)
            self.metric_collector.record_metric('system_memory_available', memory.available, MetricType.GAUGE)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.metric_collector.record_metric('system_disk_usage', disk.percent / 100.0, MetricType.GAUGE)
            
            # Network I/O
            network = psutil.net_io_counters()
            self.metric_collector.record_metric('system_network_bytes_sent', network.bytes_sent, MetricType.COUNTER)
            self.metric_collector.record_metric('system_network_bytes_recv', network.bytes_recv, MetricType.COUNTER)
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    def _log_alert(self, alert: Alert):
        """Default alert handler - log to logger"""        log_level = {
            AlertLevel.INFO: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.ERROR: logging.ERROR,
            AlertLevel.CRITICAL: logging.CRITICAL
        }.get(alert.level, logging.WARNING)
        
        logger.log(log_level, f"ALERT [{alert.level.value.upper()}] {alert.title}: {alert.message}")
    
    def get_cache_health(self, cache_name: str) -> CacheHealthStatus:
        """Get overall health status for cache"""        
        # Get recent metrics
        hit_rate_stats = self.metric_collector.get_metric_statistics(
            'cache_hit_rate', {'cache': cache_name}, 15
        )
        memory_stats = self.metric_collector.get_metric_statistics(
            'memory_utilization', {'cache': cache_name}, 15
        )
        latency_stats = self.metric_collector.get_metric_statistics(
            'average_latency', {'cache': cache_name}, 15
        )
        error_stats = self.metric_collector.get_metric_statistics(
            'error_rate', {'cache': cache_name}, 15
        )
        
        # Calculate values
        hit_rate = hit_rate_stats.get('mean', 0.0) if hit_rate_stats else 0.0
        memory_utilization = memory_stats.get('mean', 0.0) if memory_stats else 0.0
        average_latency = latency_stats.get('mean', 0.0) if latency_stats else 0.0
        error_rate = error_stats.get('mean', 0.0) if error_stats else 0.0
        
        # Determine overall status
        status = "healthy"
        issues = []
        recommendations = []
        
        if hit_rate < 0.5:
            status = "critical"
            issues.append("Very low hit rate")
            recommendations.append("Increase cache size or adjust eviction strategy")
        elif hit_rate < 0.8:
            if status == "healthy":
                status = "warning"
            issues.append("Low hit rate")
            recommendations.append("Consider optimizing cache configuration")
        
        if memory_utilization > 0.95:
            status = "critical"
            issues.append("Very high memory usage")
            recommendations.append("Increase memory limit or implement compression")
        elif memory_utilization > 0.85:
            if status in ["healthy", "warning"]:
                status = "warning"
            issues.append("High memory usage")
        
        if error_rate > 0.1:
            status = "critical"
            issues.append("High error rate")
            recommendations.append("Investigate and fix cache errors")
        elif error_rate > 0.05:
            if status in ["healthy", "warning"]:
                status = "warning"
            issues.append("Elevated error rate")
        
        if average_latency > 200:
            if status in ["healthy", "warning"]:
                status = "warning"
            issues.append("High latency")
            recommendations.append("Optimize serialization or network configuration")
        
        # Calculate uptime (simplified - time since first metric)
        first_metric = None
        for metric_key in self.metric_collector.metrics:
            if f"cache:{cache_name}" in metric_key and self.metric_collector.metrics[metric_key]:
                first_timestamp = self.metric_collector.metrics[metric_key][0].timestamp
                if first_metric is None or first_timestamp < first_metric:
                    first_metric = first_timestamp
        
        uptime = 0.0
        if first_metric:
            uptime = (datetime.utcnow() - first_metric).total_seconds()
        
        return CacheHealthStatus(
            cache_name=cache_name,
            status=status,
            hit_rate=hit_rate,
            memory_utilization=memory_utilization,
            average_latency=average_latency,
            error_rate=error_rate,
            uptime=uptime,
            last_updated=datetime.utcnow(),
            issues=issues,
            recommendations=recommendations
        )
    
    def get_monitoring_dashboard_data(self, cache_name: str) -> Dict[str, Any]:
        """Get data for monitoring dashboard"""        
        health = self.get_cache_health(cache_name)
        active_alerts = self.alert_manager.get_active_alerts(cache_name)
        recent_alerts = self.alert_manager.get_alert_history(cache_name, hours=6)
        
        # Get metric time series for charts
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)
        
        hit_rate_series = self.metric_collector.get_metric_values(
            'cache_hit_rate', {'cache': cache_name}, start_time, end_time
        )
        latency_series = self.metric_collector.get_metric_values(
            'average_latency', {'cache': cache_name}, start_time, end_time
        )
        memory_series = self.metric_collector.get_metric_values(
            'memory_utilization', {'cache': cache_name}, start_time, end_time
        )
        
        return {
            'cache_name': cache_name,
            'health': asdict(health),
            'active_alerts': [alert.to_dict() for alert in active_alerts],
            'recent_alerts': [alert.to_dict() for alert in recent_alerts],
            'metrics': {
                'hit_rate': [(v.timestamp.isoformat(), v.value) for v in hit_rate_series],
                'latency': [(v.timestamp.isoformat(), v.value) for v in latency_series],
                'memory_utilization': [(v.timestamp.isoformat(), v.value) for v in memory_series]
            },
            'statistics': {
                'hit_rate': self.metric_collector.get_metric_statistics('cache_hit_rate', {'cache': cache_name}),
                'latency': self.metric_collector.get_metric_statistics('average_latency', {'cache': cache_name}),
                'memory': self.metric_collector.get_metric_statistics('memory_utilization', {'cache': cache_name})
            },
            'last_updated': datetime.utcnow().isoformat()
        }
    
    def export_metrics_prometheus(self) -> str:
        """Export metrics in Prometheus format"""        lines = []
        
        # Export all metrics
        for metric_key, values in self.metric_collector.metrics.items():
            if not values:
                continue
            
            metadata = self.metric_collector.metric_metadata.get(metric_key, {})
            metric_name = metadata.get('name', metric_key)
            labels = metadata.get('labels', {})
            
            # Convert to Prometheus format
            if labels:
                label_str = ','.join(f'{k}="{v}"' for k, v in labels.items())
                line = f'{metric_name}{{{label_str}}} {values[-1].value}'
            else:
                line = f'{metric_name} {values[-1].value}'
            
            lines.append(line)
        
        return '\n'.join(lines)
    
    async def cleanup(self):
        """Cleanup monitoring resources"""        # Cancel all monitoring tasks
        for task in self.monitoring_tasks.values():
            task.cancel()
        
        # Wait for tasks to complete
        if self.monitoring_tasks:
            await asyncio.gather(*self.monitoring_tasks.values(), return_exceptions=True)
        
        self.monitoring_tasks.clear()
        logger.info("Cache monitoring cleanup completed")
