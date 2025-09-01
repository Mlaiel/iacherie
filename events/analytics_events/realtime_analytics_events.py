"""Realtime Analytics Events Module

Real-time analytics streaming, monitoring, and alerting for multi-format content creators.
Provides live dashboard updates, anomaly detection, and instant insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
⚠️  WARNING: This code and concept are proprietary to Fahed Mlaiel.
    Any unauthorized use, copying, or distribution without explicit written 
    permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
                Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler
import websockets
import redis.asyncio as redis
from collections import deque, defaultdict
import aiohttp

from ...core.events.base_event import BaseEvent, BaseEventHandler
from ...core.cache import CacheManager
from ...core.database import DatabaseManager
from ...core.logging import get_logger
from ...ml.models.anomaly_detector import AnomalyDetector
from ...ai.streaming.realtime_processor import RealtimeProcessor
from ...utils.metrics import MetricsCalculator
from ...config import settings

logger = get_logger(__name__)


class MetricType(Enum):
    """
Types of real-time metrics"""

    ENGAGEMENT = "engagement"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    VIEWS = "views"
    LIKES = "likes"
    COMMENTS = "comments"
    SHARES = "shares"
    SAVES = "saves"
    FOLLOWERS = "followers"
    REVENUE = "revenue"
    CONVERSION = "conversion"
    RETENTION = "retention"
    VIRALITY = "virality"
    SENTIMENT = "sentiment"


class AlertSeverity(Enum):
    """Alert severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class StreamingChannel(Enum):
    """Real-time streaming channels"""

    METRICS = "metrics"
    ALERTS = "alerts"
    EVENTS = "events"
    ANOMALIES = "anomalies"
    INSIGHTS = "insights"
    NOTIFICATIONS = "notifications"
    DASHBOARD = "dashboard"
    PREDICTIONS = "predictions"


class AnomalyType(Enum):
    """Types of anomalies to detect"""

    SPIKE = "spike"
    DROP = "drop"
    TREND_CHANGE = "trend_change"
    OUTLIER = "outlier"
    PATTERN_BREAK = "pattern_break"
    SEASONAL_DEVIATION = "seasonal_deviation"
    CORRELATION_BREAK = "correlation_break"


@dataclass
class RealtimeAnalyticsEvent(BaseEvent):
    """Represents a real-time analytics event"""
    creator_id: str
    platform: str
    content_id: Optional[str]
    metric_type: MetricType
    metric_value: float
    timestamp: datetime
    streaming_data: Dict[str, Any]
    context_data: Dict[str, Any]
    aggregation_window: str  # 1m, 5m, 15m, 1h, etc.
    is_live_content: bool = False
    user_interactions: Optional[List[Dict[str, Any]]] = None
    geolocation_data: Optional[Dict[str, Any]] = None
    device_breakdown: Optional[Dict[str, int]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert realtime analytics event to dictionary"""
        return {
            **asdict(self),
            'metric_type': self.metric_type.value,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class RealtimeAlert:
    """
Represents a real-time alert"""
    alert_id: str
    creator_id: str
    alert_type: str
    severity: AlertSeverity
    title: str
    message: str
    metric_data: Dict[str, Any]
    trigger_conditions: Dict[str, Any]
    recommended_actions: List[str]
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None


@dataclass
class MetricsSnapshot:
    """
Snapshot of current metrics"""
    creator_id: str
    timestamp: datetime
    metrics: Dict[str, float]
    trends: Dict[str, str]  # up, down, stable
    percentage_changes: Dict[str, float]
    anomaly_scores: Dict[str, float]
    predictions: Dict[str, float]


class RealtimeAnalyticsEventHandler(BaseEventHandler):
    """
Handles real-time analytics events with streaming capabilities"""
    
    def __init__(self):
        super().__init__()
        self.cache_manager = CacheManager()
        self.db_manager = DatabaseManager()
        self.metrics_streamer = RealtimeMetricsStreamer()
        self.alert_engine = RealtimeAlertEngine()
        self.dashboard_engine = RealtimeDashboardEngine()
        self.anomaly_detector = RealtimeAnomalyDetector()
        self.redis_client = None
        self.websocket_connections = set()
        
    async def initialize(self):
        """
Initialize real-time components"""
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
        await self.metrics_streamer.initialize()
        await self.alert_engine.initialize()
        
    async def handle(self, event: RealtimeAnalyticsEvent) -> Dict[str, Any]:
        """
Process real-time analytics event with streaming"""
        try:
            # Validate event data
            await self._validate_event(event)
            
            # Stream metrics to real-time channels
            await self.metrics_streamer.stream_metrics(event)
            
            # Check for anomalies
            anomaly_results = await self.anomaly_detector.detect_anomalies(event)
            
            # Generate alerts if needed
            alerts = await self.alert_engine.check_alerts(event, anomaly_results)
            
            # Update dashboard in real-time
            dashboard_update = await self.dashboard_engine.update_dashboard(event)
            
            # Store for historical analysis
            await self._store_realtime_data(event)
            
            # Broadcast to connected clients
            await self._broadcast_updates(event, anomaly_results, alerts)
            
            # Update live predictions
            predictions = await self._update_live_predictions(event)
            
            return {
                'status': 'success',
                'event_id': event.event_id,
                'streaming_status': 'active',
                'anomaly_results': anomaly_results,
                'alerts_generated': len(alerts),
                'dashboard_updated': dashboard_update,
                'predictions': predictions,
                'processing_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing real-time analytics event: {str(e)}")
            await self._handle_error(event, e)
            raise
    
    async def _validate_event(self, event: RealtimeAnalyticsEvent) -> None:
        """Validate real-time analytics event data"""
        required_fields = ['creator_id', 'platform', 'metric_type', 'metric_value']
        for field in required_fields:
            if not getattr(event, field):
                raise ValueError(f"Missing required field: {field}")
        
        if event.metric_type not in MetricType:
            raise ValueError(f"Invalid metric type: {event.metric_type}")
        
        if event.metric_value < 0:
            raise ValueError("Metric value cannot be negative")
    
    async def _store_realtime_data(self, event: RealtimeAnalyticsEvent) -> None:
        """Store real-time data for historical analysis"""
        # Store in time-series database for fast retrieval
        await self.redis_client.zadd(
            f"metrics:{event.creator_id}:{event.metric_type.value}",
            {json.dumps(event.to_dict()): event.timestamp.timestamp()}
        )
        
        # Keep only last 24 hours of data in Redis
        cutoff_time = (datetime.utcnow() - timedelta(hours=24)).timestamp()
        await self.redis_client.zremrangebyscore(
            f"metrics:{event.creator_id}:{event.metric_type.value}",
            0, cutoff_time
        )
        
        # Store in permanent database
        async with self.db_manager.get_session() as session:
            await session.execute(
                """
                INSERT INTO realtime_analytics_events 
                (event_id, creator_id, platform, content_id, metric_type, metric_value,
                 timestamp, streaming_data, context_data, aggregation_window,
                 is_live_content, user_interactions, geolocation_data, device_breakdown)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    event.event_id, event.creator_id, event.platform, event.content_id,
                    event.metric_type.value, event.metric_value, event.timestamp,
                    json.dumps(event.streaming_data), json.dumps(event.context_data),
                    event.aggregation_window, event.is_live_content,
                    json.dumps(event.user_interactions), json.dumps(event.geolocation_data),
                    json.dumps(event.device_breakdown)
                )
            )
    
    async def _broadcast_updates(self, event: RealtimeAnalyticsEvent, 
                               anomaly_results: Dict[str, Any],
                               alerts: List[RealtimeAlert]) -> None:
        """
Broadcast updates to connected WebSocket clients"""
        update_message = {
            'type': 'analytics_update',
            'creator_id': event.creator_id,
            'metric_type': event.metric_type.value,
            'metric_value': event.metric_value,
            'timestamp': event.timestamp.isoformat(),
            'anomalies': anomaly_results,
            'alerts': [alert.title for alert in alerts],
            'platform': event.platform
        }
        
        # Broadcast to creator's dashboard
        await self._send_to_creator_dashboard(event.creator_id, update_message)
        
        # Broadcast to monitoring dashboards
        await self._send_to_monitoring_dashboard(update_message)


class RealtimeMetricsStreamer:
    """
Streams metrics in real-time to various channels"""
    
    def __init__(self):
        self.redis_client = None
        self.websocket_server = None
        self.active_streams = defaultdict(set)
        self.metrics_buffer = defaultdict(deque)
        
    async def initialize(self):
        """
Initialize streaming infrastructure"""
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
        
    async def stream_metrics(self, event: RealtimeAnalyticsEvent) -> None:
        """
Stream metrics to appropriate channels"""
        # Add to metrics buffer
        self.metrics_buffer[event.creator_id].append({
            'metric_type': event.metric_type.value,
            'value': event.metric_value,
            'timestamp': event.timestamp.isoformat(),
            'platform': event.platform
        })
        
        # Keep buffer size manageable
        if len(self.metrics_buffer[event.creator_id]) > 1000:
            self.metrics_buffer[event.creator_id].popleft()
        
        # Stream to Redis channels
        await self._stream_to_redis_channels(event)
        
        # Stream to WebSocket connections
        await self._stream_to_websockets(event)
        
        # Update aggregated metrics
        await self._update_aggregated_metrics(event)
    
    async def _stream_to_redis_channels(self, event: RealtimeAnalyticsEvent) -> None:
        """
Stream to Redis pub/sub channels"""
        channels = [
            f"metrics:{event.creator_id}",
            f"metrics:platform:{event.platform}",
            f"metrics:type:{event.metric_type.value}",
            "metrics:global"
        ]
        
        message = json.dumps(event.to_dict())
        
        for channel in channels:
            await self.redis_client.publish(channel, message)
    
    async def _update_aggregated_metrics(self, event: RealtimeAnalyticsEvent) -> None:
        """Update aggregated metrics for different time windows"""
        windows = ['1m', '5m', '15m', '1h', '6h', '24h']
        
        for window in windows:
            key = f"agg:{window}:{event.creator_id}:{event.metric_type.value}"
            
            # Use Redis time series or sliding window aggregation
            await self.redis_client.hincrby(key, "count", 1)
            await self.redis_client.hincrbyfloat(key, "sum", event.metric_value)
            await self.redis_client.hset(key, "last_update", event.timestamp.timestamp())
            
            # Set expiration based on window size
            expiration = self._get_window_expiration(window)
            await self.redis_client.expire(key, expiration)
    
    def _get_window_expiration(self, window: str) -> int:
        """Get expiration time for aggregation window"""
        window_map = {
            '1m': 300,    # 5 minutes
            '5m': 1800,   # 30 minutes
            '15m': 3600,  # 1 hour
            '1h': 86400,  # 24 hours
            '6h': 604800, # 7 days
            '24h': 2592000 # 30 days
        }
        return window_map.get(window, 3600)


class RealtimeAlertEngine:
    """
Generates real-time alerts based on metric thresholds and patterns"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.redis_client = None
        self.alert_rules = {}
        self.active_alerts = {}
        
    async def initialize(self):
        """
Initialize alert engine"""
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
        await self._load_alert_rules()
        
    async def check_alerts(self, event: RealtimeAnalyticsEvent, 
                          anomaly_results: Dict[str, Any]) -> List[RealtimeAlert]:
        """
Check for alert conditions and generate alerts"""
        alerts = []
        
        # Check threshold-based alerts
        threshold_alerts = await self._check_threshold_alerts(event)
        alerts.extend(threshold_alerts)
        
        # Check anomaly-based alerts
        anomaly_alerts = await self._check_anomaly_alerts(event, anomaly_results)
        alerts.extend(anomaly_alerts)
        
        # Check pattern-based alerts
        pattern_alerts = await self._check_pattern_alerts(event)
        alerts.extend(pattern_alerts)
        
        # Check velocity-based alerts
        velocity_alerts = await self._check_velocity_alerts(event)
        alerts.extend(velocity_alerts)
        
        # Store and broadcast alerts
        for alert in alerts:
            await self._store_alert(alert)
            await self._broadcast_alert(alert)
        
        return alerts
    
    async def _check_threshold_alerts(self, event: RealtimeAnalyticsEvent) -> List[RealtimeAlert]:
        """
Check for threshold-based alerts"""
        alerts = []
        creator_rules = self.alert_rules.get(event.creator_id, {})
        metric_rules = creator_rules.get(event.metric_type.value, {})
        
        for rule_name, rule_config in metric_rules.items():
            if self._evaluate_threshold_rule(event, rule_config):
                alert = RealtimeAlert(
                    alert_id=f"threshold_{rule_name}_{event.creator_id}_{datetime.utcnow().timestamp()}",
                    creator_id=event.creator_id,
                    alert_type="threshold",
                    severity=AlertSeverity(rule_config.get('severity', 'medium')),
                    title=rule_config.get('title', f"{event.metric_type.value.title()} Threshold Alert"),
                    message=rule_config.get('message', f"{event.metric_type.value} has exceeded threshold"),
                    metric_data={
                        'metric_type': event.metric_type.value,
                        'current_value': event.metric_value,
                        'threshold': rule_config.get('threshold'),
                        'platform': event.platform
                    },
                    trigger_conditions=rule_config,
                    recommended_actions=rule_config.get('actions', []),
                    created_at=datetime.utcnow()
                )
                alerts.append(alert)
        
        return alerts
    
    def _evaluate_threshold_rule(self, event: RealtimeAnalyticsEvent, rule: Dict[str, Any]) -> bool:
        """Evaluate if a threshold rule is triggered"""
        threshold = rule.get('threshold')
        operator = rule.get('operator', 'greater_than')
        
        if operator == 'greater_than':
            return event.metric_value > threshold
        elif operator == 'less_than':
            return event.metric_value < threshold
        elif operator == 'equals':
            return event.metric_value == threshold
        elif operator == 'not_equals':
            return event.metric_value != threshold
        
        return False
    
    async def _check_velocity_alerts(self, event: RealtimeAnalyticsEvent) -> List[RealtimeAlert]:
        """
Check for velocity-based alerts (rapid changes)"""
        alerts = []
        
        # Get recent values for velocity calculation
        recent_values = await self._get_recent_metric_values(
            event.creator_id, event.metric_type, minutes=5
        )
        
        if len(recent_values) < 2:
            return alerts
        
        # Calculate velocity (rate of change)
        velocity = self._calculate_velocity(recent_values)
        
        # Check for rapid spikes or drops
        if velocity > 10.0:  # Rapid increase
            alert = RealtimeAlert(
                alert_id=f"velocity_spike_{event.creator_id}_{datetime.utcnow().timestamp()}",
                creator_id=event.creator_id,
                alert_type="velocity_spike",
                severity=AlertSeverity.HIGH,
                title=f"Rapid {event.metric_type.value.title()} Spike Detected",
                message=f"Your {event.metric_type.value} is increasing rapidly (+{velocity:.1f}/min). This could indicate viral content!",
                metric_data={
                    'metric_type': event.metric_type.value,
                    'velocity': velocity,
                    'current_value': event.metric_value,
                    'platform': event.platform
                },
                trigger_conditions={'velocity_threshold': 10.0},
                recommended_actions=[
                    "Monitor content performance closely",
                    "Prepare to capitalize on viral momentum",
                    "Engage with new audience members",
                    "Consider cross-promoting this content"
                ],
                created_at=datetime.utcnow()
            )
            alerts.append(alert)
            
        elif velocity < -5.0:  # Rapid decrease
            alert = RealtimeAlert(
                alert_id=f"velocity_drop_{event.creator_id}_{datetime.utcnow().timestamp()}",
                creator_id=event.creator_id,
                alert_type="velocity_drop",
                severity=AlertSeverity.MEDIUM,
                title=f"Rapid {event.metric_type.value.title()} Drop Detected",
                message=f"Your {event.metric_type.value} is decreasing rapidly ({velocity:.1f}/min). Investigate potential issues.",
                metric_data={
                    'metric_type': event.metric_type.value,
                    'velocity': velocity,
                    'current_value': event.metric_value,
                    'platform': event.platform
                },
                trigger_conditions={'velocity_threshold': -5.0},
                recommended_actions=[
                    "Check for technical issues",
                    "Review recent content changes",
                    "Analyze audience feedback",
                    "Consider content adjustments"
                ],
                created_at=datetime.utcnow()
            )
            alerts.append(alert)
        
        return alerts
    
    def _calculate_velocity(self, values: List[Tuple[datetime, float]]) -> float:
        """Calculate velocity (rate of change) from time series data"""
        if len(values) < 2:
            return 0.0
        
        # Sort by timestamp
        values.sort(key=lambda x: x[0])
        
        # Calculate rate of change per minute
        time_diff = (values[-1][0] - values[0][0]).total_seconds() / 60  # minutes
        value_diff = values[-1][1] - values[0][1]
        
        if time_diff == 0:
            return 0.0
        
        return value_diff / time_diff


class RealtimeDashboardEngine:
    """
Manages real-time dashboard updates"""
    
    def __init__(self):
        self.redis_client = None
        self.dashboard_cache = {}
        
    async def initialize(self):
        """
Initialize dashboard engine"""
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
        
    async def update_dashboard(self, event: RealtimeAnalyticsEvent) -> Dict[str, Any]:
        """
Update real-time dashboard with new metrics"""
        # Update current metrics snapshot
        snapshot = await self._update_metrics_snapshot(event)
        
        # Update trend indicators
        trends = await self._update_trend_indicators(event)
        
        # Update performance charts
        charts_update = await self._update_performance_charts(event)
        
        # Update comparative analytics
        comparative_data = await self._update_comparative_analytics(event)
        
        # Cache dashboard state
        dashboard_state = {
            'last_update': datetime.utcnow().isoformat(),
            'metrics_snapshot': snapshot,
            'trends': trends,
            'charts': charts_update,
            'comparative': comparative_data
        }
        
        await self.redis_client.setex(
            f"dashboard:{event.creator_id}",
            3600,  # 1 hour cache
            json.dumps(dashboard_state)
        )
        
        return dashboard_state
    
    async def _update_metrics_snapshot(self, event: RealtimeAnalyticsEvent) -> MetricsSnapshot:
        """Update current metrics snapshot"""
        # Get all current metrics for creator
        current_metrics = await self._get_current_metrics(event.creator_id)
        
        # Calculate trends
        trends = await self._calculate_metric_trends(event.creator_id, current_metrics)
        
        # Calculate percentage changes
        percentage_changes = await self._calculate_percentage_changes(event.creator_id, current_metrics)
        
        # Get anomaly scores
        anomaly_scores = await self._get_current_anomaly_scores(event.creator_id)
        
        # Get predictions
        predictions = await self._get_current_predictions(event.creator_id)
        
        return MetricsSnapshot(
            creator_id=event.creator_id,
            timestamp=datetime.utcnow(),
            metrics=current_metrics,
            trends=trends,
            percentage_changes=percentage_changes,
            anomaly_scores=anomaly_scores,
            predictions=predictions
        )


class RealtimeAnomalyDetector:
    """
Detects anomalies in real-time metrics"""
    
    def __init__(self):
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = MinMaxScaler()
        self.detector = AnomalyDetector()
        self.redis_client = None
        
    async def initialize(self):
        """
Initialize anomaly detector"""
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
        
    async def detect_anomalies(self, event: RealtimeAnalyticsEvent) -> Dict[str, Any]:
        """
Detect anomalies in real-time metrics"""
        # Get historical data for comparison
        historical_data = await self._get_historical_data(event)
        
        # Statistical anomaly detection
        statistical_anomalies = await self._detect_statistical_anomalies(event, historical_data)
        
        # Pattern-based anomaly detection
        pattern_anomalies = await self._detect_pattern_anomalies(event, historical_data)
        
        # Seasonal anomaly detection
        seasonal_anomalies = await self._detect_seasonal_anomalies(event, historical_data)
        
        # ML-based anomaly detection
        ml_anomalies = await self._detect_ml_anomalies(event, historical_data)
        
        # Combine results
        combined_score = self._combine_anomaly_scores([
            statistical_anomalies.get('score', 0),
            pattern_anomalies.get('score', 0),
            seasonal_anomalies.get('score', 0),
            ml_anomalies.get('score', 0)
        ])
        
        return {
            'overall_anomaly_score': combined_score,
            'is_anomaly': combined_score > 0.7,
            'anomaly_type': self._determine_anomaly_type(combined_score),
            'statistical_anomalies': statistical_anomalies,
            'pattern_anomalies': pattern_anomalies,
            'seasonal_anomalies': seasonal_anomalies,
            'ml_anomalies': ml_anomalies,
            'confidence': max(0.5, min(0.95, combined_score))
        }
    
    async def _detect_statistical_anomalies(self, event: RealtimeAnalyticsEvent, 
                                          historical_data: List[float]) -> Dict[str, Any]:
        """
Detect statistical anomalies using z-score and IQR"""
        if len(historical_data) < 10:
            return {'score': 0, 'method': 'insufficient_data'}
        
        # Z-score based detection
        mean_val = np.mean(historical_data)
        std_val = np.std(historical_data)
        z_score = abs((event.metric_value - mean_val) / (std_val + 1e-8))
        
        # IQR based detection
        q25, q75 = np.percentile(historical_data, [25, 75])
        iqr = q75 - q25
        lower_bound = q25 - 1.5 * iqr
        upper_bound = q75 + 1.5 * iqr
        
        is_outlier_iqr = event.metric_value < lower_bound or event.metric_value > upper_bound
        
        # Combine scores
        z_score_normalized = min(1.0, z_score / 3.0)  # Normalize to 0-1
        iqr_score = 1.0 if is_outlier_iqr else 0.0
        
        combined_score = (z_score_normalized + iqr_score) / 2
        
        return {
            'score': combined_score,
            'z_score': z_score,
            'is_outlier_iqr': is_outlier_iqr,
            'method': 'statistical',
            'bounds': {'lower': lower_bound, 'upper': upper_bound},
            'statistics': {'mean': mean_val, 'std': std_val, 'iqr': iqr}
        }
    
    def _combine_anomaly_scores(self, scores: List[float]) -> float:
        """
Combine multiple anomaly scores into final score"""
        # Remove zero scores (insufficient data)
        valid_scores = [s for s in scores if s > 0]
        
        if not valid_scores:
            return 0.0
        
        # Use weighted average with emphasis on highest scores
        weights = [1.0, 1.2, 1.5, 2.0][:len(valid_scores)]
        sorted_scores = sorted(valid_scores, reverse=True)
        
        weighted_sum = sum(score * weight for score, weight in zip(sorted_scores, weights))
        weight_sum = sum(weights[:len(valid_scores)])
        
        return min(1.0, weighted_sum / weight_sum)
    
    def _determine_anomaly_type(self, score: float) -> Optional[AnomalyType]:
        """
Determine the type of anomaly based on score and patterns"""
        if score > 0.9:
            return AnomalyType.SPIKE
        elif score > 0.7:
            return AnomalyType.OUTLIER
        elif score > 0.5:
            return AnomalyType.TREND_CHANGE
        else:
            return None
