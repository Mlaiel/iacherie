"""Real-time Analytics Processor - Live Analytics Engine
=====================================================

High-performance real-time analytics processing with streaming aggregations,
live dashboards, alerting, and sub-second response times.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from collections import defaultdict, deque
import statistics

try:
    import sqlalchemy as sa
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import declarative_base, sessionmaker
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

import redis.asyncio as redis


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class MetricType(Enum):
    """Real-time metric types."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"


@dataclass
class RealTimeMetric:
    """Real-time metric definition."""
    id: str
    name: str
    metric_type: MetricType
    description: str
    aggregation_window: timedelta = timedelta(minutes=1)
    retention_period: timedelta = timedelta(hours=24)
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricDataPoint:
    """Single metric data point."""
    metric_id: str
    timestamp: datetime
    value: float
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """Real-time alert."""
    id: str
    metric_id: str
    severity: AlertSeverity
    message: str
    current_value: float
    threshold_value: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    resolved: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Dashboard:
    """Real-time dashboard configuration."""
    id: str
    name: str
    metric_ids: List[str]
    refresh_interval: timedelta = timedelta(seconds=5)
    layout: Dict[str, Any] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class RealTimeAnalyticsProcessor:
    """High-performance real-time analytics processing engine."""
    
    def __init__(
        self,
        redis_url: str,
        database_url: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Redis setup for real-time data
        self.redis_url = redis_url
        self.redis_client = None
        
        # Database setup for persistence
        self.database_url = database_url
        self.engine = None
        self.async_session = None
        
        if database_url and SQLALCHEMY_AVAILABLE:
            self.engine = create_async_engine(database_url)
            self.async_session = sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )
        
        # Analytics state
        self.metrics: Dict[str, RealTimeMetric] = {}
        self.dashboards: Dict[str, Dashboard] = {}
        self.active_alerts: Dict[str, Alert] = {}
        
        # In-memory data stores for performance
        self.metric_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.aggregated_data: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        # Processing workers
        self.workers_running = False
        self.processing_tasks: List[asyncio.Task] = []
        
        # WebSocket connections for live updates
        self.websocket_connections: Set[Any] = set()
        
        # Performance tracking
        self.processor_metrics = {
            'data_points_processed': 0,
            'alerts_generated': 0,
            'dashboard_updates': 0,
            'average_processing_latency': 0.0,
            'throughput_per_second': 0.0
        }
        
        # Setup built-in metrics
        self._setup_built_in_metrics()
    
    async def initialize(self):
        """Initialize the real-time analytics processor."""
        # Initialize Redis
        self.redis_client = redis.from_url(self.redis_url)
        
        # Initialize database if configured
        if self.engine and SQLALCHEMY_AVAILABLE:
            # Create tables if needed
            pass
        
        # Start processing workers
        await self._start_workers()
        
        self.logger.info("Real-time analytics processor initialized")
    
    def _setup_built_in_metrics(self):
        """Setup built-in metrics."""
        # User activity metrics
        user_activity_metric = RealTimeMetric(
            id="user_activity_rate",
            name="User Activity Rate",
            metric_type=MetricType.RATE,
            description="Rate of user activities per minute",
            aggregation_window=timedelta(minutes=1),
            alert_thresholds={
                'low': 10.0,
                'high': 1000.0
            }
        )
        
        # Content engagement metrics
        engagement_metric = RealTimeMetric(
            id="content_engagement",
            name="Content Engagement Score",
            metric_type=MetricType.GAUGE,
            description="Real-time content engagement score",
            aggregation_window=timedelta(minutes=5),
            alert_thresholds={
                'low': 0.3
            }
        )
        
        # System performance metrics
        response_time_metric = RealTimeMetric(
            id="api_response_time",
            name="API Response Time",
            metric_type=MetricType.TIMER,
            description="API response time in milliseconds",
            aggregation_window=timedelta(minutes=1),
            alert_thresholds={
                'high': 1000.0,
                'critical': 5000.0
            }
        )
        
        # Revenue metrics
        revenue_metric = RealTimeMetric(
            id="revenue_per_minute",
            name="Revenue Per Minute",
            metric_type=MetricType.COUNTER,
            description="Revenue generated per minute",
            aggregation_window=timedelta(minutes=1),
            alert_thresholds={
                'low': 50.0
            }
        )
        
        # Register built-in metrics
        for metric in [user_activity_metric, engagement_metric, response_time_metric, revenue_metric]:
            self.metrics[metric.id] = metric
    
    async def register_metric(self, metric: RealTimeMetric):
        """Register a new real-time metric."""
        self.metrics[metric.id] = metric
        self.logger.info(f"Registered real-time metric: {metric.name}")
    
    async def ingest_data_point(self, data_point: MetricDataPoint):
        """Ingest a single data point for real-time processing."""
        start_time = time.time()
        
        try:
            # Validate metric exists
            if data_point.metric_id not in self.metrics:
                self.logger.warning(f"Unknown metric: {data_point.metric_id}")
                return
            
            # Store in memory for fast access
            self.metric_data[data_point.metric_id].append(data_point)
            
            # Store in Redis for persistence and distribution
            await self._store_data_point_redis(data_point)
            
            # Update aggregations
            await self._update_aggregations(data_point)
            
            # Check alert conditions
            await self._check_alert_conditions(data_point)
            
            # Notify live dashboards
            await self._notify_dashboards(data_point)
            
            # Update metrics
            processing_time = time.time() - start_time
            self.processor_metrics['data_points_processed'] += 1
            
            # Update average processing latency
            current_avg = self.processor_metrics['average_processing_latency']
            total_points = self.processor_metrics['data_points_processed']
            self.processor_metrics['average_processing_latency'] = (
                (current_avg * (total_points - 1) + processing_time) / total_points
            )
            
        except Exception as e:
            self.logger.error(f"Error ingesting data point: {e}")
    
    async def ingest_batch(self, data_points: List[MetricDataPoint]):
        """Ingest a batch of data points for high throughput."""
        start_time = time.time()
        
        try:
            # Process batch in parallel
            tasks = [self.ingest_data_point(dp) for dp in data_points]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Update throughput metrics
            processing_time = time.time() - start_time
            if processing_time > 0:
                throughput = len(data_points) / processing_time
                self.processor_metrics['throughput_per_second'] = throughput
            
            self.logger.debug(f"Processed batch of {len(data_points)} data points in {processing_time:.3f}s")
            
        except Exception as e:
            self.logger.error(f"Error processing batch: {e}")
    
    async def _store_data_point_redis(self, data_point: MetricDataPoint):
        """Store data point in Redis for real-time access."""
        try:
            key = f"metric:{data_point.metric_id}:data"
            value = {
                'timestamp': data_point.timestamp.isoformat(),
                'value': data_point.value,
                'tags': data_point.tags,
                'metadata': data_point.metadata
            }
            
            # Store in sorted set with timestamp as score
            await self.redis_client.zadd(
                key,
                {json.dumps(value): data_point.timestamp.timestamp()}
            )
            
            # Set expiration based on metric retention
            metric = self.metrics[data_point.metric_id]
            expire_seconds = int(metric.retention_period.total_seconds())
            await self.redis_client.expire(key, expire_seconds)
            
        except Exception as e:
            self.logger.error(f"Error storing data point in Redis: {e}")
    
    async def _update_aggregations(self, data_point: MetricDataPoint):
        """Update real-time aggregations."""
        metric = self.metrics[data_point.metric_id]
        metric_id = data_point.metric_id
        
        # Get current aggregation window
        window_key = self._get_window_key(data_point.timestamp, metric.aggregation_window)
        
        # Update aggregations based on metric type
        if metric.metric_type == MetricType.COUNTER:
            # Sum values in window
            current_sum = self.aggregated_data[metric_id].get(f"sum_{window_key}", 0.0)
            self.aggregated_data[metric_id][f"sum_{window_key}"] = current_sum + data_point.value
            
        elif metric.metric_type == MetricType.GAUGE:
            # Latest value
            self.aggregated_data[metric_id][f"latest_{window_key}"] = data_point.value
            
        elif metric.metric_type == MetricType.TIMER:
            # Average, min, max, p95
            timer_values = self.aggregated_data[metric_id].get(f"timer_values_{window_key}", [])
            timer_values.append(data_point.value)
            
            if len(timer_values) > 1000:  # Limit memory usage
                timer_values = timer_values[-1000:]
            
            self.aggregated_data[metric_id][f"timer_values_{window_key}"] = timer_values
            self.aggregated_data[metric_id][f"avg_{window_key}"] = statistics.mean(timer_values)
            self.aggregated_data[metric_id][f"min_{window_key}"] = min(timer_values)
            self.aggregated_data[metric_id][f"max_{window_key}"] = max(timer_values)
            
            if len(timer_values) > 1:
                self.aggregated_data[metric_id][f"p95_{window_key}"] = statistics.quantiles(timer_values, n=20)[18]
            
        elif metric.metric_type == MetricType.RATE:
            # Calculate rate (events per time unit)
            rate_key = f"rate_count_{window_key}"
            current_count = self.aggregated_data[metric_id].get(rate_key, 0)
            self.aggregated_data[metric_id][rate_key] = current_count + 1
            
            # Calculate rate per minute
            window_minutes = metric.aggregation_window.total_seconds() / 60
            rate_per_minute = self.aggregated_data[metric_id][rate_key] / window_minutes
            self.aggregated_data[metric_id][f"rate_{window_key}"] = rate_per_minute
        
        elif metric.metric_type == MetricType.HISTOGRAM:
            # Histogram buckets
            buckets = self.aggregated_data[metric_id].get(f"histogram_{window_key}", defaultdict(int))
            bucket = self._get_histogram_bucket(data_point.value)
            buckets[bucket] += 1
            self.aggregated_data[metric_id][f"histogram_{window_key}"] = buckets
        
        # Store aggregated data in Redis for distribution
        await self._store_aggregations_redis(metric_id, window_key)
    
    def _get_window_key(self, timestamp: datetime, window_size: timedelta) -> str:
        """Generate window key for time-based aggregation."""
        window_seconds = int(window_size.total_seconds())
        window_start = int(timestamp.timestamp()) // window_seconds * window_seconds
        return str(window_start)
    
    def _get_histogram_bucket(self, value: float) -> str:
        """Get histogram bucket for value."""
        # Simple logarithmic buckets
        if value <= 0:
            return "0"
        elif value <= 1:
            return "1"
        elif value <= 10:
            return "10"
        elif value <= 100:
            return "100"
        elif value <= 1000:
            return "1000"
        else:
            return "1000+"
    
    async def _store_aggregations_redis(self, metric_id: str, window_key: str):
        """Store aggregated data in Redis."""
        try:
            aggregations = self.aggregated_data[metric_id]
            window_aggregations = {
                k: v for k, v in aggregations.items() 
                if window_key in k
            }
            
            if window_aggregations:
                key = f"aggregations:{metric_id}:{window_key}"
                await self.redis_client.hset(key, mapping={
                    k: json.dumps(v) if isinstance(v, (dict, list)) else str(v)
                    for k, v in window_aggregations.items()
                })
                
                # Set expiration
                metric = self.metrics[metric_id]
                expire_seconds = int(metric.retention_period.total_seconds())
                await self.redis_client.expire(key, expire_seconds)
                
        except Exception as e:
            self.logger.error(f"Error storing aggregations in Redis: {e}")
    
    async def _check_alert_conditions(self, data_point: MetricDataPoint):
        """Check if data point triggers any alerts."""
        metric = self.metrics[data_point.metric_id]
        
        for threshold_name, threshold_value in metric.alert_thresholds.items():
            should_alert = False
            severity = AlertSeverity.WARNING
            
            if threshold_name == "high" and data_point.value > threshold_value:
                should_alert = True
                severity = AlertSeverity.WARNING
            elif threshold_name == "critical" and data_point.value > threshold_value:
                should_alert = True
                severity = AlertSeverity.CRITICAL
            elif threshold_name == "low" and data_point.value < threshold_value:
                should_alert = True
                severity = AlertSeverity.WARNING
            elif threshold_name == "emergency" and data_point.value > threshold_value:
                should_alert = True
                severity = AlertSeverity.EMERGENCY
            
            if should_alert:
                await self._create_alert(metric, data_point, threshold_name, threshold_value, severity)
    
    async def _create_alert(
        self, 
        metric: RealTimeMetric, 
        data_point: MetricDataPoint, 
        threshold_name: str, 
        threshold_value: float, 
        severity: AlertSeverity
    ):
        """Create and process an alert."""
        alert_id = str(uuid.uuid4())
        
        # Check for duplicate alerts (avoid spam)
        recent_alerts = [
            alert for alert in self.active_alerts.values()
            if (alert.metric_id == metric.id and 
                (datetime.utcnow() - alert.timestamp).total_seconds() < 300)  # 5 minutes
        ]
        
        if len(recent_alerts) >= 3:  # Max 3 alerts per 5 minutes
            return
        
        alert = Alert(
            id=alert_id,
            metric_id=metric.id,
            severity=severity,
            message=f"{metric.name} {threshold_name} threshold exceeded",
            current_value=data_point.value,
            threshold_value=threshold_value,
            metadata={
                'threshold_name': threshold_name,
                'metric_name': metric.name,
                'tags': data_point.tags
            }
        )
        
        self.active_alerts[alert_id] = alert
        
        # Store alert in Redis for distribution
        await self._store_alert_redis(alert)
        
        # Send notifications
        await self._send_alert_notification(alert)
        
        self.processor_metrics['alerts_generated'] += 1
        self.logger.warning(f"Alert created: {alert.message} (value: {data_point.value})")
    
    async def _store_alert_redis(self, alert: Alert):
        """Store alert in Redis."""
        try:
            key = f"alert:{alert.id}"
            value = {
                'metric_id': alert.metric_id,
                'severity': alert.severity.value,
                'message': alert.message,
                'current_value': alert.current_value,
                'threshold_value': alert.threshold_value,
                'timestamp': alert.timestamp.isoformat(),
                'acknowledged': alert.acknowledged,
                'resolved': alert.resolved,
                'metadata': alert.metadata
            }
            
            await self.redis_client.setex(key, 86400, json.dumps(value))  # 24 hour expiry
            
            # Add to active alerts list
            await self.redis_client.zadd(
                "active_alerts",
                {alert.id: alert.timestamp.timestamp()}
            )
            
        except Exception as e:
            self.logger.error(f"Error storing alert in Redis: {e}")
    
    async def _send_alert_notification(self, alert: Alert):
        """Send alert notification."""
        # This would integrate with notification systems
        notification_data = {
            'type': 'real_time_alert',
            'alert_id': alert.id,
            'severity': alert.severity.value,
            'message': alert.message,
            'metric_id': alert.metric_id,
            'current_value': alert.current_value,
            'threshold_value': alert.threshold_value,
            'timestamp': alert.timestamp.isoformat()
        }
        
        # Store in Redis for pickup by notification service
        await self.redis_client.lpush('alert_notifications', json.dumps(notification_data))
        
        # Send to live dashboard connections
        await self._broadcast_to_dashboards('alert', notification_data)
    
    async def _notify_dashboards(self, data_point: MetricDataPoint):
        """Notify live dashboards of new data."""
        # Find dashboards that include this metric
        relevant_dashboards = [
            dashboard for dashboard in self.dashboards.values()
            if data_point.metric_id in dashboard.metric_ids
        ]
        
        if relevant_dashboards:
            update_data = {
                'type': 'metric_update',
                'metric_id': data_point.metric_id,
                'timestamp': data_point.timestamp.isoformat(),
                'value': data_point.value,
                'tags': data_point.tags
            }
            
            await self._broadcast_to_dashboards('metric_update', update_data)
            self.processor_metrics['dashboard_updates'] += 1
    
    async def _broadcast_to_dashboards(self, message_type: str, data: Dict[str, Any]):
        """Broadcast message to connected dashboards."""
        if self.websocket_connections:
            message = {
                'type': message_type,
                'data': data,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Send to all connected WebSocket clients
            disconnected = set()
            for ws in self.websocket_connections:
                try:
                    await ws.send(json.dumps(message))
                except:
                    disconnected.add(ws)
            
            # Clean up disconnected clients
            self.websocket_connections -= disconnected
    
    async def create_dashboard(self, dashboard: Dashboard):
        """Create a real-time dashboard."""
        self.dashboards[dashboard.id] = dashboard
        self.logger.info(f"Created real-time dashboard: {dashboard.name}")
    
    async def get_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """Get current data for a dashboard."""
        if dashboard_id not in self.dashboards:
            return {}
        
        dashboard = self.dashboards[dashboard_id]
        dashboard_data = {
            'dashboard_id': dashboard_id,
            'name': dashboard.name,
            'metrics': {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Get current data for each metric
        for metric_id in dashboard.metric_ids:
            if metric_id in self.metrics:
                metric_data = await self._get_current_metric_data(metric_id)
                dashboard_data['metrics'][metric_id] = metric_data
        
        return dashboard_data
    
    async def _get_current_metric_data(self, metric_id: str) -> Dict[str, Any]:
        """Get current aggregated data for a metric."""
        metric = self.metrics[metric_id]
        current_time = datetime.utcnow()
        window_key = self._get_window_key(current_time, metric.aggregation_window)
        
        # Get aggregated data for current window
        aggregations = self.aggregated_data[metric_id]
        current_data = {
            'metric_id': metric_id,
            'metric_name': metric.name,
            'metric_type': metric.metric_type.value,
            'current_window': window_key,
            'aggregations': {}
        }
        
        # Extract relevant aggregations for current window
        for key, value in aggregations.items():
            if window_key in key:
                agg_type = key.replace(f"_{window_key}", "")
                current_data['aggregations'][agg_type] = value
        
        # Get recent raw data points
        if metric_id in self.metric_data:
            recent_points = list(self.metric_data[metric_id])[-10:]  # Last 10 points
            current_data['recent_points'] = [
                {
                    'timestamp': dp.timestamp.isoformat(),
                    'value': dp.value,
                    'tags': dp.tags
                }
                for dp in recent_points
            ]
        
        return current_data
    
    async def get_metric_history(
        self, 
        metric_id: str, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """Get historical data for a metric."""
        try:
            key = f"metric:{metric_id}:data"
            
            # Get data from Redis sorted set by timestamp range
            data_points = await self.redis_client.zrangebyscore(
                key,
                start_time.timestamp(),
                end_time.timestamp(),
                withscores=True
            )
            
            history = []
            for data_json, timestamp in data_points:
                data = json.loads(data_json)
                history.append({
                    'timestamp': datetime.fromtimestamp(timestamp).isoformat(),
                    'value': data['value'],
                    'tags': data['tags']
                })
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting metric history: {e}")
            return []
    
    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge an alert."""
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        alert.acknowledged = True
        alert.metadata['acknowledged_by'] = user_id
        alert.metadata['acknowledged_at'] = datetime.utcnow().isoformat()
        
        # Update in Redis
        await self._store_alert_redis(alert)
        
        self.logger.info(f"Alert acknowledged: {alert_id} by {user_id}")
        return True
    
    async def resolve_alert(self, alert_id: str, user_id: str, resolution_notes: str = "") -> bool:
        """Resolve an alert."""
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        alert.resolved = True
        alert.metadata['resolved_by'] = user_id
        alert.metadata['resolved_at'] = datetime.utcnow().isoformat()
        alert.metadata['resolution_notes'] = resolution_notes
        
        # Update in Redis
        await self._store_alert_redis(alert)
        
        # Remove from active alerts
        del self.active_alerts[alert_id]
        
        self.logger.info(f"Alert resolved: {alert_id} by {user_id}")
        return True
    
    async def register_websocket(self, websocket):
        """Register WebSocket connection for live updates."""
        self.websocket_connections.add(websocket)
        self.logger.debug("WebSocket connection registered for real-time updates")
    
    async def unregister_websocket(self, websocket):
        """Unregister WebSocket connection."""
        self.websocket_connections.discard(websocket)
        self.logger.debug("WebSocket connection unregistered")
    
    # Worker management
    async def _start_workers(self):
        """Start background processing workers."""
        self.workers_running = True
        
        # Start cleanup worker
        cleanup_task = asyncio.create_task(self._cleanup_worker())
        self.processing_tasks.append(cleanup_task)
        
        # Start metrics calculation worker
        metrics_task = asyncio.create_task(self._metrics_worker())
        self.processing_tasks.append(metrics_task)
        
        # Start alert management worker
        alert_task = asyncio.create_task(self._alert_management_worker())
        self.processing_tasks.append(alert_task)
        
        self.logger.info("Real-time processing workers started")
    
    async def _stop_workers(self):
        """Stop background workers."""
        self.workers_running = False
        
        for task in self.processing_tasks:
            task.cancel()
        
        if self.processing_tasks:
            await asyncio.gather(*self.processing_tasks, return_exceptions=True)
        
        self.processing_tasks.clear()
        self.logger.info("Real-time processing workers stopped")
    
    async def _cleanup_worker(self):
        """Background worker for data cleanup."""
        while self.workers_running:
            try:
                current_time = datetime.utcnow()
                
                # Clean up old aggregated data
                for metric_id, aggregations in list(self.aggregated_data.items()):
                    if metric_id in self.metrics:
                        retention_period = self.metrics[metric_id].retention_period
                        cutoff_time = current_time - retention_period
                        
                        # Remove old window data
                        keys_to_remove = []
                        for key in aggregations.keys():
                            if "_" in key:
                                try:
                                    window_timestamp = int(key.split("_")[-1])
                                    if datetime.fromtimestamp(window_timestamp) < cutoff_time:
                                        keys_to_remove.append(key)
                                except:
                                    pass
                        
                        for key in keys_to_remove:
                            del aggregations[key]
                
                # Clean up resolved alerts older than 24 hours
                alerts_to_remove = []
                for alert_id, alert in self.active_alerts.items():
                    if (alert.resolved and 
                        (current_time - alert.timestamp).total_seconds() > 86400):
                        alerts_to_remove.append(alert_id)
                
                for alert_id in alerts_to_remove:
                    del self.active_alerts[alert_id]
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cleanup worker error: {e}")
                await asyncio.sleep(60)
    
    async def _metrics_worker(self):
        """Background worker for performance metrics calculation."""
        while self.workers_running:
            try:
                # Calculate throughput
                current_time = time.time()
                if hasattr(self, '_last_metrics_time'):
                    time_diff = current_time - self._last_metrics_time
                    if time_diff > 0:
                        points_diff = (self.processor_metrics['data_points_processed'] - 
                                     getattr(self, '_last_points_count', 0))
                        self.processor_metrics['throughput_per_second'] = points_diff / time_diff
                
                self._last_metrics_time = current_time
                self._last_points_count = self.processor_metrics['data_points_processed']
                
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Metrics worker error: {e}")
                await asyncio.sleep(30)
    
    async def _alert_management_worker(self):
        """Background worker for alert management."""
        while self.workers_running:
            try:
                # Auto-resolve alerts that are no longer triggered
                current_time = datetime.utcnow()
                
                for alert in list(self.active_alerts.values()):
                    if not alert.resolved and not alert.acknowledged:
                        # Check if condition is still true
                        metric_id = alert.metric_id
                        if metric_id in self.metric_data and self.metric_data[metric_id]:
                            latest_point = self.metric_data[metric_id][-1]
                            
                            # Simple check - if latest value is back to normal, auto-resolve
                            threshold_name = alert.metadata.get('threshold_name', '')
                            
                            should_auto_resolve = False
                            if threshold_name == "high" and latest_point.value <= alert.threshold_value:
                                should_auto_resolve = True
                            elif threshold_name == "low" and latest_point.value >= alert.threshold_value:
                                should_auto_resolve = True
                            
                            if should_auto_resolve:
                                await self.resolve_alert(alert.id, "system", "Auto-resolved: condition normalized")
                
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Alert management worker error: {e}")
                await asyncio.sleep(60)
    
    def get_processor_metrics(self) -> Dict[str, Any]:
        """Get real-time processor metrics."""
        return {
            **self.processor_metrics,
            'registered_metrics': len(self.metrics),
            'active_dashboards': len(self.dashboards),
            'active_alerts': len(self.active_alerts),
            'websocket_connections': len(self.websocket_connections),
            'memory_usage': {
                'metric_data_points': sum(len(data) for data in self.metric_data.values()),
                'aggregated_windows': sum(len(agg) for agg in self.aggregated_data.values())
            }
        }
    
    async def shutdown(self):
        """Shutdown the real-time analytics processor."""
        await self._stop_workers()
        
        if self.redis_client:
            await self.redis_client.close()
        
        self.logger.info("Real-time analytics processor shutdown complete")


# Example usage
if __name__ == "__main__":
    async def main():
        # Initialize processor
        processor = RealTimeAnalyticsProcessor(
            redis_url="redis://localhost:6379",
            database_url="postgresql+asyncpg://user:pass@localhost/db"
        )
        
        await processor.initialize()
        
        # Create a custom metric
        custom_metric = RealTimeMetric(
            id="custom_engagement",
            name="Custom Engagement Metric",
            metric_type=MetricType.GAUGE,
            description="Custom engagement tracking",
            alert_thresholds={'low': 0.5, 'high': 0.9}
        )
        
        await processor.register_metric(custom_metric)
        
        # Create dashboard
        dashboard = Dashboard(
            id="main_dashboard",
            name="Main Analytics Dashboard",
            metric_ids=["user_activity_rate", "content_engagement", "custom_engagement"],
            refresh_interval=timedelta(seconds=5)
        )
        
        await processor.create_dashboard(dashboard)
        
        # Simulate data ingestion
        for i in range(10):
            data_point = MetricDataPoint(
                metric_id="custom_engagement",
                timestamp=datetime.utcnow(),
                value=0.3 + (i * 0.1),  # Will trigger low alert initially
                tags={"platform": "youtube", "region": "us"}
            )
            
            await processor.ingest_data_point(data_point)
            await asyncio.sleep(1)
        
        # Get dashboard data
        dashboard_data = await processor.get_dashboard_data("main_dashboard")
        print(f"Dashboard data: {json.dumps(dashboard_data, indent=2)}")
        
        # Get processor metrics
        metrics = processor.get_processor_metrics()
        print(f"Processor metrics: {metrics}")
        
        await processor.shutdown()
    
    asyncio.run(main())