"""Analytics Cache for IA Influencer Agent Platform
High-performance caching for analytics data, metrics, and real-time statistics

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""
import asyncio
import logging
import json
import time
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
from collections import defaultdict, deque

from .redis_cache import RedisCache, RedisConfig
from .memory_cache import MemoryCache

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics tracked"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"

class TimeWindow(Enum):
    """Time windows for aggregation"""
    MINUTE = "1m"
    HOUR = "1h"
    DAY = "1d"
    WEEK = "1w"
    MONTH = "1M"

@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: float
    value: float
    tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}

@dataclass
class AnalyticsEvent:
    """Analytics event structure"""
    event_type: str
    user_id: Optional[str]
    session_id: Optional[str]
    tenant_id: Optional[str]
    timestamp: float
    properties: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

class AnalyticsCache:
    """
    Advanced analytics cache for tracking user behavior, performance metrics,
    and business intelligence data
    """
    
    def __init__(self,
                 redis_config: RedisConfig,
                 retention_days: int = 30,
                 aggregation_interval: int = 60):  # seconds
        
        self.retention_days = retention_days
        self.aggregation_interval = aggregation_interval
        
        # Initialize caches
        self.redis_cache = RedisCache(redis_config)
        self.memory_cache = MemoryCache(
            max_size=10000,
            default_ttl=300  # 5 minutes
        )
        
        # In-memory buffers for real-time data
        self._event_buffer = deque(maxlen=10000)
        self._metric_buffer: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._aggregation_cache: Dict[str, Dict[str, Any]] = {}
        
        # Cache key prefixes
        self.EVENT_PREFIX = "analytics:event"
        self.METRIC_PREFIX = "analytics:metric"
        self.AGGREGATION_PREFIX = "analytics:agg"
        self.USER_ANALYTICS_PREFIX = "analytics:user"
        self.CONTENT_ANALYTICS_PREFIX = "analytics:content"
        self.REALTIME_PREFIX = "analytics:realtime"
        
        # Statistics
        self._stats = {
            'events_tracked': 0,
            'metrics_recorded': 0,
            'aggregations_computed': 0,
            'queries_served': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        logger.info("AnalyticsCache initialized")
    
    async def initialize(self):
        """Initialize cache connections"""
        await self.redis_cache.connect()
    
    async def track_event(self,
                         event_type: str,
                         user_id: Optional[str] = None,
                         session_id: Optional[str] = None,
                         tenant_id: Optional[str] = None,
                         properties: Optional[Dict[str, Any]] = None,
                         ip_address: Optional[str] = None,
                         user_agent: Optional[str] = None) -> bool:
        """Track analytics event"""
        
        event = AnalyticsEvent(
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            tenant_id=tenant_id,
            timestamp=time.time(),
            properties=properties or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        try:
            # Add to memory buffer for real-time processing
            self._event_buffer.append(event)
            
            # Store in Redis with TTL
            event_key = f"{self.EVENT_PREFIX}:{event_type}:{int(event.timestamp)}"
            await self.redis_cache.set(
                event_key,
                json.dumps(event.to_dict()),
                ttl=self.retention_days * 86400
            )
            
            # Update real-time counters
            await self._update_realtime_counters(event)
            
            # Update user-specific analytics
            if user_id:
                await self._update_user_analytics(user_id, event)
            
            # Update content-specific analytics if applicable
            content_id = properties.get('content_id') if properties else None
            if content_id:
                await self._update_content_analytics(content_id, event)
            
            self._stats['events_tracked'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Failed to track event {event_type}: {e}")
            return False
    
    async def record_metric(self,
                          metric_name: str,
                          value: float,
                          metric_type: MetricType = MetricType.GAUGE,
                          tags: Optional[Dict[str, str]] = None,
                          timestamp: Optional[float] = None) -> bool:
        """Record performance metric"""
        
        if timestamp is None:
            timestamp = time.time()
        
        metric_point = MetricPoint(
            timestamp=timestamp,
            value=value,
            tags=tags or {}
        )
        
        try:
            # Add to memory buffer
            self._metric_buffer[metric_name].append(metric_point)
            
            # Create metric key with timestamp bucket
            time_bucket = int(timestamp // self.aggregation_interval) * self.aggregation_interval
            metric_key = f"{self.METRIC_PREFIX}:{metric_name}:{time_bucket}"
            
            # Get existing metrics for this bucket
            existing_data = await self.redis_cache.get(metric_key)
            if existing_data:
                bucket_data = json.loads(existing_data)
            else:
                bucket_data = {
                    'metric_name': metric_name,
                    'metric_type': metric_type.value,
                    'time_bucket': time_bucket,
                    'points': [],
                    'aggregations': {}
                }
            
            # Add new point
            bucket_data['points'].append({
                'timestamp': timestamp,
                'value': value,
                'tags': metric_point.tags
            })
            
            # Compute aggregations for this bucket
            values = [p['value'] for p in bucket_data['points']]
            bucket_data['aggregations'] = {
                'count': len(values),
                'sum': sum(values),
                'avg': statistics.mean(values),
                'min': min(values),
                'max': max(values),
                'last': values[-1]
            }
            
            if len(values) > 1:
                bucket_data['aggregations']['stddev'] = statistics.stdev(values)
            
            # Store updated bucket
            await self.redis_cache.set(
                metric_key,
                json.dumps(bucket_data),
                ttl=self.retention_days * 86400
            )
            
            self._stats['metrics_recorded'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Failed to record metric {metric_name}: {e}")
            return False
    
    async def get_events(self,
                        event_type: Optional[str] = None,
                        user_id: Optional[str] = None,
                        start_time: Optional[float] = None,
                        end_time: Optional[float] = None,
                        limit: int = 1000) -> List[AnalyticsEvent]:
        """Query analytics events"""
        
        try:
            # Build search pattern
            if event_type:
                pattern = f"{self.EVENT_PREFIX}:{event_type}:*"
            else:
                pattern = f"{self.EVENT_PREFIX}:*"
            
            # Get matching keys
            keys = await self.redis_cache.keys(pattern)
            
            # Filter by time range if specified
            if start_time or end_time:
                filtered_keys = []
                for key in keys:
                    timestamp_str = key.split(':')[-1]
                    try:
                        timestamp = float(timestamp_str)
                        if start_time and timestamp < start_time:
                            continue
                        if end_time and timestamp > end_time:
                            continue
                        filtered_keys.append(key)
                    except ValueError:
                        continue
                keys = filtered_keys
            
            # Sort by timestamp (most recent first)
            keys.sort(key=lambda k: float(k.split(':')[-1]), reverse=True)
            
            # Limit results
            keys = keys[:limit]
            
            # Fetch events
            events = []
            for key in keys:
                event_data = await self.redis_cache.get(key)
                if event_data:
                    event_dict = json.loads(event_data)
                    event = AnalyticsEvent(**event_dict)
                    
                    # Filter by user_id if specified
                    if user_id and event.user_id != user_id:
                        continue
                    
                    events.append(event)
            
            self._stats['queries_served'] += 1
            self._stats['cache_hits'] += 1
            return events
            
        except Exception as e:
            logger.error(f"Failed to get events: {e}")
            self._stats['cache_misses'] += 1
            return []
    
    async def get_metric_data(self,
                            metric_name: str,
                            start_time: Optional[float] = None,
                            end_time: Optional[float] = None,
                            aggregation: str = "avg") -> List[Tuple[float, float]]:
        """Get metric data points"""
        
        try:
            # Build time range
            if not start_time:
                start_time = time.time() - 86400  # Last 24 hours
            if not end_time:
                end_time = time.time()
            
            # Get time buckets in range
            start_bucket = int(start_time // self.aggregation_interval) * self.aggregation_interval
            end_bucket = int(end_time // self.aggregation_interval) * self.aggregation_interval
            
            data_points = []
            current_bucket = start_bucket
            
            while current_bucket <= end_bucket:
                metric_key = f"{self.METRIC_PREFIX}:{metric_name}:{current_bucket}"
                bucket_data = await self.redis_cache.get(metric_key)
                
                if bucket_data:
                    bucket_dict = json.loads(bucket_data)
                    aggregations = bucket_dict.get('aggregations', {})
                    
                    if aggregation in aggregations:
                        data_points.append((current_bucket, aggregations[aggregation]))
                
                current_bucket += self.aggregation_interval
            
            self._stats['queries_served'] += 1
            self._stats['cache_hits'] += 1
            return data_points
            
        except Exception as e:
            logger.error(f"Failed to get metric data for {metric_name}: {e}")
            self._stats['cache_misses'] += 1
            return []
    
    async def get_realtime_stats(self, time_window: int = 300) -> Dict[str, Any]:
        """Get real-time statistics for last N seconds"""
        
        cache_key = f"realtime_stats_{time_window}"
        cached_stats = self.memory_cache.get(cache_key)
        
        if cached_stats:
            self._stats['cache_hits'] += 1
            return cached_stats
        
        try:
            current_time = time.time()
            start_time = current_time - time_window
            
            # Count events by type in time window
            event_counts = defaultdict(int)
            user_activity = set()
            
            # Process memory buffer first (most recent data)
            for event in self._event_buffer:
                if event.timestamp >= start_time:
                    event_counts[event.event_type] += 1
                    if event.user_id:
                        user_activity.add(event.user_id)
            
            # Get additional data from Redis for completeness
            realtime_key = f"{self.REALTIME_PREFIX}:*"
            realtime_keys = await self.redis_cache.keys(realtime_key)
            
            for key in realtime_keys:
                if 'counters' in key:
                    counter_data = await self.redis_cache.get(key)
                    if counter_data:
                        counters = json.loads(counter_data)
                        for event_type, count in counters.items():
                            event_counts[event_type] += count
            
            stats = {
                'time_window_seconds': time_window,
                'timestamp': current_time,
                'event_counts': dict(event_counts),
                'total_events': sum(event_counts.values()),
                'active_users': len(user_activity),
                'events_per_second': sum(event_counts.values()) / time_window if time_window > 0 else 0
            }
            
            # Cache for 10 seconds
            self.memory_cache.set(cache_key, stats, ttl=10)
            
            self._stats['queries_served'] += 1
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get realtime stats: {e}")
            return {}
    
    async def get_user_analytics(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get analytics for specific user"""
        
        cache_key = f"user_analytics_{user_id}_{days}"
        cached_analytics = self.memory_cache.get(cache_key)
        
        if cached_analytics:
            self._stats['cache_hits'] += 1
            return cached_analytics
        
        try:
            user_key = f"{self.USER_ANALYTICS_PREFIX}:{user_id}"
            user_data = await self.redis_cache.get(user_key)
            
            if user_data:
                analytics = json.loads(user_data)
                
                # Calculate additional metrics
                start_time = time.time() - (days * 86400)
                recent_events = await self.get_events(
                    user_id=user_id,
                    start_time=start_time,
                    limit=10000
                )
                
                # Aggregate recent activity
                event_counts = defaultdict(int)
                daily_activity = defaultdict(int)
                
                for event in recent_events:
                    event_counts[event.event_type] += 1
                    day_key = datetime.fromtimestamp(event.timestamp).strftime('%Y-%m-%d')
                    daily_activity[day_key] += 1
                
                analytics.update({
                    'recent_event_counts': dict(event_counts),
                    'daily_activity': dict(daily_activity),
                    'total_recent_events': len(recent_events),
                    'avg_daily_activity': sum(daily_activity.values()) / days if days > 0 else 0
                })
                
                # Cache for 5 minutes
                self.memory_cache.set(cache_key, analytics, ttl=300)
                
                self._stats['cache_hits'] += 1
                return analytics
            
            self._stats['cache_misses'] += 1
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get user analytics for {user_id}: {e}")
            return {}
    
    async def get_content_analytics(self, content_id: str) -> Dict[str, Any]:
        """Get analytics for specific content"""
        
        cache_key = f"content_analytics_{content_id}"
        cached_analytics = self.memory_cache.get(cache_key)
        
        if cached_analytics:
            self._stats['cache_hits'] += 1
            return cached_analytics
        
        try:
            content_key = f"{self.CONTENT_ANALYTICS_PREFIX}:{content_id}"
            content_data = await self.redis_cache.get(content_key)
            
            if content_data:
                analytics = json.loads(content_data)
                
                # Cache for 5 minutes
                self.memory_cache.set(cache_key, analytics, ttl=300)
                
                self._stats['cache_hits'] += 1
                return analytics
            
            self._stats['cache_misses'] += 1
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get content analytics for {content_id}: {e}")
            return {}
    
    async def _update_realtime_counters(self, event: AnalyticsEvent):
        """Update real-time event counters"""
        try:
            # Update minute-level counters
            minute_bucket = int(event.timestamp // 60) * 60
            counter_key = f"{self.REALTIME_PREFIX}:counters:{minute_bucket}"
            
            counter_data = await self.redis_cache.get(counter_key)
            counters = json.loads(counter_data) if counter_data else {}
            
            counters[event.event_type] = counters.get(event.event_type, 0) + 1
            
            await self.redis_cache.set(counter_key, json.dumps(counters), ttl=3600)  # 1 hour
            
        except Exception as e:
            logger.error(f"Failed to update realtime counters: {e}")
    
    async def _update_user_analytics(self, user_id: str, event: AnalyticsEvent):
        """Update user-specific analytics"""
        try:
            user_key = f"{self.USER_ANALYTICS_PREFIX}:{user_id}"
            user_data = await self.redis_cache.get(user_key)
            
            analytics = json.loads(user_data) if user_data else {
                'user_id': user_id,
                'first_seen': event.timestamp,
                'event_counts': {},
                'session_counts': {},
                'total_events': 0
            }
            
            # Update counters
            analytics['last_seen'] = event.timestamp
            analytics['event_counts'][event.event_type] = analytics['event_counts'].get(event.event_type, 0) + 1
            analytics['total_events'] += 1
            
            if event.session_id:
                analytics['session_counts'][event.session_id] = analytics['session_counts'].get(event.session_id, 0) + 1
            
            await self.redis_cache.set(
                user_key,
                json.dumps(analytics),
                ttl=self.retention_days * 86400
            )
            
        except Exception as e:
            logger.error(f"Failed to update user analytics: {e}")
    
    async def _update_content_analytics(self, content_id: str, event: AnalyticsEvent):
        """Update content-specific analytics"""
        try:
            content_key = f"{self.CONTENT_ANALYTICS_PREFIX}:{content_id}"
            content_data = await self.redis_cache.get(content_key)
            
            analytics = json.loads(content_data) if content_data else {
                'content_id': content_id,
                'first_interaction': event.timestamp,
                'interaction_counts': {},
                'unique_users': set(),
                'total_interactions': 0
            }
            
            # Update counters
            analytics['last_interaction'] = event.timestamp
            analytics['interaction_counts'][event.event_type] = analytics['interaction_counts'].get(event.event_type, 0) + 1
            analytics['total_interactions'] += 1
            
            if event.user_id:
                if isinstance(analytics['unique_users'], set):
                    analytics['unique_users'].add(event.user_id)
                else:
                    # Convert list back to set for JSON serialization compatibility
                    unique_users = set(analytics['unique_users'])
                    unique_users.add(event.user_id)
                    analytics['unique_users'] = list(unique_users)
            
            # Convert set to list for JSON serialization
            if isinstance(analytics['unique_users'], set):
                analytics['unique_users'] = list(analytics['unique_users'])
            
            await self.redis_cache.set(
                content_key,
                json.dumps(analytics),
                ttl=self.retention_days * 86400
            )
            
        except Exception as e:
            logger.error(f"Failed to update content analytics: {e}")
    
    async def aggregate_metrics(self, time_window: TimeWindow) -> Dict[str, Any]:
        """Aggregate metrics for specified time window"""
        try:
            current_time = time.time()
            
            # Calculate time window boundaries
            if time_window == TimeWindow.MINUTE:
                window_seconds = 60
            elif time_window == TimeWindow.HOUR:
                window_seconds = 3600
            elif time_window == TimeWindow.DAY:
                window_seconds = 86400
            elif time_window == TimeWindow.WEEK:
                window_seconds = 604800
            elif time_window == TimeWindow.MONTH:
                window_seconds = 2592000
            else:
                window_seconds = 3600  # Default to hour
            
            start_time = current_time - window_seconds
            
            # Get all metric keys in time range
            pattern = f"{self.METRIC_PREFIX}:*"
            metric_keys = await self.redis_cache.keys(pattern)
            
            aggregations = {}
            
            for key in metric_keys:
                parts = key.split(':')
                if len(parts) >= 4:
                    metric_name = parts[2]
                    time_bucket = float(parts[3])
                    
                    if time_bucket >= start_time:
                        if metric_name not in aggregations:
                            aggregations[metric_name] = {
                                'count': 0,
                                'sum': 0,
                                'values': []
                            }
                        
                        bucket_data = await self.redis_cache.get(key)
                        if bucket_data:
                            bucket_dict = json.loads(bucket_data)
                            bucket_agg = bucket_dict.get('aggregations', {})
                            
                            aggregations[metric_name]['count'] += bucket_agg.get('count', 0)
                            aggregations[metric_name]['sum'] += bucket_agg.get('sum', 0)
                            
                            # Collect values for percentile calculations
                            points = bucket_dict.get('points', [])
                            for point in points:
                                aggregations[metric_name]['values'].append(point['value'])
            
            # Calculate final aggregations
            final_aggregations = {}
            for metric_name, data in aggregations.items():
                if data['count'] > 0:
                    values = data['values']
                    final_aggregations[metric_name] = {
                        'count': data['count'],
                        'sum': data['sum'],
                        'avg': data['sum'] / data['count'],
                        'min': min(values) if values else 0,
                        'max': max(values) if values else 0
                    }
                    
                    if len(values) > 1:
                        values.sort()
                        final_aggregations[metric_name]['p50'] = values[len(values) // 2]
                        final_aggregations[metric_name]['p95'] = values[int(len(values) * 0.95)]
                        final_aggregations[metric_name]['p99'] = values[int(len(values) * 0.99)]
            
            self._stats['aggregations_computed'] += 1
            return final_aggregations
            
        except Exception as e:
            logger.error(f"Failed to aggregate metrics: {e}")
            return {}
    
    async def cleanup_old_data(self):
        """Clean up old analytics data beyond retention period"""
        try:
            cutoff_time = time.time() - (self.retention_days * 86400)
            
            # Clean up old events
            event_keys = await self.redis_cache.keys(f"{self.EVENT_PREFIX}:*")
            deleted_count = 0
            
            for key in event_keys:
                timestamp_str = key.split(':')[-1]
                try:
                    timestamp = float(timestamp_str)
                    if timestamp < cutoff_time:
                        await self.redis_cache.delete(key)
                        deleted_count += 1
                except ValueError:
                    continue
            
            # Clean up old metrics
            metric_keys = await self.redis_cache.keys(f"{self.METRIC_PREFIX}:*")
            
            for key in metric_keys:
                parts = key.split(':')
                if len(parts) >= 4:
                    time_bucket = float(parts[3])
                    if time_bucket < cutoff_time:
                        await self.redis_cache.delete(key)
                        deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old analytics entries")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        redis_stats = await self.redis_cache.get_stats()
        memory_stats = self.memory_cache.get_stats()
        
        return {
            'analytics_stats': self._stats,
            'redis_stats': redis_stats,
            'memory_stats': memory_stats,
            'retention_days': self.retention_days,
            'aggregation_interval': self.aggregation_interval,
            'event_buffer_size': len(self._event_buffer),
            'metric_buffer_count': len(self._metric_buffer)
        }
    
    async def close(self):
        """Close cache connections"""
        await self.redis_cache.close()
        self.memory_cache.close()

class MetricsCache(AnalyticsCache):
    """
    Simplified metrics-only cache for performance monitoring
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Predefined metric names for common use cases
        self.RESPONSE_TIME = "http_response_time"
        self.REQUEST_COUNT = "http_request_count"
        self.ERROR_RATE = "error_rate"
        self.CPU_USAGE = "cpu_usage"
        self.MEMORY_USAGE = "memory_usage"
        self.CACHE_HIT_RATE = "cache_hit_rate"
        self.ACTIVE_USERS = "active_users"
        self.CONTENT_UPLOADS = "content_uploads"
        self.FINGERPRINT_MATCHES = "fingerprint_matches"
    
    async def record_response_time(self, endpoint: str, response_time: float, status_code: int):
        """Record HTTP response time"""
        await self.record_metric(
            self.RESPONSE_TIME,
            response_time,
            MetricType.TIMER,
            tags={'endpoint': endpoint, 'status_code': str(status_code)}
        )
    
    async def increment_counter(self, metric_name: str, tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        await self.record_metric(
            metric_name,
            1,
            MetricType.COUNTER,
            tags=tags
        )
    
    async def set_gauge(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Set a gauge metric value"""
        await self.record_metric(
            metric_name,
            value,
            MetricType.GAUGE,
            tags=tags
        )
    
    async def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get key metrics for dashboard display"""
        try:
            current_time = time.time()
            last_hour = current_time - 3600
            
            # Get recent response times
            response_times = await self.get_metric_data(
                self.RESPONSE_TIME,
                start_time=last_hour,
                aggregation="avg"
            )
            
            # Get request counts
            request_counts = await self.get_metric_data(
                self.REQUEST_COUNT,
                start_time=last_hour,
                aggregation="sum"
            )
            
            # Get error rates
            error_rates = await self.get_metric_data(
                self.ERROR_RATE,
                start_time=last_hour,
                aggregation="avg"
            )
            
            # Calculate summary statistics
            avg_response_time = statistics.mean([point[1] for point in response_times]) if response_times else 0
            total_requests = sum([point[1] for point in request_counts]) if request_counts else 0
            avg_error_rate = statistics.mean([point[1] for point in error_rates]) if error_rates else 0
            
            return {
                'avg_response_time_ms': avg_response_time,
                'total_requests_last_hour': total_requests,
                'avg_error_rate_percent': avg_error_rate * 100,
                'requests_per_minute': total_requests / 60 if total_requests > 0 else 0,
                'response_time_series': response_times,
                'request_count_series': request_counts,
                'error_rate_series': error_rates
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard metrics: {e}")
            return {}
