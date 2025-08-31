"""
IA Influencer Agent - Advanced Indexing Monitoring
==================================================

Enterprise-grade monitoring and analytics system for indexing operations
with real-time metrics, performance tracking, and alerting capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Content Protection Platform

  INTELLECTUAL PROPERTY WARNING 
This code is the exclusive property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or reproduction
without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
import json
import numpy as np
from collections import defaultdict, deque
import psutil
import GPUtil
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
from redis.asyncio import Redis
import aiofiles

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics collected"""
    COUNTER = "counter"
    HISTOGRAM = "histogram" 
    GAUGE = "gauge"
    TIMER = "timer"


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class PerformanceMetrics:
    """Performance metrics structure"""
    operation_type: str
    processing_time_ms: float
    cpu_usage_percent: float
    memory_usage_mb: float
    gpu_usage_percent: float
    queue_depth: int
    success_count: int
    error_count: int
    timestamp: datetime


@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    metric_name: str
    threshold: float
    comparison: str  # >, <, ==, >=, <=
    window_minutes: int
    level: AlertLevel
    notification_channels: List[str]
    enabled: bool = True


@dataclass
class IndexingMetrics:
    """Indexing operation metrics"""
    content_indexed_total: int
    indexing_rate_per_minute: float
    average_processing_time_ms: float
    success_rate_percent: float
    queue_backlog: int
    storage_usage_gb: float
    vector_index_size: int
    fingerprint_matches_today: int


class MetricsCollector:
    """Collects and aggregates metrics from indexing operations"""
    
    def __init__(self, redis_url: str, collection_interval: int = 60):
        self.redis_url = redis_url
        self.collection_interval = collection_interval
        self.redis_client = None
        self.metrics_buffer = defaultdict(deque)
        self.performance_history = deque(maxlen=1000)
        self.alert_rules = {}
        self.registry = CollectorRegistry()
        self._setup_prometheus_metrics()
        
    def _setup_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.processing_time = Histogram(
            'indexing_processing_time_seconds',
            'Time spent processing content for indexing',
            ['content_type', 'operation'],
            registry=self.registry
        )
        
        self.content_counter = Counter(
            'indexed_content_total',
            'Total number of content items indexed',
            ['content_type', 'creator_id'],
            registry=self.registry
        )
        
        self.error_counter = Counter(
            'indexing_errors_total',
            'Total indexing errors',
            ['error_type', 'operation'],
            registry=self.registry
        )
        
        self.queue_depth = Gauge(
            'indexing_queue_depth',
            'Current depth of indexing queue',
            registry=self.registry
        )
        
        self.system_resources = Gauge(
            'system_resource_usage',
            'System resource utilization',
            ['resource_type'],
            registry=self.registry
        )
    
    async def initialize(self):
        """Initialize metrics collector"""



        try:
            self.redis_client = Redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("MetricsCollector initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize MetricsCollector: {e}")
            raise
    
    async def record_operation(
        self,
        operation_type: str,
        content_type: str,
        processing_time_ms: float,
        success: bool,
        creator_id: str = None,
        metadata: Dict[str, Any] = None
    ):
        """Record metrics for an indexing operation"""



        try:
            # Record in Prometheus
            self.processing_time.labels(
                content_type=content_type,
                operation=operation_type
            ).observe(processing_time_ms / 1000.0)
            
            if success:
                self.content_counter.labels(
                    content_type=content_type,
                    creator_id=creator_id or "unknown"
                ).inc()
            else:
                self.error_counter.labels(
                    error_type="processing_failed",
                    operation=operation_type
                ).inc()
            
            # Collect system metrics
            cpu_usage = psutil.cpu_percent()
            memory_info = psutil.virtual_memory()
            gpu_usage = 0.0
            
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_usage = gpus[0].load * 100
            except:
                pass
            
            # Store performance metrics
            metrics = PerformanceMetrics(
                operation_type=operation_type,
                processing_time_ms=processing_time_ms,
                cpu_usage_percent=cpu_usage,
                memory_usage_mb=memory_info.used / 1024 / 1024,
                gpu_usage_percent=gpu_usage,
                queue_depth=await self._get_queue_depth(),
                success_count=1 if success else 0,
                error_count=0 if success else 1,
                timestamp=datetime.now(timezone.utc)
            )
            
            self.performance_history.append(metrics)
            
            # Update system resource gauges
            self.system_resources.labels(resource_type="cpu").set(cpu_usage)
            self.system_resources.labels(resource_type="memory").set(
                memory_info.percent
            )
            self.system_resources.labels(resource_type="gpu").set(gpu_usage)
            
            # Store in Redis for real-time dashboard
            await self.redis_client.zadd(
                "indexing_metrics",
                {
                    json.dumps(asdict(metrics)): time.time()
                }
            )
            
            # Cleanup old metrics (keep last 24 hours)
            cutoff_time = time.time() - (24 * 3600)
            await self.redis_client.zremrangebyscore(
                "indexing_metrics", 0, cutoff_time
            )
            
        except Exception as e:
            logger.error(f"Failed to record operation metrics: {e}")
    
    async def _get_queue_depth(self) -> int:
        """Get current queue depth"""



        try:
            depth = await self.redis_client.llen("indexing_queue")
            self.queue_depth.set(depth)
            return depth
        except:
            return 0
    
    async def get_current_metrics(self) -> IndexingMetrics:
        """Get current aggregated metrics"""



        try:
            now = datetime.now(timezone.utc)
            last_hour = now - timedelta(hours=1)
            last_day = now - timedelta(days=1)
            
            # Calculate metrics from performance history
            recent_metrics = [
                m for m in self.performance_history
                if m.timestamp >= last_hour
            ]
            
            daily_metrics = [
                m for m in self.performance_history
                if m.timestamp >= last_day
            ]
            
            total_indexed = sum(m.success_count for m in daily_metrics)
            total_errors = sum(m.error_count for m in daily_metrics)
            
            success_rate = 0.0
            if total_indexed + total_errors > 0:
                success_rate = (total_indexed / (total_indexed + total_errors)) * 100
            
            avg_processing_time = 0.0
            if recent_metrics:
                avg_processing_time = np.mean([
                    m.processing_time_ms for m in recent_metrics
                ])
            
            indexing_rate = len(recent_metrics) * 60.0  # per minute
            
            queue_depth = await self._get_queue_depth()
            
            # Get storage usage
            storage_usage = await self._calculate_storage_usage()
            
            # Get vector index size
            vector_index_size = await self.redis_client.zcard("vector_index")
            
            # Get fingerprint matches today
            fingerprint_matches = await self.redis_client.get(
                f"fingerprint_matches:{now.strftime('%Y-%m-%d')}"
            )
            fingerprint_matches = int(fingerprint_matches or 0)
            
            return IndexingMetrics(
                content_indexed_total=total_indexed,
                indexing_rate_per_minute=indexing_rate,
                average_processing_time_ms=avg_processing_time,
                success_rate_percent=success_rate,
                queue_backlog=queue_depth,
                storage_usage_gb=storage_usage,
                vector_index_size=vector_index_size,
                fingerprint_matches_today=fingerprint_matches
            )
            
        except Exception as e:
            logger.error(f"Failed to get current metrics: {e}")
            return IndexingMetrics(
                content_indexed_total=0,
                indexing_rate_per_minute=0.0,
                average_processing_time_ms=0.0,
                success_rate_percent=0.0,
                queue_backlog=0,
                storage_usage_gb=0.0,
                vector_index_size=0,
                fingerprint_matches_today=0
            )
    
    async def _calculate_storage_usage(self) -> float:
        """Calculate total storage usage in GB"""



        try:
            # This would typically query your storage backend
            # For now, return a placeholder value
            return 0.0
        except:
            return 0.0


class AlertManager:
    """Manages alerting for indexing operations"""
    
    def __init__(self, redis_url: str, notification_config: Dict[str, Any]):
        self.redis_url = redis_url
        self.notification_config = notification_config
        self.redis_client = None
        self.alert_rules = {}
        self.active_alerts = {}
        
    async def initialize(self):
        """Initialize alert manager"""



        try:
            self.redis_client = Redis.from_url(self.redis_url)
            await self.redis_client.ping()
            await self._load_alert_rules()
            logger.info("AlertManager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AlertManager: {e}")
            raise
    
    async def add_alert_rule(self, rule: AlertRule):
        """Add a new alert rule"""



        try:
            self.alert_rules[rule.name] = rule
            
            # Store in Redis
            await self.redis_client.hset(
                "alert_rules",
                rule.name,
                json.dumps(asdict(rule), default=str)
            )
            
            logger.info(f"Added alert rule: {rule.name}")
            
        except Exception as e:
            logger.error(f"Failed to add alert rule {rule.name}: {e}")
            raise
    
    async def _load_alert_rules(self):
        """Load alert rules from Redis"""



        try:
            rules_data = await self.redis_client.hgetall("alert_rules")
            
            for rule_name, rule_json in rules_data.items():
                rule_dict = json.loads(rule_json)
                rule = AlertRule(**rule_dict)
                self.alert_rules[rule_name] = rule
                
            logger.info(f"Loaded {len(self.alert_rules)} alert rules")
            
        except Exception as e:
            logger.error(f"Failed to load alert rules: {e}")
    
    async def check_alerts(self, metrics: IndexingMetrics):
        """Check all alert rules against current metrics"""



        try:
            for rule_name, rule in self.alert_rules.items():
                if not rule.enabled:
                    continue
                
                # Get metric value
                metric_value = getattr(metrics, rule.metric_name, None)
                if metric_value is None:
                    continue
                
                # Evaluate alert condition
                should_alert = self._evaluate_condition(
                    metric_value, rule.threshold, rule.comparison
                )
                
                if should_alert:
                    await self._trigger_alert(rule, metric_value)
                else:
                    await self._resolve_alert(rule_name)
                    
        except Exception as e:
            logger.error(f"Failed to check alerts: {e}")
    
    def _evaluate_condition(
        self, value: float, threshold: float, comparison: str
    ) -> bool:
        """Evaluate alert condition"""
        if comparison == ">":
            return value > threshold
        elif comparison == "<":
            return value < threshold
        elif comparison == ">=":
            return value >= threshold
        elif comparison == "<=":
            return value <= threshold
        elif comparison == "==":
            return abs(value - threshold) < 0.001
        else:
            return False
    
    async def _trigger_alert(self, rule: AlertRule, metric_value: float):
        """Trigger an alert"""



        try:
            alert_key = f"alert:{rule.name}"
            
            # Check if alert is already active
            if alert_key in self.active_alerts:
                return
            
            alert_data = {
                "rule_name": rule.name,
                "metric_name": rule.metric_name,
                "metric_value": metric_value,
                "threshold": rule.threshold,
                "level": rule.level.value,
                "triggered_at": datetime.now(timezone.utc).isoformat(),
                "message": f"{rule.metric_name} is {metric_value}, threshold: {rule.threshold}"
            }
            
            self.active_alerts[alert_key] = alert_data
            
            # Store in Redis
            await self.redis_client.hset(
                "active_alerts",
                alert_key,
                json.dumps(alert_data, default=str)
            )
            
            # Send notifications
            await self._send_notifications(alert_data, rule.notification_channels)
            
            logger.warning(f"Alert triggered: {rule.name} - {alert_data['message']}")
            
        except Exception as e:
            logger.error(f"Failed to trigger alert {rule.name}: {e}")
    
    async def _resolve_alert(self, rule_name: str):
        """Resolve an active alert"""



        try:
            alert_key = f"alert:{rule_name}"
            
            if alert_key in self.active_alerts:
                del self.active_alerts[alert_key]
                
                # Remove from Redis
                await self.redis_client.hdel("active_alerts", alert_key)
                
                logger.info(f"Alert resolved: {rule_name}")
                
        except Exception as e:
            logger.error(f"Failed to resolve alert {rule_name}: {e}")
    
    async def _send_notifications(
        self, alert_data: Dict[str, Any], channels: List[str]
    ):
        """Send alert notifications"""



        try:
            for channel in channels:
                if channel == "email":
                    await self._send_email_notification(alert_data)
                elif channel == "slack":
                    await self._send_slack_notification(alert_data)
                elif channel == "webhook":
                    await self._send_webhook_notification(alert_data)
                    
        except Exception as e:
            logger.error(f"Failed to send notifications: {e}")
    
    async def _send_email_notification(self, alert_data: Dict[str, Any]):
        """Send email notification (placeholder)"""
        # Implementation would depend on your email service
        logger.info(f"Email notification sent for alert: {alert_data['rule_name']}")
    
    async def _send_slack_notification(self, alert_data: Dict[str, Any]):
        """Send Slack notification (placeholder)"""
        # Implementation would depend on Slack API
        logger.info(f"Slack notification sent for alert: {alert_data['rule_name']}")
    
    async def _send_webhook_notification(self, alert_data: Dict[str, Any]):
        """Send webhook notification (placeholder)"""
        # Implementation would depend on webhook configuration
        logger.info(f"Webhook notification sent for alert: {alert_data['rule_name']}")


class PerformanceAnalyzer:
    """Analyzes performance trends and provides optimization recommendations"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.analysis_cache = {}
        
    async def analyze_performance_trends(
        self, time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """Analyze performance trends over specified time window"""



        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
            
            relevant_metrics = [
                m for m in self.metrics_collector.performance_history
                if m.timestamp >= cutoff_time
            ]
            
            if not relevant_metrics:
                return {"status": "insufficient_data"}
            
            # Calculate trends
            processing_times = [m.processing_time_ms for m in relevant_metrics]
            cpu_usage = [m.cpu_usage_percent for m in relevant_metrics]
            memory_usage = [m.memory_usage_mb for m in relevant_metrics]
            gpu_usage = [m.gpu_usage_percent for m in relevant_metrics]
            
            analysis = {
                "time_window_hours": time_window_hours,
                "total_operations": len(relevant_metrics),
                "processing_time": {
                    "average": np.mean(processing_times),
                    "median": np.median(processing_times),
                    "p95": np.percentile(processing_times, 95),
                    "p99": np.percentile(processing_times, 99),
                    "trend": self._calculate_trend(processing_times)
                },
                "resource_usage": {
                    "cpu": {
                        "average": np.mean(cpu_usage),
                        "peak": np.max(cpu_usage),
                        "trend": self._calculate_trend(cpu_usage)
                    },
                    "memory": {
                        "average": np.mean(memory_usage),
                        "peak": np.max(memory_usage),
                        "trend": self._calculate_trend(memory_usage)
                    },
                    "gpu": {
                        "average": np.mean(gpu_usage),
                        "peak": np.max(gpu_usage),
                        "trend": self._calculate_trend(gpu_usage)
                    }
                },
                "recommendations": self._generate_recommendations(relevant_metrics)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze performance trends: {e}")
            return {"status": "error", "message": str(e)}
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for a series of values"""
        if len(values) < 2:
            return "stable"
        
        # Simple linear trend calculation
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _generate_recommendations(
        self, metrics: List[PerformanceMetrics]
    ) -> List[str]:
        """Generate optimization recommendations based on metrics"""
        recommendations = []
        
        # Analyze processing time
        processing_times = [m.processing_time_ms for m in metrics]
        avg_processing_time = np.mean(processing_times)
        
        if avg_processing_time > 5000:  # 5 seconds
            recommendations.append(
                "Consider optimizing content processing algorithms - "
                "average processing time is high"
            )
        
        # Analyze CPU usage
        cpu_usage = [m.cpu_usage_percent for m in metrics]
        avg_cpu = np.mean(cpu_usage)
        
        if avg_cpu > 80:
            recommendations.append(
                "High CPU usage detected - consider scaling horizontally "
                "or optimizing CPU-intensive operations"
            )
        
        # Analyze memory usage
        memory_usage = [m.memory_usage_mb for m in metrics]
        avg_memory = np.mean(memory_usage)
        
        if avg_memory > 8000:  # 8GB
            recommendations.append(
                "High memory usage detected - consider memory optimization "
                "or increasing available RAM"
            )
        
        # Analyze queue depth
        queue_depths = [m.queue_depth for m in metrics]
        avg_queue_depth = np.mean(queue_depths)
        
        if avg_queue_depth > 100:
            recommendations.append(
                "Processing queue backlog detected - consider increasing "
                "worker processes or optimizing batch processing"
            )
        
        # Analyze error rate
        total_operations = len(metrics)
        total_errors = sum(m.error_count for m in metrics)
        error_rate = (total_errors / total_operations) * 100 if total_operations > 0 else 0
        
        if error_rate > 5:
            recommendations.append(
                f"High error rate ({error_rate:.1f}%) detected - "
                "investigate and fix processing issues"
            )
        
        if not recommendations:
            recommendations.append("System performance is optimal")
        
        return recommendations
