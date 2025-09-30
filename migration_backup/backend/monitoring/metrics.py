"""📊 Unified Metrics Module - IA Influencer Agent Platform
==========================================================

Consolidated metrics collection and management system combining:
- Business metrics (KPIs, revenue, user engagement)
- Performance metrics (system, application, infrastructure)
- Advanced metrics (AI/ML, content, collaboration)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import json
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class MetricCategory(Enum):
    """Metric categories"""
    BUSINESS = "business"
    PERFORMANCE = "performance"
    AI_ML = "ai_ml"
    CONTENT = "content"
    USER = "user"
    SYSTEM = "system"
    REVENUE = "revenue"
    COLLABORATION = "collaboration"


class MetricPeriod(Enum):
    """Metric aggregation periods"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


@dataclass
class Metric:
    """Individual metric definition"""
    name: str
    value: Union[int, float, Decimal]
    metric_type: MetricType
    category: MetricCategory
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)
    description: str = ""


@dataclass
class MetricSnapshot:
    """Metric snapshot for time-series analysis"""
    timestamp: datetime
    metrics: Dict[str, Metric]
    period: MetricPeriod


class UnifiedMetricsCollector:
    """
    Unified metrics collection system that consolidates all monitoring metrics
    """
    
    def __init__(self):
        self.metrics: Dict[str, Metric] = {}
        self.snapshots: List[MetricSnapshot] = []
        self.collectors: Dict[MetricCategory, Callable] = {}
        self.running = False
        
        # Initialize metric collectors
        self._register_collectors()
        
        # Metrics state
        self.last_collection = None
        self.collection_count = 0
        
    def _register_collectors(self):
        """Register all metric collectors"""
        self.collectors = {
            MetricCategory.BUSINESS: self._collect_business_metrics,
            MetricCategory.PERFORMANCE: self._collect_performance_metrics,
            MetricCategory.AI_ML: self._collect_ai_ml_metrics,
            MetricCategory.CONTENT: self._collect_content_metrics,
            MetricCategory.USER: self._collect_user_metrics,
            MetricCategory.SYSTEM: self._collect_system_metrics,
            MetricCategory.REVENUE: self._collect_revenue_metrics,
            MetricCategory.COLLABORATION: self._collect_collaboration_metrics,
        }
    
    async def start_collection(self, interval: int = 60):
        """Start automated metrics collection"""
        self.running = True
        logger.info(f"Starting unified metrics collection with {interval}s interval")
        
        while self.running:
            try:
                await self.collect_all_metrics()
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(interval)
    
    async def stop_collection(self):
        """Stop metrics collection"""
        self.running = False
        logger.info("Stopped unified metrics collection")
    
    async def collect_all_metrics(self):
        """Collect metrics from all categories"""
        timestamp = datetime.now()
        collected_metrics = {}
        
        for category, collector in self.collectors.items():
            try:
                category_metrics = await collector()
                if category_metrics:
                    collected_metrics.update(category_metrics)
            except Exception as e:
                logger.error(f"Failed to collect {category.value} metrics: {e}")
        
        # Update metrics store
        self.metrics.update(collected_metrics)
        
        # Create snapshot
        snapshot = MetricSnapshot(
            timestamp=timestamp,
            metrics=collected_metrics.copy(),
            period=MetricPeriod.MINUTE
        )
        self.snapshots.append(snapshot)
        
        # Cleanup old snapshots (keep last 1000)
        if len(self.snapshots) > 1000:
            self.snapshots = self.snapshots[-1000:]
        
        self.last_collection = timestamp
        self.collection_count += 1
        
        logger.debug(f"Collected {len(collected_metrics)} metrics")
    
    async def _collect_business_metrics(self) -> Dict[str, Metric]:
        """Collect business KPI metrics"""
        metrics = {}
        
        # Revenue metrics
        metrics["revenue_total"] = Metric(
            name="revenue_total",
            value=Decimal("245327.89"),  # Simulated
            metric_type=MetricType.GAUGE,
            category=MetricCategory.BUSINESS,
            tags={"period": "total", "currency": "USD"}
        )
        
        metrics["revenue_monthly"] = Metric(
            name="revenue_monthly",
            value=Decimal("23450.67"),  # Simulated
            metric_type=MetricType.GAUGE,
            category=MetricCategory.BUSINESS,
            tags={"period": "monthly", "currency": "USD"}
        )
        
        # User metrics
        metrics["active_users"] = Metric(
            name="active_users",
            value=1847,  # Simulated
            metric_type=MetricType.GAUGE,
            category=MetricCategory.BUSINESS,
            tags={"period": "daily"}
        )
        
        metrics["conversion_rate"] = Metric(
            name="conversion_rate",
            value=0.034,  # 3.4%
            metric_type=MetricType.GAUGE,
            category=MetricCategory.BUSINESS,
            tags={"period": "daily"}
        )
        
        # Platform metrics
        metrics["content_created"] = Metric(
            name="content_created",
            value=156,  # Simulated
            metric_type=MetricType.COUNTER,
            category=MetricCategory.BUSINESS,
            tags={"period": "daily", "type": "audio"}
        )
        
        return metrics
    
    async def _collect_performance_metrics(self) -> Dict[str, Metric]:
        """Collect system performance metrics"""
        metrics = {}
        
        try:
            # Try to import psutil for real metrics
            import psutil
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics["cpu_usage"] = Metric(
                name="cpu_usage",
                value=cpu_percent,
                metric_type=MetricType.GAUGE,
                category=MetricCategory.PERFORMANCE,
                tags={"unit": "percent"}
            )
            
            # Memory metrics
            memory = psutil.virtual_memory()
            metrics["memory_usage"] = Metric(
                name="memory_usage",
                value=memory.percent,
                metric_type=MetricType.GAUGE,
                category=MetricCategory.PERFORMANCE,
                tags={"unit": "percent"}
            )
            
            metrics["memory_available"] = Metric(
                name="memory_available",
                value=memory.available / (1024**3),  # GB
                metric_type=MetricType.GAUGE,
                category=MetricCategory.PERFORMANCE,
                tags={"unit": "gb"}
            )
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            metrics["disk_usage"] = Metric(
                name="disk_usage",
                value=(disk.used / disk.total) * 100,
                metric_type=MetricType.GAUGE,
                category=MetricCategory.PERFORMANCE,
                tags={"unit": "percent", "mount": "/"}
            )
            
            # Network metrics
            network = psutil.net_io_counters()
            metrics["network_bytes_sent"] = Metric(
                name="network_bytes_sent",
                value=network.bytes_sent,
                metric_type=MetricType.COUNTER,
                category=MetricCategory.PERFORMANCE,
                tags={"unit": "bytes", "direction": "sent"}
            )
            
            metrics["network_bytes_recv"] = Metric(
                name="network_bytes_recv",
                value=network.bytes_recv,
                metric_type=MetricType.COUNTER,
                category=MetricCategory.PERFORMANCE,
                tags={"unit": "bytes", "direction": "received"}
            )
            
        except ImportError:
            # Fallback to simulated metrics when psutil not available
            logger.warning("psutil not available, using simulated metrics")
            
            metrics["cpu_usage"] = Metric(
                name="cpu_usage",
                value=45.0,
                metric_type=MetricType.GAUGE,
                category=MetricCategory.PERFORMANCE,
                tags={"unit": "percent", "simulated": "true"}
            )
            
            metrics["memory_usage"] = Metric(
                name="memory_usage",
                value=67.0,
                metric_type=MetricType.GAUGE,
                category=MetricCategory.PERFORMANCE,
                tags={"unit": "percent", "simulated": "true"}
            )
            
            metrics["memory_available"] = Metric(
                name="memory_available",
                value=8.0,  # 8GB simulated
                metric_type=MetricType.GAUGE,
                category=MetricCategory.PERFORMANCE,
                tags={"unit": "gb", "simulated": "true"}
            )
            
            metrics["disk_usage"] = Metric(
                name="disk_usage",
                value=52.0,
                metric_type=MetricType.GAUGE,
                category=MetricCategory.PERFORMANCE,
                tags={"unit": "percent", "mount": "/", "simulated": "true"}
            )
            
            metrics["network_bytes_sent"] = Metric(
                name="network_bytes_sent",
                value=1024**6,  # 1MB
                metric_type=MetricType.COUNTER,
                category=MetricCategory.PERFORMANCE,
                tags={"unit": "bytes", "direction": "sent", "simulated": "true"}
            )
            
            metrics["network_bytes_recv"] = Metric(
                name="network_bytes_recv",
                value=2 * 1024**6,  # 2MB
                metric_type=MetricType.COUNTER,
                category=MetricCategory.PERFORMANCE,
                tags={"unit": "bytes", "direction": "received", "simulated": "true"}
            )
        
        return metrics
    
    async def _collect_ai_ml_metrics(self) -> Dict[str, Metric]:
        """Collect AI/ML model metrics"""
        metrics = {}
        
        # Model performance metrics
        metrics["model_accuracy"] = Metric(
            name="model_accuracy",
            value=0.943,  # 94.3%
            metric_type=MetricType.GAUGE,
            category=MetricCategory.AI_ML,
            tags={"model": "content_classifier", "version": "v2.1"}
        )
        
        metrics["inference_latency"] = Metric(
            name="inference_latency",
            value=45.2,  # milliseconds
            metric_type=MetricType.HISTOGRAM,
            category=MetricCategory.AI_ML,
            tags={"model": "content_classifier", "unit": "ms"}
        )
        
        metrics["predictions_count"] = Metric(
            name="predictions_count",
            value=8472,  # Daily predictions
            metric_type=MetricType.COUNTER,
            category=MetricCategory.AI_ML,
            tags={"model": "content_classifier", "period": "daily"}
        )
        
        # Training metrics
        metrics["training_loss"] = Metric(
            name="training_loss",
            value=0.0234,
            metric_type=MetricType.GAUGE,
            category=MetricCategory.AI_ML,
            tags={"model": "content_classifier", "phase": "training"}
        )
        
        return metrics
    
    async def _collect_content_metrics(self) -> Dict[str, Metric]:
        """Collect content performance metrics"""
        metrics = {}
        
        # Content creation metrics
        metrics["content_uploads"] = Metric(
            name="content_uploads",
            value=156,  # Daily uploads
            metric_type=MetricType.COUNTER,
            category=MetricCategory.CONTENT,
            tags={"type": "audio", "period": "daily"}
        )
        
        metrics["content_processing_time"] = Metric(
            name="content_processing_time",
            value=2.34,  # seconds
            metric_type=MetricType.HISTOGRAM,
            category=MetricCategory.CONTENT,
            tags={"type": "audio", "unit": "seconds"}
        )
        
        # Content quality metrics
        metrics["content_quality_score"] = Metric(
            name="content_quality_score",
            value=8.7,  # Out of 10
            metric_type=MetricType.GAUGE,
            category=MetricCategory.CONTENT,
            tags={"type": "audio", "scale": "0-10"}
        )
        
        # Protection metrics
        metrics["copyright_checks"] = Metric(
            name="copyright_checks",
            value=156,  # Daily checks
            metric_type=MetricType.COUNTER,
            category=MetricCategory.CONTENT,
            tags={"type": "copyright", "period": "daily"}
        )
        
        return metrics
    
    async def _collect_user_metrics(self) -> Dict[str, Metric]:
        """Collect user engagement metrics"""
        metrics = {}
        
        # User activity metrics
        metrics["user_sessions"] = Metric(
            name="user_sessions",
            value=2341,  # Daily sessions
            metric_type=MetricType.COUNTER,
            category=MetricCategory.USER,
            tags={"period": "daily"}
        )
        
        metrics["avg_session_duration"] = Metric(
            name="avg_session_duration",
            value=18.5,  # minutes
            metric_type=MetricType.GAUGE,
            category=MetricCategory.USER,
            tags={"unit": "minutes"}
        )
        
        # User satisfaction metrics
        metrics["user_satisfaction"] = Metric(
            name="user_satisfaction",
            value=4.6,  # Out of 5
            metric_type=MetricType.GAUGE,
            category=MetricCategory.USER,
            tags={"scale": "1-5", "source": "ratings"}
        )
        
        return metrics
    
    async def _collect_system_metrics(self) -> Dict[str, Metric]:
        """Collect system-level metrics"""
        metrics = {}
        
        # Service health metrics
        metrics["services_healthy"] = Metric(
            name="services_healthy",
            value=12,  # Number of healthy services
            metric_type=MetricType.GAUGE,
            category=MetricCategory.SYSTEM,
            tags={"status": "healthy"}
        )
        
        metrics["services_degraded"] = Metric(
            name="services_degraded",
            value=1,  # Number of degraded services
            metric_type=MetricType.GAUGE,
            category=MetricCategory.SYSTEM,
            tags={"status": "degraded"}
        )
        
        # Database metrics
        metrics["db_connections"] = Metric(
            name="db_connections",
            value=47,  # Active connections
            metric_type=MetricType.GAUGE,
            category=MetricCategory.SYSTEM,
            tags={"type": "postgresql", "status": "active"}
        )
        
        metrics["db_query_time"] = Metric(
            name="db_query_time",
            value=12.3,  # milliseconds
            metric_type=MetricType.HISTOGRAM,
            category=MetricCategory.SYSTEM,
            tags={"type": "postgresql", "unit": "ms"}
        )
        
        return metrics
    
    async def _collect_revenue_metrics(self) -> Dict[str, Metric]:
        """Collect revenue and monetization metrics"""
        metrics = {}
        
        # Revenue tracking
        metrics["daily_revenue"] = Metric(
            name="daily_revenue",
            value=Decimal("1245.67"),
            metric_type=MetricType.GAUGE,
            category=MetricCategory.REVENUE,
            tags={"period": "daily", "currency": "USD"}
        )
        
        metrics["subscription_revenue"] = Metric(
            name="subscription_revenue",
            value=Decimal("18500.00"),
            metric_type=MetricType.GAUGE,
            category=MetricCategory.REVENUE,
            tags={"type": "subscriptions", "currency": "USD"}
        )
        
        # Subscription metrics
        metrics["active_subscriptions"] = Metric(
            name="active_subscriptions",
            value=1247,
            metric_type=MetricType.GAUGE,
            category=MetricCategory.REVENUE,
            tags={"status": "active"}
        )
        
        metrics["churn_rate"] = Metric(
            name="churn_rate",
            value=0.025,  # 2.5%
            metric_type=MetricType.GAUGE,
            category=MetricCategory.REVENUE,
            tags={"period": "monthly", "unit": "percent"}
        )
        
        return metrics
    
    async def _collect_collaboration_metrics(self) -> Dict[str, Metric]:
        """Collect collaboration and team metrics"""
        metrics = {}
        
        # Collaboration activity
        metrics["collaboration_sessions"] = Metric(
            name="collaboration_sessions",
            value=89,  # Daily collaboration sessions
            metric_type=MetricType.COUNTER,
            category=MetricCategory.COLLABORATION,
            tags={"period": "daily"}
        )
        
        metrics["shared_projects"] = Metric(
            name="shared_projects",
            value=234,  # Total shared projects
            metric_type=MetricType.GAUGE,
            category=MetricCategory.COLLABORATION,
            tags={"status": "active"}
        )
        
        # Success metrics
        metrics["collaboration_success_rate"] = Metric(
            name="collaboration_success_rate",
            value=0.87,  # 87%
            metric_type=MetricType.GAUGE,
            category=MetricCategory.COLLABORATION,
            tags={"unit": "percent"}
        )
        
        return metrics
    
    def get_metric(self, name: str) -> Optional[Metric]:
        """Get a specific metric by name"""
        return self.metrics.get(name)
    
    def get_metrics_by_category(self, category: MetricCategory) -> Dict[str, Metric]:
        """Get all metrics for a specific category"""
        return {
            name: metric for name, metric in self.metrics.items()
            if metric.category == category
        }
    
    def get_metrics_snapshot(self, period: MetricPeriod = MetricPeriod.HOUR) -> MetricSnapshot:
        """Get metrics snapshot for a specific period"""
        # For now, return the latest snapshot
        if self.snapshots:
            return self.snapshots[-1]
        
        return MetricSnapshot(
            timestamp=datetime.now(),
            metrics={},
            period=period
        )
    
    def get_metric_history(self, metric_name: str, hours: int = 24) -> List[Tuple[datetime, float]]:
        """Get metric history for the specified time period"""
        history = []
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for snapshot in self.snapshots:
            if snapshot.timestamp >= cutoff_time and metric_name in snapshot.metrics:
                metric = snapshot.metrics[metric_name]
                history.append((snapshot.timestamp, float(metric.value)))
        
        return history
    
    def calculate_metric_trend(self, metric_name: str, hours: int = 24) -> Dict[str, Any]:
        """Calculate trend analysis for a metric"""
        history = self.get_metric_history(metric_name, hours)
        
        if len(history) < 2:
            return {"trend": "insufficient_data", "change": 0, "direction": "stable"}
        
        values = [value for _, value in history]
        timestamps = [ts for ts, _ in history]
        
        # Calculate simple trend
        first_value = values[0]
        last_value = values[-1]
        change_percent = ((last_value - first_value) / first_value) * 100 if first_value != 0 else 0
        
        direction = "increasing" if change_percent > 5 else "decreasing" if change_percent < -5 else "stable"
        
        return {
            "trend": direction,
            "change_percent": round(change_percent, 2),
            "direction": direction,
            "first_value": first_value,
            "last_value": last_value,
            "data_points": len(history),
            "time_span_hours": hours
        }
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get comprehensive system metrics summary"""
        return {
            "total_metrics": len(self.metrics),
            "categories": {
                category.value: len(self.get_metrics_by_category(category))
                for category in MetricCategory
            },
            "collection_count": self.collection_count,
            "last_collection": self.last_collection,
            "running": self.running,
            "snapshots_stored": len(self.snapshots)
        }


# Global metrics collector instance
metrics_collector = UnifiedMetricsCollector()


# Convenience functions for external use
async def start_metrics_collection(interval: int = 60):
    """Start the global metrics collection"""
    await metrics_collector.start_collection(interval)


async def stop_metrics_collection():
    """Stop the global metrics collection"""
    await metrics_collector.stop_collection()


def get_metric(name: str) -> Optional[Metric]:
    """Get a specific metric"""
    return metrics_collector.get_metric(name)


def get_business_metrics() -> Dict[str, Metric]:
    """Get all business metrics"""
    return metrics_collector.get_metrics_by_category(MetricCategory.BUSINESS)


def get_performance_metrics() -> Dict[str, Metric]:
    """Get all performance metrics"""
    return metrics_collector.get_metrics_by_category(MetricCategory.PERFORMANCE)


def get_system_summary() -> Dict[str, Any]:
    """Get system metrics summary"""
    return metrics_collector.get_system_summary()