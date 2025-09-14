"""Metrics Collector for IA Influencer Agent Platform
==================================================

Industrial-grade metrics collection system with Prometheus integration
for comprehensive system and application monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 Fahed Mlaiel. All rights reserved.
"""

import time
import psutil
import asyncio
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from prometheus_client import Counter, Histogram, Gauge, Summary, start_http_server
import redis
import logging
from sqlalchemy import create_engine, text
import json

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """
Individual metric data point"""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: str = "gauge"


@dataclass
class MetricThreshold:
    """Metric threshold configuration"""
    warning: float
    critical: float
    comparison: str = "greater_than"  # greater_than, less_than, equals


class MetricsCollector:
    """
    Advanced metrics collection system with multi-source aggregation
    and real-time processing capabilities.
    """
    
    def __init__(
        self,
        redis_client -> None: Optional[redis.Redis] = None,
        db_engine -> None: Optional[Any] = None,
        collection_interval -> None: int = 30,
        retention_days -> None: int = 30
    ) -> None:
        self.redis_client = redis_client
        self.db_engine = db_engine
        self.collection_interval = collection_interval
        self.retention_days = retention_days
        
        # Prometheus metrics
        self.system_metrics = {
            'cpu_usage': Gauge('system_cpu_usage_percent', 'CPU usage percentage'),
            'memory_usage': Gauge('system_memory_usage_percent', 'Memory usage percentage'),
            'disk_usage': Gauge('system_disk_usage_percent', 'Disk usage percentage', ['mount_point']),
            'network_io': Counter('system_network_io_bytes_total', 'Network I/O bytes', ['direction']),
            'disk_io': Counter('system_disk_io_bytes_total', 'Disk I/O bytes', ['direction'])
        }
        
        self.application_metrics = {
            'request_duration': Histogram('http_request_duration_seconds', 'Request duration', ['method', 'endpoint', 'status']),
            'request_count': Counter('http_requests_total', 'Total requests', ['method', 'endpoint', 'status']),
            'active_connections': Gauge('active_connections_total', 'Active connections'),
            'queue_size': Gauge('queue_size_total', 'Queue size', ['queue_name']),
            'cache_hits': Counter('cache_hits_total', 'Cache hits', ['cache_type']),
            'cache_misses': Counter('cache_misses_total', 'Cache misses', ['cache_type'])
        }
        
        self.business_metrics = {
            'fingerprint_operations': Counter('fingerprint_operations_total', 'Fingerprint operations', ['operation_type', 'content_type']),
            'protection_alerts': Counter('protection_alerts_total', 'Protection alerts', ['platform', 'status']),
            'revenue_tracked': Summary('revenue_tracked_amount', 'Revenue tracked amount', ['currency', 'platform']),
            'user_actions': Counter('user_actions_total', 'User actions', ['action_type', 'tenant_id'])
        }
        
        # Collection state
        self._collecting = False
        self._collection_thread = None
        self._custom_collectors: Dict[str, Callable] = {}
        self._thresholds: Dict[str, MetricThreshold] = {}
        
        # Internal storage
        self._metrics_buffer: List[MetricPoint] = []
        self._buffer_lock = threading.Lock()
        
    def start_collection(self, prometheus_port -> None: int = 8000) -> None:
        """
Start metrics collection with Prometheus server"""
        if self._collecting:
            logger.warning("Metrics collection already running")
            return
            
        self._collecting = True
        
        # Start Prometheus HTTP server
        try:
            start_http_server(prometheus_port)
            logger.info(f"Prometheus metrics server started on port {prometheus_port}")
        except Exception as e:
            logger.error(f"Failed to start Prometheus server: {e}")
            
        # Start collection thread
        self._collection_thread = threading.Thread(target=self._collection_loop, daemon=True)
        self._collection_thread.start()
        
        logger.info("Metrics collection started")
        
    def stop_collection(self) -> None:
        """Stop metrics collection"""
        self._collecting = False
        if self._collection_thread:
            self._collection_thread.join(timeout=5)
        logger.info("Metrics collection stopped")
        
    def _collection_loop(self) -> None:
        """Main collection loop"""
        while self._collecting:
            try:
                self._collect_system_metrics()
                self._collect_application_metrics()
                self._collect_business_metrics()
                self._run_custom_collectors()
                self._process_metrics_buffer()
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                time.sleep(5)  # Backoff on error
                
    def _collect_system_metrics(self) -> None:
        """Collect system-level metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.system_metrics['cpu_usage'].set(cpu_percent)
            self._add_metric("system.cpu.usage", cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.system_metrics['memory_usage'].set(memory_percent)
            self._add_metric("system.memory.usage", memory_percent)
            
            # Disk usage
            for partition in psutil.disk_partitions():
                try:
                    disk_usage = psutil.disk_usage(partition.mountpoint)
                    disk_percent = (disk_usage.used / disk_usage.total) * 100
                    self.system_metrics['disk_usage'].labels(mount_point=partition.mountpoint).set(disk_percent)
                    self._add_metric("system.disk.usage", disk_percent, {"mount_point": partition.mountpoint})
                except PermissionError:
                    continue
                    
            # Network I/O
            network_io = psutil.net_io_counters()
            self.system_metrics['network_io'].labels(direction='sent')._value._value = network_io.bytes_sent
            self.system_metrics['network_io'].labels(direction='recv')._value._value = network_io.bytes_recv
            self._add_metric("system.network.bytes_sent", network_io.bytes_sent)
            self._add_metric("system.network.bytes_recv", network_io.bytes_recv)
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                self.system_metrics['disk_io'].labels(direction='read')._value._value = disk_io.read_bytes
                self.system_metrics['disk_io'].labels(direction='write')._value._value = disk_io.write_bytes
                self._add_metric("system.disk.bytes_read", disk_io.read_bytes)
                self._add_metric("system.disk.bytes_write", disk_io.write_bytes)
                
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            
    def _collect_application_metrics(self) -> None:
        """Collect application-level metrics"""
        try:
            # Redis metrics
            if self.redis_client:
                info = self.redis_client.info()
                connected_clients = info.get('connected_clients', 0)
                self.application_metrics['active_connections'].set(connected_clients)
                self._add_metric("application.redis.connected_clients", connected_clients)
                
                used_memory = info.get('used_memory', 0)
                self._add_metric("application.redis.used_memory", used_memory)
                
            # Database metrics
            if self.db_engine:
                with self.db_engine.connect() as conn:
                    # Connection count
                    result = conn.execute(text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"))
                    active_connections = result.scalar()
                    self._add_metric("application.database.active_connections", active_connections)
                    
                    # Database size
                    result = conn.execute(text("SELECT pg_database_size(current_database())"))
                    db_size = result.scalar()
                    self._add_metric("application.database.size_bytes", db_size)
                    
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
            
    def _collect_business_metrics(self) -> None:
        """Collect business-specific metrics"""
        try:
            if self.db_engine:
                with self.db_engine.connect() as conn:
                    # Fingerprint operations count
                    result = conn.execute(text("""
                        SELECT content_type, COUNT(*) 
                        FROM content_fingerprints 
                        WHERE created_at > NOW() - INTERVAL '1 hour'
                        GROUP BY content_type
                    """))
                    
                    for row in result:
                        content_type, count = row
                        self._add_metric("business.fingerprints.hourly", count, {"content_type": content_type})
                        
                    # Protection alerts count
                    result = conn.execute(text("""
                        SELECT platform, status, COUNT(*) 
                        FROM protection_alerts 
                        WHERE created_at > NOW() - INTERVAL '1 hour'
                        GROUP BY platform, status
                    """))
                    
                    for row in result:
                        platform, status, count = row
                        self._add_metric("business.alerts.hourly", count, {"platform": platform, "status": status})
                        
                    # Revenue tracking
                    result = conn.execute(text("""
                        SELECT platform, currency, SUM(revenue_amount) 
                        FROM revenue_tracking 
                        WHERE created_at > NOW() - INTERVAL '1 day'
                        GROUP BY platform, currency
                    """))
                    
                    for row in result:
                        platform, currency, amount = row
                        self._add_metric("business.revenue.daily", float(amount), {"platform": platform, "currency": currency})
                        
        except Exception as e:
            logger.error(f"Error collecting business metrics: {e}")
            
    def _run_custom_collectors(self) -> None:
        """Run custom metric collectors"""
        for name, collector in self._custom_collectors.items():
            try:
                metrics = collector()
                if isinstance(metrics, list):
                    for metric in metrics:
                        if isinstance(metric, MetricPoint):
                            self._add_metric_point(metric)
                        elif isinstance(metric, tuple) and len(metric) >= 2:
                            self._add_metric(metric[0], metric[1], metric[2] if len(metric) > 2 else {})
            except Exception as e:
                logger.error(f"Error in custom collector '{name}': {e}")
                
    def _add_metric(self, name -> None: str, value -> None: float, labels -> None: Dict[str, str] = None) -> None:
        """Add a metric to the buffer"""
        metric_point = MetricPoint(
            name=name,
            value=value,
            timestamp=datetime.utcnow(),
            labels=labels or {}
        )
        self._add_metric_point(metric_point)
        
    def _add_metric_point(self, metric -> None: MetricPoint) -> None:
        """
Add a metric point to the buffer"""
        with self._buffer_lock:
            self._metrics_buffer.append(metric)
            
            # Prevent buffer overflow
            if len(self._metrics_buffer) > 10000:
                self._metrics_buffer = self._metrics_buffer[-5000:]
                
    def _process_metrics_buffer(self) -> None:
        """
Process metrics buffer"""
        if not self._metrics_buffer:
            return
            
        with self._buffer_lock:
            metrics_to_process = self._metrics_buffer.copy()
            self._metrics_buffer.clear()
            
        # Store metrics in Redis for real-time access
        if self.redis_client:
            try:
                pipeline = self.redis_client.pipeline()
                
                for metric in metrics_to_process:
                    key = f"metrics:{metric.name}"
                    value = {
                        "value": metric.value,
                        "timestamp": metric.timestamp.isoformat(),
                        "labels": metric.labels
                    }
                    
                    # Store current value
                    pipeline.set(key, json.dumps(value), ex=3600)  # 1 hour TTL
                    
                    # Store in time series
                    ts_key = f"metrics:ts:{metric.name}"
                    pipeline.zadd(ts_key, {json.dumps(value): metric.timestamp.timestamp()})
                    
                    # Cleanup old time series data
                    cutoff = (datetime.utcnow() - timedelta(days=self.retention_days)).timestamp()
                    pipeline.zremrangebyscore(ts_key, 0, cutoff)
                    
                pipeline.execute()
                
            except Exception as e:
                logger.error(f"Error storing metrics to Redis: {e}")
                
    def register_custom_collector(self, name: str, collector: Callable) -> None:
        """Register a custom metrics collector"""
        self._custom_collectors[name] = collector
        logger.info(f"Registered custom collector: {name}")
        
    def unregister_custom_collector(self, name: str) -> None:
        """Unregister a custom metrics collector"""
        if name in self._custom_collectors:
            del self._custom_collectors[name]
            logger.info(f"Unregistered custom collector: {name}")
            
    def set_threshold(self, metric_name: str, threshold: MetricThreshold) -> None:
        """Set threshold for a metric"""
        self._thresholds[metric_name] = threshold
        logger.info(f"Set threshold for metric: {metric_name}")
        
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metric values"""
        if not self.redis_client:
            return {}
            
        try:
            keys = self.redis_client.keys("metrics:*")
            metrics = {}
            
            for key in keys:
                if b":ts:" not in key:  # Skip time series keys
                    metric_name = key.decode().replace("metrics:", "")
                    value_json = self.redis_client.get(key)
                    if value_json:
                        metrics[metric_name] = json.loads(value_json)
                        
            return metrics
            
        except Exception as e:
            logger.error(f"Error retrieving current metrics: {e}")
            return {}
            
    def get_metric_history(
        self, 
        metric_name: str, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get metric history from time series"""
        if not self.redis_client:
            return []
            
        try:
            ts_key = f"metrics:ts:{metric_name}"
            
            start_score = start_time.timestamp() if start_time else 0
            end_score = end_time.timestamp() if end_time else "+inf"
            
            values = self.redis_client.zrangebyscore(ts_key, start_score, end_score, withscores=True)
            
            history = []
            for value_json, timestamp in values:
                metric_data = json.loads(value_json)
                metric_data['timestamp'] = datetime.fromtimestamp(timestamp)
                history.append(metric_data)
                
            return history
            
        except Exception as e:
            logger.error(f"Error retrieving metric history for {metric_name}: {e}")
            return []
            
    def check_thresholds(self) -> List[Dict[str, Any]]:
        """Check metric thresholds and return violations"""
        violations = []
        current_metrics = self.get_current_metrics()
        
        for metric_name, threshold in self._thresholds.items():
            if metric_name in current_metrics:
                value = current_metrics[metric_name]['value']
                
                violation_level = None
                if threshold.comparison == "greater_than":
                    if value > threshold.critical:
                        violation_level = "critical"
                    elif value > threshold.warning:
                        violation_level = "warning"
                elif threshold.comparison == "less_than":
                    if value < threshold.critical:
                        violation_level = "critical"
                    elif value < threshold.warning:
                        violation_level = "warning"
                        
                if violation_level:
                    violations.append({
                        "metric_name": metric_name,
                        "current_value": value,
                        "threshold": threshold,
                        "level": violation_level,
                        "timestamp": datetime.utcnow()
                    })
                    
        return violations
        
    async def export_metrics(self, format_type: str = "prometheus") -> str:
        """Export metrics in specified format"""
        if format_type == "prometheus":
            # Prometheus format handled by prometheus_client
            return "Prometheus metrics available at /metrics endpoint"
        elif format_type == "json":
            metrics = self.get_current_metrics()
            return json.dumps(metrics, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
            
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics of metrics collection"""
        try:
            current_metrics = self.get_current_metrics()
            violations = self.check_thresholds()
            
            return {
                "total_metrics": len(current_metrics),
                "collection_interval": self.collection_interval,
                "retention_days": self.retention_days,
                "custom_collectors": len(self._custom_collectors),
                "thresholds_configured": len(self._thresholds),
                "current_violations": len(violations),
                "collection_status": "active" if self._collecting else "stopped",
                "last_collection": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating summary stats: {e}")
            return {"error": str(e)}
