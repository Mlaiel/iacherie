"""
Platform Metrics Module

Advanced metrics collection and analysis for platform performance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import logging
import statistics
from collections import defaultdict, deque
import time

from .base import PlatformBase, AnalyticsData, PlatformType

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics to collect"""
    PERFORMANCE = "performance"
    ENGAGEMENT = "engagement"
    GROWTH = "growth"
    REVENUE = "revenue"
    TECHNICAL = "technical"
    USER_BEHAVIOR = "user_behavior"


class MetricInterval(Enum):
    """Metric collection intervals"""
    REAL_TIME = "real_time"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    value: Union[int, float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'value': self.value,
            'metadata': self.metadata
        }


@dataclass
class MetricSeries:
    """Time series of metric points"""
    metric_name: str
    metric_type: MetricType
    platform_id: str
    data_points: List[MetricPoint] = field(default_factory=list)
    max_points: int = 1000
    
    def add_point(self, value: Union[int, float], metadata: Dict[str, Any] = None):
        """Add data point to series"""
        point = MetricPoint(
            timestamp=datetime.utcnow(),
            value=value,
            metadata=metadata or {}
        )
        
        self.data_points.append(point)
        
        # Keep only latest points
        if len(self.data_points) > self.max_points:
            self.data_points = self.data_points[-self.max_points:]
    
    def get_latest_value(self) -> Optional[Union[int, float]]:
        """Get latest metric value"""
        if self.data_points:
            return self.data_points[-1].value
        return None
    
    def get_average(self, hours: int = 24) -> Optional[float]:
        """Get average value over time period"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        relevant_points = [
            point for point in self.data_points 
            if point.timestamp > cutoff
        ]
        
        if relevant_points:
            return statistics.mean([point.value for point in relevant_points])
        return None
    
    def get_trend(self, hours: int = 24) -> Optional[str]:
        """Get trend direction over time period"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        relevant_points = [
            point for point in self.data_points 
            if point.timestamp > cutoff
        ]
        
        if len(relevant_points) < 2:
            return None
        
        # Simple trend calculation
        values = [point.value for point in relevant_points]
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        if not first_half or not second_half:
            return "stable"
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        change_percent = ((second_avg - first_avg) / first_avg) * 100 if first_avg != 0 else 0
        
        if change_percent > 5:
            return "increasing"
        elif change_percent < -5:
            return "decreasing"
        else:
            return "stable"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'metric_name': self.metric_name,
            'metric_type': self.metric_type.value,
            'platform_id': self.platform_id,
            'data_points': [point.to_dict() for point in self.data_points],
            'latest_value': self.get_latest_value(),
            'average_24h': self.get_average(24),
            'trend_24h': self.get_trend(24)
        }


@dataclass
class PerformanceMetrics:
    """Platform performance metrics"""
    platform_id: str
    response_time_ms: float
    success_rate: float
    error_rate: float
    requests_per_minute: float
    data_transfer_mb: float
    uptime_percentage: float
    last_updated: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'platform_id': self.platform_id,
            'response_time_ms': self.response_time_ms,
            'success_rate': self.success_rate,
            'error_rate': self.error_rate,
            'requests_per_minute': self.requests_per_minute,
            'data_transfer_mb': self.data_transfer_mb,
            'uptime_percentage': self.uptime_percentage,
            'last_updated': self.last_updated.isoformat()
        }


@dataclass
class EngagementMetrics:
    """Content engagement metrics"""
    platform_id: str
    total_views: int
    total_likes: int
    total_shares: int
    total_comments: int
    engagement_rate: float
    reach: int
    impressions: int
    click_through_rate: float
    conversion_rate: float
    last_updated: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'platform_id': self.platform_id,
            'total_views': self.total_views,
            'total_likes': self.total_likes,
            'total_shares': self.total_shares,
            'total_comments': self.total_comments,
            'engagement_rate': self.engagement_rate,
            'reach': self.reach,
            'impressions': self.impressions,
            'click_through_rate': self.click_through_rate,
            'conversion_rate': self.conversion_rate,
            'last_updated': self.last_updated.isoformat()
        }


class MetricsCollector:
    """Collects and manages platform metrics"""
    
    def __init__(self, collection_interval: int = 60):
        """
        Initialize metrics collector
        
        Args:
            collection_interval: Collection interval in seconds
        """
        self.collection_interval = collection_interval
        self.metrics: Dict[str, Dict[str, MetricSeries]] = defaultdict(dict)
        self.performance_metrics: Dict[str, PerformanceMetrics] = {}
        self.engagement_metrics: Dict[str, EngagementMetrics] = {}
        self.collection_active = False
        self.collection_task: Optional[asyncio.Task] = None
        self.request_counters: Dict[str, deque] = defaultdict(lambda: deque(maxlen=60))
        
    def register_platform(self, platform: PlatformBase):
        """Register platform for metrics collection"""
        platform_id = platform.platform_id
        
        # Initialize performance metrics
        self.metrics[platform_id]['response_time'] = MetricSeries(
            'response_time', MetricType.PERFORMANCE, platform_id
        )
        self.metrics[platform_id]['success_rate'] = MetricSeries(
            'success_rate', MetricType.PERFORMANCE, platform_id
        )
        self.metrics[platform_id]['error_count'] = MetricSeries(
            'error_count', MetricType.TECHNICAL, platform_id
        )
        self.metrics[platform_id]['request_count'] = MetricSeries(
            'request_count', MetricType.TECHNICAL, platform_id
        )
        
        # Initialize engagement metrics
        self.metrics[platform_id]['views'] = MetricSeries(
            'views', MetricType.ENGAGEMENT, platform_id
        )
        self.metrics[platform_id]['likes'] = MetricSeries(
            'likes', MetricType.ENGAGEMENT, platform_id
        )
        self.metrics[platform_id]['shares'] = MetricSeries(
            'shares', MetricType.ENGAGEMENT, platform_id
        )
        self.metrics[platform_id]['comments'] = MetricSeries(
            'comments', MetricType.ENGAGEMENT, platform_id
        )
        
        logger.info(f"Registered platform {platform_id} for metrics collection")
    
    def record_request_metric(self, platform_id: str, response_time_ms: float, success: bool):
        """Record request metrics"""
        current_time = datetime.utcnow()
        
        # Record response time
        if platform_id in self.metrics and 'response_time' in self.metrics[platform_id]:
            self.metrics[platform_id]['response_time'].add_point(
                response_time_ms,
                {'success': success}
            )
        
        # Record success/error
        if platform_id in self.metrics:
            if success:
                if 'success_rate' in self.metrics[platform_id]:
                    self.metrics[platform_id]['success_rate'].add_point(1.0)
            else:
                if 'error_count' in self.metrics[platform_id]:
                    self.metrics[platform_id]['error_count'].add_point(1.0)
        
        # Update request counter
        self.request_counters[platform_id].append(current_time)
    
    def record_engagement_metric(self, platform_id: str, analytics: AnalyticsData):
        """Record engagement metrics"""
        if platform_id not in self.metrics:
            return
        
        metrics_map = {
            'views': analytics.views,
            'likes': analytics.likes,
            'shares': analytics.shares,
            'comments': analytics.comments
        }
        
        for metric_name, value in metrics_map.items():
            if metric_name in self.metrics[platform_id]:
                self.metrics[platform_id][metric_name].add_point(
                    value,
                    {
                        'content_id': analytics.content_id,
                        'engagement_rate': analytics.engagement_rate,
                        'reach': analytics.reach
                    }
                )
    
    async def collect_platform_metrics(self, platform: PlatformBase):
        """Collect comprehensive metrics for a platform"""
        platform_id = platform.platform_id
        
        try:
            # Collect performance metrics
            start_time = time.time()
            is_healthy = await platform.test_connection()
            response_time = (time.time() - start_time) * 1000
            
            self.record_request_metric(platform_id, response_time, is_healthy)
            
            # Calculate requests per minute
            now = datetime.utcnow()
            minute_ago = now - timedelta(minutes=1)
            recent_requests = [
                req_time for req_time in self.request_counters[platform_id]
                if req_time > minute_ago
            ]
            requests_per_minute = len(recent_requests)
            
            # Update performance metrics
            success_rate = self._calculate_success_rate(platform_id)
            error_rate = 1.0 - success_rate if success_rate is not None else 0.0
            
            self.performance_metrics[platform_id] = PerformanceMetrics(
                platform_id=platform_id,
                response_time_ms=response_time,
                success_rate=success_rate or 0.0,
                error_rate=error_rate,
                requests_per_minute=requests_per_minute,
                data_transfer_mb=0.0,  # Would need to track actual data transfer
                uptime_percentage=self._calculate_uptime(platform_id),
                last_updated=now
            )
            
            # Try to collect engagement metrics
            try:
                user_content = await platform.get_user_content()
                if user_content:
                    # Get analytics for recent content
                    for content in user_content[:5]:  # Sample recent content
                        content_id = content.get('id')
                        if content_id:
                            try:
                                end_date = datetime.utcnow()
                                start_date = end_date - timedelta(days=1)
                                analytics = await platform.get_analytics(content_id, start_date, end_date)
                                self.record_engagement_metric(platform_id, analytics)
                            except:
                                continue
            except:
                pass  # Engagement metrics are optional
            
        except Exception as e:
            logger.error(f"Error collecting metrics for {platform_id}: {e}")
            self.record_request_metric(platform_id, 0, False)
    
    def _calculate_success_rate(self, platform_id: str, hours: int = 1) -> Optional[float]:
        """Calculate success rate over time period"""
        if platform_id not in self.metrics:
            return None
        
        success_series = self.metrics[platform_id].get('success_rate')
        error_series = self.metrics[platform_id].get('error_count')
        
        if not success_series and not error_series:
            return None
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        successes = 0
        errors = 0
        
        if success_series:
            recent_successes = [
                point for point in success_series.data_points
                if point.timestamp > cutoff
            ]
            successes = len(recent_successes)
        
        if error_series:
            recent_errors = [
                point for point in error_series.data_points
                if point.timestamp > cutoff
            ]
            errors = len(recent_errors)
        
        total = successes + errors
        if total == 0:
            return None
        
        return successes / total
    
    def _calculate_uptime(self, platform_id: str, hours: int = 24) -> float:
        """Calculate uptime percentage"""
        success_rate = self._calculate_success_rate(platform_id, hours)
        return (success_rate * 100) if success_rate is not None else 100.0
    
    async def start_collection(self, platforms: List[PlatformBase]):
        """Start metrics collection"""
        if self.collection_active:
            logger.warning("Metrics collection already active")
            return
        
        # Register all platforms
        for platform in platforms:
            self.register_platform(platform)
        
        self.collection_active = True
        self.collection_task = asyncio.create_task(self._collection_loop(platforms))
        logger.info(f"Started metrics collection for {len(platforms)} platforms")
    
    async def stop_collection(self):
        """Stop metrics collection"""
        if not self.collection_active:
            return
        
        self.collection_active = False
        
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped metrics collection")
    
    async def _collection_loop(self, platforms: List[PlatformBase]):
        """Main collection loop"""
        try:
            while self.collection_active:
                logger.debug("Collecting platform metrics")
                
                # Collect metrics from all platforms concurrently
                tasks = [
                    self.collect_platform_metrics(platform)
                    for platform in platforms
                ]
                
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # Wait for next collection interval
                await asyncio.sleep(self.collection_interval)
                
        except asyncio.CancelledError:
            logger.info("Metrics collection loop cancelled")
        except Exception as e:
            logger.error(f"Metrics collection loop error: {e}")
            self.collection_active = False
    
    def get_platform_metrics(self, platform_id: str) -> Dict[str, Any]:
        """Get all metrics for a platform"""
        result = {
            'platform_id': platform_id,
            'performance': None,
            'engagement': None,
            'time_series': {}
        }
        
        # Add performance metrics
        if platform_id in self.performance_metrics:
            result['performance'] = self.performance_metrics[platform_id].to_dict()
        
        # Add engagement metrics
        if platform_id in self.engagement_metrics:
            result['engagement'] = self.engagement_metrics[platform_id].to_dict()
        
        # Add time series data
        if platform_id in self.metrics:
            for metric_name, series in self.metrics[platform_id].items():
                result['time_series'][metric_name] = series.to_dict()
        
        return result
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get metrics for all platforms"""
        return {
            platform_id: self.get_platform_metrics(platform_id)
            for platform_id in self.metrics.keys()
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary across all platforms"""
        total_platforms = len(self.metrics)
        
        if total_platforms == 0:
            return {'total_platforms': 0}
        
        # Calculate aggregate performance
        avg_response_time = 0
        avg_success_rate = 0
        total_requests = 0
        
        performance_count = 0
        for perf_metrics in self.performance_metrics.values():
            avg_response_time += perf_metrics.response_time_ms
            avg_success_rate += perf_metrics.success_rate
            total_requests += perf_metrics.requests_per_minute
            performance_count += 1
        
        if performance_count > 0:
            avg_response_time /= performance_count
            avg_success_rate /= performance_count
        
        # Count healthy platforms
        healthy_platforms = sum(
            1 for perf in self.performance_metrics.values()
            if perf.success_rate > 0.8 and perf.response_time_ms < 5000
        )
        
        return {
            'total_platforms': total_platforms,
            'healthy_platforms': healthy_platforms,
            'unhealthy_platforms': total_platforms - healthy_platforms,
            'average_response_time_ms': round(avg_response_time, 2),
            'average_success_rate': round(avg_success_rate * 100, 2),
            'total_requests_per_minute': total_requests,
            'collection_active': self.collection_active,
            'collection_interval_seconds': self.collection_interval
        }
    
    def export_metrics(self, platform_id: str = None, format: str = "json") -> Dict[str, Any]:
        """Export metrics data"""
        if platform_id:
            data = self.get_platform_metrics(platform_id)
        else:
            data = self.get_all_metrics()
        
        export_data = {
            'export_metadata': {
                'timestamp': datetime.utcnow().isoformat(),
                'format': format,
                'platform_filter': platform_id,
                'collection_interval': self.collection_interval
            },
            'metrics_data': data,
            'summary': self.get_metrics_summary()
        }
        
        return export_data
    
    def clear_metrics(self, platform_id: str = None):
        """Clear metrics data"""
        if platform_id:
            if platform_id in self.metrics:
                del self.metrics[platform_id]
            if platform_id in self.performance_metrics:
                del self.performance_metrics[platform_id]
            if platform_id in self.engagement_metrics:
                del self.engagement_metrics[platform_id]
            if platform_id in self.request_counters:
                del self.request_counters[platform_id]
            logger.info(f"Cleared metrics for {platform_id}")
        else:
            self.metrics.clear()
            self.performance_metrics.clear()
            self.engagement_metrics.clear()
            self.request_counters.clear()
            logger.info("Cleared all metrics data")


# Global metrics collector instance
_global_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance"""
    global _global_collector
    
    if _global_collector is None:
        _global_collector = MetricsCollector()
    
    return _global_collector


async def start_metrics_collection(platforms: List[PlatformBase]):
    """Start global metrics collection"""
    collector = get_metrics_collector()
    await collector.start_collection(platforms)


async def stop_metrics_collection():
    """Stop global metrics collection"""
    global _global_collector
    
    if _global_collector:
        await _global_collector.stop_collection()
