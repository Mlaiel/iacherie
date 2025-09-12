#!/usr/bin/env python3
"""
Performance Metrics Collector - Ainflue DevOps Platform
=====================================================

Enterprise performance monitoring and metrics collection system.
Demonstrates DevOps + Backend Senior + DBA expertise.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import psutil
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import yaml
import numpy as np
import pandas as pd
import sqlite3
import redis
import aiohttp
import aiofiles
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram, generate_latest
import matplotlib.pyplot as plt
import seaborn as sns
from collections import deque, defaultdict
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of performance metrics"""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    DATABASE_PERFORMANCE = "database_performance"
    CACHE_PERFORMANCE = "cache_performance"
    CUSTOM = "custom"


class MetricSeverity(Enum):
    """Metric alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class MetricSource(Enum):
    """Sources of performance metrics"""
    SYSTEM = "system"
    APPLICATION = "application"
    DATABASE = "database"
    CACHE = "cache"
    EXTERNAL_API = "external_api"
    LOAD_BALANCER = "load_balancer"
    CDN = "cdn"


@dataclass
class MetricPoint:
    """Individual metric data point"""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricSeries:
    """Time series of metric points"""
    name: str
    metric_type: MetricType
    source: MetricSource
    unit: str
    description: str
    points: List[MetricPoint] = field(default_factory=list)
    aggregation_window: int = 60  # seconds
    retention_period: int = 86400  # 24 hours in seconds


@dataclass
class PerformanceBaseline:
    """Performance baseline for comparison"""
    metric_name: str
    baseline_value: float
    tolerance_percent: float
    warning_threshold: float
    critical_threshold: float
    calculation_method: str = "percentile_95"
    baseline_period: int = 7  # days
    last_calculated: Optional[datetime] = None


@dataclass
class AlertRule:
    """Performance alert rule"""
    rule_id: str
    metric_name: str
    condition: str  # ">", "<", ">=", "<=", "=="
    threshold: float
    severity: MetricSeverity
    duration: int  # seconds - how long condition must be true
    cooldown: int = 300  # seconds between alerts
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    notification_channels: List[str] = field(default_factory=list)


@dataclass
class PerformanceReport:
    """Performance analysis report"""
    report_id: str
    period_start: datetime
    period_end: datetime
    metrics_analyzed: List[str]
    baseline_comparisons: Dict[str, Dict] = field(default_factory=dict)
    anomalies_detected: List[Dict] = field(default_factory=list)
    performance_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    trends: Dict[str, str] = field(default_factory=dict)
    sla_compliance: Dict[str, float] = field(default_factory=dict)


class PerformanceMetricsCollector:
    """
    Enterprise performance metrics collection and analysis system
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path("config/performance_metrics.yaml")
        self.config = self._load_config()
        self.database_path = Path("data/performance_metrics.db")
        self.metrics_storage: Dict[str, MetricSeries] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.baselines: Dict[str, PerformanceBaseline] = {}
        self.prometheus_registry = CollectorRegistry()
        self.prometheus_metrics: Dict[str, Any] = {}
        self.collection_active = False
        self.redis_client = None
        self._initialize_database()
        self._initialize_prometheus_metrics()
        self._load_alert_rules()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        default_config = {
            "collection": {
                "interval_seconds": 15,
                "batch_size": 100,
                "buffer_size": 1000,
                "auto_start": True
            },
            "metrics": {
                "system_metrics": True,
                "application_metrics": True,
                "database_metrics": True,
                "cache_metrics": True,
                "custom_metrics": True
            },
            "storage": {
                "retention_days": 30,
                "compression": True,
                "batch_write": True
            },
            "alerting": {
                "enabled": True,
                "check_interval": 30,
                "notification_channels": ["email", "slack", "webhook"]
            },
            "analysis": {
                "baseline_calculation": True,
                "anomaly_detection": True,
                "trend_analysis": True,
                "sla_monitoring": True
            },
            "external_integrations": {
                "prometheus": {
                    "enabled": True,
                    "port": 8001
                },
                "redis": {
                    "enabled": True,
                    "host": "localhost",
                    "port": 6379,
                    "db": 1
                }
            },
            "performance_targets": {
                "response_time_ms": 200,
                "error_rate_percent": 1.0,
                "cpu_usage_percent": 70,
                "memory_usage_percent": 80,
                "disk_usage_percent": 85
            }
        }
        
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config

    def _initialize_database(self):
        """Initialize SQLite database for metrics storage"""
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.database_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    metric_type TEXT,
                    source TEXT,
                    value REAL,
                    unit TEXT,
                    timestamp TEXT,
                    labels TEXT,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS baselines (
                    metric_name TEXT PRIMARY KEY,
                    baseline_value REAL,
                    tolerance_percent REAL,
                    warning_threshold REAL,
                    critical_threshold REAL,
                    calculation_method TEXT,
                    last_calculated TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_id TEXT,
                    metric_name TEXT,
                    severity TEXT,
                    message TEXT,
                    timestamp TEXT,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_timestamp TEXT
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_name_timestamp ON metrics(name, timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)")

    def _initialize_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        if not self.config["external_integrations"]["prometheus"]["enabled"]:
            return
        
        try:
            # System metrics
            self.prometheus_metrics.update({
                "cpu_usage": Gauge('cpu_usage_percent', 'CPU usage percentage', registry=self.prometheus_registry),
                "memory_usage": Gauge('memory_usage_percent', 'Memory usage percentage', registry=self.prometheus_registry),
                "disk_usage": Gauge('disk_usage_percent', 'Disk usage percentage', registry=self.prometheus_registry),
                "response_time": Histogram('response_time_seconds', 'Response time in seconds', 
                                         buckets=[0.1, 0.2, 0.5, 1.0, 2.0, 5.0], registry=self.prometheus_registry),
                "requests_total": Counter('requests_total', 'Total requests', ['method', 'endpoint'], 
                                        registry=self.prometheus_registry),
                "errors_total": Counter('errors_total', 'Total errors', ['type'], registry=self.prometheus_registry)
            })
            
            logger.info("Prometheus metrics initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Prometheus metrics: {e}")

    def _load_alert_rules(self):
        """Load alert rules from configuration"""
        # Default alert rules
        default_rules = [
            AlertRule(
                rule_id="high_cpu_usage",
                metric_name="cpu_usage",
                condition=">",
                threshold=self.config["performance_targets"]["cpu_usage_percent"],
                severity=MetricSeverity.HIGH,
                duration=300,  # 5 minutes
                notification_channels=["email"]
            ),
            AlertRule(
                rule_id="high_memory_usage",
                metric_name="memory_usage",
                condition=">",
                threshold=self.config["performance_targets"]["memory_usage_percent"],
                severity=MetricSeverity.HIGH,
                duration=300,
                notification_channels=["email"]
            ),
            AlertRule(
                rule_id="high_response_time",
                metric_name="response_time",
                condition=">",
                threshold=self.config["performance_targets"]["response_time_ms"] / 1000,
                severity=MetricSeverity.MEDIUM,
                duration=180,  # 3 minutes
                notification_channels=["slack"]
            ),
            AlertRule(
                rule_id="high_error_rate",
                metric_name="error_rate",
                condition=">",
                threshold=self.config["performance_targets"]["error_rate_percent"],
                severity=MetricSeverity.CRITICAL,
                duration=60,  # 1 minute
                notification_channels=["email", "slack"]
            )
        ]
        
        for rule in default_rules:
            self.alert_rules[rule.rule_id] = rule

    async def start_collection(self):
        """Start metrics collection"""
        if self.collection_active:
            logger.warning("Metrics collection already active")
            return
        
        self.collection_active = True
        logger.info("Starting performance metrics collection")
        
        # Initialize Redis connection if enabled
        if self.config["external_integrations"]["redis"]["enabled"]:
            try:
                redis_config = self.config["external_integrations"]["redis"]
                self.redis_client = redis.Redis(
                    host=redis_config["host"],
                    port=redis_config["port"],
                    db=redis_config["db"],
                    decode_responses=True
                )
                logger.info("Redis connection established")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")
        
        # Start collection tasks
        tasks = []
        
        if self.config["metrics"]["system_metrics"]:
            tasks.append(asyncio.create_task(self._collect_system_metrics()))
        
        if self.config["metrics"]["application_metrics"]:
            tasks.append(asyncio.create_task(self._collect_application_metrics()))
        
        if self.config["metrics"]["database_metrics"]:
            tasks.append(asyncio.create_task(self._collect_database_metrics()))
        
        if self.config["alerting"]["enabled"]:
            tasks.append(asyncio.create_task(self._monitor_alerts()))
        
        # Start background tasks
        await asyncio.gather(*tasks, return_exceptions=True)

    async def stop_collection(self):
        """Stop metrics collection"""
        self.collection_active = False
        logger.info("Stopping performance metrics collection")

    async def _collect_system_metrics(self):
        """Collect system performance metrics"""
        interval = self.config["collection"]["interval_seconds"]
        
        while self.collection_active:
            try:
                timestamp = datetime.now()
                
                # CPU metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                await self._store_metric(
                    "cpu_usage", cpu_percent, MetricType.CPU_USAGE, 
                    MetricSource.SYSTEM, "percent", timestamp
                )
                
                # Memory metrics
                memory = psutil.virtual_memory()
                await self._store_metric(
                    "memory_usage", memory.percent, MetricType.MEMORY_USAGE,
                    MetricSource.SYSTEM, "percent", timestamp
                )
                
                # Disk metrics
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                await self._store_metric(
                    "disk_usage", disk_percent, MetricType.DISK_IO,
                    MetricSource.SYSTEM, "percent", timestamp
                )
                
                # Network metrics
                network = psutil.net_io_counters()
                await self._store_metric(
                    "network_bytes_sent", network.bytes_sent, MetricType.NETWORK_IO,
                    MetricSource.SYSTEM, "bytes", timestamp
                )
                await self._store_metric(
                    "network_bytes_recv", network.bytes_recv, MetricType.NETWORK_IO,
                    MetricSource.SYSTEM, "bytes", timestamp
                )
                
                # Update Prometheus metrics
                if "cpu_usage" in self.prometheus_metrics:
                    self.prometheus_metrics["cpu_usage"].set(cpu_percent)
                if "memory_usage" in self.prometheus_metrics:
                    self.prometheus_metrics["memory_usage"].set(memory.percent)
                if "disk_usage" in self.prometheus_metrics:
                    self.prometheus_metrics["disk_usage"].set(disk_percent)
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"System metrics collection failed: {e}")
                await asyncio.sleep(interval)

    async def _collect_application_metrics(self):
        """Collect application performance metrics"""
        interval = self.config["collection"]["interval_seconds"]
        
        while self.collection_active:
            try:
                timestamp = datetime.now()
                
                # Placeholder for application-specific metrics
                # In a real implementation, this would collect from application endpoints
                
                # Simulate response time collection
                response_times = await self._collect_response_times()
                if response_times:
                    avg_response_time = statistics.mean(response_times)
                    await self._store_metric(
                        "response_time", avg_response_time, MetricType.RESPONSE_TIME,
                        MetricSource.APPLICATION, "seconds", timestamp
                    )
                
                # Simulate throughput collection
                throughput = await self._collect_throughput()
                if throughput:
                    await self._store_metric(
                        "throughput", throughput, MetricType.THROUGHPUT,
                        MetricSource.APPLICATION, "requests_per_second", timestamp
                    )
                
                # Simulate error rate collection
                error_rate = await self._collect_error_rate()
                if error_rate is not None:
                    await self._store_metric(
                        "error_rate", error_rate, MetricType.ERROR_RATE,
                        MetricSource.APPLICATION, "percent", timestamp
                    )
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Application metrics collection failed: {e}")
                await asyncio.sleep(interval)

    async def _collect_database_metrics(self):
        """Collect database performance metrics"""
        interval = self.config["collection"]["interval_seconds"] * 2  # Less frequent
        
        while self.collection_active:
            try:
                timestamp = datetime.now()
                
                # Simulate database metrics collection
                # In a real implementation, this would connect to actual databases
                
                # Connection pool metrics
                active_connections = await self._get_db_active_connections()
                if active_connections is not None:
                    await self._store_metric(
                        "db_active_connections", active_connections, MetricType.DATABASE_PERFORMANCE,
                        MetricSource.DATABASE, "count", timestamp
                    )
                
                # Query performance
                avg_query_time = await self._get_avg_query_time()
                if avg_query_time is not None:
                    await self._store_metric(
                        "db_avg_query_time", avg_query_time, MetricType.DATABASE_PERFORMANCE,
                        MetricSource.DATABASE, "milliseconds", timestamp
                    )
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Database metrics collection failed: {e}")
                await asyncio.sleep(interval)

    async def _store_metric(self, name: str, value: float, metric_type: MetricType, 
                          source: MetricSource, unit: str, timestamp: datetime,
                          labels: Optional[Dict[str, str]] = None,
                          metadata: Optional[Dict[str, Any]] = None):
        """Store metric in database and memory"""
        try:
            # Create metric point
            point = MetricPoint(
                timestamp=timestamp,
                value=value,
                labels=labels or {},
                metadata=metadata or {}
            )
            
            # Store in memory
            if name not in self.metrics_storage:
                self.metrics_storage[name] = MetricSeries(
                    name=name,
                    metric_type=metric_type,
                    source=source,
                    unit=unit,
                    description=f"{name} metric"
                )
            
            self.metrics_storage[name].points.append(point)
            
            # Limit memory storage size
            max_points = self.config["collection"]["buffer_size"]
            if len(self.metrics_storage[name].points) > max_points:
                self.metrics_storage[name].points = self.metrics_storage[name].points[-max_points:]
            
            # Store in database (batch write for performance)
            if self.config["storage"]["batch_write"]:
                await self._batch_store_metric(name, point, metric_type, source, unit)
            else:
                await self._immediate_store_metric(name, point, metric_type, source, unit)
            
            # Store in Redis for fast access
            if self.redis_client:
                await self._store_metric_in_redis(name, point)
            
        except Exception as e:
            logger.error(f"Failed to store metric {name}: {e}")

    async def _immediate_store_metric(self, name: str, point: MetricPoint, 
                                    metric_type: MetricType, source: MetricSource, unit: str):
        """Store metric immediately in database"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                conn.execute("""
                    INSERT INTO metrics (name, metric_type, source, value, unit, timestamp, labels, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    name,
                    metric_type.value,
                    source.value,
                    point.value,
                    unit,
                    point.timestamp.isoformat(),
                    json.dumps(point.labels),
                    json.dumps(point.metadata)
                ))
        except Exception as e:
            logger.error(f"Failed to store metric in database: {e}")

    async def _batch_store_metric(self, name: str, point: MetricPoint, 
                                metric_type: MetricType, source: MetricSource, unit: str):
        """Store metric in batch (placeholder for optimization)"""
        # In a real implementation, this would accumulate metrics and write in batches
        await self._immediate_store_metric(name, point, metric_type, source, unit)

    async def _store_metric_in_redis(self, name: str, point: MetricPoint):
        """Store metric in Redis for fast access"""
        try:
            if self.redis_client:
                key = f"metric:{name}:latest"
                value = {
                    "value": point.value,
                    "timestamp": point.timestamp.isoformat(),
                    "labels": point.labels
                }
                self.redis_client.set(key, json.dumps(value), ex=3600)  # 1 hour TTL
        except Exception as e:
            logger.error(f"Failed to store metric in Redis: {e}")

    async def _monitor_alerts(self):
        """Monitor metrics for alert conditions"""
        check_interval = self.config["alerting"]["check_interval"]
        
        while self.collection_active:
            try:
                for rule in self.alert_rules.values():
                    if not rule.enabled:
                        continue
                    
                    await self._check_alert_rule(rule)
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Alert monitoring failed: {e}")
                await asyncio.sleep(check_interval)

    async def _check_alert_rule(self, rule: AlertRule):
        """Check if alert rule condition is met"""
        try:
            # Get recent metric values
            recent_values = await self._get_recent_metric_values(rule.metric_name, rule.duration)
            
            if not recent_values:
                return
            
            # Check if condition is met for the duration
            condition_met = True
            for value in recent_values:
                if not self._evaluate_condition(value, rule.condition, rule.threshold):
                    condition_met = False
                    break
            
            if condition_met:
                # Check cooldown period
                if rule.last_triggered:
                    time_since_last = (datetime.now() - rule.last_triggered).total_seconds()
                    if time_since_last < rule.cooldown:
                        return
                
                # Trigger alert
                await self._trigger_alert(rule, recent_values[-1])
                rule.last_triggered = datetime.now()
            
        except Exception as e:
            logger.error(f"Alert rule check failed for {rule.rule_id}: {e}")

    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Evaluate alert condition"""
        if condition == ">":
            return value > threshold
        elif condition == "<":
            return value < threshold
        elif condition == ">=":
            return value >= threshold
        elif condition == "<=":
            return value <= threshold
        elif condition == "==":
            return abs(value - threshold) < 0.001  # Float comparison tolerance
        else:
            return False

    async def _trigger_alert(self, rule: AlertRule, current_value: float):
        """Trigger alert notification"""
        try:
            alert_message = f"Alert: {rule.metric_name} {rule.condition} {rule.threshold} (current: {current_value:.2f})"
            
            # Store alert in database
            with sqlite3.connect(self.database_path) as conn:
                conn.execute("""
                    INSERT INTO alerts (rule_id, metric_name, severity, message, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    rule.rule_id,
                    rule.metric_name,
                    rule.severity.value,
                    alert_message,
                    datetime.now().isoformat()
                ))
            
            # Send notifications (placeholder)
            for channel in rule.notification_channels:
                await self._send_notification(channel, alert_message, rule.severity)
            
            logger.warning(f"Alert triggered: {alert_message}")
            
        except Exception as e:
            logger.error(f"Failed to trigger alert: {e}")

    async def _send_notification(self, channel: str, message: str, severity: MetricSeverity):
        """Send alert notification to channel"""
        # Placeholder for notification implementation
        logger.info(f"Notification [{channel}] {severity.value}: {message}")

    async def _get_recent_metric_values(self, metric_name: str, duration_seconds: int) -> List[float]:
        """Get recent metric values for alert checking"""
        try:
            if metric_name in self.metrics_storage:
                cutoff_time = datetime.now() - timedelta(seconds=duration_seconds)
                recent_points = [
                    point for point in self.metrics_storage[metric_name].points
                    if point.timestamp >= cutoff_time
                ]
                return [point.value for point in recent_points]
            return []
        except Exception as e:
            logger.error(f"Failed to get recent values for {metric_name}: {e}")
            return []

    async def _collect_response_times(self) -> List[float]:
        """Collect application response times"""
        # Placeholder - would integrate with actual application monitoring
        return [0.1, 0.15, 0.12, 0.18, 0.14]  # Sample response times

    async def _collect_throughput(self) -> Optional[float]:
        """Collect application throughput"""
        # Placeholder - would integrate with actual application monitoring
        return 150.0  # requests per second

    async def _collect_error_rate(self) -> Optional[float]:
        """Collect application error rate"""
        # Placeholder - would integrate with actual application monitoring
        return 0.5  # 0.5% error rate

    async def _get_db_active_connections(self) -> Optional[int]:
        """Get database active connections"""
        # Placeholder - would query actual database
        return 25

    async def _get_avg_query_time(self) -> Optional[float]:
        """Get average database query time"""
        # Placeholder - would query actual database
        return 45.5  # milliseconds

    async def get_metrics(self, metric_name: str, start_time: Optional[datetime] = None, 
                         end_time: Optional[datetime] = None) -> Optional[MetricSeries]:
        """Get metrics data for a specific metric"""
        try:
            if metric_name in self.metrics_storage:
                series = self.metrics_storage[metric_name]
                
                if start_time or end_time:
                    # Filter by time range
                    filtered_points = []
                    for point in series.points:
                        if start_time and point.timestamp < start_time:
                            continue
                        if end_time and point.timestamp > end_time:
                            continue
                        filtered_points.append(point)
                    
                    # Create filtered series
                    filtered_series = MetricSeries(
                        name=series.name,
                        metric_type=series.metric_type,
                        source=series.source,
                        unit=series.unit,
                        description=series.description,
                        points=filtered_points
                    )
                    return filtered_series
                
                return series
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get metrics for {metric_name}: {e}")
            return None

    async def generate_performance_report(self, period_hours: int = 24) -> PerformanceReport:
        """Generate comprehensive performance report"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=period_hours)
            
            report = PerformanceReport(
                report_id=f"perf_report_{int(end_time.timestamp())}",
                period_start=start_time,
                period_end=end_time,
                metrics_analyzed=list(self.metrics_storage.keys())
            )
            
            # Analyze each metric
            for metric_name in self.metrics_storage.keys():
                series = await self.get_metrics(metric_name, start_time, end_time)
                if series and series.points:
                    # Calculate statistics
                    values = [point.value for point in series.points]
                    avg_value = statistics.mean(values)
                    max_value = max(values)
                    min_value = min(values)
                    
                    # Check against baselines
                    baseline = self.baselines.get(metric_name)
                    if baseline:
                        deviation = abs(avg_value - baseline.baseline_value) / baseline.baseline_value * 100
                        report.baseline_comparisons[metric_name] = {
                            "current_avg": avg_value,
                            "baseline": baseline.baseline_value,
                            "deviation_percent": deviation,
                            "within_tolerance": deviation <= baseline.tolerance_percent
                        }
                    
                    # Detect anomalies (simple threshold-based)
                    if len(values) > 10:
                        mean = statistics.mean(values)
                        stdev = statistics.stdev(values)
                        threshold = mean + 2 * stdev
                        
                        anomalies = [
                            {"timestamp": point.timestamp.isoformat(), "value": point.value}
                            for point in series.points
                            if point.value > threshold
                        ]
                        
                        if anomalies:
                            report.anomalies_detected.extend(anomalies)
                    
                    # Trend analysis
                    if len(values) >= 2:
                        if values[-1] > values[0]:
                            report.trends[metric_name] = "increasing"
                        elif values[-1] < values[0]:
                            report.trends[metric_name] = "decreasing"
                        else:
                            report.trends[metric_name] = "stable"
            
            # Calculate overall performance score
            report.performance_score = await self._calculate_performance_score(report)
            
            # Generate recommendations
            report.recommendations = await self._generate_performance_recommendations(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            raise

    async def _calculate_performance_score(self, report: PerformanceReport) -> float:
        """Calculate overall performance score"""
        try:
            score = 100.0
            
            # Deduct points for baseline deviations
            for metric_name, comparison in report.baseline_comparisons.items():
                if not comparison["within_tolerance"]:
                    score -= min(20, comparison["deviation_percent"] / 5)
            
            # Deduct points for anomalies
            anomaly_penalty = min(30, len(report.anomalies_detected) * 2)
            score -= anomaly_penalty
            
            # Deduct points for negative trends in critical metrics
            critical_metrics = ["response_time", "error_rate", "cpu_usage", "memory_usage"]
            for metric in critical_metrics:
                if metric in report.trends:
                    if (metric in ["response_time", "error_rate", "cpu_usage", "memory_usage"] and 
                        report.trends[metric] == "increasing"):
                        score -= 10
            
            return max(0, score)
            
        except Exception as e:
            logger.error(f"Performance score calculation failed: {e}")
            return 0.0

    async def _generate_performance_recommendations(self, report: PerformanceReport) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        # Baseline deviation recommendations
        for metric_name, comparison in report.baseline_comparisons.items():
            if not comparison["within_tolerance"]:
                if metric_name == "response_time":
                    recommendations.append("Consider optimizing application code or scaling infrastructure to improve response times")
                elif metric_name == "cpu_usage":
                    recommendations.append("High CPU usage detected - consider horizontal scaling or code optimization")
                elif metric_name == "memory_usage":
                    recommendations.append("Memory usage is high - check for memory leaks or increase available memory")
                elif metric_name == "error_rate":
                    recommendations.append("Error rate is elevated - review application logs and fix underlying issues")
        
        # Anomaly recommendations
        if len(report.anomalies_detected) > 5:
            recommendations.append("Multiple anomalies detected - implement more robust monitoring and alerting")
        
        # Trend recommendations
        for metric, trend in report.trends.items():
            if metric == "response_time" and trend == "increasing":
                recommendations.append("Response times are trending upward - investigate performance bottlenecks")
            elif metric == "error_rate" and trend == "increasing":
                recommendations.append("Error rate is increasing - urgent investigation required")
        
        if not recommendations:
            recommendations.append("Performance metrics are within acceptable ranges - continue monitoring")
        
        return recommendations

    def get_prometheus_metrics(self) -> str:
        """Get Prometheus-formatted metrics"""
        try:
            return generate_latest(self.prometheus_registry).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to generate Prometheus metrics: {e}")
            return ""


# Global instance
performance_metrics_collector = PerformanceMetricsCollector()

# Convenience functions
async def start_performance_monitoring():
    """Start performance monitoring"""
    await performance_metrics_collector.start_collection()

async def stop_performance_monitoring():
    """Stop performance monitoring"""
    await performance_metrics_collector.stop_collection()

async def get_performance_report(hours: int = 24):
    """Get performance report"""
    return await performance_metrics_collector.generate_performance_report(hours)

async def record_custom_metric(name: str, value: float, unit: str = "count", 
                              labels: Optional[Dict[str, str]] = None):
    """Record custom application metric"""
    await performance_metrics_collector._store_metric(
        name, value, MetricType.CUSTOM, MetricSource.APPLICATION, 
        unit, datetime.now(), labels
    )

if __name__ == "__main__":
    # Example usage
    async def main():
        # Start monitoring
        await start_performance_monitoring()
        
        # Let it run for a bit
        await asyncio.sleep(30)
        
        # Generate report
        report = await get_performance_report(1)  # Last hour
        print(f"Performance Score: {report.performance_score:.1f}")
        print(f"Anomalies: {len(report.anomalies_detected)}")
        
        # Stop monitoring
        await stop_performance_monitoring()
    
    asyncio.run(main())