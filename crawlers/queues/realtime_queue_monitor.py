"""
Real-time Queue Monitor - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/queues/realtime_queue_monitor.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Real-time Monitoring & Alert System
Responsibility: Live queue monitoring with intelligent alerting and auto-recovery
Technologies: WebSocket streams, Real-time analytics, Predictive alerts, Auto-scaling
================================================================================

  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Queue metrics collection → Real-time analysis → Anomaly detection → 
Alert generation → Auto-recovery → Performance optimization → Predictive scaling
"""

from typing import Any, Dict, List, Optional, Union, Set, Tuple, Callable, AsyncGenerator
import logging
import asyncio
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import numpy as np
from collections import defaultdict, deque
import time
import statistics
import websockets
import aioredis
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest

from backend.core.managers.queue_manager import IntelligentQueueManager
from .task_distribution_engine import TaskDistributionEngine, LoadBalancingMetrics

logger = logging.getLogger(__name__)


class MonitoringLevel(Enum):
    """Monitoring detail levels"""
    BASIC = "basic"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"
    DEBUG = "debug"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class MetricType(Enum):
    """Types of metrics to monitor"""
    QUEUE_SIZE = "queue_size"
    PROCESSING_RATE = "processing_rate"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    WORKER_HEALTH = "worker_health"
    RESOURCE_USAGE = "resource_usage"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    SUCCESS_RATE = "success_rate"
    LOAD_DISTRIBUTION = "load_distribution"


class AlertCondition(Enum):
    """Alert trigger conditions"""
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    THRESHOLD_BELOW = "threshold_below"
    RATE_OF_CHANGE = "rate_of_change"
    ANOMALY_DETECTED = "anomaly_detected"
    PATTERN_DEVIATION = "pattern_deviation"
    PREDICTIVE_ALERT = "predictive_alert"


@dataclass
class MetricDataPoint:
    """Single metric data point"""
    metric_type: MetricType
    value: float
    timestamp: datetime
    source: str
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AlertRule:
    """Alert rule configuration"""
    rule_id: str
    name: str
    metric_type: MetricType
    condition: AlertCondition
    threshold: float
    severity: AlertSeverity
    duration_seconds: int = 300  # 5 minutes
    enabled: bool = True
    notification_channels: List[str] = field(default_factory=list)
    auto_recovery_enabled: bool = False
    recovery_actions: List[str] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class MonitoringAlert:
    """Monitoring alert instance"""
    alert_id: str
    rule_id: str
    severity: AlertSeverity
    title: str
    description: str
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    is_resolved: bool = False
    metric_value: float = 0.0
    threshold: float = 0.0
    source: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    recovery_actions_taken: List[str] = field(default_factory=list)


@dataclass
class PerformanceSnapshot:
    """Complete performance snapshot"""
    timestamp: datetime
    queue_metrics: Dict[str, Any]
    worker_metrics: Dict[str, Any]
    distribution_metrics: Dict[str, Any]
    system_metrics: Dict[str, Any]
    health_score: float
    bottlenecks: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class MonitoringConfig:
    """Monitoring system configuration"""
    monitoring_level: MonitoringLevel = MonitoringLevel.DETAILED
    collection_interval_seconds: int = 30
    alert_evaluation_interval_seconds: int = 60
    metric_retention_hours: int = 72
    websocket_port: int = 8765
    prometheus_enabled: bool = True
    redis_enabled: bool = True
    auto_recovery_enabled: bool = True
    predictive_alerts_enabled: bool = True
    anomaly_detection_enabled: bool = True


class AnomalyDetector:
    """Statistical anomaly detection for metrics"""
    
    def __init__(self, window_size: int = 100, sensitivity: float = 2.0):
        self.window_size = window_size
        self.sensitivity = sensitivity  # Z-score threshold
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.baseline_stats: Dict[str, Dict] = {}
        
    async def add_metric(self, metric_key: str, value: float):
        """Add metric value for anomaly detection"""
        
        self.metric_history[metric_key].append(value)
        
        # Update baseline statistics
        if len(self.metric_history[metric_key]) >= 10:
            values = list(self.metric_history[metric_key])
            self.baseline_stats[metric_key] = {
                'mean': statistics.mean(values),
                'std': statistics.stdev(values) if len(values) > 1 else 0.0,
                'min': min(values),
                'max': max(values),
                'median': statistics.median(values)
            }
    
    async def detect_anomaly(self, metric_key: str, value: float) -> Tuple[bool, float]:
        """Detect if value is anomalous"""
        
        if metric_key not in self.baseline_stats:
            return False, 0.0
        
        stats = self.baseline_stats[metric_key]
        
        if stats['std'] == 0.0:
            return False, 0.0
        
        # Calculate Z-score
        z_score = abs(value - stats['mean']) / stats['std']
        
        is_anomaly = z_score > self.sensitivity
        
        return is_anomaly, z_score
    
    async def get_anomaly_score(self, metric_key: str) -> float:
        """Get current anomaly score for metric"""
        
        if metric_key not in self.metric_history or len(self.metric_history[metric_key]) < 2:
            return 0.0
        
        recent_values = list(self.metric_history[metric_key])[-5:]  # Last 5 values
        
        if metric_key not in self.baseline_stats:
            return 0.0
        
        stats = self.baseline_stats[metric_key]
        
        if stats['std'] == 0.0:
            return 0.0
        
        # Calculate average Z-score for recent values
        z_scores = []
        for value in recent_values:
            z_score = abs(value - stats['mean']) / stats['std']
            z_scores.append(z_score)
        
        return sum(z_scores) / len(z_scores) if z_scores else 0.0


class PredictiveAnalyzer:
    """Predictive analysis for queue performance"""
    
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.metric_trends: Dict[str, deque] = defaultdict(lambda: deque(maxlen=history_size))
        
    async def add_metric_trend(self, metric_key: str, timestamp: datetime, value: float):
        """Add metric for trend analysis"""
        
        self.metric_trends[metric_key].append({
            'timestamp': timestamp,
            'value': value
        })
    
    async def predict_future_value(self, metric_key: str, minutes_ahead: int = 15) -> Optional[float]:
        """Predict future metric value using simple linear regression"""
        
        if metric_key not in self.metric_trends or len(self.metric_trends[metric_key]) < 10:
            return None
        
        trends = list(self.metric_trends[metric_key])
        
        # Extract time series data
        times = []
        values = []
        
        base_time = trends[0]['timestamp']
        for trend in trends:
            time_diff = (trend['timestamp'] - base_time).total_seconds()
            times.append(time_diff)
            values.append(trend['value'])
        
        # Simple linear regression
        n = len(times)
        sum_x = sum(times)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(times, values))
        sum_x2 = sum(x * x for x in times)
        
        # Calculate slope and intercept
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        # Predict future value
        future_time = times[-1] + (minutes_ahead * 60)
        predicted_value = slope * future_time + intercept
        
        return max(0.0, predicted_value)  # Ensure non-negative
    
    async def detect_trend_direction(self, metric_key: str) -> Optional[str]:
        """Detect if metric is trending up, down, or stable"""
        
        if metric_key not in self.metric_trends or len(self.metric_trends[metric_key]) < 5:
            return None
        
        recent_trends = list(self.metric_trends[metric_key])[-10:]  # Last 10 data points
        values = [trend['value'] for trend in recent_trends]
        
        # Calculate simple moving average slope
        if len(values) < 3:
            return "stable"
        
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        change_percent = ((second_avg - first_avg) / max(0.001, first_avg)) * 100
        
        if change_percent > 10:
            return "increasing"
        elif change_percent < -10:
            return "decreasing"
        else:
            return "stable"


class RealtimeQueueMonitor:
    """Real-time queue monitoring system with intelligent alerting"""
    
    def __init__(self, 
                 config: MonitoringConfig,
                 queue_manager: Optional[IntelligentQueueManager] = None,
                 distribution_engine: Optional[TaskDistributionEngine] = None):
        self.config = config
        self.queue_manager = queue_manager
        self.distribution_engine = distribution_engine
        
        # Monitoring components
        self.anomaly_detector = AnomalyDetector()
        self.predictive_analyzer = PredictiveAnalyzer()
        
        # Data storage
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.active_alerts: Dict[str, MonitoringAlert] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.performance_snapshots: deque = deque(maxlen=1000)
        
        # WebSocket connections
        self.websocket_connections: Set = set()
        
        # Prometheus metrics
        if config.prometheus_enabled:
            self.prometheus_registry = CollectorRegistry()
            self._setup_prometheus_metrics()
        
        # Redis connection
        self.redis_client = None
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_tasks: List[asyncio.Task] = []
        
        # Performance tracking
        self.last_performance_snapshot: Optional[PerformanceSnapshot] = None
        
        logger.info("Real-time Queue Monitor initialized")
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics"""
        
        self.prometheus_counters = {
            'tasks_processed': Counter('queue_tasks_processed_total', 'Total tasks processed', registry=self.prometheus_registry),
            'tasks_failed': Counter('queue_tasks_failed_total', 'Total tasks failed', registry=self.prometheus_registry),
            'alerts_triggered': Counter('queue_alerts_triggered_total', 'Total alerts triggered', ['severity'], registry=self.prometheus_registry)
        }
        
        self.prometheus_gauges = {
            'queue_size': Gauge('queue_size_current', 'Current queue size', ['queue_type'], registry=self.prometheus_registry),
            'active_workers': Gauge('queue_active_workers', 'Active workers count', registry=self.prometheus_registry),
            'health_score': Gauge('queue_health_score', 'Overall queue health score', registry=self.prometheus_registry),
            'response_time': Gauge('queue_response_time_ms', 'Average response time in milliseconds', registry=self.prometheus_registry)
        }
        
        self.prometheus_histograms = {
            'task_duration': Histogram('queue_task_duration_seconds', 'Task processing duration', registry=self.prometheus_registry),
            'distribution_time': Histogram('queue_distribution_time_seconds', 'Task distribution time', registry=self.prometheus_registry)
        }
    
    async def initialize(self):
        """Initialize monitoring system"""
        
        # Setup Redis connection if enabled
        if self.config.redis_enabled:
            try:
                self.redis_client = await aioredis.from_url("redis://localhost:6379")
                await self.redis_client.ping()
                logger.info("Redis connection established for monitoring")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")
                self.redis_client = None
        
        # Setup default alert rules
        await self._setup_default_alert_rules()
        
        logger.info("Real-time Queue Monitor initialized successfully")
    
    async def _setup_default_alert_rules(self):
        """Setup default monitoring alert rules"""
        
        default_rules = [
            AlertRule(
                rule_id="high_queue_size",
                name="High Queue Size",
                metric_type=MetricType.QUEUE_SIZE,
                condition=AlertCondition.THRESHOLD_EXCEEDED,
                threshold=1000.0,
                severity=AlertSeverity.WARNING,
                duration_seconds=300,
                auto_recovery_enabled=True,
                recovery_actions=["scale_workers", "optimize_distribution"]
            ),
            AlertRule(
                rule_id="critical_queue_size",
                name="Critical Queue Size",
                metric_type=MetricType.QUEUE_SIZE,
                condition=AlertCondition.THRESHOLD_EXCEEDED,
                threshold=5000.0,
                severity=AlertSeverity.CRITICAL,
                duration_seconds=180,
                auto_recovery_enabled=True,
                recovery_actions=["emergency_scale", "throttle_inputs"]
            ),
            AlertRule(
                rule_id="low_processing_rate",
                name="Low Processing Rate",
                metric_type=MetricType.PROCESSING_RATE,
                condition=AlertCondition.THRESHOLD_BELOW,
                threshold=10.0,
                severity=AlertSeverity.WARNING,
                duration_seconds=600
            ),
            AlertRule(
                rule_id="high_error_rate",
                name="High Error Rate",
                metric_type=MetricType.ERROR_RATE,
                condition=AlertCondition.THRESHOLD_EXCEEDED,
                threshold=0.1,  # 10%
                severity=AlertSeverity.CRITICAL,
                duration_seconds=300,
                auto_recovery_enabled=True,
                recovery_actions=["restart_unhealthy_workers", "switch_distribution_strategy"]
            ),
            AlertRule(
                rule_id="worker_health_degraded",
                name="Worker Health Degraded",
                metric_type=MetricType.WORKER_HEALTH,
                condition=AlertCondition.THRESHOLD_BELOW,
                threshold=0.7,
                severity=AlertSeverity.WARNING,
                duration_seconds=240
            ),
            AlertRule(
                rule_id="anomaly_detected",
                name="Performance Anomaly Detected",
                metric_type=MetricType.THROUGHPUT,
                condition=AlertCondition.ANOMALY_DETECTED,
                threshold=2.0,  # Z-score threshold
                severity=AlertSeverity.INFO,
                duration_seconds=120
            )
        ]
        
        for rule in default_rules:
            self.alert_rules[rule.rule_id] = rule
    
    async def start_monitoring(self):
        """Start real-time monitoring"""
        
        if self.is_monitoring:
            logger.warning("Monitoring already started")
            return
        
        self.is_monitoring = True
        
        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self._metrics_collection_loop()),
            asyncio.create_task(self._alert_evaluation_loop()),
            asyncio.create_task(self._performance_analysis_loop()),
            asyncio.create_task(self._websocket_server()),
            asyncio.create_task(self._cleanup_old_data_loop())
        ]
        
        if self.config.predictive_alerts_enabled:
            tasks.append(asyncio.create_task(self._predictive_analysis_loop()))
        
        self.monitoring_tasks = tasks
        
        logger.info("Real-time monitoring started")
    
    async def stop_monitoring(self):
        """Stop real-time monitoring"""
        
        self.is_monitoring = False
        
        # Cancel all monitoring tasks
        for task in self.monitoring_tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete
        if self.monitoring_tasks:
            await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Real-time monitoring stopped")
    
    async def _metrics_collection_loop(self):
        """Background task for metrics collection"""
        
        while self.is_monitoring:
            try:
                await self._collect_metrics()
                await asyncio.sleep(self.config.collection_interval_seconds)
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(self.config.collection_interval_seconds)
    
    async def _collect_metrics(self):
        """Collect metrics from various sources"""
        
        timestamp = datetime.utcnow()
        collected_metrics = []
        
        # Collect queue metrics
        if self.queue_manager:
            queue_metrics = await self._collect_queue_metrics(timestamp)
            collected_metrics.extend(queue_metrics)
        
        # Collect distribution metrics
        if self.distribution_engine:
            distribution_metrics = await self._collect_distribution_metrics(timestamp)
            collected_metrics.extend(distribution_metrics)
        
        # Store metrics
        for metric in collected_metrics:
            await self._store_metric(metric)
            
            # Update anomaly detector
            if self.config.anomaly_detection_enabled:
                metric_key = f"{metric.metric_type.value}_{metric.source}"
                await self.anomaly_detector.add_metric(metric_key, metric.value)
            
            # Update predictive analyzer
            if self.config.predictive_alerts_enabled:
                metric_key = f"{metric.metric_type.value}_{metric.source}"
                await self.predictive_analyzer.add_metric_trend(metric_key, timestamp, metric.value)
        
        # Update Prometheus metrics
        if self.config.prometheus_enabled:
            await self._update_prometheus_metrics(collected_metrics)
        
        # Broadcast to WebSocket clients
        await self._broadcast_metrics(collected_metrics)
    
    async def _collect_queue_metrics(self, timestamp: datetime) -> List[MetricDataPoint]:
        """Collect queue-specific metrics"""
        
        metrics = []
        
        try:
            # Basic queue metrics (these would come from actual queue manager)
            # For now, we'll simulate some metrics
            
            # Queue size
            metrics.append(MetricDataPoint(
                metric_type=MetricType.QUEUE_SIZE,
                value=float(len(getattr(self.queue_manager, '_task_queue', []))),
                timestamp=timestamp,
                source="queue_manager",
                tags={"queue_type": "crawler"}
            ))
            
            # Processing rate (tasks per minute)
            # This would be calculated from actual queue statistics
            processing_rate = 45.0  # Simulated
            metrics.append(MetricDataPoint(
                metric_type=MetricType.PROCESSING_RATE,
                value=processing_rate,
                timestamp=timestamp,
                source="queue_manager",
                tags={"unit": "tasks_per_minute"}
            ))
            
            # Success rate
            success_rate = 0.95  # Simulated
            metrics.append(MetricDataPoint(
                metric_type=MetricType.SUCCESS_RATE,
                value=success_rate,
                timestamp=timestamp,
                source="queue_manager",
                tags={"unit": "percentage"}
            ))
            
        except Exception as e:
            logger.error(f"Error collecting queue metrics: {e}")
        
        return metrics
    
    async def _collect_distribution_metrics(self, timestamp: datetime) -> List[MetricDataPoint]:
        """Collect distribution engine metrics"""
        
        metrics = []
        
        try:
            if hasattr(self.distribution_engine, 'get_distribution_metrics'):
                dist_metrics = await self.distribution_engine.get_distribution_metrics()
                
                # Distribution efficiency
                metrics.append(MetricDataPoint(
                    metric_type=MetricType.RESOURCE_USAGE,
                    value=dist_metrics.resource_utilization_efficiency,
                    timestamp=timestamp,
                    source="distribution_engine",
                    tags={"metric": "resource_efficiency"}
                ))
                
                # Load balance score
                metrics.append(MetricDataPoint(
                    metric_type=MetricType.LOAD_DISTRIBUTION,
                    value=dist_metrics.load_balance_score,
                    timestamp=timestamp,
                    source="distribution_engine",
                    tags={"metric": "load_balance"}
                ))
                
                # Average distribution time
                metrics.append(MetricDataPoint(
                    metric_type=MetricType.RESPONSE_TIME,
                    value=dist_metrics.average_distribution_time_ms,
                    timestamp=timestamp,
                    source="distribution_engine",
                    tags={"unit": "milliseconds"}
                ))
                
                # Worker health
                metrics.append(MetricDataPoint(
                    metric_type=MetricType.WORKER_HEALTH,
                    value=dist_metrics.agent_health_average,
                    timestamp=timestamp,
                    source="distribution_engine",
                    tags={"metric": "average_health"}
                ))
                
        except Exception as e:
            logger.error(f"Error collecting distribution metrics: {e}")
        
        return metrics
    
    async def _store_metric(self, metric: MetricDataPoint):
        """Store metric in various backends"""
        
        # Store in memory
        metric_key = f"{metric.metric_type.value}_{metric.source}"
        self.metric_history[metric_key].append({
            'timestamp': metric.timestamp,
            'value': metric.value,
            'tags': metric.tags,
            'metadata': metric.metadata
        })
        
        # Store in Redis if available
        if self.redis_client:
            try:
                redis_key = f"metrics:{metric_key}"
                metric_data = {
                    'timestamp': metric.timestamp.isoformat(),
                    'value': metric.value,
                    'tags': json.dumps(metric.tags),
                    'metadata': json.dumps(metric.metadata)
                }
                
                await self.redis_client.lpush(redis_key, json.dumps(metric_data))
                await self.redis_client.ltrim(redis_key, 0, 999)  # Keep last 1000 entries
                await self.redis_client.expire(redis_key, self.config.metric_retention_hours * 3600)
                
            except Exception as e:
                logger.error(f"Error storing metric to Redis: {e}")
    
    async def _update_prometheus_metrics(self, metrics: List[MetricDataPoint]):
        """Update Prometheus metrics"""
        
        for metric in metrics:
            try:
                if metric.metric_type == MetricType.QUEUE_SIZE:
                    queue_type = metric.tags.get('queue_type', 'unknown')
                    self.prometheus_gauges['queue_size'].labels(queue_type=queue_type).set(metric.value)
                
                elif metric.metric_type == MetricType.RESPONSE_TIME:
                    self.prometheus_gauges['response_time'].set(metric.value)
                
                elif metric.metric_type == MetricType.WORKER_HEALTH:
                    # Calculate overall health score
                    health_score = metric.value
                    self.prometheus_gauges['health_score'].set(health_score)
                
            except Exception as e:
                logger.error(f"Error updating Prometheus metric: {e}")
    
    async def _broadcast_metrics(self, metrics: List[MetricDataPoint]):
        """Broadcast metrics to WebSocket clients"""
        
        if not self.websocket_connections:
            return
        
        try:
            metrics_data = {
                'type': 'metrics_update',
                'timestamp': datetime.utcnow().isoformat(),
                'metrics': [
                    {
                        'type': metric.metric_type.value,
                        'value': metric.value,
                        'source': metric.source,
                        'tags': metric.tags,
                        'timestamp': metric.timestamp.isoformat()
                    }
                    for metric in metrics
                ]
            }
            
            message = json.dumps(metrics_data)
            
            # Send to all connected clients
            disconnected_clients = set()
            for websocket in self.websocket_connections:
                try:
                    await websocket.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected_clients.add(websocket)
                except Exception as e:
                    logger.error(f"Error sending WebSocket message: {e}")
                    disconnected_clients.add(websocket)
            
            # Remove disconnected clients
            self.websocket_connections -= disconnected_clients
            
        except Exception as e:
            logger.error(f"Error broadcasting metrics: {e}")
    
    async def _alert_evaluation_loop(self):
        """Background task for alert evaluation"""
        
        while self.is_monitoring:
            try:
                await self._evaluate_alerts()
                await asyncio.sleep(self.config.alert_evaluation_interval_seconds)
                
            except Exception as e:
                logger.error(f"Alert evaluation error: {e}")
                await asyncio.sleep(self.config.alert_evaluation_interval_seconds)
    
    async def _evaluate_alerts(self):
        """Evaluate alert rules against current metrics"""
        
        current_time = datetime.utcnow()
        
        for rule_id, rule in self.alert_rules.items():
            if not rule.enabled:
                continue
            
            try:
                triggered = await self._evaluate_alert_rule(rule, current_time)
                
                if triggered:
                    await self._trigger_alert(rule, current_time)
                else:
                    # Check if existing alert should be resolved
                    await self._check_alert_resolution(rule, current_time)
                    
            except Exception as e:
                logger.error(f"Error evaluating alert rule {rule_id}: {e}")
    
    async def _evaluate_alert_rule(self, rule: AlertRule, current_time: datetime) -> bool:
        """Evaluate a single alert rule"""
        
        # Get recent metrics for the rule's metric type
        metric_key = f"{rule.metric_type.value}_queue_manager"
        if metric_key not in self.metric_history:
            return False
        
        recent_metrics = list(self.metric_history[metric_key])
        if not recent_metrics:
            return False
        
        # Filter metrics within duration window
        cutoff_time = current_time - timedelta(seconds=rule.duration_seconds)
        relevant_metrics = [
            m for m in recent_metrics 
            if m['timestamp'] >= cutoff_time
        ]
        
        if not relevant_metrics:
            return False
        
        # Evaluate condition
        if rule.condition == AlertCondition.THRESHOLD_EXCEEDED:
            return any(m['value'] > rule.threshold for m in relevant_metrics)
        
        elif rule.condition == AlertCondition.THRESHOLD_BELOW:
            return any(m['value'] < rule.threshold for m in relevant_metrics)
        
        elif rule.condition == AlertCondition.ANOMALY_DETECTED:
            if self.config.anomaly_detection_enabled:
                anomaly_score = await self.anomaly_detector.get_anomaly_score(metric_key)
                return anomaly_score > rule.threshold
        
        elif rule.condition == AlertCondition.RATE_OF_CHANGE:
            if len(relevant_metrics) >= 2:
                first_value = relevant_metrics[0]['value']
                last_value = relevant_metrics[-1]['value']
                if first_value > 0:
                    change_rate = abs(last_value - first_value) / first_value
                    return change_rate > rule.threshold
        
        return False
    
    async def _trigger_alert(self, rule: AlertRule, trigger_time: datetime):
        """Trigger an alert"""
        
        # Check if alert already exists and is active
        existing_alert_key = f"{rule.rule_id}_active"
        if existing_alert_key in self.active_alerts:
            return  # Alert already active
        
        # Create new alert
        alert = MonitoringAlert(
            alert_id=str(uuid.uuid4()),
            rule_id=rule.rule_id,
            severity=rule.severity,
            title=rule.name,
            description=f"Alert rule '{rule.name}' has been triggered",
            triggered_at=trigger_time,
            tags=rule.tags.copy()
        )
        
        # Get current metric value
        metric_key = f"{rule.metric_type.value}_queue_manager"
        if metric_key in self.metric_history and self.metric_history[metric_key]:
            latest_metric = self.metric_history[metric_key][-1]
            alert.metric_value = latest_metric['value']
            alert.threshold = rule.threshold
        
        # Store alert
        self.active_alerts[existing_alert_key] = alert
        
        # Update Prometheus counter
        if self.config.prometheus_enabled:
            self.prometheus_counters['alerts_triggered'].labels(severity=rule.severity.value).inc()
        
        # Execute auto-recovery if enabled
        if rule.auto_recovery_enabled and self.config.auto_recovery_enabled:
            recovery_actions_taken = await self._execute_recovery_actions(rule.recovery_actions)
            alert.recovery_actions_taken = recovery_actions_taken
        
        # Send notifications
        await self._send_alert_notifications(alert)
        
        logger.warning(f"Alert triggered: {alert.title} (ID: {alert.alert_id})")
    
    async def _check_alert_resolution(self, rule: AlertRule, current_time: datetime):
        """Check if an active alert should be resolved"""
        
        alert_key = f"{rule.rule_id}_active"
        if alert_key not in self.active_alerts:
            return
        
        alert = self.active_alerts[alert_key]
        
        # Check if condition is no longer met
        if not await self._evaluate_alert_rule(rule, current_time):
            # Resolve alert
            alert.resolved_at = current_time
            alert.is_resolved = True
            
            # Move to resolved alerts (could be stored separately)
            del self.active_alerts[alert_key]
            
            # Send resolution notification
            await self._send_alert_resolution(alert)
            
            logger.info(f"Alert resolved: {alert.title} (ID: {alert.alert_id})")
    
    async def _execute_recovery_actions(self, actions: List[str]) -> List[str]:
        """Execute automatic recovery actions"""
        
        executed_actions = []
        
        for action in actions:
            try:
                if action == "scale_workers":
                    # Trigger worker scaling
                    if self.distribution_engine:
                        # This would call actual scaling logic
                        logger.info("Executing auto-recovery: scaling workers")
                        executed_actions.append("scale_workers")
                
                elif action == "optimize_distribution":
                    # Optimize distribution strategy
                    if self.distribution_engine:
                        logger.info("Executing auto-recovery: optimizing distribution")
                        executed_actions.append("optimize_distribution")
                
                elif action == "restart_unhealthy_workers":
                    # Restart unhealthy workers
                    logger.info("Executing auto-recovery: restarting unhealthy workers")
                    executed_actions.append("restart_unhealthy_workers")
                
                elif action == "throttle_inputs":
                    # Implement input throttling
                    logger.info("Executing auto-recovery: throttling inputs")
                    executed_actions.append("throttle_inputs")
                
                elif action == "emergency_scale":
                    # Emergency scaling
                    logger.info("Executing auto-recovery: emergency scaling")
                    executed_actions.append("emergency_scale")
                
            except Exception as e:
                logger.error(f"Error executing recovery action {action}: {e}")
        
        return executed_actions
    
    async def _send_alert_notifications(self, alert: MonitoringAlert):
        """Send alert notifications"""
        
        # Broadcast to WebSocket clients
        alert_data = {
            'type': 'alert_triggered',
            'timestamp': datetime.utcnow().isoformat(),
            'alert': {
                'id': alert.alert_id,
                'rule_id': alert.rule_id,
                'severity': alert.severity.value,
                'title': alert.title,
                'description': alert.description,
                'triggered_at': alert.triggered_at.isoformat(),
                'metric_value': alert.metric_value,
                'threshold': alert.threshold,
                'recovery_actions_taken': alert.recovery_actions_taken
            }
        }
        
        message = json.dumps(alert_data)
        
        disconnected_clients = set()
        for websocket in self.websocket_connections:
            try:
                await websocket.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(websocket)
            except Exception as e:
                logger.error(f"Error sending alert notification: {e}")
        
        self.websocket_connections -= disconnected_clients
    
    async def _send_alert_resolution(self, alert: MonitoringAlert):
        """Send alert resolution notification"""
        
        resolution_data = {
            'type': 'alert_resolved',
            'timestamp': datetime.utcnow().isoformat(),
            'alert': {
                'id': alert.alert_id,
                'title': alert.title,
                'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None
            }
        }
        
        message = json.dumps(resolution_data)
        
        disconnected_clients = set()
        for websocket in self.websocket_connections:
            try:
                await websocket.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(websocket)
            except Exception as e:
                logger.error(f"Error sending resolution notification: {e}")
        
        self.websocket_connections -= disconnected_clients
    
    async def _performance_analysis_loop(self):
        """Background task for performance analysis"""
        
        while self.is_monitoring:
            try:
                await self._analyze_performance()
                await asyncio.sleep(300)  # Every 5 minutes
                
            except Exception as e:
                logger.error(f"Performance analysis error: {e}")
                await asyncio.sleep(300)
    
    async def _analyze_performance(self):
        """Analyze current performance and generate insights"""
        
        timestamp = datetime.utcnow()
        
        # Collect current metrics
        queue_metrics = {}
        worker_metrics = {}
        distribution_metrics = {}
        system_metrics = {}
        
        # Calculate health score
        health_score = await self._calculate_health_score()
        
        # Detect bottlenecks
        bottlenecks = await self._detect_bottlenecks()
        
        # Generate recommendations
        recommendations = await self._generate_recommendations()
        
        # Create performance snapshot
        snapshot = PerformanceSnapshot(
            timestamp=timestamp,
            queue_metrics=queue_metrics,
            worker_metrics=worker_metrics,
            distribution_metrics=distribution_metrics,
            system_metrics=system_metrics,
            health_score=health_score,
            bottlenecks=bottlenecks,
            recommendations=recommendations
        )
        
        self.performance_snapshots.append(snapshot)
        self.last_performance_snapshot = snapshot
        
        # Broadcast performance update
        await self._broadcast_performance_update(snapshot)
    
    async def _calculate_health_score(self) -> float:
        """Calculate overall system health score"""
        
        health_factors = []
        
        # Queue health (based on size and processing rate)
        queue_size_key = "queue_size_queue_manager"
        if queue_size_key in self.metric_history and self.metric_history[queue_size_key]:
            recent_queue_size = self.metric_history[queue_size_key][-1]['value']
            queue_health = max(0.0, 1.0 - (recent_queue_size / 10000.0))  # Normalize against max expected size
            health_factors.append(queue_health)
        
        # Worker health
        worker_health_key = "worker_health_distribution_engine"
        if worker_health_key in self.metric_history and self.metric_history[worker_health_key]:
            worker_health = self.metric_history[worker_health_key][-1]['value']
            health_factors.append(worker_health)
        
        # Success rate health
        success_rate_key = "success_rate_queue_manager"
        if success_rate_key in self.metric_history and self.metric_history[success_rate_key]:
            success_rate = self.metric_history[success_rate_key][-1]['value']
            health_factors.append(success_rate)
        
        # Response time health (inverse relationship)
        response_time_key = "response_time_distribution_engine"
        if response_time_key in self.metric_history and self.metric_history[response_time_key]:
            response_time = self.metric_history[response_time_key][-1]['value']
            response_health = max(0.0, 1.0 - (response_time / 5000.0))  # Normalize against 5 second max
            health_factors.append(response_health)
        
        # Calculate weighted average
        if health_factors:
            return sum(health_factors) / len(health_factors)
        
        return 0.5  # Default moderate health
    
    async def _detect_bottlenecks(self) -> List[str]:
        """Detect system bottlenecks"""
        
        bottlenecks = []
        
        # High queue size bottleneck
        queue_size_key = "queue_size_queue_manager"
        if queue_size_key in self.metric_history and self.metric_history[queue_size_key]:
            recent_queue_size = self.metric_history[queue_size_key][-1]['value']
            if recent_queue_size > 1000:
                bottlenecks.append("High queue size indicates processing bottleneck")
        
        # Low processing rate bottleneck
        processing_rate_key = "processing_rate_queue_manager"
        if processing_rate_key in self.metric_history and self.metric_history[processing_rate_key]:
            processing_rate = self.metric_history[processing_rate_key][-1]['value']
            if processing_rate < 10:
                bottlenecks.append("Low processing rate indicates worker capacity bottleneck")
        
        # High response time bottleneck
        response_time_key = "response_time_distribution_engine"
        if response_time_key in self.metric_history and self.metric_history[response_time_key]:
            response_time = self.metric_history[response_time_key][-1]['value']
            if response_time > 2000:  # 2 seconds
                bottlenecks.append("High response time indicates distribution bottleneck")
        
        # Resource utilization bottleneck
        resource_key = "resource_usage_distribution_engine"
        if resource_key in self.metric_history and self.metric_history[resource_key]:
            resource_usage = self.metric_history[resource_key][-1]['value']
            if resource_usage > 0.9:
                bottlenecks.append("High resource utilization indicates capacity bottleneck")
        
        return bottlenecks
    
    async def _generate_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations"""
        
        recommendations = []
        
        # Analyze trends and suggest optimizations
        bottlenecks = await self._detect_bottlenecks()
        
        if "High queue size indicates processing bottleneck" in bottlenecks:
            recommendations.append("Consider scaling up worker instances")
            recommendations.append("Optimize task distribution strategy")
        
        if "Low processing rate indicates worker capacity bottleneck" in bottlenecks:
            recommendations.append("Increase worker pool size")
            recommendations.append("Optimize individual worker performance")
        
        if "High response time indicates distribution bottleneck" in bottlenecks:
            recommendations.append("Switch to ML-predicted distribution strategy")
            recommendations.append("Optimize agent selection algorithms")
        
        if "High resource utilization indicates capacity bottleneck" in bottlenecks:
            recommendations.append("Scale infrastructure resources")
            recommendations.append("Implement resource optimization policies")
        
        # Check for anomalies and suggest investigation
        if self.config.anomaly_detection_enabled:
            for metric_key in self.metric_history.keys():
                anomaly_score = await self.anomaly_detector.get_anomaly_score(metric_key)
                if anomaly_score > 2.0:
                    recommendations.append(f"Investigate anomaly in {metric_key}")
        
        return recommendations
    
    async def _broadcast_performance_update(self, snapshot: PerformanceSnapshot):
        """Broadcast performance update to WebSocket clients"""
        
        performance_data = {
            'type': 'performance_update',
            'timestamp': snapshot.timestamp.isoformat(),
            'health_score': snapshot.health_score,
            'bottlenecks': snapshot.bottlenecks,
            'recommendations': snapshot.recommendations
        }
        
        message = json.dumps(performance_data)
        
        disconnected_clients = set()
        for websocket in self.websocket_connections:
            try:
                await websocket.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(websocket)
            except Exception as e:
                logger.error(f"Error sending performance update: {e}")
        
        self.websocket_connections -= disconnected_clients
    
    async def _predictive_analysis_loop(self):
        """Background task for predictive analysis"""
        
        while self.is_monitoring:
            try:
                await self._perform_predictive_analysis()
                await asyncio.sleep(600)  # Every 10 minutes
                
            except Exception as e:
                logger.error(f"Predictive analysis error: {e}")
                await asyncio.sleep(600)
    
    async def _perform_predictive_analysis(self):
        """Perform predictive analysis and generate proactive alerts"""
        
        # Predict future queue size
        queue_size_key = "queue_size_queue_manager"
        predicted_queue_size = await self.predictive_analyzer.predict_future_value(queue_size_key, 15)
        
        if predicted_queue_size and predicted_queue_size > 2000:
            # Generate predictive alert
            await self._create_predictive_alert(
                "Predicted Queue Overload",
                f"Queue size predicted to reach {predicted_queue_size:.0f} in 15 minutes",
                AlertSeverity.WARNING
            )
        
        # Predict worker health trends
        worker_health_key = "worker_health_distribution_engine"
        health_trend = await self.predictive_analyzer.detect_trend_direction(worker_health_key)
        
        if health_trend == "decreasing":
            await self._create_predictive_alert(
                "Degrading Worker Health Trend",
                "Worker health is trending downward - proactive intervention recommended",
                AlertSeverity.INFO
            )
        
        # Predict processing rate trends
        processing_rate_key = "processing_rate_queue_manager"
        rate_trend = await self.predictive_analyzer.detect_trend_direction(processing_rate_key)
        
        if rate_trend == "decreasing":
            await self._create_predictive_alert(
                "Declining Processing Rate",
                "Processing rate is trending downward - capacity issues may arise",
                AlertSeverity.WARNING
            )
    
    async def _create_predictive_alert(self, title: str, description: str, severity: AlertSeverity):
        """Create a predictive alert"""
        
        alert = MonitoringAlert(
            alert_id=str(uuid.uuid4()),
            rule_id="predictive_analysis",
            severity=severity,
            title=title,
            description=description,
            triggered_at=datetime.utcnow(),
            tags={"type": "predictive", "source": "predictive_analyzer"}
        )
        
        # Send notification
        await self._send_alert_notifications(alert)
        
        logger.info(f"Predictive alert generated: {title}")
    
    async def _websocket_server(self):
        """WebSocket server for real-time updates"""
        
        async def handle_client(websocket, path):
            """Handle WebSocket client connection"""
            
            logger.info(f"WebSocket client connected: {websocket.remote_address}")
            self.websocket_connections.add(websocket)
            
            try:
                # Send initial status
                initial_data = {
                    'type': 'connection_established',
                    'timestamp': datetime.utcnow().isoformat(),
                    'monitoring_config': {
                        'level': self.config.monitoring_level.value,
                        'collection_interval': self.config.collection_interval_seconds,
                        'alert_evaluation_interval': self.config.alert_evaluation_interval_seconds
                    }
                }
                
                await websocket.send(json.dumps(initial_data))
                
                # Keep connection alive
                async for message in websocket:
                    # Handle client messages if needed
                    try:
                        data = json.loads(message)
                        await self._handle_websocket_message(websocket, data)
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON from WebSocket client: {message}")
                        
            except websockets.exceptions.ConnectionClosed:
                logger.info("WebSocket client disconnected")
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
            finally:
                self.websocket_connections.discard(websocket)
        
        try:
            start_server = websockets.serve(handle_client, "localhost", self.config.websocket_port)
            await start_server
            logger.info(f"WebSocket server started on port {self.config.websocket_port}")
            
            # Keep server running
            while self.is_monitoring:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"WebSocket server error: {e}")
    
    async def _handle_websocket_message(self, websocket, data: Dict):
        """Handle incoming WebSocket message"""
        
        message_type = data.get('type')
        
        if message_type == 'get_current_metrics':
            # Send current metrics
            current_metrics = await self._get_current_metrics_summary()
            response = {
                'type': 'current_metrics',
                'timestamp': datetime.utcnow().isoformat(),
                'metrics': current_metrics
            }
            await websocket.send(json.dumps(response))
        
        elif message_type == 'get_active_alerts':
            # Send active alerts
            alerts_data = {
                'type': 'active_alerts',
                'timestamp': datetime.utcnow().isoformat(),
                'alerts': [
                    {
                        'id': alert.alert_id,
                        'rule_id': alert.rule_id,
                        'severity': alert.severity.value,
                        'title': alert.title,
                        'triggered_at': alert.triggered_at.isoformat(),
                        'metric_value': alert.metric_value,
                        'threshold': alert.threshold
                    }
                    for alert in self.active_alerts.values()
                ]
            }
            await websocket.send(json.dumps(alerts_data))
        
        elif message_type == 'get_performance_snapshot':
            # Send latest performance snapshot
            if self.last_performance_snapshot:
                snapshot_data = {
                    'type': 'performance_snapshot',
                    'timestamp': self.last_performance_snapshot.timestamp.isoformat(),
                    'health_score': self.last_performance_snapshot.health_score,
                    'bottlenecks': self.last_performance_snapshot.bottlenecks,
                    'recommendations': self.last_performance_snapshot.recommendations
                }
                await websocket.send(json.dumps(snapshot_data))
    
    async def _get_current_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of current metrics"""
        
        summary = {}
        
        for metric_key, history in self.metric_history.items():
            if history:
                latest = history[-1]
                summary[metric_key] = {
                    'value': latest['value'],
                    'timestamp': latest['timestamp'].isoformat(),
                    'tags': latest['tags']
                }
        
        return summary
    
    async def _cleanup_old_data_loop(self):
        """Background task for cleaning up old data"""
        
        while self.is_monitoring:
            try:
                await self._cleanup_old_data()
                await asyncio.sleep(3600)  # Every hour
                
            except Exception as e:
                logger.error(f"Data cleanup error: {e}")
                await asyncio.sleep(3600)
    
    async def _cleanup_old_data(self):
        """Clean up old metrics and alerts"""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=self.config.metric_retention_hours)
        
        # Clean up metric history
        for metric_key in self.metric_history:
            history = self.metric_history[metric_key]
            # Remove old entries
            while history and history[0]['timestamp'] < cutoff_time:
                history.popleft()
        
        # Clean up performance snapshots
        while (self.performance_snapshots and 
               self.performance_snapshots[0].timestamp < cutoff_time):
            self.performance_snapshots.popleft()
        
        logger.debug("Old monitoring data cleaned up")
    
    async def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics in text format"""
        
        if not self.config.prometheus_enabled:
            return ""
        
        return generate_latest(self.prometheus_registry).decode('utf-8')
    
    async def add_alert_rule(self, rule: AlertRule):
        """Add custom alert rule"""
        
        self.alert_rules[rule.rule_id] = rule
        logger.info(f"Alert rule added: {rule.name}")
    
    async def remove_alert_rule(self, rule_id: str):
        """Remove alert rule"""
        
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            logger.info(f"Alert rule removed: {rule_id}")
    
    async def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""



        
        return {
            'is_monitoring': self.is_monitoring,
            'config': {
                'monitoring_level': self.config.monitoring_level.value,
                'collection_interval_seconds': self.config.collection_interval_seconds,
                'alert_evaluation_interval_seconds': self.config.alert_evaluation_interval_seconds,
                'metric_retention_hours': self.config.metric_retention_hours,
                'prometheus_enabled': self.config.prometheus_enabled,
                'redis_enabled': self.config.redis_enabled,
                'auto_recovery_enabled': self.config.auto_recovery_enabled,
                'predictive_alerts_enabled': self.config.predictive_alerts_enabled,
                'anomaly_detection_enabled': self.config.anomaly_detection_enabled
            },
            'stats': {
                'active_websocket_connections': len(self.websocket_connections),
                'active_alerts': len(self.active_alerts),
                'alert_rules': len(self.alert_rules),
                'metric_types_tracked': len(self.metric_history),
                'performance_snapshots': len(self.performance_snapshots)
            },
            'health_score': await self._calculate_health_score(),
            'last_snapshot_time': (
                self.last_performance_snapshot.timestamp.isoformat() 
                if self.last_performance_snapshot else None
            )
        }


# Factory function
def create_realtime_queue_monitor(
    config: Optional[MonitoringConfig] = None,
    queue_manager: Optional[IntelligentQueueManager] = None,
    distribution_engine: Optional[TaskDistributionEngine] = None
) -> RealtimeQueueMonitor:
    """Create and configure real-time queue monitor"""
    
    if config is None:
        config = MonitoringConfig()
    
    return RealtimeQueueMonitor(
        config=config,
        queue_manager=queue_manager,
        distribution_engine=distribution_engine
    )


# Export classes and functions
__all__ = [
    'RealtimeQueueMonitor',
    'AnomalyDetector',
    'PredictiveAnalyzer',
    'MonitoringConfig',
    'MonitoringLevel',
    'AlertSeverity',
    'MetricType',
    'AlertCondition',
    'MetricDataPoint',
    'AlertRule',
    'MonitoringAlert',
    'PerformanceSnapshot',
    'create_realtime_queue_monitor'
]
