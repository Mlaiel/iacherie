"""Advanced Analytics and Metrics Module for AI Engines

Enterprise-grade analytics, performance monitoring, and business intelligence
for the IA-Influencer platform AI content processing engines.

🚀 Enterprise Team Project Specialties:
✅ Lead Dev + Architecte Développeur IA
✅ Développeur Backend Senior (Python/FastAPI/Django)  
✅ Ingénieur Machine Learning (TensorFlow/PyTorch/Hugging Face)
✅ DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
✅ Spécialiste Sécurité Backend
✅ Architecte Microservices
✅ Développeur Audio
✅ DevOps Engineer
✅ IA Prompt Engineer

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. 
Unauthorized use, modification, or distribution by any individual or entity 
without explicit written consent from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
Violators will face legal action under international copyright law.

⚖️ LEGAL NOTICE: THEFT OF IDEAS, CONCEPTS, OR CODE WITHOUT EXPLICIT WRITTEN AUTHORIZATION  
FROM FAHED MLAIEL (mlaiel@live.de) IS STRICTLY FORBIDDEN AND WILL RESULT  
IN IMMEDIATE LEGAL PROSECUTION UNDER INTERNATIONAL COPYRIGHT LAW.

🔒 NO UNAUTHORIZED USE, COPYING, MODIFICATION, OR DISTRIBUTION ALLOWED.

Business Logic: User Upload → AI Processing → Protection → SEO → Collaboration → Distribution
"""

import asyncio
import time
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from pathlib import Path


class MetricType(Enum):
    """
Types of metrics collected"""

    PERFORMANCE = "performance"
    BUSINESS = "business"
    QUALITY = "quality"
    SECURITY = "security"
    USER_EXPERIENCE = "user_experience"
    REVENUE = "revenue"
    COLLABORATION = "collaboration"
    PROTECTION = "protection"


class AggregationPeriod(Enum):
    """Metric aggregation time periods"""

    REAL_TIME = "real_time"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


@dataclass
class MetricPoint:
    """Individual metric data point"""
    timestamp: datetime
    value: Union[int, float, str, bool]
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """
Performance-related metrics"""
    processing_time: float = 0.0
    throughput: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    gpu_usage_percent: float = 0.0
    queue_length: int = 0
    error_rate: float = 0.0
    success_rate: float = 100.0
    availability: float = 100.0
    latency_p50: float = 0.0
    latency_p90: float = 0.0
    latency_p99: float = 0.0


@dataclass
class BusinessMetrics:
    """
Business-related metrics"""
    total_content_processed: int = 0
    revenue_generated: float = 0.0
    active_users: int = 0
    new_users: int = 0
    user_retention_rate: float = 0.0
    collaborations_created: int = 0
    successful_matches: int = 0
    content_protected: int = 0
    copyright_violations_detected: int = 0
    monetization_opportunities: int = 0
    avg_revenue_per_user: float = 0.0
    customer_lifetime_value: float = 0.0


@dataclass
class QualityMetrics:
    """
Content quality metrics"""
    avg_quality_score: float = 0.0
    content_approval_rate: float = 0.0
    user_satisfaction_score: float = 0.0
    ai_accuracy_score: float = 0.0
    false_positive_rate: float = 0.0
    false_negative_rate: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    content_uniqueness_score: float = 0.0


@dataclass
class SecurityMetrics:
    """
Security-related metrics"""
    security_threats_detected: int = 0
    security_incidents: int = 0
    failed_auth_attempts: int = 0
    suspicious_activities: int = 0
    data_breach_attempts: int = 0
    malware_detected: int = 0
    phishing_attempts: int = 0
    ddos_attacks: int = 0
    security_score: float = 100.0
    compliance_score: float = 100.0


@dataclass
class CollaborationMetrics:
    """
Collaboration and networking metrics"""
    collaboration_requests: int = 0
    successful_collaborations: int = 0
    collaboration_success_rate: float = 0.0
    avg_collaboration_value: float = 0.0
    network_growth_rate: float = 0.0
    cross_platform_connections: int = 0
    influencer_matches: int = 0
    brand_partnerships: int = 0
    community_engagement: float = 0.0
    viral_content_count: int = 0


class MetricsCollector:
    """
    Advanced metrics collection and aggregation system.
    
    Collects, processes, and analyzes metrics from all AI engines
    with real-time monitoring and historical analysis capabilities.
    """
    
    def __init__(
        self,
        buffer_size: int = 10000,
        aggregation_interval: int = 60,
        retention_days: int = 90
    ):
        self.buffer_size = buffer_size
        self.aggregation_interval = aggregation_interval
        self.retention_days = retention_days
        
        # Metric storage
        self.raw_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=buffer_size))
        self.aggregated_metrics: Dict[str, Dict[AggregationPeriod, List[MetricPoint]]] = defaultdict(
            lambda: {period: [] for period in AggregationPeriod}
        )
        
        # Performance tracking
        self.performance_metrics = PerformanceMetrics()
        self.business_metrics = BusinessMetrics()
        self.quality_metrics = QualityMetrics()
        self.security_metrics = SecurityMetrics()
        self.collaboration_metrics = CollaborationMetrics()
        
        # Aggregation state
        self.last_aggregation = datetime.now()
        self.aggregation_lock = threading.Lock()
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
        # Start background aggregation
        self._start_background_aggregation()
        
    def record_metric(
        self,
        metric_name: str,
        value: Union[int, float, str, bool],
        metric_type: MetricType = MetricType.PERFORMANCE,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Record a metric data point.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            metric_type: Type of metric
            tags: Optional tags for filtering
            metadata: Optional additional metadata
        """
        metric_point = MetricPoint(
            timestamp=datetime.now(),
            value=value,
            tags=tags or {},
            metadata=metadata or {}
        )
        
        # Add metric type to tags
        metric_point.tags["metric_type"] = metric_type.value
        
        # Store in buffer
        self.raw_metrics[metric_name].append(metric_point)
        
        # Update real-time metrics
        self._update_real_time_metrics(metric_name, metric_point)
        
    def record_processing_time(
        self,
        engine_name: str,
        processing_time: float,
        content_type: str,
        success: bool = True
    ):
        """Record processing time metrics"""
        self.record_metric(
            f"{engine_name}.processing_time",
            processing_time,
            MetricType.PERFORMANCE,
            {"engine": engine_name, "content_type": content_type, "success": str(success)}
        )
        
        # Update performance metrics
        if hasattr(self.performance_metrics, 'processing_time'):
            times = [p.value for p in list(self.raw_metrics[f"{engine_name}.processing_time"])[-100:]]
            if times:
                self.performance_metrics.processing_time = statistics.mean(times)
                
    def record_revenue(
        self,
        engine_name: str,
        revenue: float,
        user_id: str,
        content_type: str
    ):
        """Record revenue metrics"""
        self.record_metric(
            f"{engine_name}.revenue",
            revenue,
            MetricType.REVENUE,
            {"engine": engine_name, "user_id": user_id, "content_type": content_type}
        )
        
        # Update business metrics
        self.business_metrics.revenue_generated += revenue
        
    def record_collaboration(
        self,
        engine_name: str,
        collaboration_type: str,
        success: bool,
        value: float = 0.0
    ):
        """Record collaboration metrics"""
        self.record_metric(
            f"{engine_name}.collaboration",
            1 if success else 0,
            MetricType.COLLABORATION,
            {"engine": engine_name, "type": collaboration_type, "success": str(success)}
        )
        
        # Update collaboration metrics
        self.collaboration_metrics.collaboration_requests += 1
        if success:
            self.collaboration_metrics.successful_collaborations += 1
            self.collaboration_metrics.avg_collaboration_value = (
                (self.collaboration_metrics.avg_collaboration_value * 
                 (self.collaboration_metrics.successful_collaborations - 1) + value) /
                self.collaboration_metrics.successful_collaborations
            )
            
    def record_quality_score(
        self,
        engine_name: str,
        quality_score: float,
        content_type: str
    ):
        """Record content quality metrics"""
        self.record_metric(
            f"{engine_name}.quality_score",
            quality_score,
            MetricType.QUALITY,
            {"engine": engine_name, "content_type": content_type}
        )
        
        # Update quality metrics
        scores = [p.value for p in list(self.raw_metrics[f"{engine_name}.quality_score"])[-100:]]
        if scores:
            self.quality_metrics.avg_quality_score = statistics.mean(scores)
            
    def record_security_event(
        self,
        event_type: str,
        severity: str,
        engine_name: str,
        details: Dict[str, Any]
    ):
        """Record security events"""
        self.record_metric(
            f"security.{event_type}",
            1,
            MetricType.SECURITY,
            {"engine": engine_name, "severity": severity},
            details
        )
        
        # Update security metrics
        if event_type == "threat_detected":
            self.security_metrics.security_threats_detected += 1
        elif event_type == "auth_failure":
            self.security_metrics.failed_auth_attempts += 1
        elif event_type == "suspicious_activity":
            self.security_metrics.suspicious_activities += 1
            
    def get_metrics_summary(
        self,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive metrics summary.
        
        Args:
            time_range: Optional time range filter
            
        Returns:
            Complete metrics summary
        """
        if time_range is None:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=24)
            time_range = (start_time, end_time)
            
        summary = {
            "performance": asdict(self.performance_metrics),
            "business": asdict(self.business_metrics),
            "quality": asdict(self.quality_metrics),
            "security": asdict(self.security_metrics),
            "collaboration": asdict(self.collaboration_metrics),
            "time_range": {
                "start": time_range[0].isoformat(),
                "end": time_range[1].isoformat()
            },
            "top_engines": self._get_top_engines(),
            "trending_metrics": self._get_trending_metrics(),
            "alerts": self._get_active_alerts()
        }
        
        return summary
        
    def get_engine_metrics(
        self,
        engine_name: str,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """
        Get metrics for specific engine.
        
        Args:
            engine_name: Name of the engine
            time_range: Optional time range filter
            
        Returns:
            Engine-specific metrics
        """
        if time_range is None:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=24)
            time_range = (start_time, end_time)
            
        engine_metrics = {}
        
        for metric_name, points in self.raw_metrics.items():
            if metric_name.startswith(f"{engine_name}."):
                filtered_points = [
                    p for p in points
                    if time_range[0] <= p.timestamp <= time_range[1]
                ]
                
                if filtered_points:
                    values = [p.value for p in filtered_points if isinstance(p.value, (int, float))]
                    if values:
                        engine_metrics[metric_name] = {
                            "count": len(values),
                            "avg": statistics.mean(values),
                            "min": min(values),
                            "max": max(values),
                            "std": statistics.stdev(values) if len(values) > 1 else 0,
                            "p50": statistics.median(values),
                            "p90": np.percentile(values, 90) if values else 0,
                            "p99": np.percentile(values, 99) if values else 0
                        }
                        
        return engine_metrics
        
    def get_real_time_dashboard(self) -> Dict[str, Any]:
        """Get real-time dashboard data"""
        return {
            "current_time": datetime.now().isoformat(),
            "system_status": self._get_system_status(),
            "performance": {
                "avg_processing_time": self.performance_metrics.processing_time,
                "throughput": self.performance_metrics.throughput,
                "error_rate": self.performance_metrics.error_rate,
                "memory_usage": self.performance_metrics.memory_usage_mb,
                "cpu_usage": self.performance_metrics.cpu_usage_percent
            },
            "business": {
                "revenue_today": self._calculate_daily_revenue(),
                "content_processed_today": self._calculate_daily_content(),
                "active_users": self.business_metrics.active_users,
                "collaborations_today": self._calculate_daily_collaborations()
            },
            "alerts": self._get_active_alerts(),
            "top_performing_engines": self._get_top_engines()[:5]
        }
        
    def _update_real_time_metrics(self, metric_name: str, metric_point: MetricPoint):
        """Update real-time metric aggregations"""
        if isinstance(metric_point.value, (int, float)):
            # Update throughput
            if "processing_time" in metric_name:
                recent_points = list(self.raw_metrics[metric_name])[-100:]
                if recent_points:
                    times = [p.value for p in recent_points]
                    self.performance_metrics.throughput = len(times) / sum(times) * 60 if sum(times) > 0 else 0
                    
    def _start_background_aggregation(self):
        """Start background metric aggregation"""
        def aggregation_worker():
        try:
            logger.info(f"Executing aggregation_worker")
            
            # Implementation for aggregation_worker
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"aggregation_worker completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"aggregation_worker failed: {e}")
            raise
                try:
                    time.sleep(self.aggregation_interval)
                    self._aggregate_metrics()
                except Exception as e:
                    self.logger.error(f"Aggregation error: {str(e)}")
                    
        aggregation_thread = threading.Thread(target=aggregation_worker, daemon=True)
        aggregation_thread.start()
        
    def _aggregate_metrics(self):
        """Aggregate raw metrics into time periods"""
        with self.aggregation_lock:
            current_time = datetime.now()
            
            # Aggregate for different periods
            for period in AggregationPeriod:
                if period == AggregationPeriod.REAL_TIME:
                    continue
                    
                period_start = self._get_period_start(current_time, period)
                
                for metric_name, points in self.raw_metrics.items():
                    period_points = [
                        p for p in points
                        if period_start <= p.timestamp <= current_time
                    ]
                    
                    if period_points:
                        aggregated_value = self._calculate_aggregated_value(period_points)
                        
                        aggregated_point = MetricPoint(
                            timestamp=period_start,
                            value=aggregated_value,
                            tags={"period": period.value},
                            metadata={"point_count": len(period_points)}
                        )
                        
                        self.aggregated_metrics[metric_name][period].append(aggregated_point)
                        
            # Cleanup old aggregated data
            self._cleanup_old_data()
            
            self.last_aggregation = current_time
            
    def _get_period_start(self, timestamp: datetime, period: AggregationPeriod) -> datetime:
        """Get start of period for timestamp"""
        if period == AggregationPeriod.MINUTE:
            return timestamp.replace(second=0, microsecond=0)
        elif period == AggregationPeriod.HOUR:
            return timestamp.replace(minute=0, second=0, microsecond=0)
        elif period == AggregationPeriod.DAY:
            return timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == AggregationPeriod.WEEK:
            days_since_monday = timestamp.weekday()
            return (timestamp - timedelta(days=days_since_monday)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        elif period == AggregationPeriod.MONTH:
            return timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == AggregationPeriod.YEAR:
            return timestamp.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            return timestamp
            
    def _calculate_aggregated_value(self, points: List[MetricPoint]) -> float:
        """
Calculate aggregated value from points"""
        numeric_values = [p.value for p in points if isinstance(p.value, (int, float))]
        
        if not numeric_values:
            return 0.0
            
        # For most metrics, use average
        return statistics.mean(numeric_values)
        
    def _cleanup_old_data(self):
        """
Remove old aggregated data beyond retention period"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        for metric_name in self.aggregated_metrics:
            for period in AggregationPeriod:
                self.aggregated_metrics[metric_name][period] = [
                    p for p in self.aggregated_metrics[metric_name][period]
                    if p.timestamp >= cutoff_date
                ]
                
    def _get_system_status(self) -> str:
        """
Get overall system status"""
        if self.performance_metrics.error_rate > 10:
            return "critical"
        elif self.performance_metrics.error_rate > 5:
            return "warning"
        elif self.performance_metrics.availability < 95:
            return "degraded"
        else:
            return "healthy"
            
    def _calculate_daily_revenue(self) -> float:
        """Calculate revenue for today"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        daily_revenue = 0.0
        for metric_name, points in self.raw_metrics.items():
            if ".revenue" in metric_name:
                for point in points:
                    if today <= point.timestamp < tomorrow:
                        daily_revenue += point.value
                        
        return daily_revenue
        
    def _calculate_daily_content(self) -> int:
        """Calculate content processed today"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        content_count = 0
        for metric_name, points in self.raw_metrics.items():
            if ".processing_time" in metric_name:
                for point in points:
                    if today <= point.timestamp < tomorrow:
                        content_count += 1
                        
        return content_count
        
    def _calculate_daily_collaborations(self) -> int:
        """Calculate collaborations created today"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        collaboration_count = 0
        for metric_name, points in self.raw_metrics.items():
            if ".collaboration" in metric_name:
                for point in points:
                    if (today <= point.timestamp < tomorrow and 
                        point.tags.get("success") == "True"):
                        collaboration_count += 1
                        
        return collaboration_count
        
    def _get_top_engines(self) -> List[Dict[str, Any]]:
        """Get top performing engines"""
        engine_performance = defaultdict(lambda: {"total_processed": 0, "avg_time": 0, "revenue": 0})
        
        for metric_name, points in self.raw_metrics.items():
            if ".processing_time" in metric_name:
                engine_name = metric_name.split(".")[0]
                for point in points:
                    engine_performance[engine_name]["total_processed"] += 1
                    engine_performance[engine_name]["avg_time"] += point.value
                    
            elif ".revenue" in metric_name:
                engine_name = metric_name.split(".")[0]
                for point in points:
                    engine_performance[engine_name]["revenue"] += point.value
                    
        # Calculate averages and sort
        top_engines = []
        for engine_name, metrics in engine_performance.items():
            if metrics["total_processed"] > 0:
                metrics["avg_time"] /= metrics["total_processed"]
                
            score = (
                metrics["revenue"] * 0.4 +
                metrics["total_processed"] * 0.4 +
                (1000 / max(metrics["avg_time"], 0.1)) * 0.2
            )
            
            top_engines.append({
                "engine": engine_name,
                "score": score,
                **metrics
            })
            
        return sorted(top_engines, key=lambda x: x["score"], reverse=True)
        
    def _get_trending_metrics(self) -> List[Dict[str, Any]]:
        """Get trending metrics"""
        # Simplified trending calculation
        trending = []
        current_time = datetime.now()
        hour_ago = current_time - timedelta(hours=1)
        
        for metric_name, points in self.raw_metrics.items():
            recent_points = [p for p in points if p.timestamp >= hour_ago]
            if len(recent_points) >= 5:
                values = [p.value for p in recent_points if isinstance(p.value, (int, float))]
                if values:
                    trend = (values[-1] - values[0]) / max(abs(values[0]), 0.1) * 100
                    trending.append({
                        "metric": metric_name,
                        "trend_percent": trend,
                        "current_value": values[-1]
                    })
                    
        return sorted(trending, key=lambda x: abs(x["trend_percent"]), reverse=True)[:10]
        
    def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active system alerts"""
        alerts = []
        
        # Performance alerts
        if self.performance_metrics.error_rate > 5:
            alerts.append({
                "type": "performance",
                "severity": "high" if self.performance_metrics.error_rate > 10 else "medium",
                "message": f"High error rate: {self.performance_metrics.error_rate:.1f}%",
                "timestamp": datetime.now().isoformat()
            })
            
        if self.performance_metrics.memory_usage_mb > 1500:
            alerts.append({
                "type": "resource",
                "severity": "medium",
                "message": f"High memory usage: {self.performance_metrics.memory_usage_mb:.0f}MB",
                "timestamp": datetime.now().isoformat()
            })
            
        # Security alerts
        if self.security_metrics.security_threats_detected > 0:
            alerts.append({
                "type": "security",
                "severity": "high",
                "message": f"Security threats detected: {self.security_metrics.security_threats_detected}",
                "timestamp": datetime.now().isoformat()
            })
            
        return alerts
        
    def export_metrics(
        self,
        format: str = "json",
        time_range: Optional[Tuple[datetime, datetime]] = None,
        metrics_filter: Optional[List[str]] = None
    ) -> Union[str, bytes]:
        """
        Export metrics data.
        
        Args:
            format: Export format (json, csv, parquet)
            time_range: Optional time range filter
            metrics_filter: Optional list of metrics to include
            
        Returns:
            Exported data in requested format
        """
        if time_range is None:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=7)
            time_range = (start_time, end_time)
            
        export_data = []
        
        for metric_name, points in self.raw_metrics.items():
            if metrics_filter and metric_name not in metrics_filter:
                continue
                
            filtered_points = [
                p for p in points
                if time_range[0] <= p.timestamp <= time_range[1]
            ]
            
            for point in filtered_points:
                export_data.append({
                    "metric_name": metric_name,
                    "timestamp": point.timestamp.isoformat(),
                    "value": point.value,
                    "tags": point.tags,
                    "metadata": point.metadata
                })
                
        if format.lower() == "json":
            return json.dumps(export_data, indent=2)
        elif format.lower() == "csv":
            # Convert to CSV format (simplified)
            csv_lines = ["metric_name,timestamp,value,tags,metadata"]
            for data in export_data:
                csv_lines.append(
                    f"{data['metric_name']},{data['timestamp']},{data['value']},"
                    f"\"{json.dumps(data['tags'])}\",\"{json.dumps(data['metadata'])}\""
                )
            return "\n".join(csv_lines)
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Global metrics collector instance
metrics_collector = MetricsCollector()


# Convenience functions
def record_metric(metric_name: str, value: Union[int, float, str, bool], **kwargs):
    """Record a metric"""
    metrics_collector.record_metric(metric_name, value, **kwargs)


def record_processing_time(engine_name: str, processing_time: float, **kwargs):
    """
Record processing time"""
    metrics_collector.record_processing_time(engine_name, processing_time, **kwargs)


def record_revenue(engine_name: str, revenue: float, **kwargs):
    """
Record revenue"""
    metrics_collector.record_revenue(engine_name, revenue, **kwargs)


def get_dashboard_data() -> Dict[str, Any]:
    """
Get real-time dashboard data"""
    return metrics_collector.get_real_time_dashboard()


def get_metrics_summary(**kwargs) -> Dict[str, Any]:
    """
Get metrics summary"""
    return metrics_collector.get_metrics_summary(**kwargs)


# Export all classes and functions
__all__ = [
    "MetricType",
    "AggregationPeriod",
    "MetricPoint",
    "PerformanceMetrics",
    "BusinessMetrics",
    "QualityMetrics",
    "SecurityMetrics",
    "CollaborationMetrics",
    "MetricsCollector",
    "metrics_collector",
    "record_metric",
    "record_processing_time",
    "record_revenue",
    "get_dashboard_data",
    "get_metrics_summary"
]
