"""
Advanced Alert Metrics and Monitoring System
Created by: Fahed Mlaiel (mlaiel@live.de)

WARNING: This code is proprietary and confidential.
Unauthorized use, reproduction, or distribution is strictly prohibited.
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Comprehensive metrics collection, monitoring, and alerting system with
real-time analytics, performance tracking, and business intelligence.
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from collections import defaultdict, deque
import statistics
from contextlib import asynccontextmanager

import redis.asyncio as redis
from pydantic import BaseModel, Field
import numpy as np
from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry, generate_latest
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from .alert_models import AlertSeverity, AlertStatus, AlertCategory, ContentProtectionAlert
from ...core.database import get_async_session
from ...core.cache import CacheManager

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of metrics collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    CUSTOM = "custom"


class MetricScope(str, Enum):
    """Scope of metric collection."""
    SYSTEM = "system"
    APPLICATION = "application"
    BUSINESS = "business"
    SECURITY = "security"
    PERFORMANCE = "performance"


@dataclass
class MetricDefinition:
    """Definition of a metric to be collected."""
    name: str
    metric_type: MetricType
    description: str
    labels: List[str] = field(default_factory=list)
    buckets: Optional[List[float]] = None  # For histograms
    scope: MetricScope = MetricScope.APPLICATION
    unit: Optional[str] = None
    aggregation_interval: int = 60  # seconds
    retention_days: int = 30


@dataclass
class AlertMetric:
    """Container for alert-related metrics."""
    timestamp: datetime
    alert_id: str
    metric_name: str
    value: Union[int, float]
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BusinessMetrics(BaseModel):
    """Business intelligence metrics."""
    
    # Volume metrics
    total_alerts_created: int = 0
    total_alerts_resolved: int = 0
    total_content_protected: int = 0
    
    # Performance metrics
    average_resolution_time_minutes: float = 0.0
    average_detection_time_seconds: float = 0.0
    false_positive_rate_percent: float = 0.0
    detection_accuracy_percent: float = 0.0
    
    # Business impact
    estimated_revenue_protected: float = 0.0
    content_theft_prevented: int = 0
    legal_actions_initiated: int = 0
    
    # Efficiency metrics
    automation_rate_percent: float = 0.0
    manual_intervention_required: int = 0
    cost_per_alert: float = 0.0
    
    # User satisfaction
    user_satisfaction_score: float = 0.0
    support_tickets_created: int = 0
    feature_adoption_rate: float = 0.0


class SystemPerformanceMetrics(BaseModel):
    """System performance metrics."""
    
    # Processing metrics
    alert_processing_latency_ms: float = 0.0
    notification_delivery_latency_ms: float = 0.0
    evidence_collection_time_ms: float = 0.0
    
    # Throughput metrics
    alerts_per_second: float = 0.0
    peak_alerts_per_minute: int = 0
    concurrent_alert_processing: int = 0
    
    # Resource utilization
    cpu_usage_percent: float = 0.0
    memory_usage_percent: float = 0.0
    disk_usage_percent: float = 0.0
    network_bandwidth_mbps: float = 0.0
    
    # Database metrics
    database_connection_pool_usage: float = 0.0
    database_query_latency_ms: float = 0.0
    redis_memory_usage_mb: float = 0.0
    
    # Error rates
    api_error_rate_percent: float = 0.0
    notification_failure_rate_percent: float = 0.0
    escalation_failure_rate_percent: float = 0.0


class SecurityMetrics(BaseModel):
    """Security-related metrics."""
    
    # Threat detection
    suspicious_activities_detected: int = 0
    blocked_ip_addresses: int = 0
    failed_authentication_attempts: int = 0
    
    # Incident response
    security_incidents_created: int = 0
    security_incidents_resolved: int = 0
    average_incident_response_time_minutes: float = 0.0
    
    # Compliance
    audit_log_entries_created: int = 0
    compliance_violations_detected: int = 0
    data_access_requests: int = 0
    
    # Vulnerabilities
    vulnerability_scans_performed: int = 0
    vulnerabilities_found: int = 0
    vulnerabilities_fixed: int = 0


class AlertMetricsCollector:
    """
    Advanced metrics collection system for alert operations.
    Provides real-time metrics, historical analysis, and business intelligence.
    """
    
    def __init__(
        self,
        cache_manager: CacheManager,
        redis_client: redis.Redis,
        prometheus_registry: Optional[CollectorRegistry] = None
    ):
        self.cache_manager = cache_manager
        self.redis_client = redis_client
        self.prometheus_registry = prometheus_registry or CollectorRegistry()
        
        # Metric storage
        self._metric_buffer: deque = deque(maxlen=10000)
        self._real_time_metrics: Dict[str, Any] = {}
        self._aggregated_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Prometheus metrics
        self._prometheus_metrics: Dict[str, Any] = {}
        
        # Performance tracking
        self._operation_timers: Dict[str, float] = {}
        self._error_counters: Dict[str, int] = defaultdict(int)
        
        # Business metrics
        self._business_metrics = BusinessMetrics()
        self._system_metrics = SystemPerformanceMetrics()
        self._security_metrics = SecurityMetrics()
        
        # Initialize metric definitions
        self._initialize_metrics()
        
        logger.info("Alert Metrics Collector initialized")

    async def initialize(self):
        """Initialize the metrics collector."""



        try:
            # Load historical metrics
            await self._load_historical_metrics()
            
            # Start background aggregation
            asyncio.create_task(self._metrics_aggregation_loop())
            
            # Start cleanup task
            asyncio.create_task(self._metrics_cleanup_loop())
            
            logger.info("Metrics Collector fully initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Metrics Collector: {e}")
            raise

    @asynccontextmanager
    async def timer(self, operation_name: str):
        """Context manager for timing operations."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            await self.record_timing(operation_name, duration)

    async def record_alert_created(self, alert: ContentProtectionAlert):
        """Record metrics for alert creation."""



        try:
            # Basic counters
            await self._increment_prometheus_counter("alerts_created_total", {
                "severity": alert.severity.value,
                "category": alert.category.value,
                "platform": alert.source_platform or "unknown"
            })
            
            # Business metrics
            self._business_metrics.total_alerts_created += 1
            
            # Record in buffer
            metric = AlertMetric(
                timestamp=datetime.now(timezone.utc),
                alert_id=alert.alert_id,
                metric_name="alert_created",
                value=1,
                labels={
                    "severity": alert.severity.value,
                    "category": alert.category.value,
                    "platform": alert.source_platform or "unknown"
                },
                metadata={
                    "confidence_score": alert.confidence_score,
                    "detection_method": alert.detection_method
                }
            )
            
            self._metric_buffer.append(metric)
            
            # Update real-time metrics
            await self._update_real_time_metrics("alerts_created", 1)
            
        except Exception as e:
            logger.error(f"Failed to record alert creation metrics: {e}")

    async def record_alert_resolved(self, alert: ContentProtectionAlert, resolution_time_seconds: float):
        """Record metrics for alert resolution."""



        try:
            # Resolution counter
            await self._increment_prometheus_counter("alerts_resolved_total", {
                "severity": alert.severity.value,
                "category": alert.category.value,
                "resolution_type": "manual" if alert.assigned_to else "automated"
            })
            
            # Resolution time histogram
            await self._record_prometheus_histogram("alert_resolution_time_seconds", 
                                                  resolution_time_seconds, {
                "severity": alert.severity.value,
                "category": alert.category.value
            })
            
            # Business metrics
            self._business_metrics.total_alerts_resolved += 1
            
            # Update average resolution time
            current_avg = self._business_metrics.average_resolution_time_minutes
            total_resolved = self._business_metrics.total_alerts_resolved
            new_avg = ((current_avg * (total_resolved - 1)) + (resolution_time_seconds / 60)) / total_resolved
            self._business_metrics.average_resolution_time_minutes = new_avg
            
            # Record in buffer
            metric = AlertMetric(
                timestamp=datetime.now(timezone.utc),
                alert_id=alert.alert_id,
                metric_name="alert_resolved",
                value=resolution_time_seconds,
                labels={
                    "severity": alert.severity.value,
                    "category": alert.category.value,
                    "resolution_type": "manual" if alert.assigned_to else "automated"
                }
            )
            
            self._metric_buffer.append(metric)
            
        except Exception as e:
            logger.error(f"Failed to record alert resolution metrics: {e}")

    async def record_notification_sent(self, channel: str, success: bool, latency_ms: float):
        """Record notification delivery metrics."""



        try:
            # Notification counter
            await self._increment_prometheus_counter("notifications_sent_total", {
                "channel": channel,
                "status": "success" if success else "failure"
            })
            
            # Notification latency
            if success:
                await self._record_prometheus_histogram("notification_latency_ms", latency_ms, {
                    "channel": channel
                })
            
            # Update system metrics
            if success:
                current_latency = self._system_metrics.notification_delivery_latency_ms
                self._system_metrics.notification_delivery_latency_ms = (current_latency + latency_ms) / 2
            else:
                # Update failure rate
                total_notifications = await self._get_counter_value("notifications_sent_total")
                failed_notifications = await self._get_counter_value("notifications_sent_total", {"status": "failure"})
                self._system_metrics.notification_failure_rate_percent = (failed_notifications / total_notifications) * 100
            
        except Exception as e:
            logger.error(f"Failed to record notification metrics: {e}")

    async def record_escalation(self, alert_id: str, from_level: str, to_level: str, reason: str):
        """Record escalation metrics."""



        try:
            await self._increment_prometheus_counter("alert_escalations_total", {
                "from_level": from_level,
                "to_level": to_level,
                "reason": reason
            })
            
            metric = AlertMetric(
                timestamp=datetime.now(timezone.utc),
                alert_id=alert_id,
                metric_name="alert_escalated",
                value=1,
                labels={
                    "from_level": from_level,
                    "to_level": to_level,
                    "reason": reason
                }
            )
            
            self._metric_buffer.append(metric)
            
        except Exception as e:
            logger.error(f"Failed to record escalation metrics: {e}")

    async def record_evidence_collected(self, alert_id: str, evidence_type: str, collection_time_ms: float, success: bool):
        """Record evidence collection metrics."""



        try:
            await self._increment_prometheus_counter("evidence_collection_total", {
                "type": evidence_type,
                "status": "success" if success else "failure"
            })
            
            if success:
                await self._record_prometheus_histogram("evidence_collection_time_ms", collection_time_ms, {
                    "type": evidence_type
                })
                
                # Update system metrics
                current_time = self._system_metrics.evidence_collection_time_ms
                self._system_metrics.evidence_collection_time_ms = (current_time + collection_time_ms) / 2
            
            metric = AlertMetric(
                timestamp=datetime.now(timezone.utc),
                alert_id=alert_id,
                metric_name="evidence_collected",
                value=collection_time_ms if success else 0,
                labels={
                    "type": evidence_type,
                    "status": "success" if success else "failure"
                }
            )
            
            self._metric_buffer.append(metric)
            
        except Exception as e:
            logger.error(f"Failed to record evidence collection metrics: {e}")

    async def record_timing(self, operation: str, duration_seconds: float):
        """Record operation timing."""



        try:
            await self._record_prometheus_histogram(f"{operation}_duration_seconds", duration_seconds)
            
            # Update system metrics based on operation type
            if operation == "alert_processing":
                self._system_metrics.alert_processing_latency_ms = duration_seconds * 1000
            
            self._operation_timers[operation] = duration_seconds
            
        except Exception as e:
            logger.error(f"Failed to record timing for {operation}: {e}")

    async def record_error(self, error_type: str, error_details: Dict[str, Any] = None):
        """Record error metrics."""



        try:
            await self._increment_prometheus_counter("errors_total", {
                "type": error_type
            })
            
            self._error_counters[error_type] += 1
            
            # Update error rates
            if error_type.startswith("api_"):
                total_requests = await self._get_counter_value("api_requests_total")
                total_errors = await self._get_counter_value("errors_total", {"type": error_type})
                if total_requests > 0:
                    self._system_metrics.api_error_rate_percent = (total_errors / total_requests) * 100
            
        except Exception as e:
            logger.error(f"Failed to record error metrics: {e}")

    async def record_security_event(self, event_type: str, severity: str, details: Dict[str, Any] = None):
        """Record security-related metrics."""



        try:
            await self._increment_prometheus_counter("security_events_total", {
                "type": event_type,
                "severity": severity
            })
            
            # Update security metrics
            if event_type == "suspicious_activity":
                self._security_metrics.suspicious_activities_detected += 1
            elif event_type == "failed_authentication":
                self._security_metrics.failed_authentication_attempts += 1
            elif event_type == "ip_blocked":
                self._security_metrics.blocked_ip_addresses += 1
            
        except Exception as e:
            logger.error(f"Failed to record security event metrics: {e}")

    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get current real-time metrics."""



        try:
            return {
                "business_metrics": self._business_metrics.dict(),
                "system_metrics": self._system_metrics.dict(),
                "security_metrics": self._security_metrics.dict(),
                "real_time_counters": self._real_time_metrics.copy(),
                "error_counters": dict(self._error_counters),
                "operation_timers": self._operation_timers.copy(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get real-time metrics: {e}")
            return {}

    async def get_historical_metrics(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        aggregation_interval: int = 300  # 5 minutes
    ) -> List[Dict[str, Any]]:
        """Get historical metrics with aggregation."""



        try:
            # Get metrics from Redis
            metrics_key = f"alert_metrics:{metric_name}"
            
            # Time series data
            start_timestamp = int(start_time.timestamp())
            end_timestamp = int(end_time.timestamp())
            
            raw_data = await self.redis_client.zrangebyscore(
                metrics_key,
                start_timestamp,
                end_timestamp,
                withscores=True
            )
            
            # Aggregate data
            aggregated = []
            current_bucket = start_timestamp
            bucket_values = []
            
            for data, timestamp in raw_data:
                if timestamp >= current_bucket + aggregation_interval:
                    # Finish current bucket
                    if bucket_values:
                        aggregated.append({
                            "timestamp": datetime.fromtimestamp(current_bucket, tz=timezone.utc).isoformat(),
                            "value": statistics.mean(bucket_values),
                            "count": len(bucket_values),
                            "min": min(bucket_values),
                            "max": max(bucket_values)
                        })
                    
                    # Start new bucket
                    current_bucket = int(timestamp // aggregation_interval) * aggregation_interval
                    bucket_values = []
                
                try:
                    metric_data = json.loads(data)
                    bucket_values.append(metric_data.get("value", 0))
                except json.JSONDecodeError:
                    continue
            
            # Handle last bucket
            if bucket_values:
                aggregated.append({
                    "timestamp": datetime.fromtimestamp(current_bucket, tz=timezone.utc).isoformat(),
                    "value": statistics.mean(bucket_values),
                    "count": len(bucket_values),
                    "min": min(bucket_values),
                    "max": max(bucket_values)
                })
            
            return aggregated
            
        except Exception as e:
            logger.error(f"Failed to get historical metrics: {e}")
            return []

    async def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the last N hours."""



        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=hours)
            
            # Get key performance metrics
            alert_creation_metrics = await self.get_historical_metrics("alert_created", start_time, end_time)
            alert_resolution_metrics = await self.get_historical_metrics("alert_resolved", start_time, end_time)
            
            # Calculate performance indicators
            total_alerts = sum(m["count"] for m in alert_creation_metrics)
            total_resolved = sum(m["count"] for m in alert_resolution_metrics)
            
            resolution_times = [m["value"] for m in alert_resolution_metrics if m["value"] > 0]
            avg_resolution_time = statistics.mean(resolution_times) if resolution_times else 0
            
            # Calculate throughput
            alerts_per_hour = total_alerts / hours if hours > 0 else 0
            
            # Get error rates
            total_errors = sum(self._error_counters.values())
            error_rate = (total_errors / max(total_alerts, 1)) * 100
            
            return {
                "period_hours": hours,
                "total_alerts_created": total_alerts,
                "total_alerts_resolved": total_resolved,
                "resolution_rate_percent": (total_resolved / max(total_alerts, 1)) * 100,
                "average_resolution_time_minutes": avg_resolution_time / 60 if avg_resolution_time > 0 else 0,
                "alerts_per_hour": alerts_per_hour,
                "error_rate_percent": error_rate,
                "system_health_score": self._calculate_health_score(),
                "recommendations": await self._generate_performance_recommendations()
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            return {}

    async def export_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format."""



        try:
            return generate_latest(self.prometheus_registry).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to export Prometheus metrics: {e}")
            return ""

    def _initialize_metrics(self):
        """Initialize Prometheus metrics."""
        # Alert metrics
        self._prometheus_metrics["alerts_created_total"] = Counter(
            "alerts_created_total", 
            "Total number of alerts created",
            ["severity", "category", "platform"],
            registry=self.prometheus_registry
        )
        
        self._prometheus_metrics["alerts_resolved_total"] = Counter(
            "alerts_resolved_total",
            "Total number of alerts resolved", 
            ["severity", "category", "resolution_type"],
            registry=self.prometheus_registry
        )
        
        self._prometheus_metrics["alert_resolution_time_seconds"] = Histogram(
            "alert_resolution_time_seconds",
            "Time taken to resolve alerts",
            ["severity", "category"],
            buckets=[1, 5, 10, 30, 60, 300, 600, 1800, 3600],
            registry=self.prometheus_registry
        )
        
        # Notification metrics
        self._prometheus_metrics["notifications_sent_total"] = Counter(
            "notifications_sent_total",
            "Total notifications sent",
            ["channel", "status"],
            registry=self.prometheus_registry
        )
        
        self._prometheus_metrics["notification_latency_ms"] = Histogram(
            "notification_latency_ms",
            "Notification delivery latency",
            ["channel"],
            buckets=[10, 50, 100, 500, 1000, 5000, 10000],
            registry=self.prometheus_registry
        )
        
        # System metrics
        self._prometheus_metrics["alert_processing_latency_ms"] = Gauge(
            "alert_processing_latency_ms",
            "Current alert processing latency",
            registry=self.prometheus_registry
        )
        
        self._prometheus_metrics["active_alerts"] = Gauge(
            "active_alerts",
            "Number of currently active alerts",
            registry=self.prometheus_registry
        )

    async def _increment_prometheus_counter(self, metric_name: str, labels: Dict[str, str] = None):
        """Increment Prometheus counter."""
        if metric_name in self._prometheus_metrics:
            if labels:
                self._prometheus_metrics[metric_name].labels(**labels).inc()
            else:
                self._prometheus_metrics[metric_name].inc()

    async def _record_prometheus_histogram(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Record value in Prometheus histogram."""
        if metric_name in self._prometheus_metrics:
            if labels:
                self._prometheus_metrics[metric_name].labels(**labels).observe(value)
            else:
                self._prometheus_metrics[metric_name].observe(value)

    async def _update_real_time_metrics(self, metric_name: str, value: Union[int, float]):
        """Update real-time metrics."""
        if metric_name not in self._real_time_metrics:
            self._real_time_metrics[metric_name] = 0
        
        self._real_time_metrics[metric_name] += value

    async def _get_counter_value(self, metric_name: str, labels: Dict[str, str] = None) -> float:
        """Get current value of a Prometheus counter."""



        try:
            if metric_name in self._prometheus_metrics:
                if labels:
                    return self._prometheus_metrics[metric_name].labels(**labels)._value._value
                else:
                    return self._prometheus_metrics[metric_name]._value._value
            return 0.0
        except:
            return 0.0

    async def _load_historical_metrics(self):
        """Load historical metrics from storage."""



        try:
            # Load from Redis
            keys = await self.redis_client.keys("alert_metrics:*")
            
            for key in keys:
                # Get recent data for initialization
                recent_data = await self.redis_client.zrevrange(key, 0, 100, withscores=True)
                
                # Process for real-time metrics initialization
                for data, timestamp in recent_data:
                    try:
                        metric_data = json.loads(data)
                        # Update real-time counters based on recent data
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            logger.error(f"Failed to load historical metrics: {e}")

    async def _metrics_aggregation_loop(self):
        """Background loop for metrics aggregation."""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute
                
                # Process buffered metrics
                await self._process_metric_buffer()
                
                # Aggregate metrics
                await self._aggregate_metrics()
                
                # Update derived metrics
                await self._update_derived_metrics()
                
            except Exception as e:
                logger.error(f"Metrics aggregation loop error: {e}")

    async def _metrics_cleanup_loop(self):
        """Background loop for metrics cleanup."""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Clean old metrics
                await self._cleanup_old_metrics()
                
            except Exception as e:
                logger.error(f"Metrics cleanup loop error: {e}")

    async def _process_metric_buffer(self):
        """Process metrics from buffer to persistent storage."""
        if not self._metric_buffer:
            return
        
        try:
            # Batch process buffered metrics
            metrics_to_process = []
            while self._metric_buffer and len(metrics_to_process) < 100:
                metrics_to_process.append(self._metric_buffer.popleft())
            
            # Store in Redis time series
            for metric in metrics_to_process:
                await self._store_metric_in_redis(metric)
                
        except Exception as e:
            logger.error(f"Failed to process metric buffer: {e}")

    async def _store_metric_in_redis(self, metric: AlertMetric):
        """Store individual metric in Redis time series."""



        try:
            metrics_key = f"alert_metrics:{metric.metric_name}"
            timestamp = int(metric.timestamp.timestamp())
            
            metric_data = {
                "alert_id": metric.alert_id,
                "value": metric.value,
                "labels": metric.labels,
                "metadata": metric.metadata
            }
            
            await self.redis_client.zadd(
                metrics_key,
                {json.dumps(metric_data): timestamp}
            )
            
            # Set expiration for cleanup
            await self.redis_client.expire(metrics_key, 86400 * 30)  # 30 days
            
        except Exception as e:
            logger.error(f"Failed to store metric in Redis: {e}")

    async def _aggregate_metrics(self):
        """Aggregate metrics for different time periods."""



        try:
            # Aggregate hourly, daily, weekly metrics
            now = datetime.now(timezone.utc)
            
            # Hourly aggregation
            await self._aggregate_time_period("hourly", now, timedelta(hours=1))
            
            # Daily aggregation (run once per hour)
            if now.minute == 0:
                await self._aggregate_time_period("daily", now, timedelta(days=1))
            
            # Weekly aggregation (run once per day)
            if now.hour == 0 and now.minute == 0:
                await self._aggregate_time_period("weekly", now, timedelta(weeks=1))
                
        except Exception as e:
            logger.error(f"Failed to aggregate metrics: {e}")

    async def _aggregate_time_period(self, period: str, end_time: datetime, duration: timedelta):
        """Aggregate metrics for a specific time period."""
        start_time = end_time - duration
        
        # Get all metric types
        metric_keys = await self.redis_client.keys("alert_metrics:*")
        
        for key in metric_keys:
            metric_name = key.decode().replace("alert_metrics:", "")
            
            # Get data for time period
            start_timestamp = int(start_time.timestamp())
            end_timestamp = int(end_time.timestamp())
            
            data = await self.redis_client.zrangebyscore(
                key, start_timestamp, end_timestamp, withscores=True
            )
            
            if data:
                # Calculate aggregations
                values = []
                for item, timestamp in data:
                    try:
                        metric_data = json.loads(item)
                        values.append(metric_data["value"])
                    except:
                        continue
                
                if values:
                    aggregation = {
                        "count": len(values),
                        "sum": sum(values),
                        "avg": statistics.mean(values),
                        "min": min(values),
                        "max": max(values),
                        "median": statistics.median(values)
                    }
                    
                    # Store aggregation
                    agg_key = f"alert_metrics_agg:{period}:{metric_name}"
                    agg_data = {
                        "period_start": start_time.isoformat(),
                        "period_end": end_time.isoformat(),
                        "aggregation": aggregation
                    }
                    
                    await self.redis_client.zadd(
                        agg_key,
                        {json.dumps(agg_data): end_timestamp}
                    )

    async def _update_derived_metrics(self):
        """Update derived and calculated metrics."""



        try:
            # Update business metrics calculations
            await self._update_business_metrics()
            
            # Update system health score
            self._system_metrics.cpu_usage_percent = await self._get_system_cpu_usage()
            self._system_metrics.memory_usage_percent = await self._get_system_memory_usage()
            
        except Exception as e:
            logger.error(f"Failed to update derived metrics: {e}")

    async def _update_business_metrics(self):
        """Update business-related metrics."""



        try:
            # Calculate automation rate
            total_alerts = self._business_metrics.total_alerts_created
            manual_interventions = self._business_metrics.manual_intervention_required
            
            if total_alerts > 0:
                automation_rate = ((total_alerts - manual_interventions) / total_alerts) * 100
                self._business_metrics.automation_rate_percent = automation_rate
            
            # Calculate detection accuracy
            total_resolved = self._business_metrics.total_alerts_resolved
            false_positives = await self._get_false_positive_count()
            
            if total_resolved > 0:
                accuracy = ((total_resolved - false_positives) / total_resolved) * 100
                self._business_metrics.detection_accuracy_percent = accuracy
                self._business_metrics.false_positive_rate_percent = (false_positives / total_resolved) * 100
                
        except Exception as e:
            logger.error(f"Failed to update business metrics: {e}")

    async def _cleanup_old_metrics(self):
        """Clean up old metrics to manage storage."""



        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=30)
            cutoff_timestamp = int(cutoff_time.timestamp())
            
            # Clean time series data
            metric_keys = await self.redis_client.keys("alert_metrics:*")
            
            for key in metric_keys:
                await self.redis_client.zremrangebyscore(key, 0, cutoff_timestamp)
                
        except Exception as e:
            logger.error(f"Failed to cleanup old metrics: {e}")

    def _calculate_health_score(self) -> float:
        """Calculate overall system health score (0-100)."""



        try:
            scores = []
            
            # Error rate score (lower is better)
            total_errors = sum(self._error_counters.values())
            total_operations = max(self._business_metrics.total_alerts_created, 1)
            error_rate = total_errors / total_operations
            error_score = max(0, 100 - (error_rate * 1000))  # Scale error rate
            scores.append(error_score)
            
            # Resolution rate score
            if self._business_metrics.total_alerts_created > 0:
                resolution_rate = self._business_metrics.total_alerts_resolved / self._business_metrics.total_alerts_created
                resolution_score = resolution_rate * 100
                scores.append(resolution_score)
            
            # Detection accuracy score
            accuracy_score = self._business_metrics.detection_accuracy_percent
            scores.append(accuracy_score)
            
            # System performance score
            latency_score = max(0, 100 - (self._system_metrics.alert_processing_latency_ms / 10))
            scores.append(latency_score)
            
            # Calculate weighted average
            if scores:
                return sum(scores) / len(scores)
            
            return 50.0  # Neutral score if no data
            
        except Exception as e:
            logger.error(f"Failed to calculate health score: {e}")
            return 0.0

    async def _generate_performance_recommendations(self) -> List[str]:
        """Generate performance improvement recommendations."""
        recommendations = []
        
        try:
            # Check error rates
            if self._system_metrics.api_error_rate_percent > 5:
                recommendations.append("High API error rate detected - review error handling and validation")
            
            # Check resolution times
            if self._business_metrics.average_resolution_time_minutes > 60:
                recommendations.append("Average resolution time is high - consider automation improvements")
            
            # Check false positive rate
            if self._business_metrics.false_positive_rate_percent > 10:
                recommendations.append("High false positive rate - review ML model accuracy and thresholds")
            
            # Check notification failures
            if self._system_metrics.notification_failure_rate_percent > 2:
                recommendations.append("Notification delivery issues detected - check external service integrations")
            
            # Check system resources
            if self._system_metrics.cpu_usage_percent > 80:
                recommendations.append("High CPU usage - consider scaling or optimization")
            
            if self._system_metrics.memory_usage_percent > 85:
                recommendations.append("High memory usage - review memory management and caching")
            
            # Check automation rate
            if self._business_metrics.automation_rate_percent < 80:
                recommendations.append("Low automation rate - identify manual processes for automation")
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
        
        return recommendations if recommendations else ["System is performing well - no immediate recommendations"]

    async def _get_false_positive_count(self) -> int:
        """Get count of false positive alerts."""
        # This would integrate with your alert data to count false positives
        # Implementation depends on how false positives are marked
        return 0

    async def _get_system_cpu_usage(self) -> float:
        """Get current system CPU usage."""
        # Implementation would use system monitoring tools
        return 0.0

    async def _get_system_memory_usage(self) -> float:
        """Get current system memory usage."""
        # Implementation would use system monitoring tools
        return 0.0


# Export classes
__all__ = [
    "MetricType",
    "MetricScope", 
    "MetricDefinition",
    "AlertMetric",
    "BusinessMetrics",
    "SystemPerformanceMetrics",
    "SecurityMetrics",
    "AlertMetricsCollector"
]
