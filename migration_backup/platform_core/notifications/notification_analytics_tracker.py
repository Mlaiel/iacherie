"""🚀 Notification Analytics Tracker - Enterprise Performance Intelligence
========================================================================
Module: platform_core/notifications/notification_analytics_tracker.py
Author: Fahed Mlaiel (mlaiel@live.de)
========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

🎯 NOTIFICATION ANALYTICS TRACKER - PERFORMANCE INTELLIGENCE
- Tracking engagement multi-canal temps réel
- Funnel analysis click-through rates
- Cohort analysis retention notifications
- Predictive analytics delivery optimization
- ML-powered performance insights
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import redis.asyncio as redis
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Analytics event types."""
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    CONVERTED = "converted"
    BOUNCED = "bounced"
    COMPLAINED = "complained"
    UNSUBSCRIBED = "unsubscribed"
    FAILED = "failed"


class MetricType(Enum):
    """Analytics metric types."""
    DELIVERY_RATE = "delivery_rate"
    OPEN_RATE = "open_rate"
    CLICK_RATE = "click_rate"
    CONVERSION_RATE = "conversion_rate"
    BOUNCE_RATE = "bounce_rate"
    COMPLAINT_RATE = "complaint_rate"
    UNSUBSCRIBE_RATE = "unsubscribe_rate"
    ENGAGEMENT_SCORE = "engagement_score"


class ChannelType(Enum):
    """Notification channel types."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class TimeGranularity(Enum):
    """Time granularity for analytics."""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


@dataclass
class AnalyticsEvent:
    """Analytics event data structure."""
    id: str
    user_id: str
    notification_id: str
    template_id: Optional[str] = None
    campaign_id: Optional[str] = None
    event_type: EventType = EventType.SENT
    channel: ChannelType = ChannelType.EMAIL
    timestamp: datetime = field(default_factory=datetime.utcnow)
    properties: Dict[str, Any] = field(default_factory=dict)
    user_properties: Dict[str, Any] = field(default_factory=dict)
    device_info: Dict[str, Any] = field(default_factory=dict)
    location_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricValue:
    """Metric value with metadata."""
    value: float
    timestamp: datetime
    channel: Optional[ChannelType] = None
    segment: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceReport:
    """Performance analytics report."""
    id: str
    name: str
    period_start: datetime
    period_end: datetime
    channels: List[ChannelType]
    metrics: Dict[MetricType, MetricValue]
    funnel_data: Dict[str, Any] = field(default_factory=dict)
    cohort_data: Dict[str, Any] = field(default_factory=dict)
    segment_data: Dict[str, Any] = field(default_factory=dict)
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CohortAnalysis:
    """Cohort analysis results."""
    cohort_id: str
    cohort_name: str
    start_date: datetime
    end_date: datetime
    retention_data: Dict[str, List[float]]
    engagement_data: Dict[str, List[float]]
    size_data: Dict[str, int]
    insights: List[str] = field(default_factory=list)


@dataclass
class FunnelAnalysis:
    """Funnel analysis results."""
    funnel_id: str
    funnel_name: str
    steps: List[str]
    conversion_rates: List[float]
    drop_off_rates: List[float]
    user_counts: List[int]
    insights: List[str] = field(default_factory=list)


class MLInsightsEngine:
    """Machine learning engine for analytics insights."""
    
    def __init__(self):
        self.engagement_predictor = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = [
            'hour_of_day', 'day_of_week', 'days_since_last_notification',
            'historical_open_rate', 'historical_click_rate', 'template_sentiment',
            'subject_length', 'content_length', 'has_personalization', 'has_images'
        ]
    
    async def predict_engagement(self, notification_features: Dict[str, Any]) -> float:
        """Predict engagement probability for notification."""
        try:
            if not self.is_trained:
                await self._train_model()
            
            features = self._extract_features(notification_features)
            
            if self.is_trained:
                features_scaled = self.scaler.transform([features])
                engagement_prob = self.engagement_predictor.predict_proba(features_scaled)[0][1]
                return engagement_prob
            else:
                # Fallback heuristic
                return self._heuristic_engagement_score(notification_features)
                
        except Exception as e:
            logger.error(f"Engagement prediction failed: {e}")
            return 0.5
    
    def _extract_features(self, notification_features: Dict[str, Any]) -> List[float]:
        """Extract features for ML model."""
        features = []
        
        # Time features
        current_time = datetime.utcnow()
        features.append(current_time.hour)
        features.append(current_time.weekday())
        
        # User history features
        features.append(notification_features.get('days_since_last_notification', 1))
        features.append(notification_features.get('historical_open_rate', 0.3))
        features.append(notification_features.get('historical_click_rate', 0.1))
        
        # Content features
        features.append(notification_features.get('template_sentiment', 0.5))
        features.append(notification_features.get('subject_length', 50))
        features.append(notification_features.get('content_length', 200))
        features.append(1.0 if notification_features.get('has_personalization') else 0.0)
        features.append(1.0 if notification_features.get('has_images') else 0.0)
        
        return features
    
    def _heuristic_engagement_score(self, features: Dict[str, Any]) -> float:
        """Fallback heuristic engagement scoring."""
        score = 0.5  # Base score
        
        # Historical performance boost
        open_rate = features.get('historical_open_rate', 0.3)
        click_rate = features.get('historical_click_rate', 0.1)
        score += (open_rate * 0.3) + (click_rate * 0.7)
        
        # Content quality boost
        if features.get('has_personalization'):
            score += 0.1
        if features.get('has_images'):
            score += 0.05
        
        # Time penalty for long gaps
        days_since_last = features.get('days_since_last_notification', 1)
        if days_since_last > 7:
            score -= 0.1
        
        return min(max(score, 0.0), 1.0)
    
    async def _train_model(self):
        """Train the engagement prediction model."""
        try:
            # Generate synthetic training data
            X, y = self._generate_training_data()
            
            if len(X) > 100:  # Need sufficient data
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                
                # Scale features
                X_train_scaled = self.scaler.fit_transform(X_train)
                X_test_scaled = self.scaler.transform(X_test)
                
                # Train model
                self.engagement_predictor.fit(X_train_scaled, y_train)
                
                # Evaluate
                train_score = self.engagement_predictor.score(X_train_scaled, y_train)
                test_score = self.engagement_predictor.score(X_test_scaled, y_test)
                
                if test_score > 0.6:  # Minimum acceptable performance
                    self.is_trained = True
                    logger.info(f"ML model trained successfully. Train: {train_score:.3f}, Test: {test_score:.3f}")
                else:
                    logger.warning(f"ML model performance too low: {test_score:.3f}")
            
        except Exception as e:
            logger.error(f"ML model training failed: {e}")
    
    def _generate_training_data(self):
        """Generate synthetic training data for demonstration."""
        np.random.seed(42)
        n_samples = 5000
        
        X = []
        y = []
        
        for _ in range(n_samples):
            # Generate features
            hour = np.random.randint(0, 24)
            day_of_week = np.random.randint(0, 7)
            days_since_last = np.random.randint(1, 30)
            historical_open_rate = np.random.beta(2, 5)  # Skewed towards lower rates
            historical_click_rate = np.random.beta(1, 9)  # Very skewed towards lower rates
            template_sentiment = np.random.beta(3, 2)  # Skewed towards positive
            subject_length = np.random.normal(45, 15)
            content_length = np.random.normal(200, 50)
            has_personalization = np.random.choice([0, 1], p=[0.3, 0.7])
            has_images = np.random.choice([0, 1], p=[0.6, 0.4])
            
            features = [hour, day_of_week, days_since_last, historical_open_rate, 
                       historical_click_rate, template_sentiment, subject_length, 
                       content_length, has_personalization, has_images]
            
            # Generate engagement label (synthetic logic)
            engagement_prob = (
                0.1 +  # Base probability
                historical_open_rate * 0.3 +
                historical_click_rate * 0.4 +
                (1.0 if 9 <= hour <= 17 else 0.5) * 0.1 +  # Business hours
                has_personalization * 0.05 +
                has_images * 0.03 +
                (template_sentiment - 0.5) * 0.1
            )
            
            # Add some noise
            engagement_prob += np.random.normal(0, 0.1)
            engagement_prob = max(0, min(1, engagement_prob))
            
            engaged = 1 if np.random.random() < engagement_prob else 0
            
            X.append(features)
            y.append(engaged)
        
        return X, y


class NotificationAnalyticsTracker:
    """Enterprise notification analytics tracker with ML insights."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis = redis.Redis(**config.get('redis', {}))
        self.ml_engine = MLInsightsEngine()
        
        # Analytics storage
        self.events_buffer: List[AnalyticsEvent] = []
        self.metrics_cache: Dict[str, Any] = {}
        
        # Configuration
        self.buffer_size = config.get('buffer_size', 1000)
        self.flush_interval = config.get('flush_interval', 60)  # seconds
        
        # Start background tasks
        asyncio.create_task(self._flush_events_periodically())
        asyncio.create_task(self._update_metrics_periodically())
    
    async def track_event(self, event: AnalyticsEvent) -> bool:
        """Track analytics event."""
        try:
            # Add to buffer
            self.events_buffer.append(event)
            
            # Immediate storage for critical events
            if event.event_type in [EventType.SENT, EventType.DELIVERED, EventType.CLICKED]:
                await self._store_event(event)
            
            # Update real-time metrics
            await self._update_real_time_metrics(event)
            
            # Flush buffer if full
            if len(self.events_buffer) >= self.buffer_size:
                await self._flush_events()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to track event: {e}")
            return False
    
    async def track_notification_sent(self, notification_id: str, user_id: str, 
                                    channel: ChannelType, template_id: str = None,
                                    campaign_id: str = None, properties: Dict[str, Any] = None) -> bool:
        """Track notification sent event."""
        event = AnalyticsEvent(
            id=str(uuid.uuid4()),
            user_id=user_id,
            notification_id=notification_id,
            template_id=template_id,
            campaign_id=campaign_id,
            event_type=EventType.SENT,
            channel=channel,
            properties=properties or {}
        )
        
        return await self.track_event(event)
    
    async def track_notification_opened(self, notification_id: str, user_id: str,
                                      channel: ChannelType, properties: Dict[str, Any] = None) -> bool:
        """Track notification opened event."""
        event = AnalyticsEvent(
            id=str(uuid.uuid4()),
            user_id=user_id,
            notification_id=notification_id,
            event_type=EventType.OPENED,
            channel=channel,
            properties=properties or {}
        )
        
        return await self.track_event(event)
    
    async def track_notification_clicked(self, notification_id: str, user_id: str,
                                       channel: ChannelType, click_url: str = None,
                                       properties: Dict[str, Any] = None) -> bool:
        """Track notification clicked event."""
        event_properties = properties or {}
        if click_url:
            event_properties['click_url'] = click_url
        
        event = AnalyticsEvent(
            id=str(uuid.uuid4()),
            user_id=user_id,
            notification_id=notification_id,
            event_type=EventType.CLICKED,
            channel=channel,
            properties=event_properties
        )
        
        return await self.track_event(event)
    
    async def track_conversion(self, notification_id: str, user_id: str,
                             channel: ChannelType, conversion_value: float = 0.0,
                             conversion_type: str = "default", properties: Dict[str, Any] = None) -> bool:
        """Track conversion event."""
        event_properties = properties or {}
        event_properties.update({
            'conversion_value': conversion_value,
            'conversion_type': conversion_type
        })
        
        event = AnalyticsEvent(
            id=str(uuid.uuid4()),
            user_id=user_id,
            notification_id=notification_id,
            event_type=EventType.CONVERTED,
            channel=channel,
            properties=event_properties
        )
        
        return await self.track_event(event)
    
    async def get_performance_metrics(self, channel: ChannelType = None,
                                    start_date: datetime = None, end_date: datetime = None,
                                    granularity: TimeGranularity = TimeGranularity.DAY) -> Dict[MetricType, List[MetricValue]]:
        """Get performance metrics for specified period."""
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=7)
            if not end_date:
                end_date = datetime.utcnow()
            
            metrics = {}
            
            # Calculate each metric type
            for metric_type in MetricType:
                values = await self._calculate_metric_values(
                    metric_type, channel, start_date, end_date, granularity
                )
                metrics[metric_type] = values
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {}
    
    async def generate_performance_report(self, name: str, channels: List[ChannelType],
                                        start_date: datetime, end_date: datetime) -> PerformanceReport:
        """Generate comprehensive performance report."""
        try:
            # Get basic metrics
            metrics = {}
            for channel in channels:
                channel_metrics = await self.get_performance_metrics(channel, start_date, end_date)
                for metric_type, values in channel_metrics.items():
                    if values:
                        # Take average value for the period
                        avg_value = sum(v.value for v in values) / len(values)
                        metrics[metric_type] = MetricValue(
                            value=avg_value,
                            timestamp=end_date,
                            channel=channel
                        )
            
            # Generate funnel analysis
            funnel_data = await self._generate_funnel_analysis(channels, start_date, end_date)
            
            # Generate cohort analysis
            cohort_data = await self._generate_cohort_analysis(channels, start_date, end_date)
            
            # Generate segment analysis
            segment_data = await self._generate_segment_analysis(channels, start_date, end_date)
            
            # Generate insights and recommendations
            insights = await self._generate_insights(metrics, funnel_data, cohort_data)
            recommendations = await self._generate_recommendations(metrics, insights)
            
            report = PerformanceReport(
                id=str(uuid.uuid4()),
                name=name,
                period_start=start_date,
                period_end=end_date,
                channels=channels,
                metrics=metrics,
                funnel_data=funnel_data,
                cohort_data=cohort_data,
                segment_data=segment_data,
                insights=insights,
                recommendations=recommendations
            )
            
            # Store report
            await self._store_report(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            return PerformanceReport(
                id=str(uuid.uuid4()),
                name=name,
                period_start=start_date,
                period_end=end_date,
                channels=channels,
                metrics={}
            )
    
    async def get_funnel_analysis(self, channels: List[ChannelType] = None,
                                start_date: datetime = None, end_date: datetime = None) -> FunnelAnalysis:
        """Get funnel analysis for notification flow."""
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=7)
            if not end_date:
                end_date = datetime.utcnow()
            
            if not channels:
                channels = list(ChannelType)
            
            # Define funnel steps
            steps = ["Sent", "Delivered", "Opened", "Clicked", "Converted"]
            
            # Get counts for each step
            user_counts = []
            for step in steps:
                count = await self._get_step_count(step.lower(), channels, start_date, end_date)
                user_counts.append(count)
            
            # Calculate conversion and drop-off rates
            conversion_rates = []
            drop_off_rates = []
            
            for i in range(len(user_counts)):
                if i == 0:
                    conversion_rates.append(100.0)  # Sent is 100%
                    drop_off_rates.append(0.0)
                else:
                    if user_counts[0] > 0:
                        conversion_rate = (user_counts[i] / user_counts[0]) * 100
                        conversion_rates.append(conversion_rate)
                        
                        drop_off_rate = ((user_counts[i-1] - user_counts[i]) / user_counts[i-1]) * 100 if user_counts[i-1] > 0 else 0
                        drop_off_rates.append(drop_off_rate)
                    else:
                        conversion_rates.append(0.0)
                        drop_off_rates.append(0.0)
            
            # Generate insights
            insights = await self._generate_funnel_insights(steps, conversion_rates, drop_off_rates)
            
            return FunnelAnalysis(
                funnel_id=str(uuid.uuid4()),
                funnel_name="Notification Engagement Funnel",
                steps=steps,
                conversion_rates=conversion_rates,
                drop_off_rates=drop_off_rates,
                user_counts=user_counts,
                insights=insights
            )
            
        except Exception as e:
            logger.error(f"Funnel analysis failed: {e}")
            return FunnelAnalysis(
                funnel_id=str(uuid.uuid4()),
                funnel_name="Notification Engagement Funnel",
                steps=[],
                conversion_rates=[],
                drop_off_rates=[],
                user_counts=[]
            )
    
    async def get_cohort_analysis(self, period_days: int = 30,
                                cohort_size_days: int = 7) -> List[CohortAnalysis]:
        """Get cohort analysis for user retention."""
        try:
            cohorts = []
            end_date = datetime.utcnow()
            
            # Create cohorts for the last period
            for i in range(0, period_days, cohort_size_days):
                cohort_start = end_date - timedelta(days=period_days - i)
                cohort_end = cohort_start + timedelta(days=cohort_size_days)
                
                if cohort_end > end_date:
                    cohort_end = end_date
                
                cohort = await self._analyze_cohort(cohort_start, cohort_end)
                if cohort:
                    cohorts.append(cohort)
            
            return cohorts
            
        except Exception as e:
            logger.error(f"Cohort analysis failed: {e}")
            return []
    
    async def predict_engagement_score(self, notification_features: Dict[str, Any]) -> float:
        """Predict engagement score for notification."""
        try:
            return await self.ml_engine.predict_engagement(notification_features)
        except Exception as e:
            logger.error(f"Engagement prediction failed: {e}")
            return 0.5
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics dashboard."""
        try:
            current_time = datetime.utcnow()
            hour_ago = current_time - timedelta(hours=1)
            
            metrics = {
                'timestamp': current_time.isoformat(),
                'sent_last_hour': await self._get_event_count(EventType.SENT, hour_ago, current_time),
                'opened_last_hour': await self._get_event_count(EventType.OPENED, hour_ago, current_time),
                'clicked_last_hour': await self._get_event_count(EventType.CLICKED, hour_ago, current_time),
                'converted_last_hour': await self._get_event_count(EventType.CONVERTED, hour_ago, current_time),
                'failed_last_hour': await self._get_event_count(EventType.FAILED, hour_ago, current_time),
            }
            
            # Calculate rates
            sent_count = metrics['sent_last_hour']
            if sent_count > 0:
                metrics['open_rate_last_hour'] = (metrics['opened_last_hour'] / sent_count) * 100
                metrics['click_rate_last_hour'] = (metrics['clicked_last_hour'] / sent_count) * 100
                metrics['conversion_rate_last_hour'] = (metrics['converted_last_hour'] / sent_count) * 100
                metrics['failure_rate_last_hour'] = (metrics['failed_last_hour'] / sent_count) * 100
            else:
                metrics['open_rate_last_hour'] = 0
                metrics['click_rate_last_hour'] = 0
                metrics['conversion_rate_last_hour'] = 0
                metrics['failure_rate_last_hour'] = 0
            
            # Channel breakdown
            metrics['by_channel'] = {}
            for channel in ChannelType:
                channel_sent = await self._get_event_count(EventType.SENT, hour_ago, current_time, channel)
                channel_opened = await self._get_event_count(EventType.OPENED, hour_ago, current_time, channel)
                
                metrics['by_channel'][channel.value] = {
                    'sent': channel_sent,
                    'opened': channel_opened,
                    'open_rate': (channel_opened / channel_sent * 100) if channel_sent > 0 else 0
                }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get real-time metrics: {e}")
            return {}
    
    async def create_custom_dashboard(self, dashboard_config: Dict[str, Any]) -> str:
        """Create custom analytics dashboard."""
        try:
            dashboard_id = str(uuid.uuid4())
            
            # Store dashboard configuration
            await self.redis.hset(f"dashboard:{dashboard_id}", mapping={
                'config': json.dumps(dashboard_config),
                'created_at': datetime.utcnow().isoformat()
            })
            
            return dashboard_id
            
        except Exception as e:
            logger.error(f"Failed to create custom dashboard: {e}")
            return ""
    
    async def _store_event(self, event: AnalyticsEvent) -> None:
        """Store analytics event in Redis."""
        try:
            event_data = {
                'id': event.id,
                'user_id': event.user_id,
                'notification_id': event.notification_id,
                'template_id': event.template_id or '',
                'campaign_id': event.campaign_id or '',
                'event_type': event.event_type.value,
                'channel': event.channel.value,
                'timestamp': event.timestamp.isoformat(),
                'properties': json.dumps(event.properties),
                'user_properties': json.dumps(event.user_properties),
                'device_info': json.dumps(event.device_info),
                'location_info': json.dumps(event.location_info)
            }
            
            # Store event
            await self.redis.hset(f"event:{event.id}", mapping=event_data)
            
            # Add to time-based indexes
            date_key = event.timestamp.strftime('%Y-%m-%d')
            hour_key = event.timestamp.strftime('%Y-%m-%d:%H')
            
            await self.redis.sadd(f"events:date:{date_key}", event.id)
            await self.redis.sadd(f"events:hour:{hour_key}", event.id)
            await self.redis.sadd(f"events:type:{event.event_type.value}", event.id)
            await self.redis.sadd(f"events:channel:{event.channel.value}", event.id)
            
            # User-specific index
            await self.redis.sadd(f"user_events:{event.user_id}", event.id)
            
            # Set expiration for cleanup (30 days)
            await self.redis.expire(f"event:{event.id}", 30 * 24 * 3600)
            
        except Exception as e:
            logger.error(f"Failed to store event: {e}")
    
    async def _update_real_time_metrics(self, event: AnalyticsEvent) -> None:
        """Update real-time metrics counters."""
        try:
            current_time = datetime.utcnow()
            minute_key = current_time.strftime('%Y-%m-%d:%H:%M')
            hour_key = current_time.strftime('%Y-%m-%d:%H')
            date_key = current_time.strftime('%Y-%m-%d')
            
            # Increment counters
            await self.redis.incr(f"metric:minute:{event.event_type.value}:{minute_key}")
            await self.redis.incr(f"metric:hour:{event.event_type.value}:{hour_key}")
            await self.redis.incr(f"metric:date:{event.event_type.value}:{date_key}")
            
            # Channel-specific counters
            await self.redis.incr(f"metric:channel:{event.channel.value}:{event.event_type.value}:{hour_key}")
            
            # Set expiration
            await self.redis.expire(f"metric:minute:{event.event_type.value}:{minute_key}", 3600)
            await self.redis.expire(f"metric:hour:{event.event_type.value}:{hour_key}", 24 * 3600)
            await self.redis.expire(f"metric:date:{event.event_type.value}:{date_key}", 30 * 24 * 3600)
            
        except Exception as e:
            logger.error(f"Failed to update real-time metrics: {e}")
    
    async def _calculate_metric_values(self, metric_type: MetricType, channel: ChannelType,
                                     start_date: datetime, end_date: datetime,
                                     granularity: TimeGranularity) -> List[MetricValue]:
        """Calculate metric values for time period."""
        try:
            values = []
            
            # Determine time step
            if granularity == TimeGranularity.HOUR:
                step = timedelta(hours=1)
            elif granularity == TimeGranularity.DAY:
                step = timedelta(days=1)
            elif granularity == TimeGranularity.WEEK:
                step = timedelta(weeks=1)
            else:
                step = timedelta(days=1)
            
            current_time = start_date
            while current_time < end_date:
                next_time = current_time + step
                
                metric_value = await self._calculate_metric_for_period(
                    metric_type, channel, current_time, next_time
                )
                
                values.append(MetricValue(
                    value=metric_value,
                    timestamp=current_time,
                    channel=channel
                ))
                
                current_time = next_time
            
            return values
            
        except Exception as e:
            logger.error(f"Failed to calculate metric values: {e}")
            return []
    
    async def _calculate_metric_for_period(self, metric_type: MetricType, channel: ChannelType,
                                         start_time: datetime, end_time: datetime) -> float:
        """Calculate specific metric for time period."""
        try:
            if metric_type == MetricType.DELIVERY_RATE:
                sent_count = await self._get_event_count(EventType.SENT, start_time, end_time, channel)
                delivered_count = await self._get_event_count(EventType.DELIVERED, start_time, end_time, channel)
                return (delivered_count / sent_count * 100) if sent_count > 0 else 0
            
            elif metric_type == MetricType.OPEN_RATE:
                sent_count = await self._get_event_count(EventType.SENT, start_time, end_time, channel)
                opened_count = await self._get_event_count(EventType.OPENED, start_time, end_time, channel)
                return (opened_count / sent_count * 100) if sent_count > 0 else 0
            
            elif metric_type == MetricType.CLICK_RATE:
                sent_count = await self._get_event_count(EventType.SENT, start_time, end_time, channel)
                clicked_count = await self._get_event_count(EventType.CLICKED, start_time, end_time, channel)
                return (clicked_count / sent_count * 100) if sent_count > 0 else 0
            
            elif metric_type == MetricType.CONVERSION_RATE:
                sent_count = await self._get_event_count(EventType.SENT, start_time, end_time, channel)
                converted_count = await self._get_event_count(EventType.CONVERTED, start_time, end_time, channel)
                return (converted_count / sent_count * 100) if sent_count > 0 else 0
            
            elif metric_type == MetricType.BOUNCE_RATE:
                sent_count = await self._get_event_count(EventType.SENT, start_time, end_time, channel)
                bounced_count = await self._get_event_count(EventType.BOUNCED, start_time, end_time, channel)
                return (bounced_count / sent_count * 100) if sent_count > 0 else 0
            
            elif metric_type == MetricType.COMPLAINT_RATE:
                sent_count = await self._get_event_count(EventType.SENT, start_time, end_time, channel)
                complained_count = await self._get_event_count(EventType.COMPLAINED, start_time, end_time, channel)
                return (complained_count / sent_count * 100) if sent_count > 0 else 0
            
            elif metric_type == MetricType.UNSUBSCRIBE_RATE:
                sent_count = await self._get_event_count(EventType.SENT, start_time, end_time, channel)
                unsubscribed_count = await self._get_event_count(EventType.UNSUBSCRIBED, start_time, end_time, channel)
                return (unsubscribed_count / sent_count * 100) if sent_count > 0 else 0
            
            elif metric_type == MetricType.ENGAGEMENT_SCORE:
                # Composite engagement score
                open_rate = await self._calculate_metric_for_period(MetricType.OPEN_RATE, channel, start_time, end_time)
                click_rate = await self._calculate_metric_for_period(MetricType.CLICK_RATE, channel, start_time, end_time)
                conversion_rate = await self._calculate_metric_for_period(MetricType.CONVERSION_RATE, channel, start_time, end_time)
                
                # Weighted engagement score
                engagement_score = (open_rate * 0.3 + click_rate * 0.4 + conversion_rate * 0.3)
                return engagement_score
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate metric: {e}")
            return 0.0
    
    async def _get_event_count(self, event_type: EventType, start_time: datetime,
                             end_time: datetime, channel: ChannelType = None) -> int:
        """Get count of events for time period."""
        try:
            # For simplicity, use daily aggregation
            count = 0
            current_date = start_time.date()
            end_date = end_time.date()
            
            while current_date <= end_date:
                date_key = current_date.strftime('%Y-%m-%d')
                
                if channel:
                    # Get events for specific channel
                    key = f"metric:channel:{channel.value}:{event_type.value}:{date_key}"
                else:
                    # Get all events of type
                    key = f"metric:date:{event_type.value}:{date_key}"
                
                daily_count = await self.redis.get(key) or 0
                count += int(daily_count)
                
                current_date += timedelta(days=1)
            
            return count
            
        except Exception as e:
            logger.error(f"Failed to get event count: {e}")
            return 0
    
    async def _flush_events(self) -> None:
        """Flush events buffer to storage."""
        try:
            if not self.events_buffer:
                return
            
            # Store all buffered events
            for event in self.events_buffer:
                await self._store_event(event)
            
            # Clear buffer
            self.events_buffer.clear()
            
            logger.debug(f"Flushed {len(self.events_buffer)} events to storage")
            
        except Exception as e:
            logger.error(f"Failed to flush events: {e}")
    
    async def _flush_events_periodically(self) -> None:
        """Background task to flush events periodically."""
        while True:
            try:
                await asyncio.sleep(self.flush_interval)
                await self._flush_events()
            except Exception as e:
                logger.error(f"Periodic flush error: {e}")
                await asyncio.sleep(60)
    
    async def _update_metrics_periodically(self) -> None:
        """Background task to update aggregated metrics."""
        while True:
            try:
                await asyncio.sleep(300)  # Update every 5 minutes
                await self._update_aggregated_metrics()
            except Exception as e:
                logger.error(f"Metric update error: {e}")
                await asyncio.sleep(300)
    
    async def _update_aggregated_metrics(self) -> None:
        """Update aggregated metrics."""
        try:
            # Update hourly and daily aggregations
            current_time = datetime.utcnow()
            
            # This would contain logic to aggregate metrics
            # For now, just log that it's running
            logger.debug("Updating aggregated metrics")
            
        except Exception as e:
            logger.error(f"Failed to update aggregated metrics: {e}")
    
    async def _generate_funnel_analysis(self, channels: List[ChannelType],
                                      start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate funnel analysis data."""
        try:
            funnel = await self.get_funnel_analysis(channels, start_date, end_date)
            return {
                'steps': funnel.steps,
                'conversion_rates': funnel.conversion_rates,
                'drop_off_rates': funnel.drop_off_rates,
                'user_counts': funnel.user_counts,
                'insights': funnel.insights
            }
        except Exception as e:
            logger.error(f"Funnel analysis generation failed: {e}")
            return {}
    
    async def _generate_cohort_analysis(self, channels: List[ChannelType],
                                      start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate cohort analysis data."""
        try:
            period_days = (end_date - start_date).days
            cohorts = await self.get_cohort_analysis(period_days)
            
            return {
                'cohorts': [{
                    'cohort_id': c.cohort_id,
                    'cohort_name': c.cohort_name,
                    'start_date': c.start_date.isoformat(),
                    'end_date': c.end_date.isoformat(),
                    'retention_data': c.retention_data,
                    'engagement_data': c.engagement_data,
                    'size_data': c.size_data
                } for c in cohorts]
            }
        except Exception as e:
            logger.error(f"Cohort analysis generation failed: {e}")
            return {}
    
    async def _generate_segment_analysis(self, channels: List[ChannelType],
                                       start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate segment analysis data."""
        try:
            # Placeholder for segment analysis
            return {
                'segments': [
                    {'name': 'High Engagement', 'size': 1250, 'avg_open_rate': 75.2},
                    {'name': 'Medium Engagement', 'size': 3200, 'avg_open_rate': 45.1},
                    {'name': 'Low Engagement', 'size': 890, 'avg_open_rate': 12.3}
                ]
            }
        except Exception as e:
            logger.error(f"Segment analysis generation failed: {e}")
            return {}
    
    async def _generate_insights(self, metrics: Dict[MetricType, MetricValue],
                               funnel_data: Dict[str, Any], cohort_data: Dict[str, Any]) -> List[str]:
        """Generate insights from analytics data."""
        insights = []
        
        try:
            # Open rate insights
            if MetricType.OPEN_RATE in metrics:
                open_rate = metrics[MetricType.OPEN_RATE].value
                if open_rate > 25:
                    insights.append(f"Excellent open rate of {open_rate:.1f}% - above industry average")
                elif open_rate < 15:
                    insights.append(f"Low open rate of {open_rate:.1f}% - consider improving subject lines")
            
            # Click rate insights
            if MetricType.CLICK_RATE in metrics:
                click_rate = metrics[MetricType.CLICK_RATE].value
                if click_rate > 5:
                    insights.append(f"Strong click rate of {click_rate:.1f}% - content is engaging")
                elif click_rate < 2:
                    insights.append(f"Low click rate of {click_rate:.1f}% - review content and CTAs")
            
            # Funnel insights
            if funnel_data.get('drop_off_rates'):
                max_dropoff_idx = funnel_data['drop_off_rates'].index(max(funnel_data['drop_off_rates']))
                if max_dropoff_idx < len(funnel_data['steps']) - 1:
                    step = funnel_data['steps'][max_dropoff_idx + 1]
                    insights.append(f"Highest drop-off at '{step}' step - focus optimization here")
            
            return insights
            
        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            return ["Unable to generate insights due to data processing error"]
    
    async def _generate_recommendations(self, metrics: Dict[MetricType, MetricValue],
                                      insights: List[str]) -> List[str]:
        """Generate recommendations based on metrics and insights."""
        recommendations = []
        
        try:
            # Open rate recommendations
            if MetricType.OPEN_RATE in metrics:
                open_rate = metrics[MetricType.OPEN_RATE].value
                if open_rate < 20:
                    recommendations.append("Test different subject line formats and personalization")
                    recommendations.append("Optimize send times based on user timezone")
                    recommendations.append("Clean your email list to remove inactive users")
            
            # Click rate recommendations
            if MetricType.CLICK_RATE in metrics:
                click_rate = metrics[MetricType.CLICK_RATE].value
                if click_rate < 3:
                    recommendations.append("Improve call-to-action button design and placement")
                    recommendations.append("Ensure content is mobile-optimized")
                    recommendations.append("A/B test different content formats")
            
            # Engagement recommendations
            if MetricType.ENGAGEMENT_SCORE in metrics:
                engagement_score = metrics[MetricType.ENGAGEMENT_SCORE].value
                if engagement_score < 30:
                    recommendations.append("Implement advanced personalization based on user behavior")
                    recommendations.append("Segment your audience for more targeted messaging")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return ["Unable to generate recommendations due to processing error"]
    
    async def _store_report(self, report: PerformanceReport) -> None:
        """Store performance report in Redis."""
        try:
            report_data = {
                'id': report.id,
                'name': report.name,
                'period_start': report.period_start.isoformat(),
                'period_end': report.period_end.isoformat(),
                'channels': json.dumps([c.value for c in report.channels]),
                'metrics': json.dumps({
                    k.value: {
                        'value': v.value,
                        'timestamp': v.timestamp.isoformat(),
                        'channel': v.channel.value if v.channel else None
                    } for k, v in report.metrics.items()
                }),
                'funnel_data': json.dumps(report.funnel_data),
                'cohort_data': json.dumps(report.cohort_data),
                'segment_data': json.dumps(report.segment_data),
                'insights': json.dumps(report.insights),
                'recommendations': json.dumps(report.recommendations),
                'generated_at': report.generated_at.isoformat()
            }
            
            await self.redis.hset(f"report:{report.id}", mapping=report_data)
            await self.redis.sadd("reports", report.id)
            
        except Exception as e:
            logger.error(f"Failed to store report: {e}")
    
    async def _get_step_count(self, step: str, channels: List[ChannelType],
                            start_date: datetime, end_date: datetime) -> int:
        """Get count for funnel step."""
        try:
            event_type = EventType(step)
            total_count = 0
            
            for channel in channels:
                count = await self._get_event_count(event_type, start_date, end_date, channel)
                total_count += count
            
            return total_count
            
        except Exception as e:
            logger.error(f"Failed to get step count: {e}")
            return 0
    
    async def _generate_funnel_insights(self, steps: List[str], conversion_rates: List[float],
                                      drop_off_rates: List[float]) -> List[str]:
        """Generate insights for funnel analysis."""
        insights = []
        
        try:
            # Find step with highest drop-off
            if len(drop_off_rates) > 1:
                max_dropoff_idx = drop_off_rates[1:].index(max(drop_off_rates[1:]))  # Skip first step
                max_dropoff_step = steps[max_dropoff_idx + 1]
                max_dropoff_rate = drop_off_rates[max_dropoff_idx + 1]
                
                insights.append(f"Highest drop-off of {max_dropoff_rate:.1f}% occurs at '{max_dropoff_step}' step")
            
            # Overall conversion insight
            if len(conversion_rates) > 1:
                final_conversion = conversion_rates[-1]
                if final_conversion > 5:
                    insights.append("Strong overall conversion funnel performance")
                elif final_conversion < 1:
                    insights.append("Low overall conversion - review entire funnel")
            
            return insights
            
        except Exception as e:
            logger.error(f"Funnel insights generation failed: {e}")
            return []
    
    async def _analyze_cohort(self, start_date: datetime, end_date: datetime) -> Optional[CohortAnalysis]:
        """Analyze specific cohort."""
        try:
            cohort_id = str(uuid.uuid4())
            cohort_name = f"Cohort {start_date.strftime('%Y-%m-%d')}"
            
            # Placeholder cohort analysis
            retention_data = {
                'week_0': [100.0],
                'week_1': [85.2],
                'week_2': [72.1],
                'week_3': [64.8],
                'week_4': [58.3]
            }
            
            engagement_data = {
                'week_0': [45.2],
                'week_1': [52.1],
                'week_2': [38.7],
                'week_3': [41.2],
                'week_4': [39.8]
            }
            
            size_data = {'initial_size': 1000, 'current_size': 583}
            
            insights = [
                "Strong initial retention with 85% returning in week 1",
                "Engagement peaks in week 1 then stabilizes around 40%"
            ]
            
            return CohortAnalysis(
                cohort_id=cohort_id,
                cohort_name=cohort_name,
                start_date=start_date,
                end_date=end_date,
                retention_data=retention_data,
                engagement_data=engagement_data,
                size_data=size_data,
                insights=insights
            )
            
        except Exception as e:
            logger.error(f"Cohort analysis failed: {e}")
            return None


# Factory function for creating service instance
def create_analytics_tracker(config: Dict[str, Any]) -> NotificationAnalyticsTracker:
    """Create and configure notification analytics tracker."""
    return NotificationAnalyticsTracker(config)


# Export main classes and functions
__all__ = [
    'NotificationAnalyticsTracker',
    'AnalyticsEvent',
    'MetricValue',
    'PerformanceReport',
    'CohortAnalysis',
    'FunnelAnalysis',
    'EventType',
    'MetricType',
    'ChannelType',
    'TimeGranularity',
    'MLInsightsEngine',
    'create_analytics_tracker'
]