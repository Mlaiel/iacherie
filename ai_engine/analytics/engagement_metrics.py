"""Engagement Metrics Analyzer - Advanced Metrics Collection and Analysis
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive engagement metrics analysis, real-time tracking,
and performance insights for social media content and user interactions.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import statistics
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """
Types of engagement metrics"""

    IMPRESSION = "impression"
    VIEW = "view"
    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"
    SAVE = "save"
    CLICK = "click"
    FOLLOW = "follow"
    UNFOLLOW = "unfollow"
    REACTION = "reaction"
    MENTION = "mention"
    TAG = "tag"
    BOOKMARK = "bookmark"
    REPOST = "repost"
    QUOTE = "quote"
    DOWNLOAD = "download"
    SUBSCRIPTION = "subscription"

class PlatformType(Enum):
    """Social media platforms"""

    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    DISCORD = "discord"
    REDDIT = "reddit"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    WEBSITE = "website"
    EMAIL = "email"
    SMS = "sms"

class EngagementLevel(Enum):
    """Engagement quality levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VIRAL = "viral"
    EXCEPTIONAL = "exceptional"

class TimeFrame(Enum):
    """Time frames for metrics analysis"""

    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

@dataclass
class MetricEvent:
    """Individual metric event"""
    event_id: str
    metric_type: MetricType
    platform: PlatformType
    content_id: str
    user_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    value: Union[int, float] = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    geo_location: Optional[Dict[str, str]] = None
    user_agent: Optional[str] = None
    device_type: Optional[str] = None
    source: Optional[str] = None

@dataclass
class EngagementSummary:
    """
Summary of engagement metrics"""
    content_id: str
    platform: PlatformType
    time_period: Dict[str, datetime] = field(default_factory=dict)
    total_impressions: int = 0
    total_views: int = 0
    total_likes: int = 0
    total_comments: int = 0
    total_shares: int = 0
    total_saves: int = 0
    total_clicks: int = 0
    total_follows: int = 0
    engagement_rate: float = 0.0
    viral_coefficient: float = 0.0
    quality_score: float = 0.0
    top_countries: List[str] = field(default_factory=list)
    top_devices: List[str] = field(default_factory=list)
    peak_engagement_time: Optional[datetime] = None
    demographic_breakdown: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RealTimeMetrics:
    """
Real-time engagement metrics"""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    active_users: int = 0
    current_engagement_rate: float = 0.0
    trending_content: List[str] = field(default_factory=list)
    platform_activity: Dict[str, int] = field(default_factory=dict)
    geographic_hotspots: List[Dict[str, Any]] = field(default_factory=list)
    sentiment_breakdown: Dict[str, float] = field(default_factory=dict)

@dataclass
class EngagementTrend:
    """
Engagement trend analysis"""
    metric_type: MetricType
    platform: PlatformType
    time_frame: TimeFrame
    trend_direction: str = "stable"  # up, down, stable, volatile
    trend_strength: float = 0.0  # -1.0 to 1.0
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    seasonal_pattern: Optional[str] = None
    anomalies: List[Dict[str, Any]] = field(default_factory=list)
    predictions: Dict[str, float] = field(default_factory=dict)

class EngagementMetricsAnalyzer:
    """Main engagement metrics analysis engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.metric_events = []
        self.engagement_summaries = {}
        self.real_time_data = RealTimeMetrics()
        self.trend_cache = {}
        self.performance_benchmarks = self._load_performance_benchmarks()
        self.demographic_cache = {}
        self._initialize_analytics()
        self.logger.info("EngagementMetricsAnalyzer initialized successfully")
    
    def _load_performance_benchmarks(self) -> Dict[str, Dict[str, float]]:
        """Load platform-specific performance benchmarks"""
        return {
            PlatformType.INSTAGRAM.value: {
                "engagement_rate": {"excellent": 0.06, "good": 0.03, "average": 0.015, "poor": 0.005},
                "comment_rate": {"excellent": 0.004, "good": 0.002, "average": 0.001, "poor": 0.0005},
                "save_rate": {"excellent": 0.02, "good": 0.01, "average": 0.005, "poor": 0.001},
                "share_rate": {"excellent": 0.01, "good": 0.005, "average": 0.002, "poor": 0.0005}
            },
            PlatformType.FACEBOOK.value: {
                "engagement_rate": {"excellent": 0.09, "good": 0.045, "average": 0.025, "poor": 0.01},
                "comment_rate": {"excellent": 0.003, "good": 0.0015, "average": 0.0008, "poor": 0.0003},
                "share_rate": {"excellent": 0.005, "good": 0.0025, "average": 0.001, "poor": 0.0003},
                "click_rate": {"excellent": 0.012, "good": 0.008, "average": 0.005, "poor": 0.002}
            },
            PlatformType.TWITTER.value: {
                "engagement_rate": {"excellent": 0.05, "good": 0.025, "average": 0.015, "poor": 0.005},
                "retweet_rate": {"excellent": 0.01, "good": 0.005, "average": 0.002, "poor": 0.0005},
                "reply_rate": {"excellent": 0.003, "good": 0.0015, "average": 0.0008, "poor": 0.0003},
                "click_rate": {"excellent": 0.02, "good": 0.01, "average": 0.005, "poor": 0.002}
            },
            PlatformType.LINKEDIN.value: {
                "engagement_rate": {"excellent": 0.06, "good": 0.03, "average": 0.02, "poor": 0.008},
                "comment_rate": {"excellent": 0.005, "good": 0.0025, "average": 0.001, "poor": 0.0003},
                "share_rate": {"excellent": 0.008, "good": 0.004, "average": 0.002, "poor": 0.0005},
                "click_rate": {"excellent": 0.025, "good": 0.015, "average": 0.008, "poor": 0.003}
            },
            PlatformType.YOUTUBE.value: {
                "engagement_rate": {"excellent": 0.04, "good": 0.02, "average": 0.01, "poor": 0.003},
                "comment_rate": {"excellent": 0.005, "good": 0.0025, "average": 0.001, "poor": 0.0003},
                "like_rate": {"excellent": 0.03, "good": 0.015, "average": 0.008, "poor": 0.002},
                "subscription_rate": {"excellent": 0.01, "good": 0.005, "average": 0.002, "poor": 0.0005}
            },
            PlatformType.TIKTOK.value: {
                "engagement_rate": {"excellent": 0.18, "good": 0.09, "average": 0.055, "poor": 0.02},
                "comment_rate": {"excellent": 0.008, "good": 0.004, "average": 0.002, "poor": 0.0008},
                "share_rate": {"excellent": 0.02, "good": 0.01, "average": 0.005, "poor": 0.001},
                "like_rate": {"excellent": 0.15, "good": 0.08, "average": 0.045, "poor": 0.015}
            }
        }
    
    def _initialize_analytics(self):
        """Initialize analytics components"""
        self.engagement_patterns = {
            "peak_hours": {},  # Platform -> hour -> engagement_level
            "day_patterns": {},  # Platform -> day -> engagement_level
            "content_performance": {},  # content_type -> metrics
            "user_behavior": {},  # user_segments -> behavior_patterns
            "geographic_insights": {}  # region -> engagement_characteristics
        }
        
        self.anomaly_detectors = {}
        self.trend_predictors = {}
        self.real_time_monitors = {}
    
    def record_metric_event(self, event: MetricEvent) -> bool:
        """Record a new metric event"""
        try:
            # Validate event
            if not event.event_id or not event.content_id:
                self.logger.warning("Invalid metric event: missing required fields")
                return False
            
            # Store event
            self.metric_events.append(event)
            
            # Update real-time metrics
            self._update_real_time_metrics(event)
            
            # Update engagement summary
            self._update_engagement_summary(event)
            
            # Trigger anomaly detection
            self._check_for_anomalies(event)
            
            self.logger.debug(f"Recorded metric event: {event.metric_type.value} for {event.content_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to record metric event: {e}")
            return False
    
    def _update_real_time_metrics(self, event: MetricEvent):
        """Update real-time metrics with new event"""
        try:
            # Update platform activity
            platform_key = event.platform.value
            if platform_key not in self.real_time_data.platform_activity:
                self.real_time_data.platform_activity[platform_key] = 0
            self.real_time_data.platform_activity[platform_key] += 1
            
            # Update geographic data if available
            if event.geo_location:
                country = event.geo_location.get('country', 'Unknown')
                geo_entry = {
                    'country': country,
                    'activity_count': 1,
                    'timestamp': event.timestamp
                }
                
                # Update or add geographic hotspot
                found = False
                for hotspot in self.real_time_data.geographic_hotspots:
                    if hotspot['country'] == country:
                        hotspot['activity_count'] += 1
                        hotspot['timestamp'] = event.timestamp
                        found = True
                        break
                
                if not found:
                    self.real_time_data.geographic_hotspots.append(geo_entry)
            
            # Maintain only recent geographic data
            cutoff = datetime.utcnow() - timedelta(hours=1)
            self.real_time_data.geographic_hotspots = [
                h for h in self.real_time_data.geographic_hotspots 
                if h['timestamp'] > cutoff
            ]
            
            # Update timestamp
            self.real_time_data.timestamp = datetime.utcnow()
            
        except Exception as e:
            self.logger.error(f"Failed to update real-time metrics: {e}")
    
    def _update_engagement_summary(self, event: MetricEvent):
        """Update engagement summary for content"""
        try:
            summary_key = f"{event.content_id}_{event.platform.value}"
            
            if summary_key not in self.engagement_summaries:
                self.engagement_summaries[summary_key] = EngagementSummary(
                    content_id=event.content_id,
                    platform=event.platform,
                    time_period={
                        'start': event.timestamp,
                        'end': event.timestamp
                    }
                )
            
            summary = self.engagement_summaries[summary_key]
            
            # Update time period
            if event.timestamp < summary.time_period['start']:
                summary.time_period['start'] = event.timestamp
            if event.timestamp > summary.time_period['end']:
                summary.time_period['end'] = event.timestamp
            
            # Update metric counts
            if event.metric_type == MetricType.IMPRESSION:
                summary.total_impressions += int(event.value)
            elif event.metric_type == MetricType.VIEW:
                summary.total_views += int(event.value)
            elif event.metric_type == MetricType.LIKE:
                summary.total_likes += int(event.value)
            elif event.metric_type == MetricType.COMMENT:
                summary.total_comments += int(event.value)
            elif event.metric_type == MetricType.SHARE:
                summary.total_shares += int(event.value)
            elif event.metric_type == MetricType.SAVE:
                summary.total_saves += int(event.value)
            elif event.metric_type == MetricType.CLICK:
                summary.total_clicks += int(event.value)
            elif event.metric_type == MetricType.FOLLOW:
                summary.total_follows += int(event.value)
            
            # Recalculate engagement rate
            total_engagement = (summary.total_likes + summary.total_comments + 
                              summary.total_shares + summary.total_saves + 
                              summary.total_clicks)
            
            if summary.total_impressions > 0:
                summary.engagement_rate = total_engagement / summary.total_impressions
            elif summary.total_views > 0:
                summary.engagement_rate = total_engagement / summary.total_views
            
            # Update geographic and device data
            if event.geo_location and 'country' in event.geo_location:
                country = event.geo_location['country']
                if country not in summary.top_countries:
                    summary.top_countries.append(country)
                    summary.top_countries = summary.top_countries[:10]  # Keep top 10
            
            if event.device_type:
                if event.device_type not in summary.top_devices:
                    summary.top_devices.append(event.device_type)
                    summary.top_devices = summary.top_devices[:5]  # Keep top 5
            
        except Exception as e:
            self.logger.error(f"Failed to update engagement summary: {e}")
    
    def _check_for_anomalies(self, event: MetricEvent):
        """Check for anomalous engagement patterns"""
        try:
            # Simple anomaly detection based on recent activity
            recent_events = [
                e for e in self.metric_events 
                if (e.content_id == event.content_id and 
                    e.metric_type == event.metric_type and
                    (event.timestamp - e.timestamp).total_seconds() < 3600)  # Last hour
            ]
            
            if len(recent_events) > 1:
                values = [e.value for e in recent_events]
                avg_value = statistics.mean(values)
                
                # Check if current value is significantly higher (potential viral content)
                if event.value > avg_value * 3:
                    self.logger.info(f"Potential viral content detected: {event.content_id}")
                    # Could trigger alerts or special processing here
                
                # Check for suspicious activity (potential bots)
                if len(recent_events) > 100:  # Too many events in short time
                    self.logger.warning(f"Suspicious activity detected: {event.content_id}")
            
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {e}")
    
    def get_engagement_summary(self, content_id: str, platform: PlatformType) -> Optional[EngagementSummary]:
        """Get engagement summary for specific content"""
        summary_key = f"{content_id}_{platform.value}"
        return self.engagement_summaries.get(summary_key)
    
    def calculate_engagement_rate(self, content_id: str, platform: PlatformType) -> float:
        """Calculate current engagement rate for content"""
        summary = self.get_engagement_summary(content_id, platform)
        if summary:
            return summary.engagement_rate
        return 0.0
    
    def analyze_performance_trends(self, platform: PlatformType, 
                                 days_back: int = 30) -> Dict[str, Any]:
        """
Analyze performance trends over time"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days_back)
            
            # Filter relevant events
            relevant_events = [
                e for e in self.metric_events
                if e.platform == platform and start_time <= e.timestamp <= end_time
            ]
            
            if not relevant_events:
                return {"message": "No data available for analysis"}
            
            # Group events by day
            daily_metrics = defaultdict(lambda: defaultdict(int))
            for event in relevant_events:
                day_key = event.timestamp.strftime('%Y-%m-%d')
                daily_metrics[day_key][event.metric_type.value] += event.value
            
            # Calculate trends
            trends = {}
            for metric_type in MetricType:
                daily_values = [daily_metrics[day].get(metric_type.value, 0) 
                               for day in sorted(daily_metrics.keys())]
                
                if daily_values and len(daily_values) > 1:
                    # Simple linear trend calculation
                    x_values = list(range(len(daily_values)))
                    if sum(daily_values) > 0:
                        # Calculate slope
                        n = len(daily_values)
                        sum_x = sum(x_values)
                        sum_y = sum(daily_values)
                        sum_xy = sum(x * y for x, y in zip(x_values, daily_values))
                        sum_x_squared = sum(x * x for x in x_values)
                        
                        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x_squared - sum_x * sum_x)
                        
                        # Determine trend direction
                        if abs(slope) < 0.1:
                            direction = "stable"
                        elif slope > 0:
                            direction = "increasing"
                        else:
                            direction = "decreasing"
                        
                        trends[metric_type.value] = {
                            "direction": direction,
                            "slope": slope,
                            "average": statistics.mean(daily_values),
                            "total": sum(daily_values)
                        }
            
            return {
                "platform": platform.value,
                "period": f"{days_back} days",
                "total_events": len(relevant_events),
                "trends": trends,
                "daily_breakdown": dict(daily_metrics)
            }
            
        except Exception as e:
            self.logger.error(f"Performance trend analysis failed: {e}")
            return {"error": str(e)}
    
    def get_top_performing_content(self, platform: Optional[PlatformType] = None, 
                                 metric_type: MetricType = MetricType.LIKE,
                                 limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing content by metric"""
        try:
            # Filter summaries by platform if specified
            relevant_summaries = []
            for summary in self.engagement_summaries.values():
                if platform is None or summary.platform == platform:
                    relevant_summaries.append(summary)
            
            # Sort by specified metric
            if metric_type == MetricType.LIKE:
                sorted_summaries = sorted(relevant_summaries, 
                                        key=lambda s: s.total_likes, reverse=True)
            elif metric_type == MetricType.COMMENT:
                sorted_summaries = sorted(relevant_summaries, 
                                        key=lambda s: s.total_comments, reverse=True)
            elif metric_type == MetricType.SHARE:
                sorted_summaries = sorted(relevant_summaries, 
                                        key=lambda s: s.total_shares, reverse=True)
            elif metric_type == MetricType.VIEW:
                sorted_summaries = sorted(relevant_summaries, 
                                        key=lambda s: s.total_views, reverse=True)
            else:
                # Default to engagement rate
                sorted_summaries = sorted(relevant_summaries, 
                                        key=lambda s: s.engagement_rate, reverse=True)
            
            # Convert to dict format
            top_content = []
            for summary in sorted_summaries[:limit]:
                content_info = {
                    "content_id": summary.content_id,
                    "platform": summary.platform.value,
                    "engagement_rate": summary.engagement_rate,
                    "total_impressions": summary.total_impressions,
                    "total_likes": summary.total_likes,
                    "total_comments": summary.total_comments,
                    "total_shares": summary.total_shares,
                    "total_views": summary.total_views,
                    "performance_period": summary.time_period
                }
                top_content.append(content_info)
            
            return top_content
            
        except Exception as e:
            self.logger.error(f"Failed to get top performing content: {e}")
            return []
    
    def calculate_viral_coefficient(self, content_id: str, platform: PlatformType) -> float:
        """Calculate viral coefficient (shares per impression)"""
        try:
            summary = self.get_engagement_summary(content_id, platform)
            if summary and summary.total_impressions > 0:
                viral_coefficient = (summary.total_shares + summary.total_saves) / summary.total_impressions
                summary.viral_coefficient = viral_coefficient
                return viral_coefficient
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Failed to calculate viral coefficient: {e}")
            return 0.0
    
    def get_engagement_benchmarks(self, platform: PlatformType) -> Dict[str, Any]:
        """Get engagement benchmarks for platform"""
        return self.performance_benchmarks.get(platform.value, {})
    
    def analyze_audience_behavior(self, content_id: str, platform: PlatformType) -> Dict[str, Any]:
        """
Analyze audience behavior patterns"""
        try:
            relevant_events = [
                e for e in self.metric_events
                if e.content_id == content_id and e.platform == platform
            ]
            
            if not relevant_events:
                return {"message": "No audience data available"}
            
            # Analyze timing patterns
            hourly_activity = defaultdict(int)
            daily_activity = defaultdict(int)
            device_breakdown = Counter()
            geographic_distribution = Counter()
            
            for event in relevant_events:
                hourly_activity[event.timestamp.hour] += 1
                daily_activity[event.timestamp.strftime('%A')] += 1
                
                if event.device_type:
                    device_breakdown[event.device_type] += 1
                
                if event.geo_location and 'country' in event.geo_location:
                    geographic_distribution[event.geo_location['country']] += 1
            
            # Find peak engagement times
            peak_hour = max(hourly_activity.items(), key=lambda x: x[1])[0] if hourly_activity else 12
            peak_day = max(daily_activity.items(), key=lambda x: x[1])[0] if daily_activity else "Monday"
            
            return {
                "content_id": content_id,
                "platform": platform.value,
                "total_interactions": len(relevant_events),
                "peak_engagement_hour": peak_hour,
                "peak_engagement_day": peak_day,
                "hourly_distribution": dict(hourly_activity),
                "daily_distribution": dict(daily_activity),
                "top_devices": dict(device_breakdown.most_common(5)),
                "top_countries": dict(geographic_distribution.most_common(10)),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Audience behavior analysis failed: {e}")
            return {"error": str(e)}
    
    def get_real_time_metrics(self) -> RealTimeMetrics:
        """Get current real-time engagement metrics"""
        # Update current engagement rate based on recent activity
        recent_events = [
            e for e in self.metric_events
            if (datetime.utcnow() - e.timestamp).total_seconds() < 300  # Last 5 minutes
        ]
        
        if recent_events:
            engagement_events = [
                e for e in recent_events 
                if e.metric_type in [MetricType.LIKE, MetricType.COMMENT, MetricType.SHARE]
            ]
            
            view_events = [
                e for e in recent_events 
                if e.metric_type in [MetricType.VIEW, MetricType.IMPRESSION]
            ]
            
            if view_events and engagement_events:
                self.real_time_data.current_engagement_rate = len(engagement_events) / len(view_events)
        
        # Update active users (unique users in last 5 minutes)
        unique_users = set()
        for event in recent_events:
            if event.user_id:
                unique_users.add(event.user_id)
        
        self.real_time_data.active_users = len(unique_users)
        
        return self.real_time_data
    
    def export_metrics(self, format_type: str = "json") -> Union[str, Dict[str, Any]]:
        """Export collected metrics in specified format"""
        try:
            export_data = {
                "export_timestamp": datetime.utcnow().isoformat(),
                "total_events": len(self.metric_events),
                "total_summaries": len(self.engagement_summaries),
                "summaries": [
                    {
                        "content_id": s.content_id,
                        "platform": s.platform.value,
                        "engagement_rate": s.engagement_rate,
                        "total_impressions": s.total_impressions,
                        "total_views": s.total_views,
                        "total_likes": s.total_likes,
                        "total_comments": s.total_comments,
                        "total_shares": s.total_shares,
                        "time_period": {
                            "start": s.time_period['start'].isoformat() if 'start' in s.time_period else None,
                            "end": s.time_period['end'].isoformat() if 'end' in s.time_period else None
                        }
                    }
                    for s in self.engagement_summaries.values()
                ],
                "real_time_data": {
                    "timestamp": self.real_time_data.timestamp.isoformat(),
                    "active_users": self.real_time_data.active_users,
                    "current_engagement_rate": self.real_time_data.current_engagement_rate,
                    "platform_activity": self.real_time_data.platform_activity
                }
            }
            
            if format_type.lower() == "json":
                return json.dumps(export_data, indent=2)
            else:
                return export_data
                
        except Exception as e:
            self.logger.error(f"Failed to export metrics: {e}")
            return {"error": str(e)}

# Export main classes
__all__ = [
    'EngagementMetricsAnalyzer',
    'MetricEvent',
    'EngagementSummary',
    'RealTimeMetrics',
    'EngagementTrend',
    'MetricType',
    'PlatformType',
    'EngagementLevel',
    'TimeFrame'
]

logger.info("Engagement metrics analyzer module loaded successfully")
