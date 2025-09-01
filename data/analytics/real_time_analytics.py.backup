"""Real-Time Analytics Engine
=========================

Real-time analytics processing and streaming for live content performance monitoring.
Provides instant insights, alerts, and recommendations for content optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

WARNING: This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized copying, distribution, or modification without explicit written
permission is strictly prohibited and will result in legal action.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import json
import time

import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from redis import Redis
import websockets
from fastapi import WebSocket
from collections import deque, defaultdict
import aioredis
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer


class MetricType(Enum):
    """Real-time metric types"""
    VIEWS = "views"
    LIKES = "likes"
    COMMENTS = "comments"
    SHARES = "shares"
    REVENUE = "revenue"
    ENGAGEMENT_RATE = "engagement_rate"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    CLICK_THROUGH_RATE = "click_through_rate"
    CONVERSION_RATE = "conversion_rate"


class AlertType(Enum):
    """Alert types for real-time monitoring"""
    VIRAL_CONTENT = "viral_content"
    ENGAGEMENT_SPIKE = "engagement_spike"
    REVENUE_MILESTONE = "revenue_milestone"
    NEGATIVE_SENTIMENT = "negative_sentiment"
    CONTENT_PROTECTION_ALERT = "content_protection_alert"
    PERFORMANCE_DROP = "performance_drop"
    AUDIENCE_ANOMALY = "audience_anomaly"
    PLATFORM_ISSUE = "platform_issue"


class StreamingPlatform(Enum):
    """Streaming platforms for real-time data"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SPOTIFY = "spotify"
    TWITTER = "twitter"
    TWITCH = "twitch"
    FACEBOOK = "facebook"


@dataclass
class RealTimeMetric:
    """Real-time metric data point"""
    metric_id: str
    user_id: str
    content_id: str
    platform: StreamingPlatform
    metric_type: MetricType
    value: float
    previous_value: float
    percentage_change: float
    timestamp: datetime
    confidence_score: float


@dataclass
class RealTimeAlert:
    """Real-time alert notification"""
    alert_id: str
    user_id: str
    alert_type: AlertType
    severity: str  # "low", "medium", "high", "critical"
    title: str
    description: str
    affected_content: List[str]
    recommended_actions: List[str]
    auto_resolve: bool
    created_at: datetime


@dataclass
class LiveDashboardData:
    """Live dashboard data structure"""
    user_id: str
    current_metrics: Dict[str, RealTimeMetric]
    trends: Dict[str, List[float]]
    alerts: List[RealTimeAlert]
    performance_summary: Dict[str, Any]
    live_content: List[Dict]
    audience_activity: Dict[str, Any]
    last_updated: datetime


@dataclass
class StreamingEvent:
    """Real-time streaming event"""
    event_id: str
    user_id: str
    event_type: str
    platform: StreamingPlatform
    content_id: str
    data: Dict[str, Any]
    timestamp: datetime


class RealTimeAnalytics:
    """
    Professional real-time analytics engine for live content monitoring.
    
    Provides instant analytics, streaming dashboards, real-time alerts,
    and live performance optimization for content creators and influencers.
    """
    
    def __init__(self, db_session: AsyncSession, redis_client: Redis,
                 kafka_producer: Optional[AIOKafkaProducer] = None):
        """
        Initialize RealTimeAnalytics engine.
        
        Args:
            db_session: Async database session
            redis_client: Redis client for caching and pub/sub
            kafka_producer: Kafka producer for event streaming (optional)
        """
        self.db_session = db_session
        self.redis_client = redis_client
        self.kafka_producer = kafka_producer
        self.logger = logging.getLogger(__name__)
        
        # Real-time data stores
        self.metric_buffer = defaultdict(lambda: deque(maxlen=1000))  # Buffer for metrics
        self.active_connections = {}  # WebSocket connections
        self.alert_rules = {}  # Alert configuration
        self.streaming_topics = {}  # Kafka streaming topics
        
        # Performance tracking
        self.processing_times = deque(maxlen=100)
        self.event_counts = defaultdict(int)
        
    async def start_real_time_monitoring(self, user_id: str) -> None:
        """
        Start real-time monitoring for a user.
        
        Args:
            user_id: User identifier to monitor
        """
        try:
            self.logger.info(f"Starting real-time monitoring for user {user_id}")
            
            # Initialize monitoring components
            await self._setup_metric_collectors(user_id)
            await self._setup_alert_rules(user_id)
            await self._start_streaming_processors(user_id)
            
            # Start background tasks
            asyncio.create_task(self._process_real_time_metrics(user_id))
            asyncio.create_task(self._monitor_performance_anomalies(user_id))
            asyncio.create_task(self._update_live_dashboard(user_id))
            
            self.logger.info(f"Real-time monitoring started for user {user_id}")
            
        except Exception as e:
            self.logger.error(f"Error starting real-time monitoring: {str(e)}")
    
    async def process_streaming_event(self, event: StreamingEvent) -> None:
        """
        Process incoming streaming event in real-time.
        
        Args:
            event: Streaming event to process
        """
        try:
            start_time = time.time()
            
            # Store event in buffer
            self.metric_buffer[event.user_id].append(event)
            self.event_counts[event.event_type] += 1
            
            # Process event based on type
            if event.event_type == "content_view":
                await self._process_view_event(event)
            elif event.event_type == "content_engagement":
                await self._process_engagement_event(event)
            elif event.event_type == "revenue_event":
                await self._process_revenue_event(event)
            elif event.event_type == "protection_alert":
                await self._process_protection_alert(event)
            
            # Check for alert conditions
            await self._check_alert_conditions(event)
            
            # Update real-time metrics
            await self._update_real_time_metrics(event)
            
            # Publish to subscribers
            await self._publish_event_update(event)
            
            # Track processing time
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            self.processing_times.append(processing_time)
            
        except Exception as e:
            self.logger.error(f"Error processing streaming event: {str(e)}")
    
    async def get_live_dashboard_data(self, user_id: str) -> LiveDashboardData:
        """
        Get current live dashboard data for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Live dashboard data
        """
        try:
            cache_key = f"live_dashboard:{user_id}"
            
            # Try to get from cache first
            cached_data = await self._get_cached_result(cache_key)
            if cached_data:
                return LiveDashboardData(**cached_data)
            
            # Calculate current metrics
            current_metrics = await self._calculate_current_metrics(user_id)
            
            # Get trends data
            trends = await self._calculate_metric_trends(user_id)
            
            # Get active alerts
            alerts = await self._get_active_alerts(user_id)
            
            # Get performance summary
            performance_summary = await self._calculate_performance_summary(user_id)
            
            # Get live content information
            live_content = await self._get_live_content_info(user_id)
            
            # Get audience activity
            audience_activity = await self._get_audience_activity(user_id)
            
            dashboard_data = LiveDashboardData(
                user_id=user_id,
                current_metrics=current_metrics,
                trends=trends,
                alerts=alerts,
                performance_summary=performance_summary,
                live_content=live_content,
                audience_activity=audience_activity,
                last_updated=datetime.utcnow()
            )
            
            # Cache for short time (30 seconds)
            await self._cache_result(cache_key, asdict(dashboard_data), ttl=30)
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Error getting live dashboard data: {str(e)}")
            return LiveDashboardData(
                user_id=user_id,
                current_metrics={},
                trends={},
                alerts=[],
                performance_summary={},
                live_content=[],
                audience_activity={},
                last_updated=datetime.utcnow()
            )
    
    async def setup_websocket_connection(self, websocket: WebSocket, user_id: str) -> None:
        """
        Setup WebSocket connection for real-time updates.
        
        Args:
            websocket: WebSocket connection
            user_id: User identifier
        """
        try:
            await websocket.accept()
            
            # Store connection
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            self.active_connections[user_id].append(websocket)
            
            self.logger.info(f"WebSocket connection established for user {user_id}")
            
            # Send initial dashboard data
            dashboard_data = await self.get_live_dashboard_data(user_id)
            await websocket.send_json({
                "type": "dashboard_update",
                "data": asdict(dashboard_data)
            })
            
            # Keep connection alive and handle incoming messages
            try:
                while True:
                    # Wait for messages or send periodic updates
                    try:
                        message = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)
                        await self._handle_websocket_message(websocket, user_id, message)
                    except asyncio.TimeoutError:
                        # Send periodic update
                        await self._send_periodic_update(websocket, user_id)
                        
            except Exception as e:
                self.logger.error(f"WebSocket error for user {user_id}: {str(e)}")
            finally:
                # Remove connection
                if user_id in self.active_connections:
                    if websocket in self.active_connections[user_id]:
                        self.active_connections[user_id].remove(websocket)
                        
        except Exception as e:
            self.logger.error(f"Error setting up WebSocket connection: {str(e)}")
    
    async def create_custom_alert(self, user_id: str, alert_config: Dict[str, Any]) -> str:
        """
        Create custom alert rule for user.
        
        Args:
            user_id: User identifier
            alert_config: Alert configuration
            
        Returns:
            Alert rule ID
        """
        try:
            alert_id = f"custom_{user_id}_{int(time.time())}"
            
            # Validate alert configuration
            required_fields = ['metric_type', 'condition', 'threshold', 'title']
            if not all(field in alert_config for field in required_fields):
                raise ValueError("Missing required alert configuration fields")
            
            # Store alert rule
            alert_rule = {
                'alert_id': alert_id,
                'user_id': user_id,
                'metric_type': alert_config['metric_type'],
                'condition': alert_config['condition'],  # 'greater_than', 'less_than', 'percentage_change'
                'threshold': alert_config['threshold'],
                'title': alert_config['title'],
                'description': alert_config.get('description', ''),
                'severity': alert_config.get('severity', 'medium'),
                'enabled': True,
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Store in Redis
            await self.redis_client.hset(
                f"alert_rules:{user_id}",
                alert_id,
                json.dumps(alert_rule)
            )
            
            # Update local cache
            if user_id not in self.alert_rules:
                self.alert_rules[user_id] = {}
            self.alert_rules[user_id][alert_id] = alert_rule
            
            self.logger.info(f"Created custom alert {alert_id} for user {user_id}")
            
            return alert_id
            
        except Exception as e:
            self.logger.error(f"Error creating custom alert: {str(e)}")
            return ""
    
    async def get_performance_analytics(self, user_id: str,
                                      time_window: timedelta = timedelta(hours=1)
                                      ) -> Dict[str, Any]:
        """
        Get real-time performance analytics for specified time window.
        
        Args:
            user_id: User identifier
            time_window: Time window for analysis
            
        Returns:
            Performance analytics data
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - time_window
            
            # Get metrics from buffer and database
            buffer_metrics = self._get_buffer_metrics(user_id, start_time, end_time)
            db_metrics = await self._get_db_metrics(user_id, start_time, end_time)
            
            # Combine and process metrics
            all_metrics = buffer_metrics + db_metrics
            
            if not all_metrics:
                return {"error": "No metrics available for specified time window"}
            
            # Calculate performance indicators
            performance_data = {
                "time_window": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "duration_minutes": time_window.total_seconds() / 60
                },
                "metrics_summary": self._calculate_metrics_summary(all_metrics),
                "platform_breakdown": self._calculate_platform_breakdown(all_metrics),
                "trend_analysis": self._calculate_trend_analysis(all_metrics),
                "anomaly_detection": await self._detect_anomalies(all_metrics),
                "performance_score": self._calculate_performance_score(all_metrics),
                "optimization_suggestions": await self._generate_optimization_suggestions(user_id, all_metrics)
            }
            
            return performance_data
            
        except Exception as e:
            self.logger.error(f"Error getting performance analytics: {str(e)}")
            return {"error": str(e)}
    
    async def _setup_metric_collectors(self, user_id: str) -> None:
        """Setup metric collectors for different platforms."""
        try:
            # Initialize collectors for each platform
            platforms = [StreamingPlatform.YOUTUBE, StreamingPlatform.INSTAGRAM, 
                        StreamingPlatform.TIKTOK, StreamingPlatform.SPOTIFY]
            
            for platform in platforms:
                collector_key = f"collector:{user_id}:{platform.value}"
                await self.redis_client.set(collector_key, "active", ex=3600)
                
        except Exception as e:
            self.logger.error(f"Error setting up metric collectors: {str(e)}")
    
    async def _setup_alert_rules(self, user_id: str) -> None:
        """Setup default alert rules for user."""
        try:
            default_alerts = [
                {
                    'metric_type': 'engagement_rate',
                    'condition': 'percentage_change',
                    'threshold': 50,  # 50% increase
                    'title': 'Engagement Spike Detected',
                    'severity': 'medium'
                },
                {
                    'metric_type': 'views',
                    'condition': 'greater_than',
                    'threshold': 10000,
                    'title': 'High View Count',
                    'severity': 'low'
                },
                {
                    'metric_type': 'revenue',
                    'condition': 'greater_than',
                    'threshold': 100,
                    'title': 'Revenue Milestone',
                    'severity': 'high'
                }
            ]
            
            for alert_config in default_alerts:
                await self.create_custom_alert(user_id, alert_config)
                
        except Exception as e:
            self.logger.error(f"Error setting up alert rules: {str(e)}")
    
    async def _start_streaming_processors(self, user_id: str) -> None:
        """Start streaming data processors."""
        try:
            if self.kafka_producer:
                # Start Kafka streaming
                topic = f"user_analytics_{user_id}"
                self.streaming_topics[user_id] = topic
                
                # Create topic if not exists
                await self._ensure_kafka_topic_exists(topic)
                
        except Exception as e:
            self.logger.error(f"Error starting streaming processors: {str(e)}")
    
    async def _process_real_time_metrics(self, user_id: str) -> None:
        """Background task to process real-time metrics."""
        try:
            while True:
                # Process buffered events
                if user_id in self.metric_buffer and self.metric_buffer[user_id]:
                    events_to_process = []
                    
                    # Get batch of events
                    for _ in range(min(10, len(self.metric_buffer[user_id]))):
                        if self.metric_buffer[user_id]:
                            events_to_process.append(self.metric_buffer[user_id].popleft())
                    
                    # Process batch
                    for event in events_to_process:
                        await self._process_metric_event(event)
                
                # Wait before next processing cycle
                await asyncio.sleep(5)  # Process every 5 seconds
                
        except Exception as e:
            self.logger.error(f"Error in real-time metrics processing: {str(e)}")
    
    async def _monitor_performance_anomalies(self, user_id: str) -> None:
        """Monitor for performance anomalies."""
        try:
            while True:
                # Get recent metrics
                recent_metrics = await self._get_recent_metrics(user_id, timedelta(minutes=15))
                
                # Detect anomalies
                anomalies = await self._detect_performance_anomalies(recent_metrics)
                
                # Create alerts for significant anomalies
                for anomaly in anomalies:
                    if anomaly['severity'] in ['high', 'critical']:
                        await self._create_anomaly_alert(user_id, anomaly)
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
        except Exception as e:
            self.logger.error(f"Error monitoring performance anomalies: {str(e)}")
    
    async def _update_live_dashboard(self, user_id: str) -> None:
        """Update live dashboard data."""
        try:
            while True:
                # Update dashboard data
                dashboard_data = await self.get_live_dashboard_data(user_id)
                
                # Send updates to connected WebSocket clients
                await self._broadcast_dashboard_update(user_id, dashboard_data)
                
                # Wait before next update
                await asyncio.sleep(10)  # Update every 10 seconds
                
        except Exception as e:
            self.logger.error(f"Error updating live dashboard: {str(e)}")
    
    async def _process_view_event(self, event: StreamingEvent) -> None:
        """Process content view event."""
        try:
            # Update view metrics in real-time
            metric_key = f"views:{event.user_id}:{event.content_id}"
            current_views = await self.redis_client.incr(metric_key)
            
            # Set expiration for cleanup
            await self.redis_client.expire(metric_key, 3600)  # 1 hour
            
            # Create real-time metric
            metric = RealTimeMetric(
                metric_id=f"view_{event.event_id}",
                user_id=event.user_id,
                content_id=event.content_id,
                platform=event.platform,
                metric_type=MetricType.VIEWS,
                value=current_views,
                previous_value=current_views - 1,
                percentage_change=100.0 if current_views == 1 else (1 / (current_views - 1)) * 100,
                timestamp=event.timestamp,
                confidence_score=1.0
            )
            
            # Store metric
            await self._store_real_time_metric(metric)
            
        except Exception as e:
            self.logger.error(f"Error processing view event: {str(e)}")
    
    async def _process_engagement_event(self, event: StreamingEvent) -> None:
        """Process engagement event."""
        try:
            engagement_type = event.data.get('engagement_type', 'like')
            
            # Update engagement metrics
            metric_key = f"engagement:{event.user_id}:{event.content_id}:{engagement_type}"
            current_count = await self.redis_client.incr(metric_key)
            
            # Set expiration
            await self.redis_client.expire(metric_key, 3600)
            
            # Create metric based on engagement type
            metric_type_map = {
                'like': MetricType.LIKES,
                'comment': MetricType.COMMENTS,
                'share': MetricType.SHARES
            }
            
            metric = RealTimeMetric(
                metric_id=f"engagement_{event.event_id}",
                user_id=event.user_id,
                content_id=event.content_id,
                platform=event.platform,
                metric_type=metric_type_map.get(engagement_type, MetricType.LIKES),
                value=current_count,
                previous_value=current_count - 1,
                percentage_change=100.0 if current_count == 1 else (1 / (current_count - 1)) * 100,
                timestamp=event.timestamp,
                confidence_score=1.0
            )
            
            await self._store_real_time_metric(metric)
            
        except Exception as e:
            self.logger.error(f"Error processing engagement event: {str(e)}")
    
    async def _process_revenue_event(self, event: StreamingEvent) -> None:
        """Process revenue event."""
        try:
            revenue_amount = event.data.get('amount', 0)
            
            # Update revenue metrics
            metric_key = f"revenue:{event.user_id}:{event.platform.value}"
            current_revenue = await self.redis_client.incrbyfloat(metric_key, revenue_amount)
            
            # Set expiration
            await self.redis_client.expire(metric_key, 3600)
            
            metric = RealTimeMetric(
                metric_id=f"revenue_{event.event_id}",
                user_id=event.user_id,
                content_id=event.content_id,
                platform=event.platform,
                metric_type=MetricType.REVENUE,
                value=current_revenue,
                previous_value=current_revenue - revenue_amount,
                percentage_change=((revenue_amount / (current_revenue - revenue_amount)) * 100) if current_revenue > revenue_amount else 100,
                timestamp=event.timestamp,
                confidence_score=1.0
            )
            
            await self._store_real_time_metric(metric)
            
        except Exception as e:
            self.logger.error(f"Error processing revenue event: {str(e)}")
    
    async def _process_protection_alert(self, event: StreamingEvent) -> None:
        """Process content protection alert."""
        try:
            alert = RealTimeAlert(
                alert_id=f"protection_{event.event_id}",
                user_id=event.user_id,
                alert_type=AlertType.CONTENT_PROTECTION_ALERT,
                severity="high",
                title="Content Protection Alert",
                description=event.data.get('description', 'Potential content infringement detected'),
                affected_content=[event.content_id],
                recommended_actions=[
                    "Review detected content",
                    "Take appropriate action if confirmed",
                    "Update protection settings if needed"
                ],
                auto_resolve=False,
                created_at=event.timestamp
            )
            
            await self._store_alert(alert)
            await self._send_alert_notification(alert)
            
        except Exception as e:
            self.logger.error(f"Error processing protection alert: {str(e)}")
    
    async def _calculate_current_metrics(self, user_id: str) -> Dict[str, RealTimeMetric]:
        """Calculate current real-time metrics."""
        try:
            metrics = {}
            
            # Get all metric keys for user
            pattern = f"*:{user_id}:*"
            keys = await self.redis_client.keys(pattern)
            
            for key in keys:
                try:
                    key_parts = key.decode('utf-8').split(':')
                    metric_type = key_parts[0]
                    value = await self.redis_client.get(key)
                    
                    if value:
                        metric = RealTimeMetric(
                            metric_id=f"current_{metric_type}_{user_id}",
                            user_id=user_id,
                            content_id="all",
                            platform=StreamingPlatform.YOUTUBE,  # Default
                            metric_type=MetricType(metric_type) if metric_type in [m.value for m in MetricType] else MetricType.VIEWS,
                            value=float(value),
                            previous_value=0,
                            percentage_change=0,
                            timestamp=datetime.utcnow(),
                            confidence_score=1.0
                        )
                        
                        metrics[metric_type] = metric
                        
                except Exception as e:
                    self.logger.debug(f"Error processing metric key {key}: {str(e)}")
                    continue
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating current metrics: {str(e)}")
            return {}
    
    def _get_buffer_metrics(self, user_id: str, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get metrics from memory buffer."""
        try:
            if user_id not in self.metric_buffer:
                return []
            
            buffer_metrics = []
            for event in self.metric_buffer[user_id]:
                if start_time <= event.timestamp <= end_time:
                    buffer_metrics.append({
                        'timestamp': event.timestamp,
                        'event_type': event.event_type,
                        'platform': event.platform.value,
                        'data': event.data
                    })
            
            return buffer_metrics
            
        except Exception as e:
            self.logger.error(f"Error getting buffer metrics: {str(e)}")
            return []
    
    async def _get_db_metrics(self, user_id: str, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get metrics from database."""
        try:
            query = text("""
                SELECT 
                    metric_type,
                    platform,
                    value,
                    created_at
                FROM real_time_metrics 
                WHERE user_id = :user_id 
                AND created_at BETWEEN :start_time AND :end_time
                ORDER BY created_at DESC
            """)
            
            result = await self.db_session.execute(
                query,
                {
                    "user_id": user_id,
                    "start_time": start_time,
                    "end_time": end_time
                }
            )
            
            db_metrics = []
            for row in result.fetchall():
                db_metrics.append({
                    'timestamp': row.created_at,
                    'metric_type': row.metric_type,
                    'platform': row.platform,
                    'value': row.value
                })
            
            return db_metrics
            
        except Exception as e:
            self.logger.error(f"Error getting database metrics: {str(e)}")
            return []
    
    async def _get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Get cached result from Redis."""
        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            self.logger.error(f"Error getting cached result: {str(e)}")
            return None
    
    async def _cache_result(self, cache_key: str, data: Dict, ttl: int) -> None:
        """Cache result in Redis."""
        try:
            await self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(data, default=str)
            )
        except Exception as e:
            self.logger.error(f"Error caching result: {str(e)}")
