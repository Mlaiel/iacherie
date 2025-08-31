"""Webhook Analytics - Enterprise Analytics and Monitoring System

Industrial-grade webhook analytics engine for comprehensive monitoring,
metrics collection, and business intelligence across multi-platform integrations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization without explicit written 
permission from Fahed Mlaiel <mlaiel@live.de> is strictly prohibited.
"""
import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque

import aioredis
import numpy as np
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager
try:
    from core.exceptions import AnalyticsError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    AnalyticsError = globals().get('AnalyticsError', Exception)
from ...utils.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)

Base = declarative_base()

class WebhookAnalyticsModel(Base):
    """Database model for webhook analytics events"""    __tablename__ = "webhook_analytics_events"
    
    event_id = Column(String, primary_key=True)
    endpoint_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    response_time_ms = Column(Float)
    status_code = Column(Integer)
    success = Column(Boolean)
    payload_size_bytes = Column(Integer)
    error_message = Column(Text)
    processing_duration_ms = Column(Float)
    retry_count = Column(Integer, default=0)
    metadata = Column(JSON)

class WebhookMetricsModel(Base):
    """Database model for aggregated webhook metrics"""    __tablename__ = "webhook_analytics_metrics"
    
    metric_id = Column(String, primary_key=True)
    endpoint_id = Column(String)
    user_id = Column(String)
    platform = Column(String)
    metric_type = Column(String, nullable=False)
    time_window = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    avg_response_time = Column(Float, default=0.0)
    min_response_time = Column(Float)
    max_response_time = Column(Float)
    total_payload_bytes = Column(Integer, default=0)
    error_rate = Column(Float, default=0.0)
    throughput_per_second = Column(Float, default=0.0)
    metadata = Column(JSON)

class MetricType(Enum):
    """Types of webhook metrics"""    REQUESTS = "requests"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    PAYLOAD_SIZE = "payload_size"
    PLATFORM_DISTRIBUTION = "platform_distribution"
    EVENT_TYPE_DISTRIBUTION = "event_type_distribution"
    USER_ACTIVITY = "user_activity"

class TimeWindow(Enum):
    """Time windows for metrics aggregation"""    MINUTE = "1m"
    HOUR = "1h"
    DAY = "1d"
    WEEK = "1w"
    MONTH = "1M"

@dataclass
class WebhookEvent:
    """Webhook event for analytics"""    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    endpoint_id: str = None
    user_id: str = None
    platform: str = None
    event_type: str = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    response_time_ms: float = 0.0
    status_code: int = None
    success: bool = False
    payload_size_bytes: int = 0
    error_message: Optional[str] = None
    processing_duration_ms: float = 0.0
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetricSnapshot:
    """Snapshot of webhook metrics"""    metric_type: MetricType
    time_window: TimeWindow
    timestamp: datetime
    count: int = 0
    success_count: int = 0
    failure_count: int = 0
    success_rate: float = 0.0
    error_rate: float = 0.0
    avg_response_time: float = 0.0
    min_response_time: Optional[float] = None
    max_response_time: Optional[float] = None
    throughput_per_second: float = 0.0
    total_payload_bytes: int = 0
    avg_payload_size: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalyticsQuery:
    """Query configuration for analytics data"""    start_time: datetime
    end_time: datetime
    endpoint_ids: List[str] = field(default_factory=list)
    user_ids: List[str] = field(default_factory=list)
    platforms: List[str] = field(default_factory=list)
    event_types: List[str] = field(default_factory=list)
    metric_types: List[MetricType] = field(default_factory=list)
    time_window: TimeWindow = TimeWindow.HOUR
    limit: int = 1000
    include_errors_only: bool = False
    include_success_only: bool = False

class WebhookAnalytics:
    """    Industrial-grade webhook analytics and monitoring system
    
    Provides comprehensive analytics, metrics collection, and business intelligence
    for webhook operations across multi-platform integrations with real-time
    monitoring and alerting capabilities.
    """    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.db_session = get_db_session()
        self.performance_monitor = PerformanceMonitor("webhook_analytics")
        
        # Configuration
        self.metrics_retention_days = self.config.get('metrics_retention_days', 90)
        self.real_time_window_seconds = self.config.get('real_time_window_seconds', 300)
        self.batch_size = self.config.get('batch_size', 1000)
        self.aggregation_interval_seconds = self.config.get('aggregation_interval_seconds', 60)
        self.alert_thresholds = self.config.get('alert_thresholds', {
            'error_rate': 0.05,  # 5%
            'response_time_p95': 5000,  # 5 seconds
            'throughput_drop': 0.3  # 30% drop
        })
        
        # Internal state
        self._redis_client = None
        self._event_buffer: deque = deque(maxlen=10000)
        self._metric_cache: Dict[str, Dict[str, Any]] = {}
        self._real_time_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._aggregation_tasks: Set[asyncio.Task] = set()
        self._last_aggregation_time = {}
        
        # Performance tracking
        self._request_counts = defaultdict(int)
        self._response_times = defaultdict(list)
        self._error_counts = defaultdict(int)
        self._throughput_tracker = defaultdict(deque)
        
        logger.info("WebhookAnalytics initialized")

    async def initialize(self) -> None:
        """Initialize webhook analytics with required services"""        try:
            # Initialize Redis connection
            self._redis_client = await aioredis.from_url(
                self.config.get('redis_url', 'redis://localhost:6379'),
                decode_responses=True
            )
            
            # Start aggregation tasks
            await self._start_aggregation_tasks()
            
            # Initialize metric cache
            await self._initialize_metric_cache()
            
            logger.info("WebhookAnalytics initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize WebhookAnalytics: {e}")
            raise AnalyticsError(f"Initialization failed: {str(e)}")

    async def record_webhook_event(
        self,
        endpoint_id: str,
        user_id: str,
        platform: str,
        event_type: str,
        success: bool,
        response_time_ms: float,
        status_code: int = None,
        payload_size_bytes: int = 0,
        error_message: str = None,
        processing_duration_ms: float = None,
        retry_count: int = 0,
        metadata: Dict[str, Any] = None
    ) -> str:
        """        Record webhook event for analytics
        
        Args:
            endpoint_id: Webhook endpoint identifier
            user_id: User identifier
            platform: Platform name
            event_type: Type of webhook event
            success: Whether the webhook was successful
            response_time_ms: Response time in milliseconds
            status_code: HTTP status code
            payload_size_bytes: Size of payload in bytes
            error_message: Error message if failed
            processing_duration_ms: Processing duration
            retry_count: Number of retries
            metadata: Additional metadata
            
        Returns:
            Event ID
        """        try:
            # Create event
            event = WebhookEvent(
                endpoint_id=endpoint_id,
                user_id=user_id,
                platform=platform,
                event_type=event_type,
                success=success,
                response_time_ms=response_time_ms,
                status_code=status_code,
                payload_size_bytes=payload_size_bytes,
                error_message=error_message,
                processing_duration_ms=processing_duration_ms or response_time_ms,
                retry_count=retry_count,
                metadata=metadata or {}
            )
            
            # Add to buffer
            self._event_buffer.append(event)
            
            # Update real-time metrics
            await self._update_real_time_metrics(event)
            
            # Store in database (async)
            asyncio.create_task(self._store_event_async(event))
            
            # Update Redis cache
            await self._update_redis_metrics(event)
            
            logger.debug(f"Webhook event recorded: {event.event_id}")
            return event.event_id
            
        except Exception as e:
            logger.error(f"Failed to record webhook event: {e}")
            raise AnalyticsError(f"Event recording failed: {str(e)}")

    async def get_metrics(
        self,
        query: AnalyticsQuery
    ) -> Dict[str, Any]:
        """        Get webhook metrics based on query parameters
        
        Args:
            query: Analytics query configuration
            
        Returns:
            Metrics data
        """        try:
            # Generate cache key
            cache_key = self._generate_metrics_cache_key(query)
            
            # Check cache first
            if cache_key in self._metric_cache:
                cached_result = self._metric_cache[cache_key]
                if (datetime.now(timezone.utc) - cached_result['timestamp']).seconds < 300:  # 5 min cache
                    logger.debug(f"Using cached metrics for query: {cache_key}")
                    return cached_result['data']
            
            # Query database
            metrics_data = await self._query_metrics_from_db(query)
            
            # Aggregate and process metrics
            processed_metrics = await self._process_metrics_data(metrics_data, query)
            
            # Calculate additional insights
            insights = await self._calculate_insights(processed_metrics, query)
            
            # Prepare result
            result = {
                'query': {
                    'start_time': query.start_time.isoformat(),
                    'end_time': query.end_time.isoformat(),
                    'time_window': query.time_window.value,
                    'metric_types': [mt.value for mt in query.metric_types] if query.metric_types else [],
                    'platforms': query.platforms,
                    'event_types': query.event_types
                },
                'metrics': processed_metrics,
                'insights': insights,
                'metadata': {
                    'query_time': datetime.now(timezone.utc).isoformat(),
                    'data_points': len(metrics_data),
                    'cache_hit': False
                }
            }
            
            # Cache result
            self._metric_cache[cache_key] = {
                'data': result,
                'timestamp': datetime.now(timezone.utc)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            raise AnalyticsError(f"Metrics query failed: {str(e)}")

    async def get_real_time_metrics(
        self,
        endpoint_id: str = None,
        user_id: str = None,
        platform: str = None,
        time_window_minutes: int = 5
    ) -> Dict[str, Any]:
        """        Get real-time webhook metrics
        
        Args:
            endpoint_id: Optional endpoint filter
            user_id: Optional user filter
            platform: Optional platform filter
            time_window_minutes: Time window for metrics
            
        Returns:
            Real-time metrics
        """        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=time_window_minutes)
            
            # Filter events from buffer
            recent_events = []
            for event in self._event_buffer:
                if event.timestamp >= cutoff_time:
                    # Apply filters
                    if endpoint_id and event.endpoint_id != endpoint_id:
                        continue
                    if user_id and event.user_id != user_id:
                        continue
                    if platform and event.platform != platform:
                        continue
                    
                    recent_events.append(event)
            
            # Calculate real-time metrics
            total_requests = len(recent_events)
            successful_requests = len([e for e in recent_events if e.success])
            failed_requests = total_requests - successful_requests
            
            success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
            error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
            
            response_times = [e.response_time_ms for e in recent_events if e.response_time_ms]
            avg_response_time = np.mean(response_times) if response_times else 0
            p95_response_time = np.percentile(response_times, 95) if response_times else 0
            
            # Platform distribution
            platform_counts = defaultdict(int)
            for event in recent_events:
                platform_counts[event.platform] += 1
            
            # Event type distribution
            event_type_counts = defaultdict(int)
            for event in recent_events:
                event_type_counts[event.event_type] += 1
            
            # Throughput (requests per minute)
            throughput = total_requests / time_window_minutes if time_window_minutes > 0 else 0
            
            return {
                'time_window_minutes': time_window_minutes,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'total_requests': total_requests,
                'successful_requests': successful_requests,
                'failed_requests': failed_requests,
                'success_rate_percent': round(success_rate, 2),
                'error_rate_percent': round(error_rate, 2),
                'avg_response_time_ms': round(avg_response_time, 2),
                'p95_response_time_ms': round(p95_response_time, 2),
                'throughput_per_minute': round(throughput, 2),
                'platform_distribution': dict(platform_counts),
                'event_type_distribution': dict(event_type_counts),
                'alerts': await self._check_real_time_alerts(recent_events)
            }
            
        except Exception as e:
            logger.error(f"Failed to get real-time metrics: {e}")
            raise AnalyticsError(f"Real-time metrics failed: {str(e)}")

    async def get_endpoint_analytics(
        self,
        endpoint_id: str,
        time_range_hours: int = 24
    ) -> Dict[str, Any]:
        """        Get detailed analytics for specific endpoint
        
        Args:
            endpoint_id: Endpoint identifier
            time_range_hours: Time range for analytics
            
        Returns:
            Endpoint analytics
        """        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=time_range_hours)
            
            query = AnalyticsQuery(
                start_time=start_time,
                end_time=end_time,
                endpoint_ids=[endpoint_id],
                time_window=TimeWindow.HOUR
            )
            
            # Get basic metrics
            metrics = await self.get_metrics(query)
            
            # Get endpoint-specific insights
            endpoint_insights = await self._calculate_endpoint_insights(endpoint_id, start_time, end_time)
            
            # Get error analysis
            error_analysis = await self._analyze_endpoint_errors(endpoint_id, start_time, end_time)
            
            # Get performance trends
            performance_trends = await self._calculate_performance_trends(endpoint_id, start_time, end_time)
            
            return {
                'endpoint_id': endpoint_id,
                'time_range_hours': time_range_hours,
                'metrics': metrics,
                'insights': endpoint_insights,
                'error_analysis': error_analysis,
                'performance_trends': performance_trends,
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get endpoint analytics: {e}")
            raise AnalyticsError(f"Endpoint analytics failed: {str(e)}")

    async def get_user_analytics(
        self,
        user_id: str,
        time_range_days: int = 7
    ) -> Dict[str, Any]:
        """        Get analytics for specific user
        
        Args:
            user_id: User identifier
            time_range_days: Time range for analytics
            
        Returns:
            User analytics
        """        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(days=time_range_days)
            
            query = AnalyticsQuery(
                start_time=start_time,
                end_time=end_time,
                user_ids=[user_id],
                time_window=TimeWindow.DAY
            )
            
            # Get user metrics
            metrics = await self.get_metrics(query)
            
            # Get user-specific insights
            user_insights = await self._calculate_user_insights(user_id, start_time, end_time)
            
            # Get platform usage
            platform_usage = await self._calculate_platform_usage(user_id, start_time, end_time)
            
            return {
                'user_id': user_id,
                'time_range_days': time_range_days,
                'metrics': metrics,
                'insights': user_insights,
                'platform_usage': platform_usage,
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get user analytics: {e}")
            raise AnalyticsError(f"User analytics failed: {str(e)}")

    async def get_platform_analytics(
        self,
        platform: str,
        time_range_days: int = 30
    ) -> Dict[str, Any]:
        """        Get analytics for specific platform
        
        Args:
            platform: Platform name
            time_range_days: Time range for analytics
            
        Returns:
            Platform analytics
        """        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(days=time_range_days)
            
            query = AnalyticsQuery(
                start_time=start_time,
                end_time=end_time,
                platforms=[platform],
                time_window=TimeWindow.DAY
            )
            
            # Get platform metrics
            metrics = await self.get_metrics(query)
            
            # Get platform-specific insights
            platform_insights = await self._calculate_platform_insights(platform, start_time, end_time)
            
            return {
                'platform': platform,
                'time_range_days': time_range_days,
                'metrics': metrics,
                'insights': platform_insights,
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get platform analytics: {e}")
            raise AnalyticsError(f"Platform analytics failed: {str(e)}")

    async def generate_analytics_report(
        self,
        report_type: str = "comprehensive",
        time_range_days: int = 30,
        user_id: str = None,
        platform: str = None
    ) -> Dict[str, Any]:
        """        Generate comprehensive analytics report
        
        Args:
            report_type: Type of report (comprehensive, summary, detailed)
            time_range_days: Time range for report
            user_id: Optional user filter
            platform: Optional platform filter
            
        Returns:
            Analytics report
        """        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(days=time_range_days)
            
            # Base query
            query = AnalyticsQuery(
                start_time=start_time,
                end_time=end_time,
                time_window=TimeWindow.DAY
            )
            
            if user_id:
                query.user_ids = [user_id]
            if platform:
                query.platforms = [platform]
            
            # Get comprehensive metrics
            metrics = await self.get_metrics(query)
            
            # Calculate report sections based on type
            report_sections = {}
            
            if report_type in ["comprehensive", "detailed"]:
                # Executive summary
                report_sections['executive_summary'] = await self._generate_executive_summary(metrics, query)
                
                # Performance analysis
                report_sections['performance_analysis'] = await self._generate_performance_analysis(metrics, query)
                
                # Error analysis
                report_sections['error_analysis'] = await self._generate_error_analysis(metrics, query)
                
                # Trend analysis
                report_sections['trend_analysis'] = await self._generate_trend_analysis(metrics, query)
                
                # Platform insights
                report_sections['platform_insights'] = await self._generate_platform_insights(metrics, query)
            
            if report_type == "detailed":
                # Detailed breakdowns
                report_sections['detailed_breakdowns'] = await self._generate_detailed_breakdowns(metrics, query)
                
                # Recommendations
                report_sections['recommendations'] = await self._generate_recommendations(metrics, query)
            
            # Summary statistics
            report_sections['summary'] = await self._generate_summary_statistics(metrics, query)
            
            return {
                'report_type': report_type,
                'time_range_days': time_range_days,
                'user_id': user_id,
                'platform': platform,
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'sections': report_sections,
                'metadata': {
                    'data_points': metrics.get('metadata', {}).get('data_points', 0),
                    'query_time': metrics.get('metadata', {}).get('query_time')
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate analytics report: {e}")
            raise AnalyticsError(f"Report generation failed: {str(e)}")

    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for webhook analytics"""        return {
            'status': 'healthy',
            'redis_connected': self._redis_client is not None,
            'event_buffer_size': len(self._event_buffer),
            'metric_cache_size': len(self._metric_cache),
            'aggregation_tasks': len(self._aggregation_tasks),
            'real_time_metrics_tracked': len(self._real_time_metrics)
        }

    async def shutdown(self) -> None:
        """Graceful shutdown of webhook analytics"""        try:
            logger.info("Shutting down WebhookAnalytics")
            
            # Cancel aggregation tasks
            for task in self._aggregation_tasks:
                task.cancel()
            
            # Flush remaining events
            await self._flush_event_buffer()
            
            # Close Redis connection
            if self._redis_client:
                await self._redis_client.close()
            
            logger.info("WebhookAnalytics shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during WebhookAnalytics shutdown: {e}")

    # Private methods
    
    async def _store_event_async(self, event: WebhookEvent) -> None:
        """Store event in database asynchronously"""        try:
            db_event = WebhookAnalyticsModel(
                event_id=event.event_id,
                endpoint_id=event.endpoint_id,
                user_id=event.user_id,
                platform=event.platform,
                event_type=event.event_type,
                timestamp=event.timestamp,
                response_time_ms=event.response_time_ms,
                status_code=event.status_code,
                success=event.success,
                payload_size_bytes=event.payload_size_bytes,
                error_message=event.error_message,
                processing_duration_ms=event.processing_duration_ms,
                retry_count=event.retry_count,
                metadata=event.metadata
            )
            
            self.db_session.add(db_event)
            self.db_session.commit()
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to store event in database: {e}")

    async def _update_real_time_metrics(self, event: WebhookEvent) -> None:
        """Update real-time metrics with new event"""        try:
            current_time = time.time()
            
            # Update request counts
            self._request_counts[event.platform] += 1
            self._request_counts['total'] += 1
            
            # Update response times
            if event.response_time_ms:
                self._response_times[event.platform].append(event.response_time_ms)
                self._response_times['total'].append(event.response_time_ms)
                
                # Keep only recent response times
                cutoff_time = current_time - self.real_time_window_seconds
                self._response_times[event.platform] = [
                    rt for rt in self._response_times[event.platform][-100:]
                ]
            
            # Update error counts
            if not event.success:
                self._error_counts[event.platform] += 1
                self._error_counts['total'] += 1
            
            # Update throughput tracker
            self._throughput_tracker[event.platform].append(current_time)
            self._throughput_tracker['total'].append(current_time)
            
            # Clean old throughput data
            cutoff_time = current_time - self.real_time_window_seconds
            for key in self._throughput_tracker:
                while (self._throughput_tracker[key] and 
                       self._throughput_tracker[key][0] < cutoff_time):
                    self._throughput_tracker[key].popleft()
            
        except Exception as e:
            logger.error(f"Failed to update real-time metrics: {e}")

    async def _update_redis_metrics(self, event: WebhookEvent) -> None:
        """Update Redis metrics cache"""        try:
            if self._redis_client:
                # Update request counter
                await self._redis_client.incr(f"webhook_requests:{event.platform}")
                await self._redis_client.incr("webhook_requests:total")
                
                # Set expiration
                await self._redis_client.expire(f"webhook_requests:{event.platform}", 3600)
                await self._redis_client.expire("webhook_requests:total", 3600)
                
                # Update success/failure counters
                if event.success:
                    await self._redis_client.incr(f"webhook_success:{event.platform}")
                else:
                    await self._redis_client.incr(f"webhook_errors:{event.platform}")
                
                # Store response time for averaging
                response_time_key = f"webhook_response_times:{event.platform}"
                await self._redis_client.lpush(response_time_key, event.response_time_ms)
                await self._redis_client.ltrim(response_time_key, 0, 999)  # Keep last 1000
                await self._redis_client.expire(response_time_key, 3600)
                
        except Exception as e:
            logger.error(f"Failed to update Redis metrics: {e}")

    async def _query_metrics_from_db(self, query: AnalyticsQuery) -> List[Dict[str, Any]]:
        """Query metrics data from database"""        try:
            db_query = self.db_session.query(WebhookAnalyticsModel).filter(
                WebhookAnalyticsModel.timestamp >= query.start_time,
                WebhookAnalyticsModel.timestamp <= query.end_time
            )
            
            # Apply filters
            if query.endpoint_ids:
                db_query = db_query.filter(WebhookAnalyticsModel.endpoint_id.in_(query.endpoint_ids))
            
            if query.user_ids:
                db_query = db_query.filter(WebhookAnalyticsModel.user_id.in_(query.user_ids))
            
            if query.platforms:
                db_query = db_query.filter(WebhookAnalyticsModel.platform.in_(query.platforms))
            
            if query.event_types:
                db_query = db_query.filter(WebhookAnalyticsModel.event_type.in_(query.event_types))
            
            if query.include_errors_only:
                db_query = db_query.filter(WebhookAnalyticsModel.success == False)
            
            if query.include_success_only:
                db_query = db_query.filter(WebhookAnalyticsModel.success == True)
            
            # Limit results
            db_query = db_query.limit(query.limit)
            
            # Execute query
            results = db_query.all()
            
            # Convert to dictionaries
            return [
                {
                    'event_id': event.event_id,
                    'endpoint_id': event.endpoint_id,
                    'user_id': event.user_id,
                    'platform': event.platform,
                    'event_type': event.event_type,
                    'timestamp': event.timestamp,
                    'response_time_ms': event.response_time_ms,
                    'status_code': event.status_code,
                    'success': event.success,
                    'payload_size_bytes': event.payload_size_bytes,
                    'error_message': event.error_message,
                    'processing_duration_ms': event.processing_duration_ms,
                    'retry_count': event.retry_count,
                    'metadata': event.metadata
                }
                for event in results
            ]
            
        except Exception as e:
            logger.error(f"Failed to query metrics from database: {e}")
            return []

    async def _process_metrics_data(
        self,
        raw_data: List[Dict[str, Any]],
        query: AnalyticsQuery
    ) -> Dict[str, Any]:
        """Process and aggregate raw metrics data"""        try:
            if not raw_data:
                return self._get_empty_metrics()
            
            # Basic statistics
            total_requests = len(raw_data)
            successful_requests = len([d for d in raw_data if d['success']])
            failed_requests = total_requests - successful_requests
            
            success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
            error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
            
            # Response time statistics
            response_times = [d['response_time_ms'] for d in raw_data if d['response_time_ms']]
            avg_response_time = np.mean(response_times) if response_times else 0
            min_response_time = np.min(response_times) if response_times else 0
            max_response_time = np.max(response_times) if response_times else 0
            p50_response_time = np.percentile(response_times, 50) if response_times else 0
            p95_response_time = np.percentile(response_times, 95) if response_times else 0
            p99_response_time = np.percentile(response_times, 99) if response_times else 0
            
            # Payload size statistics
            payload_sizes = [d['payload_size_bytes'] for d in raw_data if d['payload_size_bytes']]
            total_payload_bytes = sum(payload_sizes) if payload_sizes else 0
            avg_payload_size = np.mean(payload_sizes) if payload_sizes else 0
            
            # Platform distribution
            platform_counts = defaultdict(int)
            for data in raw_data:
                platform_counts[data['platform']] += 1
            
            # Event type distribution
            event_type_counts = defaultdict(int)
            for data in raw_data:
                event_type_counts[data['event_type']] += 1
            
            # Time series data (aggregated by time window)
            time_series = self._aggregate_time_series(raw_data, query.time_window)
            
            # Error analysis
            error_analysis = self._analyze_errors(raw_data)
            
            # Throughput calculation
            time_span_hours = (query.end_time - query.start_time).total_seconds() / 3600
            throughput_per_hour = total_requests / time_span_hours if time_span_hours > 0 else 0
            
            return {
                'summary': {
                    'total_requests': total_requests,
                    'successful_requests': successful_requests,
                    'failed_requests': failed_requests,
                    'success_rate_percent': round(success_rate, 2),
                    'error_rate_percent': round(error_rate, 2),
                    'throughput_per_hour': round(throughput_per_hour, 2)
                },
                'response_time': {
                    'avg_ms': round(avg_response_time, 2),
                    'min_ms': round(min_response_time, 2),
                    'max_ms': round(max_response_time, 2),
                    'p50_ms': round(p50_response_time, 2),
                    'p95_ms': round(p95_response_time, 2),
                    'p99_ms': round(p99_response_time, 2)
                },
                'payload': {
                    'total_bytes': total_payload_bytes,
                    'avg_size_bytes': round(avg_payload_size, 2),
                    'count': len(payload_sizes)
                },
                'distribution': {
                    'platforms': dict(platform_counts),
                    'event_types': dict(event_type_counts)
                },
                'time_series': time_series,
                'error_analysis': error_analysis
            }
            
        except Exception as e:
            logger.error(f"Failed to process metrics data: {e}")
            return self._get_empty_metrics()

    def _aggregate_time_series(
        self,
        data: List[Dict[str, Any]],
        time_window: TimeWindow
    ) -> List[Dict[str, Any]]:
        """Aggregate data into time series based on time window"""        try:
            # Group data by time window
            time_buckets = defaultdict(list)
            
            for item in data:
                timestamp = item['timestamp']
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                
                # Round timestamp to time window
                if time_window == TimeWindow.MINUTE:
                    bucket_time = timestamp.replace(second=0, microsecond=0)
                elif time_window == TimeWindow.HOUR:
                    bucket_time = timestamp.replace(minute=0, second=0, microsecond=0)
                elif time_window == TimeWindow.DAY:
                    bucket_time = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
                elif time_window == TimeWindow.WEEK:
                    # Start of week (Monday)
                    days_since_monday = timestamp.weekday()
                    bucket_time = (timestamp - timedelta(days=days_since_monday)).replace(
                        hour=0, minute=0, second=0, microsecond=0
                    )
                else:  # MONTH
                    bucket_time = timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                
                time_buckets[bucket_time].append(item)
            
            # Calculate metrics for each time bucket
            time_series = []
            for bucket_time, bucket_data in sorted(time_buckets.items()):
                bucket_metrics = self._calculate_bucket_metrics(bucket_data)
                bucket_metrics['timestamp'] = bucket_time.isoformat()
                time_series.append(bucket_metrics)
            
            return time_series
            
        except Exception as e:
            logger.error(f"Failed to aggregate time series: {e}")
            return []

    def _calculate_bucket_metrics(self, bucket_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate metrics for a time bucket"""        total_requests = len(bucket_data)
        successful_requests = len([d for d in bucket_data if d['success']])
        failed_requests = total_requests - successful_requests
        
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        response_times = [d['response_time_ms'] for d in bucket_data if d['response_time_ms']]
        avg_response_time = np.mean(response_times) if response_times else 0
        
        return {
            'requests': total_requests,
            'successful': successful_requests,
            'failed': failed_requests,
            'success_rate_percent': round(success_rate, 2),
            'avg_response_time_ms': round(avg_response_time, 2)
        }

    def _analyze_errors(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze errors in the data"""        errors = [d for d in data if not d['success']]
        
        if not errors:
            return {
                'total_errors': 0,
                'error_types': {},
                'top_error_messages': []
            }
        
        # Group by status code
        status_code_counts = defaultdict(int)
        for error in errors:
            if error['status_code']:
                status_code_counts[error['status_code']] += 1
        
        # Group by error message
        error_message_counts = defaultdict(int)
        for error in errors:
            if error['error_message']:
                error_message_counts[error['error_message']] += 1
        
        # Top error messages
        top_errors = sorted(error_message_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_errors': len(errors),
            'error_types': dict(status_code_counts),
            'top_error_messages': [
                {'message': msg, 'count': count} for msg, count in top_errors
            ]
        }

    def _get_empty_metrics(self) -> Dict[str, Any]:
        """Get empty metrics structure"""        return {
            'summary': {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'success_rate_percent': 0,
                'error_rate_percent': 0,
                'throughput_per_hour': 0
            },
            'response_time': {
                'avg_ms': 0,
                'min_ms': 0,
                'max_ms': 0,
                'p50_ms': 0,
                'p95_ms': 0,
                'p99_ms': 0
            },
            'payload': {
                'total_bytes': 0,
                'avg_size_bytes': 0,
                'count': 0
            },
            'distribution': {
                'platforms': {},
                'event_types': {}
            },
            'time_series': [],
            'error_analysis': {
                'total_errors': 0,
                'error_types': {},
                'top_error_messages': []
            }
        }

    async def _calculate_insights(
        self,
        metrics: Dict[str, Any],
        query: AnalyticsQuery
    ) -> Dict[str, Any]:
        """Calculate insights from metrics data"""        insights = {
            'key_findings': [],
            'recommendations': [],
            'alerts': []
        }
        
        try:
            # Success rate insights
            success_rate = metrics['summary']['success_rate_percent']
            if success_rate < 95:
                insights['key_findings'].append(
                    f"Success rate is {success_rate}%, below recommended 95%"
                )
                insights['recommendations'].append(
                    "Investigate failing webhooks and improve error handling"
                )
            
            # Response time insights
            avg_response_time = metrics['response_time']['avg_ms']
            if avg_response_time > 2000:
                insights['key_findings'].append(
                    f"Average response time is {avg_response_time}ms, above 2 second threshold"
                )
                insights['recommendations'].append(
                    "Optimize webhook processing to reduce response times"
                )
            
            # Error rate alerts
            error_rate = metrics['summary']['error_rate_percent']
            if error_rate > self.alert_thresholds['error_rate'] * 100:
                insights['alerts'].append({
                    'type': 'high_error_rate',
                    'message': f"Error rate {error_rate}% exceeds threshold",
                    'severity': 'high'
                })
            
            # Platform distribution insights
            platforms = metrics['distribution']['platforms']
            if len(platforms) > 0:
                top_platform = max(platforms, key=platforms.get)
                insights['key_findings'].append(
                    f"Most active platform: {top_platform} ({platforms[top_platform]} requests)"
                )
            
        except Exception as e:
            logger.error(f"Failed to calculate insights: {e}")
        
        return insights

    def _generate_metrics_cache_key(self, query: AnalyticsQuery) -> str:
        """Generate cache key for metrics query"""        key_components = [
            query.start_time.isoformat(),
            query.end_time.isoformat(),
            query.time_window.value,
            '_'.join(query.endpoint_ids) if query.endpoint_ids else 'all',
            '_'.join(query.user_ids) if query.user_ids else 'all',
            '_'.join(query.platforms) if query.platforms else 'all',
            '_'.join(query.event_types) if query.event_types else 'all',
            str(query.include_errors_only),
            str(query.include_success_only)
        ]
        
        return 'metrics:' + ':'.join(key_components)

    async def _start_aggregation_tasks(self) -> None:
        """Start background aggregation tasks"""        # Metrics aggregation task
        task = asyncio.create_task(self._aggregate_metrics_task())
        self._aggregation_tasks.add(task)
        
        # Cache cleanup task
        task = asyncio.create_task(self._cache_cleanup_task())
        self._aggregation_tasks.add(task)

    async def _aggregate_metrics_task(self) -> None:
        """Background task for metrics aggregation"""        while True:
            try:
                await asyncio.sleep(self.aggregation_interval_seconds)
                
                # Aggregate metrics from event buffer
                await self._aggregate_buffer_metrics()
                
            except Exception as e:
                logger.error(f"Error in metrics aggregation task: {e}")

    async def _cache_cleanup_task(self) -> None:
        """Background task for cache cleanup"""        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Clean old cache entries
                current_time = datetime.now(timezone.utc)
                expired_keys = []
                
                for key, cached_data in self._metric_cache.items():
                    if (current_time - cached_data['timestamp']).seconds > 3600:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self._metric_cache[key]
                
                logger.info(f"Cleaned {len(expired_keys)} expired cache entries")
                
            except Exception as e:
                logger.error(f"Error in cache cleanup task: {e}")

    async def _aggregate_buffer_metrics(self) -> None:
        """Aggregate metrics from event buffer"""        try:
            if not self._event_buffer:
                return
            
            # Process events in batches
            events_to_process = list(self._event_buffer)
            
            # Group by time window and calculate aggregates
            # This is a simplified implementation - production would have more sophisticated aggregation
            
            logger.debug(f"Aggregated metrics for {len(events_to_process)} events")
            
        except Exception as e:
            logger.error(f"Failed to aggregate buffer metrics: {e}")

    async def _initialize_metric_cache(self) -> None:
        """Initialize metric cache with default values"""        self._metric_cache = {}
        logger.info("Metric cache initialized")

    async def _flush_event_buffer(self) -> None:
        """Flush remaining events in buffer to database"""        try:
            while self._event_buffer:
                event = self._event_buffer.popleft()
                await self._store_event_async(event)
            
            logger.info("Event buffer flushed")
            
        except Exception as e:
            logger.error(f"Failed to flush event buffer: {e}")

    async def _check_real_time_alerts(self, events: List[WebhookEvent]) -> List[Dict[str, Any]]:
        """Check for real-time alerts based on recent events"""        alerts = []
        
        if not events:
            return alerts
        
        try:
            # High error rate alert
            failed_events = [e for e in events if not e.success]
            error_rate = len(failed_events) / len(events)
            
            if error_rate > self.alert_thresholds['error_rate']:
                alerts.append({
                    'type': 'high_error_rate',
                    'message': f"Error rate {error_rate*100:.1f}% exceeds threshold",
                    'severity': 'high',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            
            # High response time alert
            response_times = [e.response_time_ms for e in events if e.response_time_ms]
            if response_times:
                p95_response_time = np.percentile(response_times, 95)
                if p95_response_time > self.alert_thresholds['response_time_p95']:
                    alerts.append({
                        'type': 'high_response_time',
                        'message': f"P95 response time {p95_response_time:.0f}ms exceeds threshold",
                        'severity': 'medium',
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })
            
        except Exception as e:
            logger.error(f"Failed to check real-time alerts: {e}")
        
        return alerts

    # Additional insight calculation methods would be implemented here
    # These are placeholders for the comprehensive analytics features
    
    async def _calculate_endpoint_insights(self, endpoint_id: str, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Calculate insights for specific endpoint"""        return {'placeholder': 'endpoint_insights'}
    
    async def _analyze_endpoint_errors(self, endpoint_id: str, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Analyze errors for specific endpoint"""        return {'placeholder': 'error_analysis'}
    
    async def _calculate_performance_trends(self, endpoint_id: str, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Calculate performance trends for endpoint"""        return {'placeholder': 'performance_trends'}
    
    async def _calculate_user_insights(self, user_id: str, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Calculate insights for specific user"""        return {'placeholder': 'user_insights'}
    
    async def _calculate_platform_usage(self, user_id: str, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Calculate platform usage for user"""        return {'placeholder': 'platform_usage'}
    
    async def _calculate_platform_insights(self, platform: str, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Calculate insights for specific platform"""        return {'placeholder': 'platform_insights'}
    
    # Report generation methods (placeholders for full implementation)
    
    async def _generate_executive_summary(self, metrics: Dict[str, Any], query: AnalyticsQuery) -> Dict[str, Any]:
        """Generate executive summary section"""        return {'placeholder': 'executive_summary'}
    
    async def _generate_performance_analysis(self, metrics: Dict[str, Any], query: AnalyticsQuery) -> Dict[str, Any]:
        """Generate performance analysis section"""        return {'placeholder': 'performance_analysis'}
    
    async def _generate_error_analysis(self, metrics: Dict[str, Any], query: AnalyticsQuery) -> Dict[str, Any]:
        """Generate error analysis section"""        return {'placeholder': 'error_analysis'}
    
    async def _generate_trend_analysis(self, metrics: Dict[str, Any], query: AnalyticsQuery) -> Dict[str, Any]:
        """Generate trend analysis section"""        return {'placeholder': 'trend_analysis'}
    
    async def _generate_platform_insights(self, metrics: Dict[str, Any], query: AnalyticsQuery) -> Dict[str, Any]:
        """Generate platform insights section"""        return {'placeholder': 'platform_insights'}
    
    async def _generate_detailed_breakdowns(self, metrics: Dict[str, Any], query: AnalyticsQuery) -> Dict[str, Any]:
        """Generate detailed breakdowns section"""        return {'placeholder': 'detailed_breakdowns'}
    
    async def _generate_recommendations(self, metrics: Dict[str, Any], query: AnalyticsQuery) -> Dict[str, Any]:
        """Generate recommendations section"""        return {'placeholder': 'recommendations'}
    
    async def _generate_summary_statistics(self, metrics: Dict[str, Any], query: AnalyticsQuery) -> Dict[str, Any]:
        """Generate summary statistics section"""        return {'placeholder': 'summary_statistics'}
