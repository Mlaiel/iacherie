"""
Metrics Collector - Advanced Analytics & KPI Engine
===================================================

Professional metrics collection and KPI calculation system for IA-Influencer-Agent platform.
Implements comprehensive analytics, performance tracking, and business intelligence metrics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise  
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import statistics
import numpy as np
from abc import ABC, abstractmethod
import psutil
import time
from collections import defaultdict, deque
import threading
from pathlib import Path
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from sqlalchemy import create_engine, text
import redis
import aioredis
from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry

from .monitor_engine import MonitorEngine, MonitoringConfiguration, MonitoringMetrics

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Metric type enumeration."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    RATE = "rate"
    PERCENTAGE = "percentage"
    RATIO = "ratio"

class MetricCategory(Enum):
    """Metric category enumeration."""
    SYSTEM = "system"
    BUSINESS = "business"
    USER = "user"
    CONTENT = "content"
    SECURITY = "security"
    PERFORMANCE = "performance"
    FINANCIAL = "financial"
    ML = "ml"

class AggregationType(Enum):
    """Aggregation type for metrics."""
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    MEDIAN = "median"
    PERCENTILE_95 = "p95"
    PERCENTILE_99 = "p99"
    STANDARD_DEVIATION = "stddev"

@dataclass
class MetricDefinition:
    """Metric definition structure."""
    name: str
    metric_type: MetricType
    category: MetricCategory
    description: str = ""
    unit: str = ""
    labels: List[str] = field(default_factory=list)
    aggregation_types: List[AggregationType] = field(default_factory=lambda: [AggregationType.AVERAGE])
    retention_period: int = 86400  # seconds
    collection_interval: int = 60  # seconds
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    enabled: bool = True

@dataclass
class MetricDataPoint:
    """Individual metric data point."""
    metric_name: str
    value: Union[int, float]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class KPIDefinition:
    """Key Performance Indicator definition."""
    name: str
    description: str
    formula: str  # Mathematical formula using metric names
    target_value: Optional[float] = None
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    unit: str = ""
    category: MetricCategory = MetricCategory.BUSINESS
    calculation_interval: int = 300  # seconds
    dependencies: List[str] = field(default_factory=list)  # Metric names required

@dataclass
class KPIResult:
    """KPI calculation result."""
    kpi_name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: str = "normal"  # normal, warning, critical
    trend: str = "stable"  # increasing, decreasing, stable
    previous_value: Optional[float] = None
    change_percentage: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class MetricsCollector(MonitorEngine):
    """
    Advanced metrics collection and analytics engine.
    Implements comprehensive metric collection, aggregation, and KPI calculation.
    """
    
    def __init__(self, config: MonitoringConfiguration):
        super().__init__(config)
        self.metrics_definitions: Dict[str, MetricDefinition] = {}
        self.kpi_definitions: Dict[str, KPIDefinition] = {}
        self.metrics_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.kpi_results: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.collectors: Dict[str, Callable] = {}
        self.prometheus_registry = CollectorRegistry()
        self.prometheus_metrics: Dict[str, Any] = {}
        self.redis_client: Optional[redis.Redis] = None
        self.collection_tasks: Dict[str, asyncio.Task] = {}
        
        # System metrics collectors
        self._initialize_system_collectors()
        
        # Business metrics definitions
        self._initialize_business_metrics()
        
        # KPI definitions
        self._initialize_kpi_definitions()
    
    def _initialize_system_collectors(self):
        """Initialize system-level metric collectors."""
        system_metrics = [
            MetricDefinition(
                name="cpu_usage_percent",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.SYSTEM,
                description="CPU usage percentage",
                unit="percent",
                alert_thresholds={"warning": 70.0, "critical": 90.0}
            ),
            MetricDefinition(
                name="memory_usage_percent",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.SYSTEM,
                description="Memory usage percentage",
                unit="percent",
                alert_thresholds={"warning": 80.0, "critical": 95.0}
            ),
            MetricDefinition(
                name="disk_usage_percent",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.SYSTEM,
                description="Disk usage percentage",
                unit="percent",
                labels=["mount_point"],
                alert_thresholds={"warning": 85.0, "critical": 95.0}
            ),
            MetricDefinition(
                name="network_bytes_sent",
                metric_type=MetricType.COUNTER,
                category=MetricCategory.SYSTEM,
                description="Network bytes sent",
                unit="bytes",
                labels=["interface"]
            ),
            MetricDefinition(
                name="network_bytes_received",
                metric_type=MetricType.COUNTER,
                category=MetricCategory.SYSTEM,
                description="Network bytes received",
                unit="bytes",
                labels=["interface"]
            ),
            MetricDefinition(
                name="process_count",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.SYSTEM,
                description="Number of running processes",
                unit="count"
            )
        ]
        
        for metric_def in system_metrics:
            self.metrics_definitions[metric_def.name] = metric_def
        
        # Register system collectors
        self.collectors["system"] = self._collect_system_metrics
    
    def _initialize_business_metrics(self):
        """Initialize business-specific metric definitions."""
        business_metrics = [
            MetricDefinition(
                name="content_uploads_total",
                metric_type=MetricType.COUNTER,
                category=MetricCategory.CONTENT,
                description="Total number of content uploads",
                unit="count",
                labels=["content_type", "user_tier"]
            ),
            MetricDefinition(
                name="content_processing_duration",
                metric_type=MetricType.HISTOGRAM,
                category=MetricCategory.PERFORMANCE,
                description="Content processing duration",
                unit="seconds",
                labels=["content_type", "processing_stage"]
            ),
            MetricDefinition(
                name="fingerprint_generation_time",
                metric_type=MetricType.HISTOGRAM,
                category=MetricCategory.PERFORMANCE,
                description="Time to generate content fingerprint",
                unit="seconds",
                labels=["content_type"]
            ),
            MetricDefinition(
                name="infringement_detections_total",
                metric_type=MetricType.COUNTER,
                category=MetricCategory.SECURITY,
                description="Total infringement detections",
                unit="count",
                labels=["severity", "platform", "content_type"]
            ),
            MetricDefinition(
                name="user_registrations_total",
                metric_type=MetricType.COUNTER,
                category=MetricCategory.USER,
                description="Total user registrations",
                unit="count",
                labels=["tier", "source"]
            ),
            MetricDefinition(
                name="active_users_daily",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.USER,
                description="Daily active users",
                unit="count",
                labels=["user_tier"]
            ),
            MetricDefinition(
                name="revenue_total",
                metric_type=MetricType.COUNTER,
                category=MetricCategory.FINANCIAL,
                description="Total revenue generated",
                unit="currency",
                labels=["currency", "revenue_type", "user_tier"]
            ),
            MetricDefinition(
                name="api_requests_total",
                metric_type=MetricType.COUNTER,
                category=MetricCategory.PERFORMANCE,
                description="Total API requests",
                unit="count",
                labels=["endpoint", "method", "status_code"]
            ),
            MetricDefinition(
                name="api_request_duration",
                metric_type=MetricType.HISTOGRAM,
                category=MetricCategory.PERFORMANCE,
                description="API request duration",
                unit="seconds",
                labels=["endpoint", "method"]
            ),
            MetricDefinition(
                name="ml_model_predictions_total",
                metric_type=MetricType.COUNTER,
                category=MetricCategory.ML,
                description="Total ML model predictions",
                unit="count",
                labels=["model_name", "model_version"]
            ),
            MetricDefinition(
                name="ml_model_accuracy",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.ML,
                description="ML model accuracy score",
                unit="ratio",
                labels=["model_name", "dataset"]
            ),
            MetricDefinition(
                name="storage_usage_bytes",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.SYSTEM,
                description="Storage usage in bytes",
                unit="bytes",
                labels=["storage_type", "user_tier"]
            ),
            MetricDefinition(
                name="protection_effectiveness_rate",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.SECURITY,
                description="Content protection effectiveness rate",
                unit="ratio",
                labels=["content_type", "protection_level"]
            )
        ]
        
        for metric_def in business_metrics:
            self.metrics_definitions[metric_def.name] = metric_def
    
    def _initialize_kpi_definitions(self):
        """Initialize KPI definitions."""
        kpis = [
            KPIDefinition(
                name="user_growth_rate",
                description="Monthly user growth rate",
                formula="(current_month_users - previous_month_users) / previous_month_users * 100",
                target_value=15.0,
                threshold_warning=10.0,
                threshold_critical=5.0,
                unit="percent",
                category=MetricCategory.USER,
                calculation_interval=3600,
                dependencies=["user_registrations_total"]
            ),
            KPIDefinition(
                name="content_processing_efficiency",
                description="Average content processing time efficiency",
                formula="1 / avg(content_processing_duration) * 100",
                target_value=80.0,
                threshold_warning=60.0,
                threshold_critical=40.0,
                unit="percent",
                category=MetricCategory.PERFORMANCE,
                dependencies=["content_processing_duration"]
            ),
            KPIDefinition(
                name="infringement_detection_rate",
                description="Rate of successful infringement detections",
                formula="infringement_detections_total / content_uploads_total * 100",
                target_value=95.0,
                threshold_warning=85.0,
                threshold_critical=70.0,
                unit="percent",
                category=MetricCategory.SECURITY,
                dependencies=["infringement_detections_total", "content_uploads_total"]
            ),
            KPIDefinition(
                name="revenue_per_user",
                description="Average revenue per user",
                formula="revenue_total / active_users_daily",
                target_value=50.0,
                threshold_warning=30.0,
                threshold_critical=20.0,
                unit="currency",
                category=MetricCategory.FINANCIAL,
                dependencies=["revenue_total", "active_users_daily"]
            ),
            KPIDefinition(
                name="system_availability",
                description="System availability percentage",
                formula="(total_time - downtime) / total_time * 100",
                target_value=99.9,
                threshold_warning=99.5,
                threshold_critical=99.0,
                unit="percent",
                category=MetricCategory.SYSTEM
            ),
            KPIDefinition(
                name="api_error_rate",
                description="API error rate percentage",
                formula="api_errors / api_requests_total * 100",
                target_value=1.0,
                threshold_warning=3.0,
                threshold_critical=5.0,
                unit="percent",
                category=MetricCategory.PERFORMANCE,
                dependencies=["api_requests_total"]
            ),
            KPIDefinition(
                name="ml_model_performance",
                description="Average ML model performance score",
                formula="avg(ml_model_accuracy) * 100",
                target_value=95.0,
                threshold_warning=90.0,
                threshold_critical=85.0,
                unit="percent",
                category=MetricCategory.ML,
                dependencies=["ml_model_accuracy"]
            ),
            KPIDefinition(
                name="customer_satisfaction_score",
                description="Customer satisfaction score",
                formula="(positive_feedback - negative_feedback) / total_feedback * 100",
                target_value=85.0,
                threshold_warning=70.0,
                threshold_critical=60.0,
                unit="percent",
                category=MetricCategory.USER
            )
        ]
        
        for kpi_def in kpis:
            self.kpi_definitions[kpi_def.name] = kpi_def
    
    async def start_monitoring(self) -> bool:
        """Start the metrics collection service."""



        try:
            self.status = "running"
            
            # Initialize Redis connection
            await self._initialize_redis()
            
            # Initialize Prometheus metrics
            self._initialize_prometheus_metrics()
            
            # Start collection tasks
            for metric_name, metric_def in self.metrics_definitions.items():
                if metric_def.enabled:
                    task = asyncio.create_task(
                        self._metric_collection_loop(metric_name, metric_def)
                    )
                    self.collection_tasks[metric_name] = task
            
            # Start KPI calculation task
            asyncio.create_task(self._kpi_calculation_loop())
            
            # Start data retention cleanup task
            asyncio.create_task(self._data_cleanup_loop())
            
            logger.info("Metrics collection service started")
            return True
        except Exception as e:
            logger.error(f"Failed to start metrics collection: {e}")
            self.status = "error"
            return False
    
    async def stop_monitoring(self) -> bool:
        """Stop the metrics collection service."""



        try:
            self.status = "stopped"
            
            # Cancel all collection tasks
            for task in self.collection_tasks.values():
                task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self.collection_tasks.values(), return_exceptions=True)
            self.collection_tasks.clear()
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Metrics collection service stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop metrics collection: {e}")
            return False
    
    async def _initialize_redis(self):
        """Initialize Redis connection for metrics storage."""



        try:
            self.redis_client = await aioredis.from_url(
                "redis://localhost:6379", 
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Redis connection established for metrics storage")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}, using in-memory storage")
            self.redis_client = None
    
    def _initialize_prometheus_metrics(self):
        """Initialize Prometheus metrics."""
        for metric_name, metric_def in self.metrics_definitions.items():
            labels = metric_def.labels + ["instance"]
            
            if metric_def.metric_type == MetricType.COUNTER:
                metric = Counter(
                    metric_name,
                    metric_def.description,
                    labels,
                    registry=self.prometheus_registry
                )
            elif metric_def.metric_type == MetricType.GAUGE:
                metric = Gauge(
                    metric_name,
                    metric_def.description,
                    labels,
                    registry=self.prometheus_registry
                )
            elif metric_def.metric_type == MetricType.HISTOGRAM:
                metric = Histogram(
                    metric_name,
                    metric_def.description,
                    labels,
                    registry=self.prometheus_registry
                )
            elif metric_def.metric_type == MetricType.SUMMARY:
                metric = Summary(
                    metric_name,
                    metric_def.description,
                    labels,
                    registry=self.prometheus_registry
                )
            else:
                continue
            
            self.prometheus_metrics[metric_name] = metric
    
    async def _metric_collection_loop(self, metric_name: str, metric_def: MetricDefinition):
        """Continuous metric collection loop."""
        while self.status == "running":
            try:
                # Collect metric value
                if metric_def.category == MetricCategory.SYSTEM:
                    await self._collect_system_metric(metric_name, metric_def)
                else:
                    # For business metrics, rely on external reporting
                    pass
                
                await asyncio.sleep(metric_def.collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error collecting metric {metric_name}: {e}")
                await asyncio.sleep(60)
    
    async def _collect_system_metric(self, metric_name: str, metric_def: MetricDefinition):
        """Collect system-specific metrics."""



        try:
            if metric_name == "cpu_usage_percent":
                value = psutil.cpu_percent(interval=1)
                await self.record_metric(metric_name, value)
            
            elif metric_name == "memory_usage_percent":
                memory = psutil.virtual_memory()
                value = memory.percent
                await self.record_metric(metric_name, value)
            
            elif metric_name == "disk_usage_percent":
                for partition in psutil.disk_partitions():
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        value = (usage.used / usage.total) * 100
                        await self.record_metric(
                            metric_name, 
                            value, 
                            labels={"mount_point": partition.mountpoint}
                        )
                    except PermissionError:
                        continue
            
            elif metric_name == "network_bytes_sent":
                net_io = psutil.net_io_counters(pernic=True)
                for interface, stats in net_io.items():
                    await self.record_metric(
                        metric_name,
                        stats.bytes_sent,
                        labels={"interface": interface}
                    )
            
            elif metric_name == "network_bytes_received":
                net_io = psutil.net_io_counters(pernic=True)
                for interface, stats in net_io.items():
                    await self.record_metric(
                        metric_name,
                        stats.bytes_recv,
                        labels={"interface": interface}
                    )
            
            elif metric_name == "process_count":
                value = len(psutil.pids())
                await self.record_metric(metric_name, value)
                
        except Exception as e:
            logger.error(f"Failed to collect system metric {metric_name}: {e}")
    
    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect all system metrics."""



        try:
            metrics = {}
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            
            metrics.update({
                "cpu_usage_percent": cpu_percent,
                "cpu_count": cpu_count,
                "load_avg_1m": load_avg[0],
                "load_avg_5m": load_avg[1],
                "load_avg_15m": load_avg[2]
            })
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            metrics.update({
                "memory_total_bytes": memory.total,
                "memory_used_bytes": memory.used,
                "memory_available_bytes": memory.available,
                "memory_usage_percent": memory.percent,
                "swap_total_bytes": swap.total,
                "swap_used_bytes": swap.used,
                "swap_usage_percent": swap.percent
            })
            
            # Disk metrics
            disk_metrics = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    mount_point = partition.mountpoint.replace("/", "_").replace("\\", "_")
                    disk_metrics.update({
                        f"disk_total_bytes_{mount_point}": usage.total,
                        f"disk_used_bytes_{mount_point}": usage.used,
                        f"disk_free_bytes_{mount_point}": usage.free,
                        f"disk_usage_percent_{mount_point}": (usage.used / usage.total) * 100
                    })
                except PermissionError:
                    continue
            
            metrics.update(disk_metrics)
            
            # Network metrics
            net_io = psutil.net_io_counters()
            if net_io:
                metrics.update({
                    "network_bytes_sent": net_io.bytes_sent,
                    "network_bytes_received": net_io.bytes_recv,
                    "network_packets_sent": net_io.packets_sent,
                    "network_packets_received": net_io.packets_recv
                })
            
            # Process metrics
            process_count = len(psutil.pids())
            metrics["process_count"] = process_count
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {}
    
    async def record_metric(self, metric_name: str, value: Union[int, float], 
                          labels: Optional[Dict[str, str]] = None, 
                          timestamp: Optional[datetime] = None):
        """Record a metric value."""



        try:
            if metric_name not in self.metrics_definitions:
                logger.warning(f"Unknown metric: {metric_name}")
                return
            
            # Create data point
            data_point = MetricDataPoint(
                metric_name=metric_name,
                value=value,
                timestamp=timestamp or datetime.utcnow(),
                labels=labels or {}
            )
            
            # Store in memory
            self.metrics_data[metric_name].append(data_point)
            
            # Store in Redis if available
            if self.redis_client:
                await self._store_metric_in_redis(data_point)
            
            # Update Prometheus metric
            if metric_name in self.prometheus_metrics:
                prometheus_metric = self.prometheus_metrics[metric_name]
                label_values = [labels.get(label, "") for label in self.metrics_definitions[metric_name].labels]
                label_values.append("main")  # instance label
                
                if isinstance(prometheus_metric, (Counter, Gauge)):
                    if hasattr(prometheus_metric, 'labels'):
                        prometheus_metric.labels(*label_values).set(value)
                    else:
                        prometheus_metric.set(value)
                elif isinstance(prometheus_metric, (Histogram, Summary)):
                    if hasattr(prometheus_metric, 'labels'):
                        prometheus_metric.labels(*label_values).observe(value)
                    else:
                        prometheus_metric.observe(value)
            
            # Check alert thresholds
            await self._check_alert_thresholds(metric_name, value)
            
        except Exception as e:
            logger.error(f"Failed to record metric {metric_name}: {e}")
    
    async def _store_metric_in_redis(self, data_point: MetricDataPoint):
        """Store metric data point in Redis."""



        try:
            key = f"metrics:{data_point.metric_name}:{data_point.timestamp.strftime('%Y%m%d%H%M%S')}"
            value = {
                "value": data_point.value,
                "labels": data_point.labels,
                "metadata": data_point.metadata
            }
            
            await self.redis_client.setex(key, 86400, json.dumps(value))  # 24h TTL
            
        except Exception as e:
            logger.error(f"Failed to store metric in Redis: {e}")
    
    async def _check_alert_thresholds(self, metric_name: str, value: float):
        """Check if metric value exceeds alert thresholds."""



        try:
            metric_def = self.metrics_definitions[metric_name]
            thresholds = metric_def.alert_thresholds
            
            if "critical" in thresholds and value >= thresholds["critical"]:
                await self._send_alert(metric_name, value, "critical")
            elif "warning" in thresholds and value >= thresholds["warning"]:
                await self._send_alert(metric_name, value, "warning")
                
        except Exception as e:
            logger.error(f"Failed to check alert thresholds: {e}")
    
    async def _send_alert(self, metric_name: str, value: float, severity: str):
        """Send metric alert."""
        logger.warning(f"METRIC ALERT [{severity.upper()}]: {metric_name} = {value}")
        # Implement actual alerting logic here (email, Slack, etc.)
    
    async def _kpi_calculation_loop(self):
        """Continuous KPI calculation loop."""
        while self.status == "running":
            try:
                for kpi_name, kpi_def in self.kpi_definitions.items():
                    result = await self.calculate_kpi(kpi_name)
                    if result:
                        self.kpi_results[kpi_name].append(result)
                
                await asyncio.sleep(300)  # Calculate KPIs every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in KPI calculation loop: {e}")
                await asyncio.sleep(60)
    
    async def calculate_kpi(self, kpi_name: str) -> Optional[KPIResult]:
        """Calculate a specific KPI."""



        try:
            if kpi_name not in self.kpi_definitions:
                logger.error(f"Unknown KPI: {kpi_name}")
                return None
            
            kpi_def = self.kpi_definitions[kpi_name]
            
            # Check if all dependencies are available
            required_metrics = {}
            for dep in kpi_def.dependencies:
                if dep not in self.metrics_data or not self.metrics_data[dep]:
                    logger.warning(f"Missing dependency {dep} for KPI {kpi_name}")
                    return None
                
                # Get recent metric values
                recent_values = [
                    dp.value for dp in list(self.metrics_data[dep])[-100:]  # Last 100 values
                ]
                required_metrics[dep] = recent_values
            
            # Calculate KPI value based on formula
            kpi_value = await self._evaluate_kpi_formula(kpi_def.formula, required_metrics)
            
            if kpi_value is None:
                return None
            
            # Determine status
            status = "normal"
            if kpi_def.threshold_critical and kpi_value <= kpi_def.threshold_critical:
                status = "critical"
            elif kpi_def.threshold_warning and kpi_value <= kpi_def.threshold_warning:
                status = "warning"
            
            # Calculate trend
            trend = "stable"
            previous_results = list(self.kpi_results[kpi_name])
            if previous_results:
                previous_value = previous_results[-1].value
                change_percentage = ((kpi_value - previous_value) / previous_value) * 100
                
                if change_percentage > 5:
                    trend = "increasing"
                elif change_percentage < -5:
                    trend = "decreasing"
            else:
                previous_value = None
                change_percentage = None
            
            result = KPIResult(
                kpi_name=kpi_name,
                value=kpi_value,
                status=status,
                trend=trend,
                previous_value=previous_value,
                change_percentage=change_percentage
            )
            
            logger.info(f"KPI calculated: {kpi_name} = {kpi_value:.2f} ({status})")
            return result
            
        except Exception as e:
            logger.error(f"Failed to calculate KPI {kpi_name}: {e}")
            return None
    
    async def _evaluate_kpi_formula(self, formula: str, metrics: Dict[str, List[float]]) -> Optional[float]:
        """Evaluate KPI formula with metric values."""



        try:
            # Simple formula evaluation (extend for more complex formulas)
            context = {}
            
            # Add metric aggregations to context
            for metric_name, values in metrics.items():
                if values:
                    context[metric_name] = values[-1]  # Latest value
                    context[f"avg_{metric_name}"] = statistics.mean(values)
                    context[f"max_{metric_name}"] = max(values)
                    context[f"min_{metric_name}"] = min(values)
                    context[f"sum_{metric_name}"] = sum(values)
                    context[f"count_{metric_name}"] = len(values)
            
            # Add mathematical functions
            context.update({
                "avg": statistics.mean,
                "max": max,
                "min": min,
                "sum": sum,
                "len": len,
                "abs": abs
            })
            
            # Evaluate formula (simplified - use proper expression parser in production)
            result = eval(formula, {"__builtins__": {}}, context)
            return float(result)
            
        except Exception as e:
            logger.error(f"Failed to evaluate KPI formula '{formula}': {e}")
            return None
    
    async def _data_cleanup_loop(self):
        """Periodic data cleanup based on retention policies."""
        while self.status == "running":
            try:
                current_time = datetime.utcnow()
                
                # Clean up old metric data
                for metric_name, metric_def in self.metrics_definitions.items():
                    if metric_name in self.metrics_data:
                        cutoff_time = current_time - timedelta(seconds=metric_def.retention_period)
                        
                        # Remove old data points
                        data_queue = self.metrics_data[metric_name]
                        while data_queue and data_queue[0].timestamp < cutoff_time:
                            data_queue.popleft()
                
                # Clean up old KPI results
                for kpi_name in self.kpi_results:
                    cutoff_time = current_time - timedelta(days=30)  # Keep KPIs for 30 days
                    
                    results_queue = self.kpi_results[kpi_name]
                    while results_queue and results_queue[0].timestamp < cutoff_time:
                        results_queue.popleft()
                
                # Clean up Redis keys if available
                if self.redis_client:
                    await self._cleanup_redis_data(current_time)
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in data cleanup loop: {e}")
                await asyncio.sleep(3600)
    
    async def _cleanup_redis_data(self, current_time: datetime):
        """Clean up old Redis metric data."""



        try:
            # Get all metric keys
            keys = await self.redis_client.keys("metrics:*")
            
            for key in keys:
                # Extract timestamp from key
                parts = key.split(":")
                if len(parts) >= 3:
                    timestamp_str = parts[2]
                    try:
                        timestamp = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
                        if (current_time - timestamp).total_seconds() > 86400:  # 24 hours
                            await self.redis_client.delete(key)
                    except ValueError:
                        continue
                        
        except Exception as e:
            logger.error(f"Failed to cleanup Redis data: {e}")
    
    async def get_metric_history(self, metric_name: str, 
                               start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None) -> List[MetricDataPoint]:
        """Get historical metric data."""



        try:
            if metric_name not in self.metrics_data:
                return []
            
            data_points = list(self.metrics_data[metric_name])
            
            # Filter by time range
            if start_time or end_time:
                filtered_points = []
                for dp in data_points:
                    if start_time and dp.timestamp < start_time:
                        continue
                    if end_time and dp.timestamp > end_time:
                        continue
                    filtered_points.append(dp)
                return filtered_points
            
            return data_points
            
        except Exception as e:
            logger.error(f"Failed to get metric history: {e}")
            return []
    
    async def get_kpi_history(self, kpi_name: str) -> List[KPIResult]:
        """Get historical KPI results."""



        try:
            if kpi_name not in self.kpi_results:
                return []
            
            return list(self.kpi_results[kpi_name])
            
        except Exception as e:
            logger.error(f"Failed to get KPI history: {e}")
            return []
    
    async def generate_metrics_dashboard(self) -> Dict[str, Any]:
        """Generate metrics dashboard data."""



        try:
            dashboard_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "system_metrics": {},
                "business_metrics": {},
                "kpis": {},
                "alerts": []
            }
            
            # Collect latest system metrics
            system_metrics = await self._collect_system_metrics()
            dashboard_data["system_metrics"] = system_metrics
            
            # Collect latest business metrics
            for metric_name, data_queue in self.metrics_data.items():
                if data_queue and self.metrics_definitions[metric_name].category != MetricCategory.SYSTEM:
                    latest_value = data_queue[-1].value
                    dashboard_data["business_metrics"][metric_name] = latest_value
            
            # Collect latest KPIs
            for kpi_name, results_queue in self.kpi_results.items():
                if results_queue:
                    latest_result = results_queue[-1]
                    dashboard_data["kpis"][kpi_name] = {
                        "value": latest_result.value,
                        "status": latest_result.status,
                        "trend": latest_result.trend,
                        "change_percentage": latest_result.change_percentage
                    }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to generate metrics dashboard: {e}")
            return {}
    
    async def get_monitoring_metrics(self) -> MonitoringMetrics:
        """Get monitoring engine metrics."""
        metrics = MonitoringMetrics()
        
        # Custom metrics for collector
        metrics.custom_metrics = {
            "defined_metrics": len(self.metrics_definitions),
            "active_metrics": len([m for m in self.metrics_definitions.values() if m.enabled]),
            "total_data_points": sum(len(queue) for queue in self.metrics_data.values()),
            "defined_kpis": len(self.kpi_definitions),
            "calculated_kpis": len(self.kpi_results),
            "collection_tasks": len(self.collection_tasks),
            "redis_connected": self.redis_client is not None
        }
        
        return metrics

class KPICalculator:
    """
    Specialized KPI calculation engine.
    Provides advanced KPI calculation and analysis capabilities.
    """
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.custom_functions: Dict[str, Callable] = {}
        self.calculation_cache: Dict[str, Any] = {}
    
    def register_custom_function(self, name: str, function: Callable):
        """Register custom function for KPI calculations."""
        self.custom_functions[name] = function
    
    async def calculate_advanced_kpi(self, formula: str, context: Dict[str, Any]) -> float:
        """Calculate KPI with advanced formula support."""
        # Enhanced formula evaluation with custom functions
        enhanced_context = {**context, **self.custom_functions}
        
        # Add statistical functions
        enhanced_context.update({
            "percentile": np.percentile,
            "correlation": np.corrcoef,
            "trend": self._calculate_trend,
            "forecast": self._simple_forecast,
            "anomaly_score": self._calculate_anomaly_score
        })
        
        result = eval(formula, {"__builtins__": {}}, enhanced_context)
        return float(result)
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values."""
        if len(values) < 2:
            return "stable"
        
        # Simple linear regression slope
        x = list(range(len(values)))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _simple_forecast(self, values: List[float], periods: int = 1) -> List[float]:
        """Simple linear forecast."""
        if len(values) < 2:
            return [values[-1]] * periods if values else [0.0] * periods
        
        x = np.array(range(len(values)))
        y = np.array(values)
        
        # Linear regression
        coeffs = np.polyfit(x, y, 1)
        
        # Forecast
        forecast_x = np.array(range(len(values), len(values) + periods))
        forecast_y = np.polyval(coeffs, forecast_x)
        
        return forecast_y.tolist()
    
    def _calculate_anomaly_score(self, values: List[float], current_value: float) -> float:
        """Calculate anomaly score for current value."""
        if len(values) < 3:
            return 0.0
        
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values) if len(values) > 1 else 0
        
        if std_val == 0:
            return 0.0
        
        # Z-score based anomaly detection
        z_score = abs((current_value - mean_val) / std_val)
        
        # Normalize to 0-1 scale
        return min(z_score / 3.0, 1.0)  # 3 standard deviations = max score
