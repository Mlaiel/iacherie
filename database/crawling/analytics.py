"""
Enterprise Crawling Analytics Manager

Advanced analytics and performance monitoring for crawling operations
with comprehensive metrics and business intelligence.

PROTECTION NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution is strictly prohibited.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security Expert
Copyright: All rights reserved
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, text
from uuid import uuid4
import json
from enum import Enum

from ..core.base import DatabaseManager
from ..models.crawling_models import (
    CrawlingAnalytics,
    AnalyticsEventType,
    MetricType
)
from ..core.exceptions import (
    DatabaseError,
    ValidationError
)


class CrawlingAnalyticsManager(DatabaseManager):
    """
    Enterprise-grade analytics manager for crawling operations.
    
    Handles:
    - Performance metrics collection
    - Business intelligence analytics
    - Real-time monitoring data
    - Trend analysis and forecasting
    - Custom dashboard metrics
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize crawling analytics manager.
        
        Args:
            db_session: SQLAlchemy database session
        """
        super().__init__(db_session)
        self.table = CrawlingAnalytics
    
    async def log_session_start(
        self,
        session_id: str,
        platform: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log session start event with comprehensive metadata.
        
        Args:
            session_id: Session identifier
            platform: Platform being crawled
            user_id: User identifier
            metadata: Additional event metadata
            
        Returns:
            Analytics event ID
        """



        try:
            return await self._log_analytics_event(
                event_type=AnalyticsEventType.SESSION_START.value,
                session_id=session_id,
                platform=platform,
                user_id=user_id,
                metric_name='session_started',
                metric_value=1.0,
                metadata=metadata
            )
        except Exception as e:
            raise DatabaseError(f"Failed to log session start: {str(e)}")
    
    async def log_job_scheduled(
        self,
        job_id: str,
        session_id: str,
        job_type: str,
        targets_count: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log job scheduling event.
        
        Args:
            job_id: Job identifier
            session_id: Session identifier
            job_type: Type of job being scheduled
            targets_count: Number of targets in job
            metadata: Additional event metadata
            
        Returns:
            Analytics event ID
        """



        try:
            event_metadata = {
                'job_id': job_id,
                'job_type': job_type,
                'targets_count': targets_count,
                **(metadata or {})
            }
            
            return await self._log_analytics_event(
                event_type=AnalyticsEventType.JOB_SCHEDULED.value,
                session_id=session_id,
                metric_name='job_scheduled',
                metric_value=float(targets_count),
                metadata=event_metadata
            )
        except Exception as e:
            raise DatabaseError(f"Failed to log job scheduled: {str(e)}")
    
    async def log_content_discovered(
        self,
        discovery_id: str,
        session_id: str,
        job_id: str,
        content_type: str,
        confidence_score: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log content discovery event.
        
        Args:
            discovery_id: Discovery identifier
            session_id: Session identifier
            job_id: Job identifier
            content_type: Type of content discovered
            confidence_score: Confidence score of discovery
            metadata: Additional event metadata
            
        Returns:
            Analytics event ID
        """



        try:
            event_metadata = {
                'discovery_id': discovery_id,
                'job_id': job_id,
                'content_type': content_type,
                'confidence_score': confidence_score,
                **(metadata or {})
            }
            
            return await self._log_analytics_event(
                event_type=AnalyticsEventType.CONTENT_DISCOVERED.value,
                session_id=session_id,
                metric_name='content_discovered',
                metric_value=confidence_score,
                metadata=event_metadata
            )
        except Exception as e:
            raise DatabaseError(f"Failed to log content discovered: {str(e)}")
    
    async def log_performance_metric(
        self,
        session_id: str,
        metric_name: str,
        metric_value: float,
        metric_type: str = MetricType.GAUGE.value,
        platform: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log custom performance metric.
        
        Args:
            session_id: Session identifier
            metric_name: Name of the metric
            metric_value: Numeric value of the metric
            metric_type: Type of metric (gauge, counter, histogram)
            platform: Optional platform filter
            metadata: Additional metric metadata
            
        Returns:
            Analytics event ID
        """



        try:
            return await self._log_analytics_event(
                event_type=AnalyticsEventType.PERFORMANCE_METRIC.value,
                session_id=session_id,
                platform=platform,
                metric_name=metric_name,
                metric_value=metric_value,
                metric_type=metric_type,
                metadata=metadata
            )
        except Exception as e:
            raise DatabaseError(f"Failed to log performance metric: {str(e)}")
    
    async def log_error(
        self,
        error_type: str,
        error_data: Dict[str, Any],
        session_id: Optional[str] = None,
        severity: str = 'error'
    ) -> str:
        """
        Log error event with comprehensive error data.
        
        Args:
            error_type: Type/category of error
            error_data: Error details and context
            session_id: Optional session identifier
            severity: Error severity level
            
        Returns:
            Analytics event ID
        """



        try:
            error_metadata = {
                'error_type': error_type,
                'severity': severity,
                **error_data
            }
            
            return await self._log_analytics_event(
                event_type=AnalyticsEventType.ERROR.value,
                session_id=session_id,
                metric_name=f'error_{error_type}',
                metric_value=1.0,
                metadata=error_metadata
            )
        except Exception as e:
            # Don't raise exception for error logging to prevent error loops
            print(f"Failed to log error: {str(e)}")
            return ""
    
    async def log_cleanup_operation(
        self,
        cleanup_stats: Dict[str, int],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log cleanup operation results.
        
        Args:
            cleanup_stats: Statistics from cleanup operation
            metadata: Additional cleanup metadata
            
        Returns:
            Analytics event ID
        """



        try:
            event_metadata = {
                'cleanup_stats': cleanup_stats,
                **(metadata or {})
            }
            
            return await self._log_analytics_event(
                event_type=AnalyticsEventType.SYSTEM_OPERATION.value,
                metric_name='cleanup_operation',
                metric_value=float(cleanup_stats.get('sessions_cleaned', 0)),
                metadata=event_metadata
            )
        except Exception as e:
            raise DatabaseError(f"Failed to log cleanup operation: {str(e)}")
    
    async def _log_analytics_event(
        self,
        event_type: str,
        metric_name: str,
        metric_value: float,
        session_id: Optional[str] = None,
        platform: Optional[str] = None,
        user_id: Optional[str] = None,
        metric_type: str = MetricType.COUNTER.value,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Internal method to log analytics events.
        
        Args:
            event_type: Type of analytics event
            metric_name: Name of the metric
            metric_value: Numeric value
            session_id: Optional session identifier
            platform: Optional platform
            user_id: Optional user identifier
            metric_type: Type of metric
            metadata: Optional metadata
            
        Returns:
            Analytics event ID
        """



        try:
            event_id = str(uuid4())
            
            analytics_data = {
                'event_id': event_id,
                'event_type': event_type,
                'session_id': session_id,
                'platform': platform,
                'user_id': user_id,
                'metric_name': metric_name,
                'metric_value': metric_value,
                'metric_type': metric_type,
                'metadata': json.dumps(metadata) if metadata else None,
                'created_at': datetime.utcnow()
            }
            
            analytics = CrawlingAnalytics(**analytics_data)
            self.db.add(analytics)
            await self.db.commit()
            
            return event_id
            
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to log analytics event: {str(e)}")
    
    async def get_user_summary(
        self,
        user_id: str,
        since: Optional[datetime] = None,
        time_range: timedelta = timedelta(days=7)
    ) -> Dict[str, Any]:
        """
        Get comprehensive analytics summary for a user.
        
        Args:
            user_id: User identifier
            since: Optional start time (overrides time_range)
            time_range: Time range for analytics (default: 7 days)
            
        Returns:
            Dict containing user analytics summary
        """



        try:
            if since is None:
                since = datetime.utcnow() - time_range
            
            # Get total discoveries
            discoveries_result = await self.db.execute(
                text("""
                SELECT COUNT(*) as total_discoveries,
                       AVG(metric_value) as avg_confidence
                FROM crawling_analytics
                WHERE user_id = :user_id
                  AND event_type = :discovery_event
                  AND created_at >= :since
                """),
                {
                    'user_id': user_id,
                    'discovery_event': AnalyticsEventType.CONTENT_DISCOVERED.value,
                    'since': since
                }
            )
            
            # Get platform breakdown
            platform_result = await self.db.execute(
                text("""
                SELECT platform,
                       COUNT(*) as events_count,
                       COUNT(CASE WHEN event_type = :discovery_event THEN 1 END) as discoveries
                FROM crawling_analytics
                WHERE user_id = :user_id
                  AND created_at >= :since
                  AND platform IS NOT NULL
                GROUP BY platform
                """),
                {
                    'user_id': user_id,
                    'discovery_event': AnalyticsEventType.CONTENT_DISCOVERED.value,
                    'since': since
                }
            )
            
            # Get success rate (successful vs error events)
            success_result = await self.db.execute(
                text("""
                SELECT 
                    COUNT(CASE WHEN event_type != :error_event THEN 1 END) as successful_events,
                    COUNT(CASE WHEN event_type = :error_event THEN 1 END) as error_events,
                    COUNT(*) as total_events
                FROM crawling_analytics
                WHERE user_id = :user_id
                  AND created_at >= :since
                """),
                {
                    'user_id': user_id,
                    'error_event': AnalyticsEventType.ERROR.value,
                    'since': since
                }
            )
            
            # Get average response time from performance metrics
            response_time_result = await self.db.execute(
                text("""
                SELECT AVG(metric_value) as avg_response_time
                FROM crawling_analytics
                WHERE user_id = :user_id
                  AND metric_name = 'response_time'
                  AND created_at >= :since
                """),
                {
                    'user_id': user_id,
                    'since': since
                }
            )
            
            discoveries_data = discoveries_result.first()
            success_data = success_result.first()
            response_time_data = response_time_result.first()
            
            platform_breakdown = {
                row.platform: {
                    'events_count': row.events_count,
                    'discoveries': row.discoveries
                }
                for row in platform_result
            }
            
            # Calculate success rate
            success_rate = 0.0
            if success_data.total_events > 0:
                success_rate = (success_data.successful_events / success_data.total_events) * 100
            
            return {
                'total_discoveries': discoveries_data.total_discoveries or 0,
                'avg_confidence_score': float(discoveries_data.avg_confidence or 0),
                'success_rate': success_rate,
                'avg_response_time': float(response_time_data.avg_response_time or 0),
                'platform_breakdown': platform_breakdown,
                'total_events': success_data.total_events or 0,
                'error_events': success_data.error_events or 0,
                'time_range_start': since.isoformat(),
                'time_range_end': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get user summary: {str(e)}")
    
    async def get_platform_analytics(
        self,
        platform: str,
        time_range: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """
        Get comprehensive analytics for a specific platform.
        
        Args:
            platform: Platform to analyze
            time_range: Time range for analytics
            
        Returns:
            Dict containing platform analytics
        """



        try:
            since = datetime.utcnow() - time_range
            
            # Get activity timeline (hourly breakdown)
            timeline_result = await self.db.execute(
                text("""
                SELECT 
                    DATE_TRUNC('hour', created_at) as hour,
                    COUNT(*) as events_count,
                    COUNT(CASE WHEN event_type = :discovery_event THEN 1 END) as discoveries,
                    COUNT(CASE WHEN event_type = :error_event THEN 1 END) as errors
                FROM crawling_analytics
                WHERE platform = :platform
                  AND created_at >= :since
                GROUP BY DATE_TRUNC('hour', created_at)
                ORDER BY hour
                """),
                {
                    'platform': platform,
                    'discovery_event': AnalyticsEventType.CONTENT_DISCOVERED.value,
                    'error_event': AnalyticsEventType.ERROR.value,
                    'since': since
                }
            )
            
            # Get top metrics
            metrics_result = await self.db.execute(
                text("""
                SELECT 
                    metric_name,
                    COUNT(*) as metric_count,
                    AVG(metric_value) as avg_value,
                    MAX(metric_value) as max_value,
                    MIN(metric_value) as min_value
                FROM crawling_analytics
                WHERE platform = :platform
                  AND created_at >= :since
                  AND metric_name IS NOT NULL
                GROUP BY metric_name
                ORDER BY metric_count DESC
                LIMIT 10
                """),
                {
                    'platform': platform,
                    'since': since
                }
            )
            
            # Get user activity
            users_result = await self.db.execute(
                text("""
                SELECT 
                    user_id,
                    COUNT(*) as events_count,
                    COUNT(CASE WHEN event_type = :discovery_event THEN 1 END) as discoveries,
                    MAX(created_at) as last_activity
                FROM crawling_analytics
                WHERE platform = :platform
                  AND created_at >= :since
                  AND user_id IS NOT NULL
                GROUP BY user_id
                ORDER BY events_count DESC
                LIMIT 20
                """),
                {
                    'platform': platform,
                    'discovery_event': AnalyticsEventType.CONTENT_DISCOVERED.value,
                    'since': since
                }
            )
            
            timeline_data = [
                {
                    'hour': row.hour.isoformat(),
                    'events_count': row.events_count,
                    'discoveries': row.discoveries,
                    'errors': row.errors
                }
                for row in timeline_result
            ]
            
            metrics_data = [
                {
                    'metric_name': row.metric_name,
                    'count': row.metric_count,
                    'avg_value': float(row.avg_value),
                    'max_value': float(row.max_value),
                    'min_value': float(row.min_value)
                }
                for row in metrics_result
            ]
            
            users_data = [
                {
                    'user_id': row.user_id,
                    'events_count': row.events_count,
                    'discoveries': row.discoveries,
                    'last_activity': row.last_activity.isoformat()
                }
                for row in users_result
            ]
            
            return {
                'platform': platform,
                'time_range_days': time_range.days,
                'activity_timeline': timeline_data,
                'top_metrics': metrics_data,
                'active_users': users_data,
                'total_timeline_points': len(timeline_data),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get platform analytics: {str(e)}")
    
    async def get_performance_trends(
        self,
        metric_names: List[str],
        time_range: timedelta = timedelta(days=30),
        granularity: str = 'daily'
    ) -> Dict[str, Any]:
        """
        Get performance trends for specified metrics.
        
        Args:
            metric_names: List of metric names to analyze
            time_range: Time range for trends
            granularity: Time granularity (hourly, daily, weekly)
            
        Returns:
            Dict containing trend analysis
        """



        try:
            since = datetime.utcnow() - time_range
            
            # Determine date truncation based on granularity
            date_trunc = {
                'hourly': 'hour',
                'daily': 'day',
                'weekly': 'week'
            }.get(granularity, 'day')
            
            trends_data = {}
            
            for metric_name in metric_names:
                trend_result = await self.db.execute(
                    text(f"""
                    SELECT 
                        DATE_TRUNC(:granularity, created_at) as time_period,
                        COUNT(*) as data_points,
                        AVG(metric_value) as avg_value,
                        MAX(metric_value) as max_value,
                        MIN(metric_value) as min_value,
                        STDDEV(metric_value) as std_dev
                    FROM crawling_analytics
                    WHERE metric_name = :metric_name
                      AND created_at >= :since
                      AND metric_value IS NOT NULL
                    GROUP BY DATE_TRUNC(:granularity, created_at)
                    ORDER BY time_period
                    """),
                    {
                        'metric_name': metric_name,
                        'granularity': date_trunc,
                        'since': since
                    }
                )
                
                trend_points = [
                    {
                        'time_period': row.time_period.isoformat(),
                        'data_points': row.data_points,
                        'avg_value': float(row.avg_value or 0),
                        'max_value': float(row.max_value or 0),
                        'min_value': float(row.min_value or 0),
                        'std_dev': float(row.std_dev or 0)
                    }
                    for row in trend_result
                ]
                
                trends_data[metric_name] = {
                    'trend_points': trend_points,
                    'total_points': len(trend_points)
                }
            
            return {
                'metrics': list(metric_names),
                'time_range_days': time_range.days,
                'granularity': granularity,
                'trends': trends_data,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get performance trends: {str(e)}")
    
    async def cleanup_old_analytics(
        self,
        retention_days: int = 90
    ) -> Dict[str, int]:
        """
        Clean up old analytics data beyond retention period.
        
        Args:
            retention_days: Number of days to retain analytics data
            
        Returns:
            Dict containing cleanup statistics
        """



        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            # Archive old data first (optional - implement if needed)
            # await self._archive_analytics_data(cutoff_date)
            
            # Delete old analytics data
            result = await self.db.execute(
                text("DELETE FROM crawling_analytics WHERE created_at < :cutoff_date"),
                {'cutoff_date': cutoff_date}
            )
            
            await self.db.commit()
            
            return {
                'deleted_records': result.rowcount,
                'cutoff_date': cutoff_date.isoformat(),
                'retention_days': retention_days
            }
            
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to cleanup old analytics: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check of analytics system.
        
        Returns:
            Dict containing health status
        """



        try:
            # Check recent analytics activity
            recent_events = await self.db.query(func.count(CrawlingAnalytics.event_id)).filter(
                CrawlingAnalytics.created_at >= datetime.utcnow() - timedelta(hours=1)
            ).scalar()
            
            # Check analytics table size
            total_events = await self.db.query(func.count(CrawlingAnalytics.event_id)).scalar()
            
            # Check for any error patterns
            recent_errors = await self.db.query(func.count(CrawlingAnalytics.event_id)).filter(
                and_(
                    CrawlingAnalytics.event_type == AnalyticsEventType.ERROR.value,
                    CrawlingAnalytics.created_at >= datetime.utcnow() - timedelta(hours=1)
                )
            ).scalar()
            
            # Determine health status
            status = 'healthy'
            if recent_errors > recent_events * 0.1:  # More than 10% errors
                status = 'degraded'
            if recent_errors > recent_events * 0.3:  # More than 30% errors
                status = 'unhealthy'
            
            return {
                'status': status,
                'recent_events_1h': recent_events,
                'total_events': total_events,
                'recent_errors_1h': recent_errors,
                'error_rate_percentage': (recent_errors / max(recent_events, 1)) * 100,
                'last_check': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.utcnow().isoformat()
            }


# Export main class
__all__ = ['CrawlingAnalyticsManager']
