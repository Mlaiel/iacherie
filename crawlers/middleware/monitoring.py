"""
Monitoring Middleware Module
===========================

Enterprise-grade monitoring middleware for crawler pipeline.
Implements comprehensive monitoring, metrics collection, and alerting.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Business Logic Monitoring:
- Multi-format content processing performance tracking
- Creator engagement and monetization metrics
- AI protection system effectiveness monitoring  
- Cross-platform distribution success rates
- Real-time threat detection and security metrics
"""

import asyncio
import json
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from enum import Enum
import redis
from pydantic import BaseModel, Field
import logging
import statistics
import threading
from dataclasses import dataclass
from collections import defaultdict, deque

from ...config.settings import get_settings
from ...utils.cache import CacheManager

settings = get_settings()
logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMING = "timing"
    RATE = "rate"
    PERCENTAGE = "percentage"


class AlertLevel(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"
    SYSTEM_DOWN = "system_down"


class BusinessMetricType(str, Enum):
    """Business-specific metric types"""
    CONTENT_PROCESSING = "content_processing"
    CREATOR_ENGAGEMENT = "creator_engagement"
    MONETIZATION = "monetization"
    PROTECTION_EFFECTIVENESS = "protection_effectiveness"
    COLLABORATION_SUCCESS = "collaboration_success"
    PLATFORM_DISTRIBUTION = "platform_distribution"


class MonitoringEvent(BaseModel):
    """Enhanced monitoring event model"""
    event_id: str = Field(description="Unique event identifier")
    event_type: str = Field(description="Type of event")
    timestamp: datetime = Field(description="Event timestamp")
    source: str = Field(description="Event source")
    user_id: Optional[str] = Field(None, description="Associated user ID")
    content_id: Optional[str] = Field(None, description="Associated content ID")
    business_context: Optional[BusinessMetricType] = Field(None, description="Business context")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Event metadata")
    duration: Optional[float] = Field(None, description="Event duration")
    status: str = Field(description="Event status")
    performance_impact: Optional[float] = Field(None, description="Performance impact score")


class MetricData(BaseModel):
    """Enhanced metric data model"""
    name: str = Field(description="Metric name")
    value: Union[int, float] = Field(description="Metric value")
    metric_type: MetricType = Field(description="Type of metric")
    business_type: Optional[BusinessMetricType] = Field(None, description="Business metric type")
    timestamp: datetime = Field(description="Metric timestamp")
    tags: Dict[str, str] = Field(default_factory=dict, description="Metric tags")
    labels: Dict[str, str] = Field(default_factory=dict, description="Metric labels")
    dimensions: Dict[str, Any] = Field(default_factory=dict, description="Additional dimensions")


class AlertRule(BaseModel):
    """Enhanced alert rule configuration"""
    rule_id: str = Field(description="Unique rule identifier")
    metric_name: str = Field(description="Metric to monitor")
    condition: str = Field(description="Alert condition (>, <, ==, etc.)")
    threshold: float = Field(description="Alert threshold value")
    duration: int = Field(description="Duration in seconds")
    severity: AlertLevel = Field(description="Alert severity")
    description: str = Field(description="Alert description")
    business_impact: str = Field(description="Business impact description")
    auto_remediation: Optional[str] = Field(None, description="Auto-remediation action")
    escalation_path: List[str] = Field(default_factory=list, description="Escalation contacts")
    enabled: bool = Field(default=True, description="Whether rule is enabled")


@dataclass
class MetricBuffer:
    """Thread-safe metric buffer for high-performance collection"""
    values: deque
    timestamps: deque
    max_size: int = 1000
    
    def __post_init__(self):
        self.values = deque(maxlen=self.max_size)
        self.timestamps = deque(maxlen=self.max_size)
        self.lock = threading.RLock()
    
    def add(self, value: float, timestamp: datetime = None):
        with self.lock:
            self.values.append(value)
            self.timestamps.append(timestamp or datetime.utcnow())
    
    def get_stats(self) -> Dict[str, float]:
        with self.lock:
            if not self.values:
                return {}
            
            values_list = list(self.values)
            return {
                "count": len(values_list),
                "sum": sum(values_list),
                "avg": statistics.mean(values_list),
                "min": min(values_list),
                "max": max(values_list),
                "median": statistics.median(values_list),
                "std_dev": statistics.stdev(values_list) if len(values_list) > 1 else 0
            }


class PerformanceMonitor:
    """Advanced system and business performance monitoring"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.cache = CacheManager()
        self.metric_buffers = defaultdict(MetricBuffer)
        self.business_metrics = defaultdict(MetricBuffer)
        
    async def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system metrics"""
        metrics = {}
        
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            metrics["cpu"] = {
                "usage_percent": cpu_percent,
                "core_count": cpu_count,
                "frequency_mhz": cpu_freq.current if cpu_freq else 0,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            }
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            metrics["memory"] = {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "usage_percent": memory.percent,
                "swap_total_gb": round(swap.total / (1024**3), 2),
                "swap_used_gb": round(swap.used / (1024**3), 2),
                "swap_percent": swap.percent
            }
            
            # Disk metrics
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            metrics["disk"] = {
                "total_gb": round(disk_usage.total / (1024**3), 2),
                "used_gb": round(disk_usage.used / (1024**3), 2),
                "free_gb": round(disk_usage.free / (1024**3), 2),
                "usage_percent": (disk_usage.used / disk_usage.total) * 100,
                "read_count": disk_io.read_count if disk_io else 0,
                "write_count": disk_io.write_count if disk_io else 0,
                "read_bytes": disk_io.read_bytes if disk_io else 0,
                "write_bytes": disk_io.write_bytes if disk_io else 0
            }
            
            # Network metrics
            network_io = psutil.net_io_counters()
            network_connections = len(psutil.net_connections())
            
            metrics["network"] = {
                "bytes_sent": network_io.bytes_sent,
                "bytes_recv": network_io.bytes_recv,
                "packets_sent": network_io.packets_sent,
                "packets_recv": network_io.packets_recv,
                "connections_count": network_connections
            }
            
            # Process metrics
            process = psutil.Process()
            
            metrics["process"] = {
                "cpu_percent": process.cpu_percent(),
                "memory_mb": round(process.memory_info().rss / (1024**2), 2),
                "memory_percent": process.memory_percent(),
                "num_threads": process.num_threads(),
                "num_fds": process.num_fds() if hasattr(process, 'num_fds') else 0,
                "create_time": process.create_time()
            }
            
            # Add timestamp
            metrics["timestamp"] = datetime.utcnow().isoformat()
            
            return metrics
            
        except Exception as e:
            logger.error(f"System metrics collection error: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}
    
    async def collect_application_metrics(self) -> Dict[str, Any]:
        """Collect application-specific metrics"""
        metrics = {}
        
        try:
            # Redis metrics
            redis_info = await self.get_redis_metrics()
            metrics["redis"] = redis_info
            
            # Cache metrics
            cache_stats = await self.get_cache_metrics()
            metrics["cache"] = cache_stats
            
            # Request metrics
            request_stats = await self.get_request_metrics()
            metrics["requests"] = request_stats
            
            # Error metrics
            error_stats = await self.get_error_metrics()
            metrics["errors"] = error_stats
            
            return metrics
            
        except Exception as e:
            logger.error(f"Application metrics collection error: {e}")
            return {"error": str(e)}
    
    async def get_redis_metrics(self) -> Dict[str, Any]:
        """Get Redis performance metrics"""



        try:
            info = self.redis_client.info()
            
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_mb": round(info.get("used_memory", 0) / (1024**2), 2),
                "used_memory_peak_mb": round(info.get("used_memory_peak", 0) / (1024**2), 2),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "expired_keys": info.get("expired_keys", 0),
                "evicted_keys": info.get("evicted_keys", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "instantaneous_ops_per_sec": info.get("instantaneous_ops_per_sec", 0)
            }
            
        except Exception as e:
            logger.error(f"Redis metrics error: {e}")
            return {"error": str(e)}
    
    async def get_cache_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics"""



        try:
            # Get cache statistics from Redis
            cache_hits = await self.redis_client.get("cache:hits") or 0
            cache_misses = await self.redis_client.get("cache:misses") or 0
            cache_sets = await self.redis_client.get("cache:sets") or 0
            
            total_requests = int(cache_hits) + int(cache_misses)
            hit_rate = (int(cache_hits) / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "hits": int(cache_hits),
                "misses": int(cache_misses),
                "sets": int(cache_sets),
                "hit_rate_percent": round(hit_rate, 2),
                "total_requests": total_requests
            }
            
        except Exception as e:
            logger.error(f"Cache metrics error: {e}")
            return {"error": str(e)}
    
    async def get_request_metrics(self) -> Dict[str, Any]:
        """Get request processing metrics"""



        try:
            now = time.time()
            hour_window = int(now // 3600)
            
            # Get request counts for current hour
            total_requests = await self.redis_client.get(f"requests:total:{hour_window}") or 0
            successful_requests = await self.redis_client.get(f"requests:success:{hour_window}") or 0
            failed_requests = await self.redis_client.get(f"requests:failed:{hour_window}") or 0
            
            # Calculate success rate
            success_rate = (int(successful_requests) / int(total_requests) * 100) if int(total_requests) > 0 else 0
            
            # Get average response time
            total_response_time = await self.redis_client.get(f"response_time:total:{hour_window}") or 0
            avg_response_time = (float(total_response_time) / int(total_requests)) if int(total_requests) > 0 else 0
            
            return {
                "total_requests": int(total_requests),
                "successful_requests": int(successful_requests),
                "failed_requests": int(failed_requests),
                "success_rate_percent": round(success_rate, 2),
                "average_response_time_ms": round(avg_response_time, 2)
            }
            
        except Exception as e:
            logger.error(f"Request metrics error: {e}")
            return {"error": str(e)}
    
    async def get_error_metrics(self) -> Dict[str, Any]:
        """Get error and exception metrics"""



        try:
            now = time.time()
            hour_window = int(now // 3600)
            
            # Get error counts by type
            error_types = ["authentication", "rate_limit", "security", "processing", "system"]
            error_counts = {}
            
            for error_type in error_types:
                count = await self.redis_client.get(f"errors:{error_type}:{hour_window}") or 0
                error_counts[f"{error_type}_errors"] = int(count)
            
            # Total errors
            total_errors = sum(error_counts.values())
            
            return {
                **error_counts,
                "total_errors": total_errors
            }
            
        except Exception as e:
            logger.error(f"Error metrics error: {e}")
            return {"error": str(e)}


class AlertManager:
    """Alert management and notification system"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.cache = CacheManager()
        self.alert_rules = []
        
    async def load_alert_rules(self) -> List[AlertRule]:
        """Load alert rules from configuration"""
        # Default alert rules
        default_rules = [
            AlertRule(
                rule_id="cpu_high",
                metric_name="cpu.usage_percent",
                condition=">",
                threshold=85.0,
                duration=300,  # 5 minutes
                severity=AlertLevel.WARNING,
                description="High CPU usage detected"
            ),
            AlertRule(
                rule_id="cpu_critical",
                metric_name="cpu.usage_percent",
                condition=">",
                threshold=95.0,
                duration=60,  # 1 minute
                severity=AlertLevel.CRITICAL,
                description="Critical CPU usage detected"
            ),
            AlertRule(
                rule_id="memory_high",
                metric_name="memory.usage_percent",
                condition=">",
                threshold=85.0,
                duration=300,
                severity=AlertLevel.WARNING,
                description="High memory usage detected"
            ),
            AlertRule(
                rule_id="memory_critical",
                metric_name="memory.usage_percent",
                condition=">",
                threshold=95.0,
                duration=60,
                severity=AlertLevel.CRITICAL,
                description="Critical memory usage detected"
            ),
            AlertRule(
                rule_id="disk_high",
                metric_name="disk.usage_percent",
                condition=">",
                threshold=85.0,
                duration=600,  # 10 minutes
                severity=AlertLevel.WARNING,
                description="High disk usage detected"
            ),
            AlertRule(
                rule_id="error_rate_high",
                metric_name="requests.success_rate_percent",
                condition="<",
                threshold=95.0,
                duration=300,
                severity=AlertLevel.WARNING,
                description="High error rate detected"
            )
        ]
        
        self.alert_rules = default_rules
        return default_rules
    
    async def evaluate_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate metrics against alert rules"""
        alerts = []
        
        for rule in self.alert_rules:
            if not rule.enabled:
                continue
                
            try:
                # Extract metric value from nested dictionary
                metric_value = self.get_nested_value(metrics, rule.metric_name)
                
                if metric_value is None:
                    continue
                
                # Evaluate condition
                triggered = self.evaluate_condition(metric_value, rule.condition, rule.threshold)
                
                if triggered:
                    # Check if alert should be suppressed (already fired recently)
                    if not await self.should_suppress_alert(rule.rule_id, rule.duration):
                        alert = await self.create_alert(rule, metric_value, metrics)
                        alerts.append(alert)
                        
                        # Record alert firing
                        await self.record_alert_firing(rule.rule_id)
                
            except Exception as e:
                logger.error(f"Alert evaluation error for rule {rule.rule_id}: {e}")
        
        return alerts
    
    def get_nested_value(self, data: Dict[str, Any], key_path: str) -> Optional[Union[int, float]]:
        """Get value from nested dictionary using dot notation"""
        keys = key_path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value if isinstance(value, (int, float)) else None
    
    def evaluate_condition(self, value: Union[int, float], condition: str, threshold: float) -> bool:
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
            return value == threshold
        elif condition == "!=":
            return value != threshold
        else:
            return False
    
    async def should_suppress_alert(self, rule_id: str, duration: int) -> bool:
        """Check if alert should be suppressed to avoid spam"""
        alert_key = f"alert_fired:{rule_id}"
        last_fired = await self.redis_client.get(alert_key)
        
        if last_fired:
            last_fired_time = float(last_fired)
            if time.time() - last_fired_time < duration:
                return True  # Suppress alert
        
        return False
    
    async def create_alert(self, rule: AlertRule, metric_value: Union[int, float], 
                         metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create alert object"""
        alert = {
            "alert_id": f"{rule.rule_id}_{int(time.time())}",
            "rule_id": rule.rule_id,
            "severity": rule.severity.value,
            "title": rule.description,
            "message": f"{rule.description}. Current value: {metric_value}, Threshold: {rule.threshold}",
            "metric_name": rule.metric_name,
            "metric_value": metric_value,
            "threshold": rule.threshold,
            "condition": rule.condition,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "active",
            "context": {
                "system_metrics": metrics.get("cpu", {}),
                "memory_metrics": metrics.get("memory", {}),
                "disk_metrics": metrics.get("disk", {})
            }
        }
        
        return alert
    
    async def record_alert_firing(self, rule_id: str):
        """Record when an alert was fired"""
        alert_key = f"alert_fired:{rule_id}"
        await self.redis_client.set(alert_key, str(time.time()), ex=3600)  # 1 hour expiry
    
    async def send_alert(self, alert: Dict[str, Any]):
        """Send alert notification"""



        try:
            # Log alert
            logger.warning(f"ALERT: {alert['title']} - {alert['message']}")
            
            # Store alert in Redis for dashboard
            alert_key = f"alerts:{alert['alert_id']}"
            await self.redis_client.set(alert_key, json.dumps(alert), ex=86400)  # 24 hours
            
            # Add to active alerts list
            await self.redis_client.lpush("active_alerts", json.dumps(alert))
            await self.redis_client.ltrim("active_alerts", 0, 100)  # Keep last 100 alerts
            
            # Send notification based on severity
            if alert["severity"] in ["critical", "emergency"]:
                await self.send_critical_alert_notification(alert)
            else:
                await self.send_standard_alert_notification(alert)
                
        except Exception as e:
            logger.error(f"Alert sending error: {e}")
    
    async def send_critical_alert_notification(self, alert: Dict[str, Any]):
        """Send critical alert notification"""
        # In production, this would integrate with:
        # - Email/SMS services
        # - Slack/Teams webhooks
        # - PagerDuty/OpsGenie
        logger.critical(f"CRITICAL ALERT: {alert['message']}")
    
    async def send_standard_alert_notification(self, alert: Dict[str, Any]):
        """Send standard alert notification"""
        # In production, this would send to monitoring dashboards
        logger.warning(f"ALERT: {alert['message']}")


class MetricsCollector:
    """Comprehensive metrics collection and storage"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.cache = CacheManager()
        
    async def record_metric(self, metric: MetricData):
        """Record a single metric"""



        try:
            # Create metric key
            metric_key = f"metrics:{metric.name}:{int(metric.timestamp.timestamp())}"
            
            # Store metric data
            metric_data = {
                "value": metric.value,
                "type": metric.metric_type.value,
                "tags": json.dumps(metric.tags),
                "labels": json.dumps(metric.labels),
                "timestamp": metric.timestamp.isoformat()
            }
            
            await self.redis_client.hmset(metric_key, metric_data)
            await self.redis_client.expire(metric_key, 86400 * 7)  # Keep for 7 days
            
            # Update metric series
            series_key = f"metric_series:{metric.name}"
            await self.redis_client.zadd(series_key, {metric_key: metric.timestamp.timestamp()})
            await self.redis_client.expire(series_key, 86400 * 7)
            
        except Exception as e:
            logger.error(f"Metric recording error: {e}")
    
    async def record_event(self, event: MonitoringEvent):
        """Record a monitoring event"""



        try:
            # Store event
            event_key = f"events:{event.event_id}"
            event_data = {
                "event_type": event.event_type,
                "timestamp": event.timestamp.isoformat(),
                "source": event.source,
                "metadata": json.dumps(event.metadata),
                "duration": event.duration or 0,
                "status": event.status
            }
            
            await self.redis_client.hmset(event_key, event_data)
            await self.redis_client.expire(event_key, 86400 * 30)  # Keep for 30 days
            
            # Add to event timeline
            timeline_key = f"timeline:{event.event_type}"
            await self.redis_client.zadd(timeline_key, {event_key: event.timestamp.timestamp()})
            await self.redis_client.expire(timeline_key, 86400 * 30)
            
        except Exception as e:
            logger.error(f"Event recording error: {e}")
    
    async def get_metric_history(self, metric_name: str, 
                               start_time: datetime, 
                               end_time: datetime) -> List[Dict[str, Any]]:
        """Get metric history for time range"""



        try:
            series_key = f"metric_series:{metric_name}"
            
            # Get metric keys in time range
            metric_keys = await self.redis_client.zrangebyscore(
                series_key, 
                start_time.timestamp(), 
                end_time.timestamp()
            )
            
            metrics = []
            for key in metric_keys:
                metric_data = await self.redis_client.hgetall(key)
                if metric_data:
                    metrics.append({
                        "timestamp": metric_data[b"timestamp"].decode(),
                        "value": float(metric_data[b"value"]),
                        "type": metric_data[b"type"].decode(),
                        "tags": json.loads(metric_data[b"tags"]),
                        "labels": json.loads(metric_data[b"labels"])
                    })
            
            return metrics
            
        except Exception as e:
            logger.error(f"Metric history retrieval error: {e}")
            return []


class MonitoringMiddleware:
    """Main monitoring middleware orchestrator"""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.cache = CacheManager()
        
        # Initialize components
        self.performance_monitor = PerformanceMonitor(self.redis_client)
        self.alert_manager = AlertManager(self.redis_client)
        self.metrics_collector = MetricsCollector(self.redis_client)
        
        # Monitoring configuration
        self.monitoring_interval = 60  # seconds
        self.monitoring_enabled = True
        
    async def start_monitoring(self):
        """Start continuous monitoring"""
        if not self.monitoring_enabled:
            return
        
        logger.info("Starting monitoring middleware")
        
        # Load alert rules
        await self.alert_manager.load_alert_rules()
        
        # Start monitoring loop
        asyncio.create_task(self.monitoring_loop())
    
    async def monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_enabled:
            try:
                # Collect metrics
                await self.collect_and_process_metrics()
                
                # Wait for next interval
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(10)  # Short wait on error
    
    async def collect_and_process_metrics(self):
        """Collect metrics and process alerts"""



        try:
            # Collect system metrics
            system_metrics = await self.performance_monitor.collect_system_metrics()
            
            # Collect application metrics
            app_metrics = await self.performance_monitor.collect_application_metrics()
            
            # Combine metrics
            all_metrics = {**system_metrics, **app_metrics}
            
            # Store metrics
            await self.store_metrics(all_metrics)
            
            # Evaluate alerts
            alerts = await self.alert_manager.evaluate_alerts(all_metrics)
            
            # Send alerts
            for alert in alerts:
                await self.alert_manager.send_alert(alert)
                
            # Log monitoring status
            logger.debug(f"Monitoring cycle completed. Metrics collected: {len(all_metrics)}, Alerts: {len(alerts)}")
            
        except Exception as e:
            logger.error(f"Metrics collection and processing error: {e}")
    
    async def store_metrics(self, metrics: Dict[str, Any]):
        """Store collected metrics"""
        timestamp = datetime.utcnow()
        
        # Flatten nested metrics for storage
        flat_metrics = self.flatten_metrics(metrics)
        
        for metric_name, value in flat_metrics.items():
            if isinstance(value, (int, float)):
                metric = MetricData(
                    name=metric_name,
                    value=value,
                    metric_type=MetricType.GAUGE,
                    timestamp=timestamp,
                    tags={"source": "system"},
                    labels={"component": "crawler_middleware"}
                )
                
                await self.metrics_collector.record_metric(metric)
    
    def flatten_metrics(self, metrics: Dict[str, Any], prefix: str = "") -> Dict[str, Union[int, float]]:
        """Flatten nested metrics dictionary"""
        flat = {}
        
        for key, value in metrics.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                flat.update(self.flatten_metrics(value, full_key))
            elif isinstance(value, (int, float)):
                flat[full_key] = value
        
        return flat
    
    async def record_request_metric(self, endpoint: str, duration: float, 
                                  status: str, user_id: Optional[str] = None):
        """Record request processing metrics"""



        try:
            now = time.time()
            hour_window = int(now // 3600)
            
            # Update request counters
            await self.redis_client.incr(f"requests:total:{hour_window}")
            if status == "success":
                await self.redis_client.incr(f"requests:success:{hour_window}")
            else:
                await self.redis_client.incr(f"requests:failed:{hour_window}")
            
            # Update response time
            await self.redis_client.incrbyfloat(f"response_time:total:{hour_window}", duration)
            
            # Set expiration
            await self.redis_client.expire(f"requests:total:{hour_window}", 86400)
            await self.redis_client.expire(f"requests:success:{hour_window}", 86400)
            await self.redis_client.expire(f"requests:failed:{hour_window}", 86400)
            await self.redis_client.expire(f"response_time:total:{hour_window}", 86400)
            
            # Record detailed metric
            metric = MetricData(
                name="request.duration",
                value=duration,
                metric_type=MetricType.TIMING,
                timestamp=datetime.utcnow(),
                tags={"endpoint": endpoint, "status": status},
                labels={"user_id": user_id or "anonymous"}
            )
            
            await self.metrics_collector.record_metric(metric)
            
        except Exception as e:
            logger.error(f"Request metric recording error: {e}")
    
    async def record_error_metric(self, error_type: str, error_message: str, 
                                context: Dict[str, Any] = None):
        """Record error metrics"""



        try:
            now = time.time()
            hour_window = int(now // 3600)
            
            # Update error counter
            await self.redis_client.incr(f"errors:{error_type}:{hour_window}")
            await self.redis_client.expire(f"errors:{error_type}:{hour_window}", 86400)
            
            # Record detailed error event
            event = MonitoringEvent(
                event_id=f"error_{int(now * 1000)}",
                event_type="error",
                timestamp=datetime.utcnow(),
                source="crawler_middleware",
                metadata={
                    "error_type": error_type,
                    "error_message": error_message,
                    "context": context or {}
                },
                status="recorded"
            )
            
            await self.metrics_collector.record_event(event)
            
        except Exception as e:
            logger.error(f"Error metric recording error: {e}")
    
    async def get_monitoring_dashboard_data(self) -> Dict[str, Any]:
        """Get data for monitoring dashboard"""



        try:
            # Get current metrics
            system_metrics = await self.performance_monitor.collect_system_metrics()
            app_metrics = await self.performance_monitor.collect_application_metrics()
            
            # Get recent alerts
            recent_alerts = await self.redis_client.lrange("active_alerts", 0, 10)
            alerts = [json.loads(alert) for alert in recent_alerts]
            
            # Get system status
            status = "healthy"
            if system_metrics.get("cpu", {}).get("usage_percent", 0) > 90:
                status = "critical"
            elif system_metrics.get("cpu", {}).get("usage_percent", 0) > 80:
                status = "warning"
            
            return {
                "system_metrics": system_metrics,
                "application_metrics": app_metrics,
                "recent_alerts": alerts,
                "system_status": status,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Dashboard data retrieval error: {e}")
            return {"error": str(e)}
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_enabled = False
        logger.info("Monitoring middleware stopped")


# Factory function for dependency injection
def get_monitoring_middleware() -> MonitoringMiddleware:
    """Get monitoring middleware instance"""



    return MonitoringMiddleware()


# Decorator for automatic request monitoring
def monitor_request(endpoint: str):
    """Decorator for automatic request monitoring"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"
            error_type = None
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "failed"
                error_type = type(e).__name__
                
                # Record error metric
                middleware = get_monitoring_middleware()
                await middleware.record_error_metric(
                    error_type=error_type,
                    error_message=str(e),
                    context={"endpoint": endpoint, "function": func.__name__}
                )
                
                raise
            finally:
                # Record request metric
                duration = (time.time() - start_time) * 1000  # Convert to milliseconds
                middleware = get_monitoring_middleware()
                await middleware.record_request_metric(
                    endpoint=endpoint,
                    duration=duration,
                    status=status
                )
        
        return wrapper
    return decorator
